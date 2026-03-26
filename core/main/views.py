from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import UserRegisterForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from .models import Event, Registration, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
import requests
from datetime import date, timedelta, datetime
import csv
from django.http import HttpResponse


# Helper to check if user is admin
def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)

def get_aqi_category(aqi):
    """Returns category and advice based on AQI value"""
    if aqi <= 50:
        return "Good", "Green", "Air quality is satisfactory, and air pollution poses little or no risk."
    elif aqi <= 100:
        return "Moderate", "Yellow", "Air quality is acceptable. However, there may be a risk for some people."
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "orange", "Members of sensitive groups may experience health effects."
    elif aqi <= 200:
        return "Unhealthy", "red", "Everyone may begin to experience health effects."
    elif aqi <= 300:
        return "Very Unhealthy", "Purple", "Health alert: The risk of health effects is increased for everyone."
    else:
        return "Hazardous", "Maroon", "Health warning of emergency conditions: the entire population is likely to be affected."

def get_pm25_color(aqi):
    if aqi <= 12: return "Green"
    elif aqi <= 35: return "Yellow"
    elif aqi <= 150: return "Orange"
    elif aqi <= 250: return "Purple"
    else: return "Maroon"

def get_pm10_color(aqi):
    if aqi <= 54: return "Green"
    elif aqi <= 154 : return "Yellow"
    elif aqi <= 354 : return "Orange"
    elif aqi <= 424 : return "Red"
    elif aqi <= 604: return "Purple"
    else: return "Maroon"

def home_view(request):
    token = "020f43646c18e56c461bb0370599675f5ee742e6"
    # Check if a specific city was searched
    city_query = request.GET.get('city', '')
    if city_query:
        url = f"https://api.waqi.info/feed/{city_query}/?token={token}"
    else:
        url = f"https://api.waqi.info/feed/here/?token={token}"
    
    context = {}
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data['status'] == 'ok':
            aqi = data['data']['aqi']
            context['aqi'] = aqi
            context['city'] = data['data']['city']['name']
            context['pm25'] = data['data']['iaqi'].get('pm25', {}).get('v', 'N/A')
            context['pm10'] = data['data']['iaqi'].get('pm10', {}).get('v', 'N/A')
            context['o3'] = data['data']['iaqi'].get('o3', {}).get('v', 'N/A')
            context['no2'] = data['data']['iaqi'].get('no2', {}).get('v', 'N/A')
            context['lat'] = data['data']['city']['geo'][0]
            context['lon'] = data['data']['city']['geo'][1]
            
            category, color, advice = get_aqi_category(aqi)
            context['category'] = category
            context['color'] = color
            context['advice'] = advice
            context['pm25color'] = get_pm25_color(context['pm25'] if context['pm25'] != 'N/A' else 0)
            context['pm10color'] = get_pm10_color(context['pm10'] if context['pm10'] != 'N/A' else 0)
    except Exception:
        context['error'] = "Could not fetch live data. Please check your connection or search query."

    return render(request, 'home.html', context)

@user_passes_test(is_admin)
def admin_report(request):
    Event.objects.filter(date__lt=date.today(), status='Upcoming').update(status='Completed')
    
    events = Event.objects.annotate(current_volunteers=Count('registration')).all()
    return render(request, 'admin_report.html', {'events': events})
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user:
            login(request, user)
            return redirect('home')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def event_list(request):
    Event.objects.filter(date__lt=date.today(), status='Upcoming').update(status='Completed')
    
    events = Event.objects.all().order_by('-date') 
    
    user_reg_ids = []
    if request.user.is_authenticated:
        user_reg_ids = Registration.objects.filter(user=request.user).values_list('event_id', flat=True)
    return render(request, 'event_list.html', {'events': events, 'user_registrations': user_reg_ids})

def event_detail(request, event_id):
    # --- NEW: Check if this specific event has passed before loading details ---
    Event.objects.filter(id=event_id, date__lt=date.today(), status='Upcoming').update(status='Completed')
    
    event = get_object_or_404(Event, id=event_id)
    
    current_count = Registration.objects.filter(event=event).count()
    remaining_spots = max(0, event.capacity - current_count)
    progress_percentage = int((current_count / event.capacity) * 100) if event.capacity > 0 else 0
    
    is_registered = False
    if request.user.is_authenticated:
        is_registered = Registration.objects.filter(user=request.user, event=event).exists()
        
    context = {
        'event': event,
        'current_count': current_count,
        'remaining_spots': remaining_spots,
        'progress_percentage': progress_percentage,
        'is_registered': is_registered,
    }
    return render(request, 'event_detail.html', context)

@login_required
def join_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    current_count = Registration.objects.filter(event=event).count()
    
    if current_count >= event.capacity:
        return redirect('event_detail', event_id=event.id) # Event full, redirect back
    
    Registration.objects.get_or_create(user=request.user, event=event)
    return redirect('my_events')


@login_required
def my_events(request):
    registrations = Registration.objects.filter(user=request.user).order_by('-reg_date')
    
    # Calculate total volunteer hours in the last 365 days
    one_year_ago = date.today() - timedelta(days=365)
    attended_regs = Registration.objects.filter(
        user=request.user, 
        status='Attended',
        event__date__gte=one_year_ago
    )
    
    total_hours = 0.0
    for reg in attended_regs:
        if reg.event.time and reg.event.end_time:
            # Combine dates to calculate duration in hours
            start = datetime.combine(date.today(), reg.event.time)
            end = datetime.combine(date.today(), reg.event.end_time)
            if end > start:
                duration = (end - start).total_seconds() / 3600.0
                total_hours += duration

    context = {
        'registrations': registrations,
        'total_hours': round(total_hours, 1),
        'today': date.today(),
    }
    return render(request, 'my_events.html', context)

@login_required
def update_registration_status(request, reg_id, status):
    """Allows a user to mark themselves as Attended or Absent"""
    reg = get_object_or_404(Registration, id=reg_id, user=request.user)
    
    # Validation: Only allow marking 'Attended' if it is the day of the event (or past)
    if status == 'Attended' and reg.event.date > date.today():
        # Do not update if trying to mark attended before the event date
        pass
    elif status in ['Attended', 'Absent']:
        reg.status = status
        reg.save()
        
    return redirect('my_events')

@login_required
def cancel_registration(request, reg_id):
    """Allows a user to completely delete their participation registration"""
    reg = get_object_or_404(Registration, id=reg_id, user=request.user)
    if request.method == 'POST':
        reg.delete()
    return redirect('my_events')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
        
    # Fetch all participation records for the logged-in user
    registrations = Registration.objects.filter(user=request.user).order_by('-reg_date')
    
    context = {
        'form': form,
        'registrations': registrations  # Pass this to the template
    }
    return render(request, 'profile.html', context)
@login_required
def download_event_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{request.user.username}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Event Title', 'Date', 'Venue', 'Status', 'Hours'])

    registrations = Registration.objects.filter(user=request.user)
    for reg in registrations:
        hours = 0
        if reg.status == 'Attended' and reg.event.time and reg.event.end_time:
            start = datetime.combine(date.today(), reg.event.time)
            end = datetime.combine(date.today(), reg.event.end_time)
            hours = round((end - start).total_seconds() / 3600.0, 1)
        
        writer.writerow([reg.event.title, reg.event.date, reg.event.venue, reg.status, hours])

    return response