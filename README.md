JH04

# 🌉 Samadhan Setu

### Jharkhand Societal Innovation Collaboration Portal

**Samadhan Setu** is an AI-powered societal innovation platform designed to connect **citizens, Panchayati Raj Institutions (PRI), Urban Local Bodies (ULBs), government officers, universities, students, faculty, and industry/CSR organizations**.

Instead of simply closing a grievance, Samadhan Setu transforms a community problem into a **validated research and innovation project** that can move through solution development, collaboration, deployment, and measurable impact.

---

## 🎯 Problem Statement

Traditional grievance platforms primarily focus on:

```text
Complaint → Resolution → Closure
```

However, many community problems require:

- Research
- Technical solutions
- University collaboration
- Student involvement
- Industry/CSR support
- Field deployment
- Long-term monitoring
- Measurable social impact

Samadhan Setu introduces a new approach:

```text
Community Problem
       ↓
AI-Based Triage
       ↓
Human Validation
       ↓
Research / Innovation Project
       ↓
University & Student Matching
       ↓
Mentor / Industry Collaboration
       ↓
Solution Development
       ↓
Field Deployment
       ↓
Impact Measurement
```

---

## 🚀 Project Overview

Samadhan Setu acts as a bridge between **societal problems and innovation ecosystems**.

Citizens and local authorities can submit problems using:

- Text
- Voice
- Images
- Documents
- Location/GPS information

The platform uses AI-assisted classification, prioritization, duplicate detection, and university matching to help transform validated problems into actionable projects.

---

## ✨ Key Features

### 📝 Multi-Modal Problem Submission

Users can submit community problems through:

- Text descriptions
- Voice input
- Photographs
- Documents
- GPS/location information

---

### 🤖 AI-Powered Problem Classification

The platform uses machine learning to classify submitted problems and assist with appropriate routing.

The AI pipeline includes:

- TF-IDF feature extraction
- LinearSVC classification
- Calibrated predictions
- Explainable priority scoring

Human officers can review and override AI-generated decisions when necessary.

---

### 🔍 Duplicate Problem Detection

Similar submissions can be identified using a combination of:

- TF-IDF similarity
- RapidFuzz
- Haversine distance

This helps reduce duplicate complaints and allows related community problems to be grouped together.

---

### 📊 Explainable Priority Scoring

Problems can be prioritized based on multiple factors instead of relying solely on submission order.

The system provides an explainable scoring mechanism to help officers understand why a particular problem receives a higher priority.

---

### 🎓 University & Student Matching

Validated problems can be matched with suitable:

- Universities
- Departments
- Students
- Faculty
- Research teams

This converts societal problems into potential academic and research projects.

---

### 🤝 Industry & CSR Collaboration

Industry and CSR organizations can participate by providing:

- Funding
- Technical expertise
- Mentorship
- Infrastructure
- Deployment support

---

### 📋 Project Lifecycle Management

A validated problem can progress through multiple stages:

```text
Problem Submitted
       ↓
AI Triage
       ↓
Officer Validation
       ↓
Research Project Created
       ↓
University Matching
       ↓
Team Formation
       ↓
Mentorship
       ↓
Solution Development
       ↓
Deployment
       ↓
Impact Measurement
```

---

### 🔐 Secure Role-Based Access

The platform implements authentication and **role-based access control (RBAC)**.

Different users receive access according to their responsibilities.

The system supports **8 user roles** across the platform.

---

### 📱 Offline-First PWA

Samadhan Setu is designed as a **Progressive Web App (PWA)** with offline-first capabilities.

This is particularly useful for situations where internet connectivity may be unreliable.

---

### 🌐 Bilingual Support

The platform is designed to support bilingual interaction, making the system more accessible to users across different communities.

---

### 🗺️ Location-Based Visualization

Problems can be associated with geographical locations and visualized using:

- Leaflet
- OpenStreetMap
- GPS coordinates
- Haversine distance calculations

This helps identify geographical clusters and nearby problems.

---

### 🔗 Provenance & Auditability

The system maintains project provenance using a **SHA-256 hash-chain mechanism**.

This helps provide a tamper-evident history of important project events and lifecycle changes.

---

## 🧠 AI / ML Pipeline

```text
User Submission
      ↓
Text Processing
      ↓
TF-IDF Feature Extraction
      ↓
LinearSVC Classification
      ↓
Calibrated Prediction
      ↓
Priority Scoring
      ↓
Duplicate Detection
      ↓
University Matching
```

