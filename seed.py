"""
seed.py – Populates the database with sample events for development.
Run once: python seed.py
"""
from app import create_app
from models import db, User, Event, StudentLogin, StudentRegistration, DocumentTrack
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import os

app = create_app()

SAMPLE_EVENTS = [
    {
        "title": "State-Level 36-Hour Hackathon",
        "description": "An intense inter-college hackathon hosted at BVM Engineering College. Open to all students in Gujarat. Form teams of 4-6 and solve real-world industry challenges.",
        "category": "Hackathon",
        "location": "BVM Auditorium, V.V. Nagar",
        "days_from_now": 18,
        "capacity": 200,
    },
    {
        "title": "ADIT Tech Symposium (Spectra)",
        "description": "A premier technical symposium hosted by ADIT. Features project showcases, paper presentations, and a CAD modeling contest. Students from all colleges are welcome to participate.",
        "category": "Tech Talk",
        "location": "ADIT Seminar Hall",
        "days_from_now": 21,
        "capacity": 150,
    },
    {
        "title": "Python & Flask Bootcamp",
        "description": "A full-day hands-on bootcamp covering Python fundamentals, Flask web development, and APIs. Hosted at ADIT but open to all programming enthusiasts in V.V. Nagar.",
        "category": "Workshop",
        "location": "Computer Lab 3, ADIT",
        "days_from_now": 5,
        "capacity": 50,
    },
    {
        "title": "BVM Innovation Pitch Deck",
        "description": "Got a startup idea? Present your pitch deck to investors at the BVM Incubation Center. Open to all student entrepreneurs from GCET, ADIT, BVM, and nearby colleges.",
        "category": "Seminar",
        "location": "BVM Incubation Center",
        "days_from_now": 10,
        "capacity": 80,
    },
    {
        "title": "IEEE IoT & Robotics Workshop",
        "description": "A hands-on workshop organized by the IEEE GCET chapter focusing on Internet of Things and basic robotics. Students from any college can register.",
        "category": "Workshop",
        "location": "Smt. Shardaben I. Patel AICTE Idea Lab, GCET",
        "days_from_now": 4,
        "capacity": 50,
    },
    {
        "title": "XITIJ - CVM University Youth Fest",
        "description": "The grand annual zonal youth festival featuring inter-college competitions in dance, music, theater, and fine arts. Come represent your college and show off your cultural talents!",
        "category": "Cultural",
        "location": "GCET Main Auditorium",
        "days_from_now": 14,
        "capacity": 500,
    },
    {
        "title": "Inter-College Cricket Tournament (Udaan)",
        "description": "The annual sports meet 'Udaan' kicks off with the highly anticipated inter-college cricket tournament. Register your team and compete for the CVM University cup.",
        "category": "Sports",
        "location": "Shastri Maidan, Vallabh Vidyanagar",
        "days_from_now": 7,
        "capacity": 300,
    },
    {
        "title": "CSI Inter-College GenAI Seminar",
        "description": "An expert seminar on Generative AI and Large Language Models, brought to you jointly by CSI chapters of ADIT and GCET. Learn how AI is shaping the future.",
        "category": "Seminar",
        "location": "ADIT Main Auditorium",
        "days_from_now": 3,
        "capacity": 250,
    },
    {
        "title": "Open Source Contribution Sprint",
        "description": "A beginner-friendly open source sprint. Learn how to use Git, GitHub, and make your first pull request. Hosted by the BVM coding club. All colleges invited.",
        "category": "Hackathon",
        "location": "Computer Center, BVM",
        "days_from_now": 12,
        "capacity": 60,
    },
    {
        "title": "Garba Night at CVM Grounds",
        "description": "Celebrate Navratri with the grand CVM University Garba Night. Open to all students of Vallabh Vidyanagar (GCET, ADIT, BVM, etc.). Put on your traditional attire!",
        "category": "Cultural",
        "location": "CVM University Grounds, V.V. Nagar",
        "days_from_now": 25,
        "capacity": 1000,
    },
    {
        "title": "Inter-College Volleyball Championship",
        "description": "Cheer for your college team in the inter-college volleyball championship. Matches will be held in the evening under floodlights.",
        "category": "Sports",
        "location": "ADIT Sports Complex",
        "days_from_now": 9,
        "capacity": 150,
    },
    {
        "title": "Tech Talk: Career in Cyber Security",
        "description": "A guest lecture by industry experts working in top cybersecurity firms. Learn about industry certifications, threat hunting, and securing networks.",
        "category": "Tech Talk",
        "location": "Conference Room 1, GCET",
        "days_from_now": 12,
        "capacity": 60,
    },
    {
        "title": "V.V. Nagar Inter-College Meetup",
        "description": "A social networking event for first-year students to interact with peers from GCET, ADIT, BVM, and MBIT. Enjoy fun icebreaker activities and games.",
        "category": "Social",
        "location": "Shastri Maidan Lawns",
        "days_from_now": 2,
        "capacity": 300,
    },
    {
        "title": "Vallabh Vidyanagar Heritage Walk",
        "description": "Explore the rich educational and cultural heritage of Vallabh Vidyanagar. A guided walk visiting historical landmarks and early institutions of CVM.",
        "category": "Social",
        "location": "Starting at BVM Circle",
        "days_from_now": 8,
        "capacity": 40,
    }
]


