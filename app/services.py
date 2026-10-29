import json
from sqlalchemy import func
from .models import STAGES


def _normal(value):
    return (value or "").strip().lower()


def _scheme_name(scheme):
    return (
        _normal(scheme.name)
        .replace("–", "-")
        .replace("—", "-")
    )


def _occupation(citizen):
    return _normal(citizen.occupation)


def _category(citizen):
    return _normal(citizen.category)


def _is_student(citizen):
    return bool(citizen.student) or _occupation(citizen) in {
        "student",
        "school student",
        "college student",
        "university student",
    }


def _is_farmer(citizen):
    return bool(citizen.farmer) or _occupation(citizen) in {
        "farmer",
        "agricultural worker",
        "agriculture",
    }


def _is_woman(citizen):
    return bool(citizen.woman) or _normal(citizen.gender) == "female"


def _is_senior(citizen):
    return bool(citizen.senior_citizen) or citizen.age >= 60


def _is_low_income(citizen):
    return (citizen.income or 0) <= 300000


def _has_vulnerable_category(citizen):
    return _category(citizen) in {
        "sc",
        "st",
        "ews",
        "minority",
        "persons with disability",
        "pwd",
    }


def check_eligibility(citizen, scheme, detailed=False):
    """
    Return (eligible, reasons) or (eligible, reasons, criteria_details).

    These are transparent academic prototype rules.
    They are intended for project demonstration only.
    Final eligibility must always be verified on the
    official government scheme website.
    """

    name = _scheme_name(scheme)
    occupation = _occupation(citizen)
    category = _category(citizen)
    age = citizen.age
    income = citizen.income or 0

    reasons = []

    # =================================================
    # GENERIC AGE AND INCOME RULES
    # =================================================

    if scheme.min_age is not None and age < scheme.min_age:
        reasons.append(
            f"Minimum age is {scheme.min_age}."
        )

    if scheme.max_age is not None and age > scheme.max_age:
        reasons.append(
            f"Maximum age is {scheme.max_age}."
        )

    if scheme.income_limit is not None and income > scheme.income_limit:
        reasons.append(
            f"Income must be at or below ₹{scheme.income_limit:,.0f}."
        )

    # Senior Citizen is an age-based profile.
    if occupation == "senior citizen" and age < 60:
        reasons.append(
            "Senior Citizen profile requires age 60 or above."
        )

    # =================================================
    # WOMEN & CHILD
    # =================================================

    if name == "beti bachao beti padhao":

        if not _is_woman(citizen) or age > 18:
            reasons.append(
                "This prototype targets girls/adolescents up to age 18."
            )

    elif name == "pradhan mantri matru vandana yojana":

        # Pregnancy/lactation information is not collected
        # in the current profile form.
        reasons.append(
            "Maternity-specific information is required and is not "
            "collected in the current profile."
        )

    elif name == "sukanya samriddhi yojana":

        if not _is_woman(citizen) or age > 10:
            reasons.append(
                "This scheme targets girls up to age 10."
            )

    elif name == "mission shakti":

        if not _is_woman(citizen):
            reasons.append(
                "This scheme targets women."
            )

    elif name == "poshan 2.0":

        # Current form does not collect pregnancy/lactation status.
        # Therefore only very young children can pass this prototype rule.
        if age > 6:
            reasons.append(
                "This prototype targets children up to age 6."
            )

    # =================================================
    # EDUCATION
    # =================================================

    elif name == "national scholarship portal schemes":

        if not _is_student(citizen):
            reasons.append(
                "Student status is required."
            )

    elif name == "pm-usp central sector scheme of scholarship":

        if not _is_student(citizen):
            reasons.append(
                "Student status is required."
            )

        if not (18 <= age <= 25):
            reasons.append(
                "This prototype uses an age range of 18 to 25."
            )

    elif name == "post-matric scholarship":

        if not _is_student(citizen):
            reasons.append(
                "Student status is required."
            )

        if age < 16:
            reasons.append(
                "Post-matric education generally requires a post-school-age student."
            )

    elif name == "pre-matric scholarship":

        if not _is_student(citizen):
            reasons.append(
                "Student status is required."
            )

        if age > 16:
            reasons.append(
                "This prototype targets school-age students."
            )

    elif name == "pm shri":

        if not _is_student(citizen):
            reasons.append(
                "Student status is required."
            )

        if age > 18:
            reasons.append(
                "This prototype targets school-age students."
            )

    # =================================================
    # AGRICULTURE & RURAL DEVELOPMENT
    # =================================================

    elif name == "pm-kisan":

        if not _is_farmer(citizen):
            reasons.append(
                "Farmer status is required."
            )

    elif name == "pradhan mantri fasal bima yojana":

        if not _is_farmer(citizen):
            reasons.append(
                "Farmer status is required."
            )

    elif name == "pradhan mantri krishi sinchayee yojana":

        if not _is_farmer(citizen):
            reasons.append(
                "Farmer or agricultural worker status is required."
            )

    elif name == "mgnrega":

        if occupation not in {
            "farmer",
            "daily wage worker",
            "unemployed",
            "agricultural worker",
        }:
            reasons.append(
                "This prototype targets rural workers and wage workers."
            )

        if age < 18:
            reasons.append(
                "Adult working age is required."
            )

    # =================================================
    # HOUSING & BASIC NEEDS
    # =================================================

    elif name == "pm awas yojana - gramin":

        # Rural residence/housing ownership information is not
        # collected in the current form.
        reasons.append(
            "Rural housing information is required and is not "
            "collected in the current profile."
        )

    elif name == "pm awas yojana - urban":

        # Urban housing/household information is not collected.
        reasons.append(
            "Urban housing information is required and is not "
            "collected in the current profile."
        )

    elif name == "jal jeevan mission":

        # Household water-access information is not collected.
        reasons.append(
            "Household water-access information is not collected "
            "in the current profile."
        )

    # =================================================
    # EMPLOYMENT & SKILLS
    # =================================================

    elif name == "pradhan mantri kaushal vikas yojana":

        if occupation not in {
            "student",
            "unemployed",
            "self-employed",
            "daily wage worker",
            "other",
        }:
            reasons.append(
                "This prototype targets people seeking skill development."
            )

        if not (15 <= age <= 45):
            reasons.append(
                "This prototype uses an age range of 15 to 45."
            )

    elif name == "pradhan mantri mudra yojana":

        if occupation != "self-employed":
            reasons.append(
                "This prototype targets self-employed people."
            )

    elif name == "pm svanidhi":

        if occupation != "street vendor":
            reasons.append(
                "Street-vendor status is required."
            )

    elif name == "national apprenticeship promotion scheme":

        if occupation not in {
            "student",
            "unemployed",
            "self-employed",
            "daily wage worker",
            "other",
        }:
            reasons.append(
                "This prototype targets people seeking apprenticeship "
                "and training opportunities."
            )

        if not (15 <= age <= 35):
            reasons.append(
                "This prototype uses an age range of 15 to 35."
            )

    # =================================================
    # HEALTH & WELLNESS
    # =================================================

    elif name == "ayushman bharat - pm-jay":

        if not _is_low_income(citizen):
            reasons.append(
                "This prototype uses a low-income threshold."
            )

        if not _has_vulnerable_category(citizen):
            reasons.append(
                "This prototype requires a vulnerable social category "
                "for PM-JAY matching."
            )

    elif name == "ayushman bharat digital mission":

        # ABDM is a broad digital-health programme rather than
        # a profile-specific benefit. It is not counted as a
        # targeted match in this prototype.
        reasons.append(
            "This is a general digital-health programme and is not "
            "profile-targeted in the current prototype."
        )

    elif name == "national health mission":

        # NHM is a broad public-health programme and does not have
        # a single profile-based eligibility rule for this form.
        reasons.append(
            "This is a broad public-health programme and is not "
            "profile-targeted in the current prototype."
        )

    # =================================================
    # SOCIAL SECURITY
    # =================================================

    elif name == "atal pension yojana":

        if not (18 <= age <= 40):
            reasons.append(
                "This prototype uses an age range of 18 to 40."
            )

    elif name == "pradhan mantri jeevan jyoti bima yojana":

        if not (18 <= age <= 50):
            reasons.append(
                "This prototype uses an age range of 18 to 50."
            )

    elif name == "pradhan mantri suraksha bima yojana":

        if not (18 <= age <= 70):
            reasons.append(
                "This prototype uses an age range of 18 to 70."
            )

    # =================================================
    # BANKING & FINANCIAL INCLUSION
    # =================================================

    elif name == "pradhan mantri jan dhan yojana":

        if not _is_low_income(citizen):
            reasons.append(
                "This prototype prioritizes low-income citizens."
            )

    elif name == "stand-up india":

        if not (
            _is_woman(citizen)
            or category in {"sc", "st"}
        ):
            reasons.append(
                "This prototype targets women and SC/ST entrepreneurs."
            )

        if occupation != "self-employed":
            reasons.append(
                "Self-employed/enterprise activity is required "
                "for this prototype match."
            )

    # =================================================
    # NATIONAL SOCIAL ASSISTANCE PROGRAMME
    # =================================================

    elif name == "national social assistance programme":

        if not _is_senior(citizen):
            reasons.append(
                "This prototype targets senior citizens."
            )

        if income > 100000:
            reasons.append(
                "This prototype uses a low-income threshold of ₹1,00,000."
            )

    # =================================================
    # RESULT
    # =================================================

    is_eligible = len(reasons) == 0

    if not detailed:
        return is_eligible, reasons

    # Build criteria breakdown for explainability
    age_ok = (scheme.min_age is None or citizen.age >= scheme.min_age) and (scheme.max_age is None or citizen.age <= scheme.max_age)
    income_ok = (scheme.income_limit is None) or (citizen.income is not None and citizen.income <= scheme.income_limit)
    occupation_ok = (not scheme.occupation) or occupation_matches_scheme(citizen, scheme)
    state_ok = (not scheme.state) or (scheme.state.lower() in ["all india", "national", "all", (citizen.state or "").lower()])

    criteria_details = {
        "age": {
            "label": "Age Requirement",
            "passed": age_ok,
            "actual": f"{citizen.age} years",
            "required": f"{scheme.min_age or 0} – {scheme.max_age or 'No upper limit'} years" if (scheme.min_age or scheme.max_age) else "No age restriction",
        },
        "income": {
            "label": "Income Ceiling",
            "passed": income_ok,
            "actual": f"₹{citizen.income:,.0f}" if citizen.income is not None else "₹0",
            "required": f"Maximum ₹{scheme.income_limit:,.0f}" if scheme.income_limit else "No income ceiling",
        },
        "occupation": {
            "label": "Target Occupation",
            "passed": occupation_ok,
            "actual": citizen.occupation or "General",
            "required": scheme.occupation or "Open to all occupations",
        },
        "state": {
            "label": "State Coverage",
            "passed": state_ok,
            "actual": citizen.state or "All India",
            "required": scheme.state or "All India",
        },
    }

    return is_eligible, reasons, criteria_details


