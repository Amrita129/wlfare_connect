import os
import sys
import click
import getpass
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()


def create_app(config_class=None, config_overrides=None):
    app = Flask(__name__)
    if config_class is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config_class)

    if config_overrides:
        app.config.update(config_overrides)

    db.init_app(app)

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
        seed_real_scheme_data()
        init_default_users()

    from .routes import main
    app.register_blueprint(main)

    register_cli_commands(app)

    return app


def register_cli_commands(app):
    @app.cli.command("set-password")
    @click.argument("email")
    @click.option("--password", "-p", default=None, help="New password (prompted securely if omitted)")
    def set_password_command(email, password):
        """Securely update the password for an existing user account."""
        from werkzeug.security import generate_password_hash
        from .models import User, ActivityLog

        email_clean = email.strip().lower()
        user = User.query.filter_by(email=email_clean).first()
        if not user:
            click.echo(f"Error: User with email '{email_clean}' not found.", err=True)
            sys.exit(1)

        if not password:
            password = getpass.getpass(f"Enter new password for {email_clean}: ")
            confirm = getpass.getpass("Confirm new password: ")
            if password != confirm:
                click.echo("Error: Passwords do not match.", err=True)
                sys.exit(1)

        if len(password) < 6:
            click.echo("Error: Password must be at least 6 characters long.", err=True)
            sys.exit(1)

        user.password_hash = generate_password_hash(password)
        log = ActivityLog(
            user_id=user.id,
            event_type="password_change",
            description="Password updated via CLI management command.",
        )
        db.session.add(log)
        db.session.commit()
        click.echo(f"Success: Password for {email_clean} has been updated successfully.")


def init_default_users():
    from werkzeug.security import generate_password_hash
    from .models import User, Citizen

    admin_pw = os.getenv("ADMIN_PASSWORD", "admin123")
    demo_pw = os.getenv("DEMO_USER_PASSWORD", "user123")

    # Ensure admin user exists
    admin = User.query.filter_by(email="admin@welfareconnect.in").first()
    if not admin:
        admin = User(
            email="admin@welfareconnect.in",
            password_hash=generate_password_hash(admin_pw),
            name="System Administrator",
            role="admin",
        )
        db.session.add(admin)

    # Ensure demo user exists
    demo_user = User.query.filter_by(email="user@welfareconnect.in").first()
    if not demo_user:
        citizen = Citizen.query.filter_by(name="WelfareConnect User").first()
        if not citizen:
            citizen = Citizen(
                name="WelfareConnect User",
                age=21,
                gender="Female",
                occupation="Student",
                income=0,
                category="General",
                state="Maharashtra",
                district=None,
                student=True,
                farmer=False,
                senior_citizen=False,
                woman=True,
            )
            db.session.add(citizen)
            db.session.flush()

        demo_user = User(
            email="user@welfareconnect.in",
            password_hash=generate_password_hash("user123"),
            name="WelfareConnect User",
            role="user",
            citizen_id=citizen.id,
        )
        db.session.add(demo_user)

    db.session.commit()


def seed_real_scheme_data():
    from .models import Scheme
    from schemes import SCHEMES

    # Names of the 30 schemes that belong to the new WelfareConnect system
    allowed_names = {
        data["name"]
        for data in SCHEMES
    }

    # ---------------------------------------------------------
    # 1. Keep admin-published schemes active
    # ---------------------------------------------------------
    all_existing_schemes = Scheme.query.all()

    # We do NOT deactivate admin-published schemes.
    # The 30 WelfareConnect schemes are activated below.

    # ---------------------------------------------------------
    # 2. Add missing schemes
    # ---------------------------------------------------------
    existing_names = {
        scheme.name
        for scheme in all_existing_schemes
    }

    new_schemes = []

    for data in SCHEMES:

        if data["name"] in existing_names:
            # Make sure one of our 30 schemes is active
            existing_scheme = Scheme.query.filter_by(
                name=data["name"]
            ).first()

            if existing_scheme:
                existing_scheme.active = True
                if data.get("apply_link"):
                    existing_scheme.official_url = data.get("apply_link")

            continue

        documents = data.get("documents", [])

        if isinstance(documents, list):
            documents = ", ".join(documents)

        scheme = Scheme(
            name=data["name"],
            category=data.get("category", ""),
            min_age=data.get("min_age"),
            max_age=data.get("max_age"),
            income_limit=data.get("income_limit"),

            # Eligibility is handled in services.py
            occupation=None,

            state=None,

            benefits=data.get("benefits", ""),
            documents=documents,

            application_info=(
                data.get("description", "")
                + " Target group: "
                + data.get("target_group", "")
            ).strip(),

            official_url=data.get("apply_link"),

            deadline="Check the official scheme website for current dates.",

            active=True,
        )

        new_schemes.append(scheme)

    if new_schemes:
        db.session.add_all(new_schemes)

    db.session.commit()

    active_count = Scheme.query.filter_by(active=True).count()

    print(f"Active schemes: {active_count}")