# School Election Management System

A complete, secure, and modern Django-based voting terminal designed for school student council elections. It is optimized to run on a shared, supervised voting booth device.

## 🌐 Live Deployment

> **The system is live and accessible at:**
>
> | Page | URL |
> |---|---|
> | 🗳️ **Student Voting** | https://school-election-app.onrender.com/vote/ |
> | 🎛️ **Invigilator Control Panel** | https://school-election-app.onrender.com/control/ |
> | 📊 **Election Results** | https://school-election-app.onrender.com/results/ |
> | 👤 **Admin Login** | https://school-election-app.onrender.com/login/ |
>
> **Admin credentials:** Username: `admin` · Password: `admin123`

---

## Key Features

* **Dual Leader Elections:** Elects one Male School Leader and one Female School Leader.
* **Supervised Booth Flow:** The invigilator assigns the active student group from the control panel.
* **Voter Anonymity:** Stores zero voter names or personal details. Only vote counts per class group are registered.
* **Double-Submission Prevention:** Automatically disables buttons and blocks multiple form posts.
* **Ticking Cooldown:** Shows a 30-second ticking progress countdown after voting, disabling inputs while a student exits the booth.
* **Electronic Beep Audio:** Plays a synthetic electronic beep via the Web Audio API on successful vote casting.
* **Live Tallies & Rankings:** Interactive charts, percentage statistics, and automatic winner assignments.
* **PDF Report Generation:** Print stylesheet formats the results page into a clean PDF log when printed.
* **Complete Candidate CRUD:** Admin dashboard to register, modify, and delete candidates with photos and manifestos.

---

## Quick Start & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** (tested successfully on Python 3.14) installed on your system.

### 2. Set Up Virtual Environment & Dependencies
Clone or copy the project files to your workspace directory, then open a terminal and run:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On macOS/Linux:
source .venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Initialize Database and Seeding
Apply migrations and seed the database with all standard classes (Standards 1 to 12, Divisions A to E) and default candidate profiles:

```bash
# Generate database schema
python manage.py migrate

# Seed data and create superuser
python populate_data.py
```

### 4. Default Admin Credentials
The seeding script registers a default administrator for the invigilator dashboard:
* **Username:** `admin`
* **Password:** `admin123`

### 5. Launch the Server
Start the local Django server:

```bash
python manage.py runserver
```

Open your browser and navigate to:
* **Student Voting screen:** `http://127.0.0.1:8000/vote/`
* **Invigilator Control Panel:** `http://127.0.0.1:8000/control/`
* **Staff Login screen:** `http://127.0.0.1:8000/login/`

---

## Step-by-Step Operator Workflow

### Step 1: Login & Setup Active Class
1. Go to `http://127.0.0.1:8000/login/` and log in as `admin`.
2. On the **Control Panel**, select a **Standard** (1–12) and **Division** (A–E) for the group currently entering the booth (e.g. Standard 8, Division C).
3. Click **SET ACTIVE CLASS**.
4. Make sure voting status displays **OPEN**.

### Step 2: Student Voting
1. Open the student screen at `http://127.0.0.1:8000/vote/` on the voting terminal.
2. The page locks to the selected group (e.g. "CURRENT VOTING GROUP: Class 8-C").
3. The student selects one Male candidate and one Female candidate by tapping their cards. The cards animate and show checkmarks.
4. The **CAST MY VOTE** button activates. Clicking it records the vote, plays a beep, and opens the success page.
5. The success page shows a 30-second progress countdown. When it hits zero, it resets back to the candidate card menu.

### Step 3: Tallying Results
1. The invigilator navigates to `http://127.0.0.1:8000/results/`.
2. View total cast votes, candidate vote share progress bars, and the winners highlighted with crown ribbons.
3. Click **EXPORT TO PDF / PRINT** to save or print the final official election report.

---

## Security Configurations
* **No Student Login:** Shared terminal removes credentials friction.
* **URL Restrictions:** Non-logged-in users trying to access `/control/`, `/results/`, or `/candidates/` are redirected to `/login/`.
* **Singleton Settings:** The `ElectionSetting` model enforces a single active configuration instance in SQLite.
* **Database Safety:** All vote records are read-only in Django Admin. Resetting results requires confirming on a secure popup modal.
