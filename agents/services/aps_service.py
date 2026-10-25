"""
APS (Admission Point Score) calculation engine for South African Universities and TVETs.
Based on Department of Basic Education (DBE) National Senior Certificate (NSC) 7-level scale.
"""

def percentage_to_aps_level(percentage: float, is_life_orientation: bool = False) -> int:
    """
    Converts a percentage mark (0-100) to standard NSC APS points (1 to 7).
    """
    if percentage >= 80:
        points = 7
    elif percentage >= 70:
        points = 6
    elif percentage >= 60:
        points = 5
    elif percentage >= 50:
        points = 4
    elif percentage >= 40:
        points = 3
    elif percentage >= 30:
        points = 2
    else:
        points = 1
    return points


# Standard South African degrees, minimum APS, and required subjects
SA_DEGREE_CATALOG = [
    {
        "faculty": "Science & Information Technology",
        "title": "BSc in Computer Science / Information Technology",
        "min_aps": 34,
        "maths_required": "Pure Mathematics",
        "min_maths": 65,
        "universities": ["Wits", "UCT", "UP (Tuks)", "UJ", "Stellenbosch"],
        "description": "Software development, artificial intelligence, cybersecurity, and cloud systems."
    },
    {
        "faculty": "Science & Information Technology",
        "title": "Diploma in ICT (Applications Development / Networks)",
        "min_aps": 24,
        "maths_required": "Maths or Maths Literacy",
        "min_maths": 50,
        "universities": ["TUT", "CPUT", "VUT", "DUT", "TVET Colleges"],
        "description": "Practical application design, networking, and IT systems administration."
    },
    {
        "faculty": "Engineering & Built Environment",
        "title": "BSc / BEng in Electrical / Mechanical / Civil Engineering",
        "min_aps": 36,
        "maths_required": "Pure Mathematics",
        "min_maths": 70,
        "science_required": "Physical Sciences >= 70%",
        "universities": ["Wits", "UCT", "UP", "Stellenbosch", "UKZN"],
        "description": "Design and build national infrastructure, energy grids, robotics, and smart systems."
    },
    {
        "faculty": "Engineering & Built Environment",
        "title": "National Diploma / N-Diploma in Engineering Studies (N4-N6)",
        "min_aps": 22,
        "maths_required": "Maths or Technical Maths",
        "min_maths": 50,
        "universities": ["TVET Colleges (Orbit, Ekurhuleni East, False Bay, etc.)", "TUT"],
        "description": "Hands-on engineering trades, electrical wiring, boiler making, fitting and turning."
    },
    {
        "faculty": "Health Sciences",
        "title": "MBChB (Medicine and Surgery)",
        "min_aps": 42,
        "maths_required": "Pure Mathematics",
        "min_maths": 75,
        "science_required": "Physical Sciences >= 75%, Life Sciences >= 75%",
        "universities": ["Wits", "UCT", "UP", "SMU", "UKZN", "UFS"],
        "description": "Clinical diagnosis, medical surgery, and hospital patient healthcare."
    },
    {
        "faculty": "Health Sciences",
        "title": "BSc / Diploma in Nursing & Emergency Care",
        "min_aps": 28,
        "maths_required": "Maths or Maths Literacy",
        "min_maths": 50,
        "science_required": "Life Sciences >= 50%",
        "universities": ["UJ", "CPUT", "DUT", "Provincial Nursing Colleges"],
        "description": "Community health, clinical patient care, paramedic, and trauma response."
    },
    {
        "faculty": "Commerce & Management",
        "title": "BCom Accounting (CA Stream / SAICA)",
        "min_aps": 34,
        "maths_required": "Pure Mathematics",
        "min_maths": 65,
        "universities": ["Wits", "UJ", "UP", "UCT", "Rhodes"],
        "description": "Chartered Accountancy, auditing, financial management, and tax advisory."
    },
    {
        "faculty": "Commerce & Management",
        "title": "Diploma in Financial Management / Logistics / HR",
        "min_aps": 23,
        "maths_required": "Maths or Maths Literacy",
        "min_maths": 45,
        "universities": ["TUT", "UJ", "DUT", "Public TVET Colleges"],
        "description": "Business operations, supply chain logistics, banking, and payroll administration."
    },
    {
        "faculty": "Law & Humanities",
        "title": "Bachelor of Laws (LLB)",
        "min_aps": 32,
        "maths_required": "Maths or Maths Lit (English HL/FAL >= 65%)",
        "min_maths": 40,
        "universities": ["Wits", "UP", "UCT", "UJ", "NWU", "Fort Hare"],
        "description": "Legal counsel, constitutional law, court advocacy, and corporate governance."
    },
    {
        "faculty": "Education",
        "title": "Bachelor of Education (B.Ed - Foundation / Senior & FET Phase)",
        "min_aps": 28,
        "maths_required": "Maths or Maths Lit",
        "min_maths": 45,
        "universities": ["UJ", "Wits", "UP", "UKZN", "UNISA"],
        "description": "Primary or high school teaching. Eligible for full Funza Lushaka government bursary."
    },
    {
        "faculty": "TVET National Certificate Vocational (NCV)",
        "title": "NC(V) / Artisan Apprenticeship (Electrical, Plumbing, Automotive, Boilermaker)",
        "min_aps": 18,
        "maths_required": "Grade 9, 10, 11 or 12 with Maths/Maths Lit",
        "min_maths": 30,
        "universities": ["50 Public TVET Colleges across all 9 Provinces"],
        "description": "High-demand red-seal artisan trade qualifications funded by NSFAS with practical workplace training."
    }
]


