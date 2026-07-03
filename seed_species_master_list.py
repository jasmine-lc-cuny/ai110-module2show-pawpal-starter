"""Unified master seeder for the PawPal+ clinic.

Combines the logic of seed_master.py, seed_massive.py, and seed_all_species.py
into one factory that builds the entire diverse clinic: dogs, cats, and all
exotics (small mammals, avians, reptiles, fish) in a single pass.

- Every species in SPECIES is guaranteed to appear at least once.
- Dogs and cats each make up ~20% of the roster (like seed_master.py).
- Exotics keep their "hacked" stats (e.g., weight -> Tank Size for fish).
- Each run rebuilds data.json from scratch.

Medical data (breed/species chronic conditions and genetic-risk markers) was
verified against veterinary references — VCA Animal Hospitals, the Merck
Veterinary Manual, PetMD, and breed/species health surveys — rather than
generated freehand. Key corrections captured: Siberian Huskies are low-risk for
hip dysplasia (their real hereditary risks are eye conditions); Scottish Folds
always carry osteochondrodysplasia (it's the fold gene itself); snakes do not
get metabolic bone disease; egg binding is female-only; and fin rot / ich are
husbandry issues, not inherited — so they're tagged as such, not as "genetic."
Senior-onset conditions (e.g., feline kidney disease) are age-gated.
"""

import random
import sys

from pawpal_system import Owner, Pet, save_owners_to_json

DATA_PATH = "data.json"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Combined master list: all unique owner names from the three original
# seeders (seed_master + seed_massive + seed_all_species), no duplicates.
OWNER_NAMES = [
    "James Smith", "Mary Johnson", "Robert Williams", "Patricia Brown", "John Jones",
    "Jennifer Garcia", "Michael Miller", "Linda Davis", "David Rodriguez", "Elizabeth Martinez",
    "William Hernandez", "Barbara Lopez", "Richard Gonzalez", "Susan Wilson", "Joseph Anderson",
    "Jessica Thomas", "Thomas Taylor", "Sarah Moore", "Christopher Jackson", "Karen Martin",
    "Charles Lee", "Lisa Perez", "Daniel Thompson", "Nancy White", "Matthew Harris",
    "Betty Sanchez", "Anthony Clark", "Sandra Ramirez", "Mark Lewis", "Margaret Robinson",
    "Donald Walker", "Ashley Young", "Steven Allen", "Kimberly King", "Andrew Wright",
    "Emily Scott", "Paul Torres", "Donna Nguyen", "Joshua Hill", "Michelle Flores",
    "Kenneth Green", "Carol Adams", "Kevin Nelson", "Amanda Baker", "Brian Hall",
    "Melissa Rivera", "George Campbell", "Deborah Mitchell", "Edward Carter", "Stephanie Roberts",
    "Alan Turing", "Marie Curie", "Nikola Tesla", "Ada Lovelace", "Grace Hopper",
    "Albert Einstein", "Isaac Newton", "Galileo Galilei", "Charles Darwin", "Stephen Hawking",
    "Rosalind Franklin", "Jane Goodall", "Carl Sagan", "Neil deGrasse Tyson", "Bill Nye",
    "Steve Irwin", "David Attenborough", "Jacques Cousteau", "Sylvia Earle", "Rachel Carson",
    "Walt Disney", "Jim Henson", "Stan Lee", "Jack Kirby", "Hayao Miyazaki",
    "Arthur Conan Doyle", "Agatha Christie", "Stephen King", "J.K. Rowling", "J.R.R. Tolkien",
    "Liam Gallagher", "Emma Thompson", "Noah Williams", "Olivia Brown", "Aria Parker",
    "Elijah Walker", "Charlotte Hall", "Lucas Allen", "Amelia Young", "Mason King",
    "Harper Wright", "Logan Scott", "Evelyn Torres", "Alexander Nguyen", "Abigail Hill",
    "Ethan Flores", "Emily Green", "Jacob Adams", "Elizabeth Nelson", "Michael Baker",
    "William Jones", "Ava Garcia", "James Martinez", "Isabella Robinson", "Oliver Clark",
    "Sophia Rodriguez", "Benjamin Lewis", "Mia Lee", "Mila Rivera", "Daniel Campbell",
    "Ella Mitchell", "Henry Carter", "Avery Roberts", "Jackson Gomez", "Sofia Phillips",
    "Sebastian Evans", "Camila Turner", "Aiden Diaz", "Matthew Cruz", "Scarlett Edwards",
    "Samuel Collins", "Victoria Reyes", "David Stewart", "Madison Morris", "Joseph Morales",
    "Luna Murphy", "Carter Cook", "Grace Rogers", "Owen Gutierrez", "Chloe Ortiz",
    "Wyatt Morgan", "Penelope Cooper", "John Peterson", "Layla Bailey", "Luke Reed",
    "Zoe Jenkins", "Levi Ward", "Stella Brooks", "Gabriel Kelly", "Nora Sanders",
    "Florence Nightingale", "Clara Barton", "Mary Seacole", "Elizabeth Blackwell", "Dorothea Dix",
    "Virginia Apgar", "Jonas Salk", "Alexander Fleming", "Louis Pasteur", "Edward Jenner",
    "George Lucas", "Steven Spielberg", "Martin Scorsese", "Alfred Hitchcock", "Stanley Kubrick",
    "Quentin Tarantino", "Christopher Nolan", "James Cameron", "Peter Jackson", "Ridley Scott",
    "John Williams", "Hans Zimmer", "Ennio Morricone", "Danny Elfman", "Howard Shore",
    "George R.R. Martin", "Isaac Asimov", "Arthur C. Clarke", "Philip K. Dick", "Frank Herbert",
]

