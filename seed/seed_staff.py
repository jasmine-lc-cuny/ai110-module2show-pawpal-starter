"""Seed the clinic's service team: random staff assigned to each bookable service.

Loads the existing clinic.json (so doctors, services, and appointments are kept
untouched), replaces the staff roster with a freshly generated one, and saves.
Sections and their staff counts mirror the "Book a Service" menu.
"""

import random
import sys
from pathlib import Path

from pawpal_system import Clinic, Staff

CLINIC_PATH = "clinic.json"
STAFF_PER_SECTION = 3  # bump this to grow every team at once

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Job titles offered per service section (first entry reads as the "lead").
SECTION_ROLES = {
    "Grooming": ["Senior Groomer", "Pet Groomer", "Bather & Brusher", "Grooming Assistant"],
    "Sitting": ["Lead Pet Sitter", "Overnight Sitter", "Day Sitter", "Drop-In Sitter"],
    "Training": ["Head Trainer", "Puppy Trainer", "Behavior Specialist", "Obedience Coach"],
    "Walking": ["Lead Dog Walker", "Dog Walker", "Pack Walker", "Adventure Walker"],
    "Dog Cafes": ["Cafe Host", "Pup Barista", "Cafe Server", "Kitchen Lead"],
}

# Per-session rate range ($) that feels right for each section.
SECTION_RATES = {
    "Grooming": (35, 75),
    "Sitting": (25, 60),
    "Training": (40, 90),
    "Walking": (15, 35),
    "Dog Cafes": (20, 45),
}

FIRST_NAMES = [
    "Maya", "Diego", "Priya", "Marcus", "Chloe", "Andre", "Sofia", "Tyler", "Nadia", "Omar",
    "Grace", "Leon", "Yuki", "Hassan", "Bianca", "Cody", "Amara", "Ravi", "Elena", "Jamal",
    "Freya", "Malik", "Ingrid", "Theo", "Rosa", "Kai", "Simone", "Dmitri", "Layla", "Beau",
]
LAST_NAMES = [
    "Reyes", "Okafor", "Sato", "Delgado", "Novak", "Bishop", "Farah", "Castillo", "Petrov", "Nguyen",
    "Abara", "Vance", "Mercer", "Solberg", "Rhodes", "Kaur", "Lindqvist", "Osei", "Bautista", "Flynn",
    "Haddad", "Cross", "Ferreira", "Ito", "Bello", "Whitlock", "Amari", "Kovac", "Salas", "Drummond",
]


def _unique_username(first, last, used):
    """Build a short login-style username, disambiguating collisions with a number."""
    base = f"{first[0]}{last}".lower().replace(" ", "")
    username, n = base, 1
    while username in used:
        n += 1
        username = f"{base}{n}"
    used.add(username)
    return username


def generate_staff():
    """Build STAFF_PER_SECTION staff members for every service section."""
    first_pool = FIRST_NAMES.copy()
    last_pool = LAST_NAMES.copy()
    random.shuffle(first_pool)
    random.shuffle(last_pool)

    staff = []
    used_usernames = set()
    i = 0
    for section, roles in SECTION_ROLES.items():
        low, high = SECTION_RATES[section]
        for slot in range(STAFF_PER_SECTION):
            first = first_pool[i % len(first_pool)]
            last = last_pool[i % len(last_pool)]
            i += 1
            username = _unique_username(first, last, used_usernames)
            # First staffer in each section gets the "lead" role (first listed).
            role = roles[0] if slot == 0 else random.choice(roles[1:])
            staff.append(
                Staff(
                    first_name=first,
                    last_name=last,
                    username=username,
                    section=section,
                    role=role,
                    phone=f"(555) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                    email=f"{username}@pawpalplus.com",
                    rate=float(random.randint(low, high)),
                    active=random.random() < 0.9,  # ~10% marked inactive for realism
                )
            )
    return staff


def seed_staff():
    """Replace the clinic's staff roster, preserving all other clinic records."""
    if Path(CLINIC_PATH).exists():
        clinic = Clinic.load_from_json(CLINIC_PATH)
    else:
        clinic = Clinic()

    clinic.staff = generate_staff()
    clinic.save_to_json(CLINIC_PATH)

    per_section = ", ".join(
        f"{section}: {len(clinic.staff_in_section(section))}" for section in SECTION_ROLES
    )
    print(f"👥 Staffed the clinic with {len(clinic.staff)} team members — {per_section}.")


if __name__ == "__main__":
    seed_staff()
