from datetime import date, timedelta

from pawpal_system import (
    Appointment,
    Clinic,
    Doctor,
    Document,
    Owner,
    Pet,
    Scheduler,
    Service,
    Staff,
    Task,
    find_owner,
    format_time_12h,
    pet_species_icon,
    priority_icon,
    task_type_icon,
)


def test_task_type_icon_varies_by_task_title():
    assert task_type_icon("Morning walk") == "🐕"
    assert task_type_icon("Heartworm medication") == "💊"
    assert task_type_icon("Breakfast") == "🍖"
    assert task_type_icon("Brush coat") == "🪮"
    assert task_type_icon("Wash") == "🧼"
    assert task_type_icon("Hair Cut") == "✂️"
    assert task_type_icon("Trim Nails") == "💅"
    assert task_type_icon("Ear Cleaning") == "👂"
    assert task_type_icon("Teeth Brushing") == "🦷"
    assert task_type_icon("Vet checkup") == "🏥"
    assert task_type_icon("Something unrelated") == "🐾"


def test_task_type_icon_heartworm_does_not_false_match_ear_substring():
    # "heartworm" contains the substring "ear" — medication must be checked
    # before the ear-care category or this would wrongly return the ear icon.
    assert task_type_icon("Heartworm Prevention") == "💊"


def test_pet_species_icon_varies_by_species():
    assert pet_species_icon("dog") == "🐕"
    assert pet_species_icon("cat") == "🐈"
    assert pet_species_icon("bunny") == "🐰"
    assert pet_species_icon("Dog") == "🐕"
    assert pet_species_icon("other") == "🐾"
    assert pet_species_icon("iguana") == "🐾"


def test_priority_icon_varies_by_level():
    assert priority_icon("high") == "🔴"
    assert priority_icon("medium") == "🟡"
    assert priority_icon("low") == "🟢"
    assert priority_icon("HIGH") == "🔴"
    assert priority_icon("unknown") == "⚪"


def test_format_time_12h_converts_24_hour_edge_cases():
    assert format_time_12h("00:00") == "12:00 AM"
    assert format_time_12h("07:30") == "7:30 AM"
    assert format_time_12h("12:00") == "12:00 PM"
    assert format_time_12h("13:05") == "1:05 PM"
    assert format_time_12h("23:59") == "11:59 PM"


def test_sort_by_time_still_uses_24_hour_storage_for_correct_ordering():
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Lunch", "12:00", 10))
    pet.add_task(Task("Breakfast", "07:30", 10))
    owner.add_pet(pet)

    sorted_tasks = Scheduler(owner).sort_by_time()

    assert [task.title for _, task in sorted_tasks] == ["Breakfast", "Lunch"]


def test_task_completion_marks_status():
    task = Task("Feed breakfast", "07:30", 10)

    task.mark_complete()

    assert task.completed is True


def test_task_mark_incomplete_reopens_a_done_task():
    task = Task("Feed breakfast", "07:30", 10, completed=True)

    task.mark_incomplete()

    assert task.completed is False


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")

    pet.add_task(Task("Morning walk", "08:00", 30))

    assert len(pet.tasks) == 1


def test_remove_task_deletes_the_correct_task_among_duplicates():
    pet = Pet("Mochi", "dog")
    walk = Task("Morning walk", "08:00", 30, priority="high")
    duplicate_walk = Task("Morning walk", "08:00", 30, priority="low")
    pet.add_task(walk)
    pet.add_task(duplicate_walk)

    removed = pet.remove_task(duplicate_walk)

    assert removed is True
    assert pet.tasks == [walk]


def test_remove_task_returns_false_when_task_not_found():
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "08:00", 30))

    assert pet.remove_task(Task("Ghost task", "00:00", 1)) is False


def test_remove_pet_deletes_the_correct_pet_among_similarly_named_ones():
    owner = Owner("Jordan")
    luna = Pet("Luna", "cat", age=2)
    luna.add_task(Task("Breakfast", "07:30", 10))
    duplicate_luna = Pet("luna", "cat", age=1)
    owner.add_pet(luna)
    owner.add_pet(duplicate_luna)

    removed = owner.remove_pet(duplicate_luna)

    assert removed is True
    assert owner.pets == [luna]


