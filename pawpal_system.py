"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta

# Allowed priorities and their sort order (higher means more important).
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}

# Allowed values for how often a task repeats.
FREQUENCIES = ("once", "daily", "weekly")

# How many days until a repeating task comes back ("once" tasks don't repeat).
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


@dataclass
class Task:
    """A single pet care activity, like a walk or a feeding."""

    title: str
    duration_minutes: int
    priority: str  # one of the keys in PRIORITY_RANKS
    time: str = ""  # optional preferred time as "HH:MM"
    frequency: str = "daily"  # one of FREQUENCIES
    completed: bool = False
    pet_name: str = ""  # set by Pet.add_task()
    due_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        """Check the task's values as soon as it is created."""
        self._validate()

    def _validate(self) -> None:
        """Normalize priority and raise ValueError for any invalid field."""
        self.priority = self.priority.strip().lower()
        if self.priority not in PRIORITY_RANKS:
            raise ValueError(
                f"priority must be one of {list(PRIORITY_RANKS)}, got {self.priority!r}"
            )
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than 0")
        if self.frequency not in FREQUENCIES:
            raise ValueError(
                f"frequency must be one of {list(FREQUENCIES)}, got {self.frequency!r}"
            )
        if self.time:
            try:
                parsed = datetime.strptime(self.time.strip(), "%H:%M")
            except ValueError:
                raise ValueError(f"time must look like 'HH:MM', got {self.time!r}") from None
            self.time = parsed.strftime("%H:%M")  # "8:00" -> "08:00" so text sorting works

    def priority_rank(self) -> int:
        """Return a number for sorting (higher means more important)."""
        return PRIORITY_RANKS[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def start_minutes(self) -> int | None:
        """Return the start time as minutes after midnight, or None if the task has no time."""
        if not self.time:
            return None
        hours, minutes = map(int, self.time.split(":"))
        return hours * 60 + minutes

    def next_occurrence(self) -> Task | None:
        """Return a fresh copy due on the next repeat day, or None for one-time tasks.

        The next date is counted from today (or the due date, if later) with timedelta:
        +1 day for "daily", +7 days for "weekly".
        """
        days = RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        start = max(self.due_date, date.today())
        return replace(self, completed=False, due_date=start + timedelta(days=days))

    def summary(self) -> str:
        """Return a one-line description like 'Walk (Mochi) - 30 min [priority: high]'."""
        return (
            f"{self.title} ({self.pet_name}) - "
            f"{self.duration_minutes} min [priority: {self.priority}]"
        )


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and set the task's pet_name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title."""
        self.tasks.remove(self._find_task(title))

    def edit_task(self, title: str, duration_minutes: int, priority: str) -> None:
        """Update the duration and priority of an existing task."""
        task = self._find_task(title)
        old_duration, old_priority = task.duration_minutes, task.priority
        task.duration_minutes, task.priority = duration_minutes, priority
        try:
            task._validate()
        except ValueError:
            task.duration_minutes, task.priority = old_duration, old_priority
            raise

    def complete_task(self, title: str) -> Task | None:
        """Mark a task done and, if it repeats, add and return its next occurrence.

        The finished task stays in the list as history; the new copy starts unfinished.
        """
        task = self._find_task(title)
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)
        return next_task

    def _find_task(self, title: str) -> Task:
        """Return the task with this title (unfinished first), or raise ValueError."""
        matches = [task for task in self.tasks if task.title == title]
        if not matches:
            raise ValueError(f"{self.name} has no task named {title!r}")
        return next((task for task in matches if not task.completed), matches[0])


@dataclass
class Owner:
    """A pet owner, their daily time budget, and their pets."""

    name: str
    available_minutes: int
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Make sure the time budget is not negative."""
        if self.available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner (pet names must be unique)."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"{self.name} already has a pet named {pet.name!r}")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        for pet in self.pets:
            if pet.name == pet_name:
                self.pets.remove(pet)
                return
        raise ValueError(f"{self.name} has no pet named {pet_name!r}")

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Builds a daily plan from an owner's tasks and available time."""

    def __init__(self, owner: Owner) -> None:
        """Store the owner to plan for and start with empty results."""
        self.owner = owner
        self.planned_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.conflicts: list[str] = []

    def generate_plan(self) -> list[Task]:
        """Plan the highest-priority unfinished tasks due today that fit the owner's time.

        Greedy: tasks are tried in priority order and kept if they fit in the minutes
        left; the rest go to skipped_tasks. Conflicts are checked on the final plan.
        """
        self.planned_tasks = []
        self.skipped_tasks = []
        minutes_left = self.owner.available_minutes

        today = date.today()
        pending = [task for task in self.filter_tasks(completed=False) if task.due_date <= today]
        for task in self.sort_by_priority(pending):
            if task.duration_minutes <= minutes_left:
                self.planned_tasks.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)
        self.conflicts = self.find_conflicts(self.planned_tasks)
        return list(self.planned_tasks)

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Return the owner's tasks that match every filter given (None means any).

        Example: filter_tasks(pet_name="Luna", completed=False) -> Luna's unfinished tasks.
        """
        return [
            task
            for task in self.owner.get_all_tasks()
            if (pet_name is None or task.pet_name == pet_name)
            and (completed is None or task.completed == completed)
        ]

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority (shorter first on ties)."""
        return sorted(tasks, key=lambda task: (-task.priority_rank(), task.duration_minutes))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks in clock order, with untimed tasks at the end.

        Times are stored zero-padded ("08:00"), so comparing the strings gives clock
        order. The key (task.time == "", task.time) puts tasks without a time last.
        """
        return sorted(tasks, key=lambda task: (task.time == "", task.time))

    def find_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning for each pair of timed tasks whose time ranges overlap.

        Sorts by start time, then compares each task with the ones after it until one
        starts after it ends. Back-to-back tasks (08:00 end, 08:00 start) don't count.
        Returns messages instead of raising, so the plan still works.
        """
        timed = self.sort_by_time([task for task in tasks if task.time])
        warnings = []
        for i, earlier in enumerate(timed):
            earlier_end = earlier.start_minutes() + earlier.duration_minutes
            for later in timed[i + 1:]:
                if later.start_minutes() >= earlier_end:
                    break  # sorted by start, so no later task can overlap `earlier`
                warnings.append(
                    f"{earlier.title} ({earlier.pet_name}) at {earlier.time} overlaps "
                    f"{later.title} ({later.pet_name}) at {later.time}"
                )
        return warnings

    def explain_plan(self) -> str:
        """Describe why tasks were chosen, and which were skipped."""
        if not self.planned_tasks and not self.skipped_tasks:
            return "No tasks planned. Add some tasks, then generate a plan."

        used = sum(task.duration_minutes for task in self.planned_tasks)
        lines = [
            f"Plan for {self.owner.name} "
            f"({used} of {self.owner.available_minutes} minutes used):"
        ]
        for number, task in enumerate(self.planned_tasks, start=1):
            lines.append(f"  {number}. {task.summary()}")
        if self.skipped_tasks:
            lines.append("Skipped (not enough time left):")
            lines.extend(f"  - {task.summary()}" for task in self.skipped_tasks)
        if self.conflicts:
            lines.append("Time conflicts (one person can't do both):")
            lines.extend(f"  - {warning}" for warning in self.conflicts)
        lines.append(
            "Why: high-priority tasks go first. On a tie, the shorter task goes first "
            "so more tasks fit."
        )
        return "\n".join(lines)