Additional techniques include:

- TF-IDF
- LinearSVC
- RapidFuzz
- Haversine distance
- TextRank
- Explainable scoring

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      Citizens        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Samadhan Setu      │
                    │       PWA            │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │      Backend         │
                    └──────────┬───────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
       ┌───────────┐     ┌───────────┐     ┌───────────┐
       │ AI / NLP  │     │ PostgreSQL│     │  Storage  │
       │ Pipeline  │     │ Database  │     │ S3-based  │
       └───────────┘     └───────────┘     └───────────┘
             │
             ▼
       ┌────────────────────────────────────────────┐
       │ Universities • Students • Faculty •        │
       │ Government • Industry • CSR • Mentors      │
       └────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Framer Motion
- Leaflet
- OpenStreetMap
- Recharts

### Backend

- FastAPI
- Python 3.12
- SQLAlchemy 2
- Alembic

### Database

- PostgreSQL
- SQLite for demonstration

### Storage

- S3-compatible object storage

### AI / Machine Learning

- TF-IDF
- LinearSVC
- RapidFuzz
- Haversine distance
- TextRank

### Authentication & Communication

- JWT Authentication
- Role-Based Access Control
- WebSockets

### Application Architecture

- Progressive Web App (PWA)
- Offline-first architecture

---

## 📁 Project Structure

```text
samadhan-setu/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── public/
│   └── ...
│
├── api/
│   ├── app/
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── ...
│
├── data/
│
├── uploads/
│
├── .gitignore
├── README.md
└── ...
```

---

## ⚙️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/anandaashutosh206/samadhan-setu.git
cd samadhan-setu
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Frontend

```bash
npm run dev
```

---

## 🐍 Backend Setup

Navigate to the API directory:

```bash
cd api
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server according to the project's backend configuration.

---

## 🔐 Environment Variables

Sensitive credentials and API keys should **never be committed to GitHub**.

Create an environment file based on the provided example:

```text
.env.example
```

Typical configuration may include:

```text
DATABASE_URL=
JWT_SECRET=
S3_ENDPOINT=
S3_ACCESS_KEY=
S3_SECRET_KEY=
```

Keep the actual `.env` file private.

---

## 🏆 Innovation

The key difference between Samadhan Setu and a conventional grievance portal is the **problem-to-project transformation**.

### Traditional Grievance System

```text
Complaint
   ↓
Officer
   ↓
Resolution
   ↓
Closed
```

### Samadhan Setu

```text
Community Problem
        ↓
AI Triage
        ↓
Human Validation
        ↓
Research Opportunity
        ↓
University / Student Matching
        ↓
Mentor & Industry Collaboration
        ↓
Solution
        ↓
Deployment
        ↓
Measured Social Impact
```

The objective is not merely to **close complaints**, but to create a structured pathway from **societal problems to sustainable innovation**.

---

## 🎓 SIH 2026

Samadhan Setu was developed for:

**Smart India Hackathon 2026**

### Problem Statement

**SIH26043 – Jharkhand Societal Innovation Collaboration Portal**

**Category:** Smart Education / Software

**Team:** MIDNIGHT CODERS

**Institute:** Narula Institute of Technology

**Mentor:** Dr. Partha Sarthi Dey

---

## 🔮 Future Scope

Potential future enhancements include:

- Advanced multilingual NLP
- Large Language Model integration
- Improved semantic similarity
- Automated research-project generation
- Advanced geospatial analytics
- Mobile applications
- Advanced analytics dashboards
- Predictive issue prioritization
- Real-time impact monitoring
- Government and university API integrations
- Large-scale deployment across districts

---

## 🎯 Expected Impact

Samadhan Setu aims to create a collaborative ecosystem connecting:

```text
Citizens
    ↕
Government
    ↕
Universities
    ↕
Students & Faculty
    ↕
Industry & CSR
```

This ecosystem can help transform local problems into:

- Research projects
- Student projects
- Technology solutions
- Innovation opportunities
- Startups
- Publications
- Deployable solutions
- Measurable social impact

---

## 👨‍💻 Team

### Team Midnight Coders

Developed by students of **Narula Institute of Technology** for Smart India Hackathon 2026.

---

## 📜 License

This project was developed for educational, innovation, and hackathon purposes.
