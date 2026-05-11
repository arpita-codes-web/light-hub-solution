from django.apps import AppConfig  #har app ko register karta he 


class CoreConfig(AppConfig):    #configuration class
    default_auto_field = 'django.db.models.BigAutoField'  #autometic id create karta he
    name = 'core'
