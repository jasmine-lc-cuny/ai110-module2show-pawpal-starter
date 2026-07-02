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
    (("medic", "med", "pill", "heartworm", "vaccine", "dose", "injection"), "💊"),
    (("feed", "breakfast", "lunch", "dinner", "meal", "snack"), "🍖"),
    (("ear",), "👂"),
    (("tooth", "teeth", "dental"), "🦷"),
    (("nail", "trim"), "💅"),
    (("haircut", "hair cut", "cut"), "✂️"),
    (("wash", "bath"), "🧼"),
    (("brush", "comb", "groom"), "🪮"),
    (("vet", "appointment", "checkup", "exam", "surgery", "x-ray", "blood"), "🏥"),
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
    notes: str | None = None

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
            "notes": self.notes,
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
            notes=data.get("notes"),
        )


@dataclass
class Document:
    """Represent one uploaded file (x-ray, lab result, etc.) attached to a pet."""

    category: str
    filename: str
    path: str
    uploaded_at: date = field(default_factory=date.today)

    def to_dict(self) -> dict:
        """Convert this document to a JSON-serializable dictionary."""
        return {
            "category": self.category,
            "filename": self.filename,
            "path": self.path,
            "uploaded_at": self.uploaded_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Document:
        """Rebuild a Document from a dictionary produced by to_dict()."""
        return cls(
            category=data["category"],
            filename=data["filename"],
            path=data["path"],
            uploaded_at=date.fromisoformat(data["uploaded_at"]),
        )


@dataclass
class Pet:
    """Store pet details and assigned care tasks."""

    name: str
    species: str
    age: int | None = None
    sex: str | None = None
    tasks: list[Task] = field(default_factory=list)
    weight: str | None = None
    diet_good: list[str] = field(default_factory=list)
    diet_bad: list[str] = field(default_factory=list)
    chronic_conditions: list[str] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    blood_type: str | None = None
    breed: str | None = None
    height: str | None = None
    color_markings: str | None = None
    microchip_number: str | None = None
    spayed_neutered: str | None = None
    allergies: str | None = None
    behavioral_notes: str | None = None
    status: str = "Alive"

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
            "weight": self.weight,
            "diet_good": self.diet_good,
            "diet_bad": self.diet_bad,
            "chronic_conditions": self.chronic_conditions,
            "documents": [document.to_dict() for document in self.documents],
            "blood_type": self.blood_type,
            "breed": self.breed,
            "height": self.height,
            "color_markings": self.color_markings,
            "microchip_number": self.microchip_number,
            "spayed_neutered": self.spayed_neutered,
            "allergies": self.allergies,
            "behavioral_notes": self.behavioral_notes,
            "status": self.status,
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
            weight=data.get("weight"),
            diet_good=data.get("diet_good", []),
            diet_bad=data.get("diet_bad", []),
            chronic_conditions=data.get("chronic_conditions", []),
            documents=[
                Document.from_dict(document_data)
                for document_data in data.get("documents", [])
            ],
            blood_type=data.get("blood_type"),
            breed=data.get("breed"),
            height=data.get("height"),
            color_markings=data.get("color_markings"),
            microchip_number=data.get("microchip_number"),
            spayed_neutered=data.get("spayed_neutered"),
            allergies=data.get("allergies"),
            behavioral_notes=data.get("behavioral_notes"),
            status=data.get("status", "Alive"),
        )


