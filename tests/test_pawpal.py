from datetime import date

import pytest

from pawpal_system import CareTask, Owner, Pet, Scheduler


def make_scheduler(minutes=120):
    """Return (scheduler, mochi, luna) with an owner who has two empty pets."""
    owner = Owner("Sam", available_minutes=minutes)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    return Scheduler(owner), mochi, luna


# --- Basics -----------------------------------------------------------------


def test_mark_complete_changes_status():
    task = CareTask("Walk", 30)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(CareTask("Walk", 30))
    assert len(pet.tasks) == 1
    pet.add_task(CareTask("Feed", 10))
    assert len(pet.tasks) == 2


def test_invalid_task_is_rejected():
    with pytest.raises(ValueError):
        CareTask("Walk", 0)
    with pytest.raises(ValueError):
        CareTask("Walk", 10, priority="urgent")
    with pytest.raises(ValueError):
        CareTask("Walk", 10, preferred_time="8am")


# --- Sorting ----------------------------------------------------------------


def test_sort_by_time_is_chronological_across_pets():
    sched, mochi, luna = make_scheduler()
    mochi.add_task(CareTask("Evening walk", 30, preferred_time="18:00"))
    luna.add_task(CareTask("Breakfast", 10, preferred_time="08:00"))
    mochi.add_task(CareTask("Lunch", 10, preferred_time="12:30"))

    titles = [t.title for t in sched.sort_by_time()]

    assert titles == ["Breakfast", "Lunch", "Evening walk"]


def test_sort_by_time_puts_untimed_tasks_last():
    sched, mochi, _ = make_scheduler()
    mochi.add_task(CareTask("Grooming", 20))
    mochi.add_task(CareTask("Walk", 30, preferred_time="09:00"))

    assert [t.title for t in sched.sort_by_time()] == ["Walk", "Grooming"]


def test_sort_by_time_handles_unpadded_hours():
    sched, mochi, _ = make_scheduler()
    mochi.add_task(CareTask("Late", 10, preferred_time="10:00"))
    mochi.add_task(CareTask("Early", 10, preferred_time="8:30"))

    assert [t.title for t in sched.sort_by_time()] == ["Early", "Late"]


def test_sort_by_time_with_no_tasks_returns_empty_list():
    sched, _, _ = make_scheduler()
    assert sched.sort_by_time() == []


# --- Filtering --------------------------------------------------------------


def test_filter_by_pet_and_status():
    sched, mochi, luna = make_scheduler()
    walk = CareTask("Walk", 30)
    feed = CareTask("Feed", 10)
    mochi.add_task(walk)
    luna.add_task(feed)
    feed.mark_complete()

    assert sched.filter_tasks(pet_name="Mochi") == [walk]
    assert sched.filter_tasks(completed=True) == [feed]
    assert sched.filter_tasks(completed=False) == [walk]
    assert sched.filter_tasks(pet_name="Luna", completed=False) == []
    assert len(sched.filter_tasks()) == 2


def test_filter_unknown_pet_returns_empty_list():
    sched, mochi, _ = make_scheduler()
    mochi.add_task(CareTask("Walk", 30))
    assert sched.filter_tasks(pet_name="Rex") == []


# --- Recurrence -------------------------------------------------------------


def test_completing_daily_task_creates_task_for_next_day():
    sched, mochi, _ = make_scheduler()
    walk = CareTask("Walk", 30, recurring="daily", due_date=date(2026, 3, 10))
    mochi.add_task(walk)

    following = sched.mark_task_complete(walk)

    assert walk.completed is True
    assert following is not None
    assert following.due_date == date(2026, 3, 11)
    assert following.completed is False
    assert following in mochi.tasks
    assert following.pet is mochi
    assert len(mochi.tasks) == 2


def test_completing_weekly_task_creates_task_seven_days_later():
    sched, mochi, _ = make_scheduler()
    groom = CareTask("Groom", 25, recurring="weekly", due_date=date(2026, 3, 10))
    mochi.add_task(groom)

    assert sched.mark_task_complete(groom).due_date == date(2026, 3, 17)


def test_daily_recurrence_rolls_over_month_and_year():
    sched, mochi, _ = make_scheduler()
    task = CareTask("Meds", 5, recurring="daily", due_date=date(2026, 12, 31))
    mochi.add_task(task)

    assert sched.mark_task_complete(task).due_date == date(2027, 1, 1)


