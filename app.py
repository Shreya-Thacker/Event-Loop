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
        from models import Event
        featured = Event.query.filter(
            Event.date >= datetime.utcnow()
        ).order_by(Event.date.asc()).limit(6).all()
        return render_template('index.html', featured=featured)

    # Create all DB tables on first run
    with app.app_context():
        db.create_all()

    return app


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
