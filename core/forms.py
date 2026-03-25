import re
from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'contact']

    def clean_contact(self):
     contact = self.cleaned_data.get('contact')
 
     if not contact.isdigit():
        raise forms.ValidationError("Only numbers allowed")

     if len(contact) != 10:
        raise forms.ValidationError("Must be exactly 10 digits")

     return contact
     

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user
    
   

def clean_password1(self):
    password = self.cleaned_data.get('password1')

    if len(password) < 8:
        raise forms.ValidationError("Password must be at least 8 characters")

    if not re.search(r'[A-Z]', password):
        raise forms.ValidationError("Must contain at least one uppercase letter")

    if not re.search(r'[0-9]', password):
        raise forms.ValidationError("Must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
        raise forms.ValidationError("Must contain at least one special character")

    return password

def clean(self):
    cleaned_data = super().clean()
    p1 = cleaned_data.get("password1")
    p2 = cleaned_data.get("password2")

    if p1 and p2 and p1 != p2:
        raise forms.ValidationError("Passwords do not match")