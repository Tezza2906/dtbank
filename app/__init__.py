

from flask import Blueprint, Flask, redirect, url_for, render_template, session
from flask_bcrypt import Bcrypt
from config import SECRET_KEY  # make sure in config.py it is SECRET_KEY (all caps)

bcrypt = Bcrypt()

def create_app():
    # Tell Flask explicitly where templates folder is
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = SECRET_KEY

    bcrypt.init_app(app)

    # Import blueprints after app is created
    from .customer_routes import customer_bp
    from .admin_routes import admin_bp

    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def home():
        if "customer_id" in session:
            return redirect(url_for("customer.dashboard"))
        elif "admin_id" in session:
            return redirect(url_for("admin.dashboard"))
        return render_template("frontpage.html")



    return app
