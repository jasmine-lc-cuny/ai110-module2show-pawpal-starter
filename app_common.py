"""Shared state and UI helpers used across every page of the multi-page app."""

# ==========================================
# 📦 IMPORTS & SYSTEM PATHS
# Defines where the app looks for files and tools
# ==========================================
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
    priority_icon,
    save_owners_to_json,
    task_type_icon,
)

DATA_PATH = Path("data.json")
CLINIC_DATA_PATH = Path("clinic.json")
UPLOADS_PATH = Path("uploads")
NEW_OWNER_CHOICE = "+ Add new owner"

# ==========================================
# 🗄️ GLOBAL CONFIGURATION & MENUS
# Stores all the fixed lists, colors, and dictionary data 
# used to populate dropdowns across the app
# ==========================================

# st.badge() color per Appointment.status, matching the mockup's palette.
APPOINTMENT_STATUS_COLORS = {
    "Pending": "yellow",
    "Confirmed": "blue",
    "Completed": "green",
    "Cancelled": "red",
}

# Categories offered when uploading a Document
DOCUMENT_CATEGORIES = [
    "Digital radiography",
    "Dental digital x-ray",
    "In-house laboratory diagnostics",
    "Other",
]

# Colors for the weekly-schedule timeline
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

# Common care tasks offered in "Schedule a Task" dropdowns
COMMON_TASK_TITLES = [
    "Morning Walk", "Afternoon Walk", "Evening Walk", 
    "Breakfast", "Lunch", "Dinner", 
    "Give Medication", "Heartworm Prevention", "Vet Appointment", 
    "X-Ray", "Injection Medication", "Injection Vaccine", 
    "Injection Subcutaneous", "Injection Intramuscular", "Injection Intravenous", 
    "Blood Work", "Surgery", "Brush Coat", "Wash / Bath", "Hair Cut", 
    "Trim Nails", "Ear Cleaning", "Teeth Brushing", "Playtime",
]

# Sub-options offered on the veterinary quick-add form (Task.notes)
VETERINARY_TASK_REASONS = {
    "Give Medication": ["Heartworm Prevention", "Antibiotics"],
    "X-Ray": ["Hip"],
    "Blood Work": [
        "Complete Blood Count (CBC)", "Serum Chemistry", "Thyroid Panel",
        "Electrolyte Panel", "Pre-Anesthetic Panel", "Coagulation Profile",
    ],
    "Injection Subcutaneous": ["Routine Vaccines", "Maintenance Medications (e.g. Insulin)", "Fluid Therapy"],
    "Injection Intramuscular": ["Pain Management", "Sedatives and Tranquilizers", "Antibiotics"],
    "Injection Intravenous": ["General Anesthesia", "Emergency Medications", "Chemotherapy", "Continuous Fluid Therapy"],
}

# Sub-options that differ by species
VETERINARY_TASK_REASONS_BY_SPECIES = {
    "Injection Vaccine": {
        "dog": ["Rabies", "Distemper", "Parvovirus", "Adenovirus"],
        "cat": ["Rabies", "Panleukopenia", "Calicivirus", "Herpesvirus"],
    },
    "Surgery": {
        "dog": ["Neuter", "Dental Extractions", "Mass/Tumor Removals", "Gastrointestinal Surgeries", "Exploratory Laparotomy", "C-Section"],
        "cat": ["Spay", "Dental Extractions", "Mass/Tumor Removals", "Gastrointestinal Surgeries", "Exploratory Laparotomy", "C-Section"],
    },
}

INJECTION_MEDICATION_CATEGORIES = [
    "Pain & Arthritis Management",
    "Flea, Tick, & Allergy Relief",
    "Antibiotics & General Treatment",
]

INJECTION_MEDICATION_PAIN_OPTIONS_BY_SPECIES = {
    "dog": ["Librela (bedinvetmab)", "Adequan Canine (polysulfated glycosaminoglycan)"],
    "cat": ["Solensia (frunevetmab)"],
}

INJECTION_MEDICATION_OPTIONS = {
    "Flea, Tick, & Allergy Relief": ["Bravecto Quantum", "Cytopoint"],
    "Antibiotics & General Treatment": ["Convenia (cefovecin sodium)", "Injectable Insulin (Vetsulin or ProZinc)"],
}

