"""Seed a roster of clinic doctors into clinic.json.

This preserves any existing services, appointments, and staff while restoring
the clinic's specialist roster and visit fees used by the appointments and
clinic pages.
"""

import sys
from pathlib import Path

from pawpal_system import Clinic, Doctor

CLINIC_PATH = "clinic.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Single source of truth for the clinic's doctor roster.
DOCTOR_ROSTER = [
    ("Ava", "Patel", "general", "General Practice", "Primary Care", "DVM", 85.0),
    ("Noah", "Kim", "surgery", "Surgery", "Soft Tissue Surgery", "DVM, DACVS", 145.0),
    ("Mia", "Johnson", "dent", "Dentistry", "Oral Health", "DVM", 110.0),
    ("Lucas", "Garcia", "derm", "Dermatology", "Dermatology", "DVM", 100.0),
    ("Zoe", "Martinez", "exotics", "Exotics", "Exotic Animal Medicine", "DVM", 120.0),
    ("Ethan", "Brown", "urgent", "Emergency", "Urgent Care", "DVM", 130.0),
    ("Nora", "Davis", "cardio", "Cardiology", "Cardiology", "DVM, DACVIM", 150.0),
    ("Levi", "Wilson", "ortho", "Orthopedics", "Orthopedic Surgery", "DVM", 135.0),
]


def seed_doctors():
    """Replace the clinic's doctor roster, preserving all other clinic records."""
    if Path(CLINIC_PATH).exists():
        clinic = Clinic.load_from_json(CLINIC_PATH)
    else:
        clinic = Clinic()

    clinic.doctors = []
    for first_name, last_name, username, department, specialization, education, fee in DOCTOR_ROSTER:
        clinic.doctors.append(
            Doctor(
                first_name=first_name,
                last_name=last_name,
                username=username,
                department_name=department,
                specialization=specialization,
                education=education,
                visit_fee=fee,
                active=True,
            )
        )

    clinic.save_to_json(CLINIC_PATH)
    print(f"Doctors seeded: {len(clinic.doctors)} records restored.")


if __name__ == "__main__":
    seed_doctors()
