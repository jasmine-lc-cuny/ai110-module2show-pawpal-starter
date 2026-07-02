# AI Interactions Log

## Agent Workflow

This project used two different AI coding assistants for two different jobs: Codex built the initial skeleton and backend, and Claude Code (used in the follow-up session covering this log) audited that work against the assignment, fixed what was actually broken, and completed the optional challenges. Codex was then brought back in for one narrow, specific job: acting as the second model in the Challenge 5 comparison below.

### Stage 1 — Initial build (Codex)

**What task did I give the agent?**

I asked Codex to help me complete the PawPal+ project from the CodePath instructions. The work was split into phases: create a UML design and class skeleton, implement the OOP backend, connect the backend to Streamlit, add scheduling algorithms, write pytest tests, and finish the README/reflection.

**What did the agent do?**

Codex created `pawpal_system.py` with the `Owner`, `Pet`, `Task`, and `Scheduler` classes, updated `diagrams/uml.mmd`, and added `diagrams/uml_final.mmd`. It implemented sorting by time, priority sorting, filtering, recurrence, conflict detection, and task completion. It also created `main.py` for CLI verification, rewrote `app.py` so Streamlit uses `st.session_state`, added `tests/test_pawpal.py`, and produced an initial pass at `README.md`/`reflection.md`.

### Stage 2 — Audit, bug fixes, and optional challenges (Claude Code)

**What task did I give the agent?**

I asked Claude Code to check whether Codex's finished project actually matched the assignment line by line, not just look complete, and to fix anything it found — including going after the optional challenges properly instead of leaving them undone or half-claimed.

**What did the agent do?**

- Audited every phase and all five optional challenges against the assignment text, and reported the gap honestly instead of assuming the project was done: the README's "Sample Output" section showed emoji formatting and two whole sections ("🚨 Next Urgent Task", "⭐ Today's Top 3 Priorities") that didn't exist anywhere in the actual code. It traced this to an abandoned git branch (`backup-current-ef1058f`) whose output had been pasted into the README on `main` without the code that produced it ever being merged.
- Fixed that by re-running `main.py` for real and replacing the fabricated output with the actual output, everywhere it appeared in the README.
- First made the emojis genuinely real instead of removing them: added `✅`/`⏳` status icons to `Task.summary()` and emoji section headers to `main.py`. On review this only satisfied Optional Challenge 4 loosely — the assignment lists three example formats (color-coded status, emojis for different task types, structured CLI tables) and only one was even partially covered, and not quite as literally described. Closed all three for real: (1) added `task_type_icon()` in `pawpal_system.py`, a keyword lookup that picks a different emoji per task category (🐕 walk, 💊 medication, 🍖 feeding, 🧼 grooming, 🏥 vet); (2) documented the color-coded `st.success()`/`st.warning()`/`st.info()` indicators already present in `app.py` from Phase 6, which Streamlit renders in distinct colors — that one just hadn't been credited before; (3) added the `tabulate` library (`requirements.txt`) and rewrote `main.py`'s `print_schedule()` to render every schedule section as a real table.
- Caught (from a screenshot the user shared of the README rendered in VS Code) that the first `tabulate` attempt used a Unicode box-drawing format (`tablefmt="rounded_outline"`) with the task-type icon in its own column with an empty header. In VS Code's markdown preview, emoji glyphs render wider than the single monospace column `tabulate` assumes, and that width error compounded across the row, breaking the box borders and clipping the "Status" header to "Stat". Fixed by merging the icon into the Task column's text instead of a dedicated icon-only column, and switching to `tablefmt="github"` (plain ASCII `|`/`-` characters, no Unicode corners) so any remaining width drift shows as minor uneven spacing instead of a visibly broken table.
- Swapped `tabulate` for `prettytable` at the user's request, keeping the same alignment fix in mind: used `PrettyTable` with `TableStyle.MARKDOWN` (pipe/dash characters, no box corners), not the library's default box-drawing style, which would have reintroduced the same fragility. Confirmed the emoji-in-Task-column output still renders cleanly with this style before adopting it. `requirements.txt` updated (`tabulate` removed, `prettytable>=3.10` added). Verified the new README output is byte-for-byte identical to a fresh `python main.py` run.
- Implemented `Scheduler.next_urgent_task()` and `Scheduler.top_priorities(n)` — a distinct ranking capability beyond the four base scheduling algorithms — which is what earns Optional Challenge 1.
- Implemented Optional Challenge 2 (JSON persistence) for real: `to_dict()`/`from_dict()` on `Task`, `Pet`, and `Owner`, plus `Owner.save_to_json()`/`Owner.load_from_json()`. Wired into `main.py` (a real save-then-reload round trip) and into `app.py` (auto-load on session start, auto-save after every render, so Streamlit state survives a full app restart, not just `st.session_state` within one session).
- Ran the Challenge 5 multi-model comparison below, and — this is the important part — didn't just record the comparison, but caught the integration gap in Codex's answer and fixed it in the actual codebase (see the Prompt Comparison section).
- Added 7 new pytest cases covering all of the above (13 total, up from 6), kept `diagrams/uml_final.mmd` in sync with every new/changed method signature, and verified everything by actually running `pytest`, running `main.py`, and booting the Streamlit app headlessly rather than assuming the code worked.

**What did I have to verify or fix manually?**

