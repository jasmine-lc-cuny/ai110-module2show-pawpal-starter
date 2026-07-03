"""Seed a realistic spread of tasks and vet appointments across existing pets.

Populates the schedule layer so every view has something to show:
- Today's Schedule (varied tasks due today)
- Each Book-a-Service section (grooming, walking, sitting, training, dog cafes)
- Calendar (tasks spread across the next few weeks)
- Doctors / Appointments (vet appointments, mirrored as tasks like the UI does)
- Conflict detection (a couple of deliberate double-bookings)

Service tasks are assigned to staff from that section; vet appointments are
assigned to a doctor and mirrored onto the pet as a "veterinary" task, exactly
like booking through the Appointments page. Re-runnable: it rebuilds the
schedule layer from scratch (pet profiles are untouched).
"""

import random
import sys
from datetime import date, timedelta

from pawpal_system import (
    Appointment,
    Clinic,
    Owner,
    Scheduler,
    Task,
    load_owners_from_json,
    save_owners_to_json,
)

DATA_PATH = "data.json"
CLINIC_PATH = "clinic.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# The "today" the seeded schedule is anchored to, so the "due today" batch and
# its deliberate conflicts land on a specific demo date instead of whatever
# day happens to run this script. Set to None to use the real date.today().
ANCHOR_DATE = date(2026, 7, 6)

random.seed(2026)  # reproducible demo dataset


def time_slots(start_hour, end_hour):
    """Return every 15-minute "HH:MM" slot in [start_hour, end_hour)."""
    return [f"{h:02d}:{m}" for h in range(start_hour, end_hour) for m in ("00", "15", "30", "45")]


