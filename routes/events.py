from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Event, Registration, SavedEvent
from datetime import datetime
from sqlalchemy import and_

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
    from flask import session
    event = Event.query.get_or_404(event_id)
    related = Event.query.filter(
        Event.category == event.category,
        Event.id != event.id,
        Event.date >= datetime.utcnow()
    ).limit(3).all()

    # Calculate match
    user_interests = session.get('interests', [])
    match_score = 0
    match_reasons = []
    
    if user_interests:
        if event.category in user_interests:
            match_score += 80
            match_reasons.append(f"Matches your interest in {event.category}")
            
        if match_score == 0:
            match_score = 15
            match_reasons.append("Explore something new")
        else:
            match_score = min(98, match_score + 10)

    is_registered = False
    is_saved      = False
    if current_user.is_authenticated:
        is_registered = Registration.query.filter_by(
            user_id=current_user.id, event_id=event_id).first() is not None
        is_saved = SavedEvent.query.filter_by(
            user_id=current_user.id, event_id=event_id).first() is not None

    return render_template('events/detail.html',
                           event=event,
                           related=related,
                           is_registered=is_registered,
                           is_saved=is_saved,
                           match_score=match_score,
                           match_reasons=match_reasons)


# ── Create Event ──────────────────────────────────────────────────────────────
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if request.method == 'POST':
        errors = _validate_event_form(request.form)

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('events/create.html',
                                   categories=CATEGORIES,
                                   form=request.form)

        event_dt = _parse_datetime(request.form['date'], request.form['time'])

        event = Event(
            title       = request.form['title'].strip(),
            description = request.form['description'].strip(),
            category    = request.form['category'],
            location    = request.form['location'].strip(),
            date        = event_dt,
            capacity    = int(request.form['capacity']),
            created_by  = current_user.id
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Event "{event.title}" created successfully!', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('events/create.html', categories=CATEGORIES, form={})


# ── Edit Event ────────────────────────────────────────────────────────────────
@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.created_by != current_user.id:
        flash('You are not authorised to edit this event.', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))

    if request.method == 'POST':
        errors = _validate_event_form(request.form)

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('events/create.html',
                                   categories=CATEGORIES,
                                   event=event,
                                   form=request.form)

        event_dt = _parse_datetime(request.form['date'], request.form['time'])

        event.title       = request.form['title'].strip()
        event.description = request.form['description'].strip()
        event.category    = request.form['category']
        event.location    = request.form['location'].strip()
        event.date        = event_dt
        event.capacity    = int(request.form['capacity'])

        db.session.commit()

        flash(f'Event "{event.title}" updated successfully!', 'success')
        return redirect(url_for('events.event_detail', event_id=event.id))

    return render_template('events/create.html',
                           categories=CATEGORIES,
                           event=event,
                           form={})


# ── Delete Event ──────────────────────────────────────────────────────────────
@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.created_by != current_user.id:
        flash('You are not authorised to delete this event.', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))

    title = event.title
    # Remove related records before deleting event
    Registration.query.filter_by(event_id=event_id).delete()
    SavedEvent.query.filter_by(event_id=event_id).delete()
    db.session.delete(event)
    db.session.commit()

    flash(f'Event "{title}" has been deleted.', 'info')
    return redirect(url_for('events.list_events'))


# ── Helpers ───────────────────────────────────────────────────────────────────
def _validate_event_form(form):
    errors = []
    title    = form.get('title', '').strip()
    desc     = form.get('description', '').strip()
    category = form.get('category', '').strip()
    location = form.get('location', '').strip()
    date_str = form.get('date', '').strip()
    time_str = form.get('time', '').strip()
    capacity = form.get('capacity', '').strip()

    if not title or len(title) < 5:
        errors.append('Event title must be at least 5 characters.')
    if not desc or len(desc) < 20:
        errors.append('Description must be at least 20 characters.')
    if category not in CATEGORIES:
        errors.append('Please select a valid category.')
    if not location:
        errors.append('Location is required.')
    if not date_str or not time_str:
        errors.append('Date and time are required.')
    else:
        try:
            event_dt = _parse_datetime(date_str, time_str)
            if event_dt <= datetime.utcnow():
                errors.append('Event date must be in the future.')
        except ValueError:
            errors.append('Invalid date or time format.')
    if not capacity:
        errors.append('Capacity is required.')
    else:
        try:
            cap = int(capacity)
            if cap < 1 or cap > 5000:
                errors.append('Capacity must be between 1 and 5000.')
        except ValueError:
            errors.append('Capacity must be a number.')

    return errors


def _parse_datetime(date_str, time_str):
    """Combine separate date (YYYY-MM-DD) and time (HH:MM) strings into a datetime."""
    return datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')


# ── Register for Event ────────────────────────────────────────────────────────
@events_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
def register_event(event_id):
    event = Event.query.get_or_404(event_id)

    if event.date <= datetime.utcnow():
        flash('This event has already passed.', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))

    already = Registration.query.filter_by(
        user_id=current_user.id, event_id=event_id).first()
    if already:
        flash('You are already registered for this event.', 'info')
        return redirect(url_for('events.event_detail', event_id=event_id))

    if event.is_full:
        flash('Sorry, this event is now full.', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))

    reg = Registration(user_id=current_user.id, event_id=event_id)
    db.session.add(reg)
    db.session.commit()
    flash(f'You are registered for "{event.title}"!', 'success')
    return redirect(url_for('events.event_detail', event_id=event_id))


# ── Unregister from Event ─────────────────────────────────────────────────────
@events_bp.route('/<int:event_id>/unregister', methods=['POST'])
@login_required
def unregister_event(event_id):
    event = Event.query.get_or_404(event_id)
    reg = Registration.query.filter_by(
        user_id=current_user.id, event_id=event_id).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash(f'You have unregistered from "{event.title}".', 'info')
    return redirect(url_for('events.event_detail', event_id=event_id))


# ── Save / Unsave Event (Toggle) ──────────────────────────────────────────────
@events_bp.route('/<int:event_id>/save', methods=['POST'])
@login_required
def save_event(event_id):
    event = Event.query.get_or_404(event_id)
    existing = SavedEvent.query.filter_by(
        user_id=current_user.id, event_id=event_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash(f'"{event.title}" removed from saved events.', 'info')
    else:
        saved = SavedEvent(user_id=current_user.id, event_id=event_id)
        db.session.add(saved)
        db.session.commit()
        flash(f'"{event.title}" added to your saved events!', 'success')
    return redirect(url_for('events.event_detail', event_id=event_id))
