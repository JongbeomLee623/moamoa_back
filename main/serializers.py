from rest_framework import serializers
from accounts.models import User
from main.models import Store, Review, Board, Chat, Scrap, Menu, Store_Image, Review_Image


class StoreSerializer(serializers.ModelSerializer):

    images = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()

    def get_reviews(self, instance):
        serializer = ReviewSerializer(instance=instance.reviews, many=True, context=self.context)
        return serializer.data

    def get_images(self, instance):
        image = instance.image.all()
        return ImageSerializer(instance=image, many = True, context=self.context).data
    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        
        if images_data:
            for image_data in images_data:
                image_id = image_data.get('id', None)
                if image_id:
                    image_instance = instance.image.get(id=image_id)
                    image_serializer = ImageSerializer(instance=image_instance, data=image_data)
                    if image_serializer.is_valid():
                        image_serializer.save()
                else:
                    # Create a new image instance
                    ImageSerializer(data=image_data, context=self.context).save(store=instance)
        
        # Continue with the rest of the update logic
        return super().update(instance, validated_data)
    
    def get_ratings(self, instance):
        return instance.calculate_average_rating()
    
    class Meta:
        model = Store
        fields = ['store_id','name','type','road_address','operation_time','store_num','store_other_data','images','ratings', 'reviews']
        

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url= True, required = False)
    
    class Meta:
        model = Store_Image
        fields = ['image']        

class MenuSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField()
    store = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    
class ReviewSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    def get_username(self, instance):
        if instance.user is not None:
            return instance.user.nickname
        else:
            return "UnKnown"

    def get_images(self, instance):
        image = instance.image.all()
        return ImageSerializer(instance=image, many=True, context=self.context).data
    
    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        
        if images_data:
            for image_data in images_data:
                image_id = image_data.get('id', None)
                if image_id:
                    image_instance = instance.image.get(id=image_id)
                    image_serializer = ImageSerializer(instance=image_instance, data=image_data)
                    if image_serializer.is_valid():
                        image_serializer.save()
                else:
                    # Create a new image instance
                    ImageSerializer(data=image_data, context=self.context).save(store=instance)

        # Update other fields
        instance.title = validated_data.get('title', instance.title)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        # Update store's average rating if applicable
        if instance.store:
            instance.store.rating = instance.store.calculate_average_rating()
            instance.store.save()
        
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'rating' in data and data['rating'] is not None:
            formatted_rating = "{:.1f}".format(data['rating']).rstrip('0').rstrip('.')
            data['rating'] = f"{formatted_rating}/5"
        return data

    class Meta:
        model = Review
        fields = ['review_id','title','store','username','content','rating', 'images', 'created_at', 'updated_at']
        read_only_fields = ['review_id','username','store', 'user', 'created_at', 'updated_at']

class ReviewImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url= True, required = False)
    
    class Meta:
        model = Review_Image
        fields = ['image']    

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


