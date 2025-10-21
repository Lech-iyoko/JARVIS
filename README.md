# VISION: A Visually-Grounded Voice Assistant

[![Project Status: In Development](https://img.shields.io/badge/status-in_development-yellowgreen.svg)](https://shields.io/)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://shields.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A portfolio project exploring how predictive world models can power a new generation of context-aware AI assistants that augment human intelligence.

---

## Demo

*[The short video demo will go here]*

## Core Thesis: Beyond Reactive AI

Today's AI assistants are powerful, but fundamentally "blind." They react to commands and analyse static snapshots of the world. This project explores a different paradigm: **predictive understanding**.

VISION is an experiment to test the hypothesis that by using a predictive world model like Meta's **V-JEPA**, we can create an assistant that learns the underlying dynamics of its environment. Instead of just describing *what is*, it builds an internal model to anticipate *what's next*. This is a step towards an AI co-pilot that offers truly contextual, proactive assistance.

*For a deeper dive into the philosophy behind this project, read my Substack post: [Link to your Substack post here]*

## System Architecture

The system is built on a modular, two-stream architecture that fuses real-time voice and vision data.

*[Your System Architecture Diagram will go here]*

1.  **🎙️ Voice Pipeline:** Handles real-time audio capture, Speech-to-Text (ASR), reasoning via an LLM, and Text-to-Speech (TTS) output.
2.  **👁️ Vision Pipeline:** Uses a webcam to feed visual data into the V-JEPA world model, which generates abstract feature embeddings representing the user's visual context.
3.  **🧠 Fusion Core:** The transcribed text and visual embeddings are combined into a single, context-rich prompt for the LLM, enabling grounded, situationally-aware responses.

## 🛠️ Tech Stack

| Component | Technology / Service |
| :--- | :--- |
| **🧠 Vision Model** | Meta's V-JEPA |
| **🗣️ Speech-to-Text (ASR)** | Deepgram (Nova-2 Model) |
| **🤖 Reasoning (LLM)** | Groq (Llama 3.1 8B Model) |
| **🔊 Text-to-Speech (TTS)** | Unreal Speech |
| **🎤 Audio Streaming** | PyAudio / SoundDevice |
| **💻 Language** | Python 3.10+ |
| **📦 Environment** | GitHub Codespaces |

## Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

* Python 3.10 or higher
* A GitHub account (for Codespaces) or a local environment with `pip`
* API keys for:
    * [Deepgram](https://console.deepgram.com)
    * [Groq](https://console.groq.com/)
    * [Unreal Speech](https://unrealspeech.com/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/jarvis-cv-beta.git](https://github.com/your-username/jarvis-cv-bet.git)
    cd jarvis-cv-beta
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your API keys:**
    * Create a file named `.env` in the root of the project.
    * Copy the contents of `.env.example` into `.env`.
    * Add your API keys to the `.env` file:
        ```env
        # .env file
        DEEPGRAM_API_KEY="YOUR_DEEPGRAM_API_KEY"
        GROQ_API_KEY="YOUR_GROQ_API_KEY"
        UNREAL_SPEECH_API_KEY="YOUR_UNREAL_SPEECH_API_KEY"
        ```

## ▶️ How to Run

Execute the main application script from the root directory:

```bash
python main.py
