"""PawPal+ logic layer.

Backend classes for the pet care planning assistant: CareTask, Pet, Owner and
Scheduler. The Scheduler reads every task through Owner.get_all_tasks() so a
plan always spans all of the owner's pets.
"""

PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}


def _to_minutes(hhmm):
    """Convert an "HH:MM" string to minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _to_hhmm(total_minutes):
    """Convert minutes since midnight to an "HH:MM" string."""
    total_minutes %= 24 * 60
    return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"


class CareTask:
    """One unit of pet care work (a walk, a feeding, a dose of meds)."""

    def __init__(
        self,
        title,
        duration_minutes,
        priority="medium",
        category="other",
        preferred_time=None,
        recurring="daily",
    ):
        if priority not in PRIORITY_SCORES:
            raise ValueError(f"priority must be one of {sorted(PRIORITY_SCORES)}")
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if preferred_time is not None:
            _to_minutes(preferred_time)  # raises ValueError if not "HH:MM"
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.preferred_time = preferred_time
        self.recurring = recurring
        self.completed = False
        self.pet = None  # set by Pet.add_task so a scheduled task knows whose it is

    def priority_score(self):
        """Return a sortable number for this task's priority (higher = more urgent)."""
        return PRIORITY_SCORES[self.priority]

    def mark_complete(self):
        """Mark this task as done for the day."""
        self.completed = True

    def fits_in(self, remaining_minutes):
        """Return True if this task can be done within the minutes left."""
        return self.duration_minutes <= remaining_minutes

    def __str__(self):
        pet = f" ({self.pet.name})" if self.pet else ""
        status = "done" if self.completed else "pending"
        return (
            f"{self.title}{pet} - {self.duration_minutes} min, "
            f"{self.priority} priority [{status}]"
        )


class Pet:
    """An animal in the owner's care, along with the tasks it needs."""

    def __init__(self, name, species, breed=None, age=None):
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.tasks = []

    def add_task(self, task):
        """Attach a CareTask to this pet."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, title):
        """Remove the task with the given title, if present."""
        for task in self.tasks:
            if task.title == title:
                self.tasks.remove(task)
                task.pet = None
                return True
        return False

    def tasks_by_priority(self):
        """Return this pet's tasks sorted most urgent first."""
        return sorted(self.tasks, key=lambda t: -t.priority_score())

    def pending_tasks(self):
        """Return the tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    """The person using PawPal+, their pets, and their daily time budget."""

    def __init__(self, name, available_minutes=0, preferences=None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets = []

    def add_pet(self, pet):
        """Add a Pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name):
        """Remove the pet with the given name, if present."""
        for pet in self.pets:
            if pet.name == pet_name:
                self.pets.remove(pet)
                return True
        return False

    def set_available_minutes(self, minutes):
        """Set how many minutes the owner has for pet care today."""
        if minutes < 0:
            raise ValueError("minutes cannot be negative")
        self.available_minutes = minutes

    def get_all_tasks(self, pending_only=False):
        """Return every pet's tasks together (optionally only the unfinished ones)."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.pending_tasks() if pending_only else pet.tasks)
        return tasks

    def total_task_load(self):
        """Return the total minutes required by every pending task across all pets."""
        return sum(t.duration_minutes for t in self.get_all_tasks(pending_only=True))


class Scheduler:
    """Builds a daily plan from an owner's pets, tasks, and time budget."""

    def __init__(self, owner, start_time="08:00", available_minutes=None):
        self.owner = owner
        self.start_time = start_time
        # Optional override; None means "use owner.available_minutes".
        self.available_minutes = available_minutes
        self.scheduled = []  # list of (task, "HH:MM" start time)
        self.skipped = []  # list of (task, reason)

    def minutes_budget(self):
        """Return the time budget in effect: the override if set, else the owner's."""
        if self.available_minutes is not None:
            return self.available_minutes
        return self.owner.available_minutes

    def build_plan(self):
        """Select and order tasks into a daily plan. Populates scheduled and skipped."""
        self.scheduled = []
        self.skipped = []
        remaining = self.minutes_budget()

        # Select by priority (greedy), reading across all pets via the Owner.
        chosen = []
        for task in self.sort_tasks(self.owner.get_all_tasks(pending_only=True)):
            if self.fits(task, remaining):
                chosen.append(task)
                remaining -= task.duration_minutes
            else:
                self.skipped.append(
                    (task, f"needs {task.duration_minutes} min but only {remaining} left")
                )

        # Order the chosen tasks by preferred time, then assign sequential start times.
        chosen.sort(
            key=lambda t: (
                _to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
                -t.priority_score(),
            )
        )
        clock = _to_minutes(self.start_time)
        for task in chosen:
            if task.preferred_time:
                clock = max(clock, _to_minutes(task.preferred_time))
            self.scheduled.append((task, _to_hhmm(clock)))
            clock += task.duration_minutes
        return self.scheduled

    def sort_tasks(self, tasks):
        """Return the given tasks ordered by the scheduling rules."""
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority_score(),
                _to_minutes(t.preferred_time) if t.preferred_time else 24 * 60,
                t.duration_minutes,
            ),
        )

    def fits(self, task, remaining):
        """Return True if the task can still be placed in the remaining time."""
        return task.fits_in(remaining)

    def explain(self):
        """Return a human-readable explanation of why the plan looks the way it does."""
        lines = [
            "Tasks are chosen highest priority first (earlier preferred time, then "
            "shorter duration break ties) until the time budget runs out, then "
            "ordered by preferred time."
        ]
        for task, start in self.scheduled:
            lines.append(
                f"- {start}: {task.title} for {task.pet.name if task.pet else '?'} "
                f"({task.priority} priority, {task.duration_minutes} min)"
            )
        for task, reason in self.skipped:
            lines.append(f"- Skipped {task.title}: {reason}")
        return "\n".join(lines)

    def summary(self):
        """Return a short overview of the plan (counts, time used, time left)."""
        used = sum(t.duration_minutes for t, _ in self.scheduled)
        budget = self.minutes_budget()
        return (
            f"{len(self.scheduled)} scheduled, {len(self.skipped)} skipped; "
            f"{used} of {budget} min used, {budget - used} left"
        )
