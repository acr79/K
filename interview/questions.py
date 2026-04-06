"""Interview question bank — seeds K's profile across all domains."""

# Each question has:
#   id        — unique key
#   domain    — which profile area it feeds
#   question  — what K asks
#   follow_up — optional follow-up if answer is shallow
#   extract   — what structured data to pull from the answer

QUESTIONS = [

    # ── Foundation ────────────────────────────────────────────────────────────
    {
        "id": "location",
        "domain": "general",
        "question": "Where are you based right now, and does that change seasonally?",
        "extract": ["location", "seasonal_travel"]
    },
    {
        "id": "lifestyle",
        "domain": "general",
        "question": "How would you describe your lifestyle — are you more urban, outdoors, both?",
        "extract": ["lifestyle_type"]
    },
    {
        "id": "work",
        "domain": "general",
        "question": "What do you do for work, and how technical are you day to day?",
        "extract": ["occupation", "tech_level"]
    },
    {
        "id": "retirement",
        "domain": "general",
        "question": "You mentioned you're approaching retirement — what does that transition look like for you?",
        "extract": ["career_stage", "consulting_interest"]
    },

    # ── Buying philosophy ─────────────────────────────────────────────────────
    {
        "id": "buy_philosophy",
        "domain": "buying",
        "question": "When you're about to buy something significant, what's your process? Do you research deeply, go with gut, ask people?",
        "extract": ["research_style", "decision_making"]
    },
    {
        "id": "buy_regret",
        "domain": "buying",
        "question": "What's a purchase you regret, and why? What did you miss in your research?",
        "extract": ["regret_pattern", "research_gap"]
    },
    {
        "id": "buy_quality",
        "domain": "buying",
        "question": "Are you a buy-once-buy-right person, or do you iterate and upgrade?",
        "extract": ["quality_vs_iteration"]
    },
    {
        "id": "budget_style",
        "domain": "buying",
        "question": "Is budget a hard constraint for you, or does the right thing justify the price?",
        "extract": ["budget_philosophy"]
    },

    # ── Firearms ──────────────────────────────────────────────────────────────
    {
        "id": "guns_overview",
        "domain": "firearms",
        "question": "Give me the 30-second overview of your gun collection — size, what types, what you're focused on.",
        "extract": ["collection_size", "gun_types", "collection_focus"]
    },
    {
        "id": "guns_use",
        "domain": "firearms",
        "question": "What do you actually use them for — range, carry, home defense, collecting?",
        "extract": ["gun_use_cases"]
    },
    {
        "id": "guns_brands",
        "domain": "firearms",
        "question": "Do you have brand loyalties or preferences? Anything you'd never buy?",
        "extract": ["gun_brand_preferences", "gun_brand_avoid"]
    },
    {
        "id": "guns_ca",
        "domain": "firearms",
        "question": "You're in California — how much does CA compliance factor into what you buy and own?",
        "extract": ["ca_compliance_priority"]
    },
    {
        "id": "guns_maintenance",
        "domain": "firearms",
        "question": "How disciplined are you about maintenance? Do you track it or go by feel?",
        "extract": ["maintenance_style"]
    },
    {
        "id": "guns_next",
        "domain": "firearms",
        "question": "Is there something specific you're looking for next, or a gap in the collection?",
        "extract": ["guns_wishlist"]
    },

    # ── Outdoor gear / clothing ───────────────────────────────────────────────
    {
        "id": "gear_overview",
        "domain": "gear",
        "question": "You have a large Arcteryx and Patagonia collection. How did that build up — are you a technical user or more of a collector?",
        "extract": ["gear_user_type", "collection_origin"]
    },
    {
        "id": "gear_use",
        "domain": "gear",
        "question": "What activities do you actually gear up for? Hiking, skiing, urban, travel?",
        "extract": ["gear_activities"]
    },
    {
        "id": "gear_gaps",
        "domain": "gear",
        "question": "You mentioned New York weather — what conditions do you feel least covered for right now?",
        "extract": ["gear_gaps", "current_location_needs"]
    },
    {
        "id": "gear_buy_trigger",
        "domain": "gear",
        "question": "What makes you pull the trigger on a new piece of gear? New colorway, new tech, specific gap?",
        "extract": ["gear_purchase_trigger"]
    },
    {
        "id": "gear_arcteryx_depth",
        "domain": "gear",
        "question": "With Arcteryx specifically — do you follow their product lines closely? Do you know the difference between the Atom LT, SL, AR off the top of your head?",
        "extract": ["arcteryx_expertise", "arcteryx_lines_known"]
    },

    # ── Health ────────────────────────────────────────────────────────────────
    {
        "id": "health_overview",
        "domain": "health",
        "question": "Health-wise — are you active, do you train, and are supplements already part of your routine?",
        "extract": ["activity_level", "supplement_use"]
    },
    {
        "id": "health_goals",
        "domain": "health",
        "question": "What are you optimizing for — performance, longevity, recovery, weight?",
        "extract": ["health_goals"]
    },
    {
        "id": "health_trusted_sources",
        "domain": "health",
        "question": "Who or what do you trust for health advice — doctors, podcasters, research, experience?",
        "extract": ["health_info_sources"]
    },

    # ── Finance ───────────────────────────────────────────────────────────────
    {
        "id": "finance_overview",
        "domain": "finance",
        "question": "How hands-on are you with your finances — do you manage investments yourself or delegate?",
        "extract": ["finance_hands_on"]
    },
    {
        "id": "finance_goals",
        "domain": "finance",
        "question": "Approaching retirement — what does financial security look like for you in that phase?",
        "extract": ["retirement_financial_goals"]
    },

    # ── Tech ─────────────────────────────────────────────────────────────────
    {
        "id": "tech_depth",
        "domain": "tech",
        "question": "You're building your own LLM system — how deep does your technical background go? Software, hardware, both?",
        "extract": ["tech_background", "coding_experience"]
    },
    {
        "id": "tech_interests",
        "domain": "tech",
        "question": "What tech rabbit holes do you fall into? AI is clearly one — what else?",
        "extract": ["tech_interests"]
    },
    {
        "id": "tech_consulting",
        "domain": "tech",
        "question": "You mentioned wanting to consult and build a coding agent. What problem are you most interested in solving?",
        "extract": ["consulting_focus", "product_idea"]
    },

    # ── Learning style ────────────────────────────────────────────────────────
    {
        "id": "learning_depth",
        "domain": "learning",
        "question": "When you go deep on something — like vector search today — what does good look like? Implementation details, conceptual understanding, both?",
        "extract": ["learning_depth_preference"]
    },
    {
        "id": "learning_format",
        "domain": "learning",
        "question": "Do you prefer things explained with analogies and examples, or straight technical detail?",
        "extract": ["explanation_style_preference"]
    },
    {
        "id": "learning_pace",
        "domain": "learning",
        "question": "Do you like to be challenged and pushed further, or do you prefer to set the pace?",
        "extract": ["learning_pace_preference"]
    },

    # ── K usage ───────────────────────────────────────────────────────────────
    {
        "id": "k_frustration",
        "domain": "k_usage",
        "question": "You've been using ChatGPT like a personal assistant for a year. What's the most frustrating thing about it?",
        "extract": ["chatgpt_frustrations"]
    },
    {
        "id": "k_ideal",
        "domain": "k_usage",
        "question": "Finish this sentence: K would be perfect if it could...",
        "extract": ["k_ideal_capability"]
    },
]


def get_questions_for_domain(domain: str) -> list[dict]:
    return [q for q in QUESTIONS if q["domain"] == domain]


def get_all_domains() -> list[str]:
    return list(dict.fromkeys(q["domain"] for q in QUESTIONS))
