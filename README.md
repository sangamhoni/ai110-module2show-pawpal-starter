# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output of `python main.py`:

```
Completed 'Litter box' -> next one due 2026-10-12

All tasks (order added):
  18:00  Evening walk   Mochi  todo  due 2026-10-11
  08:00  Breakfast      Mochi  todo  due 2026-10-11
  07:30  Morning walk   Mochi  todo  due 2026-10-11
  07:30  Flea medicine  Mochi  todo  due 2026-10-11
  19:00  Brushing       Luna   todo  due 2026-10-11
  12:00  Litter box     Luna   done  due 2026-10-11
  07:45  Medication     Luna   todo  due 2026-10-11
  08:00  Breakfast      Luna   todo  due 2026-10-11
  12:00  Litter box     Luna   todo  due 2026-10-12

Sorted by time:
  07:30  Morning walk   Mochi  todo  due 2026-10-11
  07:30  Flea medicine  Mochi  todo  due 2026-10-11
  07:45  Medication     Luna   todo  due 2026-10-11
  08:00  Breakfast      Mochi  todo  due 2026-10-11
  08:00  Breakfast      Luna   todo  due 2026-10-11
  12:00  Litter box     Luna   done  due 2026-10-11
  12:00  Litter box     Luna   todo  due 2026-10-12
  18:00  Evening walk   Mochi  todo  due 2026-10-11
  19:00  Brushing       Luna   todo  due 2026-10-11

Mochi's tasks:
  07:30  Morning walk   Mochi  todo  due 2026-10-11
  07:30  Flea medicine  Mochi  todo  due 2026-10-11
  08:00  Breakfast      Mochi  todo  due 2026-10-11
  18:00  Evening walk   Mochi  todo  due 2026-10-11

Completed tasks:
  12:00  Litter box     Luna   done  due 2026-10-11

Luna's unfinished tasks:
  07:45  Medication     Luna   todo  due 2026-10-11
  08:00  Breakfast      Luna   todo  due 2026-10-11
  12:00  Litter box     Luna   todo  due 2026-10-12
  19:00  Brushing       Luna   todo  due 2026-10-11

==================================================
  Today's Schedule for Jordan
==================================================
  Time   Task            Pet      Min  Priority
  ----------------------------------------------
  07:30  Flea medicine   Mochi      5  high
  07:30  Morning walk    Mochi     30  high
  07:45  Medication      Luna       5  high
  08:00  Breakfast       Luna       5  high
  08:00  Breakfast       Mochi     10  high
  18:00  Evening walk    Mochi     30  medium
  ----------------------------------------------
  85 of 90 minutes used

  Skipped (not enough time):
    - Brushing (Luna, 20 min, low)

  Time conflicts (one person can't do both):
    - Flea medicine (Mochi) at 07:30 overlaps Morning walk (Mochi) at 07:30
    - Morning walk (Mochi) at 07:30 overlaps Medication (Luna) at 07:45
    - Breakfast (Luna) at 08:00 overlaps Breakfast (Mochi) at 08:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite (from the project folder, with .venv activated):
python -m pytest

# Show each test by name:
python -m pytest -v
```

**What the tests cover** (30 tests in `tests/test_pawpal.py`):

- **Sorting:** tasks come back in clock order (including `"9:15"` vs `"12:00"`), untimed tasks go last, and priority ties go to the shorter task.
- **Recurring tasks:** completing a daily task creates a new one due tomorrow (weekly: +7 days). An overdue task's next copy is due tomorrow, not in the past. `once` tasks don't repeat.
- **Conflict detection:** tasks at the exact same time are flagged (same pet or different pets), as are partial overlaps and a long task overlapping a later, non-adjacent one. Back-to-back tasks, untimed tasks, and skipped tasks are not flagged.
- **Planning:** only unfinished tasks due today are planned. A task that exactly fills the remaining time fits, and a shorter low-priority task can still fill leftover time. A pet with no tasks gives an empty plan, and running the plan twice doesn't duplicate it.
- **Validation:** bad priority, duration, time, or frequency raises `ValueError`, and a failed edit leaves the task unchanged.

Output of `python -m pytest -v`:

