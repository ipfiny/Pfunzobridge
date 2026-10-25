"""
Initial data catalog for South African Bursaries, Career Quiz Questions, and Pathways.
"""
from datetime import date

DEFAULT_BURSARIES = [
    {
        "name": "NSFAS (National Student Financial Aid Scheme)",
        "provider": "Department of Higher Education & Training (DHET)",
        "category": "Government Full Bursary",
        "minimum_aps": 20,
        "eligible_fields": "All undergraduate degrees, diplomas & TVET NC(V) / Report 191 courses",
        "deadline_text": "31 January 2027",
        "deadline_date": date(2027, 1, 31),
        "coverage_details": "100% Tuition, Registration fees, Monthly Living Allowance (~R1,650/mo), Accommodation or Transport Allowance, and Personal Care/Learning Materials Allowance.",
        "application_url": "https://www.nsfas.org.za",
        "featured": True
    },
    {
        "name": "Funza Lushaka Teaching Bursary",
        "provider": "Department of Basic Education (DBE)",
        "category": "Government Sectoral Bursary",
        "minimum_aps": 28,
        "eligible_fields": "Bachelor of Education (B.Ed) or PGCE in priority subjects (Maths, Science, Tech, African Languages, Foundation Phase)",
        "deadline_text": "02 February 2027",
        "deadline_date": date(2027, 2, 2),
        "coverage_details": "Full tuition fees, accommodation with meals, prescribed book allowances, and monthly living stipend. Service contractual agreement upon graduation.",
        "application_url": "https://www.funzalushaka.doe.gov.za",
        "featured": True
    },
    {
        "name": "Sasol Foundation Bursary",
        "provider": "Sasol Foundation",
        "category": "Corporate STEM Bursary",
        "minimum_aps": 32,
        "eligible_fields": "Chemical / Mechanical / Electrical Engineering, Computer Science, Data Science, Chemistry",
        "deadline_text": "31 May 2026",
        "deadline_date": date(2026, 5, 31),
        "coverage_details": "Full tuition, residence, meal allowance, book allowance, laptop allocation, and vacation work opportunities.",
        "application_url": "https://www.sasolbursaries.com",
        "featured": True
    },
    {
        "name": "ISFAP (Ikusasa Student Financial Aid Programme)",
        "provider": "ISFAP / Private Sector Donors",
        "category": "Missing Middle & Full Funding",
        "minimum_aps": 30,
        "eligible_fields": "Occupations in High Demand (Engineering, Medicine, Actuarial Science, CA(SA), Nursing, IT)",
        "deadline_text": "31 October 2026",
        "deadline_date": date(2026, 10, 31),
        "coverage_details": "Tuition, accommodation, study materials, monthly stipend, plus wraparound psycho-social and academic mentoring.",
        "application_url": "https://www.isfap.org.za",
        "featured": True
    },
    {
        "name": "Allan Gray Orbis Fellowship",
        "provider": "Allan Gray Orbis Foundation",
        "category": "Entrepreneurship & Leadership Bursary",
        "minimum_aps": 35,
        "eligible_fields": "Commerce, Science, Engineering, Law, Humanities (Pure Maths >= 60% required)",
        "deadline_text": "30 April 2027",
        "deadline_date": date(2027, 4, 30),
        "coverage_details": "Comprehensive cost of tertiary education, private mentoring, leadership camps, entrepreneurial venture support, and international exposure.",
        "application_url": "https://www.allangrayorbis.org",
        "featured": True
    },
    {
        "name": "Motsepe Foundation Bursary",
        "provider": "The Motsepe Foundation",
        "category": "Community Development Bursary",
        "minimum_aps": 26,
        "eligible_fields": "STEM, Business Studies, Agriculture, Law, and Creative Arts",
        "deadline_text": "15 January 2027",
        "deadline_date": date(2027, 1, 15),
        "coverage_details": "Partial to full tuition coverage, prescribed textbooks, and registration fees for financially deserving learners.",
        "application_url": "https://www.motsepefoundation.org",
        "featured": False
    },
    {
        "name": "CSIR Postgraduate & Undergraduate Bursary",
        "provider": "Council for Scientific and Industrial Research",
        "category": "National Research & Science",
        "minimum_aps": 34,
        "eligible_fields": "Applied Maths, Physics, Mechatronics, Biotechnology, Artificial Intelligence, Electronics",
        "deadline_text": "15 August 2026",
        "deadline_date": date(2026, 8, 15),
        "coverage_details": "Tuition fees, prescribed books, laptop allowance, accommodation, and research mentorship at CSIR national laboratories.",
        "application_url": "https://www.csir.co.za/bursaries",
        "featured": False
    },
    {
        "name": "Shoprite Group Bursaries",
        "provider": "Shoprite Holdings",
        "category": "Retail & Supply Chain",
        "minimum_aps": 28,
        "eligible_fields": "Supply Chain, Logistics, Data Science, Pharmacy, Retail Business Management, Food Science",
        "deadline_text": "30 September 2026",
        "deadline_date": date(2026, 9, 30),
        "coverage_details": "Tuition, on-campus accommodation, allowance, plus guaranteed employment contract upon graduation.",
        "application_url": "https://www.shopriteholdings.co.za/careers.html",
        "featured": False
    }
]

