from django.urls import path
from userauths import views
from django.contrib.auth import views as auth_views


app_name="userauths"

urlpatterns=[
    
    path("sign-up/",views.register_view,name="sign-up"),
    path("sign-in/",views.login_view,name="sign-in"),
    path("sign-out/",views.logout_view,name="sign-out"),
    path("profile/", views.profile_view, name="profile"),

]