"""Shared state and UI helpers used across every page of the multi-page app."""

import re
import uuid
from datetime import date
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
    return st.session_state.owners


def get_combined_owner() -> Owner:
    """Return a synthetic Owner holding every pet across every owner, so the
    schedule/calendar pages show the whole clinic instead of one customer.

    The Pet objects are the same live instances the real owners hold — only
    the wrapping Owner is synthetic — so reads see current data. Never save
    this object's structure anywhere; save_owner()/save_owners() persist the
    real owners list.
    """
    return Owner(
        "All Owners",
        pets=[pet for owner in get_owners() for pet in owner.pets],
    )


def get_scheduler() -> Scheduler:
    """Return a Scheduler across every owner's pets."""
    return Scheduler(get_combined_owner())


def save_owners(owners: list[Owner]) -> None:
    """Persist every owner (and their pets/tasks) to data.json."""
    save_owners_to_json(owners, str(DATA_PATH))


def save_owner(owner: Owner) -> None:
    """Persist all owners to data.json — call after any mutation, on every page."""
    save_owners(get_owners())


def get_clinic() -> Clinic:
    """Return this session's Clinic (departments/doctors/services/appointments),
    loading it from clinic.json once if needed. Shared across every
    "Veterinarian" page, independent of the owners list in data.json."""
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


def pet_label(pet: Pet, owners: list[Owner]) -> str:
    """Return "🐈 Garfield (Jasmine)" — a pet's display label including its
    owner, looked up by object identity in the passed owners list.

    Owner names matter in dropdown labels for correctness, not just clarity:
    Streamlit identifies a selectbox's chosen option by its *formatted label
    string*, so two options that format identically can register as each
    other when clicked.

    Takes owners as a parameter (rather than calling get_owners()) so labels
    can be precomputed into plain lists during the script run — a selectbox
    format_func can get re-invoked outside any run context, where
    st.session_state isn't available.
    """
    for owner in owners:
        if any(existing is pet for existing in owner.pets):
            return f"{pet_species_icon(pet.species)} {pet.name} ({owner.name})"
    return f"{pet_species_icon(pet.species)} {pet.name}"


def task_pair_label(index: int, pet: Pet, task: Task, owners: list[Owner]) -> str:
    """Return a unique dropdown label for a (pet, task) pair.

    The "N." prefix guarantees no two options in one dropdown ever share a
    label (see pet_label's docstring for why identical labels are unsafe),
    even for two same-titled tasks on the same pet at the same time.
    """
    return (
        f"{index + 1}. {pet_label(pet, owners)} | {task_type_icon(task.title)} {task.title} "
        f"@ {format_time_12h(task.time)}"
    )


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


def render_veterinary_reason_picker(title: str, species: str, key_prefix: str = "vet") -> str | None:
    """Show an extra "Reason" sub-picker for veterinary task titles vets
    naturally subdivide further (which vaccine, which blood panel, etc).
    Returns the picked reason (stored on Task.notes/Appointment.reason), or
    None if this task title has no defined sub-reasons.

    Called with `title`/`species` read from widgets that live outside the
    surrounding st.form, so this picker's own widgets must too — otherwise
    it wouldn't react until the whole form is submitted.

    `key_prefix` must be unique per call site — this renders both on the
    veterinary quick-add section and inside the Book Appointment dialog on
    the same page, so identical keys in both places would crash with
    DuplicateWidgetID if the dialog happens to be open at the same time.
    """
    species_key = species.lower()

    if title == "Injection Medication":
        category = st.selectbox(
            "Medication Category",
            INJECTION_MEDICATION_CATEGORIES,
            key=f"{key_prefix}_med_category",
        )
        if category == "Pain & Arthritis Management":
            medication_options = INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES.get(
                species_key, INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES["dog"]
            )
        else:
            medication_options = INJECTION_MEDICATION_OPTIONS[category]
        return st.selectbox(
            "Medication", medication_options, key=f"{key_prefix}_med_select_{category}"
        )

    if title in VETERINARY_TASK_REASONS_BY_SPECIES:
        species_options = VETERINARY_TASK_REASONS_BY_SPECIES[title].get(
            species_key, VETERINARY_TASK_REASONS_BY_SPECIES[title]["dog"]
        )
        return st.selectbox(
            "Reason", species_options, key=f"{key_prefix}_reason_select_{title}"
        )

    if title in VETERINARY_TASK_REASONS:
        return st.selectbox(
            "Reason", VETERINARY_TASK_REASONS[title], key=f"{key_prefix}_reason_select_{title}"
        )

    return None


def render_category_page(category: str, display_name: str, icon: str) -> None:
    """Render a full "Book a Service" category page: quick-add form, filtered
    schedule, and a complete-task action, all scoped to this category.

    Completing/deleting/reopening any task still lives on "Today's Schedule"
    rather than being duplicated on every category page.
    """
    owner = get_combined_owner()
    scheduler = get_scheduler()

    st.title(f"{icon} {display_name}")

    category_tasks = scheduler.sort_by_time(tasks_in_category(owner, category))
    title_options = CATEGORY_TASK_TITLES.get(category, [])

    if not owner.pets:
        st.warning("Add a pet before scheduling tasks here.")
        st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
    elif not title_options:
        st.info(f"{display_name} isn't wired up to specific task types yet.")
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
        # Labels precomputed into a plain list so the format_func closes over
        # no session state (see pet_label's docstring).
        real_owners = get_owners()
        pet_labels = [
            f"{i + 1}. {pet_label(pet, real_owners)}" for i, pet in enumerate(owner.pets)
        ]
        selected_pet_index = st.selectbox(
            "Pet",
            range(len(owner.pets)),
            format_func=lambda i: pet_labels[i],
            key=f"{category}_pet_select",
        )
        title = st.selectbox("Task", title_options, key=f"{category}_title_select")

        reason = None
        if category == "veterinary":
            selected_species = owner.pets[selected_pet_index].species
            reason = render_veterinary_reason_picker(title, selected_species, key_prefix=category)

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
            save_owner(owner)
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
        # Index-based, then re-fetch the live pair before mutating — and
        # mutate that exact task directly rather than going through
        # Scheduler.mark_task_complete()'s pet-name lookup, which could hit
        # the wrong pet now that different owners can have same-named pets.
        complete_labels = [
            task_pair_label(i, pet, task, get_owners())
            for i, (pet, task) in enumerate(open_category_tasks)
        ]
        complete_index = st.selectbox(
            "Open task",
            range(len(open_category_tasks)),
            format_func=lambda i: complete_labels[i],
            key=f"{category}_complete_select",
        )
        if st.button("Mark complete", key=f"{category}_complete_button"):
            complete_pet, complete_task = open_category_tasks[complete_index]
            complete_task.mark_complete()
            next_task = complete_task.next_occurrence(completed_on=date.today())
            if next_task is not None:
                complete_pet.add_task(next_task)
            save_owner(owner)
            st.success(f"Completed {complete_task.title}.")
            st.rerun()

    # Deliberately no unconditional save here: every mutation above saves
    # inline before its st.rerun(). A render-time save would let a stale
    # browser session silently overwrite data.json just by sitting open.
    st.caption('Completing, deleting, and reopening tasks lives on "Today\'s Schedule".')


def render_placeholder_page(display_name: str, icon: str) -> None:
    """Render a clearly-labeled "coming soon" page for a service category that
    doesn't have matching task types in TASK_TYPE_ICONS yet."""
    st.title(f"{icon} {display_name}")
    st.info(
        f"{display_name} isn't wired up to specific task types yet — this page "
        "is a placeholder for a future update."
    )
