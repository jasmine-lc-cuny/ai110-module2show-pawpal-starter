from datetime import date, timedelta

from pawpal_system import (
    Owner,
    Pet,
    Scheduler,
    Task,
    format_time_12h,
    pet_species_icon,
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
    pet = Pet("Mochi", "dog", age=4)
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
    assert loaded_pet.tasks[0].title == "Morning walk"
    assert loaded_pet.tasks[0].frequency == "daily"
    assert loaded_pet.tasks[0].due_date == pet.tasks[0].due_date
