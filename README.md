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
- Persist all pets and tasks to `data.json` so they survive between application runs.
- Show a different emoji per task type (walk, medication, feeding, grooming, vet), color-coded status messages in the Streamlit UI, and `tabulate`-rendered tables in the CLI.

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
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🐕 │ 08:00  │ Mochi │ Morning walk         │ 30 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🧼 │ 08:00  │ Luna  │ Brush coat           │ 15 min     │ medium     │ once        │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

High Priority First
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🐕 │ 08:00  │ Mochi │ Morning walk         │ 30 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
│ 🧼 │ 08:00  │ Luna  │ Brush coat           │ 15 min     │ medium     │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

🚨 Next Urgent Task
╭────┬────────┬───────┬───────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task      │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼───────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴───────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

⭐ Today's Top 3 Priorities
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🐕 │ 08:00  │ Mochi │ Morning walk         │ 30 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

⚠️ Conflict Warnings
  Conflict on 2026-07-02 at 08:00: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created
╭────┬────────┬───────┬──────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task         │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🐕 │ 08:00  │ Mochi │ Morning walk │ 30 min     │ high       │ daily       │ 2026-07-03 │ ⏳ open  │
╰────┴────────┴───────┴──────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

💾 Saved to data.json and reloaded a fresh Owner from disk
Reloaded Schedule (from data.json)
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🧼 │ 08:00  │ Luna  │ Brush coat           │ 15 min     │ medium     │ once        │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯
```

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically using `HH:MM` strings. |
| Priority sorting | `Scheduler.sort_by_priority_then_time()` | Sorts high priority first, then by time. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name and/or completion status. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings for exact same date/time matches. |
| Recurring tasks | `Task.next_occurrence(completed_on)`, `Scheduler.mark_task_complete()` | Creates the next daily or weekly task after completion. Anchors to the original cadence, but if completion is late it skips forward until the next occurrence actually lands in the future instead of creating an already-overdue task. See `ai_interactions.md` for the two-model design comparison behind this. |
| Next urgent task | `Scheduler.next_urgent_task()` | Returns today's single highest-priority, earliest-time open task (or `None`). |
| Top priorities | `Scheduler.top_priorities(n=3)` | Returns today's top `n` open tasks ranked by priority then time. |

## Data Persistence

PawPal+ saves its state to `data.json` so pets and tasks survive between runs, instead of resetting every time the app or script restarts.

- **What was added:** `Task.to_dict()`/`Task.from_dict()`, `Pet.to_dict()`/`Pet.from_dict()`, and `Owner.to_dict()`/`Owner.from_dict()` convert the object graph to and from plain dictionaries (dates are stored as ISO strings). `Owner.save_to_json(path)` writes that dictionary to a JSON file with `json.dump`; `Owner.load_from_json(path)` (a classmethod) reads it back and rebuilds a full `Owner` → `Pet` → `Task` object graph.
- **Files modified:** `pawpal_system.py` (serialization methods), `main.py` (demonstrates a save → reload round trip at the end of the CLI run, see Sample Output above), `app.py` (loads `data.json` on first load of a session if it exists, and auto-saves after every render so pet/task changes survive an app restart), `.gitignore` (excludes the generated `data.json` so runtime data isn't committed), `tests/test_pawpal.py` (`test_save_and_load_json_round_trip` verifies a full save/reload cycle preserves pet details and task fields, including dates and recurrence).
- **Workflow:** in the CLI, `python main.py` builds the demo data, mutates it, saves it to `data.json`, then reloads a brand-new `Owner` straight from that file to prove the round trip works. In the Streamlit app, adding a pet, adding a task, or completing a task immediately persists to `data.json`; reloading the page (a fresh Streamlit session) reads that file back in instead of starting empty.

## Testing PawPal+

Run the full test suite:

```bash
python -m pytest
```

The tests cover task completion, task addition, chronological sorting,
filtering, daily recurrence, late-completion recurrence skip-ahead, conflict
detection, next-urgent-task selection, top-priority ranking, per-task-type
icon selection, and a JSON save/load round trip.

```text
============================= test session starts ==============================
platform linux -- Python 3.12.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 13 items

tests/test_pawpal.py .............                                       [100%]

============================== 13 passed in 0.04s ==============================
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
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🐕 │ 08:00  │ Mochi │ Morning walk         │ 30 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🧼 │ 08:00  │ Luna  │ Brush coat           │ 15 min     │ medium     │ once        │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

