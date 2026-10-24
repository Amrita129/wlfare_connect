from datetime import datetime, timezone

from . import db


class TimestampMixin:
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Scheme(TimestampMixin, db.Model):
    __tablename__ = "schemes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    category = db.Column(db.String(100), nullable=False)
    min_age = db.Column(db.Integer, nullable=True)
    max_age = db.Column(db.Integer, nullable=True)
    income_limit = db.Column(db.Float, nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    benefits = db.Column(db.Text, nullable=False)
    documents = db.Column(db.Text, nullable=False)
    application_info = db.Column(db.Text, nullable=False)
    official_url = db.Column(db.String(500), nullable=True)
    deadline = db.Column(db.String(50), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    applications = db.relationship(
        "Application",
        back_populates="scheme",
        cascade="all, delete-orphan",
    )


class Citizen(TimestampMixin, db.Model):
    __tablename__ = "citizens"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    income = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=True)
    district = db.Column(db.String(100), nullable=True)
    student = db.Column(db.Boolean, default=False, nullable=False)
    farmer = db.Column(db.Boolean, default=False, nullable=False)
    senior_citizen = db.Column(db.Boolean, default=False, nullable=False)
    woman = db.Column(db.Boolean, default=False, nullable=False)

    applications = db.relationship(
        "Application",
        back_populates="citizen",
        cascade="all, delete-orphan",
    )
    notification_preference = db.relationship(
        "NotificationPreference",
        back_populates="citizen",
        uselist=False,
        cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification",
        back_populates="citizen",
        cascade="all, delete-orphan",
    )


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(30), default="user", nullable=False)  # "user" or "admin"
    citizen_id = db.Column(
        db.Integer,
        db.ForeignKey("citizens.id"),
        nullable=True,
    )

    citizen = db.relationship(
        "Citizen",
        backref=db.backref("user_account", uselist=False),
    )


class Application(TimestampMixin, db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(
        db.Integer,
        db.ForeignKey("citizens.id"),
        nullable=False,
    )
    scheme_id = db.Column(
        db.Integer,
        db.ForeignKey("schemes.id"),
        nullable=False,
    )
    stage = db.Column(
        db.String(30),
        default="Eligible",
        nullable=False,
    )

    citizen = db.relationship("Citizen", back_populates="applications")
    scheme = db.relationship("Scheme", back_populates="applications")

    __table_args__ = (
        db.UniqueConstraint(
            "citizen_id",
            "scheme_id",
            name="uq_citizen_scheme",
        ),
    )


class LoginLog(db.Model):
    __tablename__ = "login_logs"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    logged_in_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class NotificationPreference(db.Model):
    __tablename__ = "notification_preferences"

    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(
        db.Integer,
        db.ForeignKey("citizens.id"),
        nullable=False,
        unique=True,
    )
    email = db.Column(db.String(254), nullable=True)
    mobile = db.Column(db.String(30), nullable=True)
    enabled = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    citizen = db.relationship(
        "Citizen",
        back_populates="notification_preference",
    )


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    citizen_id = db.Column(
        db.Integer,
        db.ForeignKey("citizens.id"),
        nullable=False,
    )
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(
        db.String(50),
        default="general",
        nullable=False,
    )
    is_read = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
    )
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    citizen = db.relationship(
        "Citizen",
        back_populates="notifications",
    )


STAGES = ["Eligible", "Aware", "Applied", "Approved", "Received"]
