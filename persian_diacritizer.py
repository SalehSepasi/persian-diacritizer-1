"""
Persian diacritization from Homo-GE2PE phoneme output.

The original Persian letters are preserved. Short-vowel marks are added

according to the model's phoneme sequence. If alignment is uncertain, the

word is returned without newly added marks rather than guessed.

"""

import os

import re

from typing import Optional

ZWNJ = "\u200c"

FATHA, KASRA, DAMMA, SHADDA = "\u064E", "\u0650", "\u064F", "\u0651"

SHORT = {"a": FATHA, "e": KASRA, "o": DAMMA}

LONG = {"A": "ا", "i": "ی", "u": "و"}

# Symbols used by the Homo-GE2PE/GE2PE output convention.

RAW2CANON = {"/": "a", "a": "A", "@": "?", "$": "S", "c": "C"}

CAND = {
    "?": set("اأإؤئءع"),
    "b": set("ب"), "p": set("پ"), "t": set("تط"),
    "s": set("سصث"), "j": set("ج"), "C": set("چ"),
    "h": set("هح"), "x": set("خ"), "d": set("د"),
    "z": set("زذضظ"), "r": set("ر"), "Z": set("ژ"),
    "S": set("ش"), "q": set("قغ"), "G": set("قغ"),
    "g": set("گ"), "k": set("ک"), "l": set("ل"),
    "m": set("م"), "n": set("ن"), "f": set("ف"),
    "v": set("و"), "y": set("ی"),

}

PERSIAN = re.compile(
    "[\u0621-\u063A\u0641-\u064A\u067E\u0686\u0698\u06A9\u06AF\u06CC\u06C0"
    + ZWNJ + "]+"

)

_DIAC = re.compile("[\u064B-\u065F\u0670\u0640]")

def _normalize(text: str) -> str:
    """Normalize common Arabic/Persian letter variants and remove old marks."""
    for old, new in (("ي", "ی"), ("ى", "ی"), ("ك", "ک"), ("ة", "ه"), ("ۀ", "ه")):
        text = text.replace(old, new)
    return _DIAC.sub("", text)

def _to_canonical(raw: str):
    """Convert model symbols to internal symbols and extract the ezafe flag."""
    ezafe = raw.endswith(("1", "۱"))
    if ezafe:
        raw = raw[:-1]
    return "".join(RAW2CANON.get(ch, ch) for ch in raw), ezafe

def _strip_ezafe(phon: str, word: str) -> str:
    """Remove the model's appended ezafe sequence before letter alignment."""
    if phon.endswith("e"):
        phon = phon[:-1]
    if phon.endswith("y") and word and word[-1] in "اوهی":
        phon = phon[:-1]
    return phon

def _silent_vav(letters: str, index: int, phoneme: str, previous: Optional[str]) -> bool:
    """Recognize the limited silent-vav patterns supported by this converter."""
    if letters[index] != "و" or phoneme in ("u", "v"):
        return False
    if previous == "o":
        return True
    return (
        index > 0 and letters[index - 1] == "خ"
        and index + 1 < len(letters) and letters[index + 1] in "اآیه"
    )

def _valid_unpronounced_tail(tail: str, out, previous_phoneme: Optional[str]) -> bool:
    """Allow only narrowly justified orthographic letters left at word end.
    Final ه may be the spelling of the preceding /e/; final و may accompany
    a short /o/ in spellings such as تو/دو. Other unmatched letters are rejected.
    """
    if not tail:
        return True
    if tail == "ه" and out and out[-1][2] and KASRA in out[-1][1]:
        return True
    if tail == "و" and out and out[-1][2] and previous_phoneme == "o":
        return True
    # In this model convention, a short /a/ can align with final ا (را، ما، اما).
    if tail == "ا" and out and out[-1][2] and FATHA in out[-1][1] and previous_phoneme == "a":
        return True
    return False

