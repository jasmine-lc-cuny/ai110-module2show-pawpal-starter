# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions I wanted PawPal+ to support were adding a pet, scheduling care tasks like walks or medication, and viewing a sorted daily schedule. My initial UML design used four main classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` stores multiple pets, `Pet` stores pet details and its task list, `Task` represents one care activity, and `Scheduler` acts as the organizer that sorts, filters, completes, and checks tasks. I kept the design simple so the Streamlit UI could call clear backend methods instead of mixing scheduling logic into the page.

**b. Design changes**

My design changed when I realized recurring tasks needed more than just a title and time. I added `due_date`, `frequency`, and `completed` to `Task` so the scheduler could know what still needs attention and create the next daily or weekly occurrence. I also added `Owner.find_pet()` because both the UI and scheduler needed a clean way to look up a pet by name. This made the code easier to read than repeatedly looping through pets inside the Streamlit file.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers scheduled time, priority, pet name, completion status, recurrence, and exact task conflicts. Time matters most for the normal schedule view because pet owners usually want to know what happens next. Priority matters for a second view because some care tasks, like medication, should stand out even if they happen later. Completion status matters so finished tasks do not clutter the open-task workflow.

**b. Tradeoffs**

One tradeoff is that conflict detection only checks for exact same date and time matches, not overlapping durations. For example, a 30-minute walk at 8:00 and a 15-minute grooming task at 8:10 would not be flagged even though they overlap in real life. I kept this simpler approach because it is easy to explain, test, and display as a warning without overcomplicating the project. If I had more time, I would add start/end time comparisons.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI as a planning and implementation teammate. Codex helped turn the assignment requirements into a phased plan, create the UML and class skeletons, implement the OOP backend, wire the Streamlit UI, write tests, and update the documentation. The most helpful prompts were specific and phase-based, such as asking how the `Scheduler` should retrieve all tasks from an `Owner` or how to keep Streamlit objects in `st.session_state`. Keeping design, implementation, testing, and documentation separate made the project easier to review.

**Which AI features were most effective?** Agent/edit mode was the most effective feature for this project — being able to point it at `pawpal_system.py`, `app.py`, and `tests/test_pawpal.py` together let it make coordinated changes (like adding `due_date`/`frequency` to `Task` and updating every place that constructs a `Task`) in one pass instead of me manually keeping files in sync. Plain chat was more useful for narrower questions, like asking for a `timedelta`-based recurrence formula or a cleaner way to format the CLI schedule.

**How did separate chat sessions help?** Starting a new session for Phase 4 (algorithms) and Phase 5 (tests) instead of continuing the Phase 1-2 session kept each conversation focused on one concern. It meant the AI wasn't trying to reconcile "skeleton design" advice with "test coverage" advice at the same time, and it made it easier for me to review each phase's output against just that phase's requirements before moving on.

**b. Judgment and verification**

One suggestion I modified was to keep conflict detection lightweight instead of building a full calendar overlap engine. A more advanced overlap algorithm would be more realistic, but it would also make the code harder to explain for this assignment. I also caught and reverted a case where AI-drafted README output (originally written against an experimental branch with emoji formatting and extra "urgent task" sections) had drifted from what `main.py` actually prints — I had to re-run the script and replace the pasted output with the real output before trusting the README as evidence the system works. I verified the final logic with a CLI demo, automated pytest cases, and a Streamlit startup check. I also reviewed the files manually to make sure the UML, README, and reflection matched the actual code.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, adding tasks to pets, sorting tasks by time, filtering by pet/status, daily recurrence, and conflict detection. These tests are important because they cover the core behaviors PawPal+ promises to users. The recurrence test checks that completing a daily task creates tomorrow's task instead of losing the routine. The conflict test checks that the scheduler returns a warning instead of crashing or silently ignoring duplicate times.

**b. Confidence**

I am 4 out of 5 confident that the scheduler works correctly for the project requirements. The tests pass and the CLI demo shows sorting, priority ordering, conflicts, and recurrence working together. The main remaining edge cases are overlapping durations, invalid time formats, and saving data after the Streamlit session ends. Those would be my next tests if I extended the project.

---

## 5. Reflection

**a. What went well**

The clean separation between backend logic and UI went well. Building `pawpal_system.py` first made it easier to test the system before worrying about Streamlit forms and tables. I am most satisfied with the scheduler methods because they are small, readable, and directly connected to the project requirements.

**b. What you would improve**

In another iteration, I would add JSON persistence so pets and tasks survive after the app closes. I would also improve conflict detection to check overlapping durations, not just exact time matches. The UI could also include edit/delete actions for pets and tasks. Those changes would make PawPal+ feel more like a real pet care app.

**c. Key takeaway**

My biggest takeaway is that being the lead architect means deciding what the AI should build, not just accepting everything it suggests. AI was helpful for scaffolding, algorithms, and tests, but I still had to choose the class relationships, keep the design understandable, and verify the behavior. Separate phases helped me stay organized because each chat or task had a clear purpose. The best results came from combining AI speed with human judgment about scope and readability.