# Combined master list: all unique pet names from the three original seeders.
PET_NAMES = [
    "Bella", "Luna", "Charlie", "Lucy", "Cooper",
    "Max", "Bailey", "Daisy", "Sadie", "Maggie",
    "Rocky", "Oreo", "Buster", "Chloe", "Sophie",
    "Lily", "Stella", "Molly", "Penny", "Lola",
    "Shelly", "Speedy", "Ninja", "Bubbles", "Flipper",
    "Spike", "Pip", "Squeak", "Apollo", "Sunny",
    "Nibbles", "Shadow", "Pippin", "Gizmo", "Yoshi",
    "Draco", "Finn", "Nemo", "Dory", "Mochi",
    "Peanut", "Barnaby", "Thor", "Cleo", "Jasper",
    "Ruby", "Simba", "Coco", "Bandit", "Hazel",
    "Blue", "Pepper", "Oscar", "Dexter", "Toby",
    "Winston", "Olive", "Milo", "Leo", "Loki",
    "Chester", "Felix", "Pumpkin", "Rosie", "Archie",
    "Willow", "Roxy", "Zeus", "Winnie", "Gus",
    "Duke", "Bear", "Tucker", "Murphy", "Oliver",
    "Harley", "Riley", "Marley", "Scout", "Jax",
    "Koda", "Mac", "Diesel", "Louie", "Hank",
    "Boomer", "Bruce", "Frankie", "Ghost", "Gunner",
    "Hunter", "Jack", "Kobe", "Moose", "Rex",
    "Rocco", "Sam", "Ziggy", "Mango", "Kiwi",
]

SPECIES = [
    # Common
    ("dog", "mammal"), ("cat", "mammal"),
    # Small Mammals
    ("rabbit", "mammal"), ("bunny", "mammal"), ("hamster", "mammal"), ("gerbil", "mammal"),
    ("mouse", "mammal"), ("mice", "mammal"), ("rat", "mammal"), ("chinchilla", "mammal"),
    ("guinea pig", "mammal"), ("ferret", "mammal"), ("hedgehog", "mammal"),
    ("sugar glider", "mammal"), ("squirrel", "mammal"),
    # Avian
    ("budgie", "avian"), ("canary", "avian"), ("finch", "avian"), ("parrot", "avian"),
    ("cockatiel", "avian"), ("conure", "avian"), ("chicken", "avian"), ("duck", "avian"),
    ("goose", "avian"), ("pigeon", "avian"), ("owl", "avian"), ("falcon", "avian"), ("snowy owl", "avian"),
    # Reptiles
    ("bearded dragon", "reptile"), ("leopard gecko", "reptile"), ("crested gecko", "reptile"),
    ("chameleon", "reptile"), ("iguana", "reptile"), ("skink", "reptile"), ("turtle", "reptile"),
    ("tortoise", "reptile"), ("corn snake", "reptile"), ("ball python", "reptile"),
    ("king snake", "reptile"), ("frog", "reptile"), ("toad", "reptile"), ("newt", "reptile"),
    ("salamander", "reptile"),
    # Fish
    ("betta", "fish"), ("guppy", "fish"), ("platy", "fish"), ("swordtail", "fish"),
    ("molly", "fish"), ("tetra", "fish"), ("goldfish", "fish"), ("danio", "fish"),
    ("minnow", "fish"), ("cichlid", "fish"), ("pleco", "fish"), ("clownfish", "fish"),
    ("damselfish", "fish"), ("goby", "fish"), ("blenny", "fish"),
]

EXOTIC_SPECIES = SPECIES[2:]  # everything except dog and cat

# Breed -> realistic weight range in lbs (upper bounds allow a chunky pet).
# Dogs and cats get their weight rolled from their breed's range, so a
# Chihuahua never outweighs a Great Dane.
DOG_BREEDS = {
    "Labrador Retriever": (55, 90), "German Shepherd": (50, 95), "Golden Retriever": (55, 80),
    "French Bulldog": (16, 30), "Bulldog": (40, 55), "Poodle": (40, 70),
    "Beagle": (18, 35), "Rottweiler": (80, 135), "Dachshund": (11, 32),
    "Yorkshire Terrier": (4, 10), "Chihuahua": (3, 9), "Great Dane": (110, 175),
    "Shih Tzu": (9, 18), "Siberian Husky": (35, 60), "Boxer": (55, 80),
    "Pembroke Welsh Corgi": (22, 33), "Border Collie": (30, 55), "Australian Shepherd": (40, 65),
    "Pit Bull Terrier": (30, 65), "Mixed Breed": (15, 90),
}
CAT_BREEDS = {
    "Domestic Shorthair": (8, 18), "Domestic Longhair": (8, 18), "Maine Coon": (10, 25),
    "Siamese": (6, 14), "Persian": (7, 15), "Ragdoll": (10, 20),
    "Bengal": (8, 16), "Sphynx": (6, 14), "British Shorthair": (7, 17),
    "Russian Blue": (7, 15), "Scottish Fold": (6, 13), "Norwegian Forest Cat": (9, 20),
}

