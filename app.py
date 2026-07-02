from datetime import date
from pathlib import Path

import streamlit as st

from pawpal_system import (
    Owner,
    Pet,
    Scheduler,
    Task,
    format_time_12h,
    pet_species_icon,
    task_type_icon,
)


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

DATA_PATH = Path("data.json")

# Common care tasks offered in the "Schedule a Task" dropdown, covering every
# category task_type_icon() recognizes, plus "Other (custom)" for anything else.
COMMON_TASK_TITLES = [
    "Morning Walk",
    "Afternoon Walk",
    "Evening Walk",
    "Breakfast",
    "Lunch",
    "Dinner",
    "Give Medication",
    "Heartworm Prevention",
    "Vet Appointment",
    "Brush Coat",
    "Wash / Bath",
    "Hair Cut",
    "Trim Nails",
    "Ear Cleaning",
    "Teeth Brushing",
    "Playtime",
]


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
            "Pet": f"{pet_species_icon(pet.species)} {pet.name}",
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
        species = st.selectbox("Species", ["dog", "cat", "bunny", "other"])
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
        submitted_pet = st.form_submit_button("Add pet")

    if submitted_pet and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species, int(age)))
        st.success(f"Added {pet_name.strip()}.")
        st.rerun()

    if owner.pets:
        st.table(
            [
                {
                    "Name": f"{pet_species_icon(pet.species)} {pet.name}",
                    "Species": pet.species,
                    "Age": pet.age,
                }
                for pet in owner.pets
            ]
        )

        pet_to_delete = st.selectbox(
            "Delete a pet",
            owner.pets,
            format_func=lambda pet: f"{pet_species_icon(pet.species)} {pet.name} ({pet.species}, age {pet.age}, {len(pet.tasks)} task(s))",
        )
        if st.button("Delete pet"):
            owner.remove_pet(pet_to_delete)
            st.success(f"Deleted {pet_to_delete.name} and their tasks.")
            st.rerun()

        st.markdown("**Edit a pet**")
        # Select by index and re-fetch owner.pets[i] fresh each run, rather
        # than mutating the object the widget itself returns — st.selectbox
        # isn't guaranteed to hand back the exact same live object across
        # reruns for complex option types, so direct mutation on that
        # returned value can silently edit a throwaway copy instead of the
        # real data.
        edit_pet_index = st.selectbox(
            "Pet to edit",
            range(len(owner.pets)),
            format_func=lambda i: f"{pet_species_icon(owner.pets[i].species)} {owner.pets[i].name}",
            key="edit_pet_select",
        )
        pet_to_edit = owner.pets[edit_pet_index]
        with st.form("edit_pet_form"):
            edited_name = st.text_input("Name", value=pet_to_edit.name)
            species_options = ["dog", "cat", "bunny", "other"]
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
        # Outside the form so picking "Other (custom)" immediately reveals the
        # text field below — widgets inside st.form don't trigger a rerun
        # until the form is submitted, so this couldn't live in there.
        title_choice = st.selectbox("Task title", COMMON_TASK_TITLES + ["Other (custom)"])

        with st.form("add_task_form", clear_on_submit=True):
            selected_pet = st.selectbox(
                "Pet", owner.pets, format_func=lambda pet: f"{pet_species_icon(pet.species)} {pet.name}"
            )
            custom_title = (
                st.text_input("Custom task title")
                if title_choice == "Other (custom)"
                else None
            )

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

        if submitted_task:
            title = (custom_title or "").strip() if title_choice == "Other (custom)" else title_choice
            if title:
                hour_24 = hour_12 % 12
                if period == "PM":
                    hour_24 += 12
                selected_pet.add_task(
                    Task(
                        title=title,
                        time=f"{hour_24:02d}:{minute}",
                        duration_minutes=int(duration),
                        priority=priority,
                        frequency=frequency,
                    )
                )
                st.success(f"Added {title} for {selected_pet.name}.")
                st.rerun()

    all_tasks_for_edit = scheduler.sort_by_time(scheduler.filter_tasks())
    if all_tasks_for_edit:
        st.markdown("**Edit a task**")
        # Same index-based approach as "Edit a pet", for the same reason:
        # re-fetch the live (pet, task) pair fresh each run instead of
        # trusting the widget to return the same live object.
        edit_task_index = st.selectbox(
            "Task to edit",
            range(len(all_tasks_for_edit)),
            format_func=lambda i: f"{pet_species_icon(all_tasks_for_edit[i][0].species)} {all_tasks_for_edit[i][0].name} | {task_type_icon(all_tasks_for_edit[i][1].title)} {all_tasks_for_edit[i][1].title}",
            key="edit_task_select",
        )
        edit_pet, edit_task = all_tasks_for_edit[edit_task_index]

        # Outside the form for the same reason as "Schedule a Task": picking
        # "Other (custom)" needs to immediately reveal the text field below.
        edit_title_choice = st.selectbox(
            "Task",
            COMMON_TASK_TITLES + ["Other (custom)"],
            index=COMMON_TASK_TITLES.index(edit_task.title)
            if edit_task.title in COMMON_TASK_TITLES
            else len(COMMON_TASK_TITLES),
            key="edit_task_title_choice",
        )

        with st.form("edit_task_form"):
            edit_custom_title = (
                st.text_input(
                    "Custom task title", value=edit_task.title, key="edit_custom_title"
                )
                if edit_title_choice == "Other (custom)"
                else None
            )

            st.write("Time")
            current_hour, current_minute = map(int, edit_task.time.split(":"))
            current_period = "AM" if current_hour < 12 else "PM"
            current_hour_12 = current_hour % 12 or 12
            minute_options = ["00", "15", "30", "45"]
            current_minute_str = f"{current_minute:02d}"

            edit_hour_col, edit_minute_col, edit_period_col = st.columns(3)
            with edit_hour_col:
                edit_hour_12 = st.selectbox(
                    "Hour",
                    list(range(1, 13)),
                    index=current_hour_12 - 1,
                    label_visibility="collapsed",
                    key="edit_hour",
                )
            with edit_minute_col:
                edit_minute = st.selectbox(
                    "Minute",
                    minute_options,
                    index=minute_options.index(current_minute_str)
                    if current_minute_str in minute_options
                    else 0,
                    label_visibility="collapsed",
                    key="edit_minute",
                )
            with edit_period_col:
                edit_period = st.selectbox(
                    "AM/PM",
                    ["AM", "PM"],
                    index=0 if current_period == "AM" else 1,
                    label_visibility="collapsed",
                    key="edit_period",
                )

            edit_duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=240,
                value=edit_task.duration_minutes,
                key="edit_duration",
            )
            priority_options = ["high", "medium", "low"]
            edit_priority = st.selectbox(
                "Priority",
                priority_options,
                index=priority_options.index(edit_task.priority),
                key="edit_priority",
            )
            frequency_options = ["once", "daily", "weekly"]
            edit_frequency = st.selectbox(
                "Frequency",
                frequency_options,
                index=frequency_options.index(edit_task.frequency),
                key="edit_frequency",
            )
            submitted_task_edit = st.form_submit_button("Save task changes")

        if submitted_task_edit:
            new_title = (
                (edit_custom_title or "").strip()
                if edit_title_choice == "Other (custom)"
                else edit_title_choice
            )
            if new_title:
                new_hour_24 = edit_hour_12 % 12
                if edit_period == "PM":
                    new_hour_24 += 12
                edit_task.title = new_title
                edit_task.time = f"{new_hour_24:02d}:{edit_minute}"
                edit_task.duration_minutes = int(edit_duration)
                edit_task.priority = edit_priority
                edit_task.frequency = edit_frequency
                st.success(f"Updated {edit_task.title} for {edit_pet.name}.")
                st.rerun()