def calculate_student_aps(subjects: list[dict]) -> dict:
    """
    Given a list of subjects:
    [
        {"name": "English HL", "mark": 74, "is_lo": False},
        ...
    ]
    Computes:
    - total_aps_standard: Top 6 subjects excluding Life Orientation (standard at most SA universities)
    - total_aps_with_lo: Top 6 subjects + LO points (used by universities like UJ)
    - subject_breakdown: Formatted list with points and levels
    - eligible_courses: List of courses student qualifies for based on min_aps
    - reach_courses: Courses within 3 APS points
    """
    if not subjects:
        return {
            "total_aps_standard": 0,
            "total_aps_with_lo": 0,
            "subject_breakdown": [],
            "eligible_courses": [],
            "reach_courses": [],
            "pass_status": "No subjects entered"
        }

    breakdown = []
    non_lo_scores = []
    lo_score = 0

    for s in subjects:
        mark = float(s.get("mark", 0))
        is_lo = s.get("is_lo", False) or "life orientation" in s.get("name", "").lower()
        level = percentage_to_aps_level(mark, is_lo)
        
        breakdown.append({
            "name": s.get("name", "Subject"),
            "mark": mark,
            "level": level,
            "is_lo": is_lo
        })

        if is_lo:
            lo_score = level
        else:
            non_lo_scores.append(level)

    # Sort non-LO scores descending
    non_lo_scores.sort(reverse=True)
    
    # Standard APS = top 6 non-LO subjects
    standard_aps = sum(non_lo_scores[:6])
    
    # APS with LO (e.g. UJ counts LO, up to max points)
    aps_with_lo = standard_aps + lo_score

    # Determine eligibility
    eligible = []
    reach = []

    for course in SA_DEGREE_CATALOG:
        required = course["min_aps"]
        if standard_aps >= required or aps_with_lo >= required:
            eligible.append(course)
        elif (standard_aps + 3) >= required:
            reach.append(course)

    # NSC Pass requirements check
    pass_status = "Bachelor Degree Pass (Eligible for University Degree admission)"
    if standard_aps < 23:
        pass_status = "Diploma Pass (Eligible for University of Technology / Diploma admission)"
    if standard_aps < 19:
        pass_status = "Higher Certificate / TVET Pass (Eligible for TVET College / NC(V) Certificates)"

    return {
        "total_aps_standard": standard_aps,
        "total_aps_with_lo": aps_with_lo,
        "subject_breakdown": breakdown,
        "eligible_courses": eligible,
        "reach_courses": reach,
        "pass_status": pass_status
    }
