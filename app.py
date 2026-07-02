from pathlib import Path

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task, format_time_12h, task_type_icon


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

DATA_PATH = Path("data.json")


def get_owner():
    """Return the session's owner, loading it from data.json once if needed."""
    if "owner" not in st.session_state:
        if DATA_PATH.exists():
            st.session_state.owner = Owner.load_from_json(str(DATA_PATH))
        else:
            st.session_state.owner = Owner("Jordan")
    return st.session_state.owner


def task_rows(task_pairs):
    """Convert scheduler task pairs into table-friendly dictionaries."""
    return [
        {
            "Type": task_type_icon(task.title),
            "Time": format_time_12h(task.time),
            "Pet": pet.name,
            "Species": pet.species,
            "Task": task.title,
            "Duration": task.duration_minutes,
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Due Date": task.due_date.isoformat(),
            "Status": "✅ Done" if task.completed else "⏳ Open",
        }
        for pet, task in task_pairs
    ]


owner = get_owner()
scheduler = Scheduler(owner)

st.title("PawPal+")
st.caption("A smart pet care scheduler for daily routines and reminders.")

owner.name = st.sidebar.text_input("Owner name", value=owner.name)
view_mode = st.sidebar.radio("Schedule view", ["Time", "Priority"], horizontal=True)
pet_filter = st.sidebar.selectbox(
    "Filter by pet",
    ["All pets"] + [pet.name for pet in owner.pets],
)
status_filter = st.sidebar.selectbox("Filter by status", ["Open", "Done", "All"])

left, right = st.columns([1, 2])

with left:
    st.subheader("Pets")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
        submitted_pet = st.form_submit_button("Add pet")

    if submitted_pet and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species, int(age)))
        st.success(f"Added {pet_name.strip()}.")
        st.rerun()

    if owner.pets:
        st.table(
            [
                {"Name": pet.name, "Species": pet.species, "Age": pet.age}
                for pet in owner.pets
            ]
        )

        pet_to_delete = st.selectbox(
            "Delete a pet",
            owner.pets,
            format_func=lambda pet: f"{pet.name} ({pet.species}, age {pet.age}, {len(pet.tasks)} task(s))",
        )
        if st.button("Delete pet"):
            owner.remove_pet(pet_to_delete)
            st.success(f"Deleted {pet_to_delete.name} and their tasks.")
            st.rerun()

        st.markdown("**Edit a pet**")
        pet_to_edit = st.selectbox(
            "Pet to edit",
            owner.pets,
            format_func=lambda pet: pet.name,
            key="edit_pet_select",
        )
        with st.form("edit_pet_form"):
            edited_name = st.text_input("Name", value=pet_to_edit.name)
            species_options = ["dog", "cat", "other"]
            edited_species = st.selectbox(
                "Species",
                species_options,
                index=species_options.index(pet_to_edit.species)
                if pet_to_edit.species in species_options
                else species_options.index("other"),
            )
            edited_age = st.number_input(
                "Age", min_value=0, max_value=40, value=pet_to_edit.age or 0
            )
            submitted_edit = st.form_submit_button("Save changes")

        if submitted_edit and edited_name.strip():
            pet_to_edit.name = edited_name.strip()
            pet_to_edit.species = edited_species
            pet_to_edit.age = int(edited_age)
            st.success(f"Updated {pet_to_edit.name}.")
            st.rerun()
    else:
        st.info("Add a pet to start scheduling care tasks.")

