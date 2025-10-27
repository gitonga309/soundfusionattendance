#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput
python manage.py migrate

# Auto-create admin user if not exists
echo "=== Creating default admin user ==="
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@soundfusion.com', 'soundfusion123')
    print('✅ Default admin user created!')
    print('   Username: admin')
    print('   Password: soundfusion123')
    print('   Email: admin@soundfusion.com')
else:
    print('ℹ️ Admin user already exists')
"
echo "=== Admin setup complete ==="