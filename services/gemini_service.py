import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.output_schema import UniversityComparisonResult, CareerPlanAnalysisResult, RecommendedCourse, StudyPlanPhase
from services.data_loader import load_courses, load_careers

load_dotenv()

def get_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key or key.strip() in ["", "your_gemini_api_key_here"]:
        return None
    try:
        return genai.Client(api_key=key.strip())
    except Exception:
        return None

def build_long_context_system_prompt() -> str:
    courses = load_courses()
    careers = load_careers()
    
    prompt = f"""You are EduPath AI Concierge, an expert academic and career advisor for engineering and technology students.
You have access to the complete database of university courses and career skill requirements.

=== FULL DATASET (LONG-CONTEXT INGESTION) ===

CAREERS DATABASE:
{json.dumps(careers, indent=2, ensure_ascii=False)}

COURSES DATABASE:
{json.dumps(courses, indent=2, ensure_ascii=False)}

=== INSTRUCTIONS & CONSTRAINTS ===
1. You MUST operate strictly on the full course & career dataset provided above. No external hallucinations.
2. Maintain prerequisite integrity: check if prerequisite courses are satisfied by user's current skills or core courses.
3. Your analysis must be quantitative, evidence-based, and highly actionable.
4. Output must strictly match the JSON Schema requested.
"""
    return prompt

def compare_universities(target_career: str, uni_a: str, uni_b: str, api_key: Optional[str] = None) -> UniversityComparisonResult:
    client = get_client(api_key)
    system_prompt = build_long_context_system_prompt()
    
    user_prompt = f"""Compare how '{uni_a}' and '{uni_b}' prepare a student for the target career: '{target_career}'.

Analyze:
1. Focus areas of both universities for this career path.
2. Unique electives from each university that directly benefit this target career.
3. Tech stack & tool differences taught in their respective curricula.
4. Curriculum scores out of 100 for each university covering:
   - theoretical_depth
   - industry_readiness
   - elective_flexibility
5. Provide a definitive, well-justified AI Concierge verdict recommending which university aligns best and why.
"""

    if client:
        try:
            models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[system_prompt, user_prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=UniversityComparisonResult,
                            temperature=0.2
                        )
                    )
                    if response and response.text:
                        data = json.loads(response.text)
                        return UniversityComparisonResult.model_validate(data)
                except Exception as e:
                    print(f"Model {model_name} error: {e}")
                    continue
        except Exception as e:
            print(f"Gemini API Call Exception: {e}")

    # Fallback response for offline / no-key mode
    return mock_compare_universities(target_career, uni_a, uni_b)

def analyze_career_gap_and_plan(
    university: str,
    target_career: str,
    current_skills: List[str],
    api_key: Optional[str] = None
) -> CareerPlanAnalysisResult:
    client = get_client(api_key)
    system_prompt = build_long_context_system_prompt()
    
    user_prompt = f"""Perform a comprehensive Skill-Gap Analysis and Course Planner for a student at '{university}' aiming for '{target_career}'.

Student Profile:
- University: {university}
- Target Role: {target_career}
- Current Skills: {json.dumps(current_skills)}

Instructions:
1. Identify missing core skills and missing advanced skills based on CAREERS DATABASE.
2. Calculate realistic career readiness percentage (0-100%), core readiness %, and advanced readiness %.
3. Recommend relevant elective and core courses from '{university}' in the COURSES DATABASE to bridge the missing skills.
4. Evaluate prerequisite status for each recommended course against current skills. (Prerequisite status MUST be 'Satisfied' or 'Missing: [Prereq Name]').
5. Create a 3-phase Study Roadmap (Phase 1, Phase 2, Phase 3) detailing target semester, courses included, and milestone goals.
6. Propose a high-impact portfolio capstone project that proves competency.
7. Provide inspiring and actionable AI Concierge advice.
"""

    if client:
        try:
            models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[system_prompt, user_prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=CareerPlanAnalysisResult,
                            temperature=0.2
                        )
                    )
                    if response and response.text:
                        data = json.loads(response.text)
                        return CareerPlanAnalysisResult.model_validate(data)
                except Exception as e:
                    print(f"Model {model_name} error: {e}")
                    continue
        except Exception as e:
            print(f"Gemini API Error: {e}")

    # Fallback mock generator
    return mock_analyze_career_gap(university, target_career, current_skills)


def mock_compare_universities(target_career: str, uni_a: str, uni_b: str) -> UniversityComparisonResult:
    courses = load_courses()
    careers = load_careers()
    
    courses_a = [c for c in courses if c.get("university") == uni_a]
    courses_b = [c for c in courses if c.get("university") == uni_b]
    
    electives_a = [c["course_name"] for c in courses_a if c.get("type") == "Elective"]
    electives_b = [c["course_name"] for c in courses_b if c.get("type") == "Elective"]
    
    return UniversityComparisonResult(
        target_career=target_career,
        focus_areas={
            uni_a: f"Heavy focus on core computer science foundations, algorithm efficiency, mathematical rigorousness, and distributed backend system design.",
            uni_b: f"Hands-on project-based learning focusing on modern cloud infrastructure, DevOps pipelines, containerized microservices, and industry tools."
        },
        unique_electives={
            uni_a: electives_a[:3] if electives_a else ["Advanced Distributed Systems", "High-Performance Backend Engineering"],
            uni_b: electives_b[:3] if electives_b else ["Cloud-Native & Microservice Development", "Scalable Backend & Distributed Databases"]
        },
        tech_stack_differences=[
            f"{uni_a} Curriculum teaches: Go, C++, PostgreSQL, Redis, Apache Airflow, PyTorch, and Deep Algorithms.",
            f"{uni_b} Curriculum teaches: Go, Node.js, AWS Cloud, Terraform, Docker/Kubernetes, MongoDB, and MLOps."
        ],
        curriculum_scores={
            uni_a: {
                "theoretical_depth": 94,
                "industry_readiness": 85,
                "elective_flexibility": 88
            },
            uni_b: {
                "theoretical_depth": 86,
                "industry_readiness": 95,
                "elective_flexibility": 90
            }
        },
        verdict=f"Both universities offer stellar engineering pathways for {target_career}. If your objective is high-scale algorithmic engineering, research, and deep distributed systems, {uni_a} provides stronger theoretical depth. If your goal is day-one cloud DevOps readiness, full-stack microservices, and fast enterprise onboarding, {uni_b} is tailored for immediate industry impact."
    )

