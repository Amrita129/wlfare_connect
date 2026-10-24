from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from sqlalchemy import func, case
from werkzeug.security import generate_password_hash, check_password_hash

from . import db
from .models import (
    Scheme,
    Citizen,
    Application,
    LoginLog,
    Notification,
    NotificationPreference,
    User,
    STAGES,
)
from .services import analytics_payload, check_eligibility, rank_schemes


main = Blueprint("main", __name__)


@main.app_template_global()
def scheme_emoji(scheme):
    """Return a small visual marker for a welfare scheme."""
    name = (scheme.name or "").lower()
    category = (scheme.category or "").lower()

    exact = {
        "pm-kisan": "🌱",
        "pradhan mantri fasal bima yojana": "🌾",
        "pradhan mantri krishi sinchayee yojana": "💧",
        "mgnrega": "👷",
        "national scholarship portal schemes": "🎓",
        "pm-usp central sector scheme of scholarship": "🎓",
        "post-matric scholarship": "🎓",
        "pre-matric scholarship": "🎓",
        "pm shri": "🎓",
        "national apprenticeship promotion scheme": "🎓",
        "beti bachao beti padhao": "👧",
        "pradhan mantri matru vandana yojana": "🤰",
        "sukanya samriddhi yojana": "👧",
        "mission shakti": "👩",
        "poshan 2.0": "🥗",
        "ayushman bharat – pm-jay": "🏥",
        "ayushman bharat digital mission": "📱",
        "national health mission": "🩺",
        "pm awas yojana – gramin": "🏡",
        "pm awas yojana – urban": "🏙️",
        "jal jeevan mission": "💧",
        "pradhan mantri kaushal vikas yojana": "🛠️",
        "pradhan mantri mudra yojana": "💼",
        "pm svanidhi": "🛍️",
        "atal pension yojana": "👴",
        "pradhan mantri jeevan jyoti bima yojana": "🛡️",
        "pradhan mantri suraksha bima yojana": "🛡️",
        "pradhan mantri jan dhan yojana": "🏦",
        "stand-up india": "🚀",
        "national social assistance programme": "🤝",
    }

    if name in exact:
        return exact[name]

    if "education" in category:
        return "🎓"
    if "agriculture" in category:
        return "🌱"
    if "health" in category:
        return "🏥"
    if "housing" in category:
        return "🏠"
    if "employment" in category:
        return "💼"
    if "social security" in category:
        return "🛡️"
    if "banking" in category:
        return "🏦"
    if "women" in category:
        return "👩"

    return "📋"


# India Standard Time
IST = ZoneInfo("Asia/Kolkata")


# -------------------------------------------------------------------
# TIME HELPER
# -------------------------------------------------------------------

def to_ist(dt):
    """Convert a database UTC timestamp to India Standard Time."""

    if dt is None:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(IST)


@main.app_context_processor
def inject_global_data():
    citizen_id = session.get("citizen_id")
    unread = 0
    if citizen_id:
        unread = Notification.query.filter_by(
            citizen_id=citizen_id,
            is_read=False,
        ).count()
    return {
        "unread_notification_count": unread,
        "current_user_name": session.get("display_name", "User"),
        "user_role": session.get("role"),
    }


# -------------------------------------------------------------------
# DEMO USERS
# -------------------------------------------------------------------

DEMO_USERS = {
    "admin@welfareconnect.in": {
        "password": "admin123",
        "role": "admin",
        "name": "System Administrator",
    },
    "user@welfareconnect.in": {
        "password": "user123",
        "role": "user",
        "name": "WelfareConnect User",
    },
}


# -------------------------------------------------------------------
# CITIZEN FORM
# -------------------------------------------------------------------

