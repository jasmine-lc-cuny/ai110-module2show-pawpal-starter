"""Shared state and UI helpers used across every page of the multi-page app."""

import re
import uuid
from datetime import date
from pathlib import Path

import streamlit as st

from constants import (
    A_LA_BARK_MENU,
    APPOINTMENT_STATUS_COLORS,
    CATEGORY_TASK_TITLES,
    CATEGORY_TO_SECTION,
    COMMON_SERVICES,
    COMMON_TASK_TITLES,
    DOCUMENT_CATEGORIES,
    INJECTION_MEDICATION_CATEGORIES,
    INJECTION_MEDICATION_OPTIONS,
    INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES,
    NEW_OWNER_CHOICE,
    PAGE_BANNERS,
    PET_TIMELINE_COLORS,
    SERVICE_CATEGORY_ICONS,
    SERVICE_SECTIONS,
    VETERINARY_TASK_REASONS,
    VETERINARY_TASK_REASONS_BY_SPECIES,
)
from pawpal_system import (
    Clinic,
    Document,
    Owner,
    Pet,
    Scheduler,
    Task,
    format_time_12h,
    load_owners_from_json,
    pet_species_icon,
    priority_icon,
    task_type_icon,
)
from state import (
    ensure_demo_data,
    get_clinic,
    get_combined_owner,
    get_owners,
    get_scheduler,
    save_clinic,
    save_owner,
    save_owners,
)
from ui_helpers import render_live_clock, render_page_banner

# ==========================================
# 📎 FILE UPLOAD UTILITIES
# ==========================================

