# AI Interactions Log

## Agent Workflow

**What task did you give the agent?**

I asked Codex to help me complete the PawPal+ project from the CodePath instructions. The work was split into phases: create a UML design and class skeleton, implement the OOP backend, connect the backend to Streamlit, add scheduling algorithms, write pytest tests, and finish the README/reflection. I wanted the agent to keep the commits meaningful so the project history showed design, implementation, testing, and documentation progress.

**What did the agent do?**

Codex created `pawpal_system.py` with the `Owner`, `Pet`, `Task`, and `Scheduler` classes, updated `diagrams/uml.mmd`, and added `diagrams/uml_final.mmd`. It implemented sorting by time, priority sorting, filtering, recurrence, conflict detection, and task completion. It also created `main.py` for CLI verification, rewrote `app.py` so Streamlit uses `st.session_state`, added `tests/test_pawpal.py`, ran `python main.py`, ran `python -m pytest`, and updated `README.md` and `reflection.md`.

**What did you have to verify or fix manually?**

I reviewed the design choices and kept the conflict detection intentionally simple so it only warns on exact date/time matches. I also checked that the README output matched the actual terminal output and that the final UML matched the implemented methods. One thing I watched for was overly complex scheduling logic; I wanted the solution to be understandable for a first OOP scheduler project, not a full calendar system.

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

Earlier in the project I also compared two prompts given to the same tool (Codex) at different phases — useful for tracking how prompts evolved, but not a cross-model comparison, so it doesn't count toward Challenge 5 above.

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
