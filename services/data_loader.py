import json
from pathlib import Path
from typing import List, Dict, Any

DATA_DIR = Path(__file__).parent.parent / "data"

def load_courses() -> List[Dict[str, Any]]:
    courses_file = DATA_DIR / "courses.json"
    if not courses_file.exists():
        return []
    with open(courses_file, "r", encoding="utf-8") as f:
        return json.load(f)

def load_careers() -> Dict[str, Any]:
    careers_file = DATA_DIR / "careers.json"
    if not careers_file.exists():
        return {}
    with open(careers_file, "r", encoding="utf-8") as f:
        return json.load(f)

def get_universities() -> List[str]:
    courses = load_courses()
    unis = list(dict.fromkeys(c["university"] for c in courses if "university" in c))
    # Keep University A, University B first if present
    preferred_order = ["University A", "University B", "Chulalongkorn University", "Thammasat University", "Mahidol University", "KMUTT"]
    sorted_unis = [u for u in preferred_order if u in unis] + [u for u in sorted(unis) if u not in preferred_order]
    return sorted_unis

def get_all_skills() -> List[str]:
    courses = load_courses()
    careers = load_careers()
    skills = set()
    for c in courses:
        for s in c.get("skills_covered", []):
            skills.add(s)
    for role, data in careers.items():
        for s in data.get("required_skills", []):
            skills.add(s)
        for s in data.get("core_skills", []):
            skills.add(s)
        for s in data.get("advanced_skills", []):
            skills.add(s)
    return sorted(list(skills))
