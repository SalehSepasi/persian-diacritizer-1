<div align="center">

# 🖋️ Persian Diacritizer

**Add diacritics (اعراب) to Persian text, powered by context-aware G2P.**

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![uv](https://img.shields.io/badge/managed%20with-uv-6C47FF)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-CPU%20only-EE4C2C?logo=pytorch&logoColor=white)
![Model](https://img.shields.io/badge/Model-Homo--GE2PE-FFD21E?logo=huggingface&logoColor=black)

</div>

---

A Python-based Persian text diacritization tool powered by [Homo-GE2PE](https://github.com/MahtaFetrat/Homo-GE2PE-Persian).

The project uses a Persian Grapheme-to-Phoneme (G2P) model to help determine word pronunciations and converts its output into Persian text with diacritics.

## 📑 Table of Contents

- [✨ Features](#-features)
- [📋 Requirements](#-requirements)
- [🚀 Installation](#-installation)
- [▶️ Running the Application](#️-running-the-application)
- [🧠 Model Information](#-model-information)
- [📝 Notes](#-notes)
- [⚖️ License and Attribution](#️-license-and-attribution)

## ✨ Features

- 🔤 Persian text diacritization.
- 🧩 Context-aware pronunciation through Homo-GE2PE.
- 💻 CPU-based model inference (no NVIDIA GPU or CUDA required).
- 📦 Python environment and dependency management with [uv](https://docs.astral.sh/uv/).

## 📋 Requirements

| Requirement | Notes |
|---|---|
| 🐍 Python 3.11 | Required Python version |
| ⚡ [uv](https://docs.astral.sh/uv/getting-started/installation/) | Environment and dependency manager |
| 🌿 Git | Used to clone the project and the model repository |
| 📂 Unzip utility | Used to extract model weights and resources |

> 💡 The project is configured to use the **CPU version** of PyTorch.

## 🚀 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/SalehSepasi/persian-diacritizer-1.git
cd persian-diacritizer-1
```

### 2️⃣ Install dependencies

```bash
uv sync
```

This command creates the project environment and installs the required dependencies, including CPU-only PyTorch.

### 3️⃣ Download the model files (very important ⚠️)

This project uses the **Homo-GE2PE** model from its official Hugging Face repository.

Clone the model repository:

```bash
git clone https://huggingface.co/MahtaFetrat/Homo-GE2PE-Persian/
```

Extract the required model weights and Parsivar resources:

```bash
unzip -q Homo-GE2PE-Persian/assets/Parsivar.zip
unzip -q Homo-GE2PE-Persian/model-weights/homo-ge2pe.zip -d homo-ge2pe
unzip -q Homo-GE2PE-Persian/model-weights/homo-t5.zip -d homo-t5
```

Move the model inference script into the project directory:

```bash
mv Homo-GE2PE-Persian/assets/GE2PE.py ./
```

> 📌 **Note:** This project uses the Homo-GE2PE checkpoint (`homo-ge2pe`), not the alternative Homo-T5 checkpoint.

### 4️⃣ Apply the Parsivar compatibility fix

The original model repository documents the following compatibility fix for Parsivar:

```bash
sed -i 's/from collections import Iterable/from collections.abc import Iterable/g' Parsivar/token_merger.py
```

Apply this change if the corresponding import exists in your downloaded Parsivar version.

## ▶️ Running the Application

```bash
uv run streamlit run app.py
```

> If the Streamlit entry-point file has a different name, replace `app.py` with its actual filename.

## 🧠 Model Information

Homo-GE2PE is a Persian Grapheme-to-Phoneme model designed to handle pronunciation ambiguities (homographs) using context.

| | |
|---|---|
| 🤖 **Model** | [MahtaFetrat/Homo-GE2PE-Persian](https://huggingface.co/MahtaFetrat/Homo-GE2PE-Persian) |
| 💾 **Source code** | [GitHub Repository](https://github.com/MahtaFetrat/Homo-GE2PE-Persian) |
| 📊 **Dataset** | [HomoRich](https://huggingface.co/datasets/MahtaFetrat/HomoRich-G2P-Persian) |
| 📄 **Research paper** | [Fast, Not Fancy: Rethinking G2P with Rich Data and Rule-Based Models](https://arxiv.org/abs/2505.12973) |

The model is used as a pronunciation component; the Persian diacritization and text-processing logic in this project are separate from the original model.

## 📝 Notes

- 📥 Model weights and external resources are downloaded separately and are not included in this project's Git repository.
- 🌐 The first model download requires an internet connection.
- 🐢 Inference is configured for CPU execution and may be slower than GPU-based inference.
- 🎯 Model predictions are not guaranteed to be linguistically correct in every context.
- 🔐 The bundled Parsivar archive contains serialized resources. Review and trust the upstream source before extracting and loading them.

## ⚖️ License and Attribution

This project uses the Homo-GE2PE model and related resources. Please refer to the original repositories for their licenses, attribution requirements, and usage conditions.

🙏 All credit for the original model and research belongs to its respective authors.