def test_remove_pet_returns_false_when_pet_not_found():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))

    assert owner.remove_pet(Pet("Ghost", "dog")) is False


def test_scheduler_sorts_tasks_by_time():
    owner = Owner("Jordan")
    pet = Pet("Luna", "cat")
    pet.add_task(Task("Dinner", "18:00", 10))
    pet.add_task(Task("Breakfast", "07:30", 10))
    owner.add_pet(pet)

    sorted_tasks = Scheduler(owner).sort_by_time()

    assert [task.title for _, task in sorted_tasks] == ["Breakfast", "Dinner"]


def test_filter_tasks_by_pet_and_status():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    completed = Task("Medication", "12:00", 5, completed=True)
    open_task = Task("Brush coat", "08:00", 15)
    mochi.add_task(completed)
    luna.add_task(open_task)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    filtered = Scheduler(owner).filter_tasks(pet_name="Luna", completed=False)

    assert filtered == [(luna, open_task)]


def test_sort_by_time_handles_pet_with_no_tasks():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))

    assert Scheduler(owner).sort_by_time() == []


def test_filter_tasks_returns_empty_list_when_pet_name_has_no_match():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Morning walk", "08:00", 30))
    owner.add_pet(pet)

    filtered = Scheduler(owner).filter_tasks(pet_name="Nonexistent")

    assert filtered == []


def test_daily_recurrence_creates_tomorrows_task():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Morning walk", "08:00", 30, frequency="daily")
    pet.add_task(task)
    owner.add_pet(pet)

    completed = Scheduler(owner).mark_task_complete("Mochi", "Morning walk")

    assert completed is task
    assert task.completed is True
    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == date.today() + timedelta(days=1)
    assert pet.tasks[1].completed is False


def test_weekly_recurrence_on_time_uses_original_cadence():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    task = Task("Grooming", "10:00", 20, frequency="weekly")
    pet.add_task(task)
    owner.add_pet(pet)

    Scheduler(owner).mark_task_complete("Mochi", "Grooming", completed_on=date.today())

    assert pet.tasks[1].due_date == date.today() + timedelta(weeks=1)


def test_weekly_recurrence_skips_ahead_when_completed_late():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    three_weeks_ago = date.today() - timedelta(weeks=3)
    task = Task("Grooming", "10:00", 20, frequency="weekly", due_date=three_weeks_ago)
    pet.add_task(task)
    owner.add_pet(pet)

    completed = Scheduler(owner).mark_task_complete(
        "Mochi", "Grooming", completed_on=date.today()
    )

    assert completed is task
    next_task = pet.tasks[1]
    # Naively adding 7 days to a 3-week-old due date would still land in the
    # past; the fix should skip forward to the next date after "today".
    assert next_task.due_date > date.today()
    assert next_task.due_date == three_weeks_ago + timedelta(weeks=4)


def test_conflict_detection_flags_duplicate_times():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    luna = Pet("Luna", "cat")
    mochi.add_task(Task("Morning walk", "08:00", 30))
    luna.add_task(Task("Brush coat", "08:00", 15))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "8:00 AM" in warnings[0]
    assert "Mochi: Morning walk" in warnings[0]
    assert "Luna: Brush coat" in warnings[0]


def test_next_urgent_task_picks_highest_priority_then_earliest_time():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "09:00", 30, priority="low"))
    pet.add_task(Task("Medication", "12:00", 5, priority="high"))
    pet.add_task(Task("Breakfast", "07:00", 10, priority="high"))
    owner.add_pet(pet)

    urgent = Scheduler(owner).next_urgent_task()

    assert urgent is not None
    assert urgent[1].title == "Breakfast"


def test_next_urgent_task_returns_none_when_no_open_tasks_today():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))

    assert Scheduler(owner).next_urgent_task() is None


def test_top_priorities_returns_top_n_ranked_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "09:00", 30, priority="low"))
    pet.add_task(Task("Medication", "12:00", 5, priority="high"))
    pet.add_task(Task("Breakfast", "07:00", 10, priority="high"))
    pet.add_task(Task("Brush", "08:00", 15, priority="medium"))
    owner.add_pet(pet)

    top_two = Scheduler(owner).top_priorities(2)

    assert [task.title for _, task in top_two] == ["Breakfast", "Medication"]


