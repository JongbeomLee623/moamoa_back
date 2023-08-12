import requests, json
from django.conf import settings
from rest_framework import status

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import LocationSerializer, CafeSerializer
from rest_framework.permissions import AllowAny
from .models import Store


@api_view(['GET'])
def get_nearby_cafes(request):
    latitude = 37.55 #request.GET.get('latitude')
    longitude = 126.98 #request.GET.get('longitude')
    
    # Naver Map API URL for cafe search
    naver_map_client_key = "CLIENT_KEY" 
    naver_map_client_id = "CLIENT_ID"
    # Replace with your actual Naver Map API key
    #naver_map_url = f"https://naveropenapi.apigw.ntruss.com/map-place/v1/search?query=카페&coordinate={longitude},{latitude}&radius=500"
    naver_map_url = f'https://map.naver.com/v5/search/%EC%B9%B4%ED%8E%98?c=16.04,0,0,0,dh'
    # Send a GET request to Naver Map API for cafe search
    headers = {
        'X-NCP-APIGW-API-KEY-ID': naver_map_client_id,
        'X-NCP-APIGW-API-KEY': naver_map_client_key,
    }
    response = requests.get(naver_map_url )#,headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Extract cafe information from API responses
        cafes = []
        for place in data.get('places', []):
            cafe = {
                'name': place['name'],
                'address': place['road_address'],
            }
            cafes.append(cafe)

        return Response({'cafes': cafes})
    else:
        return Response({'error': 'Failed to fetch cafe information'}, status=response.status_code)

# @api_view(['POST'])
# @permission_classes([AllowAny, ])
# def putStore(request):
#     data = request.data
#     for cafe in data['카페 정보']:
#         if cafe['name'] not in Store.objects.filter(name=cafe['name']):
#             Store.objects.create(name=cafe['name'], type=cafe['cafe_type'], latitude=cafe['coordinates'][1], longitude=cafe['coordinates'][0])

#     return Response({'success': 'success'})