with right:
    st.subheader("Schedule a Task")
    if not owner.pets:
        st.warning("Add at least one pet before scheduling tasks.")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            selected_pet = st.selectbox("Pet", [pet.name for pet in owner.pets])
            title = st.text_input("Task title", value="Morning walk")

            st.write("Time")
            hour_col, minute_col, period_col = st.columns(3)
            with hour_col:
                hour_12 = st.selectbox(
                    "Hour", list(range(1, 13)), index=7, label_visibility="collapsed"
                )
            with minute_col:
                minute = st.selectbox(
                    "Minute", ["00", "15", "30", "45"], label_visibility="collapsed"
                )
            with period_col:
                period = st.selectbox("AM/PM", ["AM", "PM"], label_visibility="collapsed")

            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
            submitted_task = st.form_submit_button("Add task")

        if submitted_task and title.strip():
            pet = owner.find_pet(selected_pet)
            if pet is not None:
                hour_24 = hour_12 % 12
                if period == "PM":
                    hour_24 += 12
                pet.add_task(
                    Task(
                        title=title.strip(),
                        time=f"{hour_24:02d}:{minute}",
                        duration_minutes=int(duration),
                        priority=priority,
                        frequency=frequency,
                    )
                )
                st.success(f"Added {title.strip()} for {selected_pet}.")
                st.rerun()

st.divider()

completed_filter = None
if status_filter == "Open":
    completed_filter = False
elif status_filter == "Done":
    completed_filter = True

pet_name = None if pet_filter == "All pets" else pet_filter
filtered = scheduler.filter_tasks(pet_name=pet_name, completed=completed_filter)
display_tasks = (
    scheduler.sort_by_priority_then_time(filtered)
    if view_mode == "Priority"
    else scheduler.sort_by_time(filtered)
)

st.subheader("Care Schedule")
if display_tasks:
    st.table(task_rows(display_tasks))
else:
    st.info("No tasks match the current filters.")

st.divider()
st.subheader("Today's Highlights")

todays_tasks = scheduler.todays_schedule()

st.markdown("**📅 Today's Schedule**")
if todays_tasks:
    st.table(task_rows(todays_tasks))
else:
    st.info("No open tasks due today.")

st.markdown("**❗ High Priority First**")
high_priority_today = scheduler.sort_by_priority_then_time(todays_tasks)
if high_priority_today:
    st.table(task_rows(high_priority_today))
else:
    st.info("No open tasks due today.")

st.markdown("**🚨 Next Urgent Task**")
urgent = scheduler.next_urgent_task()
if urgent:
    st.table(task_rows([urgent]))
else:
    st.info("No open tasks due today.")

st.markdown("**⭐ Today's Top 3 Priorities**")
top_priorities = scheduler.top_priorities(3)
if top_priorities:
    st.table(task_rows(top_priorities))
else:
    st.info("No open tasks due today.")

st.markdown("**⚠️ Conflict Warnings**")
conflicts = scheduler.detect_conflicts(scheduler.filter_tasks(completed=False))
if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No open task conflicts.")

if owner.pets:
    st.subheader("Complete a Task")
    open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    task_options = [f"{pet.name} | {task.title}" for pet, task in open_tasks]
    if task_options:
        selected = st.selectbox("Open task", task_options)
        if st.button("Mark complete"):
            pet_name, task_title = selected.split(" | ", 1)
            scheduler.mark_task_complete(pet_name, task_title)
            st.success(f"Completed {task_title}.")
            st.rerun()
    else:
        st.info("All tasks are complete.")

    st.subheader("Delete or Reopen a Task")
    all_tasks = scheduler.sort_by_time(scheduler.filter_tasks())
    if all_tasks:
        selected_task_pair = st.selectbox(
            "Task",
            all_tasks,
            format_func=lambda pair: f"{pair[0].name} | {pair[1].title} ({'Done' if pair[1].completed else 'Open'})",
        )
        selected_pet, selected_task = selected_task_pair

        col1, col2 = st.columns(2)
        with col1:
            if selected_task.completed and st.button("Reopen task"):
                selected_task.mark_incomplete()
                st.success(f"Reopened {selected_task.title}.")
                st.rerun()
        with col2:
            if st.button("Delete task"):
                selected_pet.remove_task(selected_task)
                st.success(f"Deleted {selected_task.title}.")
                st.rerun()
    else:
        st.info("No tasks yet.")

owner.save_to_json(str(DATA_PATH))
st.caption(f"Data is auto-saved to `{DATA_PATH}` after every change, so it persists between app runs.")