def seed():
    with app.app_context():
        # Drop & recreate to apply schema changes (safe for dev)
        db.drop_all()
        db.create_all()

        # ── 1. Create system / event organiser admin user ──
        organiser = User(
            username='eventloop_admin',
            email='admin@eventloop.dev',
            password_hash=generate_password_hash('Admin@1234')
        )
        db.session.add(organiser)
        db.session.flush()

        # ── 2. Seed Campus Events ──
        now = datetime.utcnow()
        for ev in SAMPLE_EVENTS:
            event = Event(
                title=ev['title'],
                description=ev['description'],
                category=ev['category'],
                location=ev['location'],
                date=now + timedelta(days=ev['days_from_now'], hours=10),
                capacity=ev['capacity'],
                created_by=organiser.id,
            )
            db.session.add(event)

        # ── 3. Seed Student Login Table (Requirement 1) ──
        student1 = StudentLogin(
            student_id='STU2026-0001',
            username='shreya_student',
            email='student@adit.edu',
            password_hash=generate_password_hash('Student@1234'),
            phone='9876543210',
            created_at=now - timedelta(days=5),
            last_login=now
        )
        student2 = StudentLogin(
            student_id='STU2026-0002',
            username='rohit_sharma',
            email='rohit@adit.edu',
            password_hash=generate_password_hash('Student@1234'),
            phone='9876543211',
            created_at=now - timedelta(days=3),
            last_login=now - timedelta(days=1)
        )
        db.session.add_all([student1, student2])
        db.session.flush()

        # ── 4. Seed Student Registration Table (Requirement 2) ──
        reg1 = StudentRegistration(
            student_login_id=student1.id,
            application_no='ADM2026-0101',
            full_name='Shreya Thacker',
            dob=date(2006, 5, 14),
            gender='Female',
            blood_group='B+',
            nationality='Indian',
            mother_tongue='Gujarati',
            category='General',
            phone_number='9876543210',
            alternate_phone='9876500000',
            email='student@adit.edu',
            permanent_address='12, Shanti Niketan Society, Near Nana Bazar, V.V. Nagar',
            city='Anand',
            state='Gujarat',
            pincode='388120',
            father_name='Rajesh Thacker',
            mother_name='Meena Thacker',
            guardian_phone='9825000000',
            guardian_occupation='Business Executive',
            family_income='₹ 5 Lakhs - ₹ 8 Lakhs',
            course_enrolled='B.Tech - Computer Engineering',
            department='Computer Engineering',
            academic_year='2026-2027',
            admission_category='Merit / ACPC',
            semester='1st Semester',
            tenth_board='GSEB',
            tenth_percentage=91.20,
            tenth_passing_year=2024,
            twelfth_board='GHSEB Science',
            twelfth_percentage=88.50,
            twelfth_passing_year=2026,
            entrance_exam_name='GUJCET',
            entrance_exam_roll='G2610892',
            entrance_exam_score=96.40,
            registration_status='Submitted',
            submission_date=now - timedelta(days=2),
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=2)
        )

        reg2 = StudentRegistration(
            student_login_id=student2.id,
            application_no='ADM2026-0102',
            full_name='Rohit Sharma',
            dob=date(2006, 8, 22),
            gender='Male',
            blood_group='O+',
            nationality='Indian',
            mother_tongue='Gujarati',
            category='General',
            phone_number='9876543211',
            email='rohit@adit.edu',
            permanent_address='45, Sardar Patel Colony, Station Road',
            city='Nadiad',
            state='Gujarat',
            pincode='387001',
            father_name='Kishore Sharma',
            mother_name='Geeta Sharma',
            guardian_phone='9825111111',
            guardian_occupation='Engineer',
            family_income='Above ₹ 8 Lakhs',
            course_enrolled='B.Tech - Information Technology',
            department='Information Technology',
            academic_year='2026-2027',
            admission_category='Merit / ACPC',
            semester='1st Semester',
            tenth_board='CBSE',
            tenth_percentage=89.00,
            tenth_passing_year=2024,
            twelfth_board='CBSE',
            twelfth_percentage=86.40,
            twelfth_passing_year=2026,
            entrance_exam_name='JEE Main',
            entrance_exam_roll='26031002',
            entrance_exam_score=94.10,
            registration_status='Draft',
            created_at=now - timedelta(days=3),
            updated_at=now - timedelta(days=1)
        )
        db.session.add_all([reg1, reg2])
        db.session.flush()

        # ── 5. Seed Document Track Table (Requirement 3) ──
        upload_dir = app.config.get('UPLOAD_FOLDER', os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'uploads', 'documents'))
        os.makedirs(upload_dir, exist_ok=True)

        sample_docs = [
            {
                'type': '10th Standard Marksheet',
                'filename': '10th_marksheet_shreya.pdf',
                'size': 245.5,
                'status': 'Verified',
                'remarks': 'ACPC Verified and Approved'
            },
            {
                'type': '12th Standard Marksheet',
                'filename': '12th_hsc_science_marksheet.pdf',
                'size': 312.0,
                'status': 'Verified',
                'remarks': 'Attested copy verified'
            },
            {
                'type': 'Entrance Exam Scorecard (GUJCET / JEE)',
                'filename': 'gujcet_2026_scorecard.pdf',
                'size': 188.4,
                'status': 'Verified',
                'remarks': 'Scorecard confirmed: 96.40 PR'
            },
            {
                'type': 'Aadhaar Card / Photo ID Proof',
                'filename': 'aadhaar_card_scan.pdf',
                'size': 420.2,
                'status': 'Uploaded',
                'remarks': 'Government Identity Verified'
            },
            {
                'type': 'Passport Size Photograph',
                'filename': 'passport_photo.png',
                'size': 95.8,
                'status': 'Verified',
                'remarks': 'Clear color passport photograph'
            }
        ]

        for s_doc in sample_docs:
            disk_filename = f"stu_{student1.id}_{s_doc['filename']}"
            disk_path = os.path.join(upload_dir, disk_filename)
            # Create a mock placeholder file if not already present
            if not os.path.exists(disk_path):
                with open(disk_path, 'wb') as f:
                    f.write(f"Sample Student Document: {s_doc['type']} for {reg1.full_name}".encode('utf-8'))

            doc_entry = DocumentTrack(
                student_login_id=student1.id,
                student_registration_id=reg1.id,
                document_type=s_doc['type'],
                original_filename=s_doc['filename'],
                file_name=disk_filename,
                file_path=f"uploads/documents/{disk_filename}",
                file_size_kb=s_doc['size'],
                mime_type='application/pdf' if disk_filename.endswith('.pdf') else 'image/png',
                upload_status=s_doc['status'],
                remarks=s_doc['remarks'],
                uploaded_at=now - timedelta(days=1)
            )
            db.session.add(doc_entry)

        db.session.commit()

        print(f"Seeded {len(SAMPLE_EVENTS)} events, 1 admin, 2 student logins, 2 student registrations, and {len(sample_docs)} document tracks.")
        print("Admin login    -> email: admin@eventloop.dev | password: Admin@1234")
        print("Student login  -> email: student@adit.edu    | password: Student@1234")


if __name__ == '__main__':
    seed()
