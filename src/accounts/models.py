from django.contrib.auth.models import UserManager, User as BaseUser
from django.db import models
from django.db.models.signals import post_save

class User(BaseUser):
    
    objects = UserManager()
	
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        values = {}
        for field in sender._meta.local_fields:
            values[field.attname] = getattr(instance, field.attname)
        user = User(**values)
        user.save()
        
post_save.connect(create_custom_user, BaseUser)