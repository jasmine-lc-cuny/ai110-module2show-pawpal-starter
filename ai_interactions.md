# AI Interactions Log

## Agent Workflow

**What task did you give the agent?**

I asked Codex to help me complete the PawPal+ project from the CodePath instructions. The work was split into phases: create a UML design and class skeleton, implement the OOP backend, connect the backend to Streamlit, add scheduling algorithms, write pytest tests, and finish the README/reflection. I wanted the agent to keep the commits meaningful so the project history showed design, implementation, testing, and documentation progress.

**What did the agent do?**

Codex created `pawpal_system.py` with the `Owner`, `Pet`, `Task`, and `Scheduler` classes, updated `diagrams/uml.mmd`, and added `diagrams/uml_final.mmd`. It implemented sorting by time, priority sorting, filtering, recurrence, conflict detection, and task completion. It also created `main.py` for CLI verification, rewrote `app.py` so Streamlit uses `st.session_state`, added `tests/test_pawpal.py`, ran `python main.py`, ran `python -m pytest`, and updated `README.md` and `reflection.md`.

**What did you have to verify or fix manually?**

I reviewed the design choices and kept the conflict detection intentionally simple so it only warns on exact date/time matches. I also checked that the README output matched the actual terminal output and that the final UML matched the implemented methods. One thing I watched for was overly complex scheduling logic; I wanted the solution to be understandable for a first OOP scheduler project, not a full calendar system.

---

## Prompt Comparison

**Status: Optional Challenge 5 (multi-model comparison) was not completed.** The table below records two prompts given to the *same* AI coding assistant (Codex) at different phases of the project — it is a useful record of how the prompts differed, but it is **not** a comparison across two different models/tools (e.g. Claude vs. Gemini, ChatGPT vs. Copilot) as Challenge 5 requires. Leaving this here for transparency instead of dressing it up as something it isn't; a real multi-model comparison would need a second assistant run on the same task and is not part of this submission.

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
