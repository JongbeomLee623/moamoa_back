import requests, json, math
from django.conf import settings
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from .serializers import *
from rest_framework.permissions import AllowAny
<<<<<<< HEAD
from .models import *
from django.shortcuts import get_object_or_404
=======
from .models import Store, Menu, Review, Board
>>>>>>> 30641ad (menu, review,  chat 쪼금)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins


class StoreViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):

    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]

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
    def unscrap_store(self, request, pk=None):
        store = get_object_or_404(Store, pk=pk)
        user = request.user

        try:
            scrap = Scrap.objects.get(user=user, store=store)
            scrap.delete()
            return Response({'message': 'Store unscrapped successfully.'}, status=200)
        except Scrap.DoesNotExist:
            return Response({'error': 'Store is not scrapped.'}, status=400)
    
    # @action(detail=False, methods=['GET'])
    def get_store_detail(self, request):
        store_id = request.GET.get('store_id')
        queryset = Store.objects.filter(store_id=store_id)
        serializer = StoreSerializer(queryset)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
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



@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def chat_read_create(request, store_id):
    store = get_object_or_404(Store, store_id=store_id)

    if request.method=='GET':
        chats = Chat.objects.filter(store=store)
        serializer = BoardSerializer(chats, many=True)
        return Response(data=serializer.data)
    
    elif request.method == 'POST':
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_read_create(request, store_id):
    store = get_object_or_404(Store, store_id=store_id)

    if request.method=='GET':
        reviews = Review.objects.filter(store=store)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(data=serializer.data)
    
    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def review_read_create(request, store_id):
    store = get_object_or_404(Store, store_id=store_id)

    if request.method=='GET':
        reviews = Review.objects.filter(store=store)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(data=serializer.data)
    
    elif request.method == 'POST':
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([AllowAny])
def review_detail_update_delete(request, store_id,review_id):
    review = get_object_or_404(Review, review_id=review_id)

    if request.method=='GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = ReviewSerializer(instance=review, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        review.delete()
        data = {
            'deleted_review':review_id
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)