# Realistic weight ranges per species: (min, max, unit). Upper bounds allow a
# chunky-but-plausible pet — no more 67 lb cats. Dogs and cats are handled by
# their breed tables above; fish are excluded because their weight field is
# repurposed as Tank Size.
WEIGHT_RANGES = {
    # Small Mammals
    "rabbit": (2, 14, "lbs"), "bunny": (2, 14, "lbs"), "hamster": (30, 200, "g"),
    "gerbil": (50, 110, "g"), "mouse": (20, 45, "g"), "mice": (20, 45, "g"),
    "rat": (250, 650, "g"), "chinchilla": (400, 900, "g"), "guinea pig": (700, 1400, "g"),
    "ferret": (1, 6, "lbs"), "hedgehog": (300, 900, "g"), "sugar glider": (90, 160, "g"),
    "squirrel": (300, 700, "g"),
    # Avian
    "budgie": (30, 45, "g"), "canary": (15, 25, "g"), "finch": (10, 20, "g"),
    "parrot": (300, 1500, "g"), "cockatiel": (80, 120, "g"), "conure": (60, 120, "g"),
    "chicken": (4, 10, "lbs"), "duck": (2, 8, "lbs"), "goose": (7, 14, "lbs"),
    "pigeon": (240, 380, "g"), "owl": (450, 2200, "g"), "falcon": (400, 1600, "g"),
    "snowy owl": (1600, 2950, "g"),
    # Reptiles
    "bearded dragon": (280, 550, "g"), "leopard gecko": (45, 90, "g"),
    "crested gecko": (35, 60, "g"), "chameleon": (90, 200, "g"), "iguana": (9, 17, "lbs"),
    "skink": (300, 600, "g"), "turtle": (1, 5, "lbs"), "tortoise": (5, 70, "lbs"),
    "corn snake": (250, 900, "g"), "ball python": (1200, 2500, "g"),
    "king snake": (900, 1500, "g"), "frog": (20, 80, "g"), "toad": (30, 100, "g"),
    "newt": (10, 25, "g"), "salamander": (20, 120, "g"),
}


# Common real-world dog/cat allergies (food and environmental).
DOG_CAT_ALLERGIES = [
    "Chicken", "Beef", "Dairy", "Wheat / Grain", "Egg", "Lamb", "Soy",
    "Flea Saliva", "Pollen", "Dust Mites", "Grass", "Mold Spores",
]

# ---------------------------------------------------------------------------
# Medical data (verified against veterinary sources — see module docstring).
#
# Two ideas are kept distinct:
#   * chronic       - conditions a pet can actually be *diagnosed* with.
#   * risk (marker) - a predisposition the pet does NOT have. Each is tagged:
#       "hereditary"    a true genetic/inherited risk (breeds; a few exotics)
#       "predisposition" an anatomical/dietary species tendency
#       "husbandry"     an environmental problem — explicitly NOT inherited
#     This split exists because a reviewer flagged that things like fin rot and
#     metabolic bone disease are husbandry issues, not genetic markers.
# ---------------------------------------------------------------------------

CONDITION_NOTES = [
    "diagnosed, managed with medication", "mild, diet-controlled",
    "stable, monitored at checkups", "flares up seasonally", "requires ongoing treatment",
]

# Conditions that should only appear in older animals (min age in years), so a
# 1-year-old cat never rolls kidney disease.
CONDITION_MIN_AGE = {
    "Chronic Kidney Disease": 8, "Hyperthyroidism": 8, "Osteoarthritis": 7,
    "Arthritis": 7, "Diabetes": 6, "Insulinoma": 3, "Adrenal Disease": 3,
    "Lymphoma": 3, "Neoplasia": 3, "Cancer": 3, "Tumors": 2,
}

# Reproductive conditions that only make sense for females.
FEMALE_ONLY = {"Egg Binding", "Chronic Egg Laying", "Egg Yolk Peritonitis", "Uterine Adenocarcinoma"}

DOG_CHRONIC = ["Osteoarthritis", "Allergic Dermatitis (Atopy)", "Diabetes Mellitus",
               "Hypothyroidism", "Chronic Otitis (Ear Infections)"]
CAT_CHRONIC = ["Chronic Kidney Disease", "Hyperthyroidism", "Diabetes Mellitus",
               "Feline Asthma", "Dental Disease", "Inflammatory Bowel Disease"]

