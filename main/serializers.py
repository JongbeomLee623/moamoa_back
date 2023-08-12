from rest_framework import serializers

class LocationSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class CafeSerializer(serializers.Serializer):
    name = serializers.CharField()
    address = serializers.CharField()
