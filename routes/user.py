from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Registration, SavedEvent, Event
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')


# ── Profile ───────────────────────────────────────────────────────────────────
@user_bp.route('/profile')
@login_required
def profile():
    now = datetime.utcnow()

    # Registrations (with event details), split into upcoming / past
    registrations = (
        Registration.query
        .filter_by(user_id=current_user.id)
        .join(Registration.event)
        .order_by(Event.date.asc())
        .all()
    )
    upcoming_regs = [r for r in registrations if r.event.date >= now]
    past_regs     = [r for r in registrations if r.event.date <  now]

    # Saved events
    saved = (
        SavedEvent.query
        .filter_by(user_id=current_user.id)
        .join(SavedEvent.event)
        .order_by(Event.date.asc())
        .all()
    )

    # Events this user has organised
    organised = (
        Event.query
        .filter_by(created_by=current_user.id)
        .order_by(Event.date.desc())
        .all()
    )

    return render_template('user/profile.html',
                           upcoming_regs=upcoming_regs,
                           past_regs=past_regs,
                           saved=saved,
                           organised=organised,
                           now=now)
