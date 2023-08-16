import math, io, os, matplotlib, PIL
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from .serializers import *
from .models import *
from accounts.authentication import CookieAuthentication

from rest_framework.views import APIView
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes

from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
from matplotlib import font_manager

import numpy as np
from PIL import Image

matplotlib.use('Agg')


class StoreViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):

    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    authentication_classes = [CookieAuthentication]  # CookieAuthentication 적용
    permission_classes = [IsAuthenticated]

    # 두 지점 간의 거리를 계산하는 함수
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # 위도와 경도를 라디안 단위로 변환
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # 지구 반경 (미터)
        R = 6371000

        # 위도 및 경도 차이 계산
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine 공식 계산
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance
    
    @action(detail=False, methods=['GET'])
    def get_near_store(self, request):#,request):
        # user_latitude = request.GET.get('latitude')
        # user_longitude = request.GET.get('longitude')
        # 임시로 확인할 값. 추후 request로 받아올 예정
        user_latitude = 37.4688345
        user_longitude = 127.0412415
        
        stores = Store.objects.all()

        nearby_stores = []  # 주변 가게들을 담을 리스트

        for store in stores:
            store_latitude = float(store.latitude)
            store_longitude = float(store.longitude)

            distance = self.calculate_distance(user_latitude, user_longitude, store_latitude, store_longitude)
            
            if distance <= 500:
                # 임시로 카페 기준으로만 500m 내의 가게들 불러옴. 베이커리, 아이스크림 기타 등등 존재. 식당은 아직 구현 X
                if "카페" in store.type:
                    nearby_stores.append(store)

        queryset = nearby_stores[:20]
        serializer = StoreSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'])
    def scrap(self, request, pk=None):
        store = get_object_or_404(Store, pk=pk)
        user = request.user

        scrap, created = Scrap.objects.get_or_create(user=user, store=store)
        
        if created:
            return Response({'message': 'Store has been scrapped.'}, status=201)
        else:
            return Response({'message': 'Store is already scrapped.'}, status=200)
        
    
    @action(detail=True, methods=['POST'])
    def unscrap(self, request, pk=None):
        store = get_object_or_404(Store, pk=pk)
        user = request.user

        try:
            scrap = Scrap.objects.get(user=user, store=store)
            scrap.delete()
            return Response({'message': 'Store unscrapped successfully.'}, status=200)
        except Scrap.DoesNotExist:
            return Response({'error': 'Store is not scrapped.'}, status=400)
    
    
    @api_view(['GET'])
    def getStoreMenu(request):
        store_id = request.GET.get('store_id')
        store = Store.objects.get(store_id=store_id)
        menus = store.menus.all()
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data)
    
    def perform_update(self, serializer):
        images_data = self.request.FILES.getlist('images')
        instance = self.get_object()  # 현재 업데이트 중인 객체 가져오기

        # 이전 이미지 데이터 삭제
        if(instance.image.all() is not None):
            for image in instance.image.all():
                file_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
                if os.path.exists(file_path):
                    os.remove(file_path)
                image.delete()

        for image_data in images_data:
            # 이미지 업로드 후 이미지 모델에 저장
            image_instance = Store_Image.objects.create(store=instance, image=image_data)
            image_instance.save()

        return super().perform_update(serializer)


