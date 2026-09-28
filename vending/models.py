import random
import string
from django.db import models
from django.contrib.auth.models import User

def generate_license_key():
    """Generate a 16-digit alphanumeric license key"""
    chars = string.ascii_uppercase + string.digits  # A-Z and 0-9
    # Generate 16 characters with 4 blocks of 4 characters each
    key = ''.join(random.choice(chars) for _ in range(16))
    # Insert hyphens every 4 characters
    return f"{key[:4]}-{key[4:8]}-{key[8:12]}-{key[12:]}"

class Machine(models.Model):
    machine_name = models.CharField(max_length=100,null=True,blank=True)
    machine_code = models.CharField(max_length=50, unique=True)
    machine_id = models.CharField(max_length=50, unique=True)
    manufacturing_date = models.DateField(auto_now_add=True)
    country = models.CharField(max_length=100,null=True,blank=True)
    state = models.CharField(max_length=100,null=True,blank=True)
    city = models.CharField(max_length=100,null=True,blank=True)
    current_slot = models.IntegerField(null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return f"{self.machine_name} ({self.machine_code})"

class MachineSubscription(models.Model):
    machine = models.OneToOneField(Machine, on_delete=models.CASCADE, related_name='subscription')
    license_key = models.CharField(max_length=19, unique=True, default=generate_license_key, editable=False)
    start_date = models.DateField()
    end_date = models.DateField()
    subscription_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CameraFeed(models.Model):
    CAMERA_TYPE_CHOICES = [
        ('VALIDATION', 'Validation Camera'),
        ('ENTRANCE_LEFT', 'Entrance Left Camera'),
        ('ENTRANCE_RIGHT', 'Entrance Right Camera'),
        ('ENTRANCE_POS', 'Entrance POS Camera'),
        ('CHAMBER_TOP', 'Chamber Top Camera'),
        ('CHAMBER_BOTTOM', 'Chamber Bottom Camera'),
    ]

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='camera_feeds')
    camera_name = models.CharField(max_length=100)
    camera_type = models.CharField(
        max_length=50,
        choices=CAMERA_TYPE_CHOICES,
        help_text="Select the type of camera"
    )
    feed_url = models.CharField(
        max_length=500,
        help_text="Enter the camera feed URL or RTSP stream address"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['machine', 'camera_name']

    def __str__(self):
        return f"{self.machine.machine_name} - {self.camera_name}"

class Zone(models.Model):
    camera_feed = models.ForeignKey(CameraFeed, on_delete=models.CASCADE, related_name='zones')
    zone_name = models.CharField(max_length=100)
    zone_coordinates = models.JSONField(help_text="Format: {'x1': 0, 'y1': 0, 'x2': 100, 'y2': 100}")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['camera_feed', 'zone_name']

    def __str__(self):
        return f"{self.camera_feed.camera_name} - {self.zone_name}"

class Line(models.Model):
    camera_feed = models.ForeignKey(CameraFeed, on_delete=models.CASCADE, related_name='lines')
    line_name = models.CharField(max_length=100)
    line_coordinates = models.JSONField(help_text="Format: {'x1': 0, 'y1': 0, 'x2': 100, 'y2': 100}")
    line_type = models.CharField(max_length=50, choices=[
        ('entry', 'Entry Line'),
        ('exit', 'Exit Line'),
        ('counting', 'Counting Line')
    ])
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['camera_feed', 'line_name']

    def __str__(self):
        return f"{self.camera_feed.camera_name} - {self.line_name}"

class AIModel(models.Model):
    MODEL_TYPE_CHOICES = [
        ('YOLOV5', 'YOLOv5'),
        ('YOLOV7', 'YOLOv7'),
        ('YOLOV8', 'YOLOv8'),
        ('YOLOV8_SEG', 'YOLOv8 Segmentation'),
        ('YOLOV8_POSE', 'YOLOv8 Pose'),
    ]

    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)
    model_type = models.CharField(
        max_length=50,
        choices=MODEL_TYPE_CHOICES,
        help_text="Select the type of AI model"
    )
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version}"

class CameraAIModel(models.Model):
    camera_feed = models.ForeignKey(CameraFeed, on_delete=models.CASCADE, related_name='ai_models')
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    configuration = models.JSONField(default=dict, help_text="Model-specific configuration parameters")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['camera_feed', 'ai_model']

    def __str__(self):
        return f"{self.camera_feed.camera_name} - {self.ai_model.name}" 
    

class sku(models.Model):
    variant_sku = models.CharField(max_length=250)
    variant_type = models.CharField(max_length=250)
    variant_weight = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SKU - {self.variant_sku}"




    