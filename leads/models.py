#MODEL MANAGERS
# class Car(models.Model):
#     CAR_MANUFACTURERS = (
#         ('Audi', 'Audi'),
#         ('BMW', 'BMW'),
#         ('Fecccrrari', 'Ferrari'),
#     )

#     make = models.CharField(max_length=20, choices=CAR_MANUFACTURERS)
#     model = models.CharField(max_length=20)
#     year = models.IntegerField(default=2015)
## to access car(model) manager you use
# Car.objects
## to create a new car
# Car.objects.create(make="BMW", model="X5", year=2017)
## QUERYSETs
## query for all car in the database
# Car.objects.all()
## query for car with the make equal to "Audi"
# Car.objects.filter(make="Audi")
## query for car with a year greater than 2016
# Car.objects.filter(year__gt=2016)





from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser
# Create your models here.




#create your own user model
#this view means once you create a account you are by default the organizer of that account
class User(AbstractUser):
    #adding boolean fields to determine what we allow the user to do
    is_organizor = models.BooleanField(default=True)
    is_agent = models.BooleanField(default=False)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username



#class inherits from models.Model
class Lead(models.Model):
    #first_name field = datatype(CharField)
    first_name = models.CharField(max_length=20)
    #maxium charachter lenth is 20(20 characters)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField(default=0)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    #create a relationship between lead and agent table, settings on_delete to models.cascade means if a agents deleted the lead will also get deleted
    agent = models.ForeignKey("Agent", null=True, blank=True, on_delete=models.SET_NULL)
    #related_name="leads" is the relation name that you give to lead and category 
    category = models.ForeignKey("Category", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()



    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    #string representation of user in agent
    def __str__(self):
        return self.user.email
    


class Category(models.Model):
    name = models.CharField(max_length=30)  #Our 4 categories: New, Contacted, Converted, Unconverted
    organization = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


#creating a user profile
def post_user_created_signal(sender, instance, created, **kwargs):
    #tells us what user was actually saved
    if created:
        UserProfile.objects.create(user=instance)


#calling this function when we recieve the post save event
post_save.connect(post_user_created_signal, sender=User)