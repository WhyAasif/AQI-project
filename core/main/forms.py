from django import forms
from .models import User
from django.contrib.auth.forms import UserCreationForm

# Used for the Sign Up page
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

# Used for the new Profile update page
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']