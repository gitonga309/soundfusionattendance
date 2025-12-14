# Getting Started with Phase 2: Client Management

## Quick Start Guide

If you want to start building Phase 2 features, here's the simplest path forward:

---

## Step 1: Create Client Model (30 minutes)

Add to `attendance/models.py`:

```python
class Client(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    company = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.company or 'Individual'}"

    class Meta:
        ordering = ['-created_at']
```

**Then:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Step 2: Register in Admin (10 minutes)

Add to `attendance/admin.py`:

```python
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'phone', 'created_at')
    search_fields = ('name', 'company', 'email')
    list_filter = ('created_at', 'city')
    ordering = ('-created_at',)
```

---

## Step 3: Create Basic Client Views (1 hour)

Add to `attendance/views.py`:

```python
@login_required
@user_passes_test(is_admin)
def client_list(request):
    """List all clients"""
    clients = Client.objects.all()
    search = request.GET.get('search', '')
    
    if search:
        clients = clients.filter(
            models.Q(name__icontains=search) |
            models.Q(company__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    return render(request, 'attendance/client_list.html', {
        'clients': clients,
        'search': search
    })

@login_required
@user_passes_test(is_admin)
def client_detail(request, client_id):
    """View individual client details"""
    client = get_object_or_404(Client, pk=client_id)
    return render(request, 'attendance/client_detail.html', {'client': client})

@login_required
@user_passes_test(is_admin)
def client_create(request):
    """Create new client"""
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client added successfully!")
            return redirect('client_list')
    else:
        form = ClientForm()
    
    return render(request, 'attendance/client_form.html', {'form': form})
```

---

## Step 4: Create Client Form (20 minutes)

New file: `attendance/forms.py` (add to existing):

```python
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'company', 'address', 'city', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
```

---

## Step 5: Add URLs (10 minutes)

Add to `attendance/urls.py`:

```python
path('clients/', views.client_list, name='client_list'),
path('clients/<int:client_id>/', views.client_detail, name='client_detail'),
path('clients/create/', views.client_create, name='client_create'),
```

---

## Step 6: Create Templates (1 hour)

**File: `attendance/templates/attendance/client_list.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clients | Sound Fusion</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f7fa; }
        
        .navbar {
            background: linear-gradient(135deg, #0d2818 0%, #000 100%);
            padding: 1.2rem 2rem;
            color: #fff;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .container { max-width: 1000px; margin: 2rem auto; padding: 0 2rem; }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .btn-add {
            background: #2ecc71;
            color: #fff;
            padding: 0.7rem 1.5rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
        }
        
        .btn-add:hover { background: #27ae60; }
        
        .search-box {
            margin-bottom: 2rem;
        }
        
        .search-box input {
            width: 100%;
            padding: 0.8rem;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 1rem;
        }
        
        .client-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        
        .client-card {
            background: #fff;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            border-left: 5px solid #2ecc71;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .client-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(46, 204, 113, 0.15);
        }
        
        .client-card h3 { color: #0d2818; margin-bottom: 0.5rem; }
        .client-card p { color: #666; font-size: 0.9rem; margin: 0.3rem 0; }
        .client-card a { color: #2ecc71; text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>
    <div class="navbar">
        <h1><i class="fas fa-users"></i> Clients</h1>
        <a href="{% url 'logout' %}" class="btn-add">Logout</a>
    </div>
    
    <div class="container">
        <div class="header">
            <h2>All Clients</h2>
            <a href="{% url 'client_create' %}" class="btn-add">
                <i class="fas fa-plus"></i> Add Client
            </a>
        </div>
        
        <div class="search-box">
            <form method="GET">
                <input type="text" name="search" placeholder="Search clients..." value="{{ search }}">
            </form>
        </div>
        
        {% if clients %}
            <div class="client-grid">
                {% for client in clients %}
                <div class="client-card">
                    <h3>{{ client.name }}</h3>
                    <p><strong>Company:</strong> {{ client.company|default:"Individual" }}</p>
                    <p><strong>Email:</strong> <a href="mailto:{{ client.email }}">{{ client.email }}</a></p>
                    <p><strong>Phone:</strong> {{ client.phone }}</p>
                    <p style="margin-top: 1rem;">
                        <a href="{% url 'client_detail' client.id %}">View Details →</a>
                    </p>
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div style="text-align: center; padding: 3rem; background: #fff; border-radius: 10px;">
                <p style="color: #999;">No clients yet. <a href="{% url 'client_create' %}">Create one</a></p>
            </div>
        {% endif %}
    </div>
</body>
</html>
```

---

## Quick Wins to Add Now (No Extra Models)

### **1. Event Type Tagging**
Add to `AttendanceRecord`:
```python
EVENT_TYPES = [
    ('wedding', 'Wedding'),
    ('corporate', 'Corporate'),
    ('concert', 'Concert'),
    ('other', 'Other'),
]
event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
```

### **2. Worker Availability**
Add to `Profile`:
```python
available_dates = models.TextField(blank=True)  # JSON field for future events
preferred_roles = models.CharField(max_length=200, blank=True)
```

### **3. Event Notes**
Already in `AttendanceRecord.event` - use it for event details!

---

## Testing Your Client Feature

1. Create a superuser if needed:
```bash
python manage.py createsuperuser
```

2. Go to Django admin:
```
http://127.0.0.1:8000/admin/
```

3. Add some clients manually first

4. Test the views at:
```
http://127.0.0.1:8000/clients/
```

---

## Next Steps After Phase 2

Once clients work smoothly:
1. Add Events (link to clients)
2. Add EventAssignments (link events to workers)
3. Add event status tracking
4. Integrate SMS updates
5. Build client portal

---

## Resources

**Django Documentation:**
- Forms: https://docs.djangoproject.com/en/5.1/topics/forms/
- Admin: https://docs.djangoproject.com/en/5.1/ref/contrib/admin/
- Models: https://docs.djangoproject.com/en/5.1/topics/db/models/

**Africa's Talking SMS (When ready):**
- https://africastalking.com/

---

Good luck! You can build Phase 2 in about 1-2 weeks if you focus on it! 🚀
