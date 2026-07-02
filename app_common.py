"""Shared state and UI helpers used across every page of the multi-page app."""

import re
import uuid
from pathlib import Path

import streamlit as st

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
    save_owners_to_json,
    task_type_icon,
)

DATA_PATH = Path("data.json")
CLINIC_DATA_PATH = Path("clinic.json")
UPLOADS_PATH = Path("uploads")
NEW_OWNER_CHOICE = "+ Add new owner"

# st.badge() color per Appointment.status, matching the mockup's palette.
APPOINTMENT_STATUS_COLORS = {
    "Pending": "yellow",
    "Confirmed": "blue",
    "Completed": "green",
    "Cancelled": "red",
}

# Categories offered when uploading a Document, mirroring the mockup's
# document groupings.
DOCUMENT_CATEGORIES = [
    "Digital radiography",
    "Dental digital x-ray",
    "In-house laboratory diagnostics",
    "Other",
]

# Colors for the weekly-schedule timeline, assigned by a pet's index in
# owner.pets (not a name hash) so the mapping is deterministic and never
# collides. Chosen for contrast against white pill text.
PET_TIMELINE_COLORS = [
    "#3B5BDB",  # indigo
    "#099268",  # teal
    "#E8590C",  # orange
    "#C2255C",  # pink
    "#6741D9",  # violet
    "#0C8599",  # cyan
    "#E03131",  # red
    "#5C940D",  # lime
]

# Common care tasks offered in "Schedule a Task" dropdowns, covering every
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
    "X-Ray",
    "Injection Medication",
    "Injection Vaccine",
    "Injection Subcutaneous",
    "Injection Intramuscular",
    "Injection Intravenous",
    "Blood Work",
    "Surgery",
    "Brush Coat",
    "Wash / Bath",
    "Hair Cut",
    "Trim Nails",
    "Ear Cleaning",
    "Teeth Brushing",
    "Playtime",
]

# Extra "Reason" sub-options offered on the veterinary quick-add form for
# task titles vets naturally subdivide further, stored on Task.notes. Not
# every title has one — only these get a second picker after "Task". Each
# injection route lists what's actually administered that way (including
# things like chemotherapy) rather than just describing the route itself.
VETERINARY_TASK_REASONS = {
    "Give Medication": ["Heartworm Prevention", "Antibiotics"],
    "X-Ray": ["Hip"],
    "Blood Work": [
        "Complete Blood Count (CBC)",
        "Serum Chemistry",
        "Thyroid Panel",
        "Electrolyte Panel",
        "Pre-Anesthetic Panel",
        "Coagulation Profile",
    ],
    "Injection Subcutaneous": [
        "Routine Vaccines",
        "Maintenance Medications (e.g. Insulin)",
        "Fluid Therapy",
    ],
    "Injection Intramuscular": [
        "Pain Management",
        "Sedatives and Tranquilizers",
        "Antibiotics",
    ],
    "Injection Intravenous": [
        "General Anesthesia",
        "Emergency Medications",
        "Chemotherapy",
        "Continuous Fluid Therapy",
    ],
}

# Some reasons differ by the pet's species (which vaccine, which surgery);
# falls back to the "dog" list for any species without its own entry.
VETERINARY_TASK_REASONS_BY_SPECIES = {
    "Injection Vaccine": {
        "dog": ["Rabies", "Distemper", "Parvovirus", "Adenovirus"],
        "cat": ["Rabies", "Panleukopenia", "Calicivirus", "Herpesvirus"],
    },
    "Surgery": {
        "dog": [
            "Neuter",
            "Dental Extractions",
            "Mass/Tumor Removals",
            "Gastrointestinal Surgeries",
            "Exploratory Laparotomy",
            "C-Section",
        ],
        "cat": [
            "Spay",
            "Dental Extractions",
            "Mass/Tumor Removals",
            "Gastrointestinal Surgeries",
            "Exploratory Laparotomy",
            "C-Section",
        ],
    },
}

# "Injection Medication" gets its own two-step picker (Category, then the
# specific long-/fast-acting injectable) rather than one flat list, since a
# named brand-name medication makes more sense grouped by what it treats.
INJECTION_MEDICATION_CATEGORIES = [
    "Pain & Arthritis Management",
    "Flea, Tick, & Allergy Relief",
    "Antibiotics & General Treatment",
]

# Pain & arthritis injectables differ by species (Librela/Adequan Canine are
# dog-specific, Solensia is cat-specific); falls back to "dog" for any
# species without its own entry, same convention as VETERINARY_TASK_REASONS_BY_SPECIES.
INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES = {
    "dog": [
        "Librela (bedinvetmab)",
        "Adequan Canine (polysulfated glycosaminoglycan)",
    ],
    "cat": ["Solensia (frunevetmab)"],
}

