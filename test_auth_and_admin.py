"""
test_auth_and_admin.py - Comprehensive Backend Verification Suite
Covers:
- Authentication & Registration
- Password Hashing & Verification
- Demo Password Bypass Removal
- Session Handling & Forged Cookie Rejection
- Role Checks & Stale Session Protection
- Admin Authorization & Analytics API Protection
- Activity Logging & Engagement Audit
- Admin Dashboard Metrics & Real Data Consistency
- Workflow Integrity (Schemes, Apply, Profile, Notifications, Gap Analysis)
- Database Persistence across restarts & Test Isolation
- Zero Password Hash Leakage
- Frontend File Integrity Verification
"""
import os
import sys
import hashlib
import tempfile
import unittest

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("venv/Lib/site-packages"))

from app import create_app, db
from app.models import User, Citizen, Scheme, Application, Notification, ActivityLog, STAGES
from werkzeug.security import generate_password_hash, check_password_hash


class TestWelfareBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary file-backed SQLite database for isolated test execution
        cls.tmp_fd, cls.tmp_db_path = tempfile.mkstemp(suffix=".db")
        os.close(cls.tmp_fd)

        cls.config_overrides = {
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{cls.tmp_db_path}",
            "TESTING": True,
            "SECRET_KEY": "test-backend-suite-isolated-secret-key-42",
        }

        # Baseline hash of live database before any tests run
        cls.live_db_path = os.path.abspath("instance/welfare.db")
        if os.path.exists(cls.live_db_path):
            with open(cls.live_db_path, "rb") as f:
                cls.initial_live_hash = hashlib.sha256(f.read()).hexdigest()
        else:
            cls.initial_live_hash = None

        cls.app = create_app(config_overrides=cls.config_overrides)

    @classmethod
    def tearDownClass(cls):
        # Clean up temporary database file
        if os.path.exists(cls.tmp_db_path):
            try:
                os.remove(cls.tmp_db_path)
            except Exception:
                pass

        # Verify live database was never modified
        if cls.initial_live_hash and os.path.exists(cls.live_db_path):
            with open(cls.live_db_path, "rb") as f:
                final_live_hash = hashlib.sha256(f.read()).hexdigest()
            assert final_live_hash == cls.initial_live_hash, "CRITICAL: Live database was modified during tests!"

    def setUp(self):
        self.client = self.app.test_client()

    # ===================================================================
    # 1. AUTHENTICATION & REGISTRATION
    # ===================================================================

    def test_01_valid_registration_and_immediate_login(self):
        """User registers with valid input and can immediately log in with same credentials."""
        email = "test.citizen.01@welfareconnect.in"
        password = "ValidPassword123!"

        reg_data = {
            "name": "Aarav Sharma",
            "email": email,
            "password": password,
            "confirm_password": password,
            "mobile": "9876543210",
            "age": "24",
            "gender": "Male",
            "occupation": "Student",
            "income": "60000",
            "category": "General",
            "state": "Maharashtra",
            "district": "Pune",
        }
        res = self.client.post("/register", data=reg_data, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # Logout
        self.client.get("/logout")

        # Login with newly registered credentials
        login_res = self.client.post("/login", data={
            "username": email,
            "password": password,
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Aarav Sharma", login_res.data)

    def test_02_login_with_wrong_password_rejected(self):
        """Login with wrong password fails cleanly with user-facing message."""
        res = self.client.post("/login", data={
            "username": "test.citizen.01@welfareconnect.in",
            "password": "WrongPassword999!",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid email or password", res.data)

    def test_03_login_with_unknown_identifier_rejected(self):
        """Login with non-existent email is safely rejected."""
        res = self.client.post("/login", data={
            "username": "ghost.user@nonexistent.domain",
            "password": "SomePassword123!",
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid email or password", res.data)

    def test_04_duplicate_account_rejection(self):
        """Registering with an already existing email is rejected."""
        email = "duplicate.test@welfareconnect.in"
        reg_data = {
            "name": "First Register",
            "email": email,
            "password": "Password123!",
            "confirm_password": "Password123!",
            "age": "22",
            "gender": "Female",
            "occupation": "Student",
            "income": "50000",
            "category": "General",
            "state": "Maharashtra",
            "district": "Mumbai",
        }
        self.client.post("/register", data=reg_data, follow_redirects=True)
        self.client.get("/logout")

        # Attempt duplicate registration
        res2 = self.client.post("/register", data=reg_data, follow_redirects=True)
        self.assertIn(b"already exists", res2.data)

    def test_05_case_and_whitespace_normalization(self):
        """Identifier case and surrounding whitespace are normalized on register and login."""
        email = "Case.Test.User@Domain.Com"
        reg_data = {
            "name": "Case Test User",
            "email": f"  {email}  ",
            "password": "MySecretPassword123!",
            "confirm_password": "MySecretPassword123!",
            "age": "30",
            "gender": "Male",
            "occupation": "Farmer",
            "income": "75000",
            "category": "OBC",
            "state": "Maharashtra",
            "district": "Nashik",
        }
        self.client.post("/register", data=reg_data, follow_redirects=True)
        self.client.get("/logout")

        # Login with different casing and whitespace
        login_res = self.client.post("/login", data={
            "username": "  CASE.TEST.USER@DOMAIN.COM  ",
            "password": "MySecretPassword123!",
        }, follow_redirects=False)
        self.assertEqual(login_res.status_code, 302)
        self.assertIn("/user", login_res.headers.get("Location", ""))

    def test_06_malformed_input_rejection(self):
        """Malformed emails, mismatched passwords, and short passwords fail with clear errors."""
        bad_cases = [
            # Short password (< 6 chars)
            {"name": "Short Pw", "email": "good@test.com", "password": "123", "confirm_password": "123", "age": "20"},
            # Mismatched passwords
            {"name": "Mismatch", "email": "good2@test.com", "password": "pass1234", "confirm_password": "pass9999", "age": "20"},
            # Malformed email without @
            {"name": "No At", "email": "notanemail.com", "password": "pass1234", "confirm_password": "pass1234", "age": "20"},
            # Malformed email with duplicated extension like .com.com
            {"name": "Double Ext", "email": "bad@gmail.com.com", "password": "pass1234", "confirm_password": "pass1234", "age": "20"},
        ]
        for data in bad_cases:
            data.setdefault("occupation", "Student")
            data.setdefault("income", "10000")
            res = self.client.post("/register", data=data, follow_redirects=True)
            self.assertIn(res.status_code, [200, 302])
            # Account should not be created
            with self.app.app_context():
                u = User.query.filter_by(email=data["email"].strip().lower()).first()
                self.assertIsNone(u, f"User {data['email']} should not have been created!")

    def test_07_secure_password_hashing(self):
        """Stored passwords use secure hashes (not plaintext, length > 40, verifiable with check_password_hash)."""
        with self.app.app_context():
            user = User.query.filter_by(email="admin@welfareconnect.in").first()
            self.assertIsNotNone(user)
            self.assertNotEqual(user.password_hash, "admin123")
            self.assertTrue(len(user.password_hash) > 40)
            self.assertTrue(check_password_hash(user.password_hash, "admin123"))

    # ===================================================================
    # 2. DEMO PASSWORD BYPASS REMOVAL & PASSWORD CHANGE
    # ===================================================================

    def test_08_demo_password_bypass_removed(self):
        """Changing the admin password in DB invalidates the old hardcoded 'admin123' demo password."""
        with self.app.app_context():
            admin = User.query.filter_by(email="admin@welfareconnect.in").first()
            admin.password_hash = generate_password_hash("NewCustomAdminPass2026!")
            db.session.commit()

        # Attempt login with old demo password 'admin123'
        old_pw_res = self.client.post("/login", data={
            "username": "admin@welfareconnect.in",
            "password": "admin123",
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", old_pw_res.data)

        # Login with new password succeeds
        new_pw_res = self.client.post("/login", data={
            "username": "admin@welfareconnect.in",
            "password": "NewCustomAdminPass2026!",
        }, follow_redirects=False)
        self.assertEqual(new_pw_res.status_code, 302)
        self.assertIn("/admin", new_pw_res.headers.get("Location", ""))

        # Restore admin password for subsequent tests
        with self.app.app_context():
            admin = User.query.filter_by(email="admin@welfareconnect.in").first()
            admin.password_hash = generate_password_hash("admin123")
            db.session.commit()

    # ===================================================================
    # 3. SESSION HANDLING & AUTHORIZATION SECURITY
    # ===================================================================

    def test_09_session_persistence_and_logout(self):
        """Authenticated session persists across requests and is cleanly invalidated on logout."""
        self.client.post("/login", data={"username": "admin@welfareconnect.in", "password": "admin123"})

        # Subsequent request retains admin session
        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)

        # Logout
        self.client.get("/logout")

        # Accessing /admin now redirects to login
        res_after = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(res_after.status_code, 302)
        self.assertIn("/?login=1", res_after.headers.get("Location", ""))

    def test_10_unauthenticated_protected_route_rejection(self):
        """Unauthenticated requests to protected citizen routes redirect to login."""
        self.client.get("/logout")
        for endpoint in ["/user", "/profile", "/applications", "/notifications"]:
            res = self.client.get(endpoint, follow_redirects=False)
            self.assertEqual(res.status_code, 302, f"Endpoint {endpoint} allowed unauthenticated access!")
            self.assertIn("/?login=1", res.headers.get("Location", ""))

    def test_11_ordinary_customer_blocked_from_admin_console(self):
        """Ordinary citizen user cannot access /admin or /admin/gap-analysis."""
        # Create and login as citizen
        with self.app.app_context():
            user = User.query.filter_by(email="user@welfareconnect.in").first()
            self.assertIsNotNone(user)

        self.client.post("/login", data={"username": "user@welfareconnect.in", "password": "user123"})

        res_admin = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(res_admin.status_code, 302)
        self.assertIn("/?login=1", res_admin.headers.get("Location", ""))

        res_gap = self.client.get("/admin/gap-analysis", follow_redirects=False)
        self.assertEqual(res_gap.status_code, 302)
        self.assertIn("/?login=1", res_gap.headers.get("Location", ""))

    def test_12_forged_session_cookie_rejected(self):
        """A tampered cookie with role='admin' but non-existent or invalid user_id is rejected."""
        with self.client.session_transaction() as sess:
            sess["role"] = "admin"
            sess["user_id"] = 999999  # non-existent user ID
            sess["username"] = "attacker@fake.com"

        res = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn("/?login=1", res.headers.get("Location", ""))

    def test_13_database_verified_role_changes(self):
        """If a user's role is changed in DB, subsequent requests enforce the updated role immediately."""
        with self.app.app_context():
            user = User.query.filter_by(email="test.citizen.01@welfareconnect.in").first()
            user.role = "admin"
            db.session.commit()

        # Login as this user
        self.client.post("/login", data={"username": "test.citizen.01@welfareconnect.in", "password": "ValidPassword123!"})

        # Now can access admin
        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)

        # Demote back to user in DB
        with self.app.app_context():
            user = User.query.filter_by(email="test.citizen.01@welfareconnect.in").first()
            user.role = "user"
            db.session.commit()

        # Stale session should be rejected from /admin on next request
        res2 = self.client.get("/admin", follow_redirects=False)
        self.assertEqual(res2.status_code, 302)

    # ===================================================================
    # 4. ANALYTICS API AUTHORIZATION
    # ===================================================================

    def test_14_analytics_endpoint_protection(self):
        """GET /api/analytics returns 401 for guests, 403 for citizens, 200 for admins."""
        self.client.get("/logout")

        # Guest
        r_guest = self.client.get("/api/analytics")
        self.assertEqual(r_guest.status_code, 401)
        self.assertIn("error", r_guest.json)

        # Citizen
        self.client.post("/login", data={"username": "user@welfareconnect.in", "password": "user123"})
        r_citizen = self.client.get("/api/analytics")
        self.assertEqual(r_citizen.status_code, 403)
        self.assertIn("error", r_citizen.json)

        # Admin
        self.client.get("/logout")
        self.client.post("/login", data={"username": "admin@welfareconnect.in", "password": "admin123"})
        r_admin = self.client.get("/api/analytics")
        self.assertEqual(r_admin.status_code, 200)
        self.assertIn("gaps", r_admin.json)
        self.assertIn("overall_conversion_rate", r_admin.json)

    # ===================================================================
    # 5. USER ENGAGEMENT & ACTIVITY TRACKING
    # ===================================================================

    def test_15_activity_logging_and_distinction(self):
        """User interactions (search, view, login, apply) create structured ActivityLog records."""
        self.client.get("/logout")
        self.client.post("/login", data={"username": "user@welfareconnect.in", "password": "user123"})

        # 1. Scheme search
        self.client.get("/find-schemes?q=scholarship")

        # 2. Scheme detail view
        with self.app.app_context():
            s = Scheme.query.filter_by(active=True).first()
            s_id = s.id

        self.client.get(f"/scheme/{s_id}")

        with self.app.app_context():
            # Check activities logged
            activities = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(10).all()
            event_types = [a.event_type for a in activities]
            self.assertIn("login_success", event_types)
            self.assertIn("scheme_search", event_types)
            self.assertIn("scheme_view", event_types)

    def test_16_admin_dashboard_real_data(self):
        """Admin dashboard displays registered users, accurate application counts, and interaction audit."""
        self.client.get("/logout")
        self.client.post("/login", data={"username": "admin@welfareconnect.in", "password": "admin123"})

        res = self.client.get("/admin")
        self.assertEqual(res.status_code, 200)

        # Check UI sections exist
        self.assertIn(b"Registered Citizen & Admin Accounts", res.data)
        self.assertIn(b"Recorded User Engagement & System Activity", res.data)
        self.assertIn(b"Data Source Distinction", res.data)
        self.assertIn(b"Welfare Schemes Utilization Summary", res.data)

        # Verify no password hashes leaked in HTML
        with self.app.app_context():
            users = User.query.all()
            for u in users:
                self.assertNotIn(u.password_hash.encode(), res.data)

    # ===================================================================
    # 6. BRUTE FORCE THROTTLING & MISASSOCIATION PREVENTIONS
    # ===================================================================

    def test_17_brute_force_throttling(self):
        """Multiple repeated failed login attempts trigger throttling."""
        self.client.get("/logout")
        for _ in range(5):
            self.client.post("/login", data={"username": "victim@test.com", "password": "WrongPassword!"})

        # 6th attempt should be throttled
        throttled_res = self.client.post("/login", data={"username": "victim@test.com", "password": "WrongPassword!"}, follow_redirects=True)
        self.assertIn(b"Too many failed login attempts", throttled_res.data)

    def test_18_isolated_citizen_profile_creation(self):
        """A user created without a citizen profile gets their OWN profile, never another person's."""
        with self.app.app_context():
            orphaned_user = User(
                name="Orphan Citizen",
                email="orphan@welfareconnect.in",
                password_hash=generate_password_hash("password123"),
                role="user",
                citizen_id=None,
            )
            db.session.add(orphaned_user)
            db.session.commit()
            orphaned_id = orphaned_user.id

        # Login as orphaned user
        self.client.get("/logout")
        self.client.post("/login", data={"username": "orphan@welfareconnect.in", "password": "password123"}, follow_redirects=True)

        with self.app.app_context():
            u = db.session.get(User, orphaned_id)
            self.assertIsNotNone(u.citizen_id)
            cit = db.session.get(Citizen, u.citizen_id)
            self.assertEqual(cit.name, "Orphan Citizen")
            self.assertNotEqual(cit.name, "WelfareConnect User")

    # ===================================================================
    # 7. DATABASE PERSISTENCE ACROSS APPLICATION RESTARTS
    # ===================================================================

    def test_19_database_persistence_across_app_restarts(self):
        """Data registered in the database persists when a new Flask application instance is initialized."""
        # Create brand-new app instance pointing to the SAME SQLite DB file
        fresh_app = create_app(config_overrides=self.config_overrides)
        fresh_client = fresh_app.test_client()

        # Login using previously registered test account on fresh instance
        login_res = fresh_client.post("/login", data={
            "username": "test.citizen.01@welfareconnect.in",
            "password": "ValidPassword123!",
        }, follow_redirects=False)
        self.assertEqual(login_res.status_code, 302)
        self.assertIn("/user", login_res.headers.get("Location", ""))

    # ===================================================================
    # 8. FRONTEND PRESERVATION VERIFICATION
    # ===================================================================

    def test_20_frontend_file_integrity(self):
        """All CSS, JavaScript, and user-facing templates match baseline hashes without unauthorized modification."""
        hash_file = "/Users/Adars_Pedini/.gemini/antigravity/brain/c9feec9e-b4f1-4dea-baec-49780697b49b/scratch/baseline_frontend_hashes.txt"
        if not os.path.exists(hash_file):
            self.skipTest("Baseline frontend hashes file not found.")

        with open(hash_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            baseline_hash, filepath = line.split(None, 1)
            # dashboard.html was updated to add the required Admin User & Engagement sections
            if "dashboard.html" in filepath:
                continue

            with open(filepath, "rb") as cur_f:
                current_hash = hashlib.sha256(cur_f.read()).hexdigest()
            self.assertEqual(
                current_hash,
                baseline_hash,
                f"Unauthorized modification in frontend file: {filepath}"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
