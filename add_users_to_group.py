from django.contrib.auth.models import User, Group

# Get the Events Manager group
try:
    group = Group.objects.get(name='Events Manager')
    print(f"✓ Found 'Events Manager' group")
except Group.DoesNotExist:
    print("✗ Events Manager group not found!")
    exit()

# List all non-superuser users
users = User.objects.filter(is_superuser=False)

print(f"\n✓ Found {users.count()} regular users:")
for user in users:
    print(f"  - {user.username} (email: {user.email})")
    
# Add all non-admin users to the group
for user in users:
    user.groups.add(group)
    print(f"✓ Added {user.username} to Events Manager group")

print(f"\n✓ All users can now login to admin panel as Events Manager!")
print(f"✓ Groups for users: {list(User.objects.filter(is_superuser=False).values_list('username', flat=True))}")
