from rest_framework import serializers
from accounts.models import User
from main.models import Store, Review, Board, Chat, Scrap


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
    ratings = serializers.SerializerMethodField()

    # def get_ratings(self, obj):
    #     # function(avg of store.ratings.rating
    def get_ratings(self, instance):
        return instance.calculate_average_rating()
    
       
    class Meta:
        model = Store
        fields = "__all__"
        read_only_fields = ('store_id', 'name', 'type', 'latitude', 'longitude', 'rating')

class MenuSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField()
    store = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    
class ReviewSerializer(serializers.Serializer):
    #review_id = serializers.IntegerField()
    #store = serializers.IntegerField()
    #store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    user = serializers.SerializerMethodField()
    title = serializers.CharField()
    content = serializers.CharField()
    image = serializers.ImageField(use_url=True, required=False)
    rating = serializers.FloatField(allow_null=True, required=False)
    
    def get_user(self, instance):
        if instance.user is not None:
            return instance.user.username
        else:
            return "UnKnown"
    
    def create(self, validated_data):
        return Review.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        if instance.store:
            instance.store.rating = instance.store.calculate_average_rating()
            instance.store.save()
        return instance

    def delete(self, instance):
        instance.delete()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'rating' in data and data['rating'] is not None:
            data['rating'] = f"{data['rating']:.1f}/5"  # 평점을 소수점 형식으로 표기
        return data

    class Meta:
        model = Store
        fields = "__all__"



class BoardSerializer(serializers.Serializer):
    #board_id = serializers.IntegerField()
    #store = serializers.IntegerField()
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    content = serializers.CharField()
    
    def create(self, validated_data):
        return Board.objects.create(**validated_data)

    class Meta:
        model = Store
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
    
class ChatSerializer(serializers.Serializer):
    #chat_id = serializers.IntegerField()
    #store = serializers.IntegerField()
    user = serializers.SerializerMethodField()
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    content = serializers.CharField()
    
    def get_user(self, instance):
            if instance.user is not None:
                return instance.user.username
            else:
                return "UnKnown"

    def create(self, validated_data):
        return Chat.objects.create(**validated_data)

    class Meta:
        model = Store
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance


