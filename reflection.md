# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions:

1. enter basic owner + pet info
2. schedule times to feed pet
3. see daily tasks

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

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

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
