# AcadSync – Academic Management & Workflow System 🎓

**AcadSync** is a comprehensive academic ERP solution designed to centralize university operations. It automates complex workflows, from course registration and grade management to attendance-linked exam eligibility.

## 🚀 Technical Highlights
- **Eligibility Engine:** Rule-based logic that automates exam admit-card locking based on real-time attendance percentages.
- **Multi-Tenant Experience:** Distinct, secure portals for Students, Lecturers, and Administrators.
- **Relational Integrity:** Optimized SQL schema with atomic transactions for high-traffic registration periods.

## 🛠️ Tech Stack
- **Backend:** Python, Django
- **Data Visualization:** Chart.js
- **Frontend:** Bootstrap 5, JavaScript
- **Database:** PostgreSQL / SQLite



## 📥 Installation & Setup
1. **Clone the repo:**
   ```bash
   git clone [https://github.com/yourusername/acadsync.git](https://github.com/yourusername/acadsync.git)
   cd acadsync

```

2. **Create Virtual Env:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```


3. **Install & Migrate:**
```bash
pip install -r requirements.txt
python manage.py migrate

```



## 📊 Core Business Logic

The system enforces a **75% attendance threshold** for exam eligibility. The backend aggregates attendance logs daily and updates a boolean `is_eligible` flag, which dynamically controls UI access to examination resources.

```