# Breed -> inherited conditions the breed is predisposed to (used as "at risk,
# not present" markers). Empty list = mixed ancestry -> "none identified".
DOG_BREED_RISKS = {
    "Labrador Retriever": ["Hip Dysplasia", "Progressive Retinal Atrophy"],
    "German Shepherd": ["Hip Dysplasia", "Degenerative Myelopathy"],
    "Golden Retriever": ["Hip Dysplasia", "Subvalvular Aortic Stenosis"],
    "French Bulldog": ["Brachycephalic Airway Syndrome", "Intervertebral Disc Disease"],
    "Bulldog": ["Brachycephalic Airway Syndrome", "Skin Fold Dermatitis"],
    "Poodle": ["Addison's Disease", "Progressive Retinal Atrophy"],
    "Beagle": ["Epilepsy", "Hypothyroidism"],
    "Rottweiler": ["Osteosarcoma", "Hip Dysplasia"],
    "Dachshund": ["Intervertebral Disc Disease", "Luxating Patella"],
    "Yorkshire Terrier": ["Tracheal Collapse", "Luxating Patella"],
    "Chihuahua": ["Luxating Patella", "Mitral Valve Disease"],
    "Great Dane": ["Bloat (GDV)", "Dilated Cardiomyopathy"],
    "Shih Tzu": ["Brachycephalic Airway Syndrome", "Dry Eye (KCS)"],
    # Huskies are one of the LOWEST hip-dysplasia breeds; their real hereditary
    # risks are eye conditions (cataracts ~8%, corneal dystrophy ~3%).
    "Siberian Husky": ["Hereditary Cataracts", "Corneal Dystrophy"],
    "Boxer": ["Boxer Cardiomyopathy (ARVC)", "Mast Cell Tumors"],
    "Pembroke Welsh Corgi": ["Degenerative Myelopathy", "Intervertebral Disc Disease"],
    "Border Collie": ["Collie Eye Anomaly", "Epilepsy"],
    "Australian Shepherd": ["MDR1 Drug Sensitivity", "Collie Eye Anomaly"],
    "Pit Bull Terrier": ["Hip Dysplasia", "Demodectic Mange"],
    "Mixed Breed": [],
}
CAT_BREED_RISKS = {
    "Domestic Shorthair": [], "Domestic Longhair": [],
    "Maine Coon": ["Hypertrophic Cardiomyopathy", "Hip Dysplasia"],
    "Siamese": ["Progressive Retinal Atrophy", "Feline Asthma"],
    "Persian": ["Polycystic Kidney Disease", "Brachycephalic Airway Syndrome"],
    "Ragdoll": ["Hypertrophic Cardiomyopathy"],
    "Bengal": ["Progressive Retinal Atrophy", "Hypertrophic Cardiomyopathy"],
    "Sphynx": ["Hypertrophic Cardiomyopathy", "Hereditary Myopathy"],
    "British Shorthair": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Russian Blue": ["Obesity (breed tendency)"],
    # Osteochondrodysplasia is caused by the fold gene, so every fold-eared cat
    # HAS it (handled as an always-present condition below). Their at-risk
    # markers are the cardiac/kidney conditions instead.
    "Scottish Fold": ["Hypertrophic Cardiomyopathy", "Polycystic Kidney Disease"],
    "Norwegian Forest Cat": ["Glycogen Storage Disease IV", "Hypertrophic Cardiomyopathy"],
}
# Breeds where the defining trait IS a lifelong condition, so every one has it.
BREED_ALWAYS_HAS = {
    "Scottish Fold": "Osteochondrodysplasia: inherited cartilage & joint disease — present in all fold-eared cats",
}

