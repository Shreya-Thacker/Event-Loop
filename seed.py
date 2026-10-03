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
        "title": "IEEE IoT & Robotics Workshop",
        "description": "A hands-on workshop organized by the IEEE GCET chapter focusing on Internet of Things and basic robotics. Ideal for tech enthusiasts looking to build smart devices.",
        "category": "Workshop",
        "location": "Smt. Shardaben I. Patel AICTE Idea Lab, GCET",
        "days_from_now": 4,
        "capacity": 50,
    },
    {
        "title": "XITIJ - CVM University Youth Fest",
        "description": "The annual zonal youth festival featuring inter-college competitions in dance, music, theater, and fine arts. Come represent GCET and show off your cultural talents!",
        "category": "Cultural",
        "location": "GCET Main Auditorium",
        "days_from_now": 14,
        "capacity": 500,
    },
    {
        "title": "AUTONOVA Technical Symposium",
        "description": "A premier technical symposium hosted by the Mechanical and Mechatronics departments. Features project showcases, paper presentations, and a CAD modeling contest.",
        "category": "Tech Talk",
        "location": "GCET Seminar Hall B",
        "days_from_now": 21,
        "capacity": 150,
    },
    {
        "title": "IEDC Startup Pitch Deck Competition",
        "description": "Got an innovative startup idea? Present your pitch deck to a panel of industry experts and investors. Organized by the GCET Incubation & Entrepreneurship Development Cell.",
        "category": "Hackathon",
        "location": "Innovation Hub, GCET",
        "days_from_now": 10,
        "capacity": 80,
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
        "title": "CSI Student Branch: GenAI Seminar",
        "description": "An expert seminar on Generative AI and Large Language Models, brought to you by the Computer Society of India (CSI) GCET Chapter. Learn how AI is shaping the future.",
        "category": "Seminar",
        "location": "Computer Lab 1, GCET",
        "days_from_now": 3,
        "capacity": 100,
    },
    {
        "title": "Prarambh Club Social Mixer",
        "description": "A social networking event for first-year students to interact with seniors, learn about various college clubs, and enjoy fun icebreaker activities and games.",
        "category": "Social",
        "location": "GCET College Lawns",
        "days_from_now": 2,
        "capacity": 200,
    },
    {
        "title": "SSIP Hackathon 36-Hours",
        "description": "A rigorous 36-hour hackathon funded by the Student Start-up and Innovation Policy (SSIP). Solve real-world challenges posed by local industries in Gujarat.",
        "category": "Hackathon",
        "location": "AICTE Idea Lab, GCET",
        "days_from_now": 18,
        "capacity": 100,
    },
    {
        "title": "Garba Night at CVM Grounds",
        "description": "Celebrate Navratri with the grand CVM University Garba Night. Open to all students of Vallabh Vidyanagar. Put on your traditional attire and join the festivities!",
        "category": "Cultural",
        "location": "CVM University Grounds, V.V. Nagar",
        "days_from_now": 25,
        "capacity": 1000,
    },
    {
        "title": "Python & Flask Bootcamp",
        "description": "A full-day hands-on bootcamp covering Python fundamentals, Flask web development, REST APIs, and SQLite databases. Ideal for beginners and intermediate developers.",
        "category": "Workshop",
        "location": "Computer Lab 3, GCET",
        "days_from_now": 5,
        "capacity": 40,
    },
    {
        "title": "Volleyball Intra-College Championship",
        "description": "Cheer for your department branch in the intra-college volleyball championship. Matches will be held in the evening under floodlights.",
        "category": "Sports",
        "location": "GCET Volleyball Court",
        "days_from_now": 9,
        "capacity": 150,
    },
    {
        "title": "Alumni Tech Talk: Career in Cyber Security",
        "description": "A guest lecture by GCET alumni working in top cybersecurity firms. Learn about industry certifications, threat hunting, and securing networks.",
        "category": "Tech Talk",
        "location": "Conference Room 1",
        "days_from_now": 12,
        "capacity": 60,
    },
    {
        "title": "NPTEL Awareness & Study Group",
        "description": "An awareness session on NPTEL certification courses, followed by forming study groups for the upcoming semester's technical courses.",
        "category": "Seminar",
        "location": "Room 204, GCET Main Building",
        "days_from_now": 6,
        "capacity": 70,
    },
    {
        "title": "Vallabh Vidyanagar Heritage Walk",
        "description": "Explore the rich educational and cultural heritage of Vallabh Vidyanagar. A guided walk visiting historical landmarks and early institutions of CVM.",
        "category": "Social",
        "location": "Starting at GCET Main Gate",
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
