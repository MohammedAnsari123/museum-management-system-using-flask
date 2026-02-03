from flask import Flask, render_template, session, g
from db import init_db, get_db
import os
from datetime import timedelta
from routes.users import users_bp
from routes.admin import admin_bp
from routes.chatbot import chatbot_bp
from extensions import mail
from dotenv import load_dotenv

load_dotenv() # Load .env variables

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    app.permanent_session_lifetime = timedelta(days=7)

    # Email Config
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    mail.init_app(app)

    with app.app_context():
        init_db()

    if users_bp:
        app.register_blueprint(users_bp)
    if admin_bp:
        app.register_blueprint(admin_bp, url_prefix='/admin')
    if chatbot_bp:
        app.register_blueprint(chatbot_bp, url_prefix='/chatbot')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.after_request
    def add_header(response):
        """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
        """
        if 'Cache-Control' not in response.headers:
            response.headers['Cache-Control'] = 'public, max-age=600'
        return response

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=int(os.getenv("PORT", 5000)))
