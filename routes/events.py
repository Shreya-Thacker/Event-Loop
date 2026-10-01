from flask import Blueprint, render_template, request, abort
from models import Event
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/events')

CATEGORIES = ['Workshop', 'Hackathon', 'Sports', 'Cultural', 'Seminar', 'Social', 'Tech Talk']


# ── Event List ────────────────────────────────────────────────────────────────
@events_bp.route('/')
def list_events():
    category = request.args.get('category', '').strip()
    search   = request.args.get('search', '').strip()

    query = Event.query.filter(Event.date >= datetime.utcnow())

    if category and category in CATEGORIES:
        query = query.filter_by(category=category)

    if search:
        like = f'%{search}%'
        query = query.filter(
            Event.title.ilike(like) | Event.location.ilike(like) | Event.description.ilike(like)
        )

    events = query.order_by(Event.date.asc()).all()

    return render_template('events/list.html',
                           events=events,
                           categories=CATEGORIES,
                           active_category=category,
                           search=search)


# ── Event Detail ──────────────────────────────────────────────────────────────
@events_bp.route('/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    related = Event.query.filter(
        Event.category == event.category,
        Event.id != event.id,
        Event.date >= datetime.utcnow()
    ).limit(3).all()

    return render_template('events/detail.html', event=event, related=related)
