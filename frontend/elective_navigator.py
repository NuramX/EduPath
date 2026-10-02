import streamlit as st
from typing import List, Dict, Any, Set
from services.data_loader import load_courses, load_careers, get_universities, get_all_skills

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

    /* Career Card Styles */
    .career-grid-card {
        background: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 3px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.25s ease-in-out;
        min-height: 410px;
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

    if "skills_text_input" not in st.session_state:
        st.session_state["skills_text_input"] = "c++, python, marketing"

    if "user_skills" not in st.session_state or not st.session_state["user_skills"]:
        st.session_state["user_skills"] = parse_skills_from_text(st.session_state["skills_text_input"], all_skills)

    if "selected_career" not in st.session_state or not st.session_state["selected_career"]:
        default_role = "DevOps" if "DevOps" in careers else list(careers.keys())[0]
        st.session_state["selected_career"] = default_role

    if "has_generated_careers" not in st.session_state:
        st.session_state["has_generated_careers"] = False

    # Tabs configuration
    tab_labels = ["💼 1. Career Paths", "📋 2. Career Details & Electives"]
    if "navigator_active_tab" not in st.session_state or st.session_state["navigator_active_tab"] not in tab_labels:
        st.session_state["navigator_active_tab"] = tab_labels[0]

    # =========================================================================
    # Header Section
    # =========================================================================
    st.markdown("""
    <div class="navigator-header-box">
        <div class="navigator-title">🧭 Elective Navigator</div>
        <p class="navigator-subtitle">
            Explore high-demand tech career paths, assess your acquired skill competencies, and uncover tailored elective course recommendations from your university curriculum.
        </p>
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("<div class='filter-wrapper'>", unsafe_allow_html=True)
        f_col1, f_col2 = st.columns([1, 2])

        with f_col1:
            st.markdown("##### 🏛️ University Selector (ชื่อมหาลัย)")
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

        with f_col2:
            st.markdown("##### ⚡ Current Skills Input (Skills: txt ex. c++,python,marketing)")
            current_txt = st.text_input(
                "Enter your current skills",
                value=st.session_state["skills_text_input"],
                placeholder="ex. c++, python, marketing, sql",
                label_visibility="collapsed",
                key="skills_txt_input",
                help="Type comma-separated skills, e.g. c++, python, marketing, sql"
            )
            st.session_state["skills_text_input"] = current_txt

        st.markdown("<div style='margin-top:14px;'>", unsafe_allow_html=True)
        gen_clicked = st.button("🚀 Generate Career Paths", type="primary", use_container_width=True)
        if gen_clicked:
            st.session_state["user_skills"] = parse_skills_from_text(current_txt, all_skills)
            st.session_state["has_generated_careers"] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Career Path Cards Section (Only shown after Generate is clicked)
        if st.session_state.get("has_generated_careers", False):
            st.markdown("### 💼 Career Path Competency Cards")
            st.caption("คลิกปุ่ม **'View Details'** บนการ์ดใดก็ได้ เพื่อเด้งไปยังแท็บ **'📋 2. Career Details & Electives'** เพื่อดูรายละเอียดและวิชาที่แนะนำ")

            target_roles = ["DevOps", "CyberSec", "Data Sci", "PM"]
            active_role_keys = [r for r in target_roles if r in careers]
            if not active_role_keys:
                active_role_keys = list(careers.keys())[:4]

            cols = st.columns(len(active_role_keys))

            for idx, role_key in enumerate(active_role_keys):
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

                    # Recommended courses mini-preview: -> Name -> train x skills
                    preview_html = ""
                    if recommended_courses:
                        for c in recommended_courses[:2]:
                            c_name = c.get('course_name', c.get('course_id'))
                            if len(c_name) > 28:
                                c_name = c_name[:26] + "..."
                            trained_str = ", ".join(c["skills_to_get"][:2])
                            preview_html += f"""
                            <div class="preview-course-item">
                                → <b>{c_name}</b> <span class="trains-tag">→ train {trained_str}</span>
                            </div>
                            """
                    elif not unowned:
                        preview_html = "<div class='preview-course-item' style='color:#059669;'>✓ Completed all competencies</div>"
                    else:
                        preview_html = "<div class='preview-course-item' style='color:#64748B;'>No direct elective match found</div>"

                    card_html = f"""
                    <div class="{card_class}">
                        <div>
                            <div class="card-header-row">
                                <div class="role-badge-icon">{icon}</div>
                                <div>
                                    <h4 class="role-title-text">{badge_name}</h4>
                                    <span style="font-size:0.72rem; color:#64748B; font-weight:600;">{role_title}</span>
                                </div>
                            </div>
                            <div class="role-desc-text">{short_desc}</div>
                            
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
                                <div class="preview-courses-title">📚 Recommended Preview:</div>
                                {preview_html}
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)

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
            st.markdown("""
            <div style="background:#F8FAFC; border:2px dashed #CBD5E1; border-radius:14px; padding:38px 24px; text-align:center; margin-top:16px;">
                <div style="font-size:2.4rem; margin-bottom:10px;">🎯</div>
                <h4 style="color:#0F172A; margin-bottom:8px; font-weight:700;">พร้อมค้นหาเส้นทางอาชีพของคุณแล้วหรือยัง?</h4>
                <p style="color:#64748B; margin:0 auto; max-width:620px; font-size:0.95rem; line-height:1.6;">
                    กรอกทักษะปัจจุบันของคุณในช่องข้อความด้านบน (เช่น <code>c++, python, marketing</code>) และเลือกมหาวิทยาลัย<br>
                    จากนั้นกดปุ่ม <b>"🚀 Generate Career Paths"</b> เพื่อคำนวณและแสดง Career Competency Cards
                </p>
            </div>
            """, unsafe_allow_html=True)

    # =========================================================================
    # TAB 2: CAREER & COURSE DRILL-DOWN VIEW (Switched here upon card click)
    # =========================================================================
    with tab_detail:
        top_back_col, _ = st.columns([1, 4])
        with top_back_col:
            st.button(
                "← กลับไป Career Paths",
                key="btn_back_to_cards",
                use_container_width=True,
                on_click=on_switch_tab,
                args=(tab_labels[0],)
            )

        selected_role_key = st.session_state.get("selected_career")
        if selected_role_key and selected_role_key in careers:
            career = careers[selected_role_key]
            c_title = career.get("title", selected_role_key)
            c_badge = career.get("badge", selected_role_key)
            c_icon = career.get("icon", "🎯")
            c_desc = career.get("description", "")
            
            owned_skills, unowned_skills, required_skills = calculate_career_skills(career, st.session_state["user_skills"])
            recommended_courses = get_recommended_electives_for_career(
                courses, st.session_state["selected_university"], unowned_skills
            )

            st.markdown("<div class='detail-panel-box'>", unsafe_allow_html=True)
            st.markdown(f"<span class='detail-panel-badge'>📍 Selected Career Drill-Down View</span>", unsafe_allow_html=True)
            
            # 2-Column Layout (Left: Career & Skills / Right: Recommended Courses)
            d_left, d_right = st.columns([1.1, 1.2])

            # -----------------------------------------------------------------
            # Left Column (Career & Skill Breakdown)
            # -----------------------------------------------------------------
            with d_left:
                st.markdown(f"""
                <div class="detail-career-title">
                    <span>{c_icon}</span>
                    <span>{c_title} ({c_badge})</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="detail-job-desc">
                    <strong>Job Description & Industry Outlook:</strong><br>
                    {c_desc}
                </div>
                """, unsafe_allow_html=True)

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
                            st.markdown(f"<div style='margin-bottom:6px;'><span class='badge-unowned' style='font-size:0.85rem; padding:5px 10px;'>✗ {s}</span></div>", unsafe_allow_html=True)
                    else:
                        st.success("🎉 You possess all required skills!")

                with skill_sub2:
                    st.markdown("##### ✅ Owned (มีแล้ว)")
                    if owned_skills:
                        for s in owned_skills:
                            st.markdown(f"<div style='margin-bottom:6px;'><span class='badge-owned' style='font-size:0.85rem; padding:5px 10px;'>✓ {s}</span></div>", unsafe_allow_html=True)
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

                        st.markdown(f"""
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
                        """, unsafe_allow_html=True)
                else:
                    if not unowned_skills:
                        st.markdown(f"""
                        <div style="background:#ECFDF5; border:1px solid #6EE7B7; border-radius:12px; padding:20px; text-align:center;">
                            <h4 style="color:#065F46; margin:0 0 8px 0;">🎉 Full Mastery Achieved!</h4>
                            <p style="color:#047857; margin:0; font-size:0.92rem;">
                                You have already fulfilled all listed competencies for <b>{c_title}</b>.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background:#FFFBEB; border:1px solid #FCD34D; border-radius:12px; padding:20px;">
                            <h4 style="color:#92400E; margin:0 0 8px 0;">🔍 No Direct Elective Found</h4>
                            <p style="color:#B45309; margin:0; font-size:0.92rem;">
                                No specific elective course at <b>{st.session_state['selected_university']}</b> directly trains the unowned skills: {', '.join(unowned_skills)}.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("ℹ️ ยังไม่ได้เลือกสายอาชีพ กรุณากลับไปที่แท็บ **'💼 1. Career Paths'** แล้วคลิก 'View Details' บนการ์ดอาชีพที่คุณสนใจ")