@api_view(['GET'])
@permission_classes([AllowAny])
def add_menus_to_cafe(request):
    #data = request.data
    menu_data = {
        '미니말레 커피뢰스터 양재본점': {
            '[NEW]떙모반': '6300원',
            '[BEST]헬싱키 라떼(시그니처A)': '4500원',
            '[BEST]아메리카노(듄켈)': '3000원',
            '[BEST]라뗴': '3800원',
            '[BEST]아메리카노(밸런스)': '3000원',
            '[BEST]수제뉴옥쿠키(오리지널 르뱅)': '3800원',
            '[추천]브리티시 아인슈페너(시그니처B)': '4500원',
            '[추천] 수제 뉴옥 쿠키(스모어)': '3800원',
            '[추천] 수제 생크림스콘(플레인)': '2800원'
        },
        '바세츠아이스크림 양재본점': {
            '[주문1위]패밀리 4가지맛(500g)': '16500원',
            '싱글컴 개별포장(100g)': '3800원',
            '트리플 3가지맛(300g)': '10400원',
            '빅사이즈 5가지맛(1kg)': '30000원',
            '[NEW]아이스아포가토': '4000원',
        },
        '스위티몽거': {
            '개성주악 오리지널': '2700원',
            '개성주악 초코': '3500원',
            '개성주악 딸기': '3400원',
            '개성주악 샤인머스켓': '3400원',
            '개성주악 크림치즈': '3200원',
            '개성주악 옥수수크림': '3300원',
            '개성주악 앙버터': '3300원',
            '개성주악 허니플라워 ': '3200원'
        },
        '심재': {
            '솔티드카라멜스콘': '4500원',
            '믹스베리 스콘': '4300원',
            '살구 스콘': '4300원',
            '얼그레이 갸또': '7800원',
            '단호박 타르트': '7800원',
            '심재크림커피': '6500원',
            '말차라떼': '6000원',
            '쑥라떼': '6000원',
            '흑임자라떼': '6000원',
            '에스프레소': '5000원',
            '아메리카노': '5000원',
            '카페라떼': '5500원',
            '카페모카': '5500원',
            '바닐라라떼': '6000원',
            '브리티시 홍차': '6500원',
            '루이보스&허니부시 허브차': '6500원',
            '페퍼민트 리브스허브차': '6500원',
            '빅 히비스커스 허브차': '6500원',
            '핫/아이스 초콜렛': '6000원',
            '민트초콜렛': '6000원',
            '오미자&청포도에이드': '6000원',
            '배&한라봉에이드': '6000원',
        },
        '오페라빈 로스터스 본점': {
            '크라상 아보카토 오픈 토스트': '15000원',
            '무화과 고메 잠봉베르 토스트': '15000원',
            '아보카토 새우 토스트': '18500원',
            '라떼플루트': '7000원',
            '아인슈페너': '5500원',
            '더플치즈 불고기 크라상': '13000원',
            '아이스 말차라떼': '6000원',
            '고구마 라떼': '6500원',
            '바나나 프렌치 토스트': '16000원',
            '오페라빈시그니처토스트': '16000원',
        },
        '에크하우스': {
            '에소프레소': '2500원',
            '에소프레소 크림': '3000원',
            '아메리카노': '3000원',
            '카페 라떼': '3800원',
            '플랫 화이트': '3800원',
            '카푸치노': '3800원',
            '바닐라 라떼': '4500원',
            '하우스 돌체': '4800원',
            '하우스 말차': '4800원',
            '하우스 초코': '4800원',
            '하우스 크림': '5000원',
            '사과-유차': '4500원',
            '딸기-패션후르츠': '4500원',
            '블랙커런트-한라봉': '4500원',
        },
        '잔상': {
            '얼그레이오렌지케이크': '5000원',
            '잔상커피': '5500원',
            '오늘의 브루잉': '5000원',
            '콜롬비아': '5500원',
            '탄자니아': '5500원',
            '과테말라': '5500원',
            '에티오피아': '5500원',
            '에스프레소': '4000원',
            '아메리카노': '4000원',
            '카페라떼': '4000원',
            '블랙스완': '6500원',
            '아메리칸뷰티': '6000원',
            '초콜릿케이크': '5000원',
            '밀크티': '6000원',
            '자몽차': '6000원',
            '카모마일': '6000원',
        },
        '카페 어느새봄': {
            '크림커피': '5800원',
            '버터구름라뗴': '6000원',
            '딸기라뗴': '6500원',
            '썸머트로피칼에이드': '6500원',
            '옛날와플': '4500원',
            '카야버터와플': '6000원',
            '에그타르트': '2700원',
            '꿀약과샌드': '4000원',
            '아메리카노': '4500원',
            '카페라떼': '5000원',
            '바닐라라뗴': '5500원',
            '밀크티': '5500원',
        },
        '카페 토다': {
            '베이글' : '3000원',
            '크림치즈' : '3000원',
            '연어 샐러드' : '14000원',
            '핫스리 치킨 샐러드' : '8500원',
            '훈제연어 샌드위치' : '9500원',
            '아&베&달 샌드위치' : '10500원',
            '트러플 루벤 샌드위치' : '11500원',
            '감자베이컨 스프' : '8500원',
            '아메리카노' : '4500원',
        },
        '코지리틀 양재점':{
            '자몽피치 티' : '5800원',
            '오트밀크 라떼' : '5500원',
            '코지 크림모카' : '5500원',
            '누텔라크런치' : '5000원',
            '리틀썸머 샌드위치' : '7000원',
            '튜나샌드위치' : '6000원',
            '치킨샌드위치' : '6000원',
            '클래식베이글' : '6500원',
            '올데이샌드위치' : '4700원',
            '크랩샌드위치' : '6800원',
            '에그샌드위치' : '6800원',
        },
        '콘띠오':{
            '만차다' : '5300원',
            '콘레체' : '5300원',
            '아메리카노' : '4500원',
            '딸기 라떼' : '6300원',
            '아이스 아인슈페너' : '6300원',
            '아이스더치' : '5500원',
            '루이보스라뗴' : '6300원',
        },
        'marron':{
            '주문제작)생크림케익' : '24000원',
            '마론 타르트' : '3900원',
            '바나나 브레드' : '4500원',
            '시나노골드애플파이' : '3900원',
            '밤마들렌' : '2500원',
            '스콘' : '3000원',
            '발로나마들렌' : '3000원',
            '아메리칸쿠키' : '4100원',
            '피스타치오 마들렌' : '2800원',
            '피스타치오 휘낭시에' : '2500원',
            '버터바' : '3800원',
            '황치즈버터바' : '4000원',
        },
         '프릳츠 양재점': {
        '에스프레소': '4600원',
        '아메리카토': '4600원',
        '롱블랙': '4600원',
        '플랫 화이트': '5000원',
        '카푸치노': '5000원',
        '카페라뗴': '5000원',
        '바닐라라뗴': '5400원',
        '카페모카': '5800원',
        '브루잉 커피': '5500원',
        '콜드브루': '5000원',
        '콜드브루 라뗴': '5400원',
        '잎차-코랄 머스캣': '5500원',
        '잎차-루이보스 카모마일': '5500원',
        '핫/아이스 초코': '5800원',
        '프릳츠 에일': '5800원',
        '복자-C': '6300원',
        '산딸리크림 도나스': '3500원',
        '파이만주': '3000원',
        '크림치즈 타르트': '3800원',
        '코코로쉐': '1800원',
        '브리오슈': '4600원',
        '무화과 깡빠뉴': '5400원',
    }
}
    for cafe_name, menu_list in menu_data.items():
        cafe = get_object_or_404(Store, name=cafe_name)
        for menu_name, menu_price in menu_list.items():
            Menu.objects.create(store=cafe, name=menu_name, price=menu_price)

    return Response({'success': 'success'}) 