st.divider()
st.subheader("Today's Highlights")

completed_filter = None
if status_filter == "Open":
    completed_filter = False
elif status_filter == "Done":
    completed_filter = True

pet_name = None if pet_filter == "All pets" else pet_filter
today = date.today()
todays_tasks = scheduler.sort_by_time(
    [
        pair
        for pair in scheduler.filter_tasks(pet_name=pet_name, completed=completed_filter)
        if pair[1].due_date == today
    ]
)

st.markdown("**📅 Today's Schedule**")
if todays_tasks:
    st.table(task_rows(todays_tasks))
else:
    st.info("No tasks due today match the current filters.")

st.markdown("**❗ High Priority First**")
high_priority_today = scheduler.sort_by_priority_then_time(todays_tasks)
if high_priority_today:
    st.table(task_rows(high_priority_today))
else:
    st.info("No tasks due today match the current filters.")

st.markdown("**🚨 Next Urgent Task**")
urgent = scheduler.next_urgent_task(todays_tasks)
if urgent:
    st.table(task_rows([urgent]))
else:
    st.info("No tasks due today match the current filters.")

st.markdown("**⭐ Today's Top 3 Priorities**")
top_priorities = scheduler.top_priorities(3, todays_tasks)
if top_priorities:
    st.table(task_rows(top_priorities))
else:
    st.info("No tasks due today match the current filters.")

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
    if open_tasks:
        selected_open_pair = st.selectbox(
            "Open task",
            open_tasks,
            format_func=lambda pair: f"{pet_species_icon(pair[0].species)} {pair[0].name} | {task_type_icon(pair[1].title)} {pair[1].title}",
        )
        if st.button("Mark complete"):
            open_pet, open_task = selected_open_pair
            scheduler.mark_task_complete(open_pet.name, open_task.title)
            st.success(f"Completed {open_task.title}.")
            st.rerun()
    else:
        st.info("All tasks are complete.")

    st.subheader("Delete or Reopen a Task")
    all_tasks = scheduler.sort_by_time(scheduler.filter_tasks())
    if all_tasks:
        selected_task_pair = st.selectbox(
            "Task",
            all_tasks,
            format_func=lambda pair: f"{pet_species_icon(pair[0].species)} {pair[0].name} | {task_type_icon(pair[1].title)} {pair[1].title} ({'Done' if pair[1].completed else 'Open'})",
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
