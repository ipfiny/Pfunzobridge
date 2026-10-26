"""
PfunzoBridge POPIA Data Export Service
Generates official PDF reports of student personal data in accordance with
Sections 23 and 24 of the Protection of Personal Information Act (POPIA Act 4 of 2013).
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_learner_popia_pdf(user, profile, tracked_bursaries, submitted_applications):
    """
    Builds a styled PDF containing all personal and academic data held for the user.
    Returns a bytes object of the generated PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom brand styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#008479'),
        alignment=TA_LEFT
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#64748b'),
        alignment=TA_LEFT
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    body_bold = ParagraphStyle(
        'TableBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a')
    )

    legal_style = ParagraphStyle(
        'LegalText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )

    elements = []

    # 1. Document Header
    now_str = datetime.now().strftime("%d %B %Y, %H:%M SAST")
    ref_id = f"PB-POPIA-{user.id:04d}-{int(datetime.now().timestamp()) % 1000000:06d}"

    elements.append(Paragraph("<b>PfunzoBridge &bull; POPIA Data Subject Access Report</b>", title_style))
    elements.append(Paragraph(
        f"Generated under Sections 23 &amp; 24 of the Protection of Personal Information Act (Act 4 of 2013)<br/>"
        f"<b>Official Record Reference:</b> {ref_id} &nbsp;|&nbsp; <b>Export Timestamp:</b> {now_str}",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#008479'), spaceAfter=12))

    # 2. Learner Identity Information Table
    elements.append(Paragraph("1. Learner Account &amp; Identity Profile", section_heading))
    identity_data = [
        [Paragraph("<b>Username</b>", body_style), Paragraph(user.username, body_style),
         Paragraph("<b>Full Legal Name</b>", body_style), Paragraph(profile.full_name or "Not provided", body_style)],
        [Paragraph("<b>Registered Email</b>", body_style), Paragraph(user.email or profile.email or "Not provided", body_style),
         Paragraph("<b>Phone Contact</b>", body_style), Paragraph(profile.phone or "Not provided", body_style)],
        [Paragraph("<b>Grade Level</b>", body_style), Paragraph(profile.get_grade_display() if hasattr(profile, 'get_grade_display') else str(profile.grade), body_style),
         Paragraph("<b>Province</b>", body_style), Paragraph(profile.province or "Not provided", body_style)],
        [Paragraph("<b>School Name</b>", body_style), Paragraph(profile.school_name or "Not provided", body_style),
         Paragraph("<b>National ID / Birth Cert</b>", body_style), Paragraph(profile.id_number or "Protected / Not provided", body_style)],
    ]
    t_identity = Table(identity_data, colWidths=[105, 155, 105, 155])
    t_identity.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_identity)
    elements.append(Spacer(1, 12))

    # 3. Academic Records & APS Calculation
    elements.append(Paragraph("2. Academic Record &amp; APS Calculation", section_heading))
    aps_summary_data = [
        [Paragraph("<b>Calculated Standard APS (Excl LO)</b>", body_bold),
         Paragraph(f"<font color='#008479'><b>{profile.calculated_aps} Points</b></font>", body_bold),
         Paragraph("<b>Target Career / Archetype</b>", body_bold),
         Paragraph(profile.target_career or "General Matriculant Discovery", body_style)]
    ]
    t_aps_sum = Table(aps_summary_data, colWidths=[150, 110, 120, 140])
    t_aps_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#e6f4f2')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#008479')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_aps_sum)
    elements.append(Spacer(1, 6))

    # Subject breakdown
    subjects = profile.subjects_json or []
    if subjects:
        subj_table_data = [[
            Paragraph("<b>Subject Name</b>", body_bold),
            Paragraph("<b>Percentage Mark</b>", body_bold),
            Paragraph("<b>DBE Scale Level</b>", body_bold),
            Paragraph("<b>Standard APS Contribution</b>", body_bold)
        ]]
        for s in subjects:
            mark = s.get('mark', 0)
            is_lo = s.get('is_lo', False) or 'life orientation' in s.get('name', '').lower()
            # Calculate DBE level 1-7
            if mark >= 80: level = 7
            elif mark >= 70: level = 6
            elif mark >= 60: level = 5
            elif mark >= 50: level = 4
            elif mark >= 40: level = 3
            elif mark >= 30: level = 2
            else: level = 1
            
            pts_text = "Excluded (LO)" if is_lo else f"{level} Pts"
            subj_table_data.append([
                Paragraph(s.get('name', 'Subject'), body_style),
                Paragraph(f"{mark}%", body_style),
                Paragraph(f"Level {level}", body_style),
                Paragraph(pts_text, body_style)
            ])
        t_subj = Table(subj_table_data, colWidths=[190, 100, 110, 120])
        t_subj.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_subj)
    else:
        elements.append(Paragraph("<i>No subject marks saved in profile at the time of export.</i>", body_style))
    elements.append(Spacer(1, 12))

    # 4. Bookmarked Bursaries
    elements.append(Paragraph("3. Bookmarked Bursary Opportunities", section_heading))
    if tracked_bursaries.exists():
        track_data = [[
            Paragraph("<b>Bursary Scheme</b>", body_bold),
            Paragraph("<b>Provider</b>", body_bold),
            Paragraph("<b>Category</b>", body_bold),
            Paragraph("<b>Tracking Status</b>", body_bold)
        ]]
        for t in tracked_bursaries:
            track_data.append([
                Paragraph(t.bursary.name, body_style),
                Paragraph(t.bursary.provider, body_style),
                Paragraph(t.bursary.category, body_style),
                Paragraph(t.get_status_display(), body_style)
            ])
        t_track = Table(track_data, colWidths=[180, 140, 100, 100])
        t_track.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_track)
    else:
        elements.append(Paragraph("<i>No bursaries currently bookmarked.</i>", body_style))
    elements.append(Spacer(1, 12))

    # 5. Submitted Applications
    elements.append(Paragraph("4. Submitted Applications Record", section_heading))
    if submitted_applications.exists():
        app_data = [[
            Paragraph("<b>Program Name</b>", body_bold),
            Paragraph("<b>Reference Number</b>", body_bold),
            Paragraph("<b>Submitted Date</b>", body_bold),
            Paragraph("<b>Status</b>", body_bold)
        ]]
        for a in submitted_applications:
            app_data.append([
                Paragraph(a.program_name, body_style),
                Paragraph(f"<font face='Courier'>{a.reference_number}</font>", body_style),
                Paragraph(a.submitted_at.strftime("%d %b %Y"), body_style),
                Paragraph(a.get_status_display(), body_style)
            ])
        t_app = Table(app_data, colWidths=[180, 130, 100, 110])
        t_app.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(t_app)
    else:
        elements.append(Paragraph("<i>No applications submitted through PfunzoBridge yet.</i>", body_style))
    elements.append(Spacer(1, 14))

    # 6. POPIA Compliance & Legal Statement
    elements.append(Paragraph("5. POPIA Data Governance Statement", section_heading))
    legal_text = (
        "<b>Lawful Processing:</b> This record represents the complete personal information processed by PfunzoBridge "
        "under Section 11 of the Protection of Personal Information Act (POPIA Act 4 of 2013) on the basis of your voluntary consent.<br/>"
        "<b>Right to Rectification (Section 24):</b> You may update any inaccurate marks or details at any time directly in your account.<br/>"
        "<b>Right to Erasure (Section 24):</b> You maintain the absolute right to have your account and all associated records permanently "
        "deleted via the 'Delete Account' control in your Profile or by contacting the Information Officer at "
        "<b>privacy@pfunzobridge.co.za</b>.<br/>"
        "<b>Security:</b> PfunzoBridge does not sell, trade, or distribute your personal details to third-party commercial marketers."
    )
    elements.append(Paragraph(legal_text, legal_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
