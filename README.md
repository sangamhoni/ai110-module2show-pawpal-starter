# 🐾 PawPal+ (Module 2 Project)

PawPal+ is a Streamlit app that helps a busy pet owner plan a day of pet care. You enter your pets and their care tasks, and PawPal+ builds a daily plan that fits your available time, puts the most important tasks first, warns you about overlapping times, and brings repeating tasks back automatically.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## ✨ Features

- **Priority-based daily plan:** `Scheduler.generate_plan()` fills your available minutes with the most important unfinished tasks due today: high before medium before low, and the shorter task first on a tie. If a long task doesn't fit, it keeps going and fits shorter tasks into the leftover time.
- **Sorting by time:** `Scheduler.sort_by_time()` shows tasks in clock order. Times are stored as zero-padded `"HH:MM"` (so `"8:00"` becomes `"08:00"`), and tasks without a time go last.
- **Filtering by pet and status:** `Scheduler.filter_tasks(pet_name, completed)` shows one pet's tasks, only unfinished or finished tasks, or both.
- **Daily and weekly recurrence:** `Pet.complete_task()` marks a task done and, using `Task.next_occurrence()`, adds the next copy due tomorrow (daily) or in 7 days (weekly), calculated with `timedelta`. One-time tasks just complete.
- **Conflict warnings:** `Scheduler.find_conflicts()` checks the full time range of each planned task and warns when two overlap, for the same pet or different pets. It shows warnings instead of crashing, and never moves tasks on its own.
- **Plan explanation:** `Scheduler.explain_plan()` lists what was planned, what was skipped for lack of time, any conflicts, and why tasks were ordered that way.
- **Input validation:** bad priorities, durations, times or frequencies are rejected with a clear message. Priority is case-insensitive (`"High"` works).
- **Data that survives clicks:** the app keeps your owner, pets and tasks in `st.session_state` while the browser tab is open.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run it

```bash
streamlit run app.py   # the interactive app
python main.py         # terminal demo of every scheduling feature
```

### Project structure

| File | What it is |
|------|------------|
| `pawpal_system.py` | Logic layer: `Owner`, `Pet`, `Task`, `Scheduler` |
| `app.py` | Streamlit UI |
| `main.py` | Terminal demo script |
| `tests/test_pawpal.py` | 32 automated tests |
| `diagrams/uml_final.mmd` | Final UML class diagram (Mermaid) |

## 🖥️ Sample Output

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

**What the tests cover** (32 tests in `tests/test_pawpal.py`):

- **Sorting:** tasks come back in clock order (including `"9:15"` vs `"12:00"`), untimed tasks go last, and priority ties go to the shorter task.
- **Recurring tasks:** completing a daily task creates a new one due tomorrow (weekly: +7 days). An overdue task's next copy is due tomorrow, not in the past. `once` tasks don't repeat.
- **Conflict detection:** tasks at the exact same time are flagged (same pet or different pets), as are partial overlaps and a long task overlapping a later, non-adjacent one. Back-to-back tasks, untimed tasks, and skipped tasks are not flagged.
- **Planning:** only unfinished tasks due today are planned. A task that exactly fills the remaining time fits, and a shorter low-priority task can still fill leftover time. A pet with no tasks gives an empty plan, and running the plan twice doesn't duplicate it.
- **Validation:** a blank title or bad priority, duration, time, or frequency raises `ValueError`, and a failed edit leaves the task unchanged.

Output of `python -m pytest -v`:

