from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model (Keep your existing one)
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('volunteer', 'Volunteer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

# Updated Event Model
class Event(models.Model):
    title = models.CharField(max_length=150)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)  
    end_time = models.TimeField(null=True, blank=True) 
    venue = models.CharField(max_length=200)
    description = models.TextField()
    capacity = models.PositiveIntegerField(default=50) 
    status = models.CharField(max_length=20, default='Upcoming')

    def __str__(self):
        return self.title

# Updated Registration Model
class Registration(models.Model):
    STATUS_CHOICES = (
        ('Registered', 'Registered'),
        ('Attended', 'Attended'),
        ('Absent', 'Absent'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reg_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Registered') # Added Status

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.status})"