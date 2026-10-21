# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions:

1. enter basic owner + pet info
2. schedule times to feed pet
3. see daily tasks

My initial UML has four classes. Data lives in three of them (`Owner`, `Pet`, `CareTask`) and the planning logic is kept separate in `Scheduler`:

- **Owner** holds the user's name, their daily time budget (`available_minutes`), preferences, and their list of pets. It manages its pets and can report the total minutes of pending work across all of them.
- **Pet** holds the animal's details and its own list of `CareTask`s. It adds and removes tasks and can return its tasks sorted by priority or only the pending ones.
- **CareTask** is one unit of care (walk, feeding, meds). It stores duration, priority, category, preferred time, recurrence, and completion state. It knows how to turn its priority into a sortable score, mark itself done, and check whether it fits in the time left.
- **Scheduler** takes an `Owner` and builds the daily plan. It sorts tasks, places them within the time budget, records what was scheduled and what was skipped, and explains why.

Relationships: Owner has many Pets, Pet has many CareTasks, and Scheduler uses an Owner.

Object brainstorm

1. Owner — the person using the app

- Attributes: name, available_minutes (time budget for the day), preferences (e.g. preferred start time, "no walks after dark"), pets (list)
- Methods: add_pet(pet), remove_pet(pet_name), set_available_minutes(mins), total_task_load() — sum of all pets' task durations

2. Pet — the animal being cared for

- Attributes: name, species, breed, age, tasks (list of CareTask)
- Methods: add_task(task), remove_task(title), tasks_by_priority(), pending_tasks() — tasks not yet done today

3. CareTask — one unit of care work

- Attributes: title, duration_minutes, priority (low/medium/high), category (walk/feed/meds/grooming/enrichment), preferred_time, recurring (daily/weekly), completed
- Methods: priority_score() — maps priority to a sortable number, mark_complete(), fits_in(remaining_minutes), **str**()

4. Scheduler — builds the daily plan

- Attributes: owner, start_time, available_minutes, scheduled (list of placed tasks), skipped (list of (task, reason))
- Methods: build_plan(), sort_tasks(tasks), fits(task, remaining), explain() — the "why this plan" narrative, summary()

**b. Design changes**

I asked my AI assistant to review `pawpal_system.py` for missing relationships and logic bottlenecks. It raised these points, and I made two changes:

