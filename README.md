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
- Surface today's single next urgent task and a top-3 priority shortlist.
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
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Luna: Brush coat (15 min, medium, once, 2026-07-02, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-02, ⏳ open)

High Priority First
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-02, ⏳ open)
  08:00 - Luna: Brush coat (15 min, medium, once, 2026-07-02, ⏳ open)

🚨 Next Urgent Task
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)

⭐ Today's Top 3 Priorities
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-02, ⏳ open)

⚠️ Conflict Warnings
  Conflict on 2026-07-02 at 08:00: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-03, ⏳ open)
```

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically using `HH:MM` strings. |
| Priority sorting | `Scheduler.sort_by_priority_then_time()` | Sorts high priority first, then by time. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings for exact same date/time matches. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | Creates the next daily or weekly task after completion. |
| Next urgent task | `Scheduler.next_urgent_task()` | Returns today's single highest-priority, earliest-time open task (or `None`). |
| Top priorities | `Scheduler.top_priorities(n=3)` | Returns today's top `n` open tasks ranked by priority then time. |

## Testing PawPal+

Run the full test suite:

```bash
python -m pytest
```

The tests cover task completion, task addition, chronological sorting,
filtering, daily recurrence, conflict detection, next-urgent-task selection,
and top-priority ranking.

```text
============================= test session starts ==============================
platform linux -- Python 3.12.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 9 items

tests/test_pawpal.py .........                                           [100%]

============================== 9 passed in 0.02s ===============================
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

Sample CLI output from `python main.py` (same run shown in the Sample Output section above):

```text
PawPal+ schedule for Jordan
================================
📅 Today's Schedule
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Luna: Brush coat (15 min, medium, once, 2026-07-02, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-02, ⏳ open)

High Priority First
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-02, ⏳ open)
  08:00 - Luna: Brush coat (15 min, medium, once, 2026-07-02, ⏳ open)

🚨 Next Urgent Task
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)

⭐ Today's Top 3 Priorities
  07:30 - Luna: Breakfast (10 min, high, daily, 2026-07-02, ⏳ open)
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-02, ⏳ open)
  12:00 - Mochi: Heartworm medication (5 min, high, once, 2026-07-02, ⏳ open)

⚠️ Conflict Warnings
  Conflict on 2026-07-02 at 08:00: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created
  08:00 - Mochi: Morning walk (30 min, high, daily, 2026-07-03, ⏳ open)
```

## Optional Challenges

| Challenge | Status | Notes |
|---|---|---|
| 1. Advanced algorithmic capability | ✅ Done | `Scheduler.next_urgent_task()` and `Scheduler.top_priorities(n)` add a distinct ranking capability beyond the four base requirements. See the "Agent Workflow" section in `ai_interactions.md`. |
| 2. Data persistence (JSON) | ❌ Not attempted | No `save_to_json`/`load_from_json`; data only lives for the process/session lifetime. |
| 3. Advanced priority scheduling | ✅ Done | `Task.priority` (`low`/`medium`/`high`) plus `Scheduler.sort_by_priority_then_time()`; see "High Priority First" in the Sample Output above. |
| 4. Professional UI/output formatting | ✅ Done | `Task.summary()` uses ✅/⏳ status icons and `main.py` section headers use emoji (📅 🚨 ⭐ ⚠️ 🔁); no external formatting library used. |
| 5. Multi-model prompt comparison | ❌ Not attempted | `ai_interactions.md` documents a same-tool prompt comparison, not a true cross-model comparison. Would need a second assistant (e.g. Gemini/ChatGPT) run on the same prompt. |

## Architecture

- Draft UML: `diagrams/uml.mmd`
- Final UML: `diagrams/uml_final.mmd`
- Backend logic: `pawpal_system.py`
- CLI verification: `main.py`
- Streamlit UI: `app.py`
- Tests: `tests/test_pawpal.py`
