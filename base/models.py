from django.db import models
# from django.contrib.auth.models import User


from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=200, null = True)
    email  = models.EmailField(unique = True , null = True)
    bio = models.TextField(null = True)
    
    
    #  need to install Pillow library " python3 -m pip install pillow"
    avatar = models.ImageField(null = True,default ="avatar.svg")

    # USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []







# Create your models here.

class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self) :
        return self.name

class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    desription = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name="participants", blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated','-created']
    
    def __str__(self):
        return str(self.name)
    
class Message(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    #  meanning that one room will have alot of messages, if delete room, then message will be deleted
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-updated','-created']
     
    def __str__(self):
        return self.body[0:50]