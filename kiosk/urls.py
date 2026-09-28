from django.urls import path
from .views import *
from kiosk import views

# from .constants import API_ENDPOINTS 

urlpatterns = [
    # Account endpoints
    path('validation-info/', ValidationInfo.as_view(), name='validation-info'),
    path('validation-process/', ValidationProcess.as_view(), name='validation-process'),
    path('validation-success/', ValidationSuccess.as_view(), name='validation-process'),
    path('placement-refill/', PlacementRefill.as_view(), name='placement-refill'),
    path('customer-details/', CustomerDetails.as_view(), name='customer-details'),
    path('payment-process/', PaymentProcess.as_view(), name='payment-process'),

    path('get-authtoken/', GenerateAuthToken.as_view(), name='get-authtoken'),
    path('get-inventory/', CheckStockSummaryView.as_view(), name='get-inventory'),
    path('get-inventory/<str:sku_value>/', CheckStockSummaryView.as_view(), name='get-inventory-sku'),

    path('get-ai-response/', GetAIResponse.as_view(), name='cylinder-validation'),
    path('collect-empty/', EmptyCollection.as_view(), name='collect-empty'),
    path('return-empty/', ReturnEmptyView.as_view(), name='return-empty'),
    path('dispense-filled/', DispenseFilledView.as_view(), name='dispense-filled'),


    path('Process/InvokeAIValidation/', InvokeAIValidation.as_view(), name='payment-process'),
    path('Process/InvokeCylinderPlacement', InvokeCylinderPlacement.as_view(), name='payment-process'),
    path('Process/PlacementValidation', PlacementValidation.as_view(), name='payment-process'),
    path('api/Consumer/FilledCylinder', FilledCylinder.as_view(), name='payment-process'),
    path('api/Consumer/consumertransaction', consumertransaction.as_view(), name='payment-process'),

    path('getmacaddress/', GetMacAddress.as_view(), name='Get Mac address'), 
    path('pcb-response/', PcbResponse.as_view(), name='pcb-response'),
    path('pcb-integration/', PcbIntegration.as_view(), name='pcb-integration'),
    path('bda/filled-validation/', FilledCylinderValidation.as_view(), name='bda-filled-validation'),
    path('bda/receive-filled/', FilledCylinderReceive.as_view(), name='bda-receive-filled'),
    path('bda/collect-empty/', CollectEmptyCylinder.as_view(), name='bda-collect-empty'),
    path('bda/collect-filled/', CollectFilledCylinder.as_view(), name='bda-collect-filled'),
    path('check-ai-initiation/', InitiateAIValidtion.as_view(), name='Check Ai initiation'),
    path('get-kiosk-id/', GetKioskInfo.as_view(), name='kiosk-info'),
    path('reset-stock/', ResetStock.as_view(), name='reset-stock'),
    path('/id-proof/scan-window', IDProofScanWindowView.as_view(), name="id-proof-scan-window")
]