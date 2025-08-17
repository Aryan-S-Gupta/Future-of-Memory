
# 🧠 Memory Simulation Backend

This repository contains the Django-based backend for the Memory Simulation narrative game. It provides REST API endpoints for retrieving static story questions and paragraphs, and serves as the foundation for future integration of RAG, LLM, and image generation modules.

---

## 🚀 Features

- Django 4.x backend scaffolded and structured for local development
- Static story content and yes/no questions (starting from year 2035)
- Two working API endpoints:
  - `/api/static-question` – returns a random yes/no question
  - `/api/static-story?year=YYYY` – returns story background for that year
- Modular folder structure for future components:
  - `rag/` for retrieval-augmented generation
  - `llm/` for local LLM integration
  - `images/` for image generation (e.g. via ComfyUI)
  - `core/` for turn logic and timeline control

---

## 🧩 Project Structure

```
├── api/                    # API endpoints and static data
│   ├── views.py
│   ├── urls.py
│   └── data/
│       ├── static_questions.json
│       └── static_stories.json
├── core/                   # (Optional) Turn system, gameplay routes
├── llm/                    # Local LLM call interface (planned)
├── rag/                    # RAG logic and prompt templates (planned)
├── images/                 # Image generation script placeholder
├── memory_sim/             # Django settings and config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/              # (Optional) Django templates if needed
├── manage.py               # Django command line runner
├── requirements.txt        # Dependencies list
├── .gitignore              # Files to be ignored by git
```

---

## 🛠️ How to Run Locally

### ✅ Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_TEAM_NAME/DECO3801---Data-Busters.git
cd DECO3801---Data-Busters
git checkout feature/backend-init
```

> Replace the branch name if using another branch.

---

### ✅ Step 2: Set Up a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
```

---

### ✅ Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### ✅ Step 4: Run Migrations

```bash
python manage.py migrate
```

---

### ✅ Step 5: Start the Development Server

```bash
python manage.py runserver
```

Then open your browser and test:

- [http://127.0.0.1:8000/api/static-question](http://127.0.0.1:8000/api/static-question)
- [http://127.0.0.1:8000/api/static-story?year=2035](http://127.0.0.1:8000/api/static-story?year=2035)

---

## 🧪 Sample API Output

### `GET /api/static-question`
```json
{
  "year": 2037,
  "question": "Would you upload your memories to the cloud in exchange for convenience?"
}
```

### `GET /api/static-story?year=2037`
```json
{
  "year": 2037,
  "story": "MemoryCloud™, a global memory storage platform, launches permanent consciousness backup in exchange for behavioral data."
}
```

---

## 👥 For Collaborators

- Please create a new branch before developing (e.g., `feature/rag-module`, `feature/llm-api`)
- Make sure to pull latest changes before working
- Don’t commit `venv/` or `.sqlite3` files — they’re excluded via `.gitignore`
- Frontend or multiplayer team members can call these endpoints for mock data until dynamic generation is live

---

## 📌 To-Do (Backend Roadmap)

- [ ] RAG embedding + chunk loader
- [ ] LLM story/question generation
- [ ] Timeline & turn loop controller
- [ ] AI image integration (ComfyUI or SD)
- [ ] Multiplayer memory sync (Socket.io)

---

## 📬 Contact

For questions, contact `@Iris` in Discord or check the `feature/backend-init` branch for updates.
