# Security Policy — PfunzoBridge

## 🛡️ Secure Software Development Life Cycle (SSDLC) Compliance

PfunzoBridge is built in alignment with **SSDLC best practices** to safeguard learner data, privacy, and system integrity.

---

### 1. Secret & Credential Management
* **Zero Hardcoded Secrets:** No production secrets, API keys, private certificates, or database credentials are committed to version control.
* **Environment-Driven Configuration:** All sensitive variables (`DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`) are loaded via environment variables or a local `.env` file excluded by `.gitignore`.
* **Database Isolation:** Local databases (`db.sqlite3`) containing user hashes and test records are strictly ignored by git and never pushed to public repositories.

---

### 2. Authentication & Data Protection (POPIA Compliance)
* **Password Hashing:** Passwords are never stored in plaintext. Django uses standard PBKDF2 with SHA-256 algorithm and salt iterations.
* **Input Validation & Sanitization:** All learner mark submissions (0-100%) and profile data are type-checked and sanitized on both client and server sides.
* **CSRF & XSS Protection:** CSRF tokens (`{% csrf_token %}`) guard all state-changing POST requests. Template auto-escaping prevents Cross-Site Scripting (XSS).
* **Clickjacking Defense:** Handled via Django's `XFrameOptionsMiddleware` (set to `DENY` in production).
* **South African POPIA Compliance:** High school learner records are stored in session-isolated profiles with no unencrypted third-party sharing.

---

### 3. Reporting a Security Vulnerability

If you discover a security vulnerability or credential leak within this repository:

1. **Do NOT open a public GitHub issue.**
2. Report the vulnerability privately to the project maintainer:
   * **Security Contact:** PfunzoBridge Security Team
   * **Email:** [security@pfunzobridge.co.za](mailto:security@pfunzobridge.co.za)
3. Please include:
   * Description of the vulnerability.
   * Steps or script to reproduce the issue.
   * Potential impact assessment.
4. Security reports will be acknowledged within 48 hours, followed by a remediation plan and patch.

---

### 4. Production Deployment Checklist
- [ ] Set `DJANGO_DEBUG=False` in environment.
- [ ] Provide a cryptographically random `DJANGO_SECRET_KEY` (minimum 50 characters).
- [ ] Explicitly specify domains in `DJANGO_ALLOWED_HOSTS`.
- [ ] Ensure HTTPS/SSL certificates are enabled (`CSRF_COOKIE_SECURE=True`, `SESSION_COOKIE_SECURE=True`).
- [ ] Migrate database schemas using `python manage.py migrate`.
