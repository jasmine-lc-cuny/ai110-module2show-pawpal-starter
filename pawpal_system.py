from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta


PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# Keyword -> icon lookup used by Task.summary() to show a different emoji per
# task type (walk, medication, feeding, ear care, dental, nail trim, haircut,
# bath, brushing, vet visit), checked in order so more specific keywords win
# — e.g. "medic"/"heartworm" must be checked before "ear" so "Heartworm
# Prevention" doesn't false-match the "ear" substring inside "heartworm".
# Falls back to a generic paw print.
TASK_TYPE_ICONS: list[tuple[tuple[str, ...], str]] = [
    (("walk", "hike", "play", "exercise"), "🐕"),
    (("medic", "med", "pill", "heartworm", "vaccine", "dose"), "💊"),
    (("feed", "breakfast", "lunch", "dinner", "meal", "snack"), "🍖"),
    (("ear",), "👂"),
    (("tooth", "teeth", "dental"), "🦷"),
    (("nail", "trim"), "💅"),
    (("haircut", "hair cut", "cut"), "✂️"),
    (("wash", "bath"), "🧼"),
    (("brush", "comb", "groom"), "🪮"),
    (("vet", "appointment", "checkup", "exam"), "🏥"),
]


def task_type_icon(title: str) -> str:
    """Return an emoji representing the kind of care task a title describes."""
    lowered = title.lower()
    for keywords, icon in TASK_TYPE_ICONS:
        if any(keyword in lowered for keyword in keywords):
            return icon
    return "🐾"


# Species -> avatar emoji, shown next to a pet's name throughout the app.
PET_SPECIES_ICONS = {
    "dog": "🐕",
    "cat": "🐈",
    "bunny": "🐰",
}


def pet_species_icon(species: str) -> str:
    """Return an avatar emoji for a pet's species, or a generic paw print."""
    return PET_SPECIES_ICONS.get(species.lower(), "🐾")


def format_time_12h(time_str: str) -> str:
    """Convert a stored 24-hour "HH:MM" time to a 12-hour "H:MM AM/PM" display string.

    Task.time stays in 24-hour format internally because sort_by_time() relies
    on "HH:MM" strings sorting the same as their chronological order; this is
    purely a display-layer conversion.
    """
    hour, minute = map(int, time_str.split(":"))
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute:02d} {period}"


