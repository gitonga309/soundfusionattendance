#!/usr/bin/env python
"""
Test script to verify timezone handling in Django
Run with: python manage.py shell < test_timezone.py
Or in Django shell: exec(open('test_timezone.py').read())
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'soundfusion_attendance.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
import datetime

print("=" * 60)
print("TIMEZONE CONFIGURATION TEST")
print("=" * 60)
print(f"\nTIME_ZONE setting: {settings.TIME_ZONE}")
print(f"USE_TZ setting: {settings.USE_TZ}")

print("\n" + "=" * 60)
print("CURRENT TIME TESTS")
print("=" * 60)

# Test 1: timezone.now()
now_aware = timezone.now()
print(f"\n1. timezone.now() (aware):")
print(f"   Value: {now_aware}")
print(f"   Timezone: {now_aware.tzinfo}")

# Test 2: timezone.now().time()
now_time = timezone.now().time()
print(f"\n2. timezone.now().time():")
print(f"   Value: {now_time}")

# Test 3: Converted to local timezone
now_local = timezone.now().astimezone(timezone.get_current_timezone())
print(f"\n3. timezone.now().astimezone(get_current_timezone()):")
print(f"   Value: {now_local}")
print(f"   Timezone: {now_local.tzinfo}")

# Test 4: Converted time
now_local_time = now_local.time()
print(f"\n4. astimezone().time():")
print(f"   Value: {now_local_time}")

# Test 5: Create datetime with date and time
test_date = datetime.date(2025, 1, 26)
test_time = datetime.time(9, 39, 0)
combined_naive = datetime.datetime.combine(test_date, test_time)
print(f"\n5. datetime.combine(date, time):")
print(f"   Value: {combined_naive}")
print(f"   Is naive: {combined_naive.tzinfo is None}")

combined_aware = timezone.make_aware(combined_naive, timezone=timezone.get_current_timezone())
print(f"\n6. make_aware(combined_datetime):")
print(f"   Value: {combined_aware}")
print(f"   Timezone: {combined_aware.tzinfo}")

print("\n" + "=" * 60)
print("EXPECTED: If you see 9:39 AM above, timezone is configured correctly!")
print("=" * 60)