High Priority First
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🐕 │ 08:00  │ Mochi │ Morning walk         │ 30 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
│ 🧼 │ 08:00  │ Luna  │ Brush coat           │ 15 min     │ medium     │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

🚨 Next Urgent Task
╭────┬────────┬───────┬───────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task      │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼───────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴───────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

⭐ Today's Top 3 Priorities
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🐕 │ 08:00  │ Mochi │ Morning walk         │ 30 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

⚠️ Conflict Warnings
  Conflict on 2026-07-02 at 08:00: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created
╭────┬────────┬───────┬──────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task         │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🐕 │ 08:00  │ Mochi │ Morning walk │ 30 min     │ high       │ daily       │ 2026-07-03 │ ⏳ open  │
╰────┴────────┴───────┴──────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯

💾 Saved to data.json and reloaded a fresh Owner from disk
Reloaded Schedule (from data.json)
╭────┬────────┬───────┬──────────────────────┬────────────┬────────────┬─────────────┬────────────┬──────────╮
│    │ Time   │ Pet   │ Task                 │ Duration   │ Priority   │ Frequency   │ Due Date   │ Status   │
├────┼────────┼───────┼──────────────────────┼────────────┼────────────┼─────────────┼────────────┼──────────┤
│ 🍖 │ 07:30  │ Luna  │ Breakfast            │ 10 min     │ high       │ daily       │ 2026-07-02 │ ⏳ open  │
│ 🧼 │ 08:00  │ Luna  │ Brush coat           │ 15 min     │ medium     │ once        │ 2026-07-02 │ ⏳ open  │
│ 💊 │ 12:00  │ Mochi │ Heartworm medication │ 5 min      │ high       │ once        │ 2026-07-02 │ ⏳ open  │
╰────┴────────┴───────┴──────────────────────┴────────────┴────────────┴─────────────┴────────────┴──────────╯
```

## Optional Challenges

| Challenge | Status | Notes |
|---|---|---|
| 1. Advanced algorithmic capability | ✅ Done | `Scheduler.next_urgent_task()` and `Scheduler.top_priorities(n)` add a distinct ranking capability beyond the four base requirements. See the "Agent Workflow" section in `ai_interactions.md`. |
| 2. Data persistence (JSON) | ✅ Done | `Owner.save_to_json()`/`Owner.load_from_json()` (see Data Persistence section above); pets/tasks survive both `main.py` runs and Streamlit restarts via `data.json`. |
| 3. Advanced priority scheduling | ✅ Done | `Task.priority` (`low`/`medium`/`high`) plus `Scheduler.sort_by_priority_then_time()`; see "High Priority First" in the Sample Output above. |
| 4. Professional UI/output formatting | ✅ Done | All three suggested formats, all real: **(a) emojis per task type** — `task_type_icon()` in `pawpal_system.py` maps task-title keywords to a different icon (🐕 walk, 💊 medication, 🍖 feeding, 🧼 grooming, 🏥 vet), used in `main.py`'s tables and the `Type` column in `app.py`'s `task_rows()` (Streamlit table). Plus `main.py` section headers (📅 🚨 ⭐ ⚠️ 🔁) and ✅/⏳ status icons. **(b) color-coded status indicators** — the Streamlit UI uses `st.success()`/`st.warning()`/`st.info()` for pet/task confirmations, conflict warnings, and empty states; Streamlit renders each with a distinct background color (green/yellow/blue). **(c) structured CLI tables** — `main.py`'s `print_schedule()` renders every schedule section with `tabulate(rows, headers=..., tablefmt="rounded_outline")` (the `tabulate` library, added to `requirements.txt`) instead of plain printed lines; see the box-drawn tables in the Sample Output above. |
| 5. Multi-model prompt comparison | ✅ Done | Compared Codex vs. Claude on rescheduling late-completed weekly tasks; see the "Prompt Comparison" section in `ai_interactions.md`. The winning hybrid approach was adopted into `Task.next_occurrence()`/`Scheduler.mark_task_complete()`. |

## Architecture

- Draft UML: `diagrams/uml.mmd`
- Final UML: `diagrams/uml_final.mmd`
- Backend logic: `pawpal_system.py`
- CLI verification: `main.py`
- Streamlit UI: `app.py`
- Tests: `tests/test_pawpal.py`