def rank_schemes(citizen, schemes):
    """
    Return only potentially matching schemes,
    ranked using transparent prototype scoring.
    """

    ranked = []

    for scheme in schemes:

        eligible, reasons = check_eligibility(
            citizen,
            scheme
        )

        if not eligible:
            continue

        score = 100
        reasons_matched = []

        # Strong profile-to-category matches
        if (
            _is_student(citizen)
            and scheme.category == "Education & Learning"
        ):
            score += 25
            reasons_matched.append("Tailored for student education & scholarships")

        if (
            _is_farmer(citizen)
            and scheme.category == "Agriculture & Rural Development"
        ):
            score += 25
            reasons_matched.append("Directly benefits farmers & rural agriculture")

        if (
            _is_woman(citizen)
            and scheme.category == "Women & Child"
        ):
            score += 20
            reasons_matched.append("Priority scheme for women empowerment")

        if (
            _is_senior(citizen)
            and scheme.category == "Social Security"
        ):
            score += 20
            reasons_matched.append("Social security & pension support for seniors")

        if (
            occupation_matches_scheme(citizen, scheme)
        ):
            score += 15
            reasons_matched.append(f"Direct match for occupation ({citizen.occupation})")

        if (
            citizen.income is not None
            and scheme.income_limit is not None
        ):
            score += 10
            reasons_matched.append("Income qualifies under scheme threshold")

        if not reasons_matched:
            reasons_matched.append("Meets all baseline eligibility criteria")

        match_percentage = min(99, int(round((score / 175.0) * 100)))

        ranked.append(
            {
                "scheme": scheme,
                "eligible": True,
                "score": score,
                "match_percentage": match_percentage,
                "reasons": reasons_matched,
            }
        )

    return sorted(
        ranked,
        key=lambda item: (
            -item["score"],
            item["scheme"].name
        ),
    )


