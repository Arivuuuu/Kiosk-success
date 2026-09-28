from rest_framework import serializers
from .models import (
    Machine, 
    MachineSubscription, 
    CameraFeed,
    Zone,
    Line,
    AIModel,
    CameraAIModel
)

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'zone_name', 'zone_coordinates', 'is_active']

class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ['id', 'line_name', 'line_coordinates', 'line_type', 'is_active']

class AIModelDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = ['id', 'name', 'version', 'model_type']

class CameraAIModelSerializer(serializers.ModelSerializer):
    ai_model = AIModelDetailSerializer()
    
    class Meta:
        model = CameraAIModel
        fields = ['id', 'ai_model', 'configuration', 'is_active']

class CameraFeedDetailSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, read_only=True)
    lines = LineSerializer(many=True, read_only=True)
    ai_models = CameraAIModelSerializer(many=True, read_only=True)

    class Meta:
        model = CameraFeed
        fields = ['id', 'camera_name', 'camera_type', 'feed_url', 'is_active', 'zones', 'lines', 'ai_models']

class MachineSubscriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineSubscription
        fields = ['id', 'license_key', 'start_date', 'end_date', 'subscription_type', 'is_active']

class MachineDetailSerializer(serializers.ModelSerializer):
    subscription = MachineSubscriptionDetailSerializer(read_only=True)
    camera_feeds = CameraFeedDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Machine
        fields = [
            'id', 'machine_name', 'machine_code', 'machine_id', 
            'manufacturing_date', 'country', 'state', 'city', 
            'is_active', 'subscription', 'camera_feeds'
        ] 