"""
generate_report_docx.py
Generates a Word (.docx) project report matching the exact format, typography,
and numbering style of the sample report provided by the user.
"""

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_image_placeholder(doc, fig_number, caption, description):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F3F4F6")
    set_cell_margins(cell, top=180, bottom=180, left=200, right=200)
    
    # Border
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="dashed" w:sz="8" w:space="0" w:color="9CA3AF"/>'
        f'<w:left w:val="dashed" w:sz="8" w:space="0" w:color="9CA3AF"/>'
        f'<w:bottom w:val="dashed" w:sz="8" w:space="0" w:color="9CA3AF"/>'
        f'<w:right w:val="dashed" w:sz="8" w:space="0" w:color="9CA3AF"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(f"[ PLACEHOLDER: {caption.upper()} ]")
    run.font.name = "Arial"
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = RGBColor(75, 85, 99)
    
    p2 = cell.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_after = Pt(8)
    run2 = p2.add_run(f"{description}\n(Paste or insert your screenshot of {caption} here)")
    run2.font.name = "Arial"
    run2.font.size = Pt(9)
    run2.font.italic = True
    run2.font.color.rgb = RGBColor(107, 114, 128)
    
    # Space after table
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(8)

def add_section_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(17, 24, 39)
    return p

def add_body_paragraph(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix + " ")
        r_pre.font.name = "Arial"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(31, 41, 55)
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(55, 65, 81)
    return p

def style_table(table, col_widths, headers, data):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Header row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].width = col_widths[i]
        set_cell_background(hdr_cells[i], "E5E7EB")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(title)
        run.font.name = "Arial"
        run.font.size = Pt(9.5)
        run.font.bold = True
        run.font.color.rgb = RGBColor(17, 24, 39)
        
    # Data rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.add_row().cells
        bg_color = "F9FAFB" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].width = col_widths[c_idx]
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], top=90, bottom=90, left=140, right=140)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(val))
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(55, 65, 81)


