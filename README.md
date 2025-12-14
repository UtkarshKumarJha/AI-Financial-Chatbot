
# 📈 InsightInvest — AI-Powered Financial Analyst

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![AWS](https://img.shields.io/badge/deployed%20on-AWS-orange)
![License](https://img.shields.io/badge/license-MIT-green)

**InsightInvest** is a production-grade, microservices-based AI financial chatbot that delivers actionable stock insights using real-time news analysis, Retrieval-Augmented Generation (RAG), and quantitative sentiment modeling.

Unlike simple LLM wrappers, this system is engineered for **scalability and responsiveness**, leveraging asynchronous task queues to handle heavy AI workloads without blocking user requests.

---

## 🏗️ System Architecture

The application follows a **microservices architecture**, fully containerized with Docker and deployed on **AWS EC2**.

```mermaid
graph TD
    User["User (Browser)"] -->|HTTP/REST| Frontend["React + Vite Frontend"]
    Frontend -->|Requests| API["FastAPI Backend Server"]
    
    subgraph "Async Processing Layer"
        API -->|Push Task| Broker["RabbitMQ Message Broker"]
        Broker -->|Pull Task| Worker["Celery Worker Nodes"]
        Worker -->|Sentiment Analysis| FinBERT["FinBERT Model"]
    end
    
    subgraph "Data & State"
        API -->|Cache/State| Redis["Redis"]
        Worker -->|Store Results| Redis
        API -->|Vector Search| Chroma["ChromaDB (RAG Store)"]
        API -->|Fetch Financial News| NewsAPI
        API -->|Fetch Stock History| yFinance
    end
    
    subgraph "External AI"
        Worker -->|LLM Inference| Gemini["Google Gemini API"]
    end
````

---

## 🚀 Key Features

* **🧠 RAG-Powered Chat**
  Retrieves relevant financial context from ChromaDB before generating responses using Google Gemini.

* **⚡ Asynchronous AI Pipelines**
  Heavy sentiment analysis is offloaded using **Celery + RabbitMQ**, keeping the API fast and non-blocking.

* **📊 Financial Sentiment Engine**
  Analyzes financial news using **FinBERT** to classify market sentiment (Bullish / Bearish / Neutral).

* **🐳 Fully Containerized**
  Each service runs in its own Docker container and is orchestrated via Docker Compose.

* **☁️ Cloud-Native & CI/CD Ready**
  Automated builds with GitHub Actions and deployment on AWS EC2 with restart policies.

---

## 🛠️ Tech Stack

| Component   | Technology                                         |
| ----------- | -------------------------------------------------- |
| Frontend    | React.js, Vite, Tailwind CSS                       |
| Backend API | Python, FastAPI, Pydantic, NewsAPI, yFinance       |
| AI / LLM    | LangChain, Google Gemini, HuggingFace Transformers |
| Task Queue  | Celery, RabbitMQ                                   |
| Databases   | ChromaDB (Vector), Redis (Cache / Results)         |
| DevOps      | Docker, Docker Compose, AWS EC2, GitHub Actions    |

---

## 🔌 Installation & Local Setup

### Prerequisites

* Docker & Docker Desktop
* Git

### 1. Clone the Repository

```bash
git clone https://github.com/UtkarshKumarJha/AI-Financial-Chatbot.git
cd AI-Financial-Chatbot
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```ini
# AI Configuration
GOOGLE_API_KEY=your_gemini_api_key

# Infrastructure
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Vector Database
CHROMA_DB_HOST=chromadb
CHROMA_DB_PORT=8000
```

### 3. Launch with Docker Compose

This command starts all services:
Frontend, Backend API, Celery Worker, Redis, RabbitMQ, and ChromaDB.

```bash
docker compose up --build
```

Access the application at:
`http://localhost:5173`

---

## 📡 API Endpoints

| Method | Endpoint                | Description                       |
| ------ | ----------------------- | --------------------------------- |
| POST   | `/api/chat`             | Main RAG chat endpoint            |
| POST   | `/api/analyze`          | Triggers async sentiment analysis |
| GET    | `/api/status/{task_id}` | Fetches background task status    |
| GET    | `/health`               | Health check endpoint             |

---

## 🔮 Future Improvements

* Live stock price streaming using WebSockets
* OAuth2 / JWT authentication for personalized portfolios
* Migration to Kubernetes for auto-scaling worker nodes

---

## 👨‍💻 Author

**Utkarsh Kumar Jha**

* GitHub: [Utkarsh Kumar Jha](https://github.com/UtkarshKumarJha)
* LinkedIn: [Utkarsh Kumar Jha](https://www.linkedin.com/in/utkarsh-kumar-jha-993773284/)
