# Medicortex-AI: Agentic RAG-based Medical Assistance System

Medicortex-AI is an advanced medical and healthcare assistance platform built on an Agentic Retrieval-Augmented Generation (RAG) architecture. The system orchestrates multiple intelligent agents to provide evidence-based diagnostics, patient data retrieval, research paper search, and medical report analysis. By leveraging both machine learning and large language models, Medicortex-AI overcomes the limitations of traditional, non-agentic medical pipelines, delivering robust, explainable, and extensible clinical decision support.

## Key Features

- **PubMed Research Paper Retrieval:**
  - Retrieve and summarize relevant medical research papers from PubMed using natural language queries.
- **Symptom and Disease Diagnostics:**
  - Predict diseases based on user-provided symptoms using a Random Forest Classifier trained on a comprehensive medical dataset.
  - Generate actionable, evidence-based recommendations for patients.
- **Patient Data Analysis and Retrieval:**
  - Search and analyze patient records by ID, name, or semantic queries using Qdrant vector search and OpenAI embeddings.
  - Provide structured patient summaries and AI-generated recommendations.
- **Medical Report and Scan Analysis:**
  - Analyze PDF medical reports and diagnostic images (X-ray, MRI, etc.) using specialized agents and language models.
  - Extract key findings and generate recommendations from unstructured data.
- **Agentic Orchestration:**
  - Intelligent handoff between specialized agents (diagnosis, retrieval, follow-up, literature search, report analysis) for seamless workflow automation.
- **Guardrails and Query Analysis:**
  - Automatic detection and filtering of non-medical queries to ensure system focus and safety.

## Performance Benchmarks

Based on internal evaluation and benchmark results:

- **Diagnosis Prediction Model:**
  - Model: Random Forest Classifier
  - Dataset: [Medicine Recommendation System Dataset](https://www.kaggle.com/datasets/noorsaeed/medicine-recommendation-system-dataset)
  - Diseases predicted: 41
  - Symptoms: 133
  - Accuracy: 100.0%
  - F1 Score: 1.0

- **GPT Model Benchmarks:**
  | Benchmark      | MedQA | MMMU  | MMLU Pro |
  |---------------|-------|-------|----------|
  | GPT 4o mini   | 72.4% | 58.2% | 62.7%    |
  | GPT 4.1 mini  | 84.6% | 71.1% | 77.2%    |

- **Orchestrator Agent:**
  - Identification of non-medical questions: 100%
  - Handoff accuracy: 100%
  - Example handoffs:
    - "Latest treatments for Diabetes?" → PubMed Retriever
    - "Show lab reports for patient 1234" → Patient Retriever
    - "What meds was that patient prescribed?" → Follow Up Agent
    - "I have a headache and high fever, what is it?" → Diagnosis
    - "What's the capital of France?" → None (filtered)

## Setup Instructions

### Local Setup

1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd Medicortex-AI
   ```
2. **Create and activate a Python environment (recommended):**
   ```sh
   conda create -n medicortex-ai python=3.13.2
   conda activate medicortex-ai
   ```
3. **Install dependencies:**
   ```sh
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Ensure model files and data are present in the correct folders.**
5. **Run the Streamlit app:**
   ```sh
   streamlit run src/user_interface.py
   ```
6. **Access the app:**
   - Open your browser and go to `http://localhost:8501`

### Docker Setup

1. **Build the Docker image:**
   ```sh
   docker build -t medicortex-ai:latest .
   ```
2. **(Optional) Test locally:**
   ```sh
   docker run -p 8501:8501 medicortex-ai:latest
   ```
3. **Save and transfer the image to your server (if needed):**
   ```sh
   docker save -o medicortex-ai.tar medicortex-ai:latest
   scp medicortex-ai.tar username@<ip address>:~/MediCortex_AI/
   ssh username@ip address
   cd ~/MediCortex_AI
   docker load -i medicortex-ai.tar
   ```
4. **(Recommended) Use Docker Compose for production:**
   - Create a `docker-compose.yaml` in `~/MediCortex_AI`:
     ```yaml
     services:
       medicortex-ai:
         image: medicortex-ai:latest
         container_name: medicortex-ai
         ports:
           - "8501:8501"
         restart: unless-stopped
         working_dir: /app
         environment:
           - STREAMLIT_SERVER_HEADLESS=true
           - STREAMLIT_SERVER_PORT=8501
           - STREAMLIT_SERVER_ADDRESS=0.0.0.0
           - QDRANT_HOST=localhost  # or 'qdrant' if using a Qdrant service in compose
           - QDRANT_PORT=6333
     ```
   - Start the service:
     ```sh
     docker compose up -d
     ```
5. **Access the app:**
   - Open your browser and go to `http://<ip address>:8501` (or your server's IP/URL)

## Notes

- Ensure all model and data files are present before building the Docker image.
- For Qdrant or other external services, set the appropriate environment variables in your compose file or `.env`.
- For production, consider using a reverse proxy (e.g., Nginx) for HTTPS and domain routing.

- ### Personal Setup

    - Project developed on Windows 11 with Ryzen 9 7940HS, 16GB RAM, and NVIDIA RTX 4070 Laptop GPU.
    - Dockerized and hosted on my personal Linux based homeserver (Ubuntu)
    - Data pipelined into server hosted Qdrant server for Patient data (Check `\src\data\data_loader.ipynb`)

---
For more details, see the code and documentation in each module.