# 리뷰 전체 리스트, 개별 확인, 수정, 삭제
class ReviewViewSet(viewsets.GenericViewSet,
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin):
    queryset = Review.objects.all().order_by('-updated_at')  # updated_at 필드를 기준으로 최신순 정렬
    serializer_class = ReviewSerializer
    authentication_classes = [CookieAuthentication]  # CookieAuthentication 적용
    permission_classes = [IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        return obj
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        images_data = request.FILES.getlist('images')

        if(instance.image.all() is not None):
            for image in instance.image.all():
                file_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
                if os.path.exists(file_path):
                    os.remove(file_path)
                image.delete()

        if images_data:
            for image_data in images_data:
                image_instance = Review_Image.objects.create(review=instance, image=image_data)
                image_instance.save()

        serializer.save()

        return Response(serializer.data)

# 가게에 달린 리뷰 리스트, 생성
class StoreReviewViewSet(viewsets.GenericViewSet,
    mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = ReviewSerializer
    authentication_classes = [CookieAuthentication]  # CookieAuthentication 적용
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store = self.kwargs.get("store_id")
        queryset = Review.objects.filter(store_id = store).order_by('-updated_at')
        return queryset

    def perform_create(self, serializer):
        store = get_object_or_404(Store, pk=self.kwargs.get("store_id"))
        
        images_data = self.request.FILES.getlist('image')
        review = serializer.save(store=store, user=self.request.user)
        
        for image_data in images_data:
            image_instance = Review_Image.objects.create(review=review, image=image_data)
            image_instance.save()
        
        return Response(serializer.data)

    def create(self, request, store_id=None):
        store = get_object_or_404(Store, pk=store_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        images_data = request.FILES.getlist('images')
        review = serializer.save(store=store, user=request.user)
        
        for image_data in images_data:
            image_instance = Review_Image.objects.create(review=review, image=image_data)
            image_instance.save()
        
        return Response(serializer.data)
    
class ScrapedStoresListView(viewsets.GenericViewSet, mixins.ListModelMixin):
    authentication_classes = [CookieAuthentication]  # CookieAuthentication 적용
    permission_classes = [IsAuthenticated]

    serializer_class = StoreSerializer

    def get_queryset(self):
        user = self.request.user
        scrapped_stores = Scrap.objects.filter(user=user).select_related('store')
        return scrapped_stores.values_list('store', flat=True)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([CookieAuthentication])
def board_read_create(request, store_id):
    store = get_object_or_404(Store, store_id=store_id)

    if request.method=='GET':
        boards = Board.objects.filter(store=store)
        serializer = BoardSerializer(boards, many=True)
        return Response(data=serializer.data)
    
    elif request.method == 'POST':
        serializer = BoardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# @api_view(['GET', 'POST'])
# @permission_classes([IsAuthenticated])
# @authentication_classes([CookieAuthentication])
# def chat_read_create(request, store_id):
#     store = get_object_or_404(Store, store_id=store_id)

#     if request.method=='GET':
#         chats = Chat.objects.filter(store=store)
#         serializer = ChatSerializer(chats, many=True)
#         return Response(data=serializer.data)
    
#     elif request.method == 'POST':
#         serializer = ChatSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(data=serializer.data)
#         else:
#             return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class StoreChatViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    serializer_class = ChatSerializer
    authentication_classes = [CookieAuthentication]  # CookieAuthentication 적용
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store = self.kwargs.get("store_id")
        queryset = Chat.objects.filter(store=store).order_by('date')
        return queryset

    def perform_create(self, serializer):
        store = get_object_or_404(Store, pk=self.kwargs.get("store_id"))
        serializer.save(store=store, user=self.request.user)

    def create(self, request, store_id=None):
        store = get_object_or_404(Store, pk=store_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(store=store, user=request.user)

        # 새로 생성한 채팅을 조회해서 반환
        new_chat = Chat.objects.get(pk=serializer.instance.pk)
        response_serializer = self.get_serializer(new_chat)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)



def generate_wordcloud(request, store_id):

    store = Store.objects.get(pk=store_id)
    # Chat 모델에서 내용 가져오기 (예시로 최근 100개의 채팅 메시지 사용)
    chat_messages = Chat.objects.filter(store=store)
    
    word_frequencies = {}  # 단어 빈도수 저장할 딕셔너리

    excluded_words = ['ㅋㅋㅋ','ㅋㅋㅋㅋ','ㅋㅋㅋㅋㅋ', 'ㅎㅎ', 'ㅠㅠ', 'ㅅㅂ', '시발' ,'존나', '개', 'd']  # 원하는 단어들을 추가

    # 채팅 내용에서 단어 빈도수 계산
    for message in chat_messages:
        words = message.content.split()  # 공백을 기준으로 단어 분리
        for word in words:
            if word not in excluded_words:
                if word in word_frequencies:
                    word_frequencies[word] += 1
                else:
                    word_frequencies[word] = 1

    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'

    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heart.png') 
    icon = PIL.Image.open(image_path)
    img = PIL.Image.new('RGB', icon.size, (255,255,255))
    img.paste(icon, icon)
    img = np.array(img)

    # 단어 빈도수를 입력하여 워드클라우드 객체 생성
    wordcloud = WordCloud(width=400, height=400, mask=img, max_font_size=200, background_color='white', font_path=font_path, prefer_horizontal = True).generate_from_frequencies(word_frequencies)


    image_file_path = os.path.join(settings.MEDIA_ROOT, f'{store_id}',f'/wordcloud_{store_id}.png')
    wordcloud.to_file(image_file_path)

        # 이미지 파일 경로 저장 또는 업데이트
    for chat in chat_messages:
        chat.wordcloud_image_path =  f'{store_id}/wordcloud_{store_id}.png'
        chat.save()
    
    store.wordcloud = f'chat/wordcloud_{store_id}.png'
    store.save()

    # 이미지를 바이트 스트림으로 반환 (또는 이미지를 파일로 저장하여 경로를 반환)
    buf = io.BytesIO()
    plt.figure(figsize=(6, 6))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png')
    buf.seek(0)

    return HttpResponse(buf.getvalue(), content_type='image/png')

