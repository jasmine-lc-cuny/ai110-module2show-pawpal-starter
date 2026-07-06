# PawPal+ (Module 2 Project)

PawPal+ is a Streamlit pet care management app that helps an owner track pets,
schedule daily care tasks, spot conflicts, and keep recurring routines moving.
The system is built CLI-first: the backend classes in `pawpal_system.py` are
verified through `main.py` and pytest before being connected to the UI in
`app.py`.

## Features

- A multi-page Streamlit app: a Home landing page with a "Book a Service" picker (Grooming, Sitting, Training, Walking, Veterinary, Special Services), a dedicated "My Pets & Schedule" page for full pet/task management, and one page per service category showing just that category's tasks with a quick-add form.
- Add an owner, pets, and scheduled care tasks, choosing a task title from a dropdown of common care tasks (or "Other (custom)" for anything else).
- Edit or delete a pet from the Streamlit UI (deletion disambiguated by species/age/task count so similarly-named pets aren't mixed up).
- Edit a task's title, time, duration, or priority; delete a task outright; or reopen one that was marked complete by mistake. Frequency still exists in the backend for recurring-task logic, but it is hidden from the quick-add form now to keep the UI simpler.
- Track task time (shown as 12-hour AM/PM), duration, priority, due date, and completion, with frequency retained behind the scenes for recurring tasks.
- View today's schedule sorted by time and by priority side by side, always both at once.
- Filter every schedule view by pet and by completion status.
- Detect exact date/time conflicts and show warnings.
- Mark tasks complete and automatically create the next daily or weekly task.
- Surface today's single next urgent task and a top-3 priority shortlist.
- Use a Streamlit interface backed by `st.session_state` so pets and tasks stay available during the browser session.
- Persist all pets and tasks to `data.json` (Streamlit app) so they survive between application runs, separately from `main.py`'s own `main_demo_data.json`.
- Show a per-species pet avatar (🐕 dog, 🐈 cat, 🐾 other), a different emoji per task type (walk, medication, feeding, ear care, dental, nail trim, haircut, bath, brushing, vet), traffic-light priority dots (🔴 high / 🟡 medium / 🟢 low) in every schedule table, color-coded status messages in the Streamlit UI, and `PrettyTable`-rendered tables with ANSI-colored priority/status/warning text in the CLI (colors auto-disable when output is piped, the same convention `git` and `pytest` follow).

## Setup

```bash
pip install -r requirements.txt
```

Run the CLI demo:

```bash
python main.py
```

Run the Streamlit app (still `app.py` — it's now the multi-page entry point, with each page's content in `pages/`):

```bash
python -m streamlit run app.py
```

## Sample Output

Example output from running `python main.py`:

```text
PawPal+ schedule for Jordan
================================
📅 Today's Schedule

| Time     | Pet      | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-02 | ⏳ open |

❗ High Priority First

| Time     | Pet      | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-02 | ⏳ open |

🐾 Mochi's Open Tasks

| Time     | Pet      | Species | Task                    | Duration | Priority | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :--------| :---------| :----------| :-------|
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high  | once      | 2026-07-02 | ⏳ open |

🚨 Next Urgent Task

| Time    | Pet     | Species | Task         | Duration | Priority | Frequency | Due Date   | Status  |
| :-------| :-------| :-------| :------------| :--------| :--------| :---------| :----------| :-------|
| 7:30 AM | 🐈 Luna | cat     | 🍖 Breakfast | 10 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |

⭐ Today's Top 3 Priorities

| Time     | Pet      | Species | Task                    | Duration | Priority | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :--------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high  | once      | 2026-07-02 | ⏳ open |

⚠️ Conflict Warnings

  Conflict on 2026-07-02 at 8:00 AM: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created

| Time    | Pet      | Species | Task            | Duration | Priority | Frequency | Due Date   | Status  |
| :-------| :--------| :-------| :---------------| :--------| :--------| :---------| :----------| :-------|
| 8:00 AM | 🐕 Mochi | dog     | 🐕 Morning walk | 30 min   | 🔴 high  | daily     | 2026-07-03 | ⏳ open |

💾 Saved to main_demo_data.json and reloaded a fresh Owner from disk
Reloaded Schedule (from main_demo_data.json)

| Time     | Pet      | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-02 | ⏳ open |
```

## Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks chronologically using `HH:MM` strings. |
| Priority sorting | `Scheduler.sort_by_priority_then_time()` | Sorts high priority first, then by time. |
| Filtering | `Scheduler.filter_tasks()` | Filters by pet name and/or completion status; see "🐾 Mochi's Open Tasks" in the Sample Output above. |
| Conflict handling | `Scheduler.detect_conflicts()` | Returns warning strings for exact same date/time matches. |
| Recurring tasks | `Task.next_occurrence(completed_on)`, `Scheduler.mark_task_complete()` | Creates the next daily or weekly task after completion. Anchors to the original cadence, but if completion is late it skips forward until the next occurrence actually lands in the future instead of creating an already-overdue task. See `ai_interactions.md` for the two-model design comparison behind this. |
| Next urgent task | `Scheduler.next_urgent_task()` | Returns today's single highest-priority, earliest-time open task (or `None`). |
| Top priorities | `Scheduler.top_priorities(n=3)` | Returns today's top `n` open tasks ranked by priority then time. |

## Data Persistence

PawPal+ saves its state to JSON so pets and tasks survive between runs, instead of resetting every time the app or script restarts.

- **What was added:** `Task.to_dict()`/`Task.from_dict()`, `Pet.to_dict()`/`Pet.from_dict()`, and `Owner.to_dict()`/`Owner.from_dict()` convert the object graph to and from plain dictionaries (dates are stored as ISO strings). `Owner.save_to_json(path)` writes that dictionary to a JSON file with `json.dump`; `Owner.load_from_json(path)` (a classmethod) reads it back and rebuilds a full `Owner` → `Pet` → `Task` object graph.
- **Two separate files, on purpose:** `main.py`'s CLI demo saves to `main_demo_data.json`, while `app.py`'s Streamlit UI saves to `data.json`. They used to share the same `data.json`, which meant running the CLI demo (scripted `Mochi`/`Luna` data) would silently overwrite whatever real pets/tasks were saved from the live Streamlit app, and vice versa. Splitting the filenames means running one never touches the other's data.
- **Files modified:** `pawpal_system.py` (serialization methods), `main.py` (demonstrates a save → reload round trip against `main_demo_data.json` at the end of the CLI run, see Sample Output above), `app.py` (loads `data.json` on first load of a session if it exists, and auto-saves after every render so pet/task changes survive an app restart), `.gitignore` (excludes both generated files so runtime data isn't committed), `tests/test_pawpal.py` (`test_save_and_load_json_round_trip` verifies a full save/reload cycle preserves pet details and task fields, including dates and recurrence, using a temp file so it never touches either real file).
- **Workflow:** in the CLI, `python main.py` builds the demo data, mutates it, saves it to `main_demo_data.json`, then reloads a brand-new `Owner` straight from that file to prove the round trip works. In the Streamlit app, adding a pet, adding a task, or completing a task immediately persists to `data.json`; reloading the page (a fresh Streamlit session) reads that file back in instead of starting empty.

## Testing PawPal+

Run the full test suite:

```bash
python -m pytest
```

The tests cover task completion, task addition, chronological sorting (plus
an empty-list edge case), filtering (including a no-match edge case), daily
recurrence, late-completion recurrence skip-ahead, conflict detection,
next-urgent-task selection, top-priority ranking, per-task-type icon
selection, and a JSON save/load round trip.

```text
============================= test session starts ==============================
platform linux -- Python 3.12.1, pytest-9.1.1, pluggy-1.6.0
rootdir: /workspaces/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 15 items

tests/test_pawpal.py ...............                                     [100%]

============================== 15 passed in 0.02s ==============================
```

Confidence Level: 4/5 stars. The main happy paths and required scheduling
algorithms are tested, but a production system would need deeper validation for
time zones, overlapping durations, and saved data across app restarts.

## Demo Walkthrough

1. **Home** greets the user with a "Book a Service" picker — six cards (Grooming, Sitting, Training, Walking, Veterinary, Special Services) plus a link to "My Pets & Full Schedule" — and a Quick Glance of pet/open-task/conflict counts.
2. On **My Pets & Schedule**, the user enters their owner name in the sidebar (filters every schedule view by pet and by status), adds pets (name, species, sex, age), edits or deletes them, and schedules care tasks by picking a title from a dropdown of common tasks (or "Other (custom)"), plus a time (hour/minute/AM-PM), duration, priority, and frequency. An existing task's title/time/duration/priority/frequency can also be edited from a dropdown next to "Edit a pet".
3. A "Today's Highlights" section on that page mirrors the CLI's views for tasks due today, scoped by the sidebar's pet/status filters — 📅 Today's Schedule, ❗ High Priority First, 🚨 Next Urgent Task, and ⭐ Today's Top 3 Priorities — plus ⚠️ Conflict Warnings when two open tasks share the same date and time.
4. When the user marks a daily or weekly task complete, PawPal+ creates the next occurrence automatically. A task can also be deleted outright, or reopened if it was marked complete by mistake.
5. Each **service category page** (e.g. Walking) shows only that category's tasks — matched by `task_type_icon()` — with its own quick-add form (pre-scoped to relevant task titles) and a "Mark complete" action. Sitting and Training are placeholders for now, since no task types map to them yet.

Sample CLI output from `python main.py` (same run shown in the Sample Output section above):

```text
PawPal+ schedule for Jordan
================================
📅 Today's Schedule

| Time     | Pet      | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-02 | ⏳ open |

❗ High Priority First

| Time     | Pet      | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-02 | ⏳ open |

🐾 Mochi's Open Tasks

| Time     | Pet      | Species | Task                    | Duration | Priority | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :--------| :---------| :----------| :-------|
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high  | once      | 2026-07-02 | ⏳ open |

🚨 Next Urgent Task

| Time    | Pet     | Species | Task         | Duration | Priority | Frequency | Due Date   | Status  |
| :-------| :-------| :-------| :------------| :--------| :--------| :---------| :----------| :-------|
| 7:30 AM | 🐈 Luna | cat     | 🍖 Breakfast | 10 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |

⭐ Today's Top 3 Priorities

| Time     | Pet      | Species | Task                    | Duration | Priority | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :--------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐕 Mochi | dog     | 🐕 Morning walk         | 30 min   | 🔴 high  | daily     | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high  | once      | 2026-07-02 | ⏳ open |

⚠️ Conflict Warnings

  Conflict on 2026-07-02 at 8:00 AM: Mochi: Morning walk, Luna: Brush coat

🔁 Recurring Task Created

| Time    | Pet      | Species | Task            | Duration | Priority | Frequency | Due Date   | Status  |
| :-------| :--------| :-------| :---------------| :--------| :--------| :---------| :----------| :-------|
| 8:00 AM | 🐕 Mochi | dog     | 🐕 Morning walk | 30 min   | 🔴 high  | daily     | 2026-07-03 | ⏳ open |

💾 Saved to main_demo_data.json and reloaded a fresh Owner from disk
Reloaded Schedule (from main_demo_data.json)

| Time     | Pet      | Species | Task                    | Duration | Priority  | Frequency | Due Date   | Status  |
| :--------| :--------| :-------| :-----------------------| :--------| :---------| :---------| :----------| :-------|
| 7:30 AM  | 🐈 Luna  | cat     | 🍖 Breakfast            | 10 min   | 🔴 high   | daily     | 2026-07-02 | ⏳ open |
| 8:00 AM  | 🐈 Luna  | cat     | 🪮 Brush coat           | 15 min   | 🟡 medium | once      | 2026-07-02 | ⏳ open |
| 12:00 PM | 🐕 Mochi | dog     | 💊 Heartworm medication | 5 min    | 🔴 high   | once      | 2026-07-02 | ⏳ open |
```

## Optional Challenges

| Challenge | Status | Notes |
|---|---|---|
| 1. Advanced algorithmic capability | ✅ Done | `Scheduler.next_urgent_task()` and `Scheduler.top_priorities(n)` add a distinct ranking capability beyond the four base requirements. See the "Agent Workflow" section in `ai_interactions.md`. |
| 2. Data persistence (JSON) | ✅ Done | `Owner.save_to_json()`/`Owner.load_from_json()` (see Data Persistence section above); `main.py` and `app.py` persist to separate files (`main_demo_data.json` vs. `data.json`) so one never overwrites the other. |
| 3. Advanced priority scheduling | ✅ Done | `Task.priority` (`low`/`medium`/`high`) plus `Scheduler.sort_by_priority_then_time()`; see "❗ High Priority First" in the Sample Output above. |
| 4. Professional UI/output formatting | ✅ Done | **(a) emojis per task type** — `task_type_icon()` in `pawpal_system.py` picks a different icon per task (🐕 walk, 💊 medication, 🍖 feeding, 👂 ear care, 🦷 dental, 💅 nail trim, ✂️ haircut, 🧼 wash/bath, 🪮 brushing, 🏥 vet), plus `pet_species_icon()` for a per-species pet avatar (🐕 dog, 🐈 cat, 🐰 bunny, 🐾 other) and `main.py` section headers (📅 ❗ 🚨 ⭐ ⚠️ 🔁). **(b) traffic-light priority dots** — `priority_icon()` in `pawpal_system.py` (🔴 high / 🟡 medium / 🟢 low, unit-tested) renders next to every priority in both the CLI tables and every Streamlit schedule table (`task_rows()` in `app_common.py`). **(c) ANSI terminal colors** — `colorize()` in `main.py` colors priorities red/yellow/green, statuses (✅ done green / ⏳ open yellow), conflict warnings red, and section headers bold; colors are gated on `sys.stdout.isatty()` so piped/captured output (like the fenced sample blocks in this README) stays byte-clean — the same auto-disable convention `git` and `pytest` follow. **(d) color-coded status indicators** — `st.success()`/`st.warning()`/`st.info()` plus colored `st.badge()` status pills (Pending/Confirmed/Completed/Cancelled) in the Streamlit UI. **(e) structured CLI tables** — `main.py` uses `prettytable.PrettyTable` (`requirements.txt`) in Markdown style instead of plain printed lines. |
| 5. Multi-model prompt comparison | ✅ Done | Compared Codex vs. Claude on rescheduling late-completed weekly tasks; see the "Prompt Comparison" section in `ai_interactions.md`. The winning hybrid approach was adopted into `Task.next_occurrence()`/`Scheduler.mark_task_complete()`. |

## Architecture

- Draft UML: `diagrams/uml.mmd`
- Final UML: `diagrams/uml_final.mmd`
- Backend logic: `pawpal_system.py`
- CLI verification: `main.py`
- Streamlit UI: `app.py` (multi-page entry point — sets up `st.navigation()` and renders the Home landing page), `app_common.py` (shared state/helpers used by every page — `get_owner()`, `save_owner()`, `task_rows()`, category-to-icon mapping, `render_category_page()`, `render_placeholder_page()`), `pages/pets_and_schedule.py` (full pet/task management, moved intact from the original single-page `app.py`), `pages/{grooming,walking,veterinary,special_services}.py` (functional service-category pages built on `render_category_page()`), `pages/{sitting,training}.py` (placeholder pages — no matching task types yet)
- Tests: `tests/test_pawpal.py`

### A note on `st.selectbox()` and object identity

Several pages select a `Pet` or `Task` from a dropdown and then mutate it directly (edit a pet's name, add a task to a pet, mark a task complete, delete a task). Early versions of these features passed the live objects as `options` and used whatever `st.selectbox()` returned — under Streamlit's `AppTest` testing framework, that returned object is not guaranteed to be the same instance as the one inside `owner.pets`/`pet.tasks`, so mutating it silently edited a throwaway copy instead of the real data (confirmed via `id()` mismatches). Every such selectbox in this app now selects an **index** and re-fetches the live object from `owner.pets[i]` (or the equivalent list) immediately before use, which sidesteps the issue regardless of its root cause. Each fix was verified with a real `AppTest` interaction — select a value, submit, then check `data.json` on disk — not just a headless boot check.
