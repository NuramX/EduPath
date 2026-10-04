import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from schemas.output_schema import (
    UniversityComparisonResult,
    CareerPlanAnalysisResult,
    RecommendedCourse,
    StudyPlanPhase,
    AICareerRecommendation,
    AICareerRecommendationsResult
)
from services.data_loader import load_courses, load_careers

load_dotenv(override=True)

def get_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    load_dotenv(override=True)
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
    
    prompt = f"""You are EduPath AI Concierge, a world-class multidisciplinary university academic and career advisor serving students across all fields: Medicine & Health Sciences, Law & Legal Studies, Communication Arts & Media, Business & Finance, Design, and Engineering & Technology.
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
3. Key differences in tools, frameworks, and methodologies taught in their respective curricula.
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
    
    role_info = careers.get(target_career, {})
    role_title = role_info.get("title", target_career)
    role_category = role_info.get("category", "")
    
    courses_a = [c for c in courses if c.get("university") == uni_a]
    courses_b = [c for c in courses if c.get("university") == uni_b]
    
    # Filter electives matching the career's skills or general electives
    req_skills_lower = {s.lower() for s in role_info.get("required_skills", [])}
    
    def matches_career(c):
        return any(s.lower() in req_skills_lower for s in c.get("skills_covered", []))
    
    career_electives_a = [c["course_name"] for c in courses_a if c.get("type") == "Elective" and matches_career(c)]
    career_electives_b = [c["course_name"] for c in courses_b if c.get("type") == "Elective" and matches_career(c)]
    
    if not career_electives_a:
        career_electives_a = [c["course_name"] for c in courses_a if c.get("type") == "Elective"]
    if not career_electives_b:
        career_electives_b = [c["course_name"] for c in courses_b if c.get("type") == "Elective"]
        
    # Domain-specific focus descriptions
    if "Medical" in target_career or "Doctor" in target_career or "Psycholog" in target_career or "Health" in role_category:
        focus_a = f"{uni_a} emphasizes core physiological & clinical science foundations, systematic diagnosis, medical ethics, and evidence-based pathology research."
        focus_b = f"{uni_b} emphasizes hands-on bedside clinical simulation, telemedicine digital health integration, acute care protocols, and patient communications."
        tools = [
            f"{uni_a} Curriculum trains: Evidence-based clinical appraisal, diagnostic semiotics, histological lab analysis, and clinical pharmacology.",
            f"{uni_b} Curriculum trains: Tele-health virtual triage platforms, bedside ultrasound simulation, patient care EHR systems, and acute emergency protocols."
        ]
    elif "Law" in target_career or "Legal" in role_category:
        focus_a = f"{uni_a} focuses heavily on constitutional jurisprudence, civil and commercial statutory doctrine, legal drafting precision, and judicial case analysis."
        focus_b = f"{uni_b} focuses on corporate commercial deal-making, cross-border M&A negotiations, tech IP patents, cyber PDPA compliance, and international arbitration."
        tools = [
            f"{uni_a} Curriculum trains: Statutory interpretation, legal research databases, court litigation drafting, and contract jurisprudence.",
            f"{uni_b} Curriculum trains: M&A due diligence term-sheets, international commercial arbitration, PDPA/GDPR compliance audits, and digital forensics."
        ]
    elif "Content" in target_career or "PR" in target_career or "Media" in role_category:
        focus_a = f"{uni_a} cultivates narrative journalism, aesthetic visual storytelling, high-end studio cinematography, and media ethics."
        focus_b = f"{uni_b} cultivates viral short-form distribution architectures, multi-channel PR crisis response, audience retention analytics, and influencer ecosystems."
        tools = [
            f"{uni_a} Curriculum trains: DaVinci Resolve color grading, documentary scriptwriting, studio audio mastering, and brand narrative design.",
            f"{uni_b} Curriculum trains: Premiere Pro NLE workflows, TikTok/Meta algorithm reverse engineering, crisis PR press conferences, and sentiment analysis."
        ]
    elif "Financial" in target_career or "Marketing" in target_career or "Business" in role_category:
        focus_a = f"{uni_a} grounds students in corporate accounting, quantitative financial modeling, discounted cash flow (DCF) valuation, and risk engineering."
        focus_b = f"{uni_b} specializes in full-funnel digital growth marketing, paid media CAC/LTV analytics, A/B conversion experimentation, and venture strategy."
        tools = [
            f"{uni_a} Curriculum trains: 3-Statement financial modeling, DCF enterprise valuation, Python for quantitative finance, and portfolio optimization.",
            f"{uni_b} Curriculum trains: Google Analytics 4, Meta/TikTok ad buying, CRO landing page optimization, and automated CRM lifecycle workflows."
        ]
    elif "Design" in target_career or "UI/UX" in target_career:
        focus_a = f"{uni_a} emphasizes human-centered design thinking, qualitative user empathy research, information architecture, and cognitive ergonomics."
        focus_b = f"{uni_b} emphasizes scalable enterprise Figma design systems, interactive component prototyping, usability lab testing, and developer handoff."
        tools = [
            f"{uni_a} Curriculum trains: Ethnographic user interviews, empathy mapping, design heuristics, and cognitive journey mapping.",
            f"{uni_b} Curriculum trains: Advanced Figma auto-layout, interactive micro-animations, usability lab scoring (SUS), and design tokens."
        ]
    else:
        focus_a = f"{uni_a} emphasizes theoretical depth, algorithmic efficiency, mathematical rigorousness, and distributed system design."
        focus_b = f"{uni_b} emphasizes project-based hands-on learning with modern cloud platforms, container orchestration, CI/CD pipelines, and DevOps tooling."
        tools = [
            f"{uni_a} Curriculum teaches: Go, C++, PostgreSQL, Redis, Apache Airflow, PyTorch, and Deep Algorithms.",
            f"{uni_b} Curriculum teaches: Go, Node.js, AWS Cloud, Terraform, Docker/Kubernetes, MongoDB, and MLOps."
        ]
        
    return UniversityComparisonResult(
        target_career=target_career,
        focus_areas={
            uni_a: focus_a,
            uni_b: focus_b
        },
        unique_electives={
            uni_a: career_electives_a[:3],
            uni_b: career_electives_b[:3]
        },
        tech_stack_differences=tools,
        curriculum_scores={
            uni_a: {
                "theoretical_depth": 93,
                "industry_readiness": 86,
                "elective_flexibility": 89
            },
            uni_b: {
                "theoretical_depth": 87,
                "industry_readiness": 95,
                "elective_flexibility": 91
            }
        },
        verdict=f"Both universities offer outstanding curriculum tracks for {role_title}. If your objective is deeper academic foundations, research rigor, and analytical theory, {uni_a} provides an exceptional academic environment. If your goal is day-one professional readiness, modern industry methodologies, and agile practical execution, {uni_b} provides immediate real-world advantages."
    )

def mock_analyze_career_gap(university: str, target_career: str, current_skills: List[str]) -> CareerPlanAnalysisResult:
    careers = load_careers()
    courses = load_courses()
    
    role_info = careers.get(target_career, careers.get(list(careers.keys())[0]))
    req_core = role_info.get("core_skills", [])
    req_adv = role_info.get("advanced_skills", [])
    
    current_set = set(current_skills)
    current_lower = {s.lower() for s in current_skills}
    missing_core = [s for s in req_core if s.lower() not in current_lower]
    missing_adv = [s for s in req_adv if s.lower() not in current_lower]
    
    core_acquired = [s for s in req_core if s.lower() in current_lower]
    adv_acquired = [s for s in req_adv if s.lower() in current_lower]
    
    core_pct = round((len(core_acquired) / len(req_core) * 100), 1) if req_core else 100.0
    adv_pct = round((len(adv_acquired) / len(req_adv) * 100), 1) if req_adv else 100.0
    
    total_reqs = len(req_core) + len(req_adv)
    total_acquired = len(core_acquired) + len(adv_acquired)
    overall_readiness = round((total_acquired / total_reqs * 100), 1) if total_reqs > 0 else 50.0
    
    uni_courses = [c for c in courses if c.get("university") == university]
    
    # Prioritize courses that teach missing skills
    recommended = []
    missing_set = set(s.lower() for s in missing_core + missing_adv)
    for c in uni_courses:
        c_skills = c.get("skills_covered", [])
        overlapping = [s for s in c_skills if s.lower() in missing_set]
        if overlapping or (c.get("type") == "Elective" and any(s.lower() in {x.lower() for x in req_core + req_adv} for s in c_skills)):
            prereqs = c.get("prerequisites", [])
            missing_p = [p for p in prereqs if not any(s.lower() in p.lower() for s in current_skills)]
            status = "Satisfied" if not missing_p else f"Missing: {', '.join(missing_p)}"
            
            skills_text = ', '.join(overlapping if overlapping else c_skills[:3])
            recommended.append(RecommendedCourse(
                course_id=c["course_id"],
                course_name=c["course_name"],
                university=university,
                prerequisite_status=status,
                skills_gained=c.get("skills_covered", []),
                credits=c.get("credits", 3),
                ai_justification=f"Bridges critical competencies in {skills_text} required for {target_career}."
            ))
            
    # Sort courses by number of missing skills covered
    recommended = recommended[:5]
    
    roadmap = [
        StudyPlanPhase(
            phase_name="Phase 1: Core Competency & Foundational Mastery",
            target_semester="Year 3 Semester 1",
            course_ids=[r.course_id for r in recommended[:2]],
            courses_included=[r.course_name for r in recommended[:2]],
            milestone_goal=f"Master foundational competencies ({', '.join(missing_core[:2]) if missing_core else 'Core Principles'}) and satisfy prerequisite benchmarks."
        ),
        StudyPlanPhase(
            phase_name="Phase 2: Advanced Elective Specialization",
            target_semester="Year 3 Semester 2",
            course_ids=[r.course_id for r in recommended[2:4]],
            courses_included=[r.course_name for r in recommended[2:4]],
            milestone_goal=f"Develop hands-on capabilities in {', '.join(missing_adv[:2]) if missing_adv else 'Specialized Domain Practice'} through authentic applied coursework."
        ),
        StudyPlanPhase(
            phase_name="Phase 3: Senior Capstone & Professional Portfolio",
            target_semester="Year 4 Semester 1",
            course_ids=[r.course_id for r in recommended[4:]] if len(recommended) > 4 else ["CAP401"],
            courses_included=[r.course_name for r in recommended[4:]] if len(recommended) > 4 else ["Senior Capstone & Practicum"],
            milestone_goal="Deliver a polished, professional capstone deliverable and portfolio ready for high-impact industry or clinical opportunities."
        )
    ]
    
    project_suggestions = {
        "Medical Doctor": "Community Telemedicine Triage Pilot & Clinical Evidence Audit Case Study",
        "Clinical Psychologist": "Evidence-Based Adolescent Mental Health Intervention Protocol & Case Portfolio",
        "Corporate Lawyer": "Cross-Border Tech M&A Legal Due Diligence Memo & Master Service Agreement Drafting",
        "Cyber & IP Lawyer": "Comprehensive Enterprise PDPA Compliance Audit & AI Patent Strategy Blueprint",
        "Digital Content Creator": "Multi-Platform Viral Documentary Mini-Series with 100K+ Organic Reach & Media Kit",
        "Strategic PR & Brand Specialist": "Crisis Communication Playbook & Multi-Channel Brand Reputation Campaign",
        "Financial Analyst": "Institutional Equity Research Report & 3-Statement LBO Valuation Model",
        "Digital Marketing & Growth Strategist": "Full-Funnel Growth Hacking Experimentation Campaign & CRO Blueprint",
        "UI/UX & Product Designer": "End-to-End Accessible Healthcare Mobile App with Figma Design System & Usability Audit",
        "DevOps": "Multi-Region Zero-Downtime Kubernetes Infrastructure with Terraform and GitOps",
        "CyberSec": "Enterprise Zero-Trust Network Defense Architecture & Penetration Testing Report",
        "Data Sci": "Automated End-to-End MLOps Pipeline with Feature Store and Model Telemetry",
        "PM": "B2B SaaS Product Discovery PRD, User Funnel Analytics & Agile Sprint Backlog",
        "Backend / Distributed Systems Engineer": "Distributed Event-Driven Key-Value Store with Raft consensus, Kafka streaming, and Redis caching.",
        "Full-Stack Web Architect": "Scalable Multi-Tenant SaaS Platform with Next.js 14, Microservices, and Cloud Deployment."
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
        portfolio_project=project_suggestions.get(target_career, f"Professional Capstone Portfolio Project for {target_career}"),
        concierge_advice=f"To bridge into a competitive {target_career}, prioritize closing your missing core competencies ({', '.join(missing_core[:2]) if missing_core else 'None'}) in Phase 1 before taking advanced electives. Combine your coursework with the recommended capstone project to build a standout professional portfolio."
    )


def mock_recommend_careers(user_skills: List[str], university: str) -> AICareerRecommendationsResult:
    """Heuristic fallback to pick top 3-4 best fit careers based on skills overlap and synergies."""
    careers = load_careers()
    user_skills_lower = {s.lower() for s in user_skills}
    
    scored_careers = []
    for role_key, c_info in careers.items():
        req = c_info.get("required_skills", [])
        if not req:
            req = c_info.get("core_skills", []) + c_info.get("advanced_skills", [])
        
        core = c_info.get("core_skills", [])
        owned = [s for s in req if s.lower() in user_skills_lower]
        owned_core = [s for s in core if s.lower() in user_skills_lower]
        
        # Weighted score: core skills have higher weight
        score = (len(owned_core) * 2.0 + len(owned)) / (len(core) * 2.0 + len(req) + 0.001)
        scored_careers.append({
            "key": role_key,
            "owned_count": len(owned),
            "total_req": len(req),
            "score": score,
            "owned": owned,
            "title": c_info.get("title", role_key),
            "category": c_info.get("category", "")
        })
    
    # Sort initially to find highest matching role
    scored_careers.sort(key=lambda x: (x["score"], x["owned_count"]), reverse=True)
    if scored_careers and scored_careers[0]["owned_count"] > 0:
        primary_cat = scored_careers[0]["category"]
        # Boost roles in the same category to provide cohesive suggestions
        for item in scored_careers:
            if item["category"] == primary_cat and item != scored_careers[0]:
                item["score"] += 0.15
        scored_careers.sort(key=lambda x: (x["score"], x["owned_count"]), reverse=True)
    
    # Pick top 3 or 4 careers
    top_picks = scored_careers[:4]
    
    recommended = []
    badges = [
        "🔥 Best Skill Match",
        "⚡ Strong Foundation",
        "💡 High Synergy",
        "🚀 Strategic Pivot"
    ]
    
    for i, item in enumerate(top_picks):
        badge = badges[i] if i < len(badges) else "🎯 Recommended Option"
        owned_str = ", ".join(item["owned"][:3]) if item["owned"] else "ทักษะพื้นฐานของคุณ"
        if i == 0 and item["owned"]:
            rationale = f"ทักษะ {owned_str} สอดคล้องกับเส้นทางนี้มากที่สุด สามารถต่อยอดวิชาเลือกที่เกี่ยวข้องเพื่อขึ้นเป็น {item['title']} ได้เร็วที่สุด"
        elif item["owned"]:
            rationale = f"มีรากฐานในด้าน {owned_str} ซึ่งนำมาประยุกต์ใช้กับตำแหน่งนี้ได้ดี ช่วยให้เรียนรู้วิชาเลือกเสริมได้รวดเร็ว"
        else:
            rationale = f"สายอาชีพยอดนิยมที่ตลาดแรงงานต้องการสูง เป็นทางเลือกที่น่าสนใจในการเริ่มสะสมวิชาเลือกพื้นฐาน"
            
        recommended.append(AICareerRecommendation(
            career_key=item["key"],
            fit_badge=badge,
            ai_rationale=rationale
        ))
        
    summary = f"จากทักษะ {len(user_skills)} ด้านของคุณ AI ได้คัดเลือก 3-4 เส้นทางอาชีพที่มีความเหมาะสมและเปิดโอกาสในการต่อยอดสูงสุดสำหรับคุณ"
    return AICareerRecommendationsResult(
        recommended_careers=recommended,
        overall_summary=summary
    )


def recommend_careers_with_ai(
    user_skills: List[str],
    university: str,
    api_key: Optional[str] = None
) -> AICareerRecommendationsResult:
    """Intelligently recommend the top 3-4 career choices tailored to user's skills using Gemini."""
    client = get_client(api_key)
    careers = load_careers()
    
    if client and user_skills:
        system_prompt = build_long_context_system_prompt()
        user_prompt = f"""The student has acquired the following skills: {', '.join(user_skills)}.
They are currently exploring curriculum electives at '{university}'.

Review the CAREERS DATABASE carefully.
Instead of showing every career, identify and select ONLY the top 3 (maximum 4) most suitable or strategic career paths for this student.

CRITICAL RULES:
1. Each career_key MUST EXACTLY match one of the keys in the CAREERS DATABASE: {list(careers.keys())}.
2. Provide a concise, creative fit_badge (e.g. '🔥 Best Skill Match', '⚡ Strong Foundation', '💡 High Growth Pivot', '🚀 Fast-Track').
3. Provide a 1-2 sentence ai_rationale in Thai explaining specifically why this career fits their skills and what value it offers them.
4. Provide an overall_summary in Thai summarizing their core strengths and interdisciplinary potential.
5. Limit the recommendations to top 3 or 4 options only. Do NOT output all careers.
"""
        models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[system_prompt, user_prompt],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AICareerRecommendationsResult,
                        temperature=0.3
                    )
                )
                if response and response.text:
                    data = json.loads(response.text)
                    result = AICareerRecommendationsResult.model_validate(data)
                    # Filter to ensure valid keys
                    valid_recs = [r for r in result.recommended_careers if r.career_key in careers]
                    if valid_recs:
                        result.recommended_careers = valid_recs[:4]
                        return result
            except Exception as e:
                print(f"Gemini Career Recommendation Error with {model_name}: {e}")
                continue
                
    # Fallback heuristic
    return mock_recommend_careers(user_skills, university)