def occupation_matches_scheme(citizen, scheme):
    """
    Only use the Scheme.occupation field as a profile
    occupation restriction when it contains a recognized
    occupation value.

    This avoids treating descriptions such as
    'Eligible bank account holders' as an occupation.
    """

    raw = _normal(scheme.occupation)

    if not raw:
        return False

    known_occupations = {
        "student",
        "farmer",
        "salaried employee",
        "self-employed",
        "unemployed",
        "homemaker",
        "daily wage worker",
        "street vendor",
        "senior citizen",
        "other",
    }

    parts = {
        part.strip()
        for part in raw.replace(";", ",").split(",")
        if part.strip()
    }

    recognized = parts.intersection(known_occupations)

    if not recognized:
        return False

    return _occupation(citizen) in recognized


def generate_analytics_charts(counts, scheme_rows, category_counts):
    """Generate interactive Plotly chart HTML components."""
    charts = {
        "funnel_html": "",
        "scheme_bar_html": "",
        "category_donut_html": "",
    }
    try:
        import plotly.graph_objects as go

        # 1. Funnel Chart
        funnel_fig = go.Figure(
            go.Funnel(
                y=["Eligible", "Aware", "Applied", "Approved", "Received"],
                x=[counts.get(s, 0) for s in ["Eligible", "Aware", "Applied", "Approved", "Received"]],
                textinfo="value+percent initial",
                marker={
                    "color": ["#4338ca", "#4f46e5", "#6366f1", "#059669", "#10b981"]
                },
                connector={"line": {"color": "#cbd5e1", "width": 1.5}},
            )
        )
        funnel_fig.update_layout(
            margin=dict(l=15, r=15, t=30, b=20),
            height=320,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, sans-serif", size=13, color="#27345f"),
        )
        charts["funnel_html"] = funnel_fig.to_html(include_plotlyjs=False, full_html=False)

        # 2. Scheme Comparison Bar Chart
        if scheme_rows:
            top_schemes = scheme_rows[:7]
            names = [s["name"][:25] + ("..." if len(s["name"]) > 25 else "") for s in top_schemes]
            applied = [s["applied"] for s in top_schemes]
            approved = [s["approved"] for s in top_schemes]
            received = [s["received"] for s in top_schemes]

            bar_fig = go.Figure(
                data=[
                    go.Bar(name="Applied", x=names, y=applied, marker_color="#6366f1"),
                    go.Bar(name="Approved", x=names, y=approved, marker_color="#3b82f6"),
                    go.Bar(name="Received", x=names, y=received, marker_color="#10b981"),
                ]
            )
            bar_fig.update_layout(
                barmode="group",
                margin=dict(l=15, r=15, t=30, b=60),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_tickangle=-25,
                font=dict(family="DM Sans, sans-serif", size=12, color="#27345f"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            charts["scheme_bar_html"] = bar_fig.to_html(include_plotlyjs=False, full_html=False)

        # 3. Category Donut Chart
        if category_counts:
            cat_labels = list(category_counts.keys())
            cat_values = list(category_counts.values())
            donut_fig = go.Figure(
                data=[
                    go.Pie(
                        labels=cat_labels,
                        values=cat_values,
                        hole=0.45,
                        marker=dict(colors=["#6366f1", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#06b6d4"]),
                    )
                ]
            )
            donut_fig.update_layout(
                margin=dict(l=15, r=15, t=30, b=20),
                height=320,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans, sans-serif", size=12, color="#27345f"),
                legend=dict(orientation="v", y=0.5, font=dict(size=11)),
            )
            charts["category_donut_html"] = donut_fig.to_html(include_plotlyjs=False, full_html=False)

    except Exception as exc:
        print(f"Chart generation note: {exc}")

    return charts


def analytics_payload(applications):
    counts = {stage: 0 for stage in STAGES}

    scheme_stats_map = {}
    category_counts = {}
    gender_counts = {"Female": 0, "Male": 0, "Other": 0, "Not Specified": 0}
    demographic_flags = {"students": 0, "farmers": 0, "seniors": 0, "women": 0}

    for application in applications:
        stage = (
            application.stage
            if application.stage in STAGES
            else "Eligible"
        )

        index = STAGES.index(stage)

        for previous_stage in STAGES[:index + 1]:
            counts[previous_stage] += 1

        # Scheme-level stats aggregation
        if application.scheme:
            s_name = application.scheme.name
            s_cat = application.scheme.category or "General"
            if s_name not in scheme_stats_map:
                scheme_stats_map[s_name] = {
                    "name": s_name,
                    "category": s_cat,
                    "applied": 0,
                    "approved": 0,
                    "received": 0,
                }
            if stage in ["Applied", "Approved", "Received"]:
                scheme_stats_map[s_name]["applied"] += 1
            if stage in ["Approved", "Received"]:
                scheme_stats_map[s_name]["approved"] += 1
            if stage == "Received":
                scheme_stats_map[s_name]["received"] += 1

            category_counts[s_cat] = category_counts.get(s_cat, 0) + 1

        # Citizen demographic aggregation
        if application.citizen:
            cit = application.citizen
            g = (cit.gender or "").capitalize()
            if g in gender_counts:
                gender_counts[g] += 1
            else:
                gender_counts["Other"] += 1

            if cit.student:
                demographic_flags["students"] += 1
            if cit.farmer:
                demographic_flags["farmers"] += 1
            if cit.senior_citizen or cit.age >= 60:
                demographic_flags["seniors"] += 1
            if cit.woman or (cit.gender or "").lower() == "female":
                demographic_flags["women"] += 1

    gaps = {}
    rates = {}

    for i in range(len(STAGES) - 1):
        current_stage = STAGES[i]
        next_stage = STAGES[i + 1]

        current = counts[current_stage]
        nxt = counts[next_stage]

        key = f"{current_stage}_to_{next_stage}"
        gaps[key] = current - nxt
        rates[key] = (
            round((nxt / current * 100), 1)
            if current
            else 0.0
        )

    # Detailed stage transition objects for rich UI cards
    transition_meta = [
        (
            "Eligible",
            "Aware",
            "Initial Citizen Discovery",
            "Eligible citizens who discover and become informed about the scheme through notifications and recommendations.",
        ),
        (
            "Aware",
            "Applied",
            "Application Initiation",
            "Informed citizens who review requirements and proceed to submit an official scheme application.",
        ),
        (
            "Applied",
            "Approved",
            "Administrative Verification",
            "Submitted applications verified and officially approved by administering department authorities.",
        ),
        (
            "Approved",
            "Received",
            "Last-Mile Benefit Delivery",
            "Approved beneficiaries who successfully receive DBT funds, subsidies, or services in their account.",
        ),
    ]

    stage_transitions = []
    for cur_s, nxt_s, label, desc in transition_meta:
        k = f"{cur_s}_to_{nxt_s}"
        c_from = counts.get(cur_s, 0)
        c_to = counts.get(nxt_s, 0)
        gap = gaps.get(k, 0)
        rate = rates.get(k, 0.0)
        drop_rate = round(100.0 - rate, 1) if c_from > 0 else 0.0

        stage_transitions.append(
            {
                "from_stage": cur_s,
                "to_stage": nxt_s,
                "label": label,
                "description": desc,
                "from_count": c_from,
                "to_count": c_to,
                "drop_count": gap,
                "conversion_rate": rate,
                "drop_rate": drop_rate,
            }
        )

    largest_gap = max(
        gaps.items(),
        key=lambda item: item[1],
        default=(None, 0),
    )

    # Bottleneck diagnosis and policy recommendations
    stage_bottleneck = largest_gap[0] or "Applied_to_Approved"
    analysis_text = ""
    recommendation_text = ""

    if stage_bottleneck == "Applied_to_Approved":
        analysis_text = (
            "The primary bottleneck is in the Administrative Verification stage. "
            "Citizens are actively applying, but verification delays, manual document audits, "
            "or department processing backlog prevent timely approvals."
        )
        recommendation_text = (
            "Implement automated Aadhaar/document pre-verification, establish departmental processing SLAs, "
            "and alert administrators of pending review queues to accelerate verification turnaround."
        )
    elif stage_bottleneck == "Aware_to_Applied":
        analysis_text = (
            "Citizens explore schemes but drop out prior to application submission. "
            "This highlights friction in application complexity, lack of document readiness, or unclear instructions."
        )
        recommendation_text = (
            "Provide one-click pre-filled application forms, direct links to state CSC centers, and checklist guidance."
        )
    elif stage_bottleneck == "Eligible_to_Aware":
        analysis_text = (
            "A notable portion of eligible citizens have not explored suitable schemes, indicating an awareness gap."
        )
        recommendation_text = (
            "Expand multichannel notifications (SMS, WhatsApp, Email) and regional awareness campaigns."
        )
    elif stage_bottleneck == "Approved_to_Received":
        analysis_text = (
            "Applications are approved, but benefit delivery confirmation remains incomplete."
        )
        recommendation_text = (
            "Verify Aadhaar-linked DBT bank accounts, establish real-time payment tracking, and conduct disbursement audits."
        )
    else:
        analysis_text = "Pipeline flow is balanced across stages with minimal drop-off."
        recommendation_text = "Continue monitoring real-time intake and stage transitions."

    # Format scheme rows sorted by applied descending
    scheme_rows = sorted(
        scheme_stats_map.values(),
        key=lambda s: (-s["applied"], -s["approved"], s["name"]),
    )
    for s in scheme_rows:
        s["conversion_rate"] = (
            round((s["received"] / s["applied"] * 100), 1)
            if s["applied"] > 0
            else 0.0
        )

    charts = generate_analytics_charts(counts, scheme_rows, category_counts)

    overall_conversion = (
        round((counts["Received"] / counts["Eligible"] * 100), 1)
        if counts["Eligible"] > 0
        else 0.0
    )

    return {
        "stages": STAGES,
        "counts": counts,
        "gaps": gaps,
        "conversion_rates": rates,
        "overall_conversion_rate": overall_conversion,
        "largest_gap": {
            "stage": stage_bottleneck,
            "count": largest_gap[1],
            "analysis": analysis_text,
            "recommendation": recommendation_text,
        },
        "stage_transitions": stage_transitions,
        "scheme_rows": scheme_rows,
        "category_counts": category_counts,
        "gender_counts": gender_counts,
        "demographic_flags": demographic_flags,
        "charts": charts,
        "total_applications": len(applications),
    }


def log_activity(event_type, user_id=None, description=None, metadata=None, ip_address=None):
    """Safely log an activity event into the database."""
    try:
        from . import db
        from .models import ActivityLog
        meta_str = None
        if metadata is not None:
            if isinstance(metadata, (dict, list)):
                meta_str = json.dumps(metadata)
            else:
                meta_str = str(metadata)

        log = ActivityLog(
            user_id=user_id,
            event_type=event_type,
            description=description,
            metadata_json=meta_str,
            ip_address=ip_address,
        )
        db.session.add(log)
        db.session.commit()
    except Exception as exc:
        try:
            from . import db
            db.session.rollback()
        except Exception:
            pass


def admin_overview():
    """
    Generate comprehensive admin metrics from actual database records:
    - Registered user accounts with last login information (no password hashes exposed).
    - Schemes overview and status counts.
    - Application overview by stage.
    - User engagement and interaction events.
    - Explicit distinction between historical records and newly tracked activity events.
    """
    from . import db
    from .models import User, Scheme, Application, LoginLog, ActivityLog, STAGES

    # 1. Registered Users Overview
    users = User.query.order_by(User.created_at.desc()).all()
    user_rows = []
    for u in users:
        last_login_record = (
            LoginLog.query.filter_by(username=u.email)
            .order_by(LoginLog.logged_in_at.desc())
            .first()
        )
        last_login_dt = last_login_record.logged_in_at if last_login_record else None

        user_rows.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "created_at": u.created_at,
            "last_login": last_login_dt,
            "has_profile": u.citizen_id is not None,
        })

    # 2. Scheme Overview
    total_schemes = Scheme.query.count()
    active_schemes = Scheme.query.filter_by(active=True).count()
    inactive_schemes = total_schemes - active_schemes
    categories_raw = (
        db.session.query(Scheme.category, func.count(Scheme.id))
        .group_by(Scheme.category)
        .all()
    )
    categories_count = {cat: count for cat, count in categories_raw if cat}

    # 3. Application Overview
    total_applications = Application.query.count()
    app_stage_counts = {stage: 0 for stage in STAGES}
    stage_counts_raw = (
        db.session.query(Application.stage, func.count(Application.id))
        .group_by(Application.stage)
        .all()
    )
    for st, count in stage_counts_raw:
        app_stage_counts[st] = count

    # 4. User Engagement & Activity Logs
    recent_activities = (
        ActivityLog.query.order_by(ActivityLog.created_at.desc())
        .limit(25)
        .all()
    )
    activity_rows = []
    for act in recent_activities:
        user_label = act.user.name if act.user else "Anonymous / Guest"
        activity_rows.append({
            "id": act.id,
            "user_label": user_label,
            "event_type": act.event_type,
            "description": act.description or "",
            "ip_address": act.ip_address,
            "created_at": act.created_at,
        })

    # Aggregated interaction counts
    event_counts_raw = (
        db.session.query(ActivityLog.event_type, func.count(ActivityLog.id))
        .group_by(ActivityLog.event_type)
        .all()
    )
    event_counts = {evt: count for evt, count in event_counts_raw}

    return {
        "registered_users": user_rows,
        "total_users": len(user_rows),
        "total_schemes": total_schemes,
        "active_schemes": active_schemes,
        "inactive_schemes": inactive_schemes,
        "categories_count": categories_count,
        "total_applications": total_applications,
        "application_stage_counts": app_stage_counts,
        "recent_activities": activity_rows,
        "event_counts": event_counts,
        "historical_distinction": {
            "historical_data_available": True,
            "note": (
                "Registered users, applications, and historical login entries are derived from existing database records. "
                "Granular user interaction metrics (scheme searches, detail views, failed attempts) are actively tracked from when activity logging was introduced."
            )
        }
    }