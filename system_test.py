#!/usr/bin/env python
"""
Comprehensive system test for Sound Fusion Limited Attendance System
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundfusion_attendance.settings')
django.setup()

from django.db import connection
from django.apps import apps
from attendance.models import User, AttendanceRecord, Event, Profile, BalanceAdjustment

def test_database():
    """Test database connectivity"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True, "Database connection OK"
    except Exception as e:
        return False, f"Database error: {e}"

def test_migrations():
    """Check all migrations are applied"""
    from django.db.migrations.executor import MigrationExecutor
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    if not plan:
        return True, "All migrations applied"
    return False, f"Pending migrations: {plan}"

def test_models():
    """Verify all models exist and are accessible"""
    models_to_test = [User, Profile, AttendanceRecord, Event, BalanceAdjustment]
    errors = []
    for model in models_to_test:
        try:
            model.objects.count()
        except Exception as e:
            errors.append(f"{model.__name__}: {e}")
    
    if errors:
        return False, ", ".join(errors)
    return True, f"All {len(models_to_test)} models accessible"

def test_urls():
    """Check URLs configuration"""
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        patterns = resolver.url_patterns
        return True, f"URLs configured ({len(patterns)} patterns)"
    except Exception as e:
        return False, f"URL error: {e}"

def test_forms():
    """Check forms can be imported"""
    try:
        from attendance.forms import (
            UserRegisterForm, AttendanceForm, EventForm
        )
        return True, "All forms importable"
    except Exception as e:
        return False, f"Form import error: {e}"

def test_views():
    """Check views can be imported"""
    try:
        from attendance import views
        view_funcs = [
            'home', 'register', 'user_login', 'user_logout', 'dashboard',
            'view_attendance', 'mark_attendance', 'edit_attendance',
            'admin_dashboard'
        ]
        missing = [v for v in view_funcs if not hasattr(views, v)]
        if missing:
            return False, f"Missing views: {missing}"
        return True, f"All {len(view_funcs)} views accessible"
    except Exception as e:
        return False, f"View import error: {e}"

def test_templates():
    """Check core templates exist"""
    import os
    template_dir = 'attendance/templates/attendance'
    required_templates = [
        'home.html', 'register.html', 'login.html', 'dashboard.html',
        'view_attendance.html', 'mark_attendance.html', 'admin_dashboard.html'
    ]
    missing = []
    for template in required_templates:
        path = os.path.join(template_dir, template)
        if not os.path.exists(path):
            missing.append(template)
    
    if missing:
        return False, f"Missing templates: {missing}"
    return True, f"All {len(required_templates)} core templates exist"

def test_settings():
    """Check critical settings"""
    from django.conf import settings
    errors = []
    
    if not settings.DEBUG:
        errors.append("DEBUG is False (set to True for development)")
    if not settings.ALLOWED_HOSTS or '*' not in settings.ALLOWED_HOSTS:
        if '127.0.0.1' not in settings.ALLOWED_HOSTS:
            errors.append("ALLOWED_HOSTS may need '127.0.0.1'")
    if not settings.INSTALLED_APPS or 'attendance' not in settings.INSTALLED_APPS:
        errors.append("'attendance' app not installed")
    if not settings.DATABASES:
        errors.append("No databases configured")
    
    if errors:
        return False, "; ".join(errors)
    return True, "Settings configured correctly"

def main():
    """Run all tests"""
    print("=" * 60)
    print("SOUND FUSION LIMITED - SYSTEM DIAGNOSTIC TEST")
    print("=" * 60 + "\n")
    
    tests = [
        ("Database Connection", test_database),
        ("Migrations", test_migrations),
        ("Models", test_models),
        ("URLs", test_urls),
        ("Forms", test_forms),
        ("Views", test_views),
        ("Templates", test_templates),
        ("Settings", test_settings),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            success, message = test_func()
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} | {test_name}: {message}")
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ FAIL | {test_name}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ SYSTEM READY FOR USE")
        return 0
    else:
        print("⚠️  SYSTEM HAS ISSUES - FIX BEFORE DEPLOYMENT")
        return 1

if __name__ == '__main__':
    sys.exit(main())