```
tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  3%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [  6%]
tests/test_pawpal.py::test_time_is_zero_padded_and_sorts_correctly PASSED [  9%]
tests/test_pawpal.py::test_filter_by_pet_returns_only_that_pets_tasks PASSED [ 12%]
tests/test_pawpal.py::test_completing_daily_task_creates_one_due_tomorrow PASSED [ 15%]
tests/test_pawpal.py::test_completing_once_task_does_not_repeat PASSED   [ 18%]
tests/test_pawpal.py::test_task_due_tomorrow_is_not_planned_today PASSED [ 21%]
tests/test_pawpal.py::test_overlapping_tasks_are_reported_as_conflict PASSED [ 25%]
tests/test_pawpal.py::test_back_to_back_tasks_are_not_a_conflict PASSED  [ 28%]
tests/test_pawpal.py::test_same_time_same_pet_is_a_conflict PASSED       [ 31%]
tests/test_pawpal.py::test_completing_weekly_task_creates_one_due_in_seven_days PASSED [ 34%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 37%]
tests/test_pawpal.py::test_sort_by_time_puts_untimed_tasks_last PASSED   [ 40%]
tests/test_pawpal.py::test_sort_by_priority_breaks_ties_with_shorter_task PASSED [ 43%]
tests/test_pawpal.py::test_overdue_daily_task_next_copy_is_due_tomorrow PASSED [ 46%]
tests/test_pawpal.py::test_completing_same_title_twice_targets_the_new_copy PASSED [ 50%]
tests/test_pawpal.py::test_completed_daily_task_leaves_nothing_due_today PASSED [ 53%]
tests/test_pawpal.py::test_complete_exact_task_when_titles_repeat PASSED [ 56%]
tests/test_pawpal.py::test_exact_same_time_different_pets_is_a_conflict PASSED [ 59%]
tests/test_pawpal.py::test_long_task_conflicts_with_non_adjacent_later_task PASSED [ 62%]
tests/test_pawpal.py::test_untimed_tasks_never_conflict PASSED           [ 65%]
tests/test_pawpal.py::test_skipped_task_is_not_reported_as_conflict PASSED [ 68%]
tests/test_pawpal.py::test_pet_with_no_tasks_gives_empty_plan PASSED     [ 71%]
tests/test_pawpal.py::test_task_that_exactly_fills_time_is_planned PASSED [ 75%]
tests/test_pawpal.py::test_shorter_lower_priority_task_fills_leftover_time PASSED [ 78%]
tests/test_pawpal.py::test_generate_plan_twice_does_not_duplicate PASSED [ 81%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value0] PASSED  [ 84%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value1] PASSED  [ 87%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value2] PASSED  [ 90%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value3] PASSED  [ 93%]
tests/test_pawpal.py::test_invalid_task_values_raise[bad_value4] PASSED  [ 96%]
tests/test_pawpal.py::test_failed_edit_leaves_task_unchanged PASSED      [100%]

============================== 32 passed in 0.03s ==============================
```

**Confidence level: ★★★★☆ (4/5)**

All 32 tests pass, and they cover the core scheduling rules plus the edge cases I was most worried about (same-time conflicts, overdue recurring tasks, empty pets, exact time limits). I'm not giving 5 stars because:
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

### What you can do in the app

| Section | Actions |
|---------|---------|
| **Owner** | Set your name and how many minutes you have for pet care today |
| **Pets** | Add pets (name + species); duplicate names are rejected |
| **Tasks** | Add a task for a pet: title, duration, priority, optional time (`HH:MM`), and how often it repeats |
| **Mark a task done** | Pick an unfinished task and complete it; daily/weekly tasks come back automatically |
| **All tasks** | See every task sorted by time, filtered by pet and by status (To do / Done / All) |
| **Build Schedule** | Generate today's plan: summary numbers, conflict warnings, the schedule table, skipped tasks, and a "Why this plan?" explanation |

### Example workflow

1. Run `streamlit run app.py`. Enter **Jordan** as the owner and set **60** minutes available today.
2. Add two pets: **Mochi** (dog) and **Luna** (cat). They appear in the Pets table.
3. Add four tasks, deliberately out of order:
   - Mochi: Evening walk, 18:00, 30 min, medium
   - Mochi: Morning walk, 07:30, 30 min, high
   - Luna: Medication, 07:45, 5 min, high
   - Luna: Litter box, 12:00, 10 min, medium

   The **All tasks** table shows them in clock order: 07:30, 07:45, 12:00, 18:00.
4. Set **Show pet** to **Luna**. Only Medication and Litter box appear ("Showing 2 of 4 tasks, sorted by time").
5. Under **Mark a task done**, pick Luna's Litter box and click **Mark done**. A green message says it repeats daily and shows the next due date (e.g. "next one is due Mon Oct 12"). Set **Status** to **Done** to see it, or **To do** to see tomorrow's copy.
6. Click **Generate schedule**:
   - The summary shows **2 tasks planned · 35 / 60 minutes used · 1 skipped**.
   - A yellow warning says Morning walk (Mochi) at 07:30 overlaps Medication (Luna) at 07:45, and suggests moving one or doing them back-to-back.
   - The schedule table lists Morning walk and Medication in time order.
   - Evening walk is listed as skipped: only 25 minutes were left.
   - **Why this plan?** expands to the full explanation.

### Scheduler behaviors shown

- **Priority planning:** high-priority tasks were picked first, and the plan stopped adding tasks when the 60 minutes ran out.
- **Sorting:** tasks entered out of order are shown in clock order.
- **Filtering:** by pet and by done/to-do status.
- **Recurrence:** completing a daily task created tomorrow's copy, which isn't planned today.
- **Conflict warnings:** overlapping times are flagged without blocking the plan.

### CLI demo (`python main.py`)

The terminal demo runs the same logic with more tasks, including two at the exact same time. The full output is in [Sample Output](#️-sample-output). Here's the schedule part:

```
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

**Screenshot** *(optional)*: <!-- add a screenshot of the Build Schedule section here -->