CAREER_QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "When working on a group school project, which role comes most naturally to you?",
        "options": [
            {"text": "Designing the system, coding or building models with hands-on tools", "trait": "tech_builder"},
            {"text": "Analyzing the numbers, researching data, and solving logic puzzles", "trait": "analytical"},
            {"text": "Caring for teammates, mediating discussions, and explaining ideas to others", "trait": "people_social"},
            {"text": "Taking the lead, pitching the presentation, and managing resources/money", "trait": "enterprise_business"}
        ]
    },
    {
        "id": 2,
        "question": "Which school subjects or activities give you the most energy?",
        "options": [
            {"text": "Information Tech, Computer Applications Tech (CAT), or Physical Sciences", "trait": "tech_builder"},
            {"text": "Pure Mathematics, Accounting, or Economics", "trait": "analytical"},
            {"text": "Life Sciences, History, English Literature, or Life Orientation community work", "trait": "people_social"},
            {"text": "Business Studies, Debate, Junior Achievement, or Student Council", "trait": "enterprise_business"}
        ]
    },
    {
        "id": 3,
        "question": "What kind of work environment excites you most for your future?",
        "options": [
            {"text": "A tech hub, engineering lab, robotics workshop, or renewable energy site", "trait": "tech_builder"},
            {"text": "A financial institution, investment firm, research center, or actuarial lab", "trait": "analytical"},
            {"text": "A hospital, community clinic, high school classroom, or legal aid clinic", "trait": "people_social"},
            {"text": "A thriving start-up, corporate boardroom, or running my own company", "trait": "enterprise_business"}
        ]
    },
    {
        "id": 4,
        "question": "How do you prefer to solve real-world problems facing South Africa?",
        "options": [
            {"text": "Building smart low-cost tech apps, fixing infrastructure, or solar/water solutions", "trait": "tech_builder"},
            {"text": "Auditing budgets, optimizing supply chains, and preventing financial crime", "trait": "analytical"},
            {"text": "Teaching youth, treating illnesses, or advocating for human rights and justice", "trait": "people_social"},
            {"text": "Creating jobs, commercializing local inventions, and trade partnerships", "trait": "enterprise_business"}
        ]
    },
    {
        "id": 5,
        "question": "Which learning pathway sounds most appealing to you after Matric?",
        "options": [
            {"text": "Practical hands-on apprenticeships or fast-paced technical coding diplomas", "trait": "tech_builder"},
            {"text": "Intensive university bachelor's degree with quantitative research", "trait": "analytical"},
            {"text": "Professional certification with clinical rotations or classroom teaching internships", "trait": "people_social"},
            {"text": "Entrepreneurship accelerator, commerce degree, or sales/marketing management", "trait": "enterprise_business"}
        ]
    }
]

CAREER_ARCHETYPES = {
    "tech_builder": {
        "title": "Innovator & Systems Builder",
        "badge": "STEM & Digital Economy",
        "description": "You thrive when building, creating tangible solutions, understanding how things work under the hood, and solving practical problems.",
        "top_careers": [
            "Software & Mobile App Developer",
            "Electrical / Renewable Energy Engineer",
            "Robotics & Automation Specialist",
            "Red-Seal Qualified Artisan (Electrician / Mechatronics)",
            "Cloud & Cybersecurity Architect"
        ],
        "top_institutions": ["Wits", "UP", "UCT", "TUT", "Public TVET Colleges"],
        "recommended_path": "BSc Computer Science, BEng Engineering, or National Diploma in IT / TVET N4-N6 Electrical.",
        "bursaries": ["Sasol Foundation", "CSIR", "ISFAP", "NSFAS"]
    },
    "analytical": {
        "title": "Strategic Analyst & Problem Solver",
        "badge": "Finance, Data & Research",
        "description": "You excel with logic, patterns, financial structures, precision, and deep data-driven problem solving.",
        "top_careers": [
            "Chartered Accountant (CA SA)",
            "Data Scientist & AI Quantitative Analyst",
            "Actuarial Scientist",
            "Investment Banker & Financial Risk Manager",
            "Economist & Policy Researcher"
        ],
        "top_institutions": ["UCT", "Wits", "UJ", "UP", "Stellenbosch"],
        "recommended_path": "BCom Accounting (SAICA), BSc Applied Mathematics, or BCom Econometrics.",
        "bursaries": ["Allan Gray Orbis", "Standard Bank CSI", "ISFAP", "NSFAS"]
    },
    "people_social": {
        "title": "Community Healer & Educator",
        "badge": "Healthcare, Education & Public Service",
        "description": "You are driven by empathy, community empowerment, human health, social justice, and transferring knowledge.",
        "top_careers": [
            "Medical Doctor / Clinical Associate",
            "Registered Nurse & Emergency Paramedic",
            "High School / FET Teacher (Maths & Sciences)",
            "Human Rights Advocate / Legal Counsel",
            "Public Health Specialist"
        ],
        "top_institutions": ["SMU", "Wits", "UP", "UCT", "UJ", "Provincial Nursing Colleges"],
        "recommended_path": "MBChB, BSc Nursing, B.Ed (Funza Lushaka), or Bachelor of Laws (LLB).",
        "bursaries": ["Funza Lushaka", "NSFAS", "ISFAP", "Motsepe Foundation"]
    },
    "enterprise_business": {
        "title": "Visionary Entrepreneur & Commercial Leader",
        "badge": "Business, Trade & Leadership",
        "description": "You possess natural drive, leadership charisma, commercial instincts, and the ambition to organize teams and build enterprises.",
        "top_careers": [
            "Tech Startup Founder & Entrepreneur",
            "Supply Chain & Operations Director",
            "Marketing & Brand Strategist",
            "Commercial Corporate Lawyer",
            "Project Management Executive"
        ],
        "top_institutions": ["UJ", "Wits", "UP", "UCT", "TUT"],
        "recommended_path": "BCom Business Management, BCom Marketing, Logistics Diploma, or Allan Gray Fellowship.",
        "bursaries": ["Allan Gray Orbis Foundation", "Shoprite Group", "NSFAS"]
    }
}