```
tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  3%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  6%]
tests/test_pawpal.py::test_time_is_zero_padded_and_sorts_correctly PASSED [ 10%]
tests/test_pawpal.py::test_filter_by_pet_returns_only_that_pets_tasks PASSED [ 13%]
tests/test_pawpal.py::test_completing_daily_task_creates_one_due_tomorrow PASSED [ 16%]
tests/test_pawpal.py::test_completing_once_task_does_not_repeat PASSED   [ 20%]
tests/test_pawpal.py::test_task_due_tomorrow_is_not_planned_today PASSED [ 23%]
tests/test_pawpal.py::test_overlapping_tasks_are_reported_as_conflict PASSED [ 26%]
tests/test_pawpal.py::test_back_to_back_tasks_are_not_a_conflict PASSED  [ 30%]
tests/test_pawpal.py::test_same_time_same_pet_is_a_conflict PASSED       [ 33%]
tests/test_pawpal.py::test_completing_weekly_task_creates_one_due_in_seven_days PASSED [ 36%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 40%]
tests/test_pawpal.py::test_sort_by_time_puts_untimed_tasks_last PASSED   [ 43%]
tests/test_pawpal.py::test_sort_by_priority_breaks_ties_with_shorter_task PASSED [ 46%]
tests/test_pawpal.py::test_overdue_daily_task_next_copy_is_due_tomorrow PASSED [ 50%]
tests/test_pawpal.py::test_completing_same_title_twice_targets_the_new_copy PASSED [ 53%]
tests/test_pawpal.py::test_completed_daily_task_leaves_nothing_due_today PASSED [ 56%]
tests/test_pawpal.py::test_exact_same_time_different_pets_is_a_conflict PASSED [ 60%]
tests/test_pawpal.py::test_long_task_conflicts_with_non_adjacent_later_task PASSED [ 63%]
tests/test_pawpal.py::test_untimed_tasks_never_conflict PASSED           [ 66%]
tests/test_pawpal.py::test_skipped_task_is_not_reported_as_conflict PASSED [ 70%]
tests/test_pawpal.py::test_pet_with_no_tasks_gives_empty_plan PASSED     [ 73%]
tests/test_pawpal.py::test_task_that_exactly_fills_time_is_planned PASSED [ 76%]
tests/test_pawpal.py::test_shorter_lower_priority_task_fills_leftover_time PASSED [ 80%]
tests/test_pawpal.py::test_generate_plan_twice_does_not_duplicate PASSED [ 83%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value0] PASSED  [ 86%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value1] PASSED  [ 90%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value2] PASSED  [ 93%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value3] PASSED  [ 96%]
tests/test_pawpal.py::test_failed_edit_leaves_task_unchanged PASSED      [100%]

============================== 30 passed in 0.03s ==============================
```

**Confidence level: ★★★★☆ (4/5)**

All 30 tests pass, and they cover the core scheduling rules plus the edge cases I was most worried about (same-time conflicts, overdue recurring tasks, empty pets, exact time limits). I'm not giving 5 stars because:
- the Streamlit UI in `app.py` was only checked by hand, not with automated tests;
- the tests use the real date (`date.today()`), so I haven't tested things like a run that crosses midnight;
- the greedy planner is easy to explain but doesn't always fit the most tasks possible.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_priority()`, `Scheduler.sort_by_time()` | Planning picks high priority first (shorter task wins a tie). Display uses clock order via a `sorted()` lambda key on zero-padded `"HH:MM"` strings; untimed tasks go last. |
| Filtering | `Scheduler.filter_tasks(pet_name, completed)`, `Scheduler.generate_plan()` | Filter by pet, completion status, or both. The plan only uses unfinished tasks due today and skips any that don't fit in the owner's remaining minutes. |
| Conflict handling | `Scheduler.find_conflicts()` | Sorts timed tasks by start, then flags any task that starts before an earlier one ends (same pet or different pets). Returns warning messages instead of raising errors; nothing is moved automatically. |
| Recurring tasks | `Pet.complete_task()`, `Task.next_occurrence()` | Completing a `daily` or `weekly` task adds a new copy due `+1` or `+7` days (via `timedelta`). `once` tasks don't repeat. |

Run `python main.py` to see each feature in action. Tasks are added out of order, filtered by pet and status, a daily task repeats when completed, and overlapping tasks produce warnings.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
