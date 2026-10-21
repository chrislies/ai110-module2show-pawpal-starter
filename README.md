# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The 24 tests in `tests/test_pawpal.py` cover:

- **Sorting:** chronological order across pets, untimed tasks last, unpadded hours (`8:30`), and an empty task list.
- **Filtering:** by pet, by completion status, and both together, plus an unknown pet name.
- **Recurring tasks:** completing a daily task creates one due the next day on the same pet, weekly adds 7 days, month and year rollover, one-off tasks create nothing, and tomorrow's task is not planned today.
- **Conflict detection:** same time for one pet and across pets, overlapping windows flagged, back-to-back tasks not flagged, and untimed or completed tasks ignored.
- **Plan building:** high priority wins when time is short, same-time tasks are pushed apart, and an empty plan.
- **Validation:** bad duration, priority, or time values raise `ValueError`.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-8.4.2, pluggy-1.6.0
rootdir: D:\Programming\codepath\ai110\ai110-module2show-pawpal-starter
plugins: anyio-4.9.0
collected 24 items

tests\test_pawpal.py ........................                            [100%]

============================= 24 passed in 0.04s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All 24 tests pass and they cover the main scheduling behaviors and their edge cases. I am not giving 5 because the Streamlit UI (`app.py`) has no automated tests, conflict detection only looks at preferred times, and the scheduler picks tasks greedily by priority, so it may not fit the most tasks into the time available.

## 📐 Smarter Scheduling

PawPal+ goes beyond a fixed to-do list with four small algorithms, all in
`pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sorting | `Scheduler.sort_by_time()` | Orders tasks by preferred time, earliest first, with untimed tasks last. Times are compared as minutes, so `8:30` sorts before `10:00`. Defaults to every task across all pets. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)` | Returns tasks for one pet, by completion status, or both. Either filter can be left out. Pass the result to `sort_by_time()` to combine them. |
| Conflict detection | `Scheduler.detect_conflicts()` | Flags pending tasks whose preferred-time windows (start plus duration) overlap, for the same pet or different pets. Returns warning strings and never raises or changes the plan. Tasks with no preferred time are ignored. |
| Recurring tasks | `CareTask.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `"daily"` task creates a copy due 1 day later and a `"weekly"` task 7 days later, using `timedelta`. The copy is added to the same pet. One-off tasks (`recurring=None`) create nothing. |

Supporting behavior:

- `CareTask.due_date` defaults to today. `Scheduler.due_tasks()` lets
  `build_plan()` skip tasks that are not due yet, so tomorrow's walk is not
  scheduled today.
- `build_plan()` still selects greedily by priority until the time budget runs
  out, then orders by preferred time. Conflict warnings describe the *requested*
  times; the final plan never overlaps because later tasks are pushed back.

Run `python main.py` to see sorting, filtering, recurrence, and conflict
warnings in the terminal.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

## Sample Output

Output of `python main.py`:

```text
Today's Schedule for Sam
============================================================
Time   Pet      Task               Min  Priority
------------------------------------------------------------
08:00  Luna     Breakfast           10  high
08:30  Mochi    Morning walk        30  high
09:30  Luna     Medication           5  high
18:00  Mochi    Evening walk        30  medium
------------------------------------------------------------
Skipped:
  Luna: Laser play (needs 20 min but only 15 left)
  Mochi: Grooming (needs 25 min but only 15 left)
============================================================
4 scheduled, 2 skipped; 75 of 90 min used, 15 left
```
