from datetime import date

import streamlit as st

from app_common import (
    get_combined_owner,
    get_owners,
    get_scheduler,
    save_owner,
    task_pair_label,
    task_rows,
)

owner = get_combined_owner()
scheduler = get_scheduler()
real_owners = get_owners()

st.title("📅 Today's Schedule")
st.caption("See today's schedule, priorities, and conflicts, and complete, delete, or reopen tasks.")

# Deduplicated: several owners have same-named pets, and the filter matches
# by name anyway (duplicate option labels are also unsafe — see pet_label).
pet_filter = st.sidebar.selectbox(
    "Filter by pet",
    ["All pets"] + sorted({pet.name for pet in owner.pets}),
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
        # Index-based, then re-fetch the live pair before mutating — and
        # mutate that exact task directly rather than going through
        # Scheduler.mark_task_complete()'s pet-name lookup, which could hit
        # the wrong pet now that different owners can have same-named pets.
        # task_pair_label() keeps every option label unique, which Streamlit
        # needs to reliably map the clicked option back to the right index.
        # Labels precomputed into a plain list so the format_func closes over
        # no session state (see pet_label's docstring in app_common).
        open_labels = [
            task_pair_label(i, pet, task, real_owners)
            for i, (pet, task) in enumerate(open_tasks)
        ]
        complete_index = st.selectbox(
            "Open task",
            range(len(open_tasks)),
            format_func=lambda i: open_labels[i],
            key="todays_complete_select",
        )
        if st.button("Mark complete"):
            open_pet, open_task = open_tasks[complete_index]
            open_task.mark_complete()
            next_task = open_task.next_occurrence(completed_on=date.today())
            if next_task is not None:
                open_pet.add_task(next_task)
            save_owner(owner)
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
        all_task_labels = [
            f"{task_pair_label(i, pet, task, real_owners)} ({'Done' if task.completed else 'Open'})"
            for i, (pet, task) in enumerate(all_tasks)
        ]
        selected_task_index = st.selectbox(
            "Task",
            range(len(all_tasks)),
            format_func=lambda i: all_task_labels[i],
            key="todays_task_select",
        )
        preview_pet, preview_task = all_tasks[selected_task_index]

        col1, col2 = st.columns(2)
        with col1:
            if preview_task.completed and st.button("Reopen task"):
                _, task_to_reopen = all_tasks[selected_task_index]
                task_to_reopen.mark_incomplete()
                save_owner(owner)
                st.success(f"Reopened {task_to_reopen.title}.")
                st.rerun()
        with col2:
            if st.button("Delete task"):
                pet_to_edit_tasks, task_to_delete = all_tasks[selected_task_index]
                pet_to_edit_tasks.remove_task(task_to_delete)
                save_owner(owner)
                st.success(f"Deleted {task_to_delete.title}.")
                st.rerun()
    else:
        st.info("No tasks yet.")

# Deliberately no unconditional save here: every mutation above saves inline
# before its st.rerun(). A render-time save would let a stale browser session
# silently overwrite data.json just by sitting open.
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
