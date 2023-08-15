from rest_framework import serializers
from accounts.models import User
from main.models import Store, Review, Board, Chat, Scrap, Menu, Store_Image


class StoreSerializer(serializers.ModelSerializer):

    images = serializers.SerializerMethodField()
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
    
    
    class Meta:
        model = Store
        fields = ['store_id','name','type','road_address','operation_time','store_num','store_other_data','images']
        

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
    
class ReviewSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    #store = serializers.IntegerField()
    store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    user = serializers.SerializerMethodField()
    content = serializers.CharField()

    def get_user(self, instance):
        if instance.user_id is not None:
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
        return instance

    def delete(self, instance):
        instance.delete()
        return instance


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


