from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Represents a registered student user."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    registrations = db.relationship('Registration', backref='user', lazy=True)
    saved_events = db.relationship('SavedEvent', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Event(db.Model):
    """Represents a campus/community event."""
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)       # e.g. Workshop, Hackathon, Sports
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=50)
    image_url = db.Column(db.String(300), nullable=True)      # Optional banner image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    organizer = db.relationship('User', foreign_keys=[created_by], backref='organized_events')
    registrations = db.relationship('Registration', backref='event', lazy=True)
    saved_by = db.relationship('SavedEvent', backref='event', lazy=True)

    @property
    def spots_left(self):
        return self.capacity - len(self.registrations)

    @property
    def is_full(self):
        return self.spots_left <= 0

    def __repr__(self):
        return f'<Event {self.title}>'


class Registration(db.Model):
    """Tracks which user registered for which event (CRUD: participate history)."""
    __tablename__ = 'registrations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Registration user={self.user_id} event={self.event_id}>'


class SavedEvent(db.Model):
    """Tracks events bookmarked/saved by a user."""
    __tablename__ = 'saved_events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedEvent user={self.user_id} event={self.event_id}>'