def seed_schedules():
    owners = load_owners_from_json(DATA_PATH)
    clinic = Clinic.load_from_json(CLINIC_PATH)

    # Rebuild only the schedule layer; leave pet profiles alone.
    for owner in owners:
        for pet in owner.pets:
            pet.tasks = []
    clinic.appointments = []

    pairs = [(owner, pet) for owner in owners for pet in owner.pets]
    dogs_cats = [(o, p) for o, p in pairs if p.species in ("dog", "cat")]
    dogs = [(o, p) for o, p in pairs if p.species == "dog"]
    bookable_doctors = [d for d in clinic.doctors if d.active] or clinic.doctors

    def staff_name(section):
        team = [s for s in clinic.staff_in_section(section) if s.active]
        return random.choice(team).full_name if team else None

    def add(pet, title, time, category, due, *, freq="once", priority="medium",
            duration=30, assignee=None, notes=None, completed=False):
        pet.add_task(Task(
            title=title, time=time, duration_minutes=duration, priority=priority,
            frequency=freq, due_date=due, completed=completed, notes=notes,
            assignee=assignee, category=category,
        ))

    def book_vet(owner, pet, title, time, due, status, reason=None):
        """Create an Appointment AND its mirrored 'veterinary' task, as the UI does."""
        doctor = random.choice(bookable_doctors)
        clinic.appointments.append(Appointment(
            owner_name=owner.name, pet_name=pet.name, doctor_username=doctor.username,
            date=due, time=time, reason=reason or title, status=status,
        ))
        add(pet, title, time, "veterinary", due, priority="high",
            assignee=doctor.full_name, notes=reason or title, completed=(status == "Completed"))

    today = ANCHOR_DATE or date.today()

    # --- TODAY: give each task a unique slot so the only conflicts are the
    #     deliberate ones below. 09:00 and 14:00 are reserved for those. ---
    today_slots = time_slots(6, 20)
    for reserved in ("09:00", "14:00"):
        today_slots.remove(reserved)
    random.shuffle(today_slots)

    for owner, pet in random.sample(dogs_cats, min(18, len(dogs_cats))):
        if random.random() < 0.5:
            add(pet, random.choice(["Morning Walk", "Afternoon Walk", "Evening Walk", "Playtime"]),
                today_slots.pop(), "walking", today, freq="daily",
                priority=random.choice(["high", "medium"]), assignee=staff_name("Walking"))
        else:
            add(pet, random.choice(["Breakfast", "Lunch", "Dinner"]),
                today_slots.pop(), "special_services", today, freq="daily",
                assignee=staff_name("Dog Cafes"))

    for owner, pet in random.sample(dogs_cats, min(4, len(dogs_cats))):
        add(pet, random.choice(["Wash / Bath", "Trim Nails", "Brush Coat"]),
            today_slots.pop(), "grooming", today, assignee=staff_name("Grooming"))

    for owner, pet in random.sample(pairs, min(5, len(pairs))):
        book_vet(owner, pet, random.choice(["Vet Appointment", "Blood Work", "X-Ray"]),
                 today_slots.pop(), today, random.choice(["Pending", "Confirmed", "Completed"]))

    # --- DELIBERATE CONFLICTS (today), to demonstrate conflict detection ---
    # Same pet double-booked at 09:00 (a walk and a vet visit):
    o1, p1 = dogs_cats[0]
    add(p1, "Morning Walk", "09:00", "walking", today, priority="high", assignee=staff_name("Walking"))
    book_vet(o1, p1, "Vet Appointment", "09:00", today, "Confirmed", reason="Annual checkup")
    # Two different pets booked at 14:00:
    o2, p2 = dogs_cats[1]
    o3, p3 = dogs_cats[2]
    add(p2, "Wash / Bath", "14:00", "grooming", today, assignee=staff_name("Grooming"))
    add(p3, "Obedience Training", "14:00", "training", today, assignee=staff_name("Training"))

    # --- UPCOMING: spread across the next 3 weeks (calendar + each section) ---
    upcoming = [today + timedelta(days=n) for n in range(1, 22)]

    def add_spread(section, category, titles, count, pool, freq="once", priority="medium"):
        for _ in range(count):
            _, pet = random.choice(pool)
            add(pet, random.choice(titles), random.choice(time_slots(8, 18)),
                category, random.choice(upcoming), freq=freq, priority=priority,
                assignee=staff_name(section))

    add_spread("Grooming", "grooming",
               ["Wash / Bath", "Hair Cut", "Trim Nails", "Ear Cleaning", "Teeth Brushing", "Brush Coat"], 12, dogs_cats)
    add_spread("Training", "training",
               ["Obedience Training", "Puppy Class", "Leash Training", "Trick Training"], 8, dogs)
    add_spread("Sitting", "sitting",
               ["Day Sitting", "Overnight Sitting", "Drop-In Visit", "House Sitting"], 8, pairs)
    add_spread("Walking", "walking",
               ["Morning Walk", "Afternoon Walk", "Evening Walk", "Playtime"], 10, dogs_cats, freq="weekly")
    add_spread("Dog Cafes", "special_services", ["Breakfast", "Lunch", "Dinner"], 6, dogs)

    for _ in range(12):
        owner, pet = random.choice(pairs)
        book_vet(owner, pet,
                 random.choice(["Vet Appointment", "Injection Vaccine", "Surgery", "Blood Work", "Give Medication"]),
                 random.choice(time_slots(9, 17)), random.choice(upcoming),
                 random.choice(["Pending", "Confirmed"]))

    save_owners_to_json(owners, DATA_PATH)
    clinic.save_to_json(CLINIC_PATH)

    # Report what got seeded, using the same combined-owner view the app uses.
    combined = Owner("All", pets=[p for o in owners for p in o.pets])
    scheduler = Scheduler(combined)
    total = len(combined.all_tasks())
    due_today = len([1 for _, t in combined.all_tasks() if t.due_date == today])
    conflicts = scheduler.detect_conflicts()
    by_cat = {}
    for _, t in combined.all_tasks():
        by_cat[t.category] = by_cat.get(t.category, 0) + 1

    print(f"📅 Seeded {total} tasks ({due_today} due today) and {len(clinic.appointments)} appointments.")
    print(f"   By section: {by_cat}")
    print(f"   Conflicts detected: {len(conflicts)}")
    for warning in conflicts[:5]:
        print(f"     ⚠️  {warning}")


if __name__ == "__main__":
    seed_schedules()
