from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion_marks_status():
    task = Task("Feed breakfast", "07:30", 10)

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")

    pet.add_task(Task("Morning walk", "08:00", 30))

    assert len(pet.tasks) == 1


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
    assert "08:00" in warnings[0]
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
