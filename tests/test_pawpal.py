"""Quick tests for the PawPal+ logic layer."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler(*pets: Pet, minutes: int = 120) -> Scheduler:
    owner = Owner("Jordan", available_minutes=minutes)
    for pet in pets:
        owner.add_pet(pet)
    return Scheduler(owner)


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Breakfast", 10, "high"))

    assert len(pet.tasks) == 1


def test_time_is_zero_padded_and_sorts_correctly():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Lunch", 10, "high", time="12:00"))
    pet.add_task(Task("Breakfast", 10, "high", time="8:00"))
    scheduler = make_scheduler(pet)

    ordered = scheduler.sort_by_time(pet.tasks)

    assert ordered[0].time == "08:00"
    assert [task.title for task in ordered] == ["Breakfast", "Lunch"]


def test_filter_by_pet_returns_only_that_pets_tasks():
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    mochi.add_task(Task("Walk", 30, "high"))
    luna.add_task(Task("Litter box", 10, "medium"))
    scheduler = make_scheduler(mochi, luna)

    result = scheduler.filter_tasks(pet_name="Luna")

    assert [task.title for task in result] == ["Litter box"]


def test_completing_daily_task_creates_one_due_tomorrow():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Breakfast", 10, "high", frequency="daily"))

    next_task = pet.complete_task("Breakfast")

    assert pet.tasks[0].completed is True
    assert next_task is not None and next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert len(pet.tasks) == 2


def test_completing_once_task_does_not_repeat():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Vet visit", 60, "high", frequency="once"))

    next_task = pet.complete_task("Vet visit")

    assert next_task is None
    assert len(pet.tasks) == 1


def test_task_due_tomorrow_is_not_planned_today():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Bath", 20, "low", due_date=date.today() + timedelta(days=1)))
    scheduler = make_scheduler(pet)

    assert scheduler.generate_plan() == []


def test_overlapping_tasks_are_reported_as_conflict():
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
    luna.add_task(Task("Medication", 5, "high", time="07:45"))
    scheduler = make_scheduler(mochi, luna)

    scheduler.generate_plan()

    assert len(scheduler.conflicts) == 1
    assert "Morning walk" in scheduler.conflicts[0]
    assert "Medication" in scheduler.conflicts[0]


def test_back_to_back_tasks_are_not_a_conflict():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", time="07:30"))
    pet.add_task(Task("Breakfast", 10, "high", time="08:00"))
    scheduler = make_scheduler(pet)

    assert scheduler.find_conflicts(pet.tasks) == []


def test_same_time_same_pet_is_a_conflict():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", 30, "high", time="07:30"))
    pet.add_task(Task("Flea medicine", 5, "high", time="07:30"))
    scheduler = make_scheduler(pet)

    assert len(scheduler.find_conflicts(pet.tasks)) == 1


def test_completing_weekly_task_creates_one_due_in_seven_days():
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Brushing", 20, "low", frequency="weekly"))

    next_task = pet.complete_task("Brushing")

    assert next_task.due_date == date.today() + timedelta(days=7)