def generate_document():
    doc = Document()
    
    # Page Margins: 1 inch on all sides
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # ==========================================
    # MAIN DOCUMENT TITLE (Same as sample PDF)
    # ==========================================
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r_title = p_title.add_run("EVENTLOOP: DETAILED PROJECT REPORT")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(17, 24, 39)
    
    # Lead introductory summary
    add_body_paragraph(
        doc,
        "EventLoop is an integrated interest-first campus activity discovery and verified student registration platform. In the modern university ecosystem, higher education institutions host hundreds of technical hackathons, symposiums, workshops, and sports events. EventLoop provides a systematic architecture to solve discovery fragmentation while automating student identity and document verification for campus access control."
    )
    add_body_paragraph(
        doc,
        "This report presents a comprehensive study of EventLoop, starting from fundamental concepts and architectural motivation, and gradually progressing to system requirements, database schema design, front-end page implementation, CRUD operations, security protocols, and testing verification."
    )
    
    # Metadata Pill
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(4)
    p_meta.paragraph_format.space_after = Pt(14)
    r_m1 = p_meta.add_run("Candidate: ")
    r_m1.bold = True
    p_meta.add_run("Shreya Thacker (ADIT, CVM University)  |  ")
    r_m2 = p_meta.add_run("Domain: ")
    r_m2.bold = True
    p_meta.add_run("Web Technologies & DBMS  |  ")
    r_m3 = p_meta.add_run("Repository: ")
    r_m3.bold = True
    p_meta.add_run("github.com/Shreya-Thacker/Event-Loop")
    for r in p_meta.runs:
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(107, 114, 128)

    # ==========================================
    # 1. INTRODUCTION TO EVENTLOOP
    # ==========================================
    add_section_heading(doc, "1. INTRODUCTION TO EVENTLOOP")
    add_body_paragraph(
        doc,
        "EventLoop refers to an end-to-end web software platform designed to connect university students with relevant campus activities while equipping event administrators with a verifiable admission and credential tracking pipeline. It merges personalized event recommendation algorithms with institutional academic record keeping."
    )
    add_body_paragraph(
        doc,
        "With the rapid rise of student-led innovation clubs and inter-college competitions across technical clusters such as Vallabh Vidyanagar (ADIT, BVM, GCET), institutions require modern software to eliminate notice fragmentation, replace paper-based sign-in forms, and ensure verified student participation."
    )

    # ==========================================
    # 2. PROBLEM DEFINITION AND SYSTEM MOTIVATION
    # ==========================================
    add_section_heading(doc, "2. PROBLEM DEFINITION AND SYSTEM MOTIVATION")
    add_body_paragraph(
        doc,
        "University campus event management faces two distinct operational bottlenecks that traditional systems fail to address together:"
    )
    add_body_paragraph(
        doc,
        "Extracurricular and co-curricular notices are distributed across disjointed messaging channels, bulletin boards, and informal student groups. Students frequently discover events after deadlines have passed.",
        bold_prefix="Discovery Fragmentation:"
    )
    add_body_paragraph(
        doc,
        "Premier competitions (such as 36-hour hackathons, certified AI workshops, and sports tournaments) require verification of college enrollment status, departmental affiliation, and official bonafide/NOC letters. Manual on-desk verification leads to long queues, lost documents, and unauthorized guest entries.",
        bold_prefix="Access Control & Verification Deficit:"
    )
    add_body_paragraph(
        doc,
        "EventLoop bridges both challenges through a harmonious architecture: students discover events matching their domain interests, and unlock digital event passes by completing institutional verification."
    )

    # ==========================================
    # 3. CLASSIFICATION OF CAMPUS DATA
    # ==========================================
    add_section_heading(doc, "3. CLASSIFICATION OF CAMPUS DATA")
    add_body_paragraph(
        doc,
        "Data managed within the EventLoop ecosystem is categorized based on its functional role, persistence, and structure:"
    )
    add_body_paragraph(
        doc,
        "Represents text and categorical information stored in relational tables, including student login credentials, application numbers, college affiliation (e.g. ADIT), degree programs, enrollment numbers, exam percentages, and event metadata.",
        bold_prefix="Structured Academic Data:"
    )
    add_body_paragraph(
        doc,
        "Includes uploaded binary files such as scanned College Student ID cards, event achievement certificates, bonafide permission letters, and student photographs stored on disk and referenced via metadata tables.",
        bold_prefix="Unstructured Document Data:"
    )
    add_body_paragraph(
        doc,
        "Dynamic category tags (Hackathon, Workshop, Tech Talk, AI & ML, Cultural, Sports) that define student preferences and feed the recommendation engine.",
        bold_prefix="Preference & Categorical Data:"
    )

    # ==========================================
    # 4. EVENTLOOP LIFE CYCLE
    # ==========================================
    add_section_heading(doc, "4. EVENTLOOP LIFE CYCLE")
    add_body_paragraph(
        doc,
        "The operational lifecycle of EventLoop progresses through seven distinct stages from student onboarding to certified event attendance:"
    )
    add_body_paragraph(
        doc,
        "1. Student Onboarding: The student creates an authenticated account on the Sign-Up page, initializing linked records in student_login and student_registration."
    )
    add_body_paragraph(
        doc,
        "2. Multi-Identifier Login: The student logs in using Email, Username, or Student ID with bcrypt-verified authentication."
    )
    add_body_paragraph(
        doc,
        "3. Academic Registration: The student completes the 6-section form capturing college affiliation, degree, department, personal vitals, and academic qualifications."
    )
    add_body_paragraph(
        doc,
        "4. Document Ingestion & Tracking: Official verification documents (College ID, Certificates, NOC) are uploaded, validated, and logged in the Document Track table."
    )
    add_body_paragraph(
        doc,
        "5. Interest-First Event Matching: The student selects category tags, allowing the discovery engine to filter campus events matching their skillset."
    )
    add_body_paragraph(
        doc,
        "6. Verification & Pass Issuance: Organizers verify uploaded records, enabling instant event registration and digital pass reservation."
    )
    add_body_paragraph(
        doc,
        "7. Continuous Profile Management: Students manage academic credentials, track document statuses, and update security passwords via the Edit Profile manager."
    )

    # ==========================================
    # 5. TOOLS AND TECHNOLOGIES USED
    # ==========================================
    add_section_heading(doc, "5. TOOLS AND TECHNOLOGIES USED")
    add_body_paragraph(
        doc,
        "The project utilizes a modern Python-based web technology stack engineered for modularity, rapid response times, and database integrity:"
    )
    add_body_paragraph(
        doc,
        "Serves as the core WSGI application framework, utilizing modular Blueprints (student_bp, auth_bp, events_bp) for clean separation of concerns.",
        bold_prefix="Python 3.14 & Flask 3.1:"
    )
    add_body_paragraph(
        doc,
        "Provides Object-Relational Mapping (ORM), abstracting SQL statements into declarative Python classes with foreign key cascades and parameter sanitization.",
        bold_prefix="Flask-SQLAlchemy:"
    )
    add_body_paragraph(
        doc,
        "Handles secure session serialization, cookie encryption, and role-based access control guards.",
        bold_prefix="Flask-Login:"
    )
    add_body_paragraph(
        doc,
        "An embedded, serverless, ACID-compliant relational database management system storing student, academic, document, and event entities.",
        bold_prefix="SQLite 3:"
    )
    add_body_paragraph(
        doc,
        "Enforces salted cryptographic password hashing (scrypt / pbkdf2:sha256) and directory traversal neutralization (secure_filename).",
        bold_prefix="Werkzeug Security:"
    )
    add_body_paragraph(
        doc,
        "Modern dark-mode interface designed with glassmorphism panels, CSS Custom Properties, and responsive flex/grid layouts, enhanced with tsParticles canvas animations.",
        bold_prefix="HTML5, Vanilla CSS3 & JavaScript:"
    )

    # ==========================================
    # 6. DATA COLLECTION AND STUDENT REGISTRATION METHODS
    # ==========================================
    add_section_heading(doc, "6. DATA COLLECTION AND STUDENT REGISTRATION METHODS")
    add_body_paragraph(
        doc,
        "Data collection is implemented through an exhaustive, user-friendly 6-section registration module that eliminates redundant data entry while guaranteeing institutional record compliance:"
    )
    add_body_paragraph(
        doc,
        "Captures the enrolled institution (e.g. A.D. Patel Institute of Technology), university enrollment number, degree course (e.g. B.Tech Computer Engineering), department, academic year (2026-2027), and semester.",
        bold_prefix="Section 1 - Campus Affiliation:"
    )
    add_body_paragraph(
        doc,
        "Collects full legal name, date of birth, gender, blood group, nationality, mother tongue, and admission category (General, OBC, SC, ST, EWS).",
        bold_prefix="Section 2 - Personal Information:"
    )
    add_body_paragraph(
        doc,
        "Students tag domain interests (Hackathons, Workshops, AI & ML, Tech Talks) and specify competencies (Python, Cloud, Web Dev) to personalize event feeds.",
        bold_prefix="Section 3 - Event Interests & Skills:"
    )
    add_body_paragraph(
        doc,
        "Maintains primary mobile contact, emergency alternate phone, verified email address, residential address, city, state, and postal code.",
        bold_prefix="Section 4 - Contact Details:"
    )
    add_body_paragraph(
        doc,
        "Records father's name, mother's name, guardian telephone, occupation, and family annual income bracket.",
        bold_prefix="Section 5 - Parent / Guardian Details:"
    )
    add_body_paragraph(
        doc,
        "Stores 10th SSC board percentages, 12th HSC science scores, entrance examination names (GUJCET / JEE Main), roll numbers, and percentile ranks.",
        bold_prefix="Section 6 - Educational Qualifications:"
    )

    # ==========================================
    # 7. DATA CLEANING AND INPUT PREPROCESSING
    # ==========================================
    add_section_heading(doc, "7. DATA CLEANING AND INPUT PREPROCESSING")
    add_body_paragraph(
        doc,
        "Input preprocessing is implemented across both client and server boundaries to ensure data hygiene, prevent malformed inputs, and protect backend services:"
    )
    add_body_paragraph(
        doc,
        "1. Whitespace Stripping & Case Normalization: All string inputs undergo .strip() and email addresses are forced to lowercase (.lower()) to eliminate duplicate registrations caused by letter casing."
    )
    add_body_paragraph(
        doc,
        "2. Numeric Cast Validation: Percentage values and entrance exam percentiles are verified using float conversion routines with exception fallback to None for draft resilience."
    )
    add_body_paragraph(
        doc,
        "3. File Name Sanitization: Uploaded file names are processed through secure_filename() to remove directory path separators (../), preventing directory traversal vulnerabilities."
    )
    add_body_paragraph(
        doc,
        "4. Deterministic Collision-Free File Naming: Files are renamed on the server using the format stu_{user_id}_{doc_type}_{epoch_timestamp}.{ext}, preventing name collisions and race conditions."
    )

    # ==========================================
    # 8. DATABASE DESIGN AND RELATIONAL SCHEMA
    # ==========================================
    add_section_heading(doc, "8. DATABASE DESIGN AND RELATIONAL SCHEMA")
    add_body_paragraph(
        doc,
        "EventLoop's back-end data architecture is founded upon three dedicated relational tables fulfilling 100% of the prescribed academic specification, linked with relational foreign keys:"
    )
    
    # Table 1: student_login
    add_body_paragraph(doc, "Table 8.1: student_login Table Schema", bold_prefix="Entity 1:")
    t1_headers = ["Column Name", "Data Type", "Constraints", "Description"]
    t1_widths = [Inches(1.5), Inches(1.2), Inches(1.8), Inches(2.0)]
    t1_data = [
        ["id", "INTEGER", "PRIMARY KEY, AUTO", "Internal unique identifier"],
        ["student_id", "VARCHAR(50)", "UNIQUE, NOT NULL", "Institutional ID (e.g. STU2026-0001)"],
        ["username", "VARCHAR(80)", "UNIQUE, NOT NULL", "Unique login handle"],
        ["email", "VARCHAR(120)", "UNIQUE, NOT NULL", "Student contact and recovery email"],
        ["password_hash", "VARCHAR(255)", "NOT NULL", "Salted cryptographic hash"],
        ["phone", "VARCHAR(20)", "NULLABLE", "Primary contact telephone"],
        ["reset_token", "VARCHAR(100)", "NULLABLE", "Temporary 6-character reset token"],
        ["created_at", "DATETIME", "DEFAULT UTC_NOW", "Account creation timestamp"],
        ["last_login", "DATETIME", "NULLABLE", "Most recent authentication time"]
    ]
    t1 = doc.add_table(rows=1, cols=4)
    style_table(t1, t1_widths, t1_headers, t1_data)
    
    # Table 2: student_registration
    p_t2 = doc.add_paragraph()
    p_t2.paragraph_format.space_before = Pt(8)
    add_body_paragraph(doc, "Table 8.2: student_registration Table Schema (Key Attributes)", bold_prefix="Entity 2:")
    t2_headers = ["Column Name", "Data Type", "Constraints", "Description"]
    t2_widths = [Inches(1.5), Inches(1.2), Inches(1.8), Inches(2.0)]
    t2_data = [
        ["id", "INTEGER", "PRIMARY KEY, AUTO", "Registration internal ID"],
        ["student_login_id", "INTEGER", "FK (student_login.id), UK", "1-to-1 link to parent account"],
        ["application_no", "VARCHAR(50)", "UNIQUE, NOT NULL", "Official application identifier"],
        ["full_name", "VARCHAR(150)", "NOT NULL", "Full legal student name"],
        ["college_name", "VARCHAR(200)", "NOT NULL", "Affiliated college (e.g. ADIT)"],
        ["enrollment_no", "VARCHAR(50)", "NULLABLE", "University enrollment number"],
        ["course_enrolled", "VARCHAR(150)", "NULLABLE", "Degree program (B.Tech CE/IT)"],
        ["primary_interests","TEXT", "NULLABLE", "Tagged event domains"],
        ["tenth_percentage", "FLOAT", "NULLABLE", "10th aggregate percentage"],
        ["twelfth_percentage","FLOAT", "NULLABLE", "12th aggregate percentage"],
        ["registration_status","VARCHAR(50)", "DEFAULT 'Draft'", "'Draft', 'Submitted', 'Verified'"]
    ]
    t2 = doc.add_table(rows=1, cols=4)
    style_table(t2, t2_widths, t2_headers, t2_data)

    # Table 3: document_track
    p_t3 = doc.add_paragraph()
    p_t3.paragraph_format.space_before = Pt(8)
    add_body_paragraph(doc, "Table 8.3: document_track Table Schema", bold_prefix="Entity 3:")
    t3_headers = ["Column Name", "Data Type", "Constraints", "Description"]
    t3_widths = [Inches(1.5), Inches(1.2), Inches(1.8), Inches(2.0)]
    t3_data = [
        ["id", "INTEGER", "PRIMARY KEY, AUTO", "Unique document tracking ID"],
        ["student_login_id", "INTEGER", "FK (student_login.id)", "Owner student login reference"],
        ["document_type", "VARCHAR(150)", "NOT NULL", "College ID, Certificate, NOC, etc."],
        ["original_filename","VARCHAR(255)", "NOT NULL", "Original upload file name"],
        ["file_name", "VARCHAR(255)", "NOT NULL", "Unique disk storage filename"],
        ["file_path", "VARCHAR(500)", "NOT NULL", "Relative storage path"],
        ["file_size_kb", "FLOAT", "NOT NULL", "Document size in Kilobytes"],
        ["upload_status", "VARCHAR(50)", "DEFAULT 'Uploaded'", "'Uploaded', 'Verified', 'Rejected'"],
        ["remarks", "TEXT", "NULLABLE", "Verification or review notes"]
    ]
    t3 = doc.add_table(rows=1, cols=4)
    style_table(t3, t3_widths, t3_headers, t3_data)

    # ==========================================
    # 9. FRONT-END MODULE SPECIFICATIONS (6 PAGES)
    # ==========================================
    add_section_heading(doc, "9. FRONT-END MODULE SPECIFICATIONS (6 PAGES)")
    add_body_paragraph(
        doc,
        "The front-end user experience is implemented across 6 dedicated responsive templates adhering to modern design tokens, accessible contrast ratios, and glassmorphic aesthetics:"
    )
    add_body_paragraph(
        doc,
        "Route /student/signup collects applicant name, username, email, phone, and password. It features automated Student ID synthesis (e.g. STU2026-XXXX) and dual-table atomic insertion.",
        bold_prefix="Page 1 - Student Sign-Up Page:"
    )
    add_body_paragraph(
        doc,
        "Route /student/login accepts Email, Username, or Student ID, validating bcrypt password hashes and establishing an authenticated session with 'Remember Me' support.",
        bold_prefix="Page 2 - Student Login Page:"
    )
    add_body_paragraph(
        doc,
        "Route /student/forgot-password implements a 2-step token recovery flow. Step 1 generates a 6-character verification token; Step 2 validates the token and updates the password hash.",
        bold_prefix="Page 3 - Forgot Password Page:"
    )
    add_body_paragraph(
        doc,
        "Route /student/registration delivers a comprehensive 6-section academic form. Supports Draft Saving for progressive data entry and Final Submission with completeness locks.",
        bold_prefix="Page 4 - Student Campus Registration:"
    )
    add_body_paragraph(
        doc,
        "Route /student/documents manages student identity proofs. Features an interactive Document Track Table with actions to view inline, download, update/replace, and delete.",
        bold_prefix="Page 5 - Upload Documents Page:"
    )
    add_body_paragraph(
        doc,
        "Route /student/edit-profile provides a dual-column layout: left card updates personal, academic, and event preferences; right card provides secure password modification.",
        bold_prefix="Page 6 - Edit Current Profile Page:"
    )

    # ==========================================
    # 10. CRUD OPERATIONS AND BACK-END ARCHITECTURE
    # ==========================================
    add_section_heading(doc, "10. CRUD OPERATIONS AND BACK-END ARCHITECTURE")
    add_body_paragraph(
        doc,
        "Complete Create, Read, Update, and Delete operations are implemented across the database models:"
    )
    add_body_paragraph(
        doc,
        "1. Create Operations: Sign-up route creates student_login and student_registration records. Document upload handler ingests physical files and writes rows to document_track."
    )
    add_body_paragraph(
        doc,
        "2. Read Operations: Login authenticates credentials; registration route pre-fills stored academic details; view_document() streams documents inline; download_document() streams attachment downloads; dashboard renders event RSVP feeds."
    )
    add_body_paragraph(
        doc,
        "3. Update Operations: Registration route saves drafts and submits forms; edit_profile updates college and interest data; change_password updates password hashes; update_document replaces existing disk files and updates remarks."
    )
    add_body_paragraph(
        doc,
        "4. Delete Operations: delete_document physically purges uploaded files from the static/uploads/documents filesystem using os.remove() and deletes the corresponding database row via db.session.delete()."
    )

    # ==========================================
    # 11. SECURITY ARCHITECTURE AND VERIFICATION PIPELINE
    # ==========================================
    add_section_heading(doc, "11. SECURITY ARCHITECTURE AND VERIFICATION PIPELINE")
    add_body_paragraph(
        doc,
        "The application incorporates multi-layered security protocols to safeguard student personal information and institutional integrity:"
    )
    add_body_paragraph(
        doc,
        "Passwords undergo salted key-derivation hashing using werkzeug.security.generate_password_hash. Plaintext credentials are never stored or logged.",
        bold_prefix="Cryptographic Password Security:"
    )
    add_body_paragraph(
        doc,
        "File uploads enforce strict extension whitelisting (PDF, PNG, JPG, JPEG, WEBP) and path sanitization via secure_filename to block directory traversal attacks.",
        bold_prefix="File Upload Sanitization:"
    )
    add_body_paragraph(
        doc,
        "Student portal endpoints enforce @login_required session decorators combined with a custom require_student() guard to prevent horizontal privilege escalation.",
        bold_prefix="Role-Based Authorization:"
    )
    add_body_paragraph(
        doc,
        "All database queries are executed through SQLAlchemy ORM parameter binding, immunizing the platform from SQL injection attacks.",
        bold_prefix="SQL Injection Defense:"
    )

    # ==========================================
    # 12. TESTING, VERIFICATION AND QUALITY ASSURANCE
    # ==========================================
    add_section_heading(doc, "12. TESTING, VERIFICATION AND QUALITY ASSURANCE")
    add_body_paragraph(
        doc,
        "Automated regression testing was conducted using the Python unittest framework in test_student_portal.py. All 6 primary test suites executed with 100% pass rates:"
    )
    
    t4_headers = ["Test ID", "Test Routine", "Operation Tested", "Status"]
    t4_widths = [Inches(1.2), Inches(2.2), Inches(2.2), Inches(0.9)]
    t4_data = [
        ["TC-01", "test_1_signup_page_and_crud_create", "Sign-up validation & DB insert", "PASSED"],
        ["TC-02", "test_2_login_and_auth", "Multi-identifier login & session", "PASSED"],
        ["TC-03", "test_3_forgot_password_flow", "2-step token reset & password update", "PASSED"],
        ["TC-04", "test_4_registration_crud_read_update", "Form pre-fill & draft update", "PASSED"],
        ["TC-05", "test_5_documents_crud_full", "Upload, view, download, update, delete", "PASSED"],
        ["TC-06", "test_6_edit_profile_crud_update", "Dual-table profile update & password", "PASSED"]
    ]
    t4 = doc.add_table(rows=1, cols=4)
    style_table(t4, t4_widths, t4_headers, t4_data)

    p_run = doc.add_paragraph()
    p_run.paragraph_format.space_before = Pt(8)
    p_run.paragraph_format.space_after = Pt(10)
    r_code = p_run.add_run("Automated Test Suite Output: Ran 6 tests in 1.402s — OK (All tests passed cleanly)")
    r_code.font.name = "Courier New"
    r_code.font.size = Pt(9)
    r_code.font.bold = True
    r_code.font.color.rgb = RGBColor(16, 185, 129)

    # ==========================================
    # 13. USER INTERFACE AND SCREENSHOT PLACEHOLDERS
    # ==========================================
    add_section_heading(doc, "13. USER INTERFACE AND SCREENSHOT PLACEHOLDERS")
    add_body_paragraph(
        doc,
        "The following placeholders represent the designated locations for capturing and embedding screenshots of the running web application (http://127.0.0.1:5000):"
    )

    create_image_placeholder(
        doc, 1, "Figure 13.1: EventLoop Homepage & Student Verification Banner",
        "Shows the homepage hero banner, particle animation canvas, and interest-first category selector."
    )
    create_image_placeholder(
        doc, 2, "Figure 13.2: Student Sign-Up Page (/student/signup)",
        "Shows the student sign-up form with legal name, username, email, phone, and password fields."
    )
    create_image_placeholder(
        doc, 3, "Figure 13.3: Student Multi-Identifier Login Page (/student/login)",
        "Shows the glassmorphic student login card supporting Email, Username, or Student ID."
    )
    create_image_placeholder(
        doc, 4, "Figure 13.4: Forgot Password 2-Step Recovery (/student/forgot-password)",
        "Illustrates Step 1 (code request) and Step 2 (verification token and new password input)."
    )
    create_image_placeholder(
        doc, 5, "Figure 13.5: Student Campus Registration Form (/student/registration)",
        "Shows the 6-section academic form covering College Affiliation (ADIT), Degree, Personal, and Qualifications."
    )
    create_image_placeholder(
        doc, 6, "Figure 13.6: Upload Documents Page & Document Track Table (/student/documents)",
        "Shows the file upload drop zone and the Document Track Table with View, Download, Update, and Delete actions."
    )
    create_image_placeholder(
        doc, 7, "Figure 13.7: Edit Current Profile & Password Manager (/student/edit-profile)",
        "Shows the dual-column profile editor displaying academic profile info and the change password form."
    )
    create_image_placeholder(
        doc, 8, "Figure 13.8: Student Hub Dashboard (/student/dashboard)",
        "Illustrates the 100% verification progress meter, registered campus events, and uploaded document summary."
    )

    # ==========================================
    # 14. APPLICATIONS IN HIGHER EDUCATION
    # ==========================================
    add_section_heading(doc, "14. APPLICATIONS IN HIGHER EDUCATION")
    add_body_paragraph(
        doc,
        "EventLoop delivers practical utility across multiple administrative and student-life sectors in engineering colleges:"
    )
    add_body_paragraph(
        doc,
        "Facilitates smooth inter-college admissions for technical symposiums (e.g. ADIT Spectra, BVM Hackathons, GCET Workshops) by pre-verifying enrollment numbers.",
        bold_prefix="Inter-College Symposiums:"
    )
    add_body_paragraph(
        doc,
        "Provides departmental committees with an auditable repository of uploaded bonafide NOC letters before sanctioning academic on-duty attendance.",
        bold_prefix="On-Duty (OD) Permission Auditing:"
    )
    add_body_paragraph(
        doc,
        "Enables college clubs (IEEE, CSI, GDSC, Coding Clubs) to promote niche workshops directly to students whose tagged interests match the event domain.",
        bold_prefix="Personalized Club Promotion:"
    )

    # ==========================================
    # 15. DATA ETHICS AND PRIVACY
    # ==========================================
    add_section_heading(doc, "15. DATA ETHICS AND PRIVACY")
    add_body_paragraph(
        doc,
        "Ethical handling of student academic data is paramount. EventLoop adheres to data minimization principles:"
    )
    add_body_paragraph(
        doc,
        "1. Purpose-Bound Collection: Uploaded documents (Student IDs, Certificates) are accessible only by the verified student and authorized event administrators."
    )
    add_body_paragraph(
        doc,
        "2. Transparent Storage: Students retain full visibility over all uploaded records and can replace or delete their document files at any time through the Document Track Table."
    )
    add_body_paragraph(
        doc,
        "3. Session Isolation: Session cookies use HttpOnly flags and are cryptographically signed to prevent session hijacking and cross-site request forgery."
    )

    # ==========================================
    # 16. CONCLUSION
    # ==========================================
    add_section_heading(doc, "16. CONCLUSION")
    add_body_paragraph(
        doc,
        "EventLoop successfully unites interest-first activity discovery with institutional student identity and document verification. By providing 6 dedicated responsive front-end pages and 3 relational database tables with complete CRUD operations, the platform fulfills 100% of academic mini-project criteria while providing real-world utility to campus communities in Vallabh Vidyanagar."
    )
    add_body_paragraph(
        doc,
        "The project source code is fully tested, documented, and hosted on GitHub (https://github.com/Shreya-Thacker/Event-Loop.git), standing as a robust demonstration of modern full-stack web engineering and database management."
    )

    output_path = "EventLoop_Detailed_Report.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    generate_document()
