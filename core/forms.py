from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    contact = forms.CharField(max_length=15)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'contact', 'password1', 'password2']