1. **Tasks didn't know their pet (changed).** `Scheduler.scheduled` would have been a flat list of tasks, so the plan couldn't say "Walk — Mochi." I added a `pet` back-reference on `CareTask`, set when `Pet.add_task` is called. `Scheduler.scheduled` now holds `(task, start_time)` pairs, so each scheduled task also carries its start time.
2. **Two sources of truth for the time budget (changed).** Both `Owner` and `Scheduler` had `available_minutes`, which could disagree. I kept the Scheduler field as an optional override (`None` means use the owner's) and added `minutes_budget()` so the scheduler has a single place to read the effective budget.
3. **Not changed yet, noted for later:**
   - Tasks are removed by title, which is ambiguous if two pets both have a "Walk". I'll handle that when implementing, either by removing within a single pet or by using IDs.
   - `completed` never resets for recurring tasks, so a daily task stays done forever. The next iteration needs a reset or a per-day completion record.
   - `priority` and `preferred_time` are plain strings. They should be validated (low/medium/high, "HH:MM") when implemented.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler works within four constraints:

- **Time budget.** The owner's available minutes for the day are a hard limit. A task that no longer fits is skipped, and the plan records why.
- **Priority.** Tasks are chosen high, then medium, then low. Among equal priorities, an earlier preferred time wins, then the shorter task.
- **Preferred time.** Chosen tasks are ordered by preferred time and given start times. A task never starts before its preferred time, and tasks that would overlap are pushed later.
- **Due date.** Only tasks due today or earlier are planned, so tomorrow's copy of a daily task stays out of today's plan.

I put the time budget first because it is the one constraint that cannot bend: there are only so many minutes. Priority comes next because the owner's main question is "what must not be skipped?" (medication before grooming). Preferred time is a preference, so it shapes the order but never causes a task to be dropped.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler picks tasks greedily by priority, so it never searches for the
combination of tasks that would fill the owner's time best. For example, with
30 minutes free it takes a 25-minute high-priority task and skips two
10-minute medium-priority tasks, even though the two would have used the time
well. A smarter knapsack-style search would pack more in, but it is harder to
explain, and a pet owner expects "important things first". The explain()
output can also state one simple rule for every skipped task.

Conflict detection makes a related tradeoff. It checks whether the preferred
time windows (start plus duration) overlap, not just exact time matches. That
catches a 08:00 feeding that runs into an 08:05 brushing. It only warns and
never reorders anything, because build_plan already pushes tasks back so the
final schedule has no overlaps, and silently dropping a task the owner asked
for would be worse than a warning. It also ignores tasks with no preferred
time, since the scheduler is free to place those anywhere.

I asked the AI how detect_conflicts could be simplified. Its suggestion was to
replace my nested loop (with an early break once later tasks start after the
current one ends) by itertools.combinations over the sorted tasks. I kept
that version: it is shorter and easier to read, and giving up the early break
costs nothing at the scale of a few dozen tasks. The pet-name label is still a
short separate expression, because folding it into the message made the line
hard to read.

---

## 3. AI Collaboration

**a. How you used AI**

I used the AI assistant for design review (it spotted that tasks did not know their pet and that the time budget lived in two places), for implementing each phase in small steps (classes, then Streamlit wiring, then sorting, filtering, recurrence, and conflicts), for drafting tests, and for keeping the docs and UML in line with the code. The most useful prompts were narrow and named the method and the behavior I wanted, for example "add `sort_by_time()` that orders tasks by their `HH:MM` time". Asking it to review finished code for missing relationships and bottlenecks also paid off. The most effective workflow was having it edit several files at once and then run `main.py` and `pytest` straight away, so every change was checked by real output.

TODO (yours to fill in): how did using separate chat sessions for each phase (design, algorithms, testing) help you stay organized, and what would you do differently?

**b. Judgment and verification**

My AI design review raised five issues, and I did not accept all of them as-is. I made the two that fixed real problems now (the `pet` back-reference on `CareTask`, and a single `minutes_budget()` for the time budget) and deliberately deferred the rest (remove-by-title ambiguity, `completed` never resetting, and string validation) until the logic existed to need them. Doing everything at once would have grown the design before I knew what the scheduler actually needed. The "completed never resets" issue was later solved a different way than a reset flag: completing a recurring task creates a new `CareTask` for the next date, so each occurrence keeps its own history. A second case was the `detect_conflicts` simplification. I took the shorter `itertools.combinations` version but kept the pet-name label as a separate expression because merging it into the message hurt readability.

I checked AI suggestions by running them: `python main.py` with deliberately out-of-order and clashing tasks, then the pytest suite. I also read the generated code before keeping it.

---

## 4. Testing and Verification

**a. What you tested**

I tested the five behaviors that make the scheduler "smart": sorting (chronological order, untimed tasks last), filtering (by pet and status), recurrence (daily and weekly due dates, month and year rollover, one-offs), conflict detection (same time, overlapping windows, back-to-back tasks not flagged), and plan building (priority wins when time is short, same-time tasks are pushed apart). I also tested input validation and the empty cases (no tasks, unknown pet). These matter because each one is a place where a quiet mistake would hand the owner a wrong plan without any error.

**b. Confidence**

I am fairly confident (4 out of 5). All 24 tests pass. I did not automate tests of the Streamlit UI; I checked it with a scripted run and by hand. With more time I would test: tasks that run past midnight, an owner with zero available minutes, two pets with the same name, many tasks with the same preferred time, a weekly task completed several days late, and a completed recurring task being completed twice.

---

## 5. Reflection

**a. What went well**

I am most satisfied with how the backend and the UI stay separate. All scheduling lives in `pawpal_system.py`, so the same logic runs from the terminal demo, the tests, and the Streamlit app, and conflict warnings reach the owner as plain-language messages in the UI.

**b. What you would improve**

I would let owners edit and delete tasks in the UI, since a conflicting task can currently only be worked around by adding a new one. I would also make conflict detection compare the times the plan actually assigns, replace the greedy picker with a better packing of tasks into the available time, and add per-day completion records.

**c. Key takeaway**

Working with a powerful AI tool made me the lead architect: it can write a lot of code quickly, but it does not decide what the system should be. I set the boundaries (logic in `pawpal_system.py`, UI in `app.py`), decided which suggestions to take now and which to defer, and chose clarity over cleverness when the two conflicted. The habit that mattered most was verifying everything by running it, with a demo that deliberately triggers the edge cases, then tests that pin them down, then the UI.
