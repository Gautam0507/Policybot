# Policy Chatbot - Setup Instructions

## 1. Clone the Repository

```sh
git clone <your-repo-url>
cd RAG_app
```

---

## 2. Create and Activate a Virtual Environment

```sh
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Python Dependencies

```sh
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Install System Dependencies for PDF Processing

Make sure you have the following system packages installed (required by `unstructured`):

**Ubuntu/Debian:**

```sh
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr libmagic1 build-essential
```

---

## 5. Run Ollama Server and Pull Llama 3.1 8B Model

**Start the Ollama server (listening on all interfaces):**

```sh
OLLAMA_HOST=0.0.0.0 ollama serve
```

**Pull the Llama 3.1 8B model:**

```sh
ollama pull llama3.1:8b
```

---

## 6. Run the Application

```sh
streamlit run streamlit_app.py
```

Then open your browser and go to [http://localhost:8501](http://localhost:8501)

---

## 7. Notes

- Make sure your `config.py` is set to use the correct Ollama model name (e.g., `llama3:8b`).
- If you change the model in `config.py`, pull it with `ollama pull <model-name>`.
- Ollama must be running for the chatbot to generate answers.
- Uploaded PDFs and embeddings are stored in the [`data`](data) directory.
