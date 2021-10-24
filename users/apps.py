from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'users'
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()
