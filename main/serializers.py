from rest_framework import serializers
from accounts.models import User
from main.models import Store, Review, Board, Chat, Scrap, Menu, Store_Image, Review_Image


class StoreSerializer(serializers.ModelSerializer):

    images = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    menus = serializers.SerializerMethodField()
    boards = serializers.SerializerMethodField()

    def get_reviews(self, instance):
        serializer = ReviewSerializer(instance=instance.reviews, many=True, context=self.context)
        return serializer.data
    
    def get_menus(self, instance):
        serializer = MenuSerializer(instance=instance.menus, many=True, context=self.context)
        return serializer.data

    def get_images(self, instance):
        image = instance.image.all()
        return ImageSerializer(instance=image, many = True, context=self.context).data
    
    def get_boards(self, instance):
        board = instance.boards.all()
        return BoardSerializer(instance=board, many = True, context=self.context).data
    
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
    
    def to_representation(self, instance):
        if self.context.get('scraps_action'):
            return {
                'store_id': instance.store_id,
                'name': instance.name,
                'road_address': instance.road_address,
                'operation_time': instance.operation_time,
                'ratings': instance.calculate_average_rating(),
                'store_num' : instance.store_num,
                'images': ImageSerializer(instance.image.all().first()).data,
            }
        else:
            return super().to_representation(instance)
    
    class Meta:
        model = Store
        fields = ['store_id','name','type','road_address','operation_time','store_num','store_other_data','boards','images','ratings','menus', 'reviews']
        

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url= True, required = False)
    
    class Meta:
        model = Store_Image
        fields = ['image']        

class MenuSerializer(serializers.ModelSerializer):

    class Meta:
        model = Menu
        fields = ['name','price']

    
class ReviewSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    username = serializers.SerializerMethodField()

    storename = serializers.SerializerMethodField()

    def get_username(self, instance):
        if instance.user is not None:
            return instance.user.nickname
        else:
            return "UnKnown"

    def get_storename(self, instance):
        if instance.store is not None:
            return instance.store.name

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
        fields = ['review_id','title','storename','username','content','rating', 'images', 'created_at', 'updated_at']
        read_only_fields = ['review_id','username','store', 'user', 'created_at', 'updated_at']

class ReviewImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url= True, required = False)
    
    class Meta:
        model = Review_Image
        fields = ['image']    

class BoardSerializer(serializers.ModelSerializer):
    #board_id = serializers.IntegerField()
    #store = serializers.IntegerField()
    # store = serializers.PrimaryKeyRelatedField(queryset=Store.objects.all())
    # content = serializers.CharField()
    
    def create(self, validated_data):
        return Board.objects.create(**validated_data)    

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance
    
    class Meta:
        model = Board
        fields = ['content','date']
    
class ChatSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    def get_user(self, instance):
            if instance.user is not None:
                return instance.user.nickname
            else:
                return "UnKnown"

    # def create(self, validated_data):
    #     return Chat.objects.create(**validated_data)

    
    # def update(self, instance, validated_data):
    #     instance.content = validated_data.get('content', instance.content)
    #     instance.save()
    #     return instance
    
    class Meta:
        model = Chat
        fields = ['user', 'content','date']
        read_only_fields = ['user', 'store_id', 'created_at', 'updated_at', 'chat_id']