def slugify_for_path(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "unnamed"

def save_uploaded_document(owner: Owner, pet: Pet, category: str, uploaded_file) -> Document:
    pet_dir = UPLOADS_PATH / f"{slugify_for_path(owner.name)}__{slugify_for_path(pet.name)}"
    pet_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
    stored_path = pet_dir / stored_name
    with open(stored_path, "wb") as file:
        file.write(uploaded_file.getbuffer())
    return Document(category=category, filename=uploaded_file.name, path=str(stored_path))

def delete_uploaded_document(document: Document) -> None:
    Path(document.path).unlink(missing_ok=True)

# ==========================================
# 🏷️ UI FORMATTERS & DATA PARSERS
# ==========================================

def pet_label(pet: Pet, owners: list[Owner]) -> str:
    return f"{pet_species_icon(pet.species)} {pet.name} ({pet.species})"

def task_pair_label(index: int, pet: Pet, task: Task, owners: list[Owner]) -> str:
    owner_name = next((o.name for o in owners if pet in o.pets), "Unknown")
    return (
        f"{index + 1}. {pet_species_icon(pet.species)} {pet.name} ({owner_name}) | {task_type_icon(task.title)} {task.title} "
        f"@ {format_time_12h(task.time)}"
    )

def task_rows(task_pairs):
    return [
        {
            "Type": task_type_icon(task.title),
            "Time": format_time_12h(task.time),
            "Pet": f"{pet_species_icon(pet.species)} {pet.name}",
            "Species": pet.species,
            "Task": task.title,
            "Reason": task.notes or "—",
            "Assigned To": task.assignee or "—",
            "Duration": task.duration_minutes,
            "Priority": f"{priority_icon(task.priority)} {task.priority}",
            "Frequency": task.frequency,
            "Due Date": task.due_date.isoformat(),
            "Status": "✅ Done" if task.completed else "⏳ Open",
        }
        for pet, task in task_pairs
    ]

def tasks_in_category(owner: Owner, category: str):
    # An explicit task.category (set when booked) wins; tasks created before
    # that field existed (category is None) fall back to matching the title's
    # icon against the category's icon set.
    icons = SERVICE_CATEGORY_ICONS.get(category, set())
    return [
        (pet, task)
        for pet, task in owner.all_tasks()
        if task.category == category
        or (task.category is None and task_type_icon(task.title) in icons)
    ]

# ==========================================
# 🎛️ CUSTOM SUB-MENU PICKERS
# ==========================================

def render_veterinary_reason_picker(title: str, species: str, key_prefix: str = "vet") -> str | None:
    species_key = species.lower()

    if title == "Injection Medication":
        category = st.selectbox("Medication Category", INJECTION_MEDICATION_CATEGORIES, key=f"{key_prefix}_med_category")
        if category == "Pain & Arthritis Management":
            medication_options = INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES.get(species_key, INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES["dog"])
        else:
            medication_options = INJECTION_MEDICATION_OPTIONS[category]
        return st.selectbox("Medication", medication_options, key=f"{key_prefix}_med_select_{category}")

    if title in VETERINARY_TASK_REASONS_BY_SPECIES:
        species_options = VETERINARY_TASK_REASONS_BY_SPECIES[title].get(species_key, VETERINARY_TASK_REASONS_BY_SPECIES[title]["dog"])
        return st.selectbox("Reason", species_options, key=f"{key_prefix}_reason_select_{title}")

    if title in VETERINARY_TASK_REASONS:
        return st.selectbox("Reason", VETERINARY_TASK_REASONS[title], key=f"{key_prefix}_reason_select_{title}")

    return None

def _render_dog_cafe_menu_picker() -> str:
    section_index = st.selectbox(
        "Menu", range(len(A_LA_BARK_MENU)), format_func=lambda i: A_LA_BARK_MENU[i][0], key="dog_cafe_menu_section"
    )
    section_name, tagline, items = A_LA_BARK_MENU[section_index]
    item_labels = [f"{name} ({price})" for name, price, _ in items]
    item_index = st.selectbox(
        "Menu Item", range(len(items)), format_func=lambda i: item_labels[i], key=f"dog_cafe_menu_item_{section_index}"
    )
    st.caption(items[item_index][2])
    return item_labels[item_index]

# ==========================================
# 🏗️ MAIN CATEGORY PAGE BUILDER (THE ENGINE)
# ==========================================

def render_category_header(category: str, display_name: str, icon: str, page_title: str | None = None) -> None:
    """Render the title, clock, banner, and queued alerts for a category page."""
    st.title(page_title if page_title else f"{icon} {display_name}")
    render_live_clock(f"{display_name} view")
    render_page_banner(category)

    if "ui_alert_success" in st.session_state:
        st.success(st.session_state.pop("ui_alert_success"))
    if "ui_alert_warning" in st.session_state:
        st.warning(st.session_state.pop("ui_alert_warning"))


def render_category_filters(category: str, display_name: str, owner: Owner, title_options: list[str]):
    """Render the page filters and return whether the booking form is open."""
    if not owner.pets:
        st.warning("Add a pet before scheduling tasks here.")
        st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
        return None
    if not title_options:
        st.info(f"{display_name} isn't wired up to specific task types yet.")
        return None

    toggle_key = f"show_booking_form_{category}"
    if toggle_key not in st.session_state:
        st.session_state[toggle_key] = False

    if st.session_state[toggle_key]:
        if st.button("🔼 Hide booking form", key=f"{category}_hide_schedule"):
            st.session_state[toggle_key] = False
            st.rerun()
    else:
        if st.button(f"➕ Book {display_name}", key=f"{category}_show_schedule", use_container_width=True):
            st.session_state[toggle_key] = True
            st.rerun()

    if category == "veterinary":
        pet_categories = {
            "🐶 General Companion": ["dog", "cat"],
            "🐹 Exotic Small Pet": ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig", "ferret", "hedgehog", "sugar glider", "squirrel"],
            "🦜 Exotic Avian": ["budgie", "canary", "finch", "parrot", "cockatiel", "conure", "chicken", "duck", "goose", "pigeon", "owl", "falcon", "snowy owl"],
            "🦎 Reptiles & Amphibians": ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "turtle", "tortoise", "corn snake", "ball python", "king snake", "frog", "toad", "newt", "salamander"],
            "🐠 Fish & Invertebrates": ["betta", "guppy", "platy", "swordtail", "molly", "tetra", "goldfish", "danio", "minnow", "cichlid", "pleco", "clownfish", "damselfish", "goby", "blenny"],
        }
        group_options = ["All Groups"] + list(pet_categories.keys())
        selected_group = st.radio("Filter by Species Group", options=group_options, horizontal=True, key=f"{category}_group_filter")
        if selected_group == "All Groups":
            allowed_species = None
        else:
            raw_species_list = pet_categories[selected_group]
            species_options = ["All"] + [f"{pet_species_icon(s)} {s.capitalize()}" for s in raw_species_list]
            selected_species_label = st.radio("Filter by Species", options=species_options, horizontal=True, key=f"{category}_species_filter")
            if selected_species_label == "All":
                allowed_species = raw_species_list
            else:
                target = selected_species_label.split(" ", 1)[-1].lower()
                allowed_species = [target]
    else:
        species_filter = st.radio(
            "Filter by Species",
            ["All (Dogs & Cats)", "🐕 Dogs", "🐈 Cats"],
            horizontal=True,
            key=f"{category}_species_filter"
        )
        filter_map = {"🐕 Dogs": "dog", "🐈 Cats": "cat"}
        target_species = filter_map.get(species_filter)
        allowed_species = [target_species] if target_species else ["dog", "cat"]

    owners_with_pets = []
    for candidate in get_owners():
        if candidate.pets and any(allowed_species is None or pet.species.lower() in allowed_species for pet in candidate.pets):
            owners_with_pets.append(candidate)

    if f"{category}_owner_index_state" not in st.session_state or st.session_state[f"{category}_owner_index_state"] >= len(owners_with_pets):
        st.session_state[f"{category}_owner_index_state"] = 0

    if not owners_with_pets:
        st.info("No owners currently have a pet matching this filter.")
        return None

    selected_owner = owners_with_pets[st.session_state[f"{category}_owner_index_state"]]
    filtered_pets = [(i, pet) for i, pet in enumerate(selected_owner.pets) if allowed_species is None or pet.species.lower() in allowed_species]
    pet_labels = [f"{i + 1}. {pet_species_icon(pet.species)} {pet.name} ({pet.species})" for i, pet in filtered_pets]
    owner_labels = [f"{i + 1}. {candidate.name}" for i, candidate in enumerate(owners_with_pets)]

    col1, col2 = st.columns(2)
    with col1:
        selected_owner_index = st.selectbox("Owner", range(len(owners_with_pets)), format_func=lambda i: owner_labels[i], key=f"{category}_owner_select")
        if selected_owner_index != st.session_state[f"{category}_owner_index_state"]:
            st.session_state[f"{category}_owner_index_state"] = selected_owner_index
            st.rerun()

    filter_state_key = "_".join(allowed_species) if allowed_species else "all"
    with col2:
        selected_filtered_index = st.selectbox(
            "Pet",
            range(len(filtered_pets)),
            format_func=lambda i: pet_labels[i],
            key=f"{category}_pet_select_{st.session_state[f'{category}_owner_index_state']}_{filter_state_key}",
        )
        selected_pet_index = filtered_pets[selected_filtered_index][0]

    return selected_owner, selected_pet_index, allowed_species, st.session_state[toggle_key]

