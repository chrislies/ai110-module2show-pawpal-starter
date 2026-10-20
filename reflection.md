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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
