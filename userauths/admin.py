# from django.contrib import admin
# from django.contrib.auth import get_user_model
# User = get_user_model()

# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id','first_name','last_name','email',)

# admin.site.register(User,UserAdmin)
from django.contrib import admin
from .models import User, Profile

# 👉 Profile inline (User ke andar show hoga)
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

# 👉 Custom User Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_contact', 'get_address')
    inlines = [ProfileInline]

    def get_contact(self, obj):
        return obj.profile.contact_no if hasattr(obj, 'profile') else "-"
    get_contact.short_description = "Contact No"

    def get_address(self, obj):
        return obj.profile.address if hasattr(obj, 'profile') else "-"
    get_address.short_description = "Address"

admin.site.register(User, UserAdmin)