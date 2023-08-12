from rest_framework import serializers
from accounts.models import User
from main.models import Store


class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class CafeSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()

class StoreSerializer(serializers.Serializer):
    store_id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    #ratings = serializers.FloatField()
    #ratings = serializers.SerializerMethodField()

    # def get_ratings(self, obj):
    #     # function(avg of store.ratings.rating

    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ('store_id', 'name', 'type', 'latitude', 'longitude')

class MenuSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField()
    store = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()