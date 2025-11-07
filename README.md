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