# Per-species exotic profiles: what they can be diagnosed with (chronic) and
# their (condition, kind) risk markers. Anything not listed here falls back to
# the per-category defaults below.
EXOTIC_PROFILES = {
    # --- Small mammals ---
    "rabbit": {"chronic": ["Dental Malocclusion", "Chronic GI Stasis", "Pododermatitis (Sore Hocks)"],
               "risk": [("Dental Malocclusion", "predisposition"), ("Uterine Adenocarcinoma", "predisposition")]},
    "bunny": {"chronic": ["Dental Malocclusion", "Chronic GI Stasis", "Pododermatitis (Sore Hocks)"],
              "risk": [("Dental Malocclusion", "predisposition"), ("Uterine Adenocarcinoma", "predisposition")]},
    "hamster": {"chronic": ["Dental Overgrowth", "Cheek Pouch Impaction"],
                "risk": [("Wet Tail (Proliferative Ileitis)", "husbandry"), ("Tumors", "predisposition")]},
    "gerbil": {"chronic": ["Dental Overgrowth", "Scent Gland Tumors"],
               "risk": [("Epilepsy (hereditary seizures)", "hereditary"), ("Scent Gland Tumors", "predisposition")]},
    "mouse": {"chronic": ["Chronic Respiratory Disease (Mycoplasma)", "Mammary Tumors"],
              "risk": [("Mammary Tumors", "predisposition"), ("Respiratory Mycoplasmosis", "husbandry")]},
    "mice": {"chronic": ["Chronic Respiratory Disease (Mycoplasma)", "Mammary Tumors"],
             "risk": [("Mammary Tumors", "predisposition"), ("Respiratory Mycoplasmosis", "husbandry")]},
    "rat": {"chronic": ["Chronic Respiratory Disease (Mycoplasma)", "Mammary Tumors"],
            "risk": [("Mammary Tumors", "predisposition"), ("Pituitary Tumors", "predisposition")]},
    "chinchilla": {"chronic": ["Dental Disease (Malocclusion)", "Fur Chewing", "Chronic GI Stasis"],
                   "risk": [("Dental Disease", "predisposition"), ("Heat Stroke", "husbandry")]},
    "guinea pig": {"chronic": ["Dental Malocclusion", "Mammary/Skin Tumors", "Pododermatitis (Bumblefoot)"],
                   "risk": [("Vitamin C Deficiency (Scurvy)", "predisposition"), ("Dental Malocclusion", "predisposition")]},
    "ferret": {"chronic": ["Insulinoma", "Adrenal Disease (Hyperadrenocorticism)", "Lymphoma"],
               "risk": [("Insulinoma", "predisposition"), ("Adrenal Disease", "predisposition")]},
    "hedgehog": {"chronic": ["Obesity / Fatty Liver Disease", "Dental Disease", "Neoplasia (Cancer)"],
                 "risk": [("Wobbly Hedgehog Syndrome", "hereditary"), ("Obesity", "predisposition")]},
    "sugar glider": {"chronic": ["Hind Limb Paralysis (Calcium Deficiency)", "Obesity", "Dental Abscesses"],
                     "risk": [("Metabolic Bone Disease", "predisposition"), ("Obesity", "predisposition")]},
    "squirrel": {"chronic": ["Metabolic Bone Disease", "Dental Overgrowth"],
                 "risk": [("Metabolic Bone Disease", "predisposition"), ("Dental Overgrowth", "predisposition")]},
    # --- Avian ---
    "budgie": {"chronic": ["Fatty Liver Disease", "Fatty Tumors (Lipomas)", "Goiter (Iodine Deficiency)"],
               "risk": [("Lipomas", "predisposition"), ("Chronic Egg Laying", "predisposition")]},
    "canary": {"chronic": ["Air Sac Mites", "Feather Cysts"],
               "risk": [("Egg Binding", "predisposition"), ("Air Sac Mites", "husbandry")]},
    "finch": {"chronic": ["Air Sac Mites", "Overgrown Beak"],
              "risk": [("Egg Binding", "predisposition"), ("Air Sac Mites", "husbandry")]},
    "parrot": {"chronic": ["Feather Destructive Behavior (Plucking)", "Fatty Liver Disease", "Chronic Sinusitis"],
               "risk": [("Atherosclerosis", "predisposition"), ("Psittacine Beak and Feather Disease", "predisposition")]},
    "cockatiel": {"chronic": ["Feather Plucking", "Fatty Liver Disease"],
                  "risk": [("Chronic Egg Laying", "predisposition"), ("Fatty Liver Disease", "predisposition")]},
    "conure": {"chronic": ["Feather Plucking", "Chronic Sinusitis"],
               "risk": [("Proventricular Dilatation Disease", "predisposition"), ("Feather Destructive Behavior", "predisposition")]},
    "chicken": {"chronic": ["Chronic Bumblefoot (Pododermatitis)", "Scaly Leg Mites"],
                "risk": [("Marek's Disease", "predisposition"), ("Egg Yolk Peritonitis", "predisposition")]},
    "duck": {"chronic": ["Bumblefoot (Pododermatitis)", "Chronic Sinusitis"],
             "risk": [("Angel Wing", "husbandry"), ("Bumblefoot", "husbandry")]},
    "goose": {"chronic": ["Bumblefoot (Pododermatitis)"],
              "risk": [("Angel Wing", "husbandry"), ("Bumblefoot", "husbandry")]},
    "pigeon": {"chronic": ["Canker (Trichomoniasis)", "Chronic Respiratory Disease"],
               "risk": [("Paramyxovirus", "husbandry"), ("Canker", "husbandry")]},
    "owl": {"chronic": ["Bumblefoot (Pododermatitis)", "Aspergillosis (Respiratory Fungal)"],
            "risk": [("Aspergillosis", "husbandry"), ("Bumblefoot", "husbandry")]},
    "falcon": {"chronic": ["Bumblefoot (Pododermatitis)", "Aspergillosis (Respiratory Fungal)"],
               "risk": [("Aspergillosis", "husbandry"), ("Bumblefoot", "husbandry")]},
    "snowy owl": {"chronic": ["Bumblefoot (Pododermatitis)", "Aspergillosis (Respiratory Fungal)"],
                  "risk": [("Aspergillosis", "husbandry"), ("Bumblefoot", "husbandry")]},
    # --- Reptiles (note: snakes do NOT get MBD — they eat whole prey) ---
    "bearded dragon": {"chronic": ["Metabolic Bone Disease", "Stomatitis (Mouth Rot)", "Chronic Respiratory Infection"],
                       "risk": [("Metabolic Bone Disease", "predisposition"), ("Atadenovirus", "predisposition")]},
    "leopard gecko": {"chronic": ["Metabolic Bone Disease", "Dysecdysis (Shedding Problems)", "Cryptosporidiosis"],
                      "risk": [("Metabolic Bone Disease", "predisposition"), ("Cryptosporidiosis", "husbandry")]},
    "crested gecko": {"chronic": ["Metabolic Bone Disease", "Dysecdysis (Shedding Problems)"],
                      "risk": [("Floppy Tail Syndrome", "predisposition"), ("Metabolic Bone Disease", "predisposition")]},
    "chameleon": {"chronic": ["Metabolic Bone Disease", "Vitamin A Deficiency", "Chronic Respiratory Infection"],
                  "risk": [("Metabolic Bone Disease", "predisposition"), ("Vitamin A Deficiency", "predisposition")]},
    "iguana": {"chronic": ["Metabolic Bone Disease", "Chronic Kidney Disease"],
               "risk": [("Chronic Kidney Disease", "predisposition"), ("Metabolic Bone Disease", "predisposition")]},
    "skink": {"chronic": ["Metabolic Bone Disease", "Dysecdysis (Shedding Problems)"],
              "risk": [("Metabolic Bone Disease", "predisposition"), ("Mites", "husbandry")]},
    "turtle": {"chronic": ["Vitamin A Deficiency", "Shell Rot", "Chronic Respiratory Infection"],
               "risk": [("Vitamin A Deficiency", "predisposition"), ("Shell Rot", "husbandry")]},
    "tortoise": {"chronic": ["Metabolic Bone Disease", "Shell Pyramiding", "Bladder Stones"],
                 "risk": [("Shell Pyramiding", "husbandry"), ("Metabolic Bone Disease", "predisposition")]},
    "corn snake": {"chronic": ["Chronic Respiratory Infection", "Stomatitis (Mouth Rot)", "Scale Rot"],
                   "risk": [("Respiratory Infection", "husbandry"), ("Scale Rot", "husbandry")]},
    "ball python": {"chronic": ["Chronic Respiratory Infection", "Stomatitis (Mouth Rot)", "Scale Rot"],
                    "risk": [("Inclusion Body Disease", "predisposition"), ("Respiratory Infection", "husbandry")]},
    "king snake": {"chronic": ["Chronic Respiratory Infection", "Scale Rot", "Stomatitis (Mouth Rot)"],
                   "risk": [("Respiratory Infection", "husbandry"), ("Scale Rot", "husbandry")]},
    "frog": {"chronic": ["Metabolic Bone Disease", "Red Leg (Bacterial Infection)"],
             "risk": [("Metabolic Bone Disease", "predisposition"), ("Chytrid Fungus", "husbandry")]},
    "toad": {"chronic": ["Metabolic Bone Disease", "Obesity"],
             "risk": [("Metabolic Bone Disease", "predisposition"), ("Red Leg", "husbandry")]},
    "newt": {"chronic": ["Chronic Skin Infection", "Chytridiomycosis"],
             "risk": [("Chytrid Fungus", "husbandry"), ("Metabolic Bone Disease", "predisposition")]},
    "salamander": {"chronic": ["Metabolic Bone Disease", "Chytridiomycosis"],
                   "risk": [("Chytrid Fungus", "husbandry"), ("Metabolic Bone Disease", "predisposition")]},
    # --- Fish (fin rot / ich / dropsy are husbandry-driven, not inherited;
    #     only fancy goldfish & long-finned bettas have a conformational risk) ---
    "goldfish": {"chronic": ["Swim Bladder Disorder", "Chronic Ich", "Fin Rot"],
                 "risk": [("Swim Bladder Disorder", "predisposition"), ("Fin Rot", "husbandry")]},
    "betta": {"chronic": ["Fin Rot", "Swim Bladder Disorder", "Chronic Ich"],
              "risk": [("Fin Damage (long-fin conformation)", "predisposition"), ("Fin Rot", "husbandry")]},
}
# Fallback profiles for exotics not individually listed above.
EXOTIC_CATEGORY_DEFAULTS = {
    "mammal": {"chronic": ["Dental Overgrowth", "Chronic Respiratory Disease", "Obesity"],
               "risk": [("Dental Overgrowth", "predisposition"), ("Respiratory Infection", "husbandry")]},
    "avian": {"chronic": ["Feather Plucking", "Fatty Liver Disease", "Chronic Sinusitis"],
              "risk": [("Fatty Liver Disease", "predisposition"), ("Aspergillosis", "husbandry")]},
    "reptile": {"chronic": ["Metabolic Bone Disease", "Chronic Respiratory Infection", "Dysecdysis (Shedding Problems)"],
                "risk": [("Metabolic Bone Disease", "predisposition"), ("Respiratory Infection", "husbandry")]},
    "fish": {"chronic": ["Chronic Ich", "Fin Rot", "Swim Bladder Disorder"],
             "risk": [("Ich (White Spot)", "husbandry"), ("Fin Rot", "husbandry")]},
}

