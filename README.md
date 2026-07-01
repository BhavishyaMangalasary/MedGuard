# MedGuard 🛡️
### AI-Powered Medication Safety Assistant

MedGuard is a multi-agent AI system that helps patients and family caregivers
manage complex medication lists safely. It analyzes your full medication list,
checks for dangerous drug interactions using live FDA label data, builds a
daily schedule, and flags upcoming refill gaps — all in one plain-language
daily brief.

Built with Google's Agent Development Kit (ADK) for the Kaggle 5-Day AI
Agents Capstone.

---

## The Problem

When a patient sees multiple doctors, no single doctor has the full picture
of what that patient is taking. A cardiologist prescribes a blood thinner.
A primary care doctor, unaware, prescribes ibuprofen for joint pain. Those
two drugs together can cause serious internal bleeding. Neither doctor made
a mistake in isolation — the system just has no mechanism to catch the
conflict across prescribers.

This gap falls hardest on elderly patients managing 5+ medications across
multiple specialists, and family caregivers coordinating care without any
clinical training.

---

## Sample Input & Output

**Input** — typed conversationally by the user:
```
============================================================
  Welcome to MedGuard - Medication Safety Assistant
============================================================

Who are you managing medications for?

> janet

Please enter janet's medication list below.
Include drug name, dose, frequency, which doctor
prescribed it, days supply, and last fill date if known.

Type DONE on a new line when finished.

From Dr. Patel (cardiologist):
- Warfarin 5mg, once daily in the evening, last filled 25 days ago, 30 day supply

From Dr. Nguyen (primary care):
- Ibuprofen 400mg, up to 3 times daily as needed for joint pain
- Lisinopril 10mg, once daily in the morning, last filled 28 days ago, 30 day supply
- Metformin 500mg, twice daily with meals, last filled 20 days ago, 30 day supply
DONE

Analyzing janet's medication list...
```

**Output** — MedGuard's daily brief:
```
============================================================
  MEDGUARD DAILY BRIEF — JANET
============================================================

Here is your daily brief for Janet:

1.  URGENT
    Janet is taking Warfarin (a blood thinner) and Ibuprofen (an NSAID). Taking these medications together significantly increases the risk of major or fatal bleeding. **Contact a pharmacist or doctor today to discuss this.**

    Lisinopril 10mg: Will run out in 2 days. Please arrange a refill today.

2.  TODAY'S SCHEDULE
    **Morning**
    *   Lisinopril 10mg
    *   Metformin 500mg (with breakfast)

    **Afternoon**
    *   *(No scheduled medications)*

    **Evening**
    *   Metformin 500mg (with dinner)
    *   Warfarin 5mg

    **Bedtime**
    *   *(No scheduled medications)*

    **As Needed**
    *   Ibuprofen 400mg (up to 3 times daily for joint pain) - Do not take until you speak to a pharmacist or doctor.

3.  WATCH FOR
    *   🔶 MODERATE - Taking Warfarin with other drugs that increase bleeding risk, such as Ibuprofen, can further increase the chance of bleeding.
        [Source: Warfarin FDA label -- Drug Interactions]
    *   🔶 MODERATE - Ibuprofen, an NSAID, carries a warning about severe stomach bleeding. The risk is higher when taken with blood thinning (anticoagulant) drugs like Warfarin.
        [Source: Ibuprofen FDA label -- Warnings]
    *   🔶 MODERATE - Co-administration of Lisinopril with NSAIDs, including Ibuprofen, may result in deterioration of kidney function, including possible acute renal failure.
        [Source: Lisinopril FDA label -- Drug Interactions]

4.  REFILLS NEEDED SOON
    *   Warfarin 5mg: Will run out in 5 days.

5.  DISCLAIMER
    This brief is informational only, based on FDA label data fetched live from api.fda.gov. It is not a substitute for advice from a pharmacist or doctor.

Save this medication list for next time? (yes/no)
> YES
Record saved for janet.
✓ Record saved for janet.
```

**Returning User**:
```
============================================================
  Welcome to MedGuard - Medication Safety Assistant
============================================================

Who are you managing medications for?
(e.g. 'myself', 'my mom', 'Janet')

> Janet

Found a saved record for Janet.
1. Load saved record
2. Enter a new list

> 1

Loading Janet's saved medication list...

Analyzing Janet's medication list...
```

