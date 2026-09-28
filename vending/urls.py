from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'machines', views.MachineViewSet)
router.register(r'subscriptions', views.MachineSubscriptionViewSet)
router.register(r'cameras', views.CameraFeedViewSet)
router.register(r'zones', views.ZoneViewSet)
router.register(r'lines', views.LineViewSet)
router.register(r'ai-models', views.AIModelViewSet)
router.register(r'camera-ai-models', views.CameraAIModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('check-subscription/', views.MachineSubscriptionCheckView.as_view(), name='check-machine'),
    path('create-new-mac/', views.CreateNewMAC.as_view(), name='create-new-mac'),
] 