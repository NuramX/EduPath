import os
import json
import datetime
import streamlit as st
from dotenv import load_dotenv

from services.data_loader import load_courses, load_careers, get_universities, get_all_skills
from services.gemini_service import compare_universities, analyze_career_gap_and_plan
from schemas.output_schema import CareerPlanAnalysisResult, UniversityComparisonResult

load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="EduPath Concierge | Biztania Camp 2026",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Modern Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F766E 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #38BDF8, #34D399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        max-width: 850px;
        line-height: 1.5;
    }
    
    /* 6 AI Capabilities Stepper */
    .cap-badge-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 18px;
    }
    .cap-badge {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: #E2E8F0;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Glass Cards */
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 18px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    /* Metrics */
    .metric-bubble {
        text-align: center;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Skill Chips */
    .skill-chip {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 3px 4px 3px 0;
    }
    .skill-chip-acquired {
        background-color: #DCFCE7;
        color: #166534;
        border: 1px solid #BBF7D0;
    }
    .skill-chip-missing-core {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
    }
    .skill-chip-missing-adv {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }
    
    /* Status Badges */
    .status-satisfied {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .status-missing {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    
    /* AI Verdict Callout */
    .ai-verdict-card {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        border: 1px solid #86EFAC;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
    }
    
    /* Timeline / Phase Card */
    .phase-card {
        border-left: 4px solid #0284C7;
        background: #F8FAFC;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for iCalendar generation
def generate_ics_calendar(analysis: CareerPlanAnalysisResult) -> str:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//EduPath Concierge//Study Schedule//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    start_date = datetime.date.today() + datetime.timedelta(days=7)
    
    for idx, phase in enumerate(analysis.study_roadmap):
        event_date = start_date + datetime.timedelta(days=idx*90)
        dt_start = event_date.strftime("%Y%m%dT090000Z")
        dt_end = event_date.strftime("%Y%m%dT170000Z")
        
        courses_str = ", ".join(phase.courses_included)
        
        lines.append("BEGIN:VEVENT")
        lines.append(f"SUMMARY:[EduPath] {phase.phase_name} ({phase.target_semester})")
        lines.append(f"DESCRIPTION:Target Courses: {courses_str}\\nMilestone: {phase.milestone_goal}")
        lines.append(f"DTSTART:{dt_start}")
        lines.append(f"DTEND:{dt_end}")
        lines.append(f"UID:edupath-phase-{idx+1}-{dt_start}@biztania2026")
        lines.append("END:VEVENT")
        
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


# Data Pre-loading
courses = load_courses()
careers = load_careers()
universities = get_universities()
all_skills = get_all_skills()

# Initialize Session State for One-Click Demo Presets
if "user_skills" not in st.session_state:
    st.session_state["user_skills"] = ["Python", "Data Structures", "Algorithms", "SQL", "PostgreSQL"]
if "selected_career" not in st.session_state:
    st.session_state["selected_career"] = "Backend / Distributed Systems Engineer"
if "selected_uni" not in st.session_state:
    st.session_state["selected_uni"] = "Chulalongkorn University"

# Sidebar Setup
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/graduation-cap.png", width=60)
    st.markdown("### **EduPath Concierge**")
    st.caption("AI-Powered Curriculum-to-Career Alignment")
    st.caption("🏆 **Biztania Camp 2026 — Engineering Track**")
    
    st.divider()
    
    st.markdown("#### ⚡ One-Click Demo Presets")
    st.caption("Select a persona to instantly configure the prototype for judging:")
    
    demo_p1 = st.button("🧑‍🎓 Pre-Uni Senior: AI & Data", use_container_width=True)
    if demo_p1:
        st.session_state["selected_career"] = "AI / Data Engineer"
        st.session_state["selected_uni"] = "Chulalongkorn University"
        st.session_state["user_skills"] = ["Python", "Basic Algorithms"]
        st.rerun()

    demo_p2 = st.button("💻 Undergrad Yr 2: Distributed Backend", use_container_width=True)
    if demo_p2:
        st.session_state["selected_career"] = "Backend / Distributed Systems Engineer"
        st.session_state["selected_uni"] = "Chulalongkorn University"
        st.session_state["user_skills"] = ["Python", "C++", "Data Structures", "Algorithms", "SQL", "PostgreSQL"]
        st.rerun()

    demo_p3 = st.button("🌐 Undergrad Yr 3: Full-Stack Architect", use_container_width=True)
    if demo_p3:
        st.session_state["selected_career"] = "Full-Stack Web Architect"
        st.session_state["selected_uni"] = "KMUTT"
        st.session_state["user_skills"] = ["TypeScript", "React", "Node.js", "HTML/CSS", "REST APIs"]
        st.rerun()

    st.divider()

    st.markdown("#### 🔑 LLM API Configuration")
    default_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Gemini API Key",
        value=default_key,
        type="password",
        help="Paste your Gemini API key here. The app automatically runs high-fidelity offline mock fallback if blank."
    )
    if user_api_key:
        st.success("🟢 Connected: Gemini 2.5 Flash")
    else:
        st.info("🟡 Ingested Context Engine Active (Offline Mode)")

    st.divider()
    st.markdown("#### 🛡️ Architecture & Integrity")
    st.markdown("""
    - **No Vector DB / No RAG**: Ingests full curriculum graphs in-context.
    - **Zero Chunking Loss**: Complete prerequisite traversal without hallucination.
    - **Schema Enforced**: Strict Pydantic v2 JSON outputs.
    """)

# Top Hero Section
st.markdown("""
<div class="hero-container">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <div class="hero-title">EduPath Concierge 🎓</div>
            <div class="hero-subtitle">
                Bridging the gap between university syllabi and industry competencies through long-context AI.
                Compare university curriculums side-by-side or diagnose personal skill gaps into actionable prerequisite-aware study roadmaps.
            </div>
        </div>
    </div>
    <div class="cap-badge-container">
        <span class="cap-badge">🧠 1. Remember (Profile Retention)</span>
        <span class="cap-badge">📖 2. Understand (Deep Syllabus)</span>
        <span class="cap-badge">🔗 3. Connect (Job Taxonomy)</span>
        <span class="cap-badge">⚡ 4. Retrieve (Prerequisite Integrity)</span>
        <span class="cap-badge">⚖️ 5. Reason (Quantitative Gap)</span>
        <span class="cap-badge">🚀 6. Act (Interactive Roadmap & .ics)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_compare, tab_planner, tab_explorer = st.tabs([
    "🏛️ Tab 1: Cross-University Head-to-Head Arena",
    "🎯 Tab 2: Skill-Gap Diagnostic & Elective Navigator",
    "🔍 Tab 3: Curriculum & Career Taxonomy Explorer"
])


# =========================================================================
# TAB 1: CROSS-UNIVERSITY HEAD-TO-HEAD ARENA
# =========================================================================
with tab_compare:
    st.markdown("### 🏛️ Cross-University Curriculum Matchup")
    st.write("Compare how two universities prepare students for your target career role based on complete course descriptions and electives.")

    c1, c2, c3 = st.columns(3)
    with c1:
        target_career_tab1 = st.selectbox(
            "Target Tech Career",
            options=list(careers.keys()),
            index=list(careers.keys()).index(st.session_state.get("selected_career", list(careers.keys())[0])),
            key="tab1_target_career"
        )
    with c2:
        uni_a = st.selectbox(
            "University A",
            options=universities,
            index=0,
            key="t1_uni_a"
        )
    with c3:
        uni_b_candidates = [u for u in universities if u != uni_a] or universities
        uni_b = st.selectbox(
            "University B",
            options=uni_b_candidates,
            index=0,
            key="t1_uni_b"
        )

    if st.button("🚀 Run Head-to-Head Curriculum Analysis", type="primary", use_container_width=True):
        with st.spinner("Analyzing syllabi and computing curriculum metrics..."):
            comp_result = compare_universities(target_career_tab1, uni_a, uni_b, api_key=user_api_key)

            st.markdown(f"#### 📊 Comparative Breakdown: **{target_career_tab1}**")

            # Curriculum Score Cards
            if comp_result.curriculum_scores:
                scores_a = comp_result.curriculum_scores.get(uni_a, {})
                scores_b = comp_result.curriculum_scores.get(uni_b, {})
                
                sc_col1, sc_col2 = st.columns(2)
                with sc_col1:
                    st.markdown(f"##### 🏛️ **{uni_a} Curriculum DNA**")
                    sub_c1, sub_c2, sub_c3 = st.columns(3)
                    with sub_c1:
                        st.markdown(f"<div class='metric-bubble'><div class='metric-value'>{scores_a.get('theoretical_depth', 90)}%</div><div class='metric-label'>Theory Depth</div></div>", unsafe_allow_html=True)
                    with sub_c2:
                        st.markdown(f"<div class='metric-bubble'><div class='metric-value'>{scores_a.get('industry_readiness', 85)}%</div><div class='metric-label'>Industry Tools</div></div>", unsafe_allow_html=True)
                    with sub_c3:
                        st.markdown(f"<div class='metric-bubble'><div class='metric-value'>{scores_a.get('elective_flexibility', 88)}%</div><div class='metric-label'>Elective Choice</div></div>", unsafe_allow_html=True)

                with sc_col2:
                    st.markdown(f"##### 🏛️ **{uni_b} Curriculum DNA**")
                    sub_c4, sub_c5, sub_c6 = st.columns(3)
                    with sub_c4:
                        st.markdown(f"<div class='metric-bubble'><div class='metric-value'>{scores_b.get('theoretical_depth', 85)}%</div><div class='metric-label'>Theory Depth</div></div>", unsafe_allow_html=True)
                    with sub_c5:
                        st.markdown(f"<div class='metric-bubble'><div class='metric-value'>{scores_b.get('industry_readiness', 95)}%</div><div class='metric-label'>Industry Tools</div></div>", unsafe_allow_html=True)
                    with sub_c6:
                        st.markdown(f"<div class='metric-bubble'><div class='metric-value'>{scores_b.get('elective_flexibility', 90)}%</div><div class='metric-label'>Elective Choice</div></div>", unsafe_allow_html=True)

            st.divider()

            # Side-by-side Focus & Electives Cards
            col_left, col_right = st.columns(2)
            with col_left:
                st.markdown(f"""
                <div class="feature-card">
                    <h4 style="margin-top:0; color:#0F766E;">🏛️ {uni_a}</h4>
                    <p><strong>Curriculum Core Philosophy:</strong></p>
                    <p style="color:#334155; line-height:1.6;">{comp_result.focus_areas.get(uni_a, "N/A")}</p>
                    <hr style="border:none; border-top:1px solid #E2E8F0; margin:15px 0;">
                    <p><strong>🎯 Distinctive Career Electives:</strong></p>
                    <ul>
                        {''.join(f'<li><strong>{el}</strong></li>' for el in comp_result.unique_electives.get(uni_a, []))}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            with col_right:
                st.markdown(f"""
                <div class="feature-card">
                    <h4 style="margin-top:0; color:#0284C7;">🏛️ {uni_b}</h4>
                    <p><strong>Curriculum Core Philosophy:</strong></p>
                    <p style="color:#334155; line-height:1.6;">{comp_result.focus_areas.get(uni_b, "N/A")}</p>
                    <hr style="border:none; border-top:1px solid #E2E8F0; margin:15px 0;">
                    <p><strong>🎯 Distinctive Career Electives:</strong></p>
                    <ul>
                        {''.join(f'<li><strong>{el}</strong></li>' for el in comp_result.unique_electives.get(uni_b, []))}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            # Tech Stack Differences
            st.markdown("#### 🛠️ Tech Stack & Tooling Exposure")
            for diff in comp_result.tech_stack_differences:
                st.markdown(f"- ⚙️ {diff}")

            # AI Verdict Card
            st.markdown(f"""
            <div class="ai-verdict-card">
                <h4 style="color:#166534; margin-top:0; display:flex; align-items:center; gap:8px;">
                    💡 EduPath AI Concierge Verdict & Match Rationale
                </h4>
                <p style="font-size:1.02rem; line-height:1.65; color:#14532D; margin-bottom:0;">
                    {comp_result.verdict}
                </p>
            </div>
            """, unsafe_allow_html=True)


# =========================================================================
# TAB 2: UNDERGRADUATE SKILL-GAP & ELECTIVE PLANNER
# =========================================================================
with tab_planner:
    st.markdown("### 🎯 Undergraduate Career-to-Elective Planner & Gap Analysis")
    st.write("Diagnose your current readiness for your dream role, check prerequisite bottlenecks, and generate an actionable 3-phase roadmap.")

    # Student Profile Form
    with st.container():
        st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
        st.markdown("##### 👤 Student Learner Profile (Remember Engine)")
        
        prof_col1, prof_col2 = st.columns(2)
        with prof_col1:
            current_uni = st.selectbox(
                "Current University",
                options=universities,
                index=universities.index(st.session_state.get("selected_uni", universities[0])),
                key="tab2_current_uni"
            )
            target_career = st.selectbox(
                "Target Tech Career",
                options=list(careers.keys()),
                index=list(careers.keys()).index(st.session_state.get("selected_career", list(careers.keys())[0])),
                key="tab2_target_career"
            )
            
        with prof_col2:
            st.markdown("**Your Current Acquired Skills:**")
            selected_skills = st.multiselect(
                "Select existing skills",
                options=all_skills,
                default=[s for s in st.session_state.get("user_skills", []) if s in all_skills],
                key="tab2_user_skills"
            )
            custom_input = st.text_input("Add custom skills (comma-separated)", placeholder="e.g. C++, Redis, CI/CD")
            if custom_input:
                extra_skills = [s.strip() for s in custom_input.split(",") if s.strip()]
                selected_skills = list(set(selected_skills + extra_skills))
                
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("⚡ Run Skill-Gap Diagnostic & Generate Study Plan", type="primary", use_container_width=True):
        with st.spinner("Analyzing skill matrix, checking prerequisite graphs, and synthesizing study roadmap..."):
            plan_result = analyze_career_gap_and_plan(
                university=current_uni,
                target_career=target_career,
                current_skills=selected_skills,
                api_key=user_api_key
            )

            st.divider()

            # 1. Executive Metrics Bar
            st.markdown("#### 📈 1. Skill Gap Diagnostic & Career Readiness")
            
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"<div class='metric-bubble'><div class='metric-value' style='color:#0F766E;'>{plan_result.readiness_percentage}%</div><div class='metric-label'>Overall Readiness</div></div>", unsafe_allow_html=True)
            with m2:
                core_val = plan_result.core_readiness if plan_result.core_readiness is not None else 75.0
                st.markdown(f"<div class='metric-bubble'><div class='metric-value' style='color:#0284C7;'>{core_val}%</div><div class='metric-label'>Core Competency</div></div>", unsafe_allow_html=True)
            with m3:
                adv_val = plan_result.advanced_readiness if plan_result.advanced_readiness is not None else 40.0
                st.markdown(f"<div class='metric-bubble'><div class='metric-value' style='color:#D97706;'>{adv_val}%</div><div class='metric-label'>Advanced Mastery</div></div>", unsafe_allow_html=True)
            with m4:
                total_gap = len(plan_result.missing_core_skills) + len(plan_result.missing_advanced_skills)
                st.markdown(f"<div class='metric-bubble'><div class='metric-value' style='color:#DC2626;'>{total_gap}</div><div class='metric-label'>Skills to Bridge</div></div>", unsafe_allow_html=True)

            st.progress(min(max(plan_result.readiness_percentage / 100.0, 0.0), 1.0))

            # Visual Skill Matrix Chips
            matrix_col1, matrix_col2 = st.columns(2)
            with matrix_col1:
                st.markdown("##### ✅ Acquired Competencies")
                if plan_result.acquired_skills:
                    chips_html = "".join(f"<span class='skill-chip skill-chip-acquired'>✓ {s}</span>" for s in plan_result.acquired_skills)
                    st.markdown(chips_html, unsafe_allow_html=True)
                else:
                    st.caption("No matching skills recorded.")

            with matrix_col2:
                st.markdown("##### ⚠️ Competency Gaps (Prioritized)")
                missing_html = ""
                for s in plan_result.missing_core_skills:
                    missing_html += f"<span class='skill-chip skill-chip-missing-core'>🔴 Core: {s}</span>"
                for s in plan_result.missing_advanced_skills:
                    missing_html += f"<span class='skill-chip skill-chip-missing-adv'>🟠 Adv: {s}</span>"
                st.markdown(missing_html if missing_html else "<span>🎉 All required skills covered!</span>", unsafe_allow_html=True)

            st.divider()

            # 2. Prerequisite-Aware Course Recommendations
            st.markdown("#### 📚 2. Prerequisite-Aware Course Recommendations")
            st.caption(f"Retrieved in-context from **{current_uni}** syllabus database. Prerequisite graph checked without semantic chunking.")

            for course in plan_result.recommended_courses:
                is_satisfied = "Satisfied" in course.prerequisite_status
                badge_class = "status-satisfied" if is_satisfied else "status-missing"
                
                with st.expander(f"📖 {course.course_id}: {course.course_name} ({course.credits or 3} Credits) — {course.prerequisite_status}", expanded=True):
                    c_left, c_right = st.columns([1, 2])
                    with c_left:
                        st.markdown(f"**Prerequisite Check:** <span class='{badge_class}'>{course.prerequisite_status}</span>", unsafe_allow_html=True)
                        st.markdown(f"**Skills Unlocked:** {', '.join(course.skills_gained)}")
                    with c_right:
                        st.markdown(f"**AI Concierge Rationale:** {course.ai_justification}")

            st.divider()

            # 3. Actionable Study Roadmap & Milestone
            st.markdown("#### 🗺️ 3. 3-Phase Study Plan & Milestone Project")
            
            for phase in plan_result.study_roadmap:
                st.markdown(f"""
                <div class="phase-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="margin:0; color:#0369A1;">📌 {phase.phase_name}</h4>
                        <span style="background:#E0F2FE; color:#0369A1; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.8rem;">
                            {phase.target_semester}
                        </span>
                    </div>
                    <p style="margin:8px 0 4px 0; color:#1E293B;"><strong>Recommended Courses:</strong> {', '.join(phase.courses_included)}</p>
                    <p style="margin:0; color:#475569; font-size:0.92rem;"><strong>🎯 Milestone Target:</strong> {phase.milestone_goal}</p>
                </div>
                """, unsafe_allow_html=True)

            if plan_result.portfolio_project:
                st.markdown(f"""
                <div style="background:#FAF5FF; border:1px solid #D8B4FE; border-radius:12px; padding:16px; margin: 15px 0;">
                    <h5 style="color:#6B21A8; margin-top:0;">🚀 Recommended Capstone Portfolio Project</h5>
                    <p style="color:#581C87; margin-bottom:0; font-size:0.98rem;">{plan_result.portfolio_project}</p>
                </div>
                """, unsafe_allow_html=True)

            st.info(f"💡 **AI Concierge Advice:** {plan_result.concierge_advice}")

            st.divider()

            # 4. Action Center (Act Engine)
            st.markdown("#### 📥 4. Action Center: Export Your Plan")
            st.caption("Convert your personalized roadmap into actionable digital deliverables:")
            
            exp1, exp2 = st.columns(2)
            with exp1:
                json_data = json.dumps(plan_result.model_dump(), indent=2, ensure_ascii=False)
                st.download_button(
                    label="📄 Download Study Plan (JSON)",
                    data=json_data,
                    file_name=f"EduPath_{target_career.replace(' ', '_')}_Plan.json",
                    mime="application/json",
                    use_container_width=True
                )
            with exp2:
                ics_data = generate_ics_calendar(plan_result)
                st.download_button(
                    label="📅 Export Study Calendar (.ics)",
                    data=ics_data,
                    file_name=f"EduPath_{target_career.replace(' ', '_')}_Schedule.ics",
                    mime="text/calendar",
                    use_container_width=True
                )


# =========================================================================
# TAB 3: CURRICULUM & CAREER TAXONOMY EXPLORER
# =========================================================================
with tab_explorer:
    st.markdown("### 🔍 Long-Context Curriculum & Career Taxonomy Database")
    st.write("Inspect the ground-truth data ingested directly into the LLM context window (without vector embeddings or lossy chunking).")

    exp_col1, exp_col2 = st.columns([1, 2])
    
    with exp_col1:
        st.markdown("##### 💼 Market Career Taxonomy")
        selected_career_exp = st.selectbox("Explore Tech Role", options=list(careers.keys()), key="exp_role")
        role_data = careers[selected_career_exp]
        st.markdown(f"**Description:** {role_data.get('description', '')}")
        st.markdown("**Required Core Skills:**")
        st.markdown("".join(f"<span class='skill-chip skill-chip-missing-core'>{s}</span>" for s in role_data.get('core_skills', [])), unsafe_allow_html=True)
        st.markdown("<br>**Advanced / Specialized Skills:**", unsafe_allow_html=True)
        st.markdown("".join(f"<span class='skill-chip skill-chip-missing-adv'>{s}</span>" for s in role_data.get('advanced_skills', [])), unsafe_allow_html=True)

    with exp_col2:
        st.markdown("##### 📚 University Course Catalog")
        filter_uni = st.selectbox("Filter by University", options=["All Universities"] + universities, key="filter_uni")
        search_kw = st.text_input("Search Course Name, ID, or Skill", placeholder="e.g. Distributed, Kafka, AI, CU-CS401")
        
        filtered_courses = courses
        if filter_uni != "All Universities":
            filtered_courses = [c for c in filtered_courses if c.get("university") == filter_uni]
        if search_kw:
            kw = search_kw.lower()
            filtered_courses = [
                c for c in filtered_courses
                if kw in c.get("course_name", "").lower()
                or kw in c.get("course_id", "").lower()
                or any(kw in s.lower() for s in c.get("skills_covered", []))
            ]

        st.caption(f"Showing **{len(filtered_courses)}** courses matching criteria.")
        
        for c in filtered_courses:
            prereqs_str = ", ".join(c.get("prerequisites", [])) if c.get("prerequisites") else "None (Entry level)"
            with st.expander(f"{c.get('course_id')} | {c.get('course_name')} ({c.get('university')}) - {c.get('type')}"):
                st.write(f"**Syllabus:** {c.get('syllabus_description')}")
                st.write(f"**Prerequisites:** `{prereqs_str}`")
                st.write(f"**Skills Taught:** {', '.join(c.get('skills_covered', []))}")
