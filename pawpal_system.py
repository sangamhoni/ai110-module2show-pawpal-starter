"""PawPal+ logic layer: backend classes for owners, pets, tasks, and scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

# Allowed priorities and their sort order (higher means more important).
PRIORITY_RANKS = {"low": 1, "medium": 2, "high": 3}

# Allowed values for how often a task repeats.
FREQUENCIES = ("once", "daily", "weekly")


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
                datetime.strptime(self.time, "%H:%M")
            except ValueError:
                raise ValueError(f"time must look like 'HH:MM', got {self.time!r}") from None

    def priority_rank(self) -> int:
        """Return a number for sorting (higher means more important)."""
        return PRIORITY_RANKS[self.priority]

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


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

    def _find_task(self, title: str) -> Task:
        """Return the first task with this title, or raise ValueError."""
        for task in self.tasks:
            if task.title == title:
                return task
        raise ValueError(f"{self.name} has no task named {title!r}")


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
        self.owner = owner
        self.planned_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def generate_plan(self) -> list[Task]:
        """Choose and order tasks that fit in the owner's available time.

        Clears planned_tasks and skipped_tasks first, and ignores completed tasks.
        """
        self.planned_tasks = []
        self.skipped_tasks = []
        minutes_left = self.owner.available_minutes

        pending = [task for task in self.owner.get_all_tasks() if not task.completed]
        for task in self.sort_by_priority(pending):
            if task.duration_minutes <= minutes_left:
                self.planned_tasks.append(task)
                minutes_left -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)
        return list(self.planned_tasks)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority (shorter first on ties)."""
        return sorted(tasks, key=lambda task: (-task.priority_rank(), task.duration_minutes))

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
            lines.append(
                f"  {number}. {task.title} ({task.pet_name}) - "
                f"{task.duration_minutes} min [priority: {task.priority}]"
            )
        if self.skipped_tasks:
            lines.append("Skipped (not enough time left):")
            for task in self.skipped_tasks:
                lines.append(
                    f"  - {task.title} ({task.pet_name}) - "
                    f"{task.duration_minutes} min [priority: {task.priority}]"
                )
        lines.append(
            "Why: high-priority tasks go first. On a tie, the shorter task goes first "
            "so more tasks fit."
        )
        return "\n".join(lines)
