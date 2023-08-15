from django.db import models
from accounts.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

# Create your models here.
def image_upload_path(instance, filename):
    return f'{instance.pk}/{filename}'

def store_image_upload_path(instance, filename):
    return f'{instance.store.store_id}/{filename}'



class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    road_address = models.CharField(max_length=255, blank=True, null=True)
    operation_time = models.CharField(max_length=100, blank=True, null=True)
    store_num = models.CharField(max_length=100, blank=True, null=True)
    store_other_data = models.CharField(max_length=255, blank=True, null=True)
    image = models.CharField(max_length=100, blank=True, null=True)
   
    def calculate_average_rating(self):
        reviews = self.reviews.all()
        total_rating = sum(review.rating for review in reviews if review.rating is not None)
        avg_rating = total_rating / len(reviews) if len(reviews) > 0 else None
        return avg_rating


    


class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='menus', blank=True, null=True)
    name = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    #models.IntegerField()

class Store_Image(models.Model):
    id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='image', blank=True, null=True)
    image = models.ImageField(upload_to=store_image_upload_path, blank=True,null=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews", null=True)
    title = models.CharField(max_length=100, default="Default Title")
    content = models.TextField()
    image = models.ImageField(upload_to='reviewimage/', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(blank=True, null=True, default=None)

class Chat(models.Model):
    chat_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats", null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='chats', blank=True, null=True)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    wordcloud_image_path = models.CharField(max_length=255, null=True, blank=True)
    wordcloud_image = models.ImageField(upload_to='chat/', null=True, blank=True)
    #consumers = models.ManyToManyField('Consumer', through='ChatConsumer')

class Scrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, related_name='scraps')

    class Meta:
        unique_together = ('user', 'store')


@receiver(post_save, sender=Review)
def update_store_rating(sender, instance, **kwargs):
    store = instance.store
    avg_rating = Review.objects.filter(store=store).aggregate(Avg('rating'))['rating__avg']
    store.rating = avg_rating
    store.save()