def render_category_booking_form(category: str, display_name: str, active_staff, selected_owner, selected_pet_index):
    """Render the task booking form and handle task creation."""
    title_options = CATEGORY_TASK_TITLES.get(category, [])
    if not title_options:
        return

    if category == "veterinary":
        title = st.selectbox("Task", title_options, key=f"{category}_title_select")
        selected_species = selected_owner.pets[selected_pet_index].species
        reason = render_veterinary_reason_picker(title, selected_species, key_prefix=category)
    elif category == "special_services":
        title = st.selectbox("Task", title_options, key=f"{category}_title_select")
        reason = _render_dog_cafe_menu_picker()
    else:
        title = st.selectbox("Task", title_options, key=f"{category}_title_select")
        st.text_input("Reason", value="—", disabled=True, key=f"{category}_disabled_reason")
        reason = None

    with st.form(f"add_{category}_task_form", clear_on_submit=True):
        date_col, staff_col = st.columns(2)
        with date_col:
            appt_date = st.date_input("Date", value=date.today(), key=f"{category}_date")
        with staff_col:
            if active_staff:
                staff_labels = [
                    f"{member.full_name} ({member.role})" if member.role else member.full_name
                    for member in active_staff
                ]
                staff_index = st.selectbox("Assigned staff", range(len(active_staff)), format_func=lambda i: staff_labels[i], key=f"{category}_staff_select")
            else:
                staff_index = None
                st.caption("No active staff in this section — add some on the Staff page.")

        st.write("Time")
        hour_col, minute_col, period_col = st.columns(3)
        with hour_col:
            hour_12 = st.selectbox("Hour", list(range(1, 13)), index=7, label_visibility="collapsed")
        with minute_col:
            minute = st.selectbox("Minute", ["00", "15", "30", "45"], label_visibility="collapsed")
        with period_col:
            period = st.selectbox("AM/PM", ["AM", "PM"], label_visibility="collapsed")

        if category == "special_services":
            duration, priority, frequency = 60, "medium", "once"
            submitted = st.form_submit_button("Dog Cafe RSVP")
        else:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            priority = st.selectbox("Priority", ["high", "medium", "low"])
            frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
            submitted = st.form_submit_button(f"Add {display_name} task")

    if submitted:
        hour_24 = hour_12 % 12
        if period == "PM":
            hour_24 += 12
        time_str = f"{hour_24:02d}:{minute}"
        selected_pet = selected_owner.pets[selected_pet_index]
        assignee = active_staff[staff_index].full_name if staff_index is not None else None
        conflict = any(t.time == time_str and t.due_date == appt_date and not t.completed for t in selected_pet.tasks)
        if conflict:
            st.session_state["ui_alert_warning"] = f"⚠️ Schedule Conflict: {selected_pet.name} already has a task scheduled at {time_str} on {appt_date.isoformat()}. Double-booking detected!"

        selected_pet.add_task(
            Task(
                title=title,
                time=time_str,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                notes=reason,
                due_date=appt_date,
                category=category,
                assignee=assignee,
            )
        )
        save_owner(get_combined_owner())
        success_message = f"Added {title} for {selected_pet.name}."
        if reason:
            success_message = f"Added {title} ({reason}) for {selected_pet.name}."
        st.session_state["ui_alert_success"] = success_message
        st.rerun()