# The Dog Cafes menu
A_LA_BARK_MENU = [
    (
        "🍔 Pooch Pub Grub",
        "Hearty, warm, and savory meals for the hungriest pups.",
        [
            ("Mini Paw Burger & Sliders", "$6.50", "Small beef patties served with a side of steamed veggies."),
            ("The Bark-B-Q Platter", "$8.50", "Slow-cooked, shredded chicken or beef with a drizzle of dog-safe bone broth."),
            ("Shepherd’s Pie for Paws", "$7.25", "Lean ground meat topped with a layer of mashed sweet potato and peas."),
            ("Barkingly Good Beef Supper", "$5.00", "A warm meal of ground beef, brown rice, and vegetables."),
            ("Waggingly Delicious Chicken Dinner", "$5.00", "Slow-cooked chicken in doggy gravy with crushed potatoes and vegetables."),
            ("Doggy Bowl", "$7.00", "A full meal featuring turkey, brown rice, corn, peas, green beans, and carrots."),
        ],
    ),
    (
        "🧁 Poodings & Paws-tisserie",
        "Sweet, decadent treats and baked goods to finish off the perfect outing.",
        [
            ("Pup-Cake Delight", "$3.75", "A single-serve cupcake topped with sugar-free yogurt icing and a biscuit crumble."),
            ("Pupcake", "$3.20", "A classic baked treat."),
            ("Doggy Doughnut", "$3.20", "A sweet ring-shaped baked good."),
            ("Doggy Éclair", "$3.84", "A specialty pastry-style treat."),
            ("Iced Bone", "$3.20", "A crunchy, frosted biscuit bone."),
        ],
    ),
    (
        "🍦 Frosty Furs & Chillers",
        "Refreshing, icy, and creamy delights for hot days.",
        [
            ("Bark-A-Licious Gelato", "$4.50", "A generous scoop of peanut butter or banana-flavored doggy ice cream."),
            ("Frosty Paws Ice Cream Cup", "$4.99", "A cool, wholesome treat containing essential vitamins, minerals, and protein."),
            ("Whipped Cream \"Pup-Tini\"", "$2.50", "A small, fluffy cup of fresh whipped cream served with a crunchy bone-shaped cookie."),
            ("Doggie Frap", "$1.89", "A small bowl of homemade whipped cream."),
            ("Puppuccino", "$2.56", "A bowl of freshly chilled goat’s milk."),
        ],
    ),
    (
        "🦴 Snack-Attack Nibbles",
        "Small, quick bites perfect for training or snacking.",
        [
            ("Lil' Nibbles", "$0.63–$3.19", "Smaller snacks including chicken breast, sausages, biscuits, or a Yorkie puddin'."),
            ("Veggie Snacks", "$3.00", "A healthy mix of apples, carrots, and cucumbers."),
            ("Scooby Snacks", "$4.00", "A treat made with pumpkin, peanut butter, milk, and oats."),
            ("Bon A-Pet Treat", "$2.00", "Homemade peanut butter bone-shaped biscuits."),
        ],
    ),
    (
        "🍺 The Wet Bar (For Canines)",
        "Non-alcoholic, dog-safe beverages.",
        [
            ("Dog Beer", "$3.84", "A refreshing, non-alcoholic brew."),
            ("Bottom Sniffer Beer", "$4.93", "A specialized doggy beer."),
            ("Pawsacco", "$3.84", "A specialized herbal blend."),
            ("Doggy Afternoon Tea", "$8.96", "Specialized blends for oral health or skin and coat support."),
        ],
    ),
]

# The five bookable service sections staff can be assigned to. Kept here so the
# staff page, the seeder, and the home-page service picker share one list.
SERVICE_SECTIONS = [
    ("🛁", "Grooming"),
    ("🏠", "Sitting"),
    ("🎓", "Training"),
    ("🐕", "Walking"),
    ("🍖", "Dog Cafes"),
]

COMMON_SERVICES = [
    ("Blood Work", 45.0),
    ("X-Ray", 100.0),
    ("Injection Medication", 25.0),
    ("Surgery", 500.0),
    ("Vaccination", 30.0),
    ("Dental Cleaning", 80.0),
    ("Spay/Neuter", 250.0),
]

SERVICE_CATEGORY_ICONS = {
    "grooming": {"👂", "🦷", "💅", "✂️", "🧼", "🪮"},
    "walking": {"🐕"},
    "sitting": {"🏠"},
    "training": {"🎓"},
    "veterinary": {"💊", "🏥"},
    "special_services": {"🍖", "🐾"},
}

CATEGORY_TASK_TITLES = {
    "grooming": ["Brush Coat", "Wash / Bath", "Hair Cut", "Trim Nails", "Ear Cleaning", "Teeth Brushing"],
    "walking": ["Morning Walk", "Afternoon Walk", "Evening Walk", "Playtime"],
    "sitting": ["Day Sitting", "Overnight Sitting", "Drop-In Visit", "House Sitting"],
    "training": ["Obedience Training", "Puppy Class", "Leash Training", "Trick Training"],
    "veterinary": [
        "Give Medication", "Heartworm Prevention", "Vet Appointment", "X-Ray",
        "Injection Medication", "Injection Vaccine", "Injection Subcutaneous",
        "Injection Intramuscular", "Injection Intravenous", "Blood Work", "Surgery",
    ],
    "special_services": ["Breakfast", "Lunch", "Dinner"],
}