# These two categories aren't species-split in practice, so they stay flat.
INJECTION_MEDICATION_OPTIONS = {
    "Flea, Tick, & Allergy Relief": ["Bravecto Quantum", "Cytopoint"],
    "Antibiotics & General Treatment": [
        "Convenia (cefovecin sodium)",
        "Injectable Insulin (Vetsulin or ProZinc)",
    ],
}

# Common clinic services offered in the "Service" dropdown on the Services
# page, each with a typical default cost that pre-fills (but doesn't lock)
# the Cost field — same "pick a common one, or Other (custom)" pattern as
# COMMON_TASK_TITLES.
COMMON_SERVICES = [
    ("Blood Work", 45.0),
    ("X-Ray", 100.0),
    ("Injection Medication", 25.0),
    ("Surgery", 500.0),
    ("Vaccination", 30.0),
    ("Dental Cleaning", 80.0),
    ("Spay/Neuter", 250.0),
]

# Which task_type_icon() emoji belong to each "Book a Service" category.
# Feeding (🍖) and anything task_type_icon() can't categorize (🐾) don't have
# an obvious home among the 6 categories, so they land under Special
# Services. Sitting and Training have no matching task types yet — their
# pages are placeholders until tasks like "Boarding" or "Training Session"
# get added to COMMON_TASK_TITLES and TASK_TYPE_ICONS.
SERVICE_CATEGORY_ICONS = {
    "grooming": {"👂", "🦷", "💅", "✂️", "🧼", "🪮"},
    "walking": {"🐕"},
    "veterinary": {"💊", "🏥"},
    "special_services": {"🍖", "🐾"},
}

# Title-dropdown options offered on each category's "quick add" form —
# a subset of COMMON_TASK_TITLES relevant to that specific category.
CATEGORY_TASK_TITLES = {
    "grooming": ["Brush Coat", "Wash / Bath", "Hair Cut", "Trim Nails", "Ear Cleaning", "Teeth Brushing"],
    "walking": ["Morning Walk", "Afternoon Walk", "Evening Walk", "Playtime"],
    "veterinary": [
        "Give Medication",
        "Heartworm Prevention",
        "Vet Appointment",
        "X-Ray",
        "Injection Medication",
        "Injection Vaccine",
        "Injection Subcutaneous",
        "Injection Intramuscular",
        "Injection Intravenous",
        "Blood Work",
        "Surgery",
    ],
    "special_services": ["Breakfast", "Lunch", "Dinner"],
}


def get_owners() -> list[Owner]:
    """Return every owner in this session (e.g. different customers, each
    with their own pets/tasks), loading them from data.json once if needed."""
    if "owners" not in st.session_state:
        if DATA_PATH.exists():
            st.session_state.owners = load_owners_from_json(str(DATA_PATH))
        else:
            st.session_state.owners = [Owner("Jordan")]
        st.session_state.current_owner_index = 0
    return st.session_state.owners


def render_owner_switcher() -> None:
    """Render the sidebar "Owner" picker. Call this exactly once near the top
    of each page, before get_owner()/get_scheduler() — calling it twice in
    the same run would register the same widget key twice and crash.

    Without this, every pet/task ever added lands in one shared owner
    record no matter whose name was typed into "Owner name", which is why
    two different customers' pets used to show up mixed together.
    """
    owners = get_owners()

    st.sidebar.subheader("Owner")
    # Only pass index= on the very first render for this key. Once
    # "owner_switcher" exists in session_state (set either by the user
    # picking an option or by _create_owner()'s callback), Streamlit uses
    # that value and warns if index= is passed alongside it.
    index_kwargs = {}
    if "owner_switcher" not in st.session_state:
        current_index = st.session_state.current_owner_index
        index_kwargs["index"] = current_index if current_index < len(owners) else 0

    choice = st.sidebar.selectbox(
        "Current owner",
        list(range(len(owners))) + [NEW_OWNER_CHOICE],
        format_func=lambda option: owners[option].name if isinstance(option, int) else option,
        key="owner_switcher",
        **index_kwargs,
    )

    if choice == NEW_OWNER_CHOICE:
        st.sidebar.text_input("New owner name", key="new_owner_name")
        # Mutating st.session_state["owner_switcher"] must happen in a
        # callback (run by Streamlit before the script re-executes) — doing
        # it inline here, after the selectbox above already instantiated
        # that key this run, raises StreamlitAPIException.
        st.sidebar.button("Create owner", key="create_owner_button", on_click=_create_owner, args=(owners,))
    else:
        st.session_state.current_owner_index = choice


