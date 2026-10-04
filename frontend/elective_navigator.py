import os
import streamlit as st
from typing import List, Dict, Any, Set
from services.data_loader import load_courses, load_careers, get_universities, get_all_skills
from services.gemini_service import recommend_careers_with_ai

def render_html(html_str: str):
    """Safely render HTML in Streamlit without triggering Markdown indented code block formatting."""
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

def inject_navigator_css():
    """Inject polished UI styles for the Elective Navigator page."""
    st.markdown("""
    <style>
    /* Elective Navigator Container Styling */
    .navigator-header-box {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px 28px;
        border-radius: 14px;
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .navigator-title {
        font-size: 2.1rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
        background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #34D399 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .navigator-subtitle {
        color: #94A3B8;
        font-size: 0.98rem;
        line-height: 1.5;
        margin: 0;
    }

    /* Top Filter Container */
    .filter-wrapper {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 22px 24px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    /* AI Recommendation Badges & Cards */
    .ai-advisor-banner {
        background: linear-gradient(135deg, #F0FDF4 0%, #EFF6FF 100%);
        border: 1.5px solid #BFDBFE;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.06);
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .ai-advisor-icon {
        font-size: 1.8rem;
        flex-shrink: 0;
    }
    .ai-advisor-text {
        font-size: 0.92rem;
        color: #1E293B;
        line-height: 1.55;
    }
    .ai-fit-badge {
        background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);
        color: #FFFFFF;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 20px;
        letter-spacing: 0.3px;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.25);
        white-space: nowrap;
    }
    .ai-rationale-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-left: 3.5px solid #2563EB;
        border-radius: 6px;
        padding: 8px 10px;
        font-size: 0.8rem;
        color: #334155;
        line-height: 1.45;
        margin-bottom: 12px;
    }

    /* Career Card Styles */
    .career-grid-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 3px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.25s ease-in-out;
        min-height: 430px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 14px;
    }
    .career-grid-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 18px -3px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    .career-grid-card.active-selected {
        border: 2.5px solid #2563EB !important;
        background: #F8FAFC !important;
        box-shadow: 0 8px 20px -2px rgba(37, 99, 235, 0.18) !important;
    }

    /* Career Card Components */
    .card-header-row {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 10px;
    }
    .role-badge-icon {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #EFF6FF;
        border: 1.5px solid #DBEAFE;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    .role-title-text {
        font-size: 1.12rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
        line-height: 1.25;
    }
    .role-desc-text {
        color: #475569;
        font-size: 0.86rem;
        line-height: 1.45;
        margin-bottom: 12px;
        min-height: 52px;
    }

    /* Skill Badges */
    .skills-section-label {
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .badge-chip-container {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-bottom: 12px;
    }
    .badge-owned {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }
    .badge-unowned {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FECACA;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
        gap: 3px;
    }
    .badge-target-skill {
        background-color: #E0E7FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-flex;
        align-items: center;
    }

    /* Recommended Courses Preview in Card */
    .preview-courses-box {
        background: #F8FAFC;
        border: 1px dashed #CBD5E1;
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: auto;
        margin-bottom: 12px;
    }
    .preview-courses-title {
        font-size: 0.76rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .preview-course-item {
        font-size: 0.77rem;
        color: #1E293B;
        margin-bottom: 4px;
        line-height: 1.35;
    }
    .preview-course-item b {
        color: #0284C7;
    }
    .preview-course-item .trains-tag {
        color: #059669;
        font-weight: 600;
    }

    /* Drill-down Detail Panel Container */
    .detail-panel-box {
        background: #FFFFFF;
        border: 2px solid #E2E8F0;
        border-radius: 16px;
        padding: 28px;
        margin-top: 14px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.07);
        position: relative;
    }
    .detail-panel-badge {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #BFDBFE;
    }
    .detail-career-title {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .detail-job-desc {
        color: #334155;
        font-size: 0.96rem;
        line-height: 1.65;
        background: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    }

    /* Course Card inside Detail Panel */
    .detail-course-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .detail-course-card:hover {
        border-color: #38BDF8;
        background: #FFFFFF;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .detail-course-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
    }
    .detail-course-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }
    .detail-course-id-badge {
        background: #E0F2FE;
        color: #0369A1;
        font-size: 0.76rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        white-space: nowrap;
    }
    .detail-course-desc {
        color: #475569;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


def parse_skills_from_text(text: str, all_skills: List[str]) -> List[str]:
    """Parse comma-separated skill string with case-insensitive canonical matching."""
    if not text or not text.strip():
        return []
    raw_tokens = [tok.strip() for tok in text.split(",") if tok.strip()]
    canonical_map = {s.lower(): s for s in all_skills}
    result = []
    for tok in raw_tokens:
        tok_low = tok.lower()
        if tok_low in canonical_map:
            result.append(canonical_map[tok_low])
        else:
            # Preserve user token (title-case if purely lowercase)
            result.append(tok.title() if tok.islower() else tok)
    # Deduplicate preserving order
    return list(dict.fromkeys(result))


def calculate_career_skills(career_data: Dict[str, Any], user_skills: List[str]):
    """Calculate owned and unowned skills for a career using case-insensitive check."""
    required = career_data.get("required_skills", [])
    if not required:
        required = career_data.get("core_skills", []) + career_data.get("advanced_skills", [])
    
    user_skills_lower = {s.lower(): s for s in user_skills}
    owned_skills = []
    unowned_skills = []
    for req in required:
        if req.lower() in user_skills_lower:
            owned_skills.append(req)
        else:
            unowned_skills.append(req)
    return owned_skills, unowned_skills, required


def get_recommended_electives_for_career(
    courses: List[Dict[str, Any]],
    university: str,
    unowned_skills: List[str]
) -> List[Dict[str, Any]]:
    """Filter elective courses at selected_university that teach unowned_skills."""
    unowned_set = set(s.lower() for s in unowned_skills)
    uni_courses = [c for c in courses if c.get("university") == university]
    
    electives = [c for c in uni_courses if c.get("type") == "Elective"]
    if not electives:
        electives = uni_courses

    recommended = []
    for c in electives:
        covered = c.get("skills_covered", [])
        skills_to_get = [s for s in covered if s.lower() in unowned_set]
        if skills_to_get:
            c_copy = dict(c)
            c_copy["skills_to_get"] = skills_to_get
            recommended.append(c_copy)
    
    # Sort descending by count of unowned skills trained
    recommended.sort(key=lambda x: len(x["skills_to_get"]), reverse=True)
    return recommended


def on_select_career_card(role_key: str, target_tab: str):
    st.session_state["selected_career"] = role_key
    st.session_state["navigator_active_tab"] = target_tab

def on_switch_tab(target_tab: str):
    st.session_state["navigator_active_tab"] = target_tab

def render_elective_navigator():
    """Main render function for the Elective Navigator page."""
    inject_navigator_css()

    # Load ground truth data
    courses = load_courses()
    careers = load_careers()
    universities = get_universities()
    all_skills = get_all_skills()

    # 1. State Management Initialization
    if "selected_university" not in st.session_state:
        st.session_state["selected_university"] = universities[0] if universities else "University A"

    if "navigator_skill_pills" not in st.session_state:
        st.session_state["navigator_skill_pills"] = ["Clinical Diagnostics", "Anatomy & Physiology"]

    if "skills_extra_input" not in st.session_state:
        st.session_state["skills_extra_input"] = "Patient Care"

    if "user_skills" not in st.session_state or not st.session_state["user_skills"]:
        init_tokens = list(st.session_state["navigator_skill_pills"]) + [tok.strip() for tok in st.session_state["skills_extra_input"].split(",") if tok.strip()]
        st.session_state["user_skills"] = parse_skills_from_text(", ".join(init_tokens), all_skills)

    if "selected_career" not in st.session_state or not st.session_state["selected_career"]:
        default_role = "Medical Doctor" if "Medical Doctor" in careers else list(careers.keys())[0]
        st.session_state["selected_career"] = default_role

    if "has_generated_careers" not in st.session_state:
        st.session_state["has_generated_careers"] = False

    if "ai_career_recommendations" not in st.session_state:
        st.session_state["ai_career_recommendations"] = None

    # Tabs configuration
    tab_labels = ["💼 1. Career Paths", "📋 2. Career Details & Electives"]
    if "navigator_active_tab" not in st.session_state or st.session_state["navigator_active_tab"] not in tab_labels:
        st.session_state["navigator_active_tab"] = tab_labels[0]

    # =========================================================================
    # Header Section
    # =========================================================================
    render_html("""
    <div class="navigator-header-box">
        <div class="navigator-title">🧭 Elective Navigator (ระบบวิเคราะห์วิชาเลือกและเส้นทางอาชีพ)</div>
        <p class="navigator-subtitle">
            ค้นหาและสำรวจเส้นทางอาชีพหลากหลายวงการ (ทั้งสายแพทย์ & สุขภาพ, กฎหมาย & นิติศาสตร์, นิเทศ & สื่อดิจิทัล, บริหาร & การเงิน, ดีไซน์, และวิศวะ & เทคโนโลยี) พร้อมประเมินทักษะที่มีและคัดสรรวิชาเลือกที่เปิดสอนจริงในมหาวิทยาลัยเพื่อพิชิตเป้าหมาย
        </p>
    </div>
    """)

    # Dynamic Tab Control via Streamlit 1.64.0
    tab_cards, tab_detail = st.tabs(
        tab_labels,
        key="navigator_active_tab",
        on_change="rerun"
    )

    # =========================================================================
    # TAB 1: CAREER PATHS & GENERATOR
    # =========================================================================
    with tab_cards:
        # Top Input Bar (Filters & User Context)
        with st.container(border=True):
            f_col1, f_col2 = st.columns([1, 2.5])

            with f_col1:
                st.markdown("##### 🏛️ University (สถาบันการศึกษา)")
                current_uni_idx = (
                    universities.index(st.session_state["selected_university"])
                    if st.session_state["selected_university"] in universities
                    else 0
                )
                selected_uni = st.selectbox(
                    "Select University",
                    options=universities,
                    index=current_uni_idx,
                    label_visibility="collapsed",
                    key="navigator_uni_select"
                )
                st.session_state["selected_university"] = selected_uni
                st.caption("🏫 เลือกสถาบันเพื่อกรองรายวิชาเลือกที่เปิดสอนจริง")

            with f_col2:
                popular_skills = [
                    "Clinical Diagnostics", "Anatomy & Physiology", "Patient Care", "Medical Ethics",
                    "Contract Law", "Legal Research", "Corporate Governance", "Legal Drafting",
                    "Visual Storytelling", "Video Production", "Scriptwriting", "Social Media Strategy", "Public Relations",
                    "Financial Modeling", "Valuation", "Accounting", "Corporate Finance", "Digital Marketing",
                    "Figma", "User Research", "Wireframing & Prototyping", "Design Systems",
                    "Python", "SQL", "Docker", "Git", "Linux", "C++", "Machine Learning"
                ]

                st.markdown("##### 🎭 Student Persona Presets (เลือกโปรไฟล์ตัวอย่างตามสายการเรียน)")
                preset_cols = st.columns(6)

                def on_click_preset(p_pills: List[str], p_extra: str):
                    valid_pills = [s for s in p_pills if s in popular_skills]
                    spillover = [s for s in p_pills if s not in popular_skills]
                    extra_tokens = [tok.strip() for tok in (p_extra or "").split(",") if tok.strip()] + spillover
                    st.session_state["navigator_skill_pills"] = valid_pills
                    st.session_state["skills_extra_input"] = ", ".join(dict.fromkeys(extra_tokens))
                    st.session_state["has_generated_careers"] = True
                    st.session_state["ai_career_recommendations"] = None

                with preset_cols[0]:
                    st.button(
                        "🩺 แพทย์/สุขภาพ",
                        key="btn_persona_med",
                        use_container_width=True,
                        on_click=on_click_preset,
                        args=(["Anatomy & Physiology", "Clinical Diagnostics", "Patient Care", "Medical Ethics"], "Pharmacology, Telemedicine")
                    )
                with preset_cols[1]:
                    st.button(
                        "⚖️ นิติศาสตร์",
                        key="btn_persona_law",
                        use_container_width=True,
                        on_click=on_click_preset,
                        args=(["Contract Law", "Legal Research", "Corporate Governance", "Legal Drafting"], "PDPA & Data Privacy, Cyber Law")
                    )
                with preset_cols[2]:
                    st.button(
                        "🎬 นิเทศ/สื่อ",
                        key="btn_persona_comm",
                        use_container_width=True,
                        on_click=on_click_preset,
                        args=(["Visual Storytelling", "Video Production", "Scriptwriting", "Social Media Strategy"], "Public Relations, Premiere Pro")
                    )
                with preset_cols[3]:
                    st.button(
                        "💼 บริหาร/ธุรกิจ",
                        key="btn_persona_bus",
                        use_container_width=True,
                        on_click=on_click_preset,
                        args=(["Financial Modeling", "Valuation", "Accounting", "Corporate Finance"], "Digital Marketing, SEO/SEM")
                    )
                with preset_cols[4]:
                    st.button(
                        "🎨 UI/UX ดีไซน์",
                        key="btn_persona_des",
                        use_container_width=True,
                        on_click=on_click_preset,
                        args=(["Figma", "User Research", "Wireframing & Prototyping", "Design Systems"], "Usability Testing, Interaction Design")
                    )
                with preset_cols[5]:
                    st.button(
                        "💻 วิศวะ/เทค",
                        key="btn_persona_tech",
                        use_container_width=True,
                        on_click=on_click_preset,
                        args=(["Python", "Git", "Linux", "Docker"], "CI/CD, AWS, Kubernetes")
                    )

            st.markdown("---")

            # Quick Skills Tag Selector
            st.markdown("##### ⚡ Quick Skill Tags (คลิกเพื่อเลือก/ยกเลิกทักษะที่คุณมีจากทุกหมวด):")

            # Strictly sanitize session state pills to guarantee no StreamlitDefaultNotInOptionsError
            curr_pills = st.session_state.get("navigator_skill_pills", [])
            valid_pills = [s for s in curr_pills if s in popular_skills]
            if len(valid_pills) != len(curr_pills) or not valid_pills:
                valid_pills = valid_pills if valid_pills else ["Clinical Diagnostics", "Anatomy & Physiology"]
            st.session_state["navigator_skill_pills"] = valid_pills

            chosen_pills = st.pills(
                "Popular Skills",
                options=popular_skills,
                selection_mode="multi",
                label_visibility="collapsed",
                key="navigator_skill_pills"
            )

            # Additional Custom Skills Input
            st.markdown("##### ✍️ Additional Skills (พิมพ์ทักษะเพิ่มเติม คั่นด้วย comma):")
            extra_txt = st.text_input(
                "Enter additional skills",
                value=st.session_state.get("skills_extra_input", "Medical Ethics"),
                placeholder="เช่น Telemedicine, PDPA, Premiere Pro, DCF Analysis, Mergers & Acquisitions, Kubernetes, Crisis Communication",
                label_visibility="collapsed",
                key="skills_extra_input",
                help="พิมพ์ทักษะเพิ่มเติมที่ไม่อยู่ใน tag ด้านบน คั่นด้วย comma"
            )

            # Recompute combined user skills
            raw_tokens = list(chosen_pills or []) + [tok.strip() for tok in (extra_txt or "").split(",") if tok.strip()]
            st.session_state["user_skills"] = parse_skills_from_text(", ".join(raw_tokens), all_skills)

            def on_trigger_ai_generate():
                st.session_state["has_generated_careers"] = True
                st.session_state["ai_career_recommendations"] = None

            st.button(
                "🚀 ให้ AI วิเคราะห์และเลือกเส้นทางอาชีพที่เหมาะสม (Generate AI Career Paths)",
                type="primary",
                use_container_width=True,
                on_click=on_trigger_ai_generate
            )

        # Career Path Cards Section (Only shown after Generate is clicked)
        if st.session_state.get("has_generated_careers", False):
            # Compute AI career recommendation if not present in session
            if not st.session_state.get("ai_career_recommendations"):
                with st.spinner("🤖 EduPath AI กำลังประเมินทักษะ ค้นหาจุดแข็ง และคัดเลือกเส้นทางอาชีพที่ดีที่สุดสำหรับคุณ..."):
                    api_key = os.getenv("GEMINI_API_KEY", "").strip() or None
                    st.session_state["ai_career_recommendations"] = recommend_careers_with_ai(
                        st.session_state["user_skills"],
                        st.session_state["selected_university"],
                        api_key=api_key
                    )

            ai_recs = st.session_state.get("ai_career_recommendations")
            recs_list = [r for r in ai_recs.recommended_careers if r.career_key in careers] if (ai_recs and ai_recs.recommended_careers) else []

            # Fallback if empty
            if not recs_list:
                for k in list(careers.keys())[:3]:
                    recs_list.append(type("AICareerRecMock", (), {
                        "career_key": k,
                        "fit_badge": "🎯 Recommended Option",
                        "ai_rationale": "สายอาชีพยอดนิยมที่ตลาดแรงงานต้องการสูง"
                    }))

            # AI Advisor Summary Banner
            if ai_recs and ai_recs.overall_summary:
                render_html(f"""
                <div class="ai-advisor-banner">
                    <div class="ai-advisor-icon">💡</div>
                    <div class="ai-advisor-text">
                        <strong>EduPath AI Advisor:</strong> {ai_recs.overall_summary}
                    </div>
                </div>
                """)

            st.markdown("### 💼 AI-Recommended Career Alternatives (ทางเลือกอาชีพที่ AI วิเคราะห์และคัดสรรให้คุณ)")
            st.caption("AI คัดเลือกเฉพาะ **3-4 สายอาชีพที่มีความเหมาะสมหรือต่อยอดได้สูงสุด** จากทักษะปัจจุบันของคุณ (ไม่มีการใส่ progress bar รกสายตา) — คลิก **'View Details'** เพื่อดูวิชาเลือก")

            cols = st.columns(len(recs_list))

            for idx, rec in enumerate(recs_list):
                role_key = rec.career_key
                career_info = careers[role_key]
                role_title = career_info.get("title", role_key)
                badge_name = career_info.get("badge", role_key)
                icon = career_info.get("icon", "🎯")
                short_desc = career_info.get("short_desc", career_info.get("description", "")[:90] + "...")

                owned, unowned, req_all = calculate_career_skills(career_info, st.session_state["user_skills"])
                recommended_courses = get_recommended_electives_for_career(
                    courses, st.session_state["selected_university"], unowned
                )

                is_selected = (st.session_state.get("selected_career") == role_key)
                card_class = "career-grid-card active-selected" if is_selected else "career-grid-card"

                with cols[idx]:
                    owned_chips = "".join([f"<span class='badge-owned'>✓ {s}</span>" for s in owned[:4]])
                    if len(owned) > 4:
                        owned_chips += f"<span class='badge-owned'>+{len(owned)-4}</span>"
                    if not owned:
                        owned_chips = "<span style='font-size:0.75rem; color:#94A3B8;'>None acquired yet</span>"

                    unowned_chips = "".join([f"<span class='badge-unowned'>✗ {s}</span>" for s in unowned[:4]])
                    if len(unowned) > 4:
                        unowned_chips += f"<span class='badge-unowned'>+{len(unowned)-4}</span>"
                    if not unowned:
                        unowned_chips = "<span class='badge-owned'>🎉 All acquired!</span>"

                    # Recommended courses mini-preview: flat single-line items
                    if recommended_courses:
                        preview_items = []
                        for c in recommended_courses[:2]:
                            c_name = c.get('course_name', c.get('course_id'))
                            if len(c_name) > 28:
                                c_name = c_name[:26] + "..."
                            trained_str = ", ".join(c["skills_to_get"][:2])
                            preview_items.append(
                                f'<div class="preview-course-item">→ <b>{c_name}</b> <span class="trains-tag">→ train {trained_str}</span></div>'
                            )
                        preview_html = "".join(preview_items)
                    elif not unowned:
                        preview_html = "<div class='preview-course-item' style='color:#059669;'>✓ Completed all competencies</div>"
                    else:
                        preview_html = "<div class='preview-course-item' style='color:#64748B;'>No direct elective match found</div>"

                    card_html = f"""
                    <div class="{card_class}">
                        <div>
                            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                                <div class="role-badge-icon">{icon}</div>
                                <span class="ai-fit-badge">{rec.fit_badge}</span>
                            </div>
                            <h4 class="role-title-text">{role_title}</h4>
                            <div style="font-size:0.75rem; color:#64748B; font-weight:600; margin-bottom:8px;">{badge_name}</div>
                            
                            <div class="ai-rationale-box">
                                <span style="font-weight:700; color:#1D4ED8;">✨ ทำไม AI ถึงแนะนำ:</span><br>
                                {rec.ai_rationale}
                            </div>
                            
                            <div class="skills-section-label">Owned Skills (เขียว):</div>
                            <div class="badge-chip-container">
                                {owned_chips}
                            </div>

                            <div class="skills-section-label">Unowned Skills (ส้ม/แดง):</div>
                            <div class="badge-chip-container">
                                {unowned_chips}
                            </div>
                        </div>

                        <div>
                            <div class="preview-courses-box">
                                <div class="preview-courses-title">📚 Recommended Electives Preview:</div>
                                {preview_html}
                            </div>
                        </div>
                    </div>
                    """
                    render_html(card_html)

                    btn_label = f"🔎 View Details & Courses"
                    st.button(
                        btn_label,
                        key=f"btn_select_{role_key}",
                        type="primary" if is_selected else "secondary",
                        use_container_width=True,
                        on_click=on_select_career_card,
                        args=(role_key, tab_labels[1])
                    )
        else:
            # Clean instruction box before generating
            render_html("""
            <div style="background:#F8FAFC; border:2px dashed #CBD5E1; border-radius:14px; padding:38px 24px; text-align:center; margin-top:16px;">
                <div style="font-size:2.4rem; margin-bottom:10px;">🎯</div>
                <h4 style="color:#0F172A; margin-bottom:8px; font-weight:700;">พร้อมค้นหาเส้นทางอาชีพและวิชาเลือกของคุณแล้วหรือยัง?</h4>
                <p style="color:#64748B; margin:0 auto; max-width:640px; font-size:0.95rem; line-height:1.6;">
                    เลือกโปรไฟล์ตัวอย่าง หรือคลิกเลือก Tag ทักษะที่คุณมีด้านบน จากนั้นกดปุ่ม <b>"🚀 ให้ AI วิเคราะห์และเลือกเส้นทางอาชีพที่เหมาะสม"</b><br>
                    หรือเปิดดูหมวดหมู่อาชีพทั้งหมดด้านล่าง (ทั้งสายการแพทย์, กฎหมาย, นิเทศ, ธุรกิจ, ดีไซน์ และเทค) เพื่อเลือกดูวิชาเลือกได้ทันที
                </p>
            </div>
            """)

        # Multidisciplinary Career Category Browser
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🌐 หรือสำรวจสายอาชีพทั้งหมดตามหมวดหมู่ (Browse All Careers by Category)", expanded=not st.session_state.get("has_generated_careers", False)):
            categories_list = [
                "ทั้งหมด (All)",
                "🩺 การแพทย์และสุขภาพ",
                "⚖️ กฎหมายและนิติศาสตร์",
                "🎬 นิเทศและสื่อดิจิทัล",
                "💼 ธุรกิจและการเงิน",
                "🎨 การออกแบบและความคิดสร้างสรรค์",
                "💻 เทคโนโลยีและวิศวกรรม"
            ]
            selected_cat = st.pills("Filter by Category", options=categories_list, default=categories_list[0], key="career_cat_filter", label_visibility="collapsed")
            
            filtered_roles = []
            for k, info in careers.items():
                cat = info.get("category", "")
                if selected_cat == "ทั้งหมด (All)":
                    filtered_roles.append(k)
                elif selected_cat.split(" ")[0] in cat or selected_cat in cat:
                    filtered_roles.append(k)
                    
            st.caption(f"พบ **{len(filtered_roles)}** สายอาชีพในหมวดที่เลือก — คลิก **'View Details'** เพื่อดูรายวิชาเลือกที่เกี่ยวข้อง")
            
            # Display in grid of 3 columns
            for r_idx in range(0, len(filtered_roles), 3):
                row_slice = filtered_roles[r_idx:r_idx+3]
                grid_cols = st.columns(len(row_slice))
                for c_idx, r_key in enumerate(row_slice):
                    c_info = careers[r_key]
                    r_title = c_info.get("title", r_key)
                    r_badge = c_info.get("badge", r_key)
                    r_icon = c_info.get("icon", "🎯")
                    r_desc = c_info.get("short_desc", c_info.get("description", "")[:90] + "...")
                    
                    owned_c, unowned_c, _ = calculate_career_skills(c_info, st.session_state["user_skills"])
                    recs_c = get_recommended_electives_for_career(courses, st.session_state["selected_university"], unowned_c)
                    
                    is_sel_c = (st.session_state.get("selected_career") == r_key)
                    card_cls_c = "career-grid-card active-selected" if is_sel_c else "career-grid-card"
                    
                    with grid_cols[c_idx]:
                        owned_chips_c = "".join([f"<span class='badge-owned'>✓ {s}</span>" for s in owned_c[:3]])
                        if len(owned_c) > 3:
                            owned_chips_c += f"<span class='badge-owned'>+{len(owned_c)-3}</span>"
                        if not owned_c:
                            owned_chips_c = "<span style='font-size:0.75rem; color:#94A3B8;'>None acquired yet</span>"

                        unowned_chips_c = "".join([f"<span class='badge-unowned'>✗ {s}</span>" for s in unowned_c[:3]])
                        if len(unowned_c) > 3:
                            unowned_chips_c += f"<span class='badge-unowned'>+{len(unowned_c)-3}</span>"
                        if not unowned_c:
                            unowned_chips_c = "<span class='badge-owned'>🎉 All acquired!</span>"

                        if recs_c:
                            p_items = []
                            for cr in recs_c[:2]:
                                cr_name = cr.get('course_name', cr.get('course_id'))
                                if len(cr_name) > 28:
                                    cr_name = cr_name[:26] + "..."
                                tr_str = ", ".join(cr["skills_to_get"][:2])
                                p_items.append(f'<div class="preview-course-item">→ <b>{cr_name}</b> <span class="trains-tag">→ {tr_str}</span></div>')
                            p_html = "".join(p_items)
                        elif not unowned_c:
                            p_html = "<div class='preview-course-item' style='color:#059669;'>✓ Completed all competencies</div>"
                        else:
                            p_html = "<div class='preview-course-item' style='color:#64748B;'>No direct elective match found</div>"

                        c_html = f"""
                        <div class="{card_cls_c}">
                            <div>
                                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
                                    <div class="role-badge-icon">{r_icon}</div>
                                    <span class="detail-course-id-badge">{r_badge}</span>
                                </div>
                                <h4 class="role-title-text">{r_title}</h4>
                                <div class="role-desc-text" style="font-size:0.83rem; margin-bottom:8px;">{r_desc}</div>
                                
                                <div class="skills-section-label">Owned Skills:</div>
                                <div class="badge-chip-container">
                                    {owned_chips_c}
                                </div>

                                <div class="skills-section-label">Unowned Skills:</div>
                                <div class="badge-chip-container">
                                    {unowned_chips_c}
                                </div>
                            </div>

                            <div>
                                <div class="preview-courses-box">
                                    <div class="preview-courses-title">📚 Recommended Electives:</div>
                                    {p_html}
                                </div>
                            </div>
                        </div>
                        """
                        render_html(c_html)
                        st.button(
                            "🔎 View Details & Courses",
                            key=f"btn_cat_sel_{r_key}",
                            type="primary" if is_sel_c else "secondary",
                            use_container_width=True,
                            on_click=on_select_career_card,
                            args=(r_key, tab_labels[1])
                        )

    # =========================================================================
    # TAB 2: CAREER & COURSE DRILL-DOWN VIEW (Switched here upon card click)
    # =========================================================================
    with tab_detail:
        selected_role_key = st.session_state.get("selected_career")
        ai_recs_state = st.session_state.get("ai_career_recommendations")
        
        # Build list containing all careers, with AI-recommended ones first
        ai_role_keys = [r.career_key for r in ai_recs_state.recommended_careers if r.career_key in careers] if (ai_recs_state and ai_recs_state.recommended_careers) else []
        all_role_keys = list(careers.keys())
        avail_roles = ai_role_keys + [k for k in all_role_keys if k not in ai_role_keys]

        if selected_role_key not in avail_roles and avail_roles:
            selected_role_key = avail_roles[0]
            st.session_state["selected_career"] = selected_role_key

        top_back_col, top_switch_col = st.columns([1, 2.2])
        with top_back_col:
            st.button(
                "← กลับไป Career Paths",
                key="btn_back_to_cards",
                use_container_width=True,
                on_click=on_switch_tab,
                args=(tab_labels[0],)
            )

        with top_switch_col:
            sel_idx = avail_roles.index(selected_role_key) if selected_role_key in avail_roles else 0
            def on_quick_role_switch():
                st.session_state["selected_career"] = st.session_state["tab2_quick_role_select"]
            st.selectbox(
                "เลือกดูสายอาชีพที่ต้องการวิเคราะห์ทันที",
                options=avail_roles,
                index=sel_idx,
                format_func=lambda k: f"{careers[k].get('icon', '🎯')} {careers[k].get('title', k)} ({careers[k].get('badge', k)}){' ⭐ [AI Recommended]' if k in ai_role_keys else ''}",
                key="tab2_quick_role_select",
                on_change=on_quick_role_switch,
                label_visibility="collapsed"
            )

        if selected_role_key and selected_role_key in careers:
            career = careers[selected_role_key]
            c_title = career.get("title", selected_role_key)
            c_badge = career.get("badge", selected_role_key)
            c_icon = career.get("icon", "🎯")
            c_desc = career.get("description", "")

            # Look up AI rationale for selected career
            ai_rec_item = None
            if ai_recs_state and ai_recs_state.recommended_careers:
                for r in ai_recs_state.recommended_careers:
                    if r.career_key == selected_role_key:
                        ai_rec_item = r
                        break

            owned_skills, unowned_skills, required_skills = calculate_career_skills(career, st.session_state["user_skills"])
            recommended_courses = get_recommended_electives_for_career(
                courses, st.session_state["selected_university"], unowned_skills
            )

            with st.container(border=True):
                render_html(f"<span class='detail-panel-badge'>📍 Selected Career Drill-Down View</span>")
                
                # 2-Column Layout (Left: Career & Skills / Right: Recommended Courses)
                d_left, d_right = st.columns([1.1, 1.2])

                # -----------------------------------------------------------------
                # Left Column (Career & Skill Breakdown)
                # -----------------------------------------------------------------
                with d_left:
                    render_html(f"""
                    <div class="detail-career-title">
                        <span>{c_icon}</span>
                        <span>{c_title} ({c_badge})</span>
                    </div>
                    """)

                    if ai_rec_item:
                        render_html(f"""
                        <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-left:4px solid #2563EB; border-radius:8px; padding:10px 14px; margin-bottom:14px;">
                            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                                <span class="ai-fit-badge">{ai_rec_item.fit_badge}</span>
                                <span style="font-size:0.82rem; font-weight:700; color:#1E40AF;">AI Recommendation Insight</span>
                            </div>
                            <div style="font-size:0.88rem; color:#1E3A8A; line-height:1.5;">{ai_rec_item.ai_rationale}</div>
                        </div>
                        """)

                    render_html(f"""
                    <div class="detail-job-desc">
                        <strong>Job Description & Industry Outlook:</strong><br>
                        {c_desc}
                    </div>
                    """)

                    total_req = len(required_skills)
                    owned_cnt = len(owned_skills)
                    pct = int((owned_cnt / total_req * 100)) if total_req > 0 else 0
                    
                    st.markdown(f"**Curriculum Readiness:** `{owned_cnt}/{total_req} Skills Acquired ({pct}%)`")
                    st.progress(pct / 100.0)

                    st.markdown("#### 🎯 Required Skills Breakdown")
                    
                    skill_sub1, skill_sub2 = st.columns(2)
                    with skill_sub1:
                        st.markdown("##### ❌ Unowned (ยังไม่มี)")
                        if unowned_skills:
                            for s in unowned_skills:
                                render_html(f"<div style='margin-bottom:6px;'><span class='badge-unowned' style='font-size:0.85rem; padding:5px 10px;'>✗ {s}</span></div>")
                        else:
                            st.success("🎉 You possess all required skills!")

                    with skill_sub2:
                        st.markdown("##### ✅ Owned (มีแล้ว)")
                        if owned_skills:
                            for s in owned_skills:
                                render_html(f"<div style='margin-bottom:6px;'><span class='badge-owned' style='font-size:0.85rem; padding:5px 10px;'>✓ {s}</span></div>")
                        else:
                            st.caption("No matching skills possessed yet.")

                # -----------------------------------------------------------------
                # Right Column (Recommended Courses)
                # -----------------------------------------------------------------
                with d_right:
                    st.markdown("### 📚 Recommended Courses")
                    st.caption(f"Curated electives at **{st.session_state['selected_university']}** specifically training your missing skills:")

                    if recommended_courses:
                        for c in recommended_courses:
                            skills_gained_html = "".join([f"<span class='badge-target-skill' style='margin-right:5px;'>★ {s}</span>" for s in c["skills_to_get"]])
                            other_skills = [s for s in c.get("skills_covered", []) if s not in c["skills_to_get"]]
                            other_skills_html = "".join([f"<span class='badge-owned' style='margin-right:5px; background:#F1F5F9; color:#475569; border-color:#CBD5E1;'>{s}</span>" for s in other_skills])

                            render_html(f"""
                            <div class="detail-course-card">
                                <div class="detail-course-header">
                                    <span class="detail-course-title">📖 {c.get('course_name')}</span>
                                    <span class="detail-course-id-badge">{c.get('course_id')} ({c.get('credits', 3)} Credits)</span>
                                </div>
                                <div class="detail-course-desc">{c.get('syllabus_description')}</div>
                                <div style="font-size:0.8rem; font-weight:700; color:#334155; margin-bottom:5px;">
                                    🎯 Skills to get (Bridges Gap):
                                </div>
                                <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:6px;">
                                    {skills_gained_html}
                                </div>
                                {f'<div style="font-size:0.75rem; color:#64748B; margin-top:4px;">Additional skills: {other_skills_html}</div>' if other_skills else ''}
                            </div>
                            """)
                    else:
                        if not unowned_skills:
                            render_html(f"""
                            <div style="background:#ECFDF5; border:1px solid #6EE7B7; border-radius:12px; padding:20px; text-align:center;">
                                <h4 style="color:#065F46; margin:0 0 8px 0;">🎉 Full Mastery Achieved!</h4>
                                <p style="color:#047857; margin:0; font-size:0.92rem;">
                                    You have already fulfilled all listed competencies for <b>{c_title}</b>.
                                </p>
                            </div>
                            """)
                        else:
                            render_html(f"""
                            <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:12px; padding:20px;">
                                <h4 style="color:#92400E; margin:0 0 8px 0;">🔍 No Direct Elective Found</h4>
                                <p style="color:#B45309; margin:0; font-size:0.92rem;">
                                    No specific elective course at <b>{st.session_state['selected_university']}</b> directly trains the unowned skills: {', '.join(unowned_skills)}.
                                </p>
                            </div>
                            """)
        else:
            st.info("ℹ️ ยังไม่ได้เลือกสายอาชีพ กรุณากลับไปที่แท็บ **'💼 1. Career Paths'** แล้วคลิก 'View Details' บนการ์ดอาชีพที่คุณสนใจ")