# Behavior notes a vet clinic might keep on file.
DOG_BEHAVIOR_NOTES = [
    "Friendly with strangers", "Pulls hard on leash", "Anxious during thunderstorms",
    "Food-motivated, easy to train", "Barks at delivery drivers",
    "Gets along well with other dogs", "Nervous at the vet — approach slowly",
    "High energy, needs daily walks", "Separation anxiety when left alone",
    "Protective of food bowl", "Excellent recall off-leash",
    "Scared of vacuum cleaners", "Jumps on guests when excited",
    "Calm and gentle with children", "Loves belly rubs",
]
CAT_BEHAVIOR_NOTES = [
    "Shy — hides from strangers", "Very vocal, especially at mealtimes",
    "Does not tolerate nail trims", "Loves lap time", "Midnight zoomies",
    "Swats when overstimulated", "Indoor only — known door-dasher",
    "Gets along with other cats", "Hisses at the carrier",
    "Enjoys being brushed", "Knocks things off tables",
    "Friendly with dogs", "Needs slow introductions to new people",
    "Territorial around the litter box",
]


def realistic_weight(species):
    """Return a random but species-appropriate weight string like '14 lbs' or '85 g'."""
    lo, hi, unit = WEIGHT_RANGES[species]
    return f"{random.randint(lo, hi)} {unit}"