@dataclass
class Owner:
    """Manage a pet owner's pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)
    phone: str | None = None
    email: str | None = None
    address: str | None = None

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
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Rebuild an Owner (and their pets/tasks) from a dictionary produced by to_dict()."""
        return cls(
            name=data["name"],
            pets=[Pet.from_dict(pet_data) for pet_data in data["pets"]],
            phone=data.get("phone"),
            email=data.get("email"),
            address=data.get("address"),
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


def find_owner(owners: list[Owner], name: str) -> Owner | None:
    """Return the owner with a matching name, if it exists."""
    for owner in owners:
        if owner.name.lower() == name.lower():
            return owner
    return None


APPOINTMENT_STATUSES = ["Pending", "Confirmed", "Completed", "Cancelled"]


@dataclass
class Doctor:
    """Represent one clinic staff member who can be assigned to appointments."""

    first_name: str
    last_name: str
    username: str
    password: str = ""
    email: str | None = None
    phone: str | None = None
    department_name: str = ""
    specialization: str = ""
    education: str = ""
    visit_fee: float = 0.0
    active: bool = True

    @property
    def full_name(self) -> str:
        """Return the doctor's display name, e.g. 'Dr. Jane Roe'."""
        return f"Dr. {self.first_name} {self.last_name}".strip()

    def to_dict(self) -> dict:
        """Convert this doctor to a JSON-serializable dictionary."""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "password": self.password,
            "email": self.email,
            "phone": self.phone,
            "department_name": self.department_name,
            "specialization": self.specialization,
            "education": self.education,
            "visit_fee": self.visit_fee,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Doctor:
        """Rebuild a Doctor from a dictionary produced by to_dict()."""
        return cls(
            first_name=data["first_name"],
            last_name=data["last_name"],
            username=data["username"],
            password=data.get("password", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            department_name=data.get("department_name", ""),
            specialization=data.get("specialization", ""),
            education=data.get("education", ""),
            visit_fee=data.get("visit_fee", 0.0),
            active=data.get("active", True),
        )


@dataclass
class Service:
    """Represent one billable clinic service (e.g. Blood Test)."""

    name: str
    cost: float = 0.0

    def to_dict(self) -> dict:
        """Convert this service to a JSON-serializable dictionary."""
        return {"name": self.name, "cost": self.cost}

    @classmethod
    def from_dict(cls, data: dict) -> Service:
        """Rebuild a Service from a dictionary produced by to_dict()."""
        return cls(name=data["name"], cost=data.get("cost", 0.0))


@dataclass
class Appointment:
    """Represent one clinic appointment linking a pet to a doctor."""

    owner_name: str
    pet_name: str
    doctor_username: str
    date: date
    time: str
    reason: str = ""
    status: str = "Pending"

    def to_dict(self) -> dict:
        """Convert this appointment to a JSON-serializable dictionary."""
        return {
            "owner_name": self.owner_name,
            "pet_name": self.pet_name,
            "doctor_username": self.doctor_username,
            "date": self.date.isoformat(),
            "time": self.time,
            "reason": self.reason,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Appointment:
        """Rebuild an Appointment from a dictionary produced by to_dict()."""
        return cls(
            owner_name=data["owner_name"],
            pet_name=data["pet_name"],
            doctor_username=data["doctor_username"],
            date=date.fromisoformat(data["date"]),
            time=data["time"],
            reason=data.get("reason", ""),
            status=data.get("status", "Pending"),
        )


class Clinic:
    """Hold clinic-wide records (doctors, services, appointments) shared
    across every owner, independent of any single Owner's pets/tasks."""

    def __init__(
        self,
        doctors: list[Doctor] | None = None,
        services: list[Service] | None = None,
        appointments: list[Appointment] | None = None,
    ):
        """Create a clinic, optionally seeded with existing records."""
        self.doctors = doctors if doctors is not None else []
        self.services = services if services is not None else []
        self.appointments = appointments if appointments is not None else []

    def find_doctor(self, username: str) -> Doctor | None:
        """Return the doctor with a matching username, if it exists."""
        for doctor in self.doctors:
            if doctor.username.lower() == username.lower():
                return doctor
        return None

    def income(self) -> float:
        """Return total income: each Completed appointment's doctor's visit fee."""
        total = 0.0
        for appointment in self.appointments:
            if appointment.status != "Completed":
                continue
            doctor = self.find_doctor(appointment.doctor_username)
            if doctor is not None:
                total += doctor.visit_fee
        return total

    def to_dict(self) -> dict:
        """Convert this clinic's records to a JSON-serializable dictionary."""
        return {
            "doctors": [doctor.to_dict() for doctor in self.doctors],
            "services": [service.to_dict() for service in self.services],
            "appointments": [appointment.to_dict() for appointment in self.appointments],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Clinic:
        """Rebuild a Clinic from a dictionary produced by to_dict()."""
        return cls(
            doctors=[Doctor.from_dict(doctor_data) for doctor_data in data.get("doctors", [])],
            services=[
                Service.from_dict(service_data) for service_data in data.get("services", [])
            ],
            appointments=[
                Appointment.from_dict(appointment_data)
                for appointment_data in data.get("appointments", [])
            ],
        )

    def save_to_json(self, path: str) -> None:
        """Save this clinic's records to a JSON file at path."""
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @classmethod
    def load_from_json(cls, path: str) -> Clinic:
        """Load a clinic's records from a JSON file at path."""
        with open(path, "r", encoding="utf-8") as file:
            return cls.from_dict(json.load(file))


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

    def completion_rate(self, pet_name: str | None = None) -> float:
        """Return the percentage of tasks marked complete, optionally scoped to one pet."""
        task_pairs = self.filter_tasks(pet_name=pet_name)
        if not task_pairs:
            return 0.0
        completed_count = sum(1 for _, task in task_pairs if task.completed)
        return round(completed_count / len(task_pairs) * 100, 1)

    def upcoming_tasks(self, n: int = 5) -> list[tuple[Pet, Task]]:
        """Return the next n open tasks due today or later, soonest first."""
        today = date.today()
        open_upcoming = [
            (pet, task)
            for pet, task in self.owner.all_tasks()
            if task.due_date >= today and not task.completed
        ]
        ranked = sorted(open_upcoming, key=lambda pair: (pair[1].due_date, pair[1].time))
        return ranked[:n]
