"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. These are skeletons
generated from diagrams/uml.mmd -- attributes and method signatures only,
no scheduling behavior yet.
"""


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
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.category = category
        self.preferred_time = preferred_time
        self.recurring = recurring
        self.completed = False

    def priority_score(self):
        """Return a sortable number for this task's priority (higher = more urgent)."""
        pass

    def mark_complete(self):
        """Mark this task as done for the day."""
        pass

    def fits_in(self, remaining_minutes):
        """Return True if this task can be done within the minutes left."""
        pass

    def __str__(self):
        pass


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
        pass

    def remove_task(self, title):
        """Remove the task with the given title, if present."""
        pass

    def tasks_by_priority(self):
        """Return this pet's tasks sorted most urgent first."""
        pass

    def pending_tasks(self):
        """Return the tasks that are not yet completed."""
        pass


class Owner:
    """The person using PawPal+, their pets, and their daily time budget."""

    def __init__(self, name, available_minutes=0, preferences=None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets = []

    def add_pet(self, pet):
        """Add a Pet to this owner."""
        pass

    def remove_pet(self, pet_name):
        """Remove the pet with the given name, if present."""
        pass

    def set_available_minutes(self, minutes):
        """Set how many minutes the owner has for pet care today."""
        pass

    def total_task_load(self):
        """Return the total minutes required by every pending task across all pets."""
        pass


class Scheduler:
    """Builds a daily plan from an owner's pets, tasks, and time budget."""

    def __init__(self, owner, start_time="08:00", available_minutes=None):
        self.owner = owner
        self.start_time = start_time
        self.available_minutes = available_minutes
        self.scheduled = []
        self.skipped = []

    def build_plan(self):
        """Select and order tasks into a daily plan. Populates scheduled and skipped."""
        pass

    def sort_tasks(self, tasks):
        """Return the given tasks ordered by the scheduling rules."""
        pass

    def fits(self, task, remaining):
        """Return True if the task can still be placed in the remaining time."""
        pass

    def explain(self):
        """Return a human-readable explanation of why the plan looks the way it does."""
        pass

    def summary(self):
        """Return a short overview of the plan (counts, time used, time left)."""
        pass