@dataclass
class Task:
    """Represent one scheduled pet care activity."""

    title: str
    time: str
    duration_minutes: int
    priority: str = "medium"
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    completed: bool = False

    def mark_complete(self):
        """Mark this task as complete."""
        self.completed = True

    def mark_incomplete(self):
        """Reopen this task by marking it not yet complete."""
        self.completed = False

    def next_occurrence(self, completed_on: date | None = None) -> Task | None:
        """Create the next daily/weekly occurrence, skipping past dates a late completion already covers."""
        if self.frequency == "daily":
            step = timedelta(days=1)
        elif self.frequency == "weekly":
            step = timedelta(weeks=1)
        else:
            return None

        anchor = completed_on or self.due_date
        next_date = self.due_date + step
        while next_date <= anchor:
            next_date += step

        return Task(
            title=self.title,
            time=self.time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_date,
        )

    def summary(self, pet_name: str | None = None) -> str:
        """Return a readable one-line description for CLI output."""
        pet_prefix = f"{pet_name}: " if pet_name else ""
        status = "✅ done" if self.completed else "⏳ open"
        icon = task_type_icon(self.title)
        return (
            f"{icon} {format_time_12h(self.time)} - {pet_prefix}{self.title} "
            f"({self.duration_minutes} min, {self.priority}, "
            f"{self.frequency}, {self.due_date.isoformat()}, {status})"
        )

    def to_dict(self) -> dict:
        """Convert this task to a JSON-serializable dictionary."""
        return {
            "title": self.title,
            "time": self.time,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat(),
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Rebuild a Task from a dictionary produced by to_dict()."""
        return cls(
            title=data["title"],
            time=data["time"],
            duration_minutes=data["duration_minutes"],
            priority=data["priority"],
            frequency=data["frequency"],
            due_date=date.fromisoformat(data["due_date"]),
            completed=data["completed"],
        )


@dataclass
class Pet:
    """Store pet details and assigned care tasks."""

    name: str
    species: str
    age: int | None = None
    sex: str | None = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> bool:
        """Remove a task from this pet's list; returns whether it was found."""
        if task in self.tasks:
            self.tasks.remove(task)
            return True
        return False

    def incomplete_tasks(self) -> list[Task]:
        """Return this pet's incomplete tasks."""
        return [task for task in self.tasks if not task.completed]

    def to_dict(self) -> dict:
        """Convert this pet and its tasks to a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "sex": self.sex,
            "tasks": [task.to_dict() for task in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Rebuild a Pet (and its tasks) from a dictionary produced by to_dict()."""
        return cls(
            name=data["name"],
            species=data["species"],
            age=data["age"],
            sex=data.get("sex"),
            tasks=[Task.from_dict(task_data) for task_data in data["tasks"]],
        )


@dataclass
class Owner:
    """Manage a pet owner's pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        self.pets.append(pet)

    def find_pet(self, pet_name: str) -> Pet | None:
        """Return the pet with a matching name, if it exists."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def remove_pet(self, pet: Pet) -> bool:
        """Remove a pet (and all its tasks) from this owner; returns whether it was found."""
        if pet in self.pets:
            self.pets.remove(pet)
            return True
        return False

    def all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return every task paired with the pet it belongs to."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def to_dict(self) -> dict:
        """Convert this owner, their pets, and all tasks to a JSON-serializable dictionary."""
        return {
            "name": self.name,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Rebuild an Owner (and their pets/tasks) from a dictionary produced by to_dict()."""
        return cls(
            name=data["name"],
            pets=[Pet.from_dict(pet_data) for pet_data in data["pets"]],
        )

    def save_to_json(self, path: str) -> None:
        """Save this owner's pets and tasks to a JSON file at path."""
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> Owner:
        """Load an owner's pets and tasks from a JSON file at path."""
        with open(path, "r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))


def save_owners_to_json(owners: list[Owner], path: str) -> None:
    """Persist multiple distinct owners (e.g. different customers, each with
    their own pets/tasks) to one JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump({"owners": [owner.to_dict() for owner in owners]}, file, indent=2)


def load_owners_from_json(path: str) -> list[Owner]:
    """Load multiple owners from a JSON file, migrating an older
    single-owner file (as written by Owner.save_to_json()) into a one-owner
    list if that's what's found."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if "owners" in data:
        return [Owner.from_dict(owner_data) for owner_data in data["owners"]]
    return [Owner.from_dict(data)]


class Scheduler:
    """Organize and manage care tasks across an owner account."""

    def __init__(self, owner: Owner):
        """Create a scheduler for one owner."""
        self.owner = owner

    def sort_by_time(
        self, tasks: list[tuple[Pet, Task]] | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return tasks sorted chronologically by HH:MM time."""
        task_pairs = tasks if tasks is not None else self.owner.all_tasks()
        return sorted(task_pairs, key=lambda pair: pair[1].time)

    def sort_by_priority_then_time(
        self, tasks: list[tuple[Pet, Task]] | None = None
    ) -> list[tuple[Pet, Task]]:
        """Return tasks sorted by priority first, then time."""
        task_pairs = tasks if tasks is not None else self.owner.all_tasks()
        return sorted(
            task_pairs,
            key=lambda pair: (PRIORITY_ORDER.get(pair[1].priority, 99), pair[1].time),
        )

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[tuple[Pet, Task]]:
        """Filter tasks by pet name and completion status."""
        task_pairs = self.owner.all_tasks()

        if pet_name:
            task_pairs = [
                (pet, task)
                for pet, task in task_pairs
                if pet.name.lower() == pet_name.lower()
            ]

        if completed is not None:
            task_pairs = [
                (pet, task)
                for pet, task in task_pairs
                if task.completed is completed
            ]

        return task_pairs

    def detect_conflicts(self, tasks: list[tuple[Pet, Task]] | None = None) -> list[str]:
        """Return warnings for tasks scheduled at the exact same date and time."""
        task_pairs = tasks if tasks is not None else self.owner.all_tasks()
        seen: dict[tuple[date, str], list[str]] = {}

        for pet, task in task_pairs:
            key = (task.due_date, task.time)
            seen.setdefault(key, []).append(f"{pet.name}: {task.title}")

        warnings = []
        for (due_date, time), labels in seen.items():
            if len(labels) > 1:
                joined = ", ".join(labels)
                warnings.append(
                    f"Conflict on {due_date.isoformat()} at {format_time_12h(time)}: {joined}"
                )

        return warnings

    def mark_task_complete(
        self, pet_name: str, task_title: str, completed_on: date | None = None
    ) -> Task | None:
        """Complete a matching task and add its next recurring occurrence."""
        pet = self.owner.find_pet(pet_name)
        if pet is None:
            return None

        for task in pet.tasks:
            if task.title.lower() == task_title.lower() and not task.completed:
                task.mark_complete()
                # Defaults completed_on to today so a late completion skips
                # straight to the next upcoming occurrence instead of one
                # that's already overdue.
                next_task = task.next_occurrence(completed_on=completed_on or date.today())
                if next_task is not None:
                    pet.add_task(next_task)
                return task

        return None

    def todays_schedule(self):
        """Return today's open tasks sorted by time."""
        today = date.today()
        open_today = [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if task.due_date == today and not task.completed
        ]
        return self.sort_by_time(open_today)

    def next_urgent_task(self, tasks: list[tuple[Pet, Task]] | None = None):
        """Return today's single highest-priority, earliest-time open task."""
        task_pairs = tasks if tasks is not None else self.todays_schedule()
        ranked = self.sort_by_priority_then_time(task_pairs)
        return ranked[0] if ranked else None

    def top_priorities(self, n: int = 3, tasks: list[tuple[Pet, Task]] | None = None):
        """Return today's top n open tasks ranked by priority then time."""
        task_pairs = tasks if tasks is not None else self.todays_schedule()
        return self.sort_by_priority_then_time(task_pairs)[:n]