# Maps a service-page category key to its staff section label (SERVICE_SECTIONS),
# so a booking form can offer the staff assigned to that service.
CATEGORY_TO_SECTION = {
    "grooming": "Grooming",
    "sitting": "Sitting",
    "training": "Training",
    "walking": "Walking",
    "special_services": "Dog Cafes",
}

# ==========================================
# 💾 STATE MANAGEMENT & DATA PERSISTENCE
# ==========================================

def get_owners() -> list[Owner]:
    if "owners" not in st.session_state:
        if DATA_PATH.exists():
            st.session_state.owners = load_owners_from_json(str(DATA_PATH))
        else:
            st.session_state.owners = [Owner("Jordan")]
    return st.session_state.owners

def get_combined_owner() -> Owner:
    return Owner(
        "All Owners",
        pets=[pet for owner in get_owners() for pet in owner.pets],
    )

def get_scheduler() -> Scheduler:
    return Scheduler(get_combined_owner())

def save_owners(owners: list[Owner]) -> None:
    save_owners_to_json(owners, str(DATA_PATH))

def save_owner(owner: Owner) -> None:
    save_owners(get_owners())

def get_clinic() -> Clinic:
    if "clinic" not in st.session_state:
        if CLINIC_DATA_PATH.exists():
            st.session_state.clinic = Clinic.load_from_json(str(CLINIC_DATA_PATH))
        else:
            st.session_state.clinic = Clinic()
    return st.session_state.clinic

