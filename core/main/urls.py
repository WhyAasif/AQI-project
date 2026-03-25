from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Events System
    path('events/', views.event_list, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'), # NEW Detail Route
    path('join/<int:event_id>/', views.join_event, name='join_event'),
    path('my-events/', views.my_events, name='my_events'),
    
    # Reports
    path('reports/admin-summary/', views.admin_report, name='admin_report'),
]