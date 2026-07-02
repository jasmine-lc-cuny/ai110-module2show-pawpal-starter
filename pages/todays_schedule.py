from datetime import date

import streamlit as st

from pawpal_system import pet_species_icon, task_type_icon
from app_common import get_owner, get_scheduler, render_owner_switcher, save_owner, task_rows

render_owner_switcher()
owner = get_owner()
scheduler = get_scheduler()

st.title("📅 Today's Schedule")
st.caption("See today's schedule, priorities, and conflicts, and complete, delete, or reopen tasks.")

pet_filter = st.sidebar.selectbox(
    "Filter by pet",
    ["All pets"] + [pet.name for pet in owner.pets],
)
status_filter = st.sidebar.selectbox("Filter by status", ["Open", "Done", "All"])

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

st.subheader("📅 Today's Schedule")
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
        # Index-based, then re-fetch all_tasks[i] fresh right before each
        # mutation — mark_incomplete() and remove_task() both need the real
        # live pet/task objects, not whatever copy the widget returns.
        selected_task_index = st.selectbox(
            "Task",
            range(len(all_tasks)),
            format_func=lambda i: f"{pet_species_icon(all_tasks[i][0].species)} {all_tasks[i][0].name} | {task_type_icon(all_tasks[i][1].title)} {all_tasks[i][1].title} ({'Done' if all_tasks[i][1].completed else 'Open'})",
        )
        preview_pet, preview_task = all_tasks[selected_task_index]

        col1, col2 = st.columns(2)
        with col1:
            if preview_task.completed and st.button("Reopen task"):
                _, task_to_reopen = all_tasks[selected_task_index]
                task_to_reopen.mark_incomplete()
                st.success(f"Reopened {task_to_reopen.title}.")
                st.rerun()
        with col2:
            if st.button("Delete task"):
                pet_to_edit_tasks, task_to_delete = all_tasks[selected_task_index]
                pet_to_edit_tasks.remove_task(task_to_delete)
                st.success(f"Deleted {task_to_delete.title}.")
                st.rerun()
    else:
        st.info("No tasks yet.")

save_owner(owner)
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
