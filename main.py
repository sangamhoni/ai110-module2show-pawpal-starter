"""Demo script: build a sample owner, pets, and tasks, then print today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(scheduler: Scheduler) -> None:
    """Print the planned tasks as a table in time order, then any skipped tasks."""
    plan = sorted(scheduler.planned_tasks, key=lambda task: task.time or "99:99")
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


def main() -> None:
    owner = Owner("Jordan", available_minutes=90)
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    mochi.add_task(Task("Morning walk", 30, "high", time="07:30"))
    mochi.add_task(Task("Breakfast", 10, "high", time="08:00"))
    mochi.add_task(Task("Evening walk", 30, "medium", time="18:00"))
    luna.add_task(Task("Medication", 5, "high", time="09:00"))
    luna.add_task(Task("Litter box", 10, "medium", time="12:00"))
    luna.add_task(Task("Brushing", 20, "low", time="19:00", frequency="weekly"))

    scheduler = Scheduler(owner)
    scheduler.generate_plan()
    print_schedule(scheduler)


if __name__ == "__main__":
    main()
