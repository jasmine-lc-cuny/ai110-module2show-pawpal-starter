"""Seed random appointments into the current PawPal pets and clinic."""

from __future__ import annotations

import random
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path

from pawpal_system import Appointment, Clinic, Doctor, Task, load_owners_from_json, save_owners_to_json

DATA_PATH = Path("data.json")
CLINIC_PATH = Path("clinic.json")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


DOCTOR_FALLBACKS = [
    Doctor("Ava", "Patel", "general", department_name="General Practice", specialization="Primary Care", education="DVM", visit_fee=85.0),
    Doctor("Noah", "Kim", "surgery", department_name="Surgery", specialization="Soft Tissue Surgery", education="DVM, DACVS", visit_fee=145.0),
    Doctor("Nora", "Davis", "cardio", department_name="Cardiology", specialization="Cardiology", education="DVM, DACVIM", visit_fee=150.0),
]

REASONS_BY_SPECIES = {
    "dog": ["Annual exam", "Vaccination follow-up", "Ear infection check", "Dental cleaning consult"],
    "cat": ["Annual exam", "Vaccination follow-up", "Weight check", "Dental consult"],
    "rabbit": ["Nail trim consult", "Digestive health check", "New patient exam"],
}

STATUS_OPTIONS = ["Pending", "Confirmed", "Completed"]

TASK_TEMPLATES = [
    ("Morning Walk", "walking", 30, "high", "daily"),
    ("Brush Coat", "grooming", 20, "medium", "once"),
    ("Breakfast", "special_services", 15, "medium", "daily"),
    ("Vet Appointment", "veterinary", 30, "high", "once"),
]

DOG_SERVICE_CATEGORIES = {"walking", "grooming", "training", "special_services"}
CAT_SERVICE_CATEGORIES = {"grooming", "sitting"}


def _round_up_to_quarter(moment: datetime) -> datetime:
    minutes = (moment.minute // 15 + 1) * 15
    if minutes == 60:
        return moment.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return moment.replace(minute=minutes, second=0, microsecond=0)


def _ensure_doctors(clinic: Clinic) -> None:
    if clinic.doctors:
        return
    clinic.doctors = DOCTOR_FALLBACKS[:]


def _doctor_for_species(clinic: Clinic, species: str) -> Doctor:
    active_doctors = [doctor for doctor in clinic.doctors if doctor.active] or clinic.doctors
    if not active_doctors:
        return DOCTOR_FALLBACKS[0]

    species_key = species.lower()
    preferred = {
        "dog": ("general", "primary"),
        "cat": ("general", "primary"),
        "rabbit": ("internal", "exotic"),
    }.get(species_key)

    if preferred:
        for doctor in active_doctors:
            haystack = f"{doctor.department_name} {doctor.specialization} {doctor.username}".lower()
            if any(token in haystack for token in preferred):
                return doctor

    return random.choice(active_doctors)


def _seed_service_tasks(owners, anchor: datetime, *, species: str, categories: set[str]) -> int:
    seeded = 0
    for owner_index, owner in enumerate(owners):
        for pet_index, pet in enumerate(owner.pets):
            if pet.species.lower() != species:
                continue

            pet.tasks = []
            available_templates = [tpl for tpl in TASK_TEMPLATES if tpl[1] in categories]
            for task_offset in range(2):
                title, category, duration, priority, frequency = available_templates[
                    (owner_index + pet_index + task_offset) % len(available_templates)
                ]
                due_date = anchor.date() + timedelta(days=(owner_index + pet_index + task_offset) % 2)
                time_str = (
                    anchor
                    + timedelta(minutes=10 + owner_index * 6 + pet_index * 9 + task_offset * 13)
                ).strftime("%H:%M")
                pet.add_task(
                    Task(
                        title=title,
                        time=time_str,
                        duration_minutes=duration,
                        priority=priority,
                        frequency=frequency,
                        due_date=due_date,
                        category=category,
                        notes=f"Seeded task near {anchor.strftime('%I:%M %p').lstrip('0')}",
                    )
                )
                seeded += 1
    return seeded


def _seed_vet_appointments(owners, clinic: Clinic, anchor: datetime) -> list[tuple[str, str, str, datetime, str, str, str]]:
    clinic.appointments = []
    all_pets = [pet for owner in owners for pet in owner.pets]
    if not all_pets:
        return []

    rows = []
    for index, pet in enumerate(random.sample(all_pets, min(len(all_pets), 18))):
        owner = next(owner for owner in owners if pet in owner.pets)
        doctor = _doctor_for_species(clinic, pet.species)
        due_date = anchor.date() + timedelta(days=index % 3)
        time_str = (anchor + timedelta(minutes=20 + index * 17)).strftime("%H:%M")
        reason = random.choice(REASONS_BY_SPECIES.get(pet.species.lower(), ["General wellness check", "Follow-up visit"]))
        status = random.choice(STATUS_OPTIONS)

        clinic.appointments.append(
            Appointment(
                owner_name=owner.name,
                pet_name=pet.name,
                doctor_username=doctor.username,
                date=due_date,
                time=time_str,
                reason=reason,
                status=status,
            )
        )
        rows.append((owner.name, pet.name, doctor.full_name, due_date, time_str, status, reason))
    return rows


def seed_random_appointments(mode: str = "all") -> None:
    """Seed either dog services, cat services, vet appointments, or all of them."""
    now = datetime.now()
    anchor = _round_up_to_quarter(now)

    owners = load_owners_from_json(str(DATA_PATH)) if DATA_PATH.exists() else []
    clinic = Clinic.load_from_json(str(CLINIC_PATH)) if CLINIC_PATH.exists() else Clinic()

    _ensure_doctors(clinic)

    if not owners:
        print("No owners found in data.json. Run the animal/client seed first.")
        return

    random.seed(anchor.toordinal())

    appointment_rows = []
    service_task_count = 0

    if mode in {"all", "dogs"}:
        service_task_count += _seed_service_tasks(owners, anchor, species="dog", categories=DOG_SERVICE_CATEGORIES)
    if mode in {"all", "cats"}:
        service_task_count += _seed_service_tasks(owners, anchor, species="cat", categories=CAT_SERVICE_CATEGORIES)

    if mode in {"all", "vet"}:
        appointment_rows = _seed_vet_appointments(owners, clinic, anchor)

    save_owners_to_json(owners, str(DATA_PATH))
    clinic.save_to_json(str(CLINIC_PATH))

    if service_task_count:
        print(f"🐾 Seeded {service_task_count} service tasks for mode '{mode}'.")
    if appointment_rows:
        print(f"📅 Seeded {len(appointment_rows)} random appointments into clinic.json")
        for owner_name, pet_name, doctor_name, due_date, time_str, status, reason in appointment_rows[:10]:
            print(f"   {due_date.isoformat()} {time_str} - {owner_name} / {pet_name} with {doctor_name} [{status}] ({reason})")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed PawPal demo services and appointments.")
    parser.add_argument(
        "mode",
        nargs="?",
        default="all",
        choices=["all", "dogs", "cats", "vet"],
        help="What to seed: all, dog services, cat services, or vet appointments.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    seed_random_appointments(args.mode)
