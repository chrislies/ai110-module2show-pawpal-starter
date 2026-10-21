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

## Features

- **Multiple pets, one owner.** An owner has any number of pets, and each pet has its own task list. All scheduling reads across every pet.
- **Priority-based planning.** `Scheduler.build_plan()` picks tasks highest priority first (earlier preferred time, then shorter duration, break ties) until the owner's available minutes run out.
- **Sorting by time.** `Scheduler.sort_by_time()` lists tasks in clock order across all pets, with tasks that have no preferred time last.
- **Filtering.** `Scheduler.filter_tasks()` narrows tasks by pet, by completion status, or both.
- **Conflict warnings.** `Scheduler.detect_conflicts()` flags tasks whose preferred-time windows overlap, for the same pet or different pets, and returns plain-language warnings instead of raising errors.
- **Daily and weekly recurrence.** Completing a recurring task with `Scheduler.mark_task_complete()` creates the next occurrence (+1 day or +7 days) on the same pet. Tasks not yet due are left out of today's plan.
- **Explained plans.** `Scheduler.explain()` and `Scheduler.summary()` say what was scheduled, what was skipped and why, and how much time is left.
- **Input validation.** Bad durations, priorities, or `HH:MM` times are rejected with a clear error.
- **Tested.** 24 automated tests cover the scheduling logic (see [Testing PawPal+](#-testing-pawpal)).

## Testing PawPal+

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

## Smarter Scheduling

PawPal+ goes beyond a fixed to-do list with four small algorithms, all in
`pawpal_system.py`.

| Feature            | Method(s)                                                      | Notes                                                                                                                                                                                                                       |
| ------------------ | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sorting            | `Scheduler.sort_by_time()`                                     | Orders tasks by preferred time, earliest first, with untimed tasks last. Times are compared as minutes, so `8:30` sorts before `10:00`. Defaults to every task across all pets.                                             |
| Filtering          | `Scheduler.filter_tasks(pet_name, completed)`                  | Returns tasks for one pet, by completion status, or both. Either filter can be left out. Pass the result to `sort_by_time()` to combine them.                                                                               |
| Conflict detection | `Scheduler.detect_conflicts()`                                 | Flags pending tasks whose preferred-time windows (start plus duration) overlap, for the same pet or different pets. Returns warning strings and never raises or changes the plan. Tasks with no preferred time are ignored. |
| Recurring tasks    | `CareTask.next_occurrence()`, `Scheduler.mark_task_complete()` | Completing a `"daily"` task creates a copy due 1 day later and a `"weekly"` task 7 days later, using `timedelta`. The copy is added to the same pet. One-off tasks (`recurring=None`) create nothing.                       |

Supporting behavior:

- `CareTask.due_date` defaults to today. `Scheduler.due_tasks()` lets
  `build_plan()` skip tasks that are not due yet, so tomorrow's walk is not
  scheduled today.
- `build_plan()` still selects greedily by priority until the time budget runs
  out, then orders by preferred time. Conflict warnings describe the _requested_
  times; the final plan never overlaps because later tasks are pushed back.

Run `python main.py` to see sorting, filtering, recurrence, and conflict
warnings in the terminal.

## 📸 Demo Walkthrough

Start the app with `streamlit run app.py`. The page is one scrolling screen, top to bottom.

### What you can do in the UI

| Section            | Actions                                                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owner**          | Set your name and the minutes you have available today.                                                                                         |
| **Add a Pet**      | Enter a name and species. Blank or duplicate names are rejected.                                                                                |
| **Tasks**          | Pick a pet and add a task with a title, duration, priority, an optional preferred time (`HH:MM`), and whether it repeats (once, daily, weekly). |
| **Your tasks**     | Filter by pet and by status (pending or completed). The table is always sorted by preferred time.                                               |
| **Mark complete**  | Finish a task. If it repeats, the next occurrence is created automatically.                                                                     |
| **Build Schedule** | Generate today's plan, see which tasks were skipped, and open "Why this plan?" for the reasoning.                                               |

### Example workflow

1. Set the owner's available minutes to 90.
2. Add two pets, for example Mochi (dog) and Luna (cat).
3. Add tasks: Mochi's "Morning walk" (30 min, high, `08:30`, daily) and Luna's "Breakfast" (10 min, high, `08:00`).
4. Add a clashing task, such as Luna's "Vet call" at `08:30`. A warning appears right away above the task table, naming both tasks and pets, so you can fix it before building a plan.
5. Use the filters to view only Luna's pending tasks. The list stays in time order.
6. Click **Mark complete** on "Morning walk". A message confirms the next one is due tomorrow.
7. Click **Generate schedule** to see today's plan with start times, a summary of time used, and a warning for anything skipped for lack of time.

### Scheduler behaviors shown

- **Sorting:** tasks from different pets are listed in clock order, with untimed tasks last.
- **Filtering:** by pet and by completion status, combined with the sort.
- **Conflict warnings:** overlapping preferred times are flagged for the same pet or across pets, as warnings that never block the plan.
- **Recurrence:** completing a daily or weekly task creates the next one; it does not appear in today's plan.
- **Constraint handling:** when time runs short, lower-priority tasks are skipped and the plan says why. Tasks that would start at the same time are pushed apart so the final schedule never overlaps.

### Sample CLI output

`python main.py` runs the same logic in the terminal, with deliberately clashing tasks:

```text
Today's Schedule for Sam
============================================================
Time   Pet      Task               Min  Priority
------------------------------------------------------------
08:00  Luna     Breakfast           10  high
08:30  Mochi    Morning walk        30  high
09:00  Luna     Vet call            15  medium
09:30  Luna     Medication           5  high
18:00  Mochi    Evening walk        30  medium
------------------------------------------------------------
Skipped:
  Luna: Laser play (needs 20 min but only 0 left)
  Luna: Brushing (needs 15 min but only 0 left)
  Mochi: Grooming (needs 25 min but only 0 left)
============================================================
5 scheduled, 3 skipped; 90 of 90 min used, 0 left

Conflict check:
  Warning: 'Breakfast' (08:00, 10 min) overlaps 'Brushing' (08:05) for Luna
  Warning: 'Morning walk' (08:30, 30 min) overlaps 'Vet call' (08:30) for Mochi and Luna

All tasks sorted by preferred time:
  08:00  Breakfast (Luna) - 10 min, high priority [pending]
  08:05  Brushing (Luna) - 15 min, low priority [pending]
  08:30  Morning walk (Mochi) - 30 min, high priority [pending]
  08:30  Vet call (Luna) - 15 min, medium priority [pending]
  09:30  Medication (Luna) - 5 min, high priority [pending]
  18:00  Evening walk (Mochi) - 30 min, medium priority [pending]
  --:--  Grooming (Mochi) - 25 min, low priority [pending]
  --:--  Laser play (Luna) - 20 min, medium priority [pending]

Recurring tasks:
  Morning walk: done 2026-10-20, next due 2026-10-21 (daily)
  Grooming: done 2026-10-20, next due 2026-10-27 (weekly)
  Laser play: done, one-off so no new task

Luna's tasks:
  Breakfast (Luna) - 10 min, high priority [done]
  Medication (Luna) - 5 min, high priority [pending]
  Laser play (Luna) - 20 min, medium priority [done]
  Vet call (Luna) - 15 min, medium priority [pending]
  Brushing (Luna) - 15 min, low priority [pending]

Completed tasks:
  Morning walk (Mochi) - 30 min, high priority [done]
  Grooming (Mochi) - 25 min, low priority [done]
  Breakfast (Luna) - 10 min, high priority [done]
  Laser play (Luna) - 20 min, medium priority [done]

Pending tasks for Mochi, by time:
  08:30  Morning walk (Mochi) - 30 min, high priority [pending]
  18:00  Evening walk (Mochi) - 30 min, medium priority [pending]
  --:--  Grooming (Mochi) - 25 min, low priority [pending]
```

The final class design is in [diagrams/uml_final.mmd](diagrams/uml_final.mmd).
