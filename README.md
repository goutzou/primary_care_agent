# Primary Care Triage Assistant

A lightweight, safety-first primary-care triage assistant built with a React frontend, FastAPI backend, and an LLM constrained through strict templates and validation.  
The system simulates a structured primary-care consultation, performs red-flag detection, and produces safe, deterministic clinical guidance.

---

## Features

- Two-stage consultation flow (intake → triage)
- Rule-based emergency detection (regex + severity scoring)
- Strict template-validated LLM responses (intake, mild, emergency)
- Safety fallback for malformed outputs
- React chat UI with structured message formatting
- Fully deterministic backend orchestration layer

---

## Tech Stack

- **Frontend:** React + Vite
- **Backend:** FastAPI (Python)
- **LLM:** OpenAI API (`gpt-4o-mini` by default)
- **Runtime:** Node, Python 3.9+

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/primary-care-agent.git
cd primary-care-agent
```

### 2. Create Python virtual environment

python3 -m venv .venv

source .venv/bin/activate

pip install -r backend/requirements.txt

### 3. Set up environment variables

Create a .env file inside backend/:

OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o

### 4. Install frontend dependencies

cd frontend

npm install

cd ..

### Running the System

From the project root:

./run.sh

This automatically launches:

Backend on http://localhost:8000

Frontend on http://localhost:5173

Open your browser to localhost:5173 to start chatting.
