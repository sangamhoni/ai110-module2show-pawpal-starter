"""Quick tests for the PawPal+ logic layer."""

from datetime import date, timedelta

import pytest

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


# --- Sorting ---

def test_sort_by_time_returns_chronological_order():
    pet = Pet("Mochi", "dog")
    for title, time in [("Dinner", "18:00"), ("Walk", "07:30"), ("Lunch", "12:00"), ("Meds", "9:15")]:
        pet.add_task(Task(title, 10, "high", time=time))
    scheduler = make_scheduler(pet)

    times = [task.time for task in scheduler.sort_by_time(pet.tasks)]

    assert times == ["07:30", "09:15", "12:00", "18:00"]


def test_sort_by_time_puts_untimed_tasks_last():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Play", 15, "low"))
    pet.add_task(Task("Walk", 30, "high", time="07:30"))
    scheduler = make_scheduler(pet)

    assert [task.title for task in scheduler.sort_by_time(pet.tasks)] == ["Walk", "Play"]


def test_sort_by_priority_breaks_ties_with_shorter_task():
    tasks = [Task("Long", 30, "high"), Task("Low", 5, "low"), Task("Short", 10, "high")]
    scheduler = make_scheduler()

    assert [task.title for task in scheduler.sort_by_priority(tasks)] == ["Short", "Long", "Low"]


# --- Recurrence ---

def test_overdue_daily_task_next_copy_is_due_tomorrow():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Breakfast", 10, "high", due_date=date.today() - timedelta(days=3)))

    next_task = pet.complete_task("Breakfast")

    assert next_task.due_date == date.today() + timedelta(days=1)


def test_completing_same_title_twice_targets_the_new_copy():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Breakfast", 10, "high"))

    pet.complete_task("Breakfast")
    pet.complete_task("Breakfast")

    assert [task.completed for task in pet.tasks] == [True, True, False]
    assert pet.tasks[-1].due_date == date.today() + timedelta(days=2)


def test_completed_daily_task_leaves_nothing_due_today():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Breakfast", 10, "high"))
    pet.complete_task("Breakfast")
    scheduler = make_scheduler(pet)

    assert scheduler.generate_plan() == []


# --- Conflict detection ---

def test_exact_same_time_different_pets_is_a_conflict():
    mochi, luna = Pet("Mochi", "dog"), Pet("Luna", "cat")
    mochi.add_task(Task("Breakfast", 10, "high", time="08:00"))
    luna.add_task(Task("Breakfast", 5, "high", time="08:00"))
    scheduler = make_scheduler(mochi, luna)

    scheduler.generate_plan()

    assert len(scheduler.conflicts) == 1
    assert "Mochi" in scheduler.conflicts[0] and "Luna" in scheduler.conflicts[0]


def test_long_task_conflicts_with_non_adjacent_later_task():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Long walk", 60, "high", time="07:00"))
    pet.add_task(Task("Meds", 5, "high", time="07:10"))
    pet.add_task(Task("Breakfast", 10, "high", time="07:30"))
    scheduler = make_scheduler(pet)

    conflicts = scheduler.find_conflicts(pet.tasks)

    assert len(conflicts) == 2
    assert all("Long walk" in warning for warning in conflicts)


def test_untimed_tasks_never_conflict():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Play", 15, "low"))
    pet.add_task(Task("Brush", 10, "low"))
    scheduler = make_scheduler(pet)

    assert scheduler.find_conflicts(pet.tasks) == []


def test_skipped_task_is_not_reported_as_conflict():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high", time="07:30"))
    pet.add_task(Task("Bath", 20, "low", time="07:30"))
    scheduler = make_scheduler(pet, minutes=30)

    scheduler.generate_plan()

    assert [task.title for task in scheduler.skipped_tasks] == ["Bath"]
    assert scheduler.conflicts == []


# --- Planning edge cases ---

def test_pet_with_no_tasks_gives_empty_plan():
    scheduler = make_scheduler(Pet("Mochi", "dog"))

    assert scheduler.generate_plan() == []
    assert scheduler.conflicts == []
    assert "No tasks planned" in scheduler.explain_plan()


def test_task_that_exactly_fills_time_is_planned():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high"))
    scheduler = make_scheduler(pet, minutes=30)

    assert [task.title for task in scheduler.generate_plan()] == ["Walk"]


def test_shorter_lower_priority_task_fills_leftover_time():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high"))
    pet.add_task(Task("Bath", 20, "medium"))
    pet.add_task(Task("Treat", 10, "low"))
    scheduler = make_scheduler(pet, minutes=40)

    planned = scheduler.generate_plan()

    assert [task.title for task in planned] == ["Walk", "Treat"]
    assert [task.title for task in scheduler.skipped_tasks] == ["Bath"]


def test_generate_plan_twice_does_not_duplicate():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high"))
    scheduler = make_scheduler(pet)

    scheduler.generate_plan()
    scheduler.generate_plan()

    assert len(scheduler.planned_tasks) == 1


# --- Validation ---

@pytest.mark.parametrize(
    "bad_value",
    [{"priority": "urgent"}, {"duration_minutes": 0}, {"time": "25:00"}, {"frequency": "monthly"}],
)
def test_invalid_task_values_raise(bad_value):
    values = {"title": "Walk", "duration_minutes": 30, "priority": "high"} | bad_value

    with pytest.raises(ValueError):
        Task(**values)


def test_failed_edit_leaves_task_unchanged():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", 30, "high"))

    with pytest.raises(ValueError):
        pet.edit_task("Walk", 0, "low")

    assert (pet.tasks[0].duration_minutes, pet.tasks[0].priority) == (30, "high")