def _align_word(word: str, phon: str, shadda: bool = False):
    """Return [letter, marks, carries_consonant] entries, or None on mismatch."""
    if not word or not phon:
        return None
    letters = word
    out = []
    i = j = 0
    previous = None
    previous_was_duplicated = False
    while j < len(phon):
        p = phon[j]
        # Every model symbol must be explicitly known. Unknown symbols are errors.
        if p not in SHORT and p not in LONG and p not in CAND:
            return None
        if p in SHORT:
            # A short vowel must attach to the immediately preceding consonant.
            if not out or not out[-1][2]:
                return None
            # Do not silently overwrite a second vowel on the same consonant.
            if any(mark in out[-1][1] for mark in (FATHA, KASRA, DAMMA)):
                return None
            out[-1][1] += SHORT[p]
            previous = p
            previous_was_duplicated = False
            j += 1
            continue
        # A repeated consonant is a geminate: exactly two consecutive copies.
        if p not in LONG and p == previous:
            if previous_was_duplicated or not out or not out[-1][2]:
                return None
            if shadda and SHADDA not in out[-1][1]:
                out[-1][1] = SHADDA + out[-1][1]
            previous_was_duplicated = True
            j += 1
            continue
        while i < len(letters) and _silent_vav(letters, i, p, previous):
            out.append([letters[i], "", False])
            i += 1
        if i >= len(letters):
            return None
        letter = letters[i]
        if letter == "آ":
            if p == "?" and j + 1 < len(phon) and phon[j + 1] == "A":
                out.append(["آ", "", False])
                i += 1
                j += 2
                previous = "A"
                previous_was_duplicated = False
                continue
            if p == "A":
                out.append(["آ", "", False])
                i += 1
                j += 1
                previous = "A"
                previous_was_duplicated = False
                continue
            return None
        if p in LONG:
            if letter == LONG[p]:
                out.append([letter, "", False])
                i += 1
                j += 1
                previous = p
                previous_was_duplicated = False
                continue
            # In the GE2PE output, canonical A can correspond either to written
            # alif/آ or to a short /a/ on the preceding consonant (e.g. @ali -> علی).
            # Resolve it from the spelling: if there is no alif to consume,
            # attach fatha to the preceding consonant and keep the current letter.
            if p == "A" and out and out[-1][2] and not any(
                mark in out[-1][1] for mark in (FATHA, KASRA, DAMMA)
            ):
                out[-1][1] += FATHA
                j += 1
                previous = p
                previous_was_duplicated = False
                continue
            return None
        candidates = CAND[p]
        if letter not in candidates:
            return None
        out.append([letter, "", True])
        i += 1
        j += 1
        previous = p
        previous_was_duplicated = False
    tail = letters[i:]
    if not _valid_unpronounced_tail(tail, out, previous):
        return None
    out.extend([[ch, "", False] for ch in tail])
    return out

def _add_ezafe(out):
    """Add ezafe to the aligned word. The caller guarantees non-empty output."""
    if not out:
        return
    char, marks, carries = out[-1]
    if not carries and char == "ه":
        out.extend([[ZWNJ, "", False], ["ی", KASRA, False]])
    elif not carries and char in "او":
        out.append(["ی", KASRA, False])
    elif KASRA not in marks:
        out[-1][1] += KASRA

def _render(out):
    return "".join(letter + marks for letter, marks, _ in out)

def _do_word(piece, raw_token, shadda=False):
    phon, ezafe = _to_canonical(raw_token)
    if ezafe:
        phon = _strip_ezafe(phon, piece)
    aligned = _align_word(piece, phon, shadda)
    if aligned is None:
        return piece
    if ezafe:
        _add_ezafe(aligned)
    return _render(aligned)

def _pieces(chunk: str):
    return [part for part in chunk.split(ZWNJ) if part]

def _map_tokens_to_words(words, tokens, shadda=False):
    """Map model tokens to words, allowing one token to contain several words.

    GE2PE occasionally omits a space between adjacent words (for example,
    ``rahdur`` for ``راه دور``). Split such a token only where each resulting
    phoneme piece can be aligned with its corresponding written word.
    """
    failed = object()
    cache = {}

    def can_align(word, raw):
        phon, ezafe = _to_canonical(raw)
        if ezafe:
            phon = _strip_ezafe(phon, word)
        return _align_word(word, phon, shadda) is not None

    def solve(word_index, token_index, offset):
        state = (word_index, token_index, offset)
        if state in cache:
            return cache[state]

        while token_index < len(tokens) and offset == len(tokens[token_index]):
            token_index += 1
            offset = 0

        if word_index == len(words):
            answer = () if token_index == len(tokens) else failed
            cache[state] = answer
            return answer
        if token_index >= len(tokens):
            cache[state] = failed
            return failed

        token = tokens[token_index]
        for end in range(offset + 1, len(token) + 1):
            piece = token[offset:end]
            if not can_align(words[word_index], piece):
                continue
            if end == len(token):
                next_token, next_offset = token_index + 1, 0
            else:
                next_token, next_offset = token_index, end
            rest = solve(word_index + 1, next_token, next_offset)
            if rest is not failed:
                answer = (piece,) + rest
                cache[state] = answer
                return answer

        cache[state] = failed
        return failed

    mapped = solve(0, 0, 0)
    return None if mapped is failed else list(mapped)


def _diacritize_segment(segment: str, raw_phonemes: str, shadda=False):
    tokens = raw_phonemes.split()
    chunks = list(PERSIAN.finditer(segment))
    words = [piece for match in chunks for piece in _pieces(match.group())]
    # Contextual corrections retained from the working version.
    if len(tokens) == len(words):
        for i, word in enumerate(words):
            if word == "رفتم":
                tokens[i] = "r/ft/m"
            elif word == "مردم" and i + 1 < len(words) and words[i + 1] == "از":
                tokens[i] = "mardom"

    mapped_tokens = _map_tokens_to_words(words, tokens, shadda)
    if mapped_tokens is None:
        return None

    result, position, token_index = [], 0, 0
    for match in chunks:
        result.append(segment[position:match.start()])
        converted = [
            _do_word(piece, mapped_tokens[token_index + i], shadda)
            for i, piece in enumerate(_pieces(match.group()))
        ]
        token_index += len(converted)
        result.append(ZWNJ.join(converted))
        position = match.end()
    result.append(segment[position:])
    return "".join(result)

