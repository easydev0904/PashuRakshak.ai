# PashuRakshak AI — SIH Showcase Guide

This guide is written for whoever is presenting the project at Smart
India Hackathon, even if you did not write any of the code. Follow it
top to bottom and you can run the entire demo yourself.

## 1. Project overview

**PashuRakshak AI** (SIH26128) is a livestock disease early-warning
and case-management platform. A farmer logs a few simple observations
about an animal (appetite, activity, breathing, dung, etc.), the
system screens them for risk, and if the risk is meaningful, a
veterinarian is alerted and can review, acknowledge, and follow up —
all tracked in one place.

Tagline: **"Observe early. Act responsibly."**

## 2. What the project does

- Lets a farmer register animals and log daily observations in under
  a minute, in English or Hindi, on a phone-sized screen.
- Screens every observation with a transparent rule engine + a
  machine-learning model and produces a **LOW / MEDIUM / HIGH**
  early-warning risk band, with the specific factors that drove it.
- Automatically raises an alert for a veterinarian when risk is
  MEDIUM or HIGH, with the animal's full history attached.
- Gives the veterinarian a queue to acknowledge, assign, request a
  follow-up, and close out cases, with their own clinical notes.
- Tracks vaccination due dates and shows farmers what's overdue.
- Publishes a bilingual prevention/education library.
- Gives an admin oversight of users, farms, content, and an audit
  trail of every sensitive action.

## 3. What the AI does NOT do

This is the single most important thing to get right in front of
judges. The system:

- **Never presents a prediction as a confirmed diagnosis.**
- Is not a diagnostic device, not a lab test, not a treatment
  recommender, and not a prescription generator.
- Cannot replace a veterinarian — every HIGH-risk result displays,
  word for word: **"AI screening alert - veterinarian assessment
  required."**
- Has no `diagnosis`, `treatment`, or `prescription` field anywhere in
  its API — this isn't just a UI choice, the data model structurally
  cannot carry one. See [safety.md](safety.md) for the full policy and
  where it's enforced/tested in code.
- Only a veterinarian can enter a "confirmed condition" on a case, and
  the UI labels that field "(veterinarian entry)" — the AI never
  writes to it.

Say this out loud during the demo. It is a strength of the project,
not a limitation to downplay.

## 4. Application URLs

| What | Local dev | Docker |
|---|---|---|
| Frontend | http://localhost:5173 | http://localhost:8080 |
| Backend API | http://localhost:8000 | http://localhost:8000 |
| API docs (Swagger) | http://localhost:8000/docs | http://localhost:8000/docs |

## 5. Demo accounts

Password for **all** accounts: `Demo@1234`

| Role | Email |
|---|---|
| Farmer (Green Valley Farm) | `farmer.demo@pashurakshak.ai` |
| Farmer (Sunrise Dairy Farm) | `farmer2.demo@pashurakshak.ai` |
| Veterinarian | `vet.demo@pashurakshak.ai` |
| Veterinarian (2nd) | `vet2.demo@pashurakshak.ai` |
| Admin | `admin.demo@pashurakshak.ai` |

The login page itself lists these and fills the form in when you tap
one — you don't need to type them from memory.

## 6. How to start the application

Pick **one** path. Docker is the safer choice if you're not sure the
laptop you're demoing on has Python/Node set up correctly.

### Option A — Docker (recommended for the actual presentation)

```bash
cp .env.example .env
docker compose up --build
```

Wait for the `backend` and `frontend` containers to report healthy
(a minute or two on first build — it also trains the ML model at
build time). Then open http://localhost:8080.

To load the demo data into the Docker database:

```bash
docker compose exec backend python -m alembic upgrade head
docker compose exec backend python /repo/seed/seed_data.py
```

### Option B — Local development (no Docker)