def save_clinic(clinic: Clinic) -> None:
    clinic.save_to_json(str(CLINIC_DATA_PATH))

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
def render_category_page(
    category: str, 
    display_name: str, 
    icon: str, 
    page_title: str | None = None,
    page_subtitle: str | None = None
) -> None:
    owner = get_combined_owner()
    scheduler = get_scheduler()

    # Staff who can be assigned to this service (empty for the veterinary page,
    # which assigns doctors via the Appointments page instead).
    section = CATEGORY_TO_SECTION.get(category)
    active_staff = (
        [member for member in get_clinic().staff_in_section(section) if member.active]
        if section
        else []
    )

    st.title(page_title if page_title else f"{icon} {display_name}")

    if "ui_alert_success" in st.session_state:
        st.success(st.session_state.pop("ui_alert_success"))
    if "ui_alert_warning" in st.session_state:
        st.warning(st.session_state.pop("ui_alert_warning"))

    category_tasks = scheduler.sort_by_time(tasks_in_category(owner, category))
    title_options = CATEGORY_TASK_TITLES.get(category, [])

    if not owner.pets:
        st.warning("Add a pet before scheduling tasks here.")
        st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
    elif not title_options:
        st.info(f"{display_name} isn't wired up to specific task types yet.")
    else:
        toggle_key = f"show_schedule_{category}"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False

        if not st.session_state[toggle_key]:
            if st.button(f"➕ Book {display_name}", key=f"{category}_show_schedule", use_container_width=True):
                st.session_state[toggle_key] = True
                st.rerun()
        else:
            if st.button("🔼 View less", key=f"{category}_hide_schedule"):
                st.session_state[toggle_key] = False
                st.rerun()

            # Use custom subtitle if provided, otherwise default to "Schedule a [Service] Task"
            if page_subtitle:
                st.subheader(page_subtitle)
            else:
                st.subheader(f"Schedule a {display_name} Task")

            if category == "veterinary":
                PET_CATEGORIES = {
                    "🐶 General Companion": ["dog", "cat"],
                    "🐹 Exotic Small Pet": ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig", "ferret", "hedgehog", "sugar glider", "squirrel"],
                    "🦜 Exotic Avian": ["budgie", "canary", "finch", "parrot", "cockatiel", "conure", "chicken", "duck", "goose", "pigeon", "owl", "falcon", "snowy owl"],
                    "🦎 Reptiles & Amphibians": ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "turtle", "tortoise", "corn snake", "ball python", "king snake", "frog", "toad", "newt", "salamander"],
                    "🐠 Fish & Invertebrates": ["betta", "guppy", "platy", "swordtail", "molly", "tetra", "goldfish", "danio", "minnow", "cichlid", "pleco", "clownfish", "damselfish", "goby", "blenny"]
                }

                group_options = ["All Groups"] + list(PET_CATEGORIES.keys())
                selected_group = st.radio(
                    "Filter by Species Group",
                    options=group_options,
                    horizontal=True,
                    key=f"{category}_group_filter"
                )

                if selected_group == "All Groups":
                    allowed_species = None
                else:
                    raw_species_list = PET_CATEGORIES[selected_group]
                    species_options = ["All"] + [f"{pet_species_icon(s)} {s.capitalize()}" for s in raw_species_list]
                
                    selected_species_label = st.radio(
                        "Filter by Species",
                        options=species_options,
                        horizontal=True,
                        key=f"{category}_species_filter"
                    )
                
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

                if target_species:
                    allowed_species = [target_species]
                else:
                    allowed_species = ["dog", "cat"]

            owners_with_pets = []
            for candidate in get_owners():
                if not candidate.pets:
                    continue
            
                has_matching_pet = False
                for pet in candidate.pets:
                    if allowed_species is None or pet.species.lower() in allowed_species:
                        has_matching_pet = True
                        break
            
                if has_matching_pet:
                    owners_with_pets.append(candidate)

            if f"{category}_owner_index_state" not in st.session_state or st.session_state[f"{category}_owner_index_state"] >= len(owners_with_pets):
                st.session_state[f"{category}_owner_index_state"] = 0

            if not owners_with_pets:
                st.info("No owners currently have a pet matching this filter.")
            else:
                selected_owner = owners_with_pets[st.session_state[f"{category}_owner_index_state"]]
            
                filtered_pets = []
                for i, pet in enumerate(selected_owner.pets):
                    if allowed_species is None or pet.species.lower() in allowed_species:
                        filtered_pets.append((i, pet))
            
                pet_labels = [
                    f"{i + 1}. {pet_species_icon(pet.species)} {pet.name} ({pet.species})"
                    for i, pet in filtered_pets
                ]
            
                owner_labels = [
                    f"{i + 1}. {candidate.name}" for i, candidate in enumerate(owners_with_pets)
                ]

                col1, col2 = st.columns(2)
            
                with col1:
                    selected_owner_index = st.selectbox(
                        "Owner",
                        range(len(owners_with_pets)),
                        format_func=lambda i: owner_labels[i],
                        key=f"{category}_owner_select",
                    )
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

                col3, col4 = st.columns(2)
            
                with col3:
                    title = st.selectbox("Task", title_options, key=f"{category}_title_select")
            
                with col4:
                    reason = None
                    if category == "veterinary":
                        selected_species = selected_owner.pets[selected_pet_index].species
                        reason = render_veterinary_reason_picker(title, selected_species, key_prefix=category)
                    elif category == "special_services":
                        reason = _render_dog_cafe_menu_picker()
                    else:
                        st.text_input("Reason", value="—", disabled=True, key=f"{category}_disabled_reason")

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
                            staff_index = st.selectbox(
                                "Assigned staff",
                                range(len(active_staff)),
                                format_func=lambda i: staff_labels[i],
                                key=f"{category}_staff_select",
                            )
                        else:
                            staff_index = None
                            if section:
                                st.caption(f"No active {section} staff — add some on the Staff page.")

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

                    if category == "special_services":
                        duration, priority, frequency = 60, "medium", "once"
                        submitted = st.form_submit_button("Dog Cafe RSVP")
                    else:
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

                    time_str = f"{hour_24:02d}:{minute}"
                    selected_pet = selected_owner.pets[selected_pet_index]
                    assignee = active_staff[staff_index].full_name if staff_index is not None else None

                    # Same pet, same date AND time = a real double-booking.
                    conflict = any(
                        t.time == time_str and t.due_date == appt_date and not t.completed
                        for t in selected_pet.tasks
                    )
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
                    save_owner(owner)
                
                    success_message = f"Added {title} for {selected_pet.name}."
                    if reason:
                        success_message = f"Added {title} ({reason}) for {selected_pet.name}."
                
                    st.session_state["ui_alert_success"] = success_message
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
            
            msg = f"Completed {complete_task.title}."
            if next_task is not None:
                complete_pet.add_task(next_task)
                msg += " 🔁 New recurring task automatically generated for next time!"
                
            save_owner(owner)
            st.session_state["ui_alert_success"] = msg
            st.rerun()

    st.caption('Completing, deleting, and reopening tasks lives on "Today\'s Schedule".')

def render_placeholder_page(display_name: str, icon: str) -> None:
    st.title(f"{icon} {display_name}")
    st.info(
        f"{display_name} isn't wired up to specific task types yet — this page "
        "is a placeholder for a future update."
    )