def test_save_and_load_json_round_trip(tmp_path):
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", age=4, sex="Male")
    pet.add_task(
        Task("Morning walk", "08:00", 30, priority="high", frequency="daily")
    )
    owner.add_pet(pet)

    json_path = tmp_path / "data.json"
    owner.save_to_json(str(json_path))
    loaded = Owner.load_from_json(str(json_path))

    assert loaded.name == "Jordan"
    assert len(loaded.pets) == 1
    loaded_pet = loaded.pets[0]
    assert loaded_pet.name == "Mochi"
    assert loaded_pet.age == 4
    assert loaded_pet.sex == "Male"
    assert loaded_pet.tasks[0].title == "Morning walk"
    assert loaded_pet.tasks[0].frequency == "daily"
    assert loaded_pet.tasks[0].due_date == pet.tasks[0].due_date


def test_pet_from_dict_defaults_sex_to_none_for_old_data_without_it():
    # Backward compatibility: data.json files saved before the "sex" field
    # was added won't have that key at all.
    old_style_data = {"name": "Mochi", "species": "dog", "age": 4, "tasks": []}

    pet = Pet.from_dict(old_style_data)

    assert pet.sex is None


def test_document_to_dict_and_from_dict_round_trip():
    document = Document(
        category="Digital radiography",
        filename="chest.png",
        path="uploads/mochi/chest.png",
        uploaded_at=date(2026, 1, 15),
    )

    loaded = Document.from_dict(document.to_dict())

    assert loaded == document


def test_pet_round_trips_all_new_fields_including_documents():
    pet = Pet(
        "Mochi",
        "dog",
        age=4,
        sex="Male",
        weight="12 kg",
        diet_good=["Chicken", "Rice"],
        diet_bad=["Chocolate"],
        chronic_conditions=["Arthritis: joint pain in cold weather"],
        documents=[
            Document("Lab diagnostics", "bloodwork.pdf", "uploads/mochi/bloodwork.pdf")
        ],
    )

    loaded = Pet.from_dict(pet.to_dict())

    assert loaded == pet


def test_pet_from_dict_defaults_new_fields_for_old_data_without_them():
    # Same backward-compatibility need as the "sex" test above, but for the
    # dashboard fields added later — old data.json entries won't have these
    # keys at all.
    old_style_data = {"name": "Mochi", "species": "dog", "age": 4, "tasks": []}

    pet = Pet.from_dict(old_style_data)

    assert pet.weight is None
    assert pet.diet_good == []
    assert pet.diet_bad == []
    assert pet.chronic_conditions == []
    assert pet.documents == []


def test_task_notes_round_trips_through_to_dict_and_from_dict():
    task = Task("Vet checkup", "10:00", 30, notes="Eats poorly, sleeps a lot")

    loaded = Task.from_dict(task.to_dict())

    assert loaded.notes == "Eats poorly, sleeps a lot"


def test_task_from_dict_defaults_notes_to_none_for_old_data_without_it():
    old_style_data = {
        "title": "Vet checkup",
        "time": "10:00",
        "duration_minutes": 30,
        "priority": "medium",
        "frequency": "once",
        "due_date": date.today().isoformat(),
        "completed": False,
    }

    task = Task.from_dict(old_style_data)

    assert task.notes is None


def test_completion_rate_returns_zero_with_no_tasks():
    owner = Owner("Jordan")
    owner.add_pet(Pet("Mochi", "dog"))

    assert Scheduler(owner).completion_rate() == 0.0


def test_completion_rate_computes_percentage_of_completed_tasks():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    pet.add_task(Task("Walk", "08:00", 30, completed=True))
    pet.add_task(Task("Medication", "12:00", 5, completed=True))
    pet.add_task(Task("Brush", "18:00", 15, completed=False))
    pet.add_task(Task("Bath", "19:00", 20, completed=False))
    owner.add_pet(pet)

    assert Scheduler(owner).completion_rate() == 50.0


def test_completion_rate_filters_by_pet_name():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "dog")
    mochi.add_task(Task("Walk", "08:00", 30, completed=True))
    luna = Pet("Luna", "cat")
    luna.add_task(Task("Brush", "08:00", 15, completed=False))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    assert Scheduler(owner).completion_rate(pet_name="Mochi") == 100.0
    assert Scheduler(owner).completion_rate(pet_name="Luna") == 0.0


