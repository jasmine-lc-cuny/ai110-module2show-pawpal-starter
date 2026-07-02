# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit pet care management app that helps an owner track pets,
schedule daily care tasks, spot conflicts, and keep recurring routines moving.
The system is built CLI-first: the backend classes in `pawpal_system.py` are
verified through `main.py` and pytest before being connected to the UI in
`app.py`.

## Features

- Add an owner, pets, and scheduled care tasks.
- Track task time, duration, priority, frequency, due date, and completion.
- View schedules sorted by time or by priority.
- Filter tasks by pet and completion status.
- Detect exact date/time conflicts and show warnings.
- Mark tasks complete and automatically create the next daily or weekly task.
- Use a Streamlit interface backed by `st.session_state` so pets and tasks stay available during the browser session.

## Setup

```bash
pip install -r requirements.txt
```

Run the CLI demo:

```bash
python main.py
```

Run the Streamlit app:

```bash
python -m streamlit run app.py
```

## Sample Output

Example output from running `python main.py`:

```text
PawPal+ schedule for Jordan
================================
📅 Today's Schedule
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-01, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-01, ⏳ open)
  08:00 - Luna: Brush coat (15 min, medium, once, 2026-07-01, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-01, ⏳ open)

High Priority First
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-01, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-01, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-01, ⏳ open)
  08:00 - Luna: Brush coat (15 min, medium, once, 2026-07-01, ⏳ open)

🚨 Next Urgent Task
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-01, ⏳ open)

⭐ Today's Top 3 Priorities
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-01, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-01, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-01, ⏳ open)

⚠️ Conflict Warnings
  Conflict on 2026-07-01 at 08:00: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
```

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically using `HH:MM` strings. |
| Priority sorting | `Scheduler.sort_by_priority_then_time()` | Sorts high priority first, then by time. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings for exact same date/time matches. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Creates the next daily or weekly task after completion. |

## Testing PawPal+

Run the full test suite:

```bash
python -m pytest
```

The tests cover task completion, task addition, chronological sorting,
filtering, daily recurrence, and conflict detection.

```text
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.0, pluggy-1.6.0
rootdir: D:\codex\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 6 items

tests\test_pawpal.py ......                                              [100%]

============================== 6 passed in 0.03s ==============================
```

Confidence Level: 4/5 stars. The main happy paths and required scheduling
algorithms are tested, but a production system would need deeper validation for
time zones, overlapping durations, and saved data across app restarts.

## Demo Walkthrough

1. The user enters their owner name in the sidebar.
2. The user adds pets such as Mochi the dog and Luna the cat.
3. The user schedules care tasks with a time, duration, priority, and frequency.
4. PawPal+ displays the schedule as a table sorted by time or priority.
5. The user filters tasks by pet/status and sees conflict warnings when two open tasks share the same date and time.
6. When the user marks a daily or weekly task complete, PawPal+ creates the next occurrence automatically.

## Architecture

- Draft UML: `diagrams/uml.mmd`
- Final UML: `diagrams/uml_final.mmd`
- Backend logic: `pawpal_system.py`
- CLI verification: `main.py`
- Streamlit UI: `app.py`
- Tests: `tests/test_pawpal.py`