def parse_citizen_form(form):
    age = int(form.get("age") or 0)
    income = float(form.get("income") or 0)

    if age < 0 or age > 120:
        raise ValueError("Age must be between 0 and 120.")

    if income < 0:
        raise ValueError("Income cannot be negative.")

    gender = form.get("gender") or None
    occupation = form.get("occupation", "").strip() or None
    category = form.get("category", "").strip() or None

    occupation_normal = (occupation or "").lower()

    return {
        "name": form.get("name", "").strip(),
        "age": age,
        "gender": gender,
        "occupation": occupation,
        "income": income,
        "category": category,
        "state": form.get("state", "").strip() or None,
        "district": form.get("district", "").strip() or None,
        "student": occupation_normal in {
            "student",
            "school student",
            "college student",
            "university student",
            "apprentice",
        },
        "farmer": occupation_normal in {
            "farmer",
            "agricultural worker",
            "agriculture",
        },
        "senior_citizen": age >= 60,
        "woman": (gender or "").lower() == "female",
    }


# -------------------------------------------------------------------
# SESSION HELPERS
# -------------------------------------------------------------------

def logged_in():
    return "role" in session


def current_citizen():
    citizen_id = session.get("citizen_id")

    if not citizen_id:
        return None

    return db.session.get(Citizen, citizen_id)


def require_user():
    if session.get("role") != "user":
        flash("Please log in as a citizen to continue.", "error")
        return redirect(url_for("main.home", login="1"))

    return None


def require_admin():
    if session.get("role") != "admin":
        flash("Admin access is required.", "error")
        return redirect(url_for("main.home", login="1"))

    return None


# -------------------------------------------------------------------
# HOME
# -------------------------------------------------------------------

@main.route("/")
def home():
    return render_template(
        "index.html",
        logged_in=logged_in(),
    )


