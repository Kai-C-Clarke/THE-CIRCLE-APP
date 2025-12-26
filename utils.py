# utils.py - Utility functions with universal age-aware categorization
import re
from datetime import datetime
import os


def parse_date_input(date_input):
    """Parse various date formats."""
    date_input = date_input.strip()
    if not date_input:
        return None, None

    # Try year only
    year_match = re.match(r"^\s*(\d{4})\s*$", date_input)
    if year_match:
        return None, int(year_match.group(1))

    # Try month year
    month_year = re.match(r"^\s*([A-Za-z]+)\s+(\d{4})\s*$", date_input, re.IGNORECASE)
    if month_year:
        return f"{month_year.group(1)} {month_year.group(2)}", int(month_year.group(2))

    return None, None


def get_user_birth_year():
    """Get user's birth year from profile table."""
    try:
        from database import get_db

        db = get_db()
        cursor = db.execute("SELECT birth_date FROM user_profile LIMIT 1")
        result = cursor.fetchone()

        if result and result[0]:
            birth_date = result[0]
            # birth_date could be "1955-02-28" or just "1955"
            year_match = re.search(r"(\d{4})", birth_date)
            if year_match:
                return int(year_match.group(1))
    except Exception as e:
        print(f"Could not get birth year from profile: {e}")

    return None


def calculate_age(memory_year):
    """Calculate user's age at time of memory."""
    birth_year = get_user_birth_year()
    if birth_year and memory_year:
        return memory_year - birth_year
    return None


def get_life_phase(age):
    """Determine life phase based on age."""
    if age is None:
        return None

    if age < 0:
        return "family-history"  # Before user was born
    elif age <= 12:
        return "childhood"
    elif age <= 19:
        return "teenage"
    elif age <= 25:
        return "young-adult"
    elif age <= 65:
        return "adult"
    else:
        return "senior"


def categorize_memory(text, year=None):
    """
    Categorize memory using AI with automatic age calculation.
    Falls back to keyword matching if AI unavailable.
    """
    # Calculate age from user's profile
    age = calculate_age(year) if year else None

    # Try AI categorization first
    try:
        from openai import OpenAI

        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

            # Build context with age if available
            context = ""
            if age is not None:
                life_phase = get_life_phase(age)
                context = (
                    f"The person was {age} years old ({life_phase} phase) in {year}. "
                )
            elif year:
                context = f"This memory is from {year}. "

            prompt = f"""{context}Categorize this memory into ONE category. Choose the MOST appropriate:

Categories:
- childhood (ages 0-12)
- teenage (ages 13-19)
- young-adult (ages 20-25)
- education (school, college, university - any age)
- work (employment, jobs, career)
- music (bands, playing instruments, performances)
- family (family members, relationships, births, deaths)
- travel (trips, holidays, vacations)
- military (service, armed forces)
- hobbies (sports, games, pastimes)
- life-event (major milestones: graduation, marriage, retirement)
- family-history (events before the person was born)
- other (if none fit)

IMPORTANT: Consider the person's age. A 30-year-old at work is "work", not "education". 
A 10-year-old playing is "childhood". Band activities are "music".

Memory: "{text[:500]}"

Respond with ONLY the category name, nothing else."""

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.3,
            )

            category = response.choices[0].message.content.strip().lower()

            # Validate it's a real category
            valid_categories = [
                "childhood",
                "teenage",
                "young-adult",
                "education",
                "work",
                "music",
                "family",
                "travel",
                "military",
                "hobbies",
                "life-event",
                "family-history",
                "other",
            ]

            if category in valid_categories:
                return category

    except Exception as e:
        print(f"AI categorization failed, using fallback: {e}")

    # Fallback: Improved keyword matching with age context
    text_lower = text.lower()

    # Age-based pre-filtering
    if age is not None:
        if age < 0:
            return "family-history"
        elif age <= 12 and any(
            word in text_lower for word in ["born", "baby", "child", "primary school"]
        ):
            return "childhood"
        elif 13 <= age <= 19 and any(
            word in text_lower
            for word in ["secondary school", "high school", "gcse", "a-level"]
        ):
            return "teenage"

    # Keyword-based categorization (prioritized by specificity)
    categories = [
        (
            "family-history",
            [
                "before i was born",
                "my mother was born",
                "my father was born",
                "my grandmother",
                "my grandfather",
            ],
        ),
        (
            "music",
            [
                "band",
                "bass",
                "guitar",
                "drums",
                "singer",
                "gig",
                "concert",
                "musician",
                "rehearsal",
                "played in",
                "performed",
            ],
        ),
        (
            "military",
            [
                "army",
                "navy",
                "air force",
                "military",
                "service",
                "soldier",
                "regiment",
                "deployed",
                "enlisted",
            ],
        ),
        (
            "work",
            [
                "worked at",
                "job",
                "career",
                "employed",
                "serving",
                "manager",
                "company",
                "office",
                "colleague",
                "boss",
                "garage",
                "petrol station",
                "hired",
                "salary",
            ],
        ),
        (
            "education",
            [
                "school",
                "college",
                "university",
                "teacher",
                "student",
                "class",
                "exam",
                "degree",
                "studying",
                "graduated",
                "claverham",
                "primary",
            ],
        ),
        (
            "life-event",
            [
                "was born",
                "birth",
                "married",
                "wedding",
                "died",
                "funeral",
                "graduated",
                "retired",
                "moved house",
            ],
        ),
        (
            "family",
            [
                "mother",
                "father",
                "parent",
                "sibling",
                "daughter",
                "son",
                "wife",
                "husband",
                "sister",
                "brother",
                "uncle",
                "aunt",
                "cousin",
            ],
        ),
        (
            "travel",
            [
                "traveled",
                "trip",
                "vacation",
                "holiday",
                "journey",
                "visited",
                "abroad",
                "flew to",
                "drove to",
            ],
        ),
        (
            "hobbies",
            [
                "hobby",
                "sport",
                "fishing",
                "cycling",
                "running",
                "painting",
                "photography",
                "played football",
                "played cricket",
            ],
        ),
    ]

    # Count matches for each category
    best_category = "other"
    best_score = 0

    for category, keywords in categories:
        # Give more weight to multi-word matches
        score = 0
        for keyword in keywords:
            if keyword in text_lower:
                score += len(keyword.split())  # Multi-word phrases score higher

        if score > best_score:
            best_score = score
            best_category = category

    # If no strong matches and we have age, use life-phase defaults
    if best_score == 0 and age is not None:
        if age < 0:
            return "family-history"
        elif age <= 12:
            return "childhood"
        elif 13 <= age <= 19:
            return "teenage"
        elif 20 <= age <= 25:
            return "young-adult"
        else:
            return "adult-life"

    return best_category


def allowed_file(filename, file_type):
    """Check if file extension is allowed."""
    allowed_extensions = {
        "image": ["jpg", "jpeg", "png", "gif", "webp"],
        "audio": ["mp3", "wav", "ogg", "m4a"],
        "video": ["mp4", "mov", "avi"],
        "document": ["pdf", "doc", "docx"],
    }

    if "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions.get(file_type, [])
