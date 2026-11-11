
# OpsPilot AI
### AI-Powered IT Incident Diagnosis and Resolution Assistant

OpsPilot AI is a local AI-powered prototype designed to help IT teams analyse incidents, identify possible technical causes, retrieve relevant troubleshooting knowledge, and plan investigation steps.

It combines a Large Language Model (LLM) with Retrieval-Augmented Generation (RAG) to provide structured, evidence-aware incident analysis.

## Problem Statement

IT teams often receive incident reports containing incomplete or unstructured information. Identifying possible causes and deciding what to investigate next can take time.

OpsPilot AI aims to organise incident information and assist technicians by generating structured analysis supported by relevant technical knowledge documents.

## Key Features

- Incident submission through a Streamlit interface.
- Incident classification based on the affected service.
- AI-generated incident summaries and possible technical causes.
- Retrieval of relevant troubleshooting information using RAG.
- Evidence references showing the source knowledge documents.
- Ordered troubleshooting and investigation recommendations.
- Initial severity based on the reported business impact.
- Human review and approval emphasis before production-changing actions.
- Local AI inference without a paid external LLM API.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | User interface |
| Ollama | Local LLM execution |
| Qwen 2.5 3B | Incident analysis |
| ChromaDB | Vector database |
| nomic-embed-text | Text embeddings |
| PyMuPDF | PDF text extraction |
| Git and GitHub | Version control |

## How It Works

1. **Incident Submission:** The user enters the incident title, description, affected service and business impact.
2. **Incident Classification:** The application identifies the incident category.
3. **Knowledge Retrieval:** ChromaDB retrieves relevant information from the technical knowledge documents.
4. **AI Analysis:** The local Qwen model analyses the incident using the supplied details and retrieved context.
5. **Report Generation:** OpsPilot AI generates a structured incident report.
6. **Human Review:** A qualified technician reviews the evidence and recommendations before approving any production-changing action.

## Architecture

```text
User
  |
  v
Streamlit Interface
  |
  v
Incident Classification
  |
  v
Knowledge Retrieval
  |
  +------> ChromaDB
  |           |
  |           v
  |     Technical Documents
  |
  v
Retrieved Context + Incident Details
  |
  v
Ollama - Qwen 2.5 3B
  |
  v
AI Incident Analysis
  |
  v
Structured Incident Report
  |
  v
Human Review and Approval
```

## Project Structure

```text
OpsPilot-AI/
|
├── app.py
├── knowledge_base.py
├── requirements.txt
├── README.md
|
├── data/
|   ├── incident_troubleshooting_guide.md
|   └── database_troubleshooting_guide.md
|
└── chroma_db/
```

The `chroma_db/` directory is generated locally when the knowledge base is processed. It is excluded from version control.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/archasunil1111-jpg/OpsPilot-AI.git
cd OpsPilot-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama Models

Install Ollama from:

https://ollama.com/

Pull the required models:

```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

Ensure Ollama is running before starting the application.

### 5. Build the Knowledge Base

```bash
python knowledge_base.py
```

This processes the supported Markdown and PDF documents inside the `data/` directory and stores their embeddings in ChromaDB.

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

## Current Knowledge Base

The prototype currently includes technical troubleshooting documents covering:

- HTTP 503 Service Unavailable incidents.
- Database connectivity and connection failures.

Additional technical knowledge documents can be added to the `data/` directory.

## Testing

The application has been tested with two sample incident scenarios:

**1. Website returning HTTP 503 error**
- Website availability incident classification.
- Retrieval of the HTTP 503 troubleshooting guide.
- Generation of possible causes and investigation steps.

**2. Application unable to connect to database**
- Database connectivity incident classification.
- Retrieval of the database troubleshooting guide.
- Generation of database-specific investigation steps.

These tests demonstrate the current prototype's incident analysis and knowledge retrieval workflow.

## Limitations

- This is a local prototype, not a production IT monitoring platform.
- It does not connect to live company infrastructure or monitor real servers.
- Its analysis depends on the information supplied by users and the available knowledge documents.
- AI-generated causes are hypotheses and require technical verification.
- It does not automatically execute repairs or modify production systems.
- The local model's response speed depends on available hardware resources.

## Future Improvements

- Support for additional incident categories and technical knowledge sources.
- Improved retrieval relevance and source-level filtering.
- Downloadable incident reports.
- Automated evaluation of diagnosis quality.
- More comprehensive validation and safety controls.
- Integration with authorised IT service management platforms.

## Responsible AI and Human Oversight

OpsPilot AI is designed as a decision-support assistant. Its output should not be treated as a confirmed root-cause diagnosis.

Technicians must validate evidence, review recommendations and approve production-changing actions.

---

**Project:** OpsPilot AI  
**Version:** 1.9  
**Developed as an individual AI project.**