def random_allergies():
    """Return 1-2 random allergies for a dog/cat, or 'No Allergies' about half the time."""
    if random.random() < 0.5:
        return "No Allergies"
    return ", ".join(random.sample(DOG_CAT_ALLERGIES, random.randint(1, 2)))


def random_behavior_notes(species):
    """Return 1-2 species-appropriate behavior notes for a dog or cat."""
    notes = DOG_BEHAVIOR_NOTES if species == "dog" else CAT_BEHAVIOR_NOTES
    return "; ".join(random.sample(notes, random.randint(1, 2)))


def plural(word):
    """Pluralize a species or breed name ('finch' -> 'finches', 'husky' -> 'huskies')."""
    if word in ("mice", "geese") or word.endswith("fish"):
        return word
    if word == "mouse":
        return "mice"
    if word == "goose":
        return "geese"
    if word.endswith("y") and word[-2].lower() not in "aeiou":
        return word[:-1] + "ies"
    if word.endswith(("s", "sh", "ch", "x")):
        return word + "es"
    return word + "s"


def _condition_min_age(condition):
    """Youngest age (years) at which a condition realistically appears; 0 if any age."""
    for key, min_age in CONDITION_MIN_AGE.items():
        if key.lower() in condition.lower():
            return min_age
    return 0


def _allowed_for_sex(condition, sex):
    """False only for female-only reproductive conditions in a non-female pet."""
    if sex == "Female":
        return True
    return not any(f.lower() in condition.lower() for f in FEMALE_ONLY)


def _format_marker(condition, kind, subject):
    """Phrase an at-risk marker according to whether it's inherited, a tendency, or husbandry."""
    if kind == "hereditary":
        return f"Hereditary risk — {condition}: hereditary in {subject} — not present, monitor at checkups"
    if kind == "husbandry":
        return f"Husbandry watch-point — {condition}: environmental, not inherited — maintain proper care"
    return f"Species predisposition — {condition}: {subject} are prone to this — not present, monitor at checkups"


def random_medical_history(species, category, breed=None, age=1, sex=None):
    """Build a chronic_conditions list: an age/sex-appropriate diagnosis (~45%) plus a risk marker."""
    if breed is not None:  # dog or cat
        chronic_pool = DOG_CHRONIC if species == "dog" else CAT_CHRONIC
        risk_table = DOG_BREED_RISKS if species == "dog" else CAT_BREED_RISKS
        risks = [(condition, "hereditary") for condition in risk_table[breed]]
        subject = plural(breed)
    else:
        profile = EXOTIC_PROFILES.get(species, EXOTIC_CATEGORY_DEFAULTS[category])
        chronic_pool = profile["chronic"]
        risks = profile["risk"]
        subject = plural(species)

    entries = []

    # Breeds whose defining trait is itself a condition always carry it.
    if breed in BREED_ALWAYS_HAS:
        entries.append(BREED_ALWAYS_HAS[breed])

    # ~45% of pets carry an actual diagnosis, filtered to be age- and sex-appropriate.
    if random.random() < 0.45:
        eligible = [c for c in chronic_pool
                    if age >= _condition_min_age(c) and _allowed_for_sex(c, sex)]
        for condition in random.sample(eligible, min(len(eligible), random.randint(1, 2))):
            entries.append(f"{condition}: {random.choice(CONDITION_NOTES)}")

    # One risk marker: a predisposition the pet does NOT currently have.
    open_risks = [(c, k) for c, k in risks
                  if _allowed_for_sex(c, sex) and not any(e.startswith(c) for e in entries)]
    if open_risks:
        condition, kind = random.choice(open_risks)
        entries.append(_format_marker(condition, kind, subject))
    elif breed is not None and not risks:
        entries.append("Hereditary risk: none identified (mixed ancestry)")

    return entries


