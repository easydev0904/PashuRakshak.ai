# SIH Demo Flow

A judge should be able to see the complete value proposition in about
3–4 minutes. This is the exact walkthrough the seeded demo data
(`seed/seed_data.py`) is built to support.

## Setup

```bash
python seed/seed_data.py
```

Demo accounts (password for all: `Demo@1234`):

| Role | Email |
|---|---|
| Farmer | `farmer.demo@pashurakshak.ai` |
| Farmer (2nd farm) | `farmer2.demo@pashurakshak.ai` |
| Veterinarian | `vet.demo@pashurakshak.ai` |
| Veterinarian (2nd) | `vet2.demo@pashurakshak.ai` |
| Admin | `admin.demo@pashurakshak.ai` |

## Walkthrough

### 1. Farmer dashboard

Log in as `farmer.demo@pashurakshak.ai`. The dashboard greets by name,
shows the farm, and leads with "N animals need a check-in today" — the
single most prominent action is **Add Today's Observation**. Below
that, "Your animals" already shows a color-coded spread: one HIGH (red),
one LOW (green), one MEDIUM (amber) — the seed data is built so this
variety is visible without any manual setup.

### 2. Animal profile

Open the HIGH-risk animal (`COW-101`). Shows its photo/avatar, species,
current risk badge, vaccination records (one upcoming, matching a
realistic "due in 10 days" state), and the health timeline — every
past observation with its own risk band and top contributing signals.

### 3. Add an observation

Click **Add Today's Observation**. Walk through the multi-step form
(appetite → activity → water intake → respiratory → dung →
temperature/milk yield/notes/photo) — large tap-target choices, no
medical jargon, ~2-3 minutes by design. Submit with a few concerning
signs selected (or use the pre-seeded HIGH example as reference for
what triggers escalation).

### 4. AI early-warning result

Immediately after submit: **Early-Warning Result**, the risk band
badge, "Why this result?" (2-4 contributing signals in plain language),
"Safe next steps" (non-prescriptive: recheck, keep records, biosecurity,
contact a vet if concerned / urgent vet for HIGH), and for HIGH — the
mandatory disclaimer in a red-bordered box: *"AI screening alert -
veterinarian assessment required."* Point out explicitly: this is a
screening flag, not a diagnosis.

### 5. Switch to veterinarian

Log out, log in as `vet.demo@pashurakshak.ai`. The **same alert**
appears immediately in the alert queue — stat cards up top (active,
high/medium priority, follow-ups due), filterable list below.

### 6. Review the alert

Open it. Three clearly separated sections: **Reported observation**
(what the farmer entered) → **AI screening** (band, factors, model
version, disclaimer) → **Veterinary assessment** (the case workspace —
empty until the vet acts). Click **Acknowledge**, then **Request
follow-up** with a note — this opens a case and moves the alert to "in
review". Optionally enter a **confirmed condition** — point out this
field is only reachable by a veterinarian; the AI never populates it.

### 7. Prevention library

Navigate to **Prevention**. Filterable by category (vaccination,
hygiene, quarantine, nutrition, biosecurity, general observation), each
entry seeded in both English and Hindi — demonstrate the language
switcher (top right) changing the whole UI, not just this content.

### 8. Farm trends

Navigate to **Analytics**. Stat cards (animals, observations, open
alerts, vaccinations due) and a 30-day daily trend table by risk band.
Read the footer note aloud: *"These are aggregated early-warning
observations for this farm, not a confirmed outbreak or diagnosis."*
— deliberately never "this village has an outbreak."

## Close

> "This supports earlier attention; a veterinarian confirms any
> diagnosis."

## Talking points if there's time

- **Offline draft**: open the observation form, use devtools to go
  offline, submit — "Saved offline" (never a false success message),
  then go back online and watch it sync automatically and get scored.
- **Admin panel**: user management, farm oversight, education content
  publishing, and a real audit-log trail of every action taken during
  the demo itself.
- **Bilingual architecture**: every string in the product routes
  through translation keys (`src/i18n/locales/en.json` / `hi.json`) —
  adding a third language is a translation file, not a code change.
- **Full case workflow**: the seed data pre-populates a case in each
  of the four states (`open` on `COW-103`, `under_review` on
  `COW-104`, `follow_up` on `COW-203`, `resolved` with a vet-confirmed
  outcome on `BUF-201`) — open any of them from the vet's alert queue
  or `GET /api/v1/animals/{id}/cases` to show the full lifecycle
  without acting anything out live.
