from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('volunteer', 'Volunteer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


# Event Model
class Event(models.Model):
    title = models.CharField(max_length=150)
    date = models.DateField()
    venue = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, default='Upcoming')

    def __str__(self):
        return self.title


# Registration Model
class Registration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    reg_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"