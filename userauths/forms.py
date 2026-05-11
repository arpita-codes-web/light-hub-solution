from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Last Name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"}))
    address = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Address", "rows": 2}))
    contact_no = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Contact No"}))

    class Meta:
        model=User
        fields=["first_name", "last_name", "email", "password1", "password2", "address", "contact_no",]

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Last Name"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
   
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email",]


from .models import Profile



class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'contact_no']
        widgets = {
            'address': forms.Textarea(attrs={'placeholder': 'Address', 'class': 'form-control'}),
            'contact_no': forms.TextInput(attrs={'placeholder': 'Contact Number', 'class': 'form-control'}),
        }