# PashuRakshak AI — The Story

**"Observe early. Act responsibly."**

## The problem

A farmer sees an animal go slightly off its feed on Monday. By the
time it's visibly sick on Thursday, the window for an easy recovery
has narrowed, the vet has less context to work with, and — at scale —
a preventable local outbreak has had three extra days to spread.

The pattern behind this isn't a lack of care. It's three structural
gaps:

1. Early warning signs are noticed but not recorded anywhere, so
   there's no trend to act on until symptoms are already severe.
2. When a vet finally does see the animal, they're starting from
   zero — no history, no timeline, no pattern.
3. Herd-level records, when they exist at all, are fragmented across
   notebooks, memory, and word-of-mouth.

## The solution

**Observe → Flag → Review → Prevent.**

PashuRakshak AI gives a farmer a two-minute daily observation form.
Every submission is screened immediately. When the signals add up to
something worth a second opinion, a veterinarian is alerted with the
animal's full history already attached — not a cold case. Prevention
content and vaccination reminders close the loop before problems
start.

## How it works

```
Farmer observation (appetite, activity, breathing, dung, ...)
            ↓
   Animal's own history (nothing evaluated in isolation)
            ↓
  Transparent rule engine  +  trained ML model
            ↓
        LOW / MEDIUM / HIGH risk band
            ↓
   Explainable factors ("why this result?")
            ↓
     Veterinarian review, acknowledge, follow-up
            ↓
   Prevention content + vaccination reminders
```

Two things make the middle step trustworthy rather than a black box:

- **The rule engine can only push risk *up*.** A dangerous sign (e.g.
  a very high temperature) forces at least a HIGH result regardless
  of what the statistical model alone would have said. The model can
  suggest calm; a genuinely urgent sign overrides it. It can never
  work the other way — nothing in the system can suppress or soften
  an urgent case.
- **Every result explains itself.** No score is shown without the
  specific plain-language factors that produced it, and every result
  carries the model version that produced it.

## What it deliberately does not claim

PashuRakshak AI is an early-warning and triage tool, not a diagnostic
one. It never tells a farmer or a vet "this animal has disease X." It
tells them "these specific signs are concerning enough that a vet
should look at this soon" — and shows exactly which signs and why. The
word "diagnosis" does not appear anywhere in a farmer- or vet-facing
result; the API has no field that could carry one. Confirming what's
actually wrong, and what to do about it, stays a veterinarian's job —
the product is built to get the right animal in front of the right
vet sooner, with better information, not to replace that judgment.

## Why this is a platform, not a script

Three roles, RBAC enforced server-side (not just hidden UI), farm-level
data isolation backed by tests, offline-capable observation capture
for patchy rural connectivity, and a bilingual interface from day one
— this is built as infrastructure a real veterinary extension program
could operate, not a hackathon-only demo path.

## The ask, in one line

Give farmers a way to say "something's off" in under two minutes, and
give vets a reason to trust that signal enough to act on it early.
