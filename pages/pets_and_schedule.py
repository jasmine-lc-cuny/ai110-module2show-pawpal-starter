import streamlit as st

from pawpal_system import Pet, Task, pet_species_icon, task_type_icon
from app_common import (
    COMMON_TASK_TITLES,
    get_owner,
    get_scheduler,
    render_owner_switcher,
    save_owner,
)

render_owner_switcher()
owner = get_owner()
scheduler = get_scheduler()

st.title("🐾 My Pets & Schedule")
st.caption("Add and manage pets, and schedule and edit tasks. See today's full schedule under Manage.")

owner.name = st.sidebar.text_input("Owner name", value=owner.name)

left, right = st.columns([1, 2])

with left:
    st.subheader("Pets")
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "bunny", "other"])
        sex = st.selectbox("Sex", ["Female", "Male"], key="add_pet_sex")
        age = st.number_input("Age", min_value=0, max_value=40, value=1)
        submitted_pet = st.form_submit_button("Add pet")

    if submitted_pet and pet_name.strip():
        owner.add_pet(Pet(pet_name.strip(), species, int(age), sex))
        st.success(f"Added {pet_name.strip()}.")
        st.rerun()

    if owner.pets:
        st.table(
            [
                {
                    "Name": f"{pet_species_icon(pet.species)} {pet.name}",
                    "Species": pet.species,
                    "Sex": pet.sex or "—",
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
            sex_options = ["Female", "Male"]
            edited_sex = st.selectbox(
                "Sex",
                sex_options,
                index=sex_options.index(pet_to_edit.sex)
                if pet_to_edit.sex in sex_options
                else 0,
                key="edit_pet_sex",
            )
            edited_age = st.number_input(
                "Age", min_value=0, max_value=40, value=pet_to_edit.age or 0
            )
            submitted_edit = st.form_submit_button("Save changes")

        if submitted_edit and edited_name.strip():
            pet_to_edit.name = edited_name.strip()
            pet_to_edit.species = edited_species
            pet_to_edit.sex = edited_sex
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
            # Index-based, then re-fetch owner.pets[i] fresh — same reasoning
            # as "Edit a pet"/"Edit a task" below: st.selectbox() isn't
            # guaranteed to hand back the same live object across reruns, and
            # selected_pet.add_task(...) mutates a list on that object, so a
            # copy would silently lose the new task.
            selected_pet_index = st.selectbox(
                "Pet",
                range(len(owner.pets)),
                format_func=lambda i: f"{pet_species_icon(owner.pets[i].species)} {owner.pets[i].name}",
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
                selected_pet = owner.pets[selected_pet_index]
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

save_owner(owner)
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
