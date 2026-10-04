from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class AICareerRecommendation(BaseModel):
    career_key: str = Field(description="Exact matching key from careers.json, e.g. 'DevOps', 'Data Sci', 'Backend / Distributed Systems Engineer', 'Full-Stack Web Architect', 'CyberSec', 'PM'")
    fit_badge: str = Field(description="Short badge label highlighting why it fits, e.g. '🔥 Best Match', '⚡ Strong Foundation', '💡 High Growth Pivot'")
    ai_rationale: str = Field(description="1-2 concise sentences in Thai explaining why this career is a great option for the student's background")

class AICareerRecommendationsResult(BaseModel):
    recommended_careers: List[AICareerRecommendation] = Field(description="Top 3 to 4 best matching or prospective career choices for this student (do not return all careers, choose the top 3-4 most relevant)")
    overall_summary: str = Field(description="Brief advisor note in Thai summarizing the student's tech profile strengths and potential")


class UniversityComparisonResult(BaseModel):
    target_career: str = Field(description="Target tech role for the comparison")
    focus_areas: Dict[str, str] = Field(
        description="Summary of focus areas for each university (key: Uni Name, value: Focus summary)"
    )
    unique_electives: Dict[str, List[str]] = Field(
        description="Key elective courses unique to each university relevant to the role"
    )
    tech_stack_differences: List[str] = Field(
        description="Key differences in tech stack / tools taught between the universities"
    )
    curriculum_scores: Optional[Dict[str, Dict[str, int]]] = Field(
        default=None,
        description="Scores out of 100 for theoretical_depth, industry_readiness, and elective_flexibility per university"
    )
    verdict: str = Field(
        description="Comprehensive AI Concierge verdict analyzing which university best fits the target career and why"
    )

class RecommendedCourse(BaseModel):
    course_id: str = Field(description="Course ID (e.g., CU-CS401)")
    course_name: str = Field(description="Full name of the course")
    university: str = Field(description="University offering the course")
    prerequisite_status: str = Field(description="Status of prerequisites (e.g. 'Satisfied' or 'Missing: Course X')")
    skills_gained: List[str] = Field(description="List of target career skills gained from this course")
    ai_justification: str = Field(description="Detailed reason why this elective is recommended for the user")
    credits: Optional[int] = Field(default=3, description="Course credits")

class StudyPlanPhase(BaseModel):
    phase_name: str = Field(description="Phase or Semester title (e.g. Phase 1: Core Fundamentals, Phase 2: Advanced Electives)")
    target_semester: str = Field(description="Suggested semester timing (e.g., Year 3 Semester 1)")
    course_ids: List[str] = Field(description="List of Course IDs in this phase")
    courses_included: List[str] = Field(description="List of Course Names in this phase")
    milestone_goal: str = Field(description="Key capability or portfolio project milestone achieved after completing this phase")

class CareerPlanAnalysisResult(BaseModel):
    target_career: str = Field(description="Target tech career role")
    acquired_skills: List[str] = Field(description="Skills the student already possesses")
    missing_core_skills: List[str] = Field(description="Required core skills for the role that the student currently lacks")
    missing_advanced_skills: List[str] = Field(description="Advanced skills for the role that the student currently lacks")
    readiness_percentage: float = Field(description="Calculated career readiness score (0 to 100)")
    core_readiness: Optional[float] = Field(default=None, description="Percentage of core skills mastered (0 to 100)")
    advanced_readiness: Optional[float] = Field(default=None, description="Percentage of advanced skills mastered (0 to 100)")
    recommended_courses: List[RecommendedCourse] = Field(description="Ranked list of recommended courses to bridge the skill gap")
    study_roadmap: List[StudyPlanPhase] = Field(description="Structured sequential study plan roadmap")
    portfolio_project: Optional[str] = Field(default=None, description="Recommended portfolio project to demonstrate competence")
    concierge_advice: str = Field(description="Personalized advice from EduPath AI Concierge")
