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

    mochi.add_task(CareTask("Morning walk", 30, "high", "walk", preferred_time="08:30", recurring="daily"))
    mochi.add_task(CareTask("Grooming", 25, "low", "grooming", recurring="weekly"))
    mochi.add_task(CareTask("Evening walk", 30, "medium", "walk", preferred_time="18:00"))
    luna.add_task(CareTask("Breakfast", 10, "high", "feed", preferred_time="08:00"))
    luna.add_task(CareTask("Medication", 5, "high", "meds", preferred_time="09:30"))
    luna.add_task(CareTask("Laser play", 20, "medium", "enrichment"))

    # Deliberate clashes: same pet at the same time, and two pets overlapping.
    luna.add_task(CareTask("Vet call", 15, "medium", "vet", preferred_time="08:30"))
    luna.add_task(CareTask("Brushing", 15, "low", "grooming", preferred_time="08:05"))

    scheduler = Scheduler(owner, start_time="08:00")
    scheduler.build_plan()
    print_schedule(scheduler)

    print("\nConflict check:")
    conflicts = scheduler.detect_conflicts()
    for warning in conflicts or ["No conflicts found."]:
        print(f"  {warning}")

    print("\nAll tasks sorted by preferred time:")
    for task in scheduler.sort_by_time():
        print(f"  {task.preferred_time or '--:--'}  {task}")

    luna.tasks[0].mark_complete()  # Breakfast is done

    print("\nRecurring tasks:")
    for task in (mochi.tasks[0], mochi.tasks[1], luna.tasks[2]):
        following = scheduler.mark_task_complete(task)
        if following:
            print(f"  {task.title}: done {task.due_date}, next due {following.due_date} ({task.recurring})")
        else:
            print(f"  {task.title}: done, one-off so no new task")
    print("\nLuna's tasks:")
    for task in scheduler.filter_tasks(pet_name="Luna"):
        print(f"  {task}")
    print("\nCompleted tasks:")
    for task in scheduler.filter_tasks(completed=True):
        print(f"  {task}")
    print("\nPending tasks for Mochi, by time:")
    for task in scheduler.sort_by_time(scheduler.filter_tasks("Mochi", completed=False)):
        print(f"  {task.preferred_time or '--:--'}  {task}")


if __name__ == "__main__":
    main()