# -------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if logged_in():
            if session.get("role") == "admin":
                return redirect(url_for("main.dashboard"))
            return redirect(url_for("main.user_home"))
        return redirect(url_for("main.home", login="1"))

    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "")

    # Look up registered user from persistent database
    user = User.query.filter_by(email=username).first()
    authenticated = False
    role = None
    display_name = None
    citizen_id = None

    if user and check_password_hash(user.password_hash, password):
        authenticated = True
        role = user.role
        display_name = user.name
        citizen_id = user.citizen_id
    elif username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
        # Fallback for demo users
        authenticated = True
        role = DEMO_USERS[username]["role"]
        display_name = DEMO_USERS[username]["name"]

    if not authenticated:
        flash("Invalid email or password. Please try again.", "error")
        return redirect(url_for("main.home", login="1"))

    session.clear()
    session["username"] = username
    session["role"] = role
    session["display_name"] = display_name

    db.session.add(
        LoginLog(
            username=username,
            role=role,
        )
    )

    if role == "user":
        if not citizen_id:
            citizen = Citizen.query.filter_by(name="WelfareConnect User").first()
            if not citizen:
                citizen = Citizen(
                    name=display_name or "WelfareConnect User",
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
            citizen_id = citizen.id
            if user:
                user.citizen_id = citizen_id

        session["citizen_id"] = citizen_id
        db.session.commit()
        flash(f"Welcome back, {display_name}!", "success")
        return redirect(url_for("main.user_home"))

    if role == "admin":
        db.session.commit()
        flash(f"Welcome to Admin Portal, {display_name}!", "success")
        return redirect(url_for("main.dashboard"))

    db.session.commit()
    return redirect(url_for("main.home"))


# -------------------------------------------------------------------
# REGISTER (CITIZEN REGISTRATION)
# -------------------------------------------------------------------

@main.route("/register", methods=["GET", "POST"])
def register():
    if logged_in():
        if session.get("role") == "admin":
            return redirect(url_for("main.dashboard"))
        return redirect(url_for("main.user_home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        name = request.form.get("name", "").strip()

        # Input validations
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "error")
            return render_template("register.html", form_data=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html", form_data=request.form)

        if password != confirm_password:
            flash("Passwords do not match. Please verify.", "error")
            return render_template("register.html", form_data=request.form)

        if not name:
            flash("Please enter your full name.", "error")
            return render_template("register.html", form_data=request.form)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email address already exists. Please log in.", "error")
            return redirect(url_for("main.home", login="1"))

        try:
            cit_data = parse_citizen_form(request.form)
            citizen = Citizen(**cit_data)
            db.session.add(citizen)
            db.session.flush()

            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                name=name,
                role="user",
                citizen_id=citizen.id,
            )
            db.session.add(user)

            mobile = request.form.get("mobile", "").strip() or None
            pref = NotificationPreference(
                citizen_id=citizen.id,
                email=email,
                mobile=mobile,
                enabled=True,
            )
            db.session.add(pref)

            welcome_notif = Notification(
                citizen_id=citizen.id,
                title="🎉 Welcome to WelfareConnect!",
                message="Your citizen profile is active. Check out personalized welfare schemes matching your profile.",
                notification_type="general",
            )
            db.session.add(welcome_notif)

            db.session.add(LoginLog(username=email, role="user"))
            db.session.commit()

            session.clear()
            session["username"] = email
            session["role"] = "user"
            session["display_name"] = name
            session["citizen_id"] = citizen.id

            flash(f"Account registered successfully! Welcome to WelfareConnect, {name}.", "success")
            return redirect(url_for("main.find_schemes"))

        except Exception as exc:
            db.session.rollback()
            flash(f"Registration failed: {str(exc)}", "error")
            return render_template("register.html", form_data=request.form)

    return render_template("register.html", form_data={})


# -------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------

@main.get("/logout")
def logout():
    session.clear()

    flash(
        "You have been logged out successfully.",
        "success",
    )

    return redirect(url_for("main.home"))


# -------------------------------------------------------------------
# USER DASHBOARD
# -------------------------------------------------------------------

@main.get("/user")
def user_home():
    guard = require_user()

    if guard:
        return guard

    citizen = current_citizen()

    applications = (
        Application.query
        .filter_by(citizen_id=citizen.id)
        .order_by(Application.created_at.desc())
        .all()
    )

    counts = {
        stage: 0
        for stage in STAGES
    }

    for app in applications:
        counts[app.stage] = counts.get(app.stage, 0) + 1

    notification_count = Notification.query.filter_by(
        citizen_id=citizen.id,
        is_read=False,
    ).count()

    return render_template(
        "user_home.html",
        citizen=citizen,
        applications=applications[:5],
        counts=counts,
        notification_count=notification_count,
        to_ist=to_ist,
    )


# -------------------------------------------------------------------
# PROFILE
# -------------------------------------------------------------------

@main.get("/profile")
def profile():
    guard = require_user()

    if guard:
        return guard

    return render_template(
        "profile.html",
        citizen=current_citizen(),
        to_ist=to_ist,
    )


@main.post("/profile")
def update_profile():
    guard = require_user()

    if guard:
        return guard

    citizen = current_citizen()

    try:
        data = parse_citizen_form(request.form)

        if not data["name"]:
            raise ValueError("Name is required.")

        for key, value in data.items():
            setattr(citizen, key, value)

        db.session.commit()

        flash(
            "Profile updated successfully.",
            "success",
        )

    except (ValueError, TypeError) as exc:
        db.session.rollback()

        flash(
            str(exc),
            "error",
        )

    return redirect(url_for("main.profile"))


# -------------------------------------------------------------------
# NOTIFICATIONS
# -------------------------------------------------------------------

@main.get("/notifications")
def notifications():
    guard = require_user()

    if guard:
        return guard

    citizen = current_citizen()

    preference = NotificationPreference.query.filter_by(
        citizen_id=citizen.id
    ).first()

    items = (
        Notification.query
        .filter_by(citizen_id=citizen.id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    # Connect new-scheme notifications to their scheme.
    for item in items:
        item.scheme_id = None

        if item.notification_type == "new_scheme":
            prefix = "🆕 New scheme: "

            if item.title.startswith(prefix):
                scheme_name = item.title[len(prefix):].strip()

                scheme = Scheme.query.filter_by(
                    name=scheme_name
                ).first()

                if scheme:
                    item.scheme_id = scheme.id

    # Viewing the notification center marks displayed items as read.
    for item in items:
        item.is_read = True

    db.session.commit()

    return render_template(
        "notifications.html",
        notifications=items,
        preference=preference,
        to_ist=to_ist,
    )


@main.post("/notifications/preferences")
def update_notification_preferences():
    guard = require_user()

    if guard:
        return guard

    citizen = current_citizen()

    email = request.form.get("email", "").strip()
    mobile = request.form.get("mobile", "").strip()
    enabled = request.form.get("notifications_enabled") == "on"

    if enabled and not email and not mobile:
        flash(
            "Please enter an email address or mobile number to receive notifications.",
            "error",
        )
        return redirect(url_for("main.notifications"))

    if email and (
        "@" not in email
        or "." not in email.split("@")[-1]
    ):
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("main.notifications"))

    digits = "".join(ch for ch in mobile if ch.isdigit())

    if mobile and not (10 <= len(digits) <= 13):
        flash("Please enter a valid mobile number.", "error")
        return redirect(url_for("main.notifications"))

    preference = NotificationPreference.query.filter_by(
        citizen_id=citizen.id
    ).first()

    if preference is None:
        preference = NotificationPreference(citizen_id=citizen.id)
        db.session.add(preference)

    preference.email = email or None
    preference.mobile = mobile or None
    preference.enabled = enabled

    db.session.commit()

    flash(
        "Notification preferences saved successfully.",
        "success",
    )

    return redirect(url_for("main.notifications"))


# -------------------------------------------------------------------
# FIND SCHEMES
# -------------------------------------------------------------------

@main.route("/find-schemes", methods=["GET", "POST"])
def find_schemes():
    guard = require_user()

    if guard:
        return guard

    citizen = current_citizen()
    error = None
    search_query = request.args.get("q", "").strip()
    selected_category = request.args.get("category", "").strip()

    if request.method == "POST":
        try:
            data = parse_citizen_form(request.form)

            if not data["name"]:
                raise ValueError("Please enter your name.")

            for key, value in data.items():
                setattr(citizen, key, value)

            db.session.commit()
            flash("Profile updated successfully! Scheme matches refreshed.", "success")

        except (ValueError, TypeError) as exc:
            db.session.rollback()
            error = str(exc)

    active_query = Scheme.query.filter_by(active=True)

    if selected_category and selected_category != "All":
        active_query = active_query.filter_by(category=selected_category)

    active_schemes = active_query.all()

    if search_query:
        sq = search_query.lower()
        active_schemes = [
            s for s in active_schemes
            if sq in (s.name or "").lower()
            or sq in (s.category or "").lower()
            or sq in (s.benefits or "").lower()
            or sq in (s.application_info or "").lower()
        ]

    reviewed_count = len(active_schemes)
    results = rank_schemes(citizen, active_schemes)

    categories = [
        "All",
        "Women & Child",
        "Education & Learning",
        "Agriculture & Rural Development",
        "Health & Wellness",
        "Housing & Basic Needs",
        "Employment & Skills",
        "Social Security",
        "Banking & Financial Inclusion",
    ]

    form_data = {
        "name": citizen.name,
        "age": citizen.age,
        "gender": citizen.gender or "",
        "occupation": citizen.occupation or "",
        "income": citizen.income or 0,
        "category": citizen.category or "",
        "state": citizen.state or "Maharashtra",
        "district": citizen.district or "",
    }

    return render_template(
        "find_schemes.html",
        results=results,
        data=form_data,
        error=error,
        reviewed_count=reviewed_count,
        search_query=search_query,
        selected_category=selected_category or "All",
        categories=categories,
        total_schemes_count=Scheme.query.filter_by(active=True).count(),
    )


# -------------------------------------------------------------------
# SCHEME DETAILS
# -------------------------------------------------------------------

@main.route("/scheme/<int:scheme_id>")
def scheme_detail(scheme_id):
    guard = require_user()

    if guard:
        return guard

    scheme = Scheme.query.get_or_404(scheme_id)
    citizen = current_citizen()

    is_eligible, reasons, criteria_details = check_eligibility(
        citizen,
        scheme,
        detailed=True,
    )

    existing_application = Application.query.filter_by(
        citizen_id=citizen.id,
        scheme_id=scheme.id,
    ).first()

    return render_template(
        "scheme_detail.html",
        scheme=scheme,
        citizen=citizen,
        is_eligible=is_eligible,
        reasons=reasons,
        criteria_details=criteria_details,
        existing_application=existing_application,
    )


# -------------------------------------------------------------------
# APPLY FOR SCHEME
# -------------------------------------------------------------------

@main.route("/apply/<int:scheme_id>", methods=["POST"])
def apply(scheme_id):
    guard = require_user()

    if guard:
        return guard

    scheme = Scheme.query.get_or_404(scheme_id)
    citizen = current_citizen()

    try:
        eligible, reasons = check_eligibility(
            citizen,
            scheme,
        )

        if not eligible:
            flash(
                "This scheme is not currently eligible for your profile: "
                + " ".join(reasons),
                "error",
            )

            return redirect(
                url_for(
                    "main.scheme_detail",
                    scheme_id=scheme.id,
                )
            )

        existing = (
            Application.query
            .filter_by(
                citizen_id=citizen.id,
                scheme_id=scheme.id,
            )
            .first()
        )

        if existing:
            flash(
                "You are already tracking this scheme.",
                "error",
            )

            return redirect(
                url_for("main.my_applications")
            )

        application = Application(
            citizen_id=citizen.id,
            scheme_id=scheme.id,
            stage="Applied",
        )

        db.session.add(application)
        db.session.flush()

        db.session.add(
            Notification(
                citizen_id=citizen.id,
                title=f"📋 {scheme.name} application added",
                message="Your scheme has been added to My Applications for tracking.",
                notification_type="application_status",
            )
        )

        db.session.commit()

        flash(
            "Application added to your WelfareConnect tracking.",
            "success",
        )

    except Exception as exc:
        db.session.rollback()

        flash(
            f"Unable to add application: {exc}",
            "error",
        )

    return redirect(
        url_for("main.my_applications")
    )


# -------------------------------------------------------------------
# MY APPLICATIONS
# -------------------------------------------------------------------

@main.route("/applications")
def my_applications():
    guard = require_user()

    if guard:
        return guard

    citizen = current_citizen()
    status_filter = request.args.get("status", "All")

    query = Application.query.filter_by(citizen_id=citizen.id)
    if status_filter in STAGES:
        query = query.filter_by(stage=status_filter)

    applications = query.order_by(Application.created_at.desc()).all()

    # Calculate counts per stage for filter tabs
    all_apps = Application.query.filter_by(citizen_id=citizen.id).all()
    stage_counts = {s: 0 for s in STAGES}
    for a in all_apps:
        if a.stage in stage_counts:
            stage_counts[a.stage] += 1

    return render_template(
        "applications.html",
        applications=applications,
        status_filter=status_filter,
        stage_counts=stage_counts,
        stages=STAGES,
        total_count=len(all_apps),
        to_ist=to_ist,
    )



# -------------------------------------------------------------------
# ADMIN - PUBLISH NEW SCHEME
# -------------------------------------------------------------------

@main.post("/admin/scheme/create")
def create_scheme():
    if session.get("role") != "admin":
        return redirect(url_for("main.login"))

    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    benefits = request.form.get("benefits", "").strip()
    documents = request.form.get("documents", "").strip()
    application_info = request.form.get("application_info", "").strip()

    if not name or not category:
        flash(
            "Scheme name and category are required.",
            "error",
        )
        return redirect(url_for("main.dashboard"))

    def to_int(value):
        try:
            return int(value) if value else None
        except ValueError:
            return None

    def to_float(value):
        try:
            return float(value) if value else None
        except ValueError:
            return None

    scheme = Scheme(
        name=name,
        category=category,
        min_age=to_int(request.form.get("min_age")),
        max_age=to_int(request.form.get("max_age")),
        income_limit=to_float(
            request.form.get("income_limit")
        ),
        occupation=request.form.get(
            "occupation",
            ""
        ).strip() or None,
        state=request.form.get(
            "state",
            ""
        ).strip() or None,
        benefits=benefits,
        documents=documents,
        application_info=application_info,
        official_url=request.form.get(
            "official_url",
            ""
        ).strip() or None,
        deadline=request.form.get(
            "deadline",
            ""
        ).strip() or None,
        active=True,
    )

    db.session.add(scheme)
    db.session.flush()

    notified = 0

    # Notify citizens who are eligible for the new scheme
    for citizen in Citizen.query.all():
        eligible, _ = check_eligibility(
            citizen,
            scheme,
        )

        if eligible:
            notification = Notification(
                citizen_id=citizen.id,
                title=f"🆕 New scheme: {scheme.name}",
                message=(
                    "A new welfare scheme has been published. "
                    "Check your profile-based eligibility and scheme details."
                ),
                notification_type="new_scheme",
            )

            db.session.add(notification)
            notified += 1

    db.session.commit()

    flash(
        f"Scheme published successfully. {notified} eligible user(s) notified.",
        "success",
    )

    return redirect(url_for("main.dashboard"))


# -------------------------------------------------------------------
# ADMIN DASHBOARD
# -------------------------------------------------------------------

@main.route("/admin")
def dashboard():
    guard = require_admin()

    if guard:
        return guard

    applications = (
        Application.query
        .order_by(Application.created_at.desc())
        .all()
    )

    payload = analytics_payload(applications)

    total_logins = LoginLog.query.count()

    unique_logins = (
        db.session
        .query(
            func.count(
                func.distinct(LoginLog.username)
            )
        )
        .scalar()
        or 0
    )

    user_login_rows = (
        db.session
        .query(
            LoginLog.username,
            LoginLog.role,
            func.count(LoginLog.id).label("login_count"),
            func.max(LoginLog.logged_in_at).label("last_login"),
        )
        .group_by(
            LoginLog.username,
            LoginLog.role,
        )
        .order_by(
            func.count(LoginLog.id).desc()
        )
        .all()
    )

    login_display_rows = []

    for row in user_login_rows:
        login_display_rows.append(
            {
                "username": row.username,
                "role": row.role,
                "login_count": row.login_count,
                "last_login": to_ist(row.last_login),
            }
        )

    scheme_rows = (
        db.session
        .query(
            Scheme.name,
            func.count(Application.id).label("applied"),
            func.sum(
                case(
                    (Application.stage == "Approved", 1),
                    else_=0,
                )
            ).label("approved"),
            func.sum(
                case(
                    (Application.stage == "Received", 1),
                    else_=0,
                )
            ).label("received"),
        )
        .outerjoin(Application)
        .group_by(Scheme.id)
        .order_by(
            func.count(Application.id).desc()
        )
        .all()
    )

    return render_template(
        "dashboard.html",
        counts=payload["counts"],
        applications=applications,
        analytics=payload,
        scheme_rows=scheme_rows,
        total_logins=total_logins,
        unique_logins=unique_logins,
        user_login_rows=login_display_rows,
        to_ist=to_ist,
    )


# -------------------------------------------------------------------
# ADMIN - GAP ANALYSIS DASHBOARD
# -------------------------------------------------------------------

@main.route("/admin/gap-analysis")
def gap_analysis():
    guard = require_admin()
    if guard:
        return guard

    applications = (
        Application.query
        .order_by(Application.created_at.desc())
        .all()
    )

    payload = analytics_payload(applications)

    total_citizens = Citizen.query.count()
    total_schemes = Scheme.query.count()
    active_schemes = Scheme.query.filter_by(active=True).count()
    total_logins = LoginLog.query.count()

    return render_template(
        "gap_analysis.html",
        analytics=payload,
        counts=payload["counts"],
        gaps=payload["gaps"],
        rates=payload["conversion_rates"],
        transitions=payload["stage_transitions"],
        bottleneck=payload["largest_gap"],
        scheme_rows=payload["scheme_rows"],
        category_counts=payload["category_counts"],
        gender_counts=payload["gender_counts"],
        demographic_flags=payload["demographic_flags"],
        charts=payload["charts"],
        total_citizens=total_citizens,
        total_schemes=total_schemes,
        active_schemes=active_schemes,
        total_logins=total_logins,
        total_applications=len(applications),
        to_ist=to_ist,
    )


# -------------------------------------------------------------------
# ADMIN - UPDATE APPLICATION STATUS
# -------------------------------------------------------------------

@main.route(
    "/admin/application/<int:application_id>/stage",
    methods=["POST"],
)
def update_stage(application_id):
    guard = require_admin()

    if guard:
        return guard

    application = Application.query.get_or_404(
        application_id
    )

    stage = request.form.get("stage")

    if stage not in STAGES:
        flash(
            "Invalid application stage.",
            "error",
        )
    else:
        application.stage = stage

        db.session.add(
            Notification(
                citizen_id=application.citizen_id,
                title=f"🔔 {application.scheme.name} status updated",
                message=f"Your application is now marked as {stage}.",
                notification_type="application_status",
            )
        )

        db.session.commit()

        flash(
            f"Application updated to {stage}.",
            "success",
        )

    return redirect(
        url_for("main.dashboard")
    )


# -------------------------------------------------------------------
# JSON API
# -------------------------------------------------------------------

@main.get("/api/health")
def api_health():
    return jsonify(
        {
            "status": "ok",
            "service": "welfare-scheme-backend",
        }
    )


@main.get("/api/schemes")
def api_schemes():
    schemes = (
        Scheme.query
        .filter_by(active=True)
        .order_by(Scheme.name)
        .all()
    )

    return jsonify(
        {
            "schemes": [
                scheme_to_dict(scheme)
                for scheme in schemes
            ]
        }
    )


@main.get("/api/schemes/<int:scheme_id>")
def api_scheme(scheme_id):
    scheme = Scheme.query.get_or_404(
        scheme_id
    )

    return jsonify(
        scheme_to_dict(scheme)
    )


@main.post("/api/recommend")
def api_recommend():
    data = request.get_json(
        silent=True
    ) or {}

    try:
        citizen = Citizen(
            name=data.get(
                "name",
                "API User",
            ),
            age=int(
                data.get(
                    "age",
                    0,
                )
            ),
            gender=data.get("gender"),
            occupation=data.get("occupation"),
            income=float(
                data.get(
                    "income",
                    0,
                )
            ),
            category=data.get("category"),
            state=data.get("state"),
            district=data.get("district"),
            student=bool(
                data.get("student")
            ),
            farmer=bool(
                data.get("farmer")
            ),
            senior_citizen=bool(
                data.get("senior_citizen")
            ),
            woman=bool(
                data.get("woman")
            ),
        )

        if (
            citizen.age < 0
            or citizen.age > 120
            or citizen.income < 0
        ):
            raise ValueError(
                "Invalid age or income."
            )

    except (ValueError, TypeError) as exc:
        return jsonify(
            {
                "error": str(exc),
            }
        ), 400

    ranked = rank_schemes(
        citizen,
        Scheme.query.filter_by(active=True).all(),
    )

    return jsonify(
        {
            "matches": [
                {
                    **scheme_to_dict(item["scheme"]),
                    "eligible": item["eligible"],
                    "score": item["score"],
                    "reasons": item["reasons"],
                }
                for item in ranked
            ]
        }
    )


@main.get("/api/analytics")
def api_analytics():
    return jsonify(
        analytics_payload(
            Application.query.all()
        )
    )


# -------------------------------------------------------------------
# SCHEME JSON SERIALIZATION
# -------------------------------------------------------------------

def scheme_to_dict(scheme):
    return {
        "id": scheme.id,
        "name": scheme.name,
        "category": scheme.category,
        "min_age": scheme.min_age,
        "max_age": scheme.max_age,
        "income_limit": scheme.income_limit,
        "occupation": scheme.occupation,
        "state": scheme.state,
        "benefits": scheme.benefits,
        "documents": scheme.documents,
        "application_info": scheme.application_info,
        "official_url": scheme.official_url,
        "deadline": scheme.deadline,
        "active": scheme.active,
        "emoji": scheme_emoji(scheme),
    }