def generate_random_pet(pet_name, species_tuple):
    """Build a Pet with standard stats for dogs/cats or 'hacked' stats for exotics."""
    species, category = species_tuple

    if species in ["dog", "cat"]:
        breeds = DOG_BREEDS if species == "dog" else CAT_BREEDS
        breed = random.choice(list(breeds))
        low, high = breeds[breed]
        age, sex = random.randint(1, 15), random.choice(["Male", "Female"])
        return Pet(
            name=pet_name, species=species, breed=breed, age=age, sex=sex,
            weight=f"{random.randint(low, high)} lbs", height=f"{random.randint(10, 30)} inches",
            allergies=random_allergies(), behavioral_notes=random_behavior_notes(species),
            chronic_conditions=random_medical_history(species, category, breed, age, sex),
            color_markings=random.choice(["Black", "White", "Brown", "Spotted", "Golden", "Tabby", "Calico"]),
            spayed_neutered=random.choice(["Yes", "No"]), microchip_number=f"9810{random.randint(100000000, 999999999)}",
            diet_good=["Dry Kibble", "Wet Food", "Carrots"], diet_bad=["Chocolate", "Grapes", "Onions", "Garlic"]
        )
    elif category == "mammal":
        age, sex = random.randint(1, 5), random.choice(["Male", "Female"])
        return Pet(
            name=pet_name, species=species, age=age, sex=sex,
            weight=realistic_weight(species), height="Small",
            chronic_conditions=random_medical_history(species, category, age=age, sex=sex),
            color_markings=random.choice(["Agouti", "White", "Black", "Spotted", "Albino"]),
            spayed_neutered=random.choice(["Yes", "No"]), diet_good=["Timothy Hay", "Pellets", "Fresh Veggies"],
            diet_bad=["Sugary fruits", "Seeds"]
        )
    elif category == "avian":
        age, sex = random.randint(1, 20), random.choice(["Male", "Female"])
        return Pet(
            name=pet_name, species=species, age=age, sex=sex,
            weight=realistic_weight(species), height=f"Wingspan: {random.randint(10, 30)} inches",
            chronic_conditions=random_medical_history(species, category, age=age, sex=sex),
            color_markings=random.choice(["Green", "Blue", "Yellow", "White", "Multi-colored"]),
            microchip_number=f"Leg Band # {random.randint(1000,9999)}", diet_good=["Seeds", "Pellets", "Fresh Fruit"],
            diet_bad=["Avocado", "Chocolate"]
        )
    elif category == "reptile":
        age, sex = random.randint(1, 15), random.choice(["Male", "Female"])
        return Pet(
            name=pet_name, species=species, age=age, sex=sex,
            weight=realistic_weight(species), color_markings=random.choice(["Green", "Brown", "Orange Morph", "Striped"]),
            chronic_conditions=random_medical_history(species, category, age=age, sex=sex),
            allergies=f"Enclosure Temp: {random.randint(75, 95)}°F", diet_good=["Insects", "Leafy Greens", "Worms"],
            diet_bad=["Fireflies", "Iceberg Lettuce"]
        )
    elif category == "fish":
        age = random.randint(1, 5)
        water_type = random.choice(["Freshwater", "Saltwater / Marine"])
        return Pet(
            name=pet_name, species=species, age=age, sex="Unknown",
            weight=f"{water_type} · Tank Size: {random.choice([10, 20, 30, 50, 100])} Gallons",
            chronic_conditions=random_medical_history(species, category, age=age, sex="Unknown"),
            color_markings=random.choice(["Iridescent", "Neon", "Red", "Blue", "Striped"]),
            diet_good=["Flakes", "Bloodworms", "Brine Shrimp"],
            diet_bad=["Wrong water type"]
        )


def build_distribution(total):
    """Plan one species per owner: all species once, then ~20% dogs, ~20% cats, rest random exotics."""
    distribution = list(SPECIES)  # guarantees every species appears at least once

    extra = total - len(distribution)
    extra_dogs = total // 5 - 1   # -1 because one dog/cat is already guaranteed above
    extra_cats = total // 5 - 1
    distribution += [("dog", "mammal")] * extra_dogs + [("cat", "mammal")] * extra_cats
    distribution += [random.choice(EXOTIC_SPECIES) for _ in range(extra - extra_dogs - extra_cats)]

    random.shuffle(distribution)
    return distribution


def seed_master_list():
    """Rebuild data.json from scratch with the full combined clinic roster."""
    distribution = build_distribution(len(OWNER_NAMES))

    owners = []
    for i, owner_name in enumerate(OWNER_NAMES):
        owner = Owner(owner_name)
        pet = generate_random_pet(PET_NAMES[i % len(PET_NAMES)], distribution[i])
        owner.add_pet(pet)
        owners.append(owner)

    save_owners_to_json(owners, DATA_PATH)

    dogs = sum(1 for d in distribution if d[0] == "dog")
    cats = sum(1 for d in distribution if d[0] == "cat")
    unique_species = len({d[0] for d in distribution})
    print(f"🏥 MASTER CLINIC BUILT! {len(owners)} owners: {dogs} dogs, {cats} cats, "
          f"{len(owners) - dogs - cats} exotics ({unique_species} unique species, all represented).")


if __name__ == "__main__":
    seed_master_list()
