from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import (
    Machine, 
    MachineSubscription, 
    CameraFeed,
    Zone,
    Line,
    AIModel,
    CameraAIModel
)
from .serializers import (
    MachineDetailSerializer,
    MachineSubscriptionDetailSerializer,
    CameraFeedDetailSerializer,
    ZoneSerializer,
    LineSerializer,
    AIModelDetailSerializer,
    CameraAIModelSerializer
)
from django.utils import timezone
from datetime import datetime

class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        machine = self.get_object()
        serializer = MachineDetailSerializer(machine)
        return Response(serializer.data)

class MachineSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = MachineSubscription.objects.all()
    serializer_class = MachineSubscriptionDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class CameraFeedViewSet(viewsets.ModelViewSet):
    queryset = CameraFeed.objects.all()
    serializer_class = CameraFeedDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticated]

class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    serializer_class = LineSerializer
    permission_classes = [permissions.IsAuthenticated]

class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

class CameraAIModelViewSet(viewsets.ModelViewSet):
    queryset = CameraAIModel.objects.all()
    serializer_class = CameraAIModelSerializer
    permission_classes = [permissions.IsAuthenticated]

class MachineSubscriptionCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        machine_id = request.data.get('machine_id')
        
        if not machine_id:
            return Response(
                {'error': 'machine_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get machine or return 404
        machine = get_object_or_404(Machine, machine_id=machine_id)

        # Check if subscription exists and is valid
        try:
            subscription = machine.subscription
            today = timezone.now().date()

            # Check if subscription is active and within valid dates
            if not subscription.is_active:
                return Response(
                    {
                        'error': 'Subscription is not active',
                        'machine_id': machine_id,
                        'subscription_status': 'inactive'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if subscription has expired
            if today > subscription.end_date:
                return Response(
                    {
                        'error': 'Subscription has expired',
                        'machine_id': machine_id,
                        'subscription_status': 'expired',
                        'expiry_date': subscription.end_date
                    },
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if subscription hasn't started yet
            if today < subscription.start_date:
                return Response(
                    {
                        'error': 'Subscription has not started yet',
                        'machine_id': machine_id,
                        'subscription_status': 'pending',
                        'start_date': subscription.start_date
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        except MachineSubscription.DoesNotExist:
            return Response(
                {
                    'error': 'No subscription found',
                    'machine_id': machine_id,
                    'subscription_status': 'not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # If subscription exists, is active, and within valid dates, return machine details
        serializer = MachineDetailSerializer(machine)
        return Response({
            'message': 'Subscription is valid',
            'subscription_status': 'active',
            'valid_until': subscription.end_date,
            'machine_details': serializer.data
        }) 

def format_date(date_str, date_format='%Y-%m-%d %H:%M'):
    """Helper function to format the date with flexible parsing."""
    if date_str:
        # Parse the date string with the appropriate format
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f%z')  # Updated format
        except ValueError:
            date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')  # Fallback format
        return date_obj.strftime(date_format)
    return None
    
class CreateNewMAC(APIView):
    permission_classes = []
    def post(self, request):
        post = request
        print(request)
        macaddr = post.data['machine_id']
        if macaddr:
            machinelist= Machine.objects.filter(machine_code=macaddr).values().first()
            machinelist['created_at'] = format_date(str( ['created_at']))
            if machinelist:
                return Response({"status":2,"message" : "Machine code already exist","data":machinelist},status=status.HTTP_200_OK) 
            else:
                Machine.objects.create(machine_id=macaddr,machine_code=macaddr)
                machine=Machine.objects.values().filter(machine_id=macaddr).first()
                return Response({"status":1,"message" : "Machine registered successfully","detail": machine},status=status.HTTP_200_OK) 
            