def test_upcoming_tasks_returns_next_n_open_tasks_sorted_by_date_then_time():
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog")
    today = date.today()
    pet.add_task(Task("Past task", "08:00", 10, due_date=today - timedelta(days=1)))
    pet.add_task(Task("Later today", "18:00", 10, due_date=today))
    pet.add_task(Task("Earlier today", "07:00", 10, due_date=today))
    pet.add_task(Task("Tomorrow", "09:00", 10, due_date=today + timedelta(days=1)))
    pet.add_task(Task("Next week", "09:00", 10, due_date=today + timedelta(weeks=1)))
    owner.add_pet(pet)

    upcoming = Scheduler(owner).upcoming_tasks(n=3)

    assert [task.title for _, task in upcoming] == [
        "Earlier today",
        "Later today",
        "Tomorrow",
    ]


def test_owner_round_trips_new_contact_fields():
    owner = Owner("Jasmine", phone="555-1234", email="jasmine@example.com", address="1 Main St")

    loaded = Owner.from_dict(owner.to_dict())

    assert loaded == owner


def test_owner_from_dict_defaults_contact_fields_to_none_for_old_data_without_them():
    old_style_data = {"name": "Jordan", "pets": []}

    owner = Owner.from_dict(old_style_data)

    assert owner.phone is None
    assert owner.email is None
    assert owner.address is None


def test_pet_round_trips_blood_type_field():
    pet = Pet("Mochi", "dog", blood_type="DEA 1.1 positive")

    loaded = Pet.from_dict(pet.to_dict())

    assert loaded.blood_type == "DEA 1.1 positive"


def test_pet_from_dict_defaults_blood_type_to_none_for_old_data_without_it():
    old_style_data = {"name": "Mochi", "species": "dog", "age": 4, "tasks": []}

    pet = Pet.from_dict(old_style_data)

    assert pet.blood_type is None


def test_pet_round_trips_profile_fields():
    pet = Pet(
        "Mochi",
        "dog",
        breed="Labrador Retriever",
        height="24 in",
        color_markings="Golden with white chest patch",
        microchip_number="985121000000001",
        spayed_neutered="Yes",
        allergies="Chicken",
        behavioral_notes="Friendly with strangers",
        status="Alive",
    )

    loaded = Pet.from_dict(pet.to_dict())

    assert loaded == pet


def test_pet_from_dict_defaults_profile_fields_for_old_data_without_them():
    old_style_data = {"name": "Mochi", "species": "dog", "age": 4, "tasks": []}

    pet = Pet.from_dict(old_style_data)

    assert pet.breed is None
    assert pet.height is None
    assert pet.color_markings is None
    assert pet.microchip_number is None
    assert pet.spayed_neutered is None
    assert pet.allergies is None
    assert pet.behavioral_notes is None
    assert pet.status == "Alive"


def test_find_owner_matches_case_insensitively():
    owners = [Owner("Jasmine"), Owner("John")]

    assert find_owner(owners, "john") is owners[1]


def test_find_owner_returns_none_when_not_found():
    owners = [Owner("Jasmine")]

    assert find_owner(owners, "Nonexistent") is None


def test_doctor_to_dict_and_from_dict_round_trip():
    doctor = Doctor(
        first_name="Jane",
        last_name="Roe",
        username="jroe",
        password="hunter2",
        email="jroe@example.com",
        phone="555-0000",
        department_name="General",
        specialization="Surgery",
        education="DVM",
        visit_fee=75.0,
        active=True,
    )

    loaded = Doctor.from_dict(doctor.to_dict())

    assert loaded == doctor
    assert loaded.full_name == "Dr. Jane Roe"


def test_service_to_dict_and_from_dict_round_trip():
    service = Service("Blood Test", 20.0)

    loaded = Service.from_dict(service.to_dict())

    assert loaded == service


def test_appointment_to_dict_and_from_dict_round_trip():
    appointment = Appointment(
        owner_name="Jasmine",
        pet_name="Garfield",
        doctor_username="jroe",
        date=date(2026, 1, 15),
        time="10:00",
        reason="Annual checkup",
        status="Confirmed",
    )

    loaded = Appointment.from_dict(appointment.to_dict())

    assert loaded == appointment


