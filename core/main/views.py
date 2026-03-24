from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from .models import Event , Registration
from django.contrib.auth.decorators import login_required
import requests


def home(request):
    return HttpResponse("Hello Aasif, your project started!")


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
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')

def event_list(request):
    events = Event.objects.all()

    user_registrations = []
    if request.user.is_authenticated:
        user_registrations = Registration.objects.filter(user=request.user).values_list('event_id', flat=True)

    return render(request, 'event_list.html', {
        'events': events,
        'user_registrations': user_registrations
    })


@login_required
def join_event(request, event_id):
    event = Event.objects.get(id=event_id)
    user = request.user
    if not Registration.objects.filter(user=user, event=event).exists():
        Registration.objects.create(user=user, event=event)
    return redirect('events')

@login_required
def my_events(request):
    registrations = Registration.objects.filter(user=request.user)

    return render(request, 'my_events.html', {
        'registrations': registrations
    })

# def aqi_view(request):
#     data = None

#     if request.method == 'POST':
#         city = request.POST.get('city')

#         # Step 1: Convert city → lat/lon
#         geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=3b97376b67bc9aaba3a87f1c4a827d5c"
#         geo_response = requests.get(geo_url).json()

#         if geo_response:
#             lat = geo_response[0]['lat']
#             lon = geo_response[0]['lon']

#             # Step 2: Get AQI using lat/lon
#             aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid=3b97376b67bc9aaba3a87f1c4a827d5c"
#             aqi_response = requests.get(aqi_url).json()

#             aqi_value = aqi_response['list'][0]['main']['aqi']
#             components = aqi_response['list'][0]['components']

#             # AQI category (OpenWeather scale 1–5)
#             if aqi_value == 1:
#                 category = "Good"
#                 color = "green"
#             elif aqi_value == 2:
#                 category = "Fair"
#                 color = "yellow"
#             elif aqi_value == 3:
#                 category = "Moderate"
#                 color = "orange"
#             elif aqi_value == 4:
#                 category = "Poor"
#                 color = "red"
#             else:
#                 category = "Very Poor"
#                 color = "purple"

#             data = {
#                 'city': city,
#                 'aqi': aqi_value,
#                 'pm25': components.get('pm2_5', 'N/A'),
#                 'pm10': components.get('pm10', 'N/A'),
#                 'category': category,
#                 'color': color
#             }

#     return render(request, 'aqi.html', {'data': data})

# import requests

def home_view(request):
    url = "https://api.waqi.info/feed/here/?token=020f43646c18e56c461bb0370599675f5ee742e6"
    response = requests.get(url)
    data = response.json()

    context = {}

    if data['status'] == 'ok':
        context['aqi'] = data['data']['aqi']
        context['city'] = data['data']['city']['name']
        context['pm25'] = data['data']['iaqi'].get('pm25', {}).get('v', 'N/A')
        context['pm10'] = data['data']['iaqi'].get('pm10', {}).get('v', 'N/A')
        context['lat']= data['data']['city']['geo'][0]
        context['lon']= data['data']['city']['geo'][1]

    return render(request, 'home.html', context)