def _create_owner(owners: list[Owner]) -> None:
    """Callback for the "Create owner" button: add a new owner and switch to them."""
    new_owner_name = st.session_state.get("new_owner_name", "").strip()
    if not new_owner_name:
        return
    owners.append(Owner(new_owner_name))
    new_index = len(owners) - 1
    st.session_state.current_owner_index = new_index
    st.session_state.owner_switcher = new_index
    save_owners(owners)


def get_owner() -> Owner:
    """Return the currently-selected owner. render_owner_switcher() must run
    earlier in the page for the selection to reflect the sidebar."""
    owners = get_owners()
    index = st.session_state.get("current_owner_index", 0)
    if index >= len(owners):
        index = 0
    return owners[index]


def get_scheduler() -> Scheduler:
    """Return a Scheduler for the currently-selected owner."""
    return Scheduler(get_owner())


def save_owners(owners: list[Owner]) -> None:
    """Persist every owner (and their pets/tasks) to data.json."""
    save_owners_to_json(owners, str(DATA_PATH))


def save_owner(owner: Owner) -> None:
    """Persist all owners to data.json — call after any mutation, on every page."""
    save_owners(get_owners())


def get_clinic() -> Clinic:
    """Return this session's Clinic (departments/doctors/services/appointments),
    loading it from clinic.json once if needed. Unlike get_owner(), this is not
    scoped to any single owner — it's shared across every "Veterinarian" page."""
    if "clinic" not in st.session_state:
        if CLINIC_DATA_PATH.exists():
            st.session_state.clinic = Clinic.load_from_json(str(CLINIC_DATA_PATH))
        else:
            st.session_state.clinic = Clinic()
    return st.session_state.clinic


def save_clinic(clinic: Clinic) -> None:
    """Persist the clinic's records to clinic.json — call after any mutation."""
    clinic.save_to_json(str(CLINIC_DATA_PATH))


def slugify_for_path(name: str) -> str:
    """Turn an owner/pet name into a filesystem-safe folder name segment."""
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "unnamed"


