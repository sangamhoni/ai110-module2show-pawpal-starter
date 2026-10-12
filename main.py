"""Demo script: build a sample owner, pets, and tasks, then print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler) -> None:
    """Print the planned tasks as a table in time order, then any skipped tasks."""
    plan = scheduler.sort_by_time(scheduler.planned_tasks)
    used = sum(task.duration_minutes for task in plan)

    print("=" * 50)
    print(f"  Today's Schedule for {scheduler.owner.name}")
    print("=" * 50)
    print(f"  {'Time':<7}{'Task':<16}{'Pet':<8}{'Min':>4}  Priority")
    print("  " + "-" * 46)
    for task in plan:
        print(
            f"  {task.time or '--:--':<7}{task.title:<16}{task.pet_name:<8}"
            f"{task.duration_minutes:>4}  {task.priority}"
        )
    print("  " + "-" * 46)
    print(f"  {used} of {scheduler.owner.available_minutes} minutes used")

    if scheduler.skipped_tasks:
        print("\n  Skipped (not enough time):")
        for task in scheduler.skipped_tasks:
            print(
                f"    - {task.title} ({task.pet_name}, "
                f"{task.duration_minutes} min, {task.priority})"
            )

    if scheduler.conflicts:
        print("\n  Time conflicts (one person can't do both):")
        for warning in scheduler.conflicts:
            print(f"    - {warning}")


def print_tasks(heading: str, tasks: list[Task]) -> None:
    """Print a heading and one line per task with its time, pet, status, and due date."""
    print(f"\n{heading}")
    for task in tasks:
        status = "done" if task.completed else "todo"
        print(f"  {task.time or '--:--'}  {task.title:<15}{task.pet_name:<7}{status}  due {task.due_date}")


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # Added out of order on purpose so sort_by_time() has something to fix.
    mochi.add_task(Task("Evening walk", 30, "medium", time="18:00"))
    mochi.add_task(Task("Breakfast", 10, "high", time="8:00"))
    mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
    luna.add_task(Task("Brushing", 20, "low", time="19:00", frequency="weekly"))
    luna.add_task(Task("Litter box", 10, "medium", time="12:00"))
    luna.add_task(Task("Medication", 5, "high", time="07:45"))

    # Two tasks at the same time as existing ones, so find_conflicts() has something to catch.
    mochi.add_task(Task("Flea medicine", 5, "high", time="07:30"))  # same pet as Morning walk
    luna.add_task(Task("Breakfast", 5, "high", time="08:00"))  # different pet from Mochi's Breakfast

    next_litter = luna.complete_task("Litter box")
    print(f"Completed 'Litter box' -> next one due {next_litter.due_date}")

    scheduler = Scheduler(owner)
    print_tasks("All tasks (order added):", owner.get_all_tasks())
    print_tasks("Sorted by time:", scheduler.sort_by_time(owner.get_all_tasks()))
    print_tasks("Mochi's tasks:", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Mochi")))
    print_tasks("Completed tasks:", scheduler.filter_tasks(completed=True))
    print_tasks(
        "Luna's unfinished tasks:",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Luna", completed=False)),
    )

    scheduler.generate_plan()
    print()
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
