"""
seed.py – Populates the database with sample events for development.
Run once: python seed.py
"""
from app import create_app
from models import db, User, Event
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

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

        # Create a system/organiser user
        organiser = User(
            username='eventloop_admin',
            email='admin@eventloop.dev',
            password_hash=generate_password_hash('Admin@1234')
        )
        db.session.add(organiser)
        db.session.flush()  # get organiser.id before commit

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

        db.session.commit()
        print(f"Seeded {len(SAMPLE_EVENTS)} events and 1 admin user.")
        print("Admin login -> email: admin@eventloop.dev | password: Admin@1234")


if __name__ == '__main__':
    seed()