def render_category_schedule(category: str, display_name: str, category_tasks):
    """Render the task table, completion actions, and schedule footer."""
    st.divider()
    st.subheader(f"{display_name} Schedule")
    if category_tasks:
        st.table(task_rows(category_tasks))
    else:
        st.info(f"No {display_name.lower()} tasks yet.")

    open_category_tasks = [pair for pair in category_tasks if not pair[1].completed]
    if open_category_tasks:
        st.subheader("Complete a Task")
        complete_labels = [task_pair_label(i, pet, task, get_owners()) for i, (pet, task) in enumerate(open_category_tasks)]
        complete_index = st.selectbox("Open task", range(len(open_category_tasks)), format_func=lambda i: complete_labels[i], key=f"{category}_complete_select")
        if st.button("Mark complete", key=f"{category}_complete_button"):
            complete_pet, complete_task = open_category_tasks[complete_index]
            complete_task.mark_complete()
            next_task = complete_task.next_occurrence(completed_on=date.today())
            msg = f"Completed {complete_task.title}."
            if next_task is not None:
                complete_pet.add_task(next_task)
                msg += " 🔁 New recurring task automatically generated for next time!"
            save_owner(get_combined_owner())
            st.session_state["ui_alert_success"] = msg
            st.rerun()

    st.caption("Completing, deleting, and reopening tasks lives on \"Today's Schedule\".")


def render_category_page(
    category: str,
    display_name: str,
    icon: str,
    page_title: str | None = None,
    page_subtitle: str | None = None,
) -> None:
    owner = get_combined_owner()
    scheduler = get_scheduler()
    section = CATEGORY_TO_SECTION.get(category)
    active_staff = [member for member in get_clinic().staff_in_section(section) if member.active] if section else []

    render_category_header(category, display_name, icon, page_title)
    today = date.today()
    category_tasks = scheduler.sort_by_time(
        [
            (pet, task)
            for pet, task in tasks_in_category(owner, category)
            if task.due_date == today and "07:00" <= task.time <= "20:00"
        ]
    )
    title_options = CATEGORY_TASK_TITLES.get(category, [])
    selection = render_category_filters(category, display_name, owner, title_options)
    if selection is None:
        return

    selected_owner, selected_pet_index, _allowed_species, show_booking_form = selection
    if page_subtitle:
        st.subheader(page_subtitle)

    if show_booking_form:
        st.subheader(f"Schedule a {display_name} Task")
        render_category_booking_form(category, display_name, active_staff, selected_owner, selected_pet_index)
    render_category_schedule(category, display_name, category_tasks)
def render_placeholder_page(display_name: str, icon: str) -> None:
    st.title(f"{icon} {display_name}")
    render_live_clock(f"{display_name} placeholder")
    st.info(
        f"{display_name} isn't wired up to specific task types yet — this page "
        "is a placeholder for a future update."
    )
