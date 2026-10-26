# Security Policy — PfunzoBridge

## 🛡️ Secure Software Development Life Cycle (SSDLC) Compliance

PfunzoBridge is engineered in strict alignment with **SSDLC best practices**, South Africa's **Protection of Personal Information Act (POPIA Act 4 of 2013)**, and **OWASP Top 10** web application security standards.

---

### 1. Security Requirements (Risk Assessment)
* **Data Privacy & POPIA Compliance:** High school learners (often minors) require strict protection of academic marks, identity details, and contact information against unauthorized processing and disclosure.
* **Integrity of Academic Records:** Prevent unauthorized tampering with learner marks (0–100%) and calculated Admission Point Scores (APS) used for bursary matching.
* **Access Control & Session Integrity:** Guard against credential stuffing, session hijacking, and brute-force attacks across both mobile cellular connections and desktop browsers.
* **Data Minimization:** Collect strictly what is necessary to compute eligibility (marks, grade, province, high school, target career) without invasive tracking or third-party ad profiling.

---

### 2. Threat Modelling & Design Review
* **Architecture:** Mobile-first Progressive Web App (PWA) built with **Python 3.14, Django 5.1, Tailwind CSS, JavaScript, and the Google Antigravity Agent Engine**.
* **STRIDE Threat Analysis:**
  * *Spoofing:* Mitigated through user-agnostic authentication supporting native Google Identity Services (GIS) One-Tap OAuth and salted PBKDF2/SHA-256 password hashing.
  * *Tampering:* Server-side validation on all mark inputs and APS score calculation routines; client inputs are never implicitly trusted.
  * *Repudiation:* Structured activity and application tracking with timestamped audit logs for submitted bursary applications.
  * *Information Disclosure:* Session-isolated learner profiles; zero unencrypted data transmission; strict `.gitignore` exclusions for databases and secrets.
  * *Denial of Service (DoS):* Asynchronous token streaming via Server-Sent Events (SSE) preventing worker thread starvation.
  * *Elevation of Privilege:* Granular Django session authentication (`@login_required`) guarding sensitive student dashboard and application submission routes.

---

### 3. Development (Secure Coding Practices)
* **Zero Hardcoded Secrets:** All credentials, API keys, and environment variables (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`) are dynamically loaded from environment variables or a local `.env` excluded from version control.
* **CSRF & XSS Defense:** Django's cryptographic CSRF tokens (`{% csrf_token %}`) guard all state-changing POST requests. Automated template auto-escaping prevents Cross-Site Scripting (XSS).
* **Injection Defense:** Fully parameterized Django ORM queries completely eliminate raw SQL injection risks.
* **Safe Redirect Resolution:** Defensive URL routing (`resolve_safe_next_url`) validates all post-login destinations, mitigating open-redirect vulnerabilities.

---

### 4. Security Testing & Verification
* **Automated Test Suite:** 22 automated Django unit tests (`python manage.py test agents`) continuously verify:
  * Authentication boundaries and unauthenticated access redirects (`302`).
  * User-agnostic Google authentication without hardcoded defaults.
  * Boundary limits on APS calculation (percentages 0–100%, DBE Levels 1–7).
  * POPIA compliance policy rendering and learner rights enforcement.
* **Input Validation Testing:** Fuzzing and boundary-value tests on subject mark payloads to ensure negative values, strings, and overflow values are rejected with `400 Bad Request`.
* **Credential Protection Testing:** Verified password reset flows and session migration from guest states into isolated authenticated profiles.

---

### 5. Assessment & Secure Integration
* **Production Cloud Hardening:** Hosted on Render with active SSL/TLS (HTTPS) encryption end-to-end.
* **HTTP Security Headers:**
  * `X_FRAME_OPTIONS = 'DENY'` (Clickjacking protection)
  * `SECURE_CONTENT_TYPE_NOSNIFF = True` (MIME-sniffing prevention)
  * `SECURE_BROWSER_XSS_FILTER = True` (Cross-site scripting filter)
  * `CSRF_COOKIE_SECURE = True` & `SESSION_COOKIE_SECURE = True` (Encrypted cookie transmission)
  * `SECURE_HSTS_SECONDS = 31536000` with subdomains and preload (Strict Transport Security)
* **POPIA Governance:** Dedicated Information Officer channel (`privacy@pfunzobridge.co.za`) providing learners full statutory rights to access, correct, or permanently erase their personal records.

---

### 6. Vulnerability Reporting
To report security vulnerabilities privately:
* **Contact:** PfunzoBridge Security Team
* **Email:** [security@pfunzobridge.co.za](mailto:security@pfunzobridge.co.za)
* **Turnaround:** Initial response within 48 hours followed by remediation patch.
