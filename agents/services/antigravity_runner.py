import asyncio
import re
from typing import AsyncGenerator
from .aps_service import SA_DEGREE_CATALOG

async def stream_agent_execution(prompt: str, profile=None) -> AsyncGenerator[str, None]:
    """
    Executes an autonomous agent task via the Antigravity SDK
    and streams tokens for mobile presentation.
    
    Includes intelligent South African Higher Education knowledge
    engine with dynamic profile context for local/offline deployment.
    """
    profile_info = ""
    student_aps = 0
    if profile:
        student_aps = getattr(profile, 'calculated_aps', 0) or 0
        if student_aps > 0:
            profile_info = f" [Student Profile: {profile.full_name}, Grade {profile.grade}, APS: {student_aps}]"

    # 1. Attempt using official google.antigravity SDK if installed
    try:
        from google.antigravity import Agent, LocalAgentConfig
        system_text = (
            "You are PfunzoBridge AI, an autonomous South African student advisor and education "
            "guidance agent. Provide structured, empathetic, and touch-friendly markdown summaries "
            "for South African matriculants, university, and TVET applicants."
        )
        if profile_info:
            system_text += f" Active user profile: {profile_info}."

        config = LocalAgentConfig(system_instructions=system_text)
        async with Agent(config) as agent:
            response = await agent.chat(prompt)
            async for token in response:
                yield token
        return
    except ImportError:
        pass
    except Exception as e:
        yield f"[Agent Warning: Switching to PfunzoBridge Autonomous Knowledge Engine: {str(e)}]\n\n"

    # 2. PfunzoBridge Knowledge Engine (Offline/Local Mobile-First Agent)
    cleaned_prompt = prompt.lower()

    # Detect if a specific APS score is mentioned in prompt (e.g. "APS is 34", "APS of 28", "APS: 30")
    aps_match = re.search(r'(?:aps\s*(?:is|of|score:?|score\s*is)?\s*|standard\s*aps\s*is\s*)(\d{1,2})', cleaned_prompt)
    target_aps = int(aps_match.group(1)) if aps_match else (student_aps if student_aps > 0 else None)

    # 1. Motivation Letters & Appeal Essays (High Priority - Must be checked BEFORE general bursaries)
    if any(k in cleaned_prompt for k in ['motivation', 'letter', 'appeal', 'essay']):
        thought = (
            "### ✍️ Official South African Bursary Motivation Letter Template\n\n"
            "Here is a proven, high-impact template designed for South African bursary committees (Sasol, ISFAP, Funza Lushaka, corporate schemes):\n\n"
            "---\n\n"
            "**[Your Full Name]**  \n"
            "[Your Residential Address, e.g. Soweto, Gauteng]  \n"
            "[Phone Number, e.g. 082 123 4567] | [Email Address]  \n"
            "**Date:** [e.g. 25 October 2026]  \n\n"
            "**To:**  \n"
            "The Bursary Selection Committee  \n"
            "[Name of Bursary Organization, e.g. Sasol Foundation / ISFAP / NSFAS]  \n"
            "[Organization Address / Department]  \n\n"
            "---\n\n"
            "**RE: APPLICATION FOR TERTIARY BURSARY FUNDING - [YOUR FULL NAME]**  \n"
            "**Applicant ID:** [Your South African ID Number]  \n"
            "**Intended Qualification:** [e.g. BSc in Computer Science / BEng Electrical / BCom Accounting]  \n"
            "**Target Institution:** [e.g. Wits University / University of Pretoria / UJ / UCT]  \n\n"
            "---\n\n"
            "**Dear Members of the Selection Committee,**\n\n"
            "I am writing to formally submit my application for the **[Bursary Name]** for the upcoming academic year. I am currently completing my Grade 12 National Senior Certificate (NSC) at **[School Name]**, maintaining consistent academic discipline with an Admission Point Score (APS) of **[Your APS, e.g. 34]** and strong performance in **[Key Subjects, e.g. Pure Mathematics (65%), Physical Sciences (68%), and English (70%)]**.\n\n"
            "My aspiration is to study **[Target Degree, e.g. Bachelor of Science in Computer Science]** because I am driven to help solve critical technical and socio-economic challenges in South Africa. Growing up in **[Your Community / Township / Town]**, I have witnessed firsthand the transformative power of higher education and technical skills. Despite financial constraints within my household (combined family income below the required threshold), I have remained focused on academic excellence, served as **[Leadership Role, e.g. Class Prefect / Peer Tutor]**, and assisted fellow learners in mathematics.\n\n"
            "Receiving the **[Bursary Name]** would relieve the heavy financial burden of university tuition fees, prescribed textbooks, accredited accommodation, and living expenses. This financial support will enable me to dedicate 100% of my energy toward excelling academically, graduating on record time, and contributing meaningfully to South Africa's economy and mentoring future matriculants.\n\n"
            "Enclosed with this letter are my certified Grade 11 report, Grade 12 Prelim results, certified copy of my South African ID, and parent/guardian proof of income.\n\n"
            "Thank you for your time, consideration, and continued investment in the future of South African youth. I look forward to the opportunity of discussing my application in an interview.\n\n"
            "Yours faithfully,  \n\n"
            "*(Signature)*  \n\n"
            "**[Your Full Name]**  \n"
            "Grade 12 Learner | Aspiring [Target Career, e.g. Software Engineer]  \n"
            "Contact: [Your Phone] | [Your Email]  \n\n"
            "---\n\n"
            "💡 **Top 4 Tips to Stand Out to Bursary Committees:**\n"
            "1. **Fill in all bracketed fields `[...]`** with your true details before submitting.\n"
            "2. **Highlight exact numbers:** State your exact APS and high marks in Pure Maths, Science, or Accounting.\n"
            "3. **Show community leadership:** Mention any school clubs, sport, tutoring, or church volunteering.\n"
            "4. **Use the 'Copy Text' button below** to copy this template directly into Word or your application portal!"
        )

    # 2. Specific APS Qualification Inquiry
    elif target_aps is not None and any(k in cleaned_prompt for k in ['recommend', 'qualify', 'degrees', 'what can i study', 'programmes', 'courses', 'wits', 'uj', 'uct', 'up', 'admission']):
        eligible = [c for c in SA_DEGREE_CATALOG if c["min_aps"] <= target_aps]
        reach = [c for c in SA_DEGREE_CATALOG if target_aps < c["min_aps"] <= (target_aps + 3)]

        thought = (
            f"### 🎯 Tailored Academic Evaluation: Standard APS {target_aps}\n\n"
            f"Great news! With an Admission Point Score of **{target_aps}**, here is your personalized university and bursary breakdown:\n\n"
            f"#### 🏛️ Direct University Degree Matches:\n"
        )
        if eligible:
            for c in eligible[:4]:
                unis = ", ".join(c["universities"][:3])
                thought += f"- **{c['title']}** (Min APS: {c['min_aps']})\n"
                thought += f"  - *Institutions:* {unis}\n"
                thought += f"  - *Prerequisite:* {c['maths_required']} (min {c['min_maths']}%)\n"
        else:
            thought += "- *Diploma & TVET Vocational pathways offer immediate admission at this score level.*\n"

        if reach:
            thought += f"\n#### ⚡ Close Reach / Competitive Programmes:\n"
            for c in reach[:2]:
                thought += f"- **{c['title']}** (Min APS: {c['min_aps']} — just {c['min_aps'] - target_aps} points away!)\n"

        thought += (
            f"\n#### 💼 High-Value Bursaries You Can Apply For:\n"
            f"- **NSFAS:** 100% full tuition, R1,650/month living stipend, accommodation & laptop funding (Household income < R350k).\n"
        )
        if target_aps >= 34:
            thought += (
                f"- **Sasol Foundation Bursary:** Top STEM funding for Engineering & Computer Science (Pure Maths & Science Level 6 required).\n"
                f"- **ISFAP Missing Middle Funding:** Comprehensive funding for household incomes between R350k and R600k.\n"
            )
        if target_aps >= 28:
            thought += f"- **Funza Lushaka Bursary:** 100% funding for Bachelor of Education (Teaching) degrees.\n"

        thought += (
            f"\n💡 *Next Steps:* Apply early through university portals before **30 September / 31 October** deadlines. Check our **Bursaries** tab to bookmark these schemes!"
        )

    # 3. Pure Maths vs Maths Literacy
    elif any(k in cleaned_prompt for k in ['maths lit', 'math literacy', 'mathematical literacy', 'pure maths', 'pure mathematics']):
        thought = (
            "### 📐 Pure Mathematics vs Mathematical Literacy: Higher Education Impact\n\n"
            "Choosing between Pure Maths and Maths Lit is one of the most critical decisions for South African learners:\n\n"
            "**1. Fields That STRICTLY Require Pure Mathematics:**\n"
            "- **Engineering (BSc/BEng):** Electrical, Civil, Mechanical, Mechatronics (Requires Pure Maths Level 5-6 / 60-70%+).\n"
            "- **Medicine & Surgery (MBChB) & Pharmacy:** Requires Pure Maths (60-75%+).\n"
            "- **Computer Science & Software Development (BSc):** Wits, UCT, UP require Pure Maths Level 5-6 (65%+).\n"
            "- **Actuarial Science & CA(SA) Accounting (BCom):** Requires Pure Maths Level 5-7 (65-80%+).\n\n"
            "**2. High-Growth Careers Where Mathematical Literacy is ACCEPTED:**\n"
            "- **Law (Bachelor of Laws - LLB):** Most universities (Wits, UJ, UP, UCT) accept Maths Lit (Level 4-6 / 50-70%) when combined with high English marks.\n"
            "- **Information Technology & Software Development (National Diploma):** TUT, CPUT, DUT, TVETs accept Maths Lit Level 4 (50%+).\n"
            "- **Nursing & Emergency Care:** Provincial nursing colleges accept Maths Lit with Life Sciences (50%+).\n"
            "- **Bachelor of Education (B.Ed):** Primary school & humanities high school teaching accept Maths Lit.\n"
            "- **Business Management, HR, Logistics, Marketing:** National Diplomas and BBA degrees accept Maths Lit.\n\n"
            "💡 *Strategic Advice:* If taking Maths Lit, aim for **Level 5 or 6 (60% - 79%)** to maximize your APS and keep diploma/degree doors wide open!"
        )

    # 4. Matric Upgrading & Second Chance
    elif any(k in cleaned_prompt for k in ['upgrade', 'rewrite', 'second chance', 'failed', 'supplementary', 'improve']):
        thought = (
            "### 🔄 Second Chance Matric & Marks Upgrade Guide\n\n"
            "If your matric marks did not meet your dream university degree cutoffs, do not lose hope! South Africa provides clear, official upgrade pathways:\n\n"
            "**1. DBE Second Chance Matric Programme (Free Government Support):**\n"
            "- The Department of Basic Education offers **free face-to-face tuition, study guides, and past exam packs** for learners upgrading subjects.\n"
            "- Official portal: [education.gov.za/Programmes/SecondChanceProgramme.aspx](https://www.education.gov.za).\n\n"
            "**2. Examination Rewrite Windows:**\n"
            "- **May / June National Senior Certificate Exams:** Open to learners who wrote matric in the previous November and want to upgrade specific subjects.\n"
            "- **Registration Deadline:** Usually closes in mid-February each year at provincial education district offices.\n\n"
            "**3. TVET NC(V) Alternative (Fast-Track to Employment):**\n"
            "- Public TVET colleges accept learners with Grade 9, 10, 11, or 12 into **NC(V) Level 2-4 and N-Diploma** programs.\n"
            "- These qualifications are 100% funded by NSFAS and lead directly to Red-Seal Artisan trades (Electrician, Boiler Maker, Millwright, IT Technician).\n\n"
            "💡 *Tip:* You can upgrade 1 or 2 critical subjects (like Pure Maths or Physical Sciences) while completing a TVET certificate simultaneously!"
        )

    # 5. Career Guidance Quiz Archetype Match
    elif any(k in cleaned_prompt for k in ['quiz', 'archetype', 'matched with the']):
        arch_title = "Selected Vocational Pathway"
        if "innovator" in cleaned_prompt:
            arch_title = "Innovator & Systems Builder (STEM & Tech)"
        elif "strategic" in cleaned_prompt or "analyst" in cleaned_prompt:
            arch_title = "Strategic Analyst & Problem Solver (Finance & Data)"
        elif "community" in cleaned_prompt or "healer" in cleaned_prompt:
            arch_title = "Community Healer & Educator (Healthcare & Law)"
        elif "visionary" in cleaned_prompt or "entrepreneur" in cleaned_prompt:
            arch_title = "Visionary Entrepreneur & Commercial Leader (Business & Tech)"

        thought = (
            f"### 🧭 Action Plan for Your Career Profile: {arch_title}\n\n"
            f"Based on your vocational match from the PfunzoBridge Career Quiz, here is your roadmap:\n\n"
            f"**1. Recommended Matric Subject Focus:**\n"
            f"- Maintain consistent marks in English (Compulsory Level 4+).\n"
            f"- Align your quantitative stream: Ensure target minimums for Pure Maths or Maths Lit.\n\n"
            f"**2. High-Priority Institutions:**\n"
            f"- Top Universities: Wits, UCT, University of Pretoria (UP), University of Johannesburg (UJ).\n"
            f"- Technical & TVET Options: TUT, CPUT, and Provincial TVET Colleges for accredited diplomas.\n\n"
            f"**3. Funding Checklist:**\n"
            f"- Apply for NSFAS as early as September.\n"
            f"- Check industry-specific corporate bursaries in our **Bursaries** tab.\n\n"
            f"💡 *Tip: Head to our **APS Calculator** tab to enter your exact subject marks and verify your point standing for this career pathway!*"
        )

    # 6. NSFAS & Financial Aid
    elif any(k in cleaned_prompt for k in ['nsfas', 'financial aid']):
        thought = (
            "### 🎓 PfunzoBridge Funding Intelligence: NSFAS 2026/2027 Guidelines\n\n"
            "**Key NSFAS Eligibility Criteria:**\n"
            "- **Household Income Threshold:** Combined gross family income must not exceed **R350,000 per annum** (or **R600,000** for students with a recognized disability).\n"
            "- **SASSA Beneficiaries:** If you or your parents receive a SASSA grant (e.g. Child Support Grant), you qualify **automatically** with no financial vetting required!\n"
            "- **Supported Institutions:** All 26 South African public universities (Wits, UCT, UP, UJ, UKZN, etc.) and all 50 public TVET colleges.\n\n"
            "**What NSFAS Covers:**\n"
            "- 100% of approved tuition and registration fees.\n"
            "- Monthly living allowance (~R1,650/month directly into your student bank account).\n"
            "- Standard university residence or accredited private accommodation allowance.\n"
            "- Annual personal care allowance and prescribed learning materials (laptop/books).\n\n"
            "**Urgent Action Checklist:**\n"
            "1. Create your profile on [my.nsfas.org.za](https://www.nsfas.org.za).\n"
            "2. Have your certified South African ID, consent form, and parents' proof of income (payslips or SASSA proof) ready in PDF format (<2MB).\n"
            "3. Remember: You can apply for NSFAS **even before** receiving your final university acceptance letter!"
        )

    # 7. Bursary Inquiries (General directory / listings)
    elif any(k in cleaned_prompt for k in ['bursary', 'bursaries', 'sasol', 'allan gray', 'isfap', 'funza', 'funding']):
        thought = (
            "### 💼 South African High-Value Bursary Advisory\n\n"
            "Top funding opportunities open for South African learners:\n\n"
            "1. **Funza Lushaka Bursary:**\n"
            "   - *Covers:* 100% tuition, meals, accommodation & stipend for B.Ed degrees.\n"
            "   - *Condition:* Service obligation to teach in public schools upon qualification.\n\n"
            "2. **Sasol Foundation Bursary:**\n"
            "   - *Focus:* Engineering, Chemistry, Data Science, and Computer Science.\n"
            "   - *Minimum:* Pure Mathematics Level 6 (70%) and Physical Sciences Level 6.\n\n"
            "3. **ISFAP (Missing Middle Funding):**\n"
            "   - *Target:* Families earning between R350,000 and R600,000 annually.\n"
            "   - *Focus:* Critical skills (Medicine, Engineering, CA(SA), Nursing).\n\n"
            "4. **Allan Gray Orbis Fellowship:**\n"
            "   - *Target:* Aspiring high-impact entrepreneurs. Requires 60%+ in Pure Maths.\n\n"
            "Check our **Bursaries** tab to bookmark these deadlines and download application checklists!"
        )

    # 8. APS General Strategy Guide
    elif any(k in cleaned_prompt for k in ['aps', 'score', 'points', 'calculate', 'marks', 'level']):
        thought = (
            "### 📊 South African APS (Admission Point Score) Strategy Guide\n\n"
            "Your Admission Point Score (APS) is calculated using the **7-point NSC achievement scale**:\n"
            "- **Level 7 (80% - 100%):** 7 Points\n"
            "- **Level 6 (70% - 79%):** 6 Points\n"
            "- **Level 5 (60% - 69%):** 5 Points\n"
            "- **Level 4 (50% - 59%):** 4 Points\n"
            "- **Level 3 (40% - 49%):** 3 Points\n"
            "- **Level 2 (30% - 39%):** 2 Points\n"
            "- **Level 1 (0% - 29%):** 1 Point\n\n"
            "**University Specific Rules:**\n"
            "- **Wits, UCT, UP, UKZN:** Top 6 subjects **excluding Life Orientation**.\n"
            "- **UJ (University of Johannesburg):** Includes Life Orientation (scaled to 1-4 points depending on faculty).\n"
            "- **Minimum Pass Levels for Degree Study:** Bachelor's endorsement requires minimum Level 4 (50%+) in 4 designated subjects and minimum Level 3 in English.\n\n"
            "💡 *Tip: Head to our built-in **APS Calculator** tab below to enter your exact subjects and see which degrees you qualify for instantly!*"
        )

    # 9. In-Demand Careers & High-Growth Sectors
    elif any(k in cleaned_prompt for k in ['career', 'tvet', 'university', 'job', 'salary', 'salaries']):
        thought = (
            "### 🚀 South African Career Pathways & In-Demand Sectors\n\n"
            "According to the latest DHET National List of Occupations in High Demand (OIHD):\n\n"
            "- **Tech & Innovation:** Software Engineering, Cloud Computing, Cybersecurity, Mobile Development (Average starting salary: R25,000 - R40,000/mo).\n"
            "- **Engineering & Green Energy:** Solar/Wind Technicians, Electrical Engineers, Mechatronics.\n"
            "- **Healthcare:** Professional Nurses, Clinical Associates, Biomedical Technologists.\n"
            "- **TVET Artisans:** Electricians, Millwrights, Welders, Toolmakers (Red-Seal qualification offers rapid employment with high demand).\n\n"
            "🎯 *Use our **Career Quiz** tab to discover your vocational archetype and personalized pathway!*"
        )

    # 10. General Counselor Guidance
    else:
        thought = (
            f"### 🤖 PfunzoBridge SA Agent Counselor\n\n"
            f"Thank you for reaching out regarding: *\"{prompt.strip()}\"*\n\n"
            "As your dedicated South African Education Guide, here is how we can assist you:\n\n"
            "1. **APS Calculation:** Calculate your exact Admission Point Score according to DBE and university rules.\n"
            "2. **Degree & TVET Matching:** Find which public universities (Wits, UCT, UP, UJ, TUT) or TVET colleges match your marks.\n"
            "3. **Funding & NSFAS:** Guidance on financial aid thresholds, required documents, and appeal letters.\n"
            "4. **Career Discovery:** Take our interactive quiz to align your strengths with high-demand South African industries.\n\n"
            "Feel free to ask specific questions, such as:\n"
            "- *\"What courses can I study with an APS of 34?\"*\n"
            "- *\"What is the difference between Maths Literacy and Pure Maths for IT degrees?\"*\n"
            "- *\"How do I write an appeal letter for NSFAS?\"*\n"
            "- *\"How do I upgrade my matric marks if I failed?\"*"
        )

    # Stream out token by token with realistic async typing
    words = re.findall(r'\S+|\n\n|\n', thought)
    for word in words:
        if word in ['\n', '\n\n']:
            yield word
        else:
            yield word + " "
        await asyncio.sleep(0.015)
