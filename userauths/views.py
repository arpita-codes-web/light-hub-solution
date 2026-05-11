from django.shortcuts import render
from django.shortcuts import redirect
from userauths.forms import UserRegisterForm
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from django.conf import settings
from userauths.forms import LoginForm 
from django.contrib.auth.decorators import login_required
from userauths.forms import UserUpdateForm ,ProfileUpdateForm # Import the form
from .models import Profile
from django.contrib.auth import get_user_model

User = get_user_model()



# def register_view(request):
#     if request.method == "POST":
#         form = UserRegisterForm(request.POST, request.FILES)  # Handle file uploads
#         if form.is_valid():
#             new_user = form.save(commit=False)  # Don't save yet

#             new_user.username = form.cleaned_data['email']
#             new_user.email = form.cleaned_data['email']
#             new_user.first_name = form.cleaned_data['first_name']
#             new_user.last_name = form.cleaned_data['last_name']
#             # new_user.address = form.cleaned_data['address']
#             # new_user.contact_no = form.cleaned_data['contact_no']
            
           

#             new_user.save()  # Now save user
#             Profile.objects.get_or_create(
#     user=new_user,
#     defaults={
#         'address': form.cleaned_data['address'],
#         'contact_no': form.cleaned_data['contact_no']
#     }
# )
#             messages.success(request, "Account created successfully.")
#             new_user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
#             if new_user is not None:
#                 login(request, new_user)
#             return redirect("core:index")
#     else:
#         form = UserRegisterForm()

#     return render(request, "userauths/sign-up.html", {"form": form})
def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)

            new_user.username = form.cleaned_data['email']
            new_user.email = form.cleaned_data['email']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']

            new_user.save()   # 👈 sirf ye hi rakho

            messages.success(request, "Account created successfully.")

            new_user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            if new_user is not None:
                login(request, new_user)

            return redirect("core:index")
    else:
        form = UserRegisterForm()

    return render(request, "userauths/sign-up.html", {"form": form})
def login_view(request):

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("core:index")
        else:
            messages.warning(request, "Invalid email or password.")

    return render(request,"userauths/sign-in.html")

 

def logout_view(request):
    logout(request)
    messages.success(request,"You logged out.")
    return redirect("userauths:sign-in")


@login_required

def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            messages.success(request, "Profile updated successfully!")
            return redirect("userauths:profile")   # redirect important hai

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        "u_form": u_form,
        "p_form": p_form,
    }
    return render(request, "userauths/profile.html", context)