def save_uploaded_document(owner: Owner, pet: Pet, category: str, uploaded_file) -> Document:
    """Save an st.file_uploader() file to disk and return a Document referencing it."""
    pet_dir = UPLOADS_PATH / f"{slugify_for_path(owner.name)}__{slugify_for_path(pet.name)}"
    pet_dir.mkdir(parents=True, exist_ok=True)

    # Prefix with a short unique token so repeat uploads of the same
    # filename (e.g. two different "xray.png") never overwrite each other
    # on disk, while Document.filename keeps the original name for display.
    stored_name = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
    stored_path = pet_dir / stored_name
    with open(stored_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return Document(category=category, filename=uploaded_file.name, path=str(stored_path))


def delete_uploaded_document(document: Document) -> None:
    """Remove an uploaded document's file from disk, if it still exists."""
    Path(document.path).unlink(missing_ok=True)


def task_rows(task_pairs):
    """Convert scheduler task pairs into table-friendly dictionaries."""
    return [
        {
            "Type": task_type_icon(task.title),
            "Time": format_time_12h(task.time),
            "Pet": f"{pet_species_icon(pet.species)} {pet.name}",
            "Species": pet.species,
            "Task": task.title,
            "Reason": task.notes or "—",
            "Duration": task.duration_minutes,
            "Priority": task.priority,
            "Frequency": task.frequency,
            "Due Date": task.due_date.isoformat(),
            "Status": "✅ Done" if task.completed else "⏳ Open",
        }
        for pet, task in task_pairs
    ]


def tasks_in_category(owner: Owner, category: str):
    """Return every (pet, task) pair whose task_type_icon() belongs to a service category."""
    icons = SERVICE_CATEGORY_ICONS.get(category, set())
    return [
        (pet, task)
        for pet, task in owner.all_tasks()
        if task_type_icon(task.title) in icons
    ]


def _render_veterinary_reason_picker(title: str, species: str) -> str | None:
    """Show an extra "Reason" sub-picker for veterinary task titles vets
    naturally subdivide further (which vaccine, which blood panel, etc).
    Returns the picked reason (stored on Task.notes), or None if this task
    title has no defined sub-reasons.

    Called with `title`/`species` read from widgets that live outside the
    surrounding st.form, so this picker's own widgets must too — otherwise
    it wouldn't react until the whole form is submitted.
    """
    species_key = species.lower()

    if title == "Injection Medication":
        category = st.selectbox(
            "Medication Category", INJECTION_MEDICATION_CATEGORIES, key="vet_med_category"
        )
        if category == "Pain & Arthritis Management":
            medication_options = INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES.get(
                species_key, INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES["dog"]
            )
        else:
            medication_options = INJECTION_MEDICATION_OPTIONS[category]
        return st.selectbox("Medication", medication_options, key=f"vet_med_select_{category}")

    if title in VETERINARY_TASK_REASONS_BY_SPECIES:
        species_options = VETERINARY_TASK_REASONS_BY_SPECIES[title].get(
            species_key, VETERINARY_TASK_REASONS_BY_SPECIES[title]["dog"]
        )
        return st.selectbox("Reason", species_options, key=f"vet_reason_select_{title}")

    if title in VETERINARY_TASK_REASONS:
        return st.selectbox("Reason", VETERINARY_TASK_REASONS[title], key=f"vet_reason_select_{title}")

    return None


def render_category_page(category: str, display_name: str, icon: str) -> None:
    """Render a full "Book a Service" category page: quick-add form, filtered
    schedule, and a complete-task action, all scoped to this category.

    Full editing/deleting/reopening of any task still lives on the "My Pets
    & Schedule" page rather than being duplicated on every category page.
    """
    render_owner_switcher()
    owner = get_owner()
    scheduler = get_scheduler()

    st.title(f"{icon} {display_name}")

    category_tasks = scheduler.sort_by_time(tasks_in_category(owner, category))
    title_options = CATEGORY_TASK_TITLES.get(category, [])

    if not owner.pets:
        st.warning('Add a pet from "My Pets & Schedule" before scheduling tasks here.')
    elif not title_options:
        st.info(
            f"{display_name} isn't wired up to specific task types yet — "
            'add pets and tasks from "My Pets & Schedule" instead.'
        )
    else:
        st.subheader(f"Schedule a {display_name} Task")

        # Pet and Task live outside the form (like the "Other (custom)"
        # reveal elsewhere) so the veterinary Reason sub-picker below can
        # react immediately to which one is selected — widgets inside
        # st.form don't trigger a rerun until the whole form is submitted.
        # Index-based, then re-fetch owner.pets[i] fresh at submit time —
        # st.selectbox() isn't guaranteed to hand back the same live object
        # across reruns, and add_task() mutates a list on that object, so a
        # copy would silently lose the new task.
        selected_pet_index = st.selectbox(
            "Pet",
            range(len(owner.pets)),
            format_func=lambda i: f"{pet_species_icon(owner.pets[i].species)} {owner.pets[i].name}",
            key=f"{category}_pet_select",
        )
        title = st.selectbox("Task", title_options, key=f"{category}_title_select")

        reason = None
        if category == "veterinary":
            selected_species = owner.pets[selected_pet_index].species
            reason = _render_veterinary_reason_picker(title, selected_species)

        with st.form(f"add_{category}_task_form", clear_on_submit=True):
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
            submitted = st.form_submit_button(f"Add {display_name} task")

        if submitted:
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
                    notes=reason,
                )
            )
            success_message = f"Added {title} for {selected_pet.name}."
            if reason:
                success_message = f"Added {title} ({reason}) for {selected_pet.name}."
            st.success(success_message)
            st.rerun()

    st.divider()
    st.subheader(f"{display_name} Schedule")
    if category_tasks:
        st.table(task_rows(category_tasks))
    else:
        st.info(f"No {display_name.lower()} tasks yet.")

    open_category_tasks = [pair for pair in category_tasks if not pair[1].completed]
    if open_category_tasks:
        st.subheader("Complete a Task")
        selected_pair = st.selectbox(
            "Open task",
            open_category_tasks,
            format_func=lambda pair: f"{pet_species_icon(pair[0].species)} {pair[0].name} | {pair[1].title}",
            key=f"{category}_complete_select",
        )
        if st.button("Mark complete", key=f"{category}_complete_button"):
            complete_pet, complete_task = selected_pair
            scheduler.mark_task_complete(complete_pet.name, complete_task.title)
            st.success(f"Completed {complete_task.title}.")
            st.rerun()

    save_owner(owner)
    st.caption('Full editing, deleting, and reopening tasks lives on "My Pets & Schedule".')


def render_placeholder_page(display_name: str, icon: str) -> None:
    """Render a clearly-labeled "coming soon" page for a service category that
    doesn't have matching task types in TASK_TYPE_ICONS yet."""
    render_owner_switcher()
    st.title(f"{icon} {display_name}")
    st.info(
        f"{display_name} isn't wired up to specific task types yet — this page "
        f'is a placeholder for a future update. In the meantime, you can track '
        f'anything {display_name.lower()}-related as a custom task from '
        f'"My Pets & Schedule".'
    )
    st.page_link("pages/pets_and_schedule.py", label="Go to My Pets & Schedule", icon="🐾")
