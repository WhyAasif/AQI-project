from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'volunteer'
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email'] 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the username field read-only
        self.fields['username'].widget.attrs['readonly'] = True
        
        # Add Bootstrap classes for a clean UI
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'