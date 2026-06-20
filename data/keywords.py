# -----------------------------------------------------------------------------
# SmartLead AI – Keyword Generation Engine
# Tiered intent keywords per domain.
# HIGH intent keywords carry the most weight in lead scoring.
# -----------------------------------------------------------------------------

DOMAIN_KEYWORDS = {

    "Aviation": {
        "subcategories": [
            "Pilot Training",
            "Flight School",
            "Aviation Courses",
            "Commercial Pilot License",
            "Air Traffic Control"
        ],
        "high_intent": [
            "want to become a pilot",
            "pilot training fees",
            "how to enroll",
            "admission open",
            "apply now",
            "commercial pilot license",
            "cpl training",
            "pilot course fees",
            "flight school admission",
            "enroll aviation",
        ],
        "medium_intent": [
            "pilot training",
            "aviation course",
            "flight school",
            "become a pilot",
            "aviation academy",
            "flight training",
            "pilot license",
            "aviation program",
            "atpl",
            "instrument rating",
        ],
        "low_intent": [
            "aviation",
            "aircraft",
            "flying",
            "airplane",
            "pilot",
            "runway",
            "airline",
            "cockpit",
            "airport",
            "helicopter",
        ],
    },

    "Laptops": {
        "subcategories": [
            "Gaming Laptops",
            "Coding / Developer Laptops",
            "Budget Laptops",
            "Business Laptops",
            "MacBook"
        ],
        "high_intent": [
            "want to buy laptop",
            "best laptop to buy",
            "which laptop should i buy",
            "laptop price",
            "laptop under budget",
            "where to buy laptop",
            "purchase laptop",
            "laptop deal",
            "laptop discount",
            "laptop offer",
        ],
        "medium_intent": [
            "laptop review",
            "best laptop",
            "laptop comparison",
            "gaming laptop",
            "coding laptop",
            "laptop for students",
            "dell laptop",
            "hp laptop",
            "lenovo laptop",
            "macbook",
        ],
        "low_intent": [
            "laptop",
            "computer",
            "notebook",
            "display",
            "processor",
            "ram",
            "storage",
            "battery",
            "keyboard",
            "screen",
        ],
    },

    "Colleges": {
        "subcategories": [
            "Engineering Admission",
            "MBA Admission",
            "Medical Admission",
            "Scholarship Programs",
            "College Counseling"
        ],
        "high_intent": [
            "how to apply",
            "admission form",
            "college admission open",
            "last date to apply",
            "scholarship apply",
            "need counselor",
            "college fees structure",
            "admission process",
            "entrance exam date",
            "need college details",
        ],
        "medium_intent": [
            "college admission",
            "engineering admission",
            "mba admission",
            "scholarship",
            "university",
            "entrance exam",
            "college counseling",
            "college review",
            "best college",
            "medical admission",
        ],
        "low_intent": [
            "college",
            "university",
            "campus",
            "degree",
            "semester",
            "lecture",
            "professor",
            "hostel",
            "placement",
            "student life",
        ],
    },

    "Courses": {
        "subcategories": [
            "Data Science",
            "Artificial Intelligence",
            "Machine Learning",
            "Python Training",
            "Full Stack Development"
        ],
        "high_intent": [
            "want to join course",
            "course fees",
            "how to enroll",
            "course details",
            "batch starting",
            "online course registration",
            "certification course",
            "course syllabus",
            "course duration",
            "enroll now",
        ],
        "medium_intent": [
            "data science course",
            "ai course",
            "machine learning course",
            "python training",
            "online course",
            "it course",
            "programming course",
            "course review",
            "best course",
            "skill development",
        ],
        "low_intent": [
            "course",
            "learning",
            "tutorial",
            "training",
            "skill",
            "certificate",
            "programming",
            "coding",
            "technology",
            "education",
        ],
    },

    "Real Estate": {
        "subcategories": [
            "Residential Properties",
            "Commercial Properties",
            "Rental Properties",
            "Plots & Land",
            "Luxury Homes"
        ],
        "high_intent": [
            "want to buy property",
            "property price",
            "site visit",
            "book flat",
            "home loan",
            "emi calculator",
            "plot for sale",
            "flat booking amount",
            "ready to move",
            "property investment",
        ],
        "medium_intent": [
            "buy flat",
            "real estate",
            "property for sale",
            "2bhk",
            "3bhk",
            "apartment",
            "villa",
            "plot",
            "rental property",
            "housing project",
        ],
        "low_intent": [
            "property",
            "house",
            "flat",
            "area",
            "location",
            "construction",
            "builder",
            "society",
            "tower",
            "floor",
        ],
    },

    "Jobs": {
        "subcategories": [
            "IT Jobs",
            "Government Jobs",
            "Freshers Jobs",
            "Remote Jobs",
            "Management Jobs"
        ],
        "high_intent": [
            "looking for job",
            "need job urgently",
            "job application",
            "how to apply job",
            "walk in interview",
            "send resume",
            "vacancy available",
            "job opening",
            "hiring now",
            "recruitment process",
        ],
        "medium_intent": [
            "job search",
            "it job",
            "government job",
            "fresher job",
            "remote job",
            "job vacancy",
            "interview tips",
            "job portal",
            "career opportunity",
            "salary package",
        ],
        "low_intent": [
            "job",
            "career",
            "work",
            "employment",
            "resume",
            "interview",
            "company",
            "recruiter",
            "hire",
            "office",
        ],
    },

    "Insurance": {
        "subcategories": [
            "Life Insurance",
            "Health Insurance",
            "Car Insurance",
            "Term Plans",
            "Investment Plans"
        ],
        "high_intent": [
            "want insurance",
            "buy insurance policy",
            "insurance premium",
            "insurance quote",
            "policy details",
            "claim process",
            "best term plan",
            "health cover",
            "insurance renewal",
            "compare insurance",
        ],
        "medium_intent": [
            "life insurance",
            "health insurance",
            "term insurance",
            "car insurance",
            "insurance plan",
            "coverage amount",
            "maturity benefit",
            "premium calculator",
            "insurance review",
            "policy comparison",
        ],
        "low_intent": [
            "insurance",
            "policy",
            "cover",
            "premium",
            "claim",
            "benefit",
            "nominee",
            "risk",
            "investment",
            "maturity",
        ],
    },

    "Cars": {
        "subcategories": [
            "Hatchback",
            "SUV",
            "Sedan",
            "Electric Vehicles",
            "Luxury Cars"
        ],
        "high_intent": [
            "want to buy car",
            "car price",
            "test drive",
            "car booking",
            "car loan emi",
            "best car to buy",
            "car delivery",
            "car discount offer",
            "on road price",
            "exchange offer",
        ],
        "medium_intent": [
            "car review",
            "best suv",
            "electric car",
            "car comparison",
            "mileage",
            "fuel efficiency",
            "car features",
            "car launch",
            "new car 2025",
            "car dealership",
        ],
        "low_intent": [
            "car",
            "vehicle",
            "engine",
            "speed",
            "drive",
            "model",
            "color",
            "variant",
            "automatic",
            "manual",
        ],
    },

    "Training Programs": {
        "subcategories": [
            "Corporate Training",
            "Soft Skills",
            "Leadership Training",
            "Sales Training",
            "Digital Marketing"
        ],
        "high_intent": [
            "interested in training",
            "training program fees",
            "corporate training inquiry",
            "enroll training",
            "batch schedule",
            "training certification",
            "workshop registration",
            "need trainer",
            "group training",
            "training program details",
        ],
        "medium_intent": [
            "corporate training",
            "soft skills training",
            "leadership program",
            "sales training",
            "digital marketing training",
            "professional development",
            "upskilling program",
            "employee training",
            "workshop",
            "bootcamp",
        ],
        "low_intent": [
            "training",
            "program",
            "workshop",
            "skill",
            "development",
            "mentor",
            "coaching",
            "session",
            "module",
            "seminar",
        ],
    },

    "Mobiles": {
        "subcategories": [
            "Flagship Phones",
            "Budget Phones",
            "Gaming Phones",
            "5G Phones",
            "Camera Phones"
        ],
        "high_intent": [
            "want to buy phone",
            "mobile price",
            "best phone to buy",
            "which mobile should i buy",
            "mobile under budget",
            "phone offer",
            "pre-order mobile",
            "purchase smartphone",
            "mobile deal",
            "compare phones",
        ],
        "medium_intent": [
            "mobile review",
            "best smartphone",
            "5g phone",
            "gaming phone",
            "camera phone",
            "iphone",
            "samsung",
            "oneplus",
            "redmi",
            "realme",
        ],
        "low_intent": [
            "phone",
            "mobile",
            "smartphone",
            "screen",
            "battery",
            "camera",
            "processor",
            "storage",
            "ram",
            "display",
        ],
    },

    "Coding Bootcamps": {
        "subcategories": [
            "Web Development Bootcamp",
            "Data Science Bootcamp",
            "Cybersecurity Bootcamp",
            "UI/UX Design",
            "DevOps & Cloud"
        ],
        "high_intent": [
            "join bootcamp",
            "bootcamp fees",
            "bootcamp schedule",
            "bootcamp enrollment",
            "career switch bootcamp",
            "placement guarantee",
            "bootcamp review",
            "which bootcamp to join",
            "bootcamp scholarship",
            "full stack bootcamp",
        ],
        "medium_intent": [
            "coding bootcamp",
            "web development bootcamp",
            "data science bootcamp",
            "full stack",
            "programming bootcamp",
            "online bootcamp",
            "tech bootcamp",
            "career change",
            "job ready",
            "intensive program",
        ],
        "low_intent": [
            "bootcamp",
            "coding",
            "programming",
            "development",
            "tech",
            "software",
            "web",
            "app",
            "backend",
            "frontend",
        ],
    },
}


def get_keywords_for_domain(domain: str) -> dict:
    """Return the full keyword dict for a domain."""
    return DOMAIN_KEYWORDS.get(domain, {})


def get_all_keywords_flat(domain: str) -> list:
    """Return a flat list of all keywords for a domain."""
    kw = DOMAIN_KEYWORDS.get(domain, {})
    return (
        kw.get("high_intent", [])
        + kw.get("medium_intent", [])
        + kw.get("low_intent", [])
    )


def get_domain_list() -> list:
    """Return sorted list of all supported domains."""
    return sorted(DOMAIN_KEYWORDS.keys())


def get_subcategories(domain: str) -> list:
    """Return subcategories for a given domain."""
    return DOMAIN_KEYWORDS.get(domain, {}).get("subcategories", [])