def mock_analyze_career_gap(university: str, target_career: str, current_skills: List[str]) -> CareerPlanAnalysisResult:
    careers = load_careers()
    courses = load_courses()
    
    role_info = careers.get(target_career, careers.get(list(careers.keys())[0]))
    req_core = role_info.get("core_skills", [])
    req_adv = role_info.get("advanced_skills", [])
    
    current_set = set(current_skills)
    missing_core = [s for s in req_core if s not in current_set]
    missing_adv = [s for s in req_adv if s not in current_set]
    
    core_acquired = [s for s in req_core if s in current_set]
    adv_acquired = [s for s in req_adv if s in current_set]
    
    core_pct = round((len(core_acquired) / len(req_core) * 100), 1) if req_core else 100.0
    adv_pct = round((len(adv_acquired) / len(req_adv) * 100), 1) if req_adv else 100.0
    
    total_reqs = len(req_core) + len(req_adv)
    total_acquired = len(core_acquired) + len(adv_acquired)
    overall_readiness = round((total_acquired / total_reqs * 100), 1) if total_reqs > 0 else 50.0
    
    uni_courses = [c for c in courses if c.get("university") == university]
    
    recommended = []
    for c in uni_courses:
        c_skills = set(c.get("skills_covered", []))
        overlapping = c_skills.intersection(set(missing_core + missing_adv))
        if overlapping or c.get("type") == "Elective":
            prereqs = c.get("prerequisites", [])
            missing_p = [p for p in prereqs if not any(s.lower() in p.lower() for s in current_skills)]
            status = "Satisfied" if not missing_p else f"Missing: {', '.join(missing_p)}"
            
            recommended.append(RecommendedCourse(
                course_id=c["course_id"],
                course_name=c["course_name"],
                university=university,
                prerequisite_status=status,
                skills_gained=c.get("skills_covered", []),
                credits=c.get("credits", 3),
                ai_justification=f"Bridges critical gaps in {', '.join(overlapping if overlapping else c_skills)} required for {target_career}."
            ))
            
    recommended = recommended[:5]
    
    roadmap = [
        StudyPlanPhase(
            phase_name="Phase 1: Core Foundation & Prerequisites",
            target_semester="Year 3 Semester 1",
            course_ids=[r.course_id for r in recommended[:2]],
            courses_included=[r.course_name for r in recommended[:2]],
            milestone_goal=f"Master foundational competencies ({', '.join(missing_core[:2]) if missing_core else 'Core Concepts'}) and satisfy advanced prerequisites."
        ),
        StudyPlanPhase(
            phase_name="Phase 2: Advanced Elective Specialization",
            target_semester="Year 3 Semester 2",
            course_ids=[r.course_id for r in recommended[2:4]],
            courses_included=[r.course_name for r in recommended[2:4]],
            milestone_goal=f"Develop hands-on capabilities in {', '.join(missing_adv[:2]) if missing_adv else 'Specialized Topics'} with scalable architecture."
        ),
        StudyPlanPhase(
            phase_name="Phase 3: Senior Capstone & Industry Readiness",
            target_semester="Year 4 Semester 1",
            course_ids=[r.course_id for r in recommended[4:]] if len(recommended) > 4 else ["CAP401"],
            courses_included=[r.course_name for r in recommended[4:]] if len(recommended) > 4 else ["Senior Capstone Project"],
            milestone_goal="Ship end-to-end production-grade portfolio system with automated CI/CD and monitoring."
        )
    ]
    
    project_suggestions = {
        "Backend / Distributed Systems Engineer": "Distributed Event-Driven Key-Value Store with Raft consensus, Kafka streaming, and Redis caching.",
        "AI / Data Engineer": "Automated End-to-End MLOps Pipeline with Apache Airflow, PySpark data lake, and real-time LLM inference deployment.",
        "Full-Stack Web Architect": "Scalable Multi-Tenant SaaS Platform with Next.js 14, Go microservices, GraphQL federation, and Docker deployment.",
        "Cloud & Cybersecurity Engineer": "Zero-Trust Cloud Infrastructure on AWS with Terraform IaC, automated container vulnerability scanning, and OAuth2/OIDC gateway."
    }
    
    return CareerPlanAnalysisResult(
        target_career=target_career,
        acquired_skills=list(current_set),
        missing_core_skills=missing_core,
        missing_advanced_skills=missing_adv,
        readiness_percentage=overall_readiness,
        core_readiness=core_pct,
        advanced_readiness=adv_pct,
        recommended_courses=recommended,
        study_roadmap=roadmap,
        portfolio_project=project_suggestions.get(target_career, "Production-grade Capstone Project"),
        concierge_advice=f"To bridge into a competitive {target_career}, prioritize closing your missing core skills ({', '.join(missing_core[:2]) if missing_core else 'None'}) in Phase 1 before loading advanced electives. Combine your coursework with the recommended capstone project to stand out in technical interviews."
    )
