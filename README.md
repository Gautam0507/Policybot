# RAG_app

A Retrieval-Augmented Generation (RAG) application for extracting and answering questions from Policy documents using LLMs.

**Python version used for this project: 3.12.11**

---

## Installation & Usage

<details>
<summary><strong>Docker Installation </strong></summary>

1. **Clone the repository**

   ```bash
   git clone https://github.com/Gautam0507/Policybot.git
   cd Policybot
   ```

2. **Host Ollama on Your Machine**

   - Ensure Ollama is running on your host at port `11434`.
   - If you don't have Ollama installed, follow instructions at [https://ollama.com/download](https://ollama.com/download).
   - Start Ollama with:
     ```bash
     OLLAMA_HOST=0.0.0.0 ollama serve
     ```
   - (Optional) Pull the model, e.g.:
     ```bash
     ollama pull llama3.1:8b
     ```
   - The app inside Docker will connect to Ollama using the special host IP `172.17.0.1:11434` (Linux) or `host.docker.internal:11434` (if supported).

3. **Enable GPU Access**

   - Install NVIDIA Container Toolkit (for GPU support):
     ```bash
     sudo apt-get install -y nvidia-container-toolkit
     sudo systemctl restart docker
     ```
   - Edit `/etc/docker/daemon.json` to include:
     ```json
     {
       "runtimes": {
         "nvidia": {
           "path": "nvidia-container-runtime",
           "runtimeArgs": []
         }
       }
     }
     ```
   - Restart Docker after editing:
     ```bash
     sudo systemctl restart docker
     ```

4. **Start and Build the App**

   ```bash
   docker-compose up --build
   ```

   This will:

   - Build the Docker image.
   - Start the app at [http://localhost:8501](http://localhost:8501).

5. **Access the logs**

   - To enter the running Docker container and view logs:

     ```bash
     docker exec -it rag_app tail -f app.log
     ```

</details>

<details>
<summary><strong>Python Virtual Environment Installation</strong></summary>

1. **Clone the repository**

   ```bash
   git clone https://github.com/Gautam0507/Policybot.git
   cd Policybot
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Host Ollama on Your Machine**

   - Ensure Ollama is running on your host at port `11434`.
   - If you don't have Ollama installed, follow instructions at [https://ollama.com/download](https://ollama.com/download).
   - Start Ollama with:
     ```bash
     OLLAMA_HOST=0.0.0.0 ollama serve
     ```
   - (Optional) Pull the model, e.g.:
     ```bash
     ollama pull llama3.1:8b
     ```

5. **Start the app**

   ```bash
   streamlit run streamlit_app.py
   ```

   The app will be available at [http://localhost:8501](http://localhost:8501).

6. **Access the logs**

   - To view logs from the project root directory:
     ```bash
     tail -f app.log
     ```

   </details>

## Notes

- For Docker, the app expects Ollama to be running on the host and accessible from the container.
- If you encounter network issues, check your Docker network settings and ensure the correct host IP is used.
- Make sure your `config.py` is set to use the correct Ollama model name (e.g., `llama3.1:8b`).
- If you change the model in `config.py`, pull it with `ollama pull <model-name>`.
- Ollama must be running for the chatbot to generate answers.
- Uploaded PDFs and embeddings are stored in the [`data`](data) directory.
