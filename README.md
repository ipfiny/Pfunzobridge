# PfunzoBridge — Mobile-First Agentic Higher Education Platform
**Project Lead:** Ipfi Nyamande  
**Tech Stack:** Python 3.14, Django 5.1, Tailwind CSS, JavaScript, Progressive Web App (PWA), Google Antigravity Agent Engine  

---

## 🌟 Overview & Problem Statement

High school learners and matriculants in South Africa face severe barriers when navigating higher education pathways:
1. **Lack of Early Career Guidance:** Students often choose subjects and tertiary degrees without understanding market demand or their own aptitude.
2. **APS Score Confusion:** Calculating Admission Point Scores (APS) correctly across different universities (such as Wits excluding Life Orientation vs UJ including it) is complex.
3. **Scattered Bursary & NSFAS Deadlines:** Thousands of eligible learners miss out on free education funding because application dates, income thresholds, and required documentation are fragmented.
4. **Data & Device Constraints:** South African learners predominantly access the internet via low-cost mobile phones with limited cellular data.

**PfunzoBridge** bridges the gap between ambition and opportunity by combining **autonomous AI counseling**, **real-time APS calculation**, **vocational career discovery**, and **centralized funding management** into a single, free, low-data mobile platform.

---

## 📱 Mobile-First Features

### 1. 🤖 PfunzoBridge AI Counselor (Agentic Core)
- Built on the **Google Antigravity SDK & Agent Architecture** with fallback knowledge engine for South African educational nuances.
- **Asynchronous Token Streaming:** Streams tokens live via Server-Sent Events (`/run-agent-api/`), providing instantaneous mobile feedback without page reloads.
- Pre-configured quick prompt chips:
  - *NSFAS 2026/2027 Eligibility Rules & Household Thresholds (R350,000 / SASSA automatic qualification)*.
  - *APS Calculation Strategy & University Rules*.
  - *Draft Bursary Motivation Letter Template*.
  - *High-Demand South African Careers & Salaries*.
  - *Pure Maths vs Mathematical Literacy Course Pathways*.

### 2. 🧮 APS & Marks Calculator (`/aps/`)
- Implements the official Department of Basic Education (DBE) 7-level NSC scale (Level 1 to 7).
- Differentiates between **Standard APS** (top 6 subjects excluding Life Orientation, used by Wits, UCT, UP, UKZN) and **Total APS with LO** (used by UJ, TVETs).
- Instant degree eligibility engine matching courses across South African faculties (Computer Science, Electrical/Mechanical Engineering, Medicine MBChB, Law LLB, BCom Accounting, B.Ed Teaching, and TVET Trades).
- One-tap "Ask AI Advisor About These Marks" button.

### 3. 🧭 Career Guidance Quiz (`/quiz/`)
- 5-question touch-optimized RIASEC vocational discovery quiz.
- Matches students to 4 South African archetypes:
  - **Innovator & Systems Builder** (STEM, Software, Robotics, Artisan Trades).
  - **Strategic Analyst & Problem Solver** (Data Science, CA(SA), Actuarial, Economics).
  - **Community Healer & Educator** (Medicine, Nursing, Teaching, Human Rights Law).
  - **Visionary Entrepreneur & Commercial Leader** (Tech Startups, Supply Chain, Business).
- Provides instant recommendations for university degrees, TVET apprenticeships, top South African universities, and targeted bursaries.

### 4. 💼 Bursaries & NSFAS Tracker (`/bursaries/`)
- Centralized catalog of major South African tertiary funding schemes:
  - **NSFAS** (Full government tertiary & TVET funding)
  - **Funza Lushaka** (100% teaching bursary with service placement)
  - **Sasol Foundation** (Corporate STEM bursary)
  - **ISFAP** (Missing middle funding R350k - R600k)
  - **Allan Gray Orbis Fellowship** (Entrepreneurial & leadership bursary)
  - **Motsepe Foundation, CSIR, Shoprite Group**
- Interactive **Document Checklist Tracker** per bursary:
  - [x] Certified South African ID Copy
  - [x] Matric Statement / Grade 11 Marks
  - [x] Proof of Household Income / SASSA Confirmation
  - [x] Motivation Letter Draft
- Direct application links to official portals.

### 5. 📊 Student Profile & Readiness Scorecard (`/profile/`)
- Displays overall learner metrics, computed APS, target career, and active funding trackers.
- Low-data session persistence for guest learners without mandatory registration barriers.

### 6. ⚡ Progressive Web App (PWA) & Low-Data Optimization
- Touch targets $\ge 48 \times 48\text{ px}$, tap-scale feedback, and fixed bottom navigation bar.
- Service Worker (`sw.js`) and Web Manifest (`manifest.json`) for caching and offline mobile use.
- Low-Data Mode toggle for minimal data consumption.

---

## 🛠️ Project Structure

```text
project/
│
├── config/                      # Django project configuration
│   ├── __init__.py              # Python 3.14 context compatibility layer
│   ├── settings.py              # Application settings & mobile static setup
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI entry point
│   └── asgi.py                  # ASGI entry point
│
├── agents/                      # PfunzoBridge Core Application
│   ├── services/
│   │   ├── __init__.py
│   │   ├── antigravity_runner.py # Antigravity agent streaming loop & fallback
│   │   ├── aps_service.py       # DBE 7-point APS engine & degree catalog
│   │   └── data_store.py        # Bursary & Career Quiz datasets
│   ├── templates/agents/
│   │   ├── base.html            # Mobile-first shell with Tailwind CSS & bottom nav
│   │   ├── index.html           # AI Counselor dashboard & live streaming feed
│   │   ├── aps.html             # APS Calculator & University course checker
│   │   ├── quiz.html            # Career Guidance Quiz
│   │   ├── bursaries.html       # Bursary & NSFAS tracker with document checklists
│   │   ├── profile.html         # Learner profile & readiness scorecard
│   │   └── detail.html          # Agent task history & audit view
│   ├── models.py                # AgentTask, StudentProfile, BursaryItem, BursaryTracking
│   ├── views.py                 # Streaming controller & page handlers
│   ├── urls.py                  # Endpoints
│   ├── tests.py                 # 10 automated test suites (100% passing)
│   └── admin.py                 # Django admin dashboard
│
├── static/
│   ├── manifest.json            # PWA manifest
│   ├── js/
│   │   ├── app.js               # Service worker registrar & prompt auto-filler
│   │   └── sw.js                # Low-data caching service worker
│   └── css/
│
├── manage.py                    # Django management CLI
├── run.py                       # Cross-platform runner script
├── start_app.bat                # Windows 1-click launcher
└── requirements.txt             # Project dependencies
```

---

## 🚀 Running the Application

### Option 1: Quick Launch
Double-click `start_app.bat` or run:
```bash
python run.py
```

### Option 2: Standard Command Line
```bash
py manage.py migrate
py manage.py runserver 0.0.0.0:8000
```

### Mobile Access:
Open `http://127.0.0.1:8000` in your web browser.  
To test on your mobile phone on the same Wi-Fi network, access `http://<your-computer-ip>:8000`.

---

## 🧪 Running Automated Tests
```bash
py manage.py test
```
All 10 unit tests for APS calculation, agent streaming, views, and APIs pass cleanly.
