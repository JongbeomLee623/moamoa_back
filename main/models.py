from django.db import models
from accounts.models import User
from django.utils import timezone

# Create your models here.

class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.CharField(max_length=100, blank=True, null=True)

class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='menus', blank=True, null=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()


class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='boards', blank=True, null=True)
    name = models.CharField(max_length=100)
    content = models.TextField()
    image = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='reviews', blank=True, null=True)
    content = models.TextField()
    image = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(blank=True, null=True)

class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='chats', blank=True, null=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    #consumers = models.ManyToManyField('Consumer', through='ChatConsumer')

class Scrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='scraps')
    date_scraped = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'store')