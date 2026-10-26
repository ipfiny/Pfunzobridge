# PfunzoBridge

Mobile-first AI higher education guidance and bursary tracking platform for South African high school learners and matriculants.

- **Live Application:** [https://pfunzobridge.onrender.com](https://pfunzobridge.onrender.com)
- **Developers:** Ipfi Nyamande, Dingilizwe Ginyani
- **Demo Credentials:** Username: `demo` | Password: `password123`

---

## Overview

South African learners face significant barriers when transitioning to tertiary education, including a 1:1,000+ school counselor ratio, complex university Admission Point Score (APS) rules, and fragmented bursary deadlines.

**PfunzoBridge** addresses these challenges in a single, free, low-data Progressive Web App (PWA) combining conversational AI advising, automated DBE APS calculation, career discovery, and bursary application tracking.

---

## Core Features

1. **PfunzoAI Education Advisor (`/`)**
   - Real-time streaming AI guidance powered by Server-Sent Events (SSE).
   - Assists with university admissions, TVET pathways, NSFAS eligibility rules, and bursary motivation letters.

2. **APS & Marks Calculator (`/aps/`)**
   - Official Department of Basic Education (DBE) 7-point scale calculation.
   - Computes both **Standard APS** (excluding Life Orientation) and **Total APS** (including Life Orientation).
   - Matches learner marks against South African university degree and TVET entry requirements with real-time cross-device sync.

3. **Career Guidance Quiz (`/quiz/`)**
   - Interactive vocational assessment matching learners to high-demand South African career archetypes, institutions, and funding programs.

4. **Bursaries & NSFAS Tracker (`/bursaries/`)**
   - Centralized catalog of national funding schemes (NSFAS, Funza Lushaka, Sasol, ISFAP, Allan Gray, CSIR) with automated deadline status indicators, document checklists, and application submission tracking.

5. **Student Profile, Security & POPIA Compliance (`/profile/`, `/privacy/`, `/terms/`)**
   - User-agnostic Google Sign-In and standard email/password authentication.
   - Dynamic Matriculant Readiness Checklist.
   - Full compliance with the Protection of Personal Information Act (POPIA Act 4 of 2013), including one-click **PDF Personal Data Export** (Section 23) and **Permanent Account & Data Deletion** (Section 24).

---

## Tech Stack

- **Backend:** Python 3.14, Django 5.1
- **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript, Progressive Web App (Service Worker & Manifest)
- **AI Engine:** Google Antigravity Agent SDK with South African curriculum fallback engine
- **Reporting & Static Serving:** ReportLab (PDF generation), WhiteNoise, Gunicorn

---

## Local Setup & Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Start the development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   Access the application at `http://127.0.0.1:8000`.

---

## Automated Testing

Run the test suite (28 unit and integration tests covering APS calculation, authentication, POPIA PDF export, account deletion, and endpoints):

```bash
python manage.py test agents
```