def test_one_off_task_does_not_recur():
    sched, mochi, _ = make_scheduler()
    task = CareTask("Vet visit", 60)
    mochi.add_task(task)

    assert sched.mark_task_complete(task) is None
    assert len(mochi.tasks) == 1


def test_next_occurrence_copies_task_details():
    task = CareTask("Walk", 30, "high", "walk", "08:30", "daily")
    following = task.next_occurrence()

    assert (following.title, following.duration_minutes, following.priority) == (
        "Walk",
        30,
        "high",
    )
    assert (following.category, following.preferred_time) == ("walk", "08:30")


def test_future_occurrence_is_not_planned_today():
    sched, mochi, _ = make_scheduler()
    walk = CareTask("Walk", 30, recurring="daily")
    mochi.add_task(walk)
    sched.mark_task_complete(walk)

    # Today's walk is done and tomorrow's is not due yet.
    assert sched.build_plan() == []


# --- Conflict detection -----------------------------------------------------


def test_exact_same_time_is_flagged_for_one_pet():
    sched, mochi, _ = make_scheduler()
    mochi.add_task(CareTask("Walk", 30, preferred_time="08:00"))
    mochi.add_task(CareTask("Grooming", 20, preferred_time="08:00"))

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Grooming" in warnings[0]
    assert "Mochi" in warnings[0]


def test_same_time_across_pets_is_flagged_with_both_names():
    sched, mochi, luna = make_scheduler()
    mochi.add_task(CareTask("Walk", 30, preferred_time="08:00"))
    luna.add_task(CareTask("Breakfast", 10, preferred_time="08:00"))

    warnings = sched.detect_conflicts()

    assert len(warnings) == 1
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


def test_overlapping_windows_are_flagged():
    sched, mochi, _ = make_scheduler()
    mochi.add_task(CareTask("Walk", 30, preferred_time="08:00"))
    mochi.add_task(CareTask("Feed", 10, preferred_time="08:20"))

    assert len(sched.detect_conflicts()) == 1


def test_back_to_back_tasks_do_not_conflict():
    sched, mochi, _ = make_scheduler()
    mochi.add_task(CareTask("Walk", 30, preferred_time="08:00"))
    mochi.add_task(CareTask("Feed", 10, preferred_time="08:30"))

    assert sched.detect_conflicts() == []


def test_untimed_and_completed_tasks_never_conflict():
    sched, mochi, _ = make_scheduler()
    done = CareTask("Walk", 30, preferred_time="08:00")
    mochi.add_task(done)
    done.mark_complete()
    mochi.add_task(CareTask("Feed", 10, preferred_time="08:00"))
    mochi.add_task(CareTask("Play", 10))
    mochi.add_task(CareTask("Brush", 10))

    assert sched.detect_conflicts() == []


def test_detect_conflicts_with_no_tasks_returns_empty_list():
    sched, _, _ = make_scheduler()
    assert sched.detect_conflicts() == []


# --- Plan building ----------------------------------------------------------


def test_build_plan_prefers_high_priority_when_time_is_short():
    sched, mochi, _ = make_scheduler(minutes=30)
    mochi.add_task(CareTask("Play", 30, priority="low"))
    mochi.add_task(CareTask("Meds", 30, priority="high"))

    plan = sched.build_plan()

    assert [t.title for t, _ in plan] == ["Meds"]
    assert [t.title for t, _ in sched.skipped] == ["Play"]


def test_build_plan_pushes_same_time_tasks_apart():
    sched, mochi, luna = make_scheduler()
    mochi.add_task(CareTask("Walk", 30, preferred_time="08:00"))
    luna.add_task(CareTask("Breakfast", 10, preferred_time="08:00"))

    plan = sched.build_plan()

    # Shorter task wins the tie and goes first; the other starts when it ends.
    assert [(t.title, start) for t, start in plan] == [
        ("Breakfast", "08:00"),
        ("Walk", "08:10"),
    ]


def test_build_plan_with_no_tasks_is_empty():
    sched, _, _ = make_scheduler()
    assert sched.build_plan() == []
    assert sched.skipped == []
