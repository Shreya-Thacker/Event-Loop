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
        "title": "Python & Flask Bootcamp",
        "description": "A full-day hands-on bootcamp covering Python fundamentals, Flask web development, REST APIs, and SQLite databases. Ideal for beginners and intermediate developers looking to build real-world web apps.",
        "category": "Workshop",
        "location": "Computer Lab 3, Block A",
        "days_from_now": 5,
        "capacity": 40,
    },
    {
        "title": "Smart India Hackathon – Campus Round",
        "description": "24-hour hackathon to build innovative solutions for real government problem statements. Form teams of 4–6, register your idea, and compete for the top spot to go to the national round.",
        "category": "Hackathon",
        "location": "Innovation Hub, Main Campus",
        "days_from_now": 12,
        "capacity": 120,
    },
    {
        "title": "Inter-College Basketball Tournament",
        "description": "Annual basketball tournament with teams from 10+ colleges competing. Come support your college team or sign up to play in the 3x3 open category.",
        "category": "Sports",
        "location": "Sports Complex, Ground Floor",
        "days_from_now": 8,
        "capacity": 200,
    },
    {
        "title": "Classical Music & Dance Night",
        "description": "An enchanting evening of classical Indian music and Bharatanatyam performances by students and invited artists. Open to all. Light refreshments provided.",
        "category": "Cultural",
        "location": "Main Auditorium",
        "days_from_now": 15,
        "capacity": 300,
    },
    {
        "title": "AI & Machine Learning Seminar",
        "description": "Expert talk on the latest advancements in generative AI, large language models, and their real-world applications. Includes a Q&A session and networking break.",
        "category": "Seminar",
        "location": "Seminar Hall B, Block C",
        "days_from_now": 3,
        "capacity": 80,
    },
    {
        "title": "Web3 & Blockchain Talk",
        "description": "Deep-dive tech talk on decentralised apps, smart contracts, and the practical uses of blockchain beyond cryptocurrency. Demos included.",
        "category": "Tech Talk",
        "location": "Conference Room 1",
        "days_from_now": 20,
        "capacity": 60,
    },
    {
        "title": "Freshman Welcome Social",
        "description": "Icebreaker games, free food, and a chance to meet your batchmates and seniors in a relaxed environment. All first-year students are warmly invited!",
        "category": "Social",
        "location": "College Lawns",
        "days_from_now": 2,
        "capacity": 150,
    },
    {
        "title": "UI/UX Design Workshop",
        "description": "Learn Figma from scratch, design principles, user research techniques, and how to build stunning prototypes. Participants get a certificate of completion.",
        "category": "Workshop",
        "location": "Media Lab, Block D",
        "days_from_now": 10,
        "capacity": 35,
    },
    {
        "title": "Code Sprint – 6-Hour Challenge",
        "description": "A focused 6-hour competitive programming contest. Solve algorithmic problems across data structures, graphs, and dynamic programming. Solo participation only.",
        "category": "Hackathon",
        "location": "Computer Lab 1 & 2, Block A",
        "days_from_now": 18,
        "capacity": 50,
    },
    {
        "title": "Photography Walk & Exhibition",
        "description": "A guided campus photography walk followed by a same-day exhibition of the best shots. All skill levels welcome. Bring your phone or DSLR.",
        "category": "Cultural",
        "location": "Starting at Main Gate",
        "days_from_now": 7,
        "capacity": 45,
    },
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
