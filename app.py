from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from models import db, User
from datetime import datetime

# ── App Factory ───────────────────────────────────────────────────────────────
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise extensions
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── Blueprints (registered here as they are built) ────────────────────────
    from routes.auth   import auth_bp
    from routes.events import events_bp
    from routes.user   import user_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(user_bp)

    # ── Temporary placeholder routes ──────────────────────────────────────────
    @app.route('/')
    def index():
        from flask import session
        from models import Event
        user_interests = session.get('interests', [])
        
        all_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date.asc()).all()
        
        # Calculate match for all events
        for e in all_events:
            # We add attributes dynamically for the template
            e.match_score = 0
            e.match_reasons = []
            if user_interests:
                if e.category in user_interests:
                    e.match_score += 80
                    e.match_reasons.append(f"Matches your interest in {e.category}")
                
                # Simple logic based on title/desc keywords if we wanted to expand
                # For now, just category match + some base score for all
                
                if e.match_score == 0:
                    e.match_score = 15 # base low score for non-matching
                    e.match_reasons.append("Explore something new")
                else:
                    e.match_score = min(98, e.match_score + 10) # cap at 98% for realism
                    
        # Sort by match score descending, then date
        all_events.sort(key=lambda x: (-getattr(x, 'match_score', 0), x.date))
        
        # Split into picked for you and explore beyond
        picked = [e for e in all_events if getattr(e, 'match_score', 0) > 50][:6]
        explore = [e for e in all_events if getattr(e, 'match_score', 0) <= 50][:4]
        
        if not user_interests:
            picked = all_events[:6]
            explore = []
            
        return render_template('index.html', picked=picked, explore=explore, user_interests=user_interests)

    @app.route('/set_interests', methods=['POST'])
    def set_interests():
        from flask import session, request, redirect, url_for
        session['interests'] = request.form.getlist('interests')
        return redirect(url_for('index'))

    # Create all DB tables on first run
    with app.app_context():
        db.create_all()

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