---

## How It Works

MedGuard runs a 4-agent pipeline using Google ADK:
```
User input (plain text medication list)
              │
              ▼
┌────────────────────────────┐
|                            |
│        Intake Agent        │  Normalizes messy input into structured
│                            │  medication records
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
|                            |
│   Conflict & Risk Agent    │  Calls live FDA label API, reasons
│                            │  across full list to flag interactions,
│      [openFDA tool]        │  timing conflicts, prescriber blind spots
|                            |
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
|                            |
│   Scheduler & Gap Agent    │  Builds daily schedule, calculates
│                            │  refill gaps
└────────────┬───────────────┘
             │
             ▼
┌────────────────────────────┐
|                            |
│      Reporter Agent        │  Synthesizes everything into one
│                            │  plain-language daily brief
└────────────────────────────┘
```

---

## Features

- **Drug interaction detection** — reasons over real FDA label text across
  your full medication list
- **Prescriber blind spot flagging** — catches conflicts between medications
  from different doctors who can't see each other's prescriptions
- **Daily schedule** — converts frequencies into a clear morning/afternoon/
  evening/bedtime plan
- **Refill alerts** — flags medications running low before they run out
- **Citations** — every finding traced back to the exact FDA label section
- **Confidence levels** — ⚠️ CRITICAL, 🔶 MODERATE, ℹ️ INFORMATIONAL
- **Live FDA data** — fetched fresh from api.fda.gov on every run, never stale
- **Save & load patient records** -- medication lists are saved
  encrypted to disk and loaded automatically next time you enter
  the same patient name -- no need to retype the full list

---

## Data Source

MedGuard uses the [openFDA Drug Label API](https://open.fda.gov/apis/drug/label/)
— free, public, no API key required, updated weekly directly from FDA
submissions. Labels are fetched live on every run — never cached or stale.

The NIH's RxNav Drug-Drug Interaction API was discontinued in January 2024,
which is why MedGuard reasons over raw FDA label text rather than querying
a precomputed interaction database.

---

## Course Concepts Demonstrated

```
|          Concept         |                    Implementation                    |
|--------------------------|------------------------------------------------------|
| Multi-agent system (ADK) | 4 agents chained via ADK SequentialAgent             |
| MCP-style tool           | openFDA client tool called by Conflict & Risk Agent  |
| Security features        | Fernet encryption at rest, per-record access scoping |
| Deployability            | Documented Cloud Run deployment path                 |
```

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/BhavishyaMangalasary/MedGuard.git
cd MedGuard
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `GOOGLE_API_KEY` — free from [Google AI Studio](https://aistudio.google.com/apikey)
- `MEDGUARD_ENCRYPTION_KEY` — generate with:
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 5. Run MedGuard
```bash
python demo.py
```

Type your medication list when prompted. Type `DONE` on a new line when finished.

### 6. Run with browser UI
```bash
adk web
```

Open `http://127.0.0.1:8000` and select `agents` from the app list.

---

## Project Structure

```
medguard/
    ├── agents/
    │   ├── intake_agent.py          # Normalizes raw input
    │   ├── conflict_risk_agent.py   # Flags interactions using FDA data
    │   ├── scheduler_gap_agent.py   # Builds schedule, tracks refills
    │   ├── reporter_agent.py        # Writes the final daily brief
    │   ├── orchestrator.py          # Wires all 4 agents together
    │   └── models.py                # Shared data structures
    ├── tools/
    │   ├── openfda_client.py        # Live FDA label API tool
    │   └── secure_storage.py        # Encrypted patient data storage
    ├── demo.py                      # Interactive CLI entry point
    ├── requirements.txt
    ├── .env.example
    └── .gitignore
```

---

## Disclaimer

MedGuard is an informational tool built on FDA label data. It is not a
substitute for advice from a pharmacist or doctor. Every output explicitly
states this. MedGuard never tells a user to stop or change a medication —
it flags patterns for human review only.

---

## Author

Built by Bhavishya for the Kaggle 5-Day AI Agents Capstone with Google.
