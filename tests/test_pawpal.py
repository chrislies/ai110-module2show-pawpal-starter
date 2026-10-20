from pawpal_system import CareTask, Pet


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