```bash
# 1. Postgres running locally on 5432, matching backend/.env
# 2. Backend
cd backend
source .venv/bin/activate      # create it first if it doesn't exist: python3 -m venv .venv
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# 3. Seed demo data (from repo root, separate terminal)
python seed/seed_data.py

# 4. Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

Full details, including exact environment variables and a real gotcha
about a native Postgres install conflicting with Docker's, are in
[deployment.md](deployment.md).

## 7. Exact demo flow (~3–4 minutes)

The full script with what to say at each step is in
[demo-flow.md](demo-flow.md). Short version:

1. **Log in as the farmer** (`farmer.demo@pashurakshak.ai`).
2. Dashboard shows "N animals need a check-in today" and a
   color-coded animal list.
3. Open **COW-101** — a HIGH-risk animal already seeded on Green
   Valley Farm. Show its species, breed, vaccination record, and
   health timeline.
4. Click **Add Today's Observation** and either walk through the
   6-step form live on a *different* animal (e.g. `COW-104`, which
   has no observation yet today) selecting the worst option at each
   step, or just open COW-101's existing HIGH entry in the timeline.
5. Submitting shows **"Early-Warning Result" → HIGH**, with "Why this
   result?" (2–4 plain-language contributing factors), "Safe next
   steps" (never a treatment plan), and the mandatory safety line.
6. Click **Contact veterinarian** (a `tel:` link — no message is sent
   automatically; escalation is a human phone call, by design).
7. **Log out, log in as the vet** (`vet.demo@pashurakshak.ai`). The
   same alert is already in the queue, with stat cards for
   total/high/medium/follow-ups-due.
8. Open the alert. Three sections: what the farmer reported → the AI
   screening (band, model version, factors, disclaimer) →
   veterinary assessment. Click **Acknowledge**, then **Request
   follow-up** with a note — this opens a case.
9. Point out the **prevention library** (bilingual) and **analytics**
   (farm trend table with the "not a confirmed outbreak" disclaimer).
10. Close with: *"This supports earlier attention; a veterinarian
    confirms any diagnosis."*

## 8. Which animal to select

| Tag | Farm | Why it's useful in the demo |
|---|---|---|
| `COW-101` | Green Valley | Pre-seeded HIGH alert, untouched — the main "today's alert" |
| `BUF-101` | Green Valley | Pre-seeded MEDIUM alert, untouched — a secondary example |
| `COW-104` | Green Valley | No observation logged yet today (use to submit live) — also has a case already in **under_review** |
| `COW-103` | Green Valley | Has a case already **open**, opened directly by a vet |
| `COW-203` | Sunrise Dairy | Has a case in **follow_up**, awaiting the vet's next visit |
| `BUF-201` | Sunrise Dairy | Has a **resolved** case with a vet-confirmed outcome |

If a judge asks "does it handle a case that's still being worked on,
one that's closed, one that was opened without an AI alert at all?" —
these four animals are your answer, already sitting in the database,
nothing to fake live.

## 9. Which observation values to enter (if doing it live)

For a HIGH result, pick the most severe option at each wizard step:
appetite **Not eating**, activity **Very low / lethargic**, water
intake **Reduced**, respiratory sign **Labored / heavy breathing**,
dung sign **Blood present**, and optionally a temperature around
**41°C**. This combination was tested live and reliably produces
HIGH — it comes from the actual rule engine + model, not a hardcoded
UI response.

For a MEDIUM result, pick one or two moderate concerns (e.g. appetite
**Reduced**, respiratory sign **Mild**) and leave the rest Normal.

## 10. Expected result

HIGH → red badge, "Why this result?" lists the specific severe signals
you picked, and the boxed line **"AI screening alert - veterinarian
assessment required."** appears. This is generated by
`ml/src/predict.py` + `ml/src/rules.py` from the actual inputs — it is
not a canned response, so if you pick different (milder) values you
will genuinely get a different band.

## 11. How to switch to veterinarian

Click **Log out** (top right), then log in with
`vet.demo@pashurakshak.ai` / `Demo@1234`. RBAC is enforced on the
backend, not just hidden in the UI — a farmer account cannot reach
`/vet/*` or `/admin/*` routes or their APIs even by guessing a URL.

## 12. How to review the alert

Open the alert from the queue. Buttons across the bottom:
**Acknowledge**, **Assign to me**, **Request follow-up**, **Resolve
alert**. "Request follow-up" is the one that opens a case and lets you
add a clinical note and a next-visit date. A "Confirmed condition"
field appears once a case exists — explicitly labeled as a
veterinarian-only entry.

## 13. How to show prevention

From either the farmer or vet nav, click **Prevention**. Filter by
category (vaccination, hygiene, quarantine, nutrition, biosecurity,
general observation). Toggle the language switcher (top right, EN/हिं)
to show the same content in Hindi — this proves the bilingual
architecture is real, not a translated screenshot.

## 14. How to show analytics

Click **Analytics**. Stat cards (animals, observations, open alerts,
vaccinations due) and a 30-day daily trend table broken down by risk
band. Read the footer note out loud — it's a deliberate safety choice:
*"These are aggregated early-warning observations for this farm, not a
confirmed outbreak or diagnosis."*

## 15. Backup demo procedure

Don't depend on venue Wi-Fi or a cloud deployment for the live demo.

- **Primary plan**: run everything locally via `docker compose up
  --build` on the presenting laptop, well before you're on stage.
  Confirm it's healthy and re-seeded at least an hour beforehand.
- **If Docker is somehow unavailable on the day**: fall back to
  Option B (local dev) in section 6 — it needs Postgres, Python 3.9+,
  and Node, all installed ahead of time.
- **If the live demo breaks mid-presentation**: don't debug on stage.
  Say "let me show you a case that's already further along" and open
  one of the four pre-seeded case-state animals from section 8 instead
  of trying to reproduce the failure. Nothing in the flow requires the
  live submission to succeed — every state you'd want to show already
  exists in the seed data.
- Re-run `python seed/seed_data.py` (or the Docker equivalent in
  section 6) any time before you go on, to reset to a clean, known
  state — it's designed to be destructive and idempotent for exactly
  this reason.

## 16. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `docker compose up` can't reach Postgres | A native Postgres install is already using port 5432 | Stop it: `brew services stop postgresql@16` (see [deployment.md](deployment.md)) |
| Frontend loads but API calls fail | Backend not up yet, or wrong `VITE_API_BASE_URL` | Wait for backend health check; confirm `.env` |
| Login says invalid credentials | Seed data not loaded, or typo | Re-run the seed script; copy the email from the login page's demo panel |
| "Session has expired" right after login | Clock skew or stale token from a previous run | Log out, clear the browser tab's local storage, log in again |
| A HIGH result doesn't show the disclaimer | Should never happen — this is tested (`RiskResultView.test.tsx`) | If seen live, it's worth flagging as a real bug, not "just a demo issue" |

## 17. Key points to explain to judges

- The AI **never** overrides or removes what a farmer reported —
  observations are stored as-entered.
- The risk score comes from a **transparent rule engine layered with
  a trained model** — rules can only push risk *up* (e.g. a very high
  temperature forces at least HIGH), never down, so the model can't
  quietly suppress an urgent case.
- Every AI response carries a **model version** and a fixed
  **clinical disclaimer** — there is no code path that emits a result
  without both.
- **Farm-level data isolation** is enforced server-side: a farmer
  cannot read another farm's animal by editing a URL or an ID in an
  API call — it's backed by tests, not just UI hiding.
- The **synthetic training/demo data** is explicitly documented as
  non-clinical — see [model-card.md](model-card.md).

## 18. Safety statement

> This is a software-only early-warning and decision-support
> prototype. It is not a diagnostic device, not a replacement for
> laboratory testing, and not an autonomous treatment or prescription
> system. Every AI-generated result is a screening signal that
> requires a licensed veterinarian's assessment before any clinical
> decision is made.

## 19. Closing statement

> "PashuRakshak AI doesn't replace the vet — it gets the right animal
> in front of the right vet sooner, with the right history already in
> hand. Observe early. Act responsibly."

## 20. If you get a technical question you can't answer

Point to the docs — they're written for exactly this:
[architecture.md](architecture.md), [security.md](security.md),
[safety.md](safety.md), [model-card.md](model-card.md),
[api.md](api.md). It's fine to say "that's covered in the security
doc, let me pull it up" rather than guessing.
