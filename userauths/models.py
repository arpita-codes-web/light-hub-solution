from django.db import models
from django.contrib.auth.models import AbstractUser

def user_directory_path(instance, filename):
    return f"user_{instance.id}/{filename}"


class User(AbstractUser):
    def __str__(self):
        return self.username

# from django.contrib.auth.models import User
from django.conf import settings



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    contact_no = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
    


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()