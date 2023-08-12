from django.db import models

# Create your models here.

class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.CharField(max_length=100, blank=True, null=True)
    menus = models.ManyToManyField('Menu', related_name='stores')
    boards = models.ForeignKey('Board', on_delete=models.CASCADE, blank=True, null=True)
    reviews = models.ForeignKey('Review', on_delete=models.CASCADE, blank=True, null=True)
    chat = models.OneToOneField('Chat', on_delete=models.CASCADE, blank=True, null=True)

class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()


class Board(models.Model):
    board_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    content = models.TextField()
    image = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    content = models.TextField()
    image = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(blank=True, null=True)

class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    #consumers = models.ManyToManyField('Consumer', through='ChatConsumer')