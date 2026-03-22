from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('events/', views.event_list, name='events'),
    path('join/<int:event_id>/', views.join_event, name='join_event'),
    path('my-events/', views.my_events, name='my_events'),
    path('aqi/', views.aqi_view, name='aqi'),
]