def test_clinic_save_and_load_json_round_trip(tmp_path):
    clinic = Clinic(
        doctors=[Doctor("Jane", "Roe", "jroe", visit_fee=75.0)],
        services=[Service("Blood Test", 20.0)],
        appointments=[
            Appointment("Jasmine", "Garfield", "jroe", date(2026, 1, 15), "10:00")
        ],
    )

    json_path = tmp_path / "clinic.json"
    clinic.save_to_json(str(json_path))
    loaded = Clinic.load_from_json(str(json_path))

    assert loaded.doctors == clinic.doctors
    assert loaded.services == clinic.services
    assert loaded.appointments == clinic.appointments


def test_clinic_find_doctor_matches_case_insensitively():
    doctor = Doctor("Jane", "Roe", "jroe")
    clinic = Clinic(doctors=[doctor])

    assert clinic.find_doctor("JROE") is doctor


def test_clinic_find_doctor_returns_none_when_not_found():
    clinic = Clinic()

    assert clinic.find_doctor("nobody") is None


def test_clinic_income_sums_visit_fee_for_completed_appointments_only():
    cheap_doctor = Doctor("Jane", "Roe", "jroe", visit_fee=50.0)
    pricey_doctor = Doctor("Sam", "Lee", "slee", visit_fee=100.0)
    clinic = Clinic(
        doctors=[cheap_doctor, pricey_doctor],
        appointments=[
            Appointment("Jasmine", "Garfield", "jroe", date.today(), "10:00", status="Completed"),
            Appointment("Jasmine", "Heathcliff", "slee", date.today(), "11:00", status="Completed"),
            Appointment("John", "Rex", "jroe", date.today(), "12:00", status="Pending"),
        ],
    )

    assert clinic.income() == 150.0


def test_clinic_income_skips_appointment_whose_doctor_was_deleted():
    clinic = Clinic(
        doctors=[],
        appointments=[
            Appointment("Jasmine", "Garfield", "ghost", date.today(), "10:00", status="Completed"),
        ],
    )

    assert clinic.income() == 0.0


def test_task_round_trips_assignee_and_category():
    task = Task("Wash / Bath", "09:00", 30, assignee="Maya Reyes", category="grooming")

    loaded = Task.from_dict(task.to_dict())

    assert loaded.assignee == "Maya Reyes"
    assert loaded.category == "grooming"


def test_task_from_dict_defaults_assignee_and_category_for_old_data():
    old_style_data = {
        "title": "Morning Walk",
        "time": "08:00",
        "duration_minutes": 20,
        "priority": "medium",
        "frequency": "once",
        "due_date": date.today().isoformat(),
        "completed": False,
    }

    task = Task.from_dict(old_style_data)

    assert task.assignee is None
    assert task.category is None


def test_recurring_task_carries_over_assignee_and_category():
    task = Task(
        "Overnight Sitting", "20:00", 60, frequency="daily",
        assignee="Diego Okafor", category="sitting",
    )

    next_task = task.next_occurrence(completed_on=date.today())

    assert next_task.assignee == "Diego Okafor"
    assert next_task.category == "sitting"


def test_staff_to_dict_and_from_dict_round_trip():
    member = Staff(
        first_name="Maya",
        last_name="Reyes",
        username="mreyes",
        section="Grooming",
        role="Senior Groomer",
        phone="(555) 123-4567",
        email="mreyes@pawpalplus.com",
        rate=55.0,
        active=True,
    )

    loaded = Staff.from_dict(member.to_dict())

    assert loaded == member
    assert loaded.full_name == "Maya Reyes"


def test_clinic_staff_in_section_filters_by_section():
    groomer = Staff("Maya", "Reyes", "mreyes", section="Grooming")
    walker = Staff("Diego", "Okafor", "dokafor", section="Walking")
    clinic = Clinic(staff=[groomer, walker])

    assert clinic.staff_in_section("Grooming") == [groomer]
    assert clinic.staff_in_section("Walking") == [walker]
    assert clinic.staff_in_section("Sitting") == []


def test_clinic_round_trips_staff(tmp_path):
    clinic = Clinic(staff=[Staff("Maya", "Reyes", "mreyes", section="Grooming", rate=55.0)])

    json_path = tmp_path / "clinic.json"
    clinic.save_to_json(str(json_path))
    loaded = Clinic.load_from_json(str(json_path))

    assert loaded.staff == clinic.staff