_G2P = None

_G2P_PATH = None

def _load_g2p(model_path="./homo-ge2pe"):
    global _G2P, _G2P_PATH
    resolved_path = os.path.abspath(model_path)
    if _G2P is None or _G2P_PATH != resolved_path:
        from GE2PE import GE2PE
        _G2P = GE2PE(model_path=model_path)
        _G2P_PATH = resolved_path
    return _G2P

def _split_segments(text: str, max_words: int = 40):
    """Split text without losing characters; ignore decimal points.
    Sentences/newlines are preferred boundaries. Very long sentences are then
    divided at Persian-word boundaries so the model never receives an enormous
    paragraph in one request.
    """
    if not text:
        return []
    sentence_parts = []
    start = 0
    for i, char in enumerate(text):
        boundary = char == "\n" or char in "!؟?؛"
        if char == ".":
            is_decimal = (
                i > 0 and i + 1 < len(text)
                and text[i - 1].isdigit() and text[i + 1].isdigit()
            )
            boundary = not is_decimal
        if boundary:
            sentence_parts.append(text[start:i + 1])
            start = i + 1
    if start < len(text):
        sentence_parts.append(text[start:])
    # Keep all original whitespace and punctuation. Split oversized parts only
    # immediately before a Persian token, never inside a word/ZWNJ compound.
    result = []
    for part in sentence_parts:
        matches = list(PERSIAN.finditer(part))
        if len(matches) <= max_words:
            if part:
                result.append(part)
            continue
        chunk_start = 0
        words_in_chunk = 0
        for match in matches:
            count = len(_pieces(match.group()))
            if words_in_chunk and words_in_chunk + count > max_words:
                result.append(part[chunk_start:match.start()])
                chunk_start = match.start()
                words_in_chunk = 0
            words_in_chunk += count
        if chunk_start < len(part):
            result.append(part[chunk_start:])
    return [part for part in result if part]

def _model_input(segment: str):
    return " ".join(
        piece
        for match in PERSIAN.finditer(segment)
        for piece in _pieces(match.group())
    )

def _safe_generate(g2p, inputs, use_rules=False):
    """Run batch inference; retry failed or malformed items one by one."""
    if not inputs:
        return []
    try:
        outputs = g2p.generate(inputs, use_rules=use_rules)
    except Exception:
        outputs = None
    if isinstance(outputs, (list, tuple)) and len(outputs) == len(inputs):
        results = [x if isinstance(x, str) else "" for x in outputs]
    else:
        results = [""] * len(inputs)
    for i, item in enumerate(inputs):
        if results[i].strip():
            continue
        try:
            one = g2p.generate([item], use_rules=use_rules)
            if isinstance(one, (list, tuple)) and len(one) == 1 and isinstance(one[0], str):
                results[i] = one[0]
        except Exception:
            pass
    return results

def _diacritize_individually(segment, g2p):
    """Last-resort fallback: infer each Persian word separately."""
    result, position = [], 0
    for match in PERSIAN.finditer(segment):
        result.append(segment[position:match.start()])
        converted = []
        for piece in _pieces(match.group()):
            raw = _safe_generate(g2p, [piece])[0]
            converted.append(_do_word(piece, raw) if raw.strip() else piece)
        result.append(ZWNJ.join(converted))
        position = match.end()
    result.append(segment[position:])
    return "".join(result)

def diacritize(text: str) -> str:
    """Add Persian diacritics to text using the cached Homo-GE2PE model."""
    if not text:
        return text
    g2p = _load_g2p()
    normalized = _normalize(text)
    segments = _split_segments(normalized)
    inputs = [_model_input(segment) for segment in segments]
    indices = [i for i, item in enumerate(inputs) if item]
    generated = _safe_generate(g2p, [inputs[i] for i in indices])
    raw_by_index = dict(zip(indices, generated))
    output = []
    for i, segment in enumerate(segments):
        raw = raw_by_index.get(i, "")
        if not raw.strip():
            output.append(segment)
            continue
        converted = _diacritize_segment(segment, raw)
        if converted is None:
            words = inputs[i].split()
            individual = _safe_generate(g2p, words)
            if len(individual) == len(words) and all(x.strip() for x in individual):
                converted = _diacritize_segment(segment, " ".join(individual))
        if converted is None:
            converted = _diacritize_individually(segment, g2p)
        output.append(converted)
    return "".join(output)