I reviewed each fix before accepting it — for example, confirming the "High Priority First" CLI section in the (formerly stale) README sample actually matched what `Scheduler.sort_by_priority_then_time()` produced, and checking that the new JSON persistence didn't silently break the existing recurrence/conflict tests before committing. I also kept the original conflict-detection design decision (exact date/time matches only, not overlapping durations) — that one was already a reasonable scope call from Stage 1 and didn't need to change.

---

## Prompt Comparison (Optional Challenge 5)

**Task:** the assignment's own suggested complex algorithmic task — rescheduling logic for weekly recurring tasks. Specifically: `Task.next_occurrence()` originally always computed `due_date + 7 days` for a weekly task, even if it was completed several days late, which could create a "next" task that was already overdue. I asked two different AI models the same self-contained prompt (the `Task`/`next_occurrence` code plus the question of how to fix this) to compare their solutions.

| | Model A: Codex | Model B: Claude |
|-|-----------------|------------------|
| **Model / tool used** | Codex (OpenAI coding agent) | Claude (Claude Code, this session) |
| **Prompt** | Same prompt given to both: the current `Task`/`next_occurrence()` code, plus "how would you implement rescheduling logic for a late-completed weekly task — anchor to the original due date or the completion date?" | Same prompt as Model A. |
| **Response summary** | Recommended a hybrid: keep the task anchored to its original cadence, but if completion is late, roll forward in `step` increments (`timedelta(weeks=1)`/`timedelta(days=1)`) past the completion date so the next occurrence always lands in the future. Provided a `next_occurrence(completed_on=...)` implementation using a `while` loop, and an updated `mark_task_complete()` signature. | Independently proposed the same core hybrid strategy (anchor to cadence, roll forward past late completions) before seeing Codex's code, since it's the standard pattern for recurring-reminder scheduling and avoids the schedule permanently drifting. Flagged two things Codex's answer didn't cover: (1) the fix is inert unless `Scheduler.mark_task_complete()` is also updated to pass `completed_on=date.today()` through to `next_occurrence()` — swapping in the new method alone changes nothing; (2) the `while` loop could be replaced with a closed-form `divmod` calculation, but for a pet-care app (nobody misses hundreds of weeks) the loop is clearer and just as correct, so not worth the complexity. |
| **What was useful** | A concrete, directly runnable implementation with a clear explanation of the anchoring tradeoff (original due date vs. completion date vs. hybrid). | Caught that the algorithm alone wasn't enough — the call site (`mark_task_complete`) had to change too, or the fix would silently do nothing. Confirmed the loop-based approach didn't need to be replaced with more "clever" math. |
| **What was flawed** | Didn't mention that the caller (`Scheduler.mark_task_complete()`) needed to be updated to actually pass a completion date — the sample code alone wouldn't change behavior if dropped in as-is. | No implementation-breaking flaw found; the main contribution was integration risk, not an alternative algorithm. |
| **Final decision** | Adopted Codex's `next_occurrence(completed_on)` implementation (the roll-forward-past-late-completions loop) largely as written. | Adopted Claude's fix for the integration gap: `Scheduler.mark_task_complete()` now accepts an optional `completed_on` and defaults it to `date.today()` before calling `next_occurrence()`, so the late-completion behavior actually takes effect without every caller having to remember to pass a date. |

**What changed in the codebase:** `Task.next_occurrence()` in `pawpal_system.py` now accepts `completed_on` and rolls the next date forward past it; `Scheduler.mark_task_complete()` passes `completed_on=completed_on or date.today()`. Covered by `test_weekly_recurrence_on_time_uses_original_cadence` and `test_weekly_recurrence_skips_ahead_when_completed_late` in `tests/test_pawpal.py`. `diagrams/uml_final.mmd` and the README's Smarter Scheduling table were updated to match.

---

## Additional Prompt Notes (single-tool, not the Challenge 5 submission)

From Stage 1 (the initial Codex build), I also compared two prompts given to the same tool (Codex) at different phases — useful for tracking how prompts evolved, but not a cross-model comparison, so it doesn't count toward Challenge 5 above.

| | Prompt A | Prompt B |
|-|----------|----------|
| **Model / tool used** | Codex, used for implementation planning | Codex, used for testing review |
| **Prompt** | "Build PawPal+ from the assignment phases and keep the backend separate from the UI." | "What should be tested for a pet scheduler with sorting, recurring tasks, and conflicts?" |
| **Response summary** | Suggested creating `Owner`, `Pet`, `Task`, and `Scheduler`, then wiring Streamlit to those classes through session state. | Suggested tests for completion, adding tasks, sorting, recurrence, filtering, and conflict detection. |
| **What was useful** | The phased approach kept the project from becoming one giant edit. | The test plan mapped directly to the assignment requirements. |
| **Problems noticed** | A more advanced conflict algorithm would have been possible but too large for the required scope. | Some edge cases, like overlapping durations, were noted but not implemented. |
| **Decision** | Keep a clean OOP design with simple exact-time conflict warnings. | Test the required behavior now and document future edge cases in the reflection. |

**Which approach did you use in your final implementation and why?**

I used the phased implementation approach because it matched the CodePath instructions and made each commit easier to understand. I also used the testing review to decide which behaviors were most important to verify before submitting. I rejected extra complexity when it would make the project harder to explain, especially around calendar-style overlap detection.
