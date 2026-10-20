"""CLI demo for the PawPal+ logic layer."""

from pawpal_system import CareTask, Owner, Pet, Scheduler


def print_schedule(scheduler):
    """Print the scheduler's plan as a readable table."""
    print(f"Today's Schedule for {scheduler.owner.name}")
    print("=" * 60)
    print(f"{'Time':<7}{'Pet':<9}{'Task':<18}{'Min':>4}  Priority")
    print("-" * 60)
    for task, start in scheduler.scheduled:
        print(
            f"{start:<7}{task.pet.name:<9}{task.title:<18}"
            f"{task.duration_minutes:>4}  {task.priority}"
        )
    if scheduler.skipped:
        print("-" * 60)
        print("Skipped:")
        for task, reason in scheduler.skipped:
            print(f"  {task.pet.name}: {task.title} ({reason})")
    print("=" * 60)
    print(scheduler.summary())


def main():
    owner = Owner("Sam", available_minutes=90)

    mochi = Pet("Mochi", "dog", breed="Corgi", age=4)
    luna = Pet("Luna", "cat", age=2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(CareTask("Morning walk", 30, "high", "walk", preferred_time="08:30"))
    mochi.add_task(CareTask("Grooming", 25, "low", "grooming"))
    mochi.add_task(CareTask("Evening walk", 30, "medium", "walk", preferred_time="18:00"))
    luna.add_task(CareTask("Breakfast", 10, "high", "feed", preferred_time="08:00"))
    luna.add_task(CareTask("Medication", 5, "high", "meds", preferred_time="09:30"))
    luna.add_task(CareTask("Laser play", 20, "medium", "enrichment"))

    scheduler = Scheduler(owner, start_time="08:00")
    scheduler.build_plan()
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
