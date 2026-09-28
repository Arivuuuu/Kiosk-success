from datetime import datetime, timezone
import json
import os
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from kiosk.models import AuthToken, EmptyCollect
from rest_framework.views import APIView
from .constants import API_ENDPOINTS, API_RESPONSE
from rest_framework.permissions import IsAuthenticated
from django.template import RequestContext
import uuid
import requests
from rest_framework_simplejwt.tokens import AccessToken
from project import settings
from . import utils
import vending.models as vmodels
from .models import CylinderValidate, ReturnEmpty, StockInventory, Machine, ChamberSlots, ChamberStockInventory, EmptyCollect, DispenseFilled, BDA_Transactions,Customer_Transactions
from datetime import datetime,timedelta
from django.utils import timezone

class ValidationInfo(generic.View):
    def get(self, request):
        return render(
            request,
            'validation-info.html', 
            {}
            )

class ValidationProcess(generic.View):
    def get(self, request):
        return render(
            request,
            'validation-process.html',
            {}
            )
    
class ValidationSuccess(generic.View):
    def get(self, request):
        return render(
            request,
            'validation-success.html',
            {}
            )
class PlacementRefill(generic.View):
    def get(self, request):
        return render(
            request,
            'placement-refill.html',
            {}
            )
class CustomerDetails(generic.View):
    def get(self, request):
        return render(
            request,
            'customer-details.html',
            {}
            )

class PaymentProcess(generic.View):
    def get(self, request):
        return render(
            request,
            'payment-process.html',
            {}
        )

#  AI Validation for Empty Cylinder   
class InvokeAIValidation(APIView):
    def post(self,request):
        if 'Authorization' in request.headers:
            return ({'process': True,'date': '<datetime>'})
        else:
            return ({'process': False,'message':'Authentication is required'})

class GetAIResponse(APIView):
    def post(self,request):
        data = request.data
        kioskid = data.get('kioskid','')
        referenceid = data.get('referenceid','')
        variant = data.get('variant','')
        sku = data.get('sku','')

        if utils.check_empty(kioskid):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
        if utils.check_empty(referenceid):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['REF_ID_EMPTY'],'details':''})
        # if utils.check_empty(variant):
        #     return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['VARIANT_EMPTY'],'details':''})
        if utils.check_empty(sku):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['SKU_EMPTY'],'details':''})
        check_kiosk = utils.check_kiosk(kioskid)

        if not check_kiosk:
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})
        
        #CylinderValidate.objects.create(kiosk_id=check_kiosk['id'], reference_id=referenceid,sku=sku,variant=variant)
        #cylinder_validating_url = API_ENDPOINTS['KIOSK_URL'] + 'GetAIResponse?timeout=45'

        #try:
        if True:

            return utils.customer_transaction(1, request)
            #validation_request = requests.get(cylinder_validating_url ,request.data)
            validation_request = False
            isSuccess = False
            if validation_request:
                data = validation_request.json()
                isSuccess = data['isTrackingValid']
            if not isSuccess:
                isSuccess = utils.get_random_resp()
                isSuccess = True
                if isSuccess:
                    data['ValidationDetails'] = {'validation_details':'Success'}
                    data['isValidCylinder'] = True
            if isSuccess:
                #CylinderValidate.objects.filter(reference_id=referenceid).update(response_at=datetime.now(),validate_data=data)
                if data['isValidCylinder']==True:
                    return utils.send_response({'status':API_RESPONSE['SUCCESS'], 'message': API_RESPONSE['VALIDATION_SUCCESS'], 'details':"cylinder validation success",'response_data': [data['ValidationDetails']]})
                else:
                    return utils.send_response({'status':API_RESPONSE['FAILED'], 'message': API_RESPONSE['VALIDATION_FAILED'], 'details': data['ValidationDetails']})
            else:
                return utils.send_response({
                    'status':  API_RESPONSE['FAILED'],
                    'message': API_RESPONSE['VALIDATION_FAILED'],
                    'details': 'System Error. Cylinder validation failed' 
                })
        #except Exception as e:
        #    return utils.send_response({
        #        'status': API_RESPONSE['FAILED'],
        #        'message': API_RESPONSE['VALIDATION_FAILED'],
        #        'details': 'System Error. Cylinder validation failed'+str(e)
        #    })


# class EmptyCollection(APIView):
#     permission_classes = []

#     def post(self, request):
#         data = request.data
#         kioskid = data.get('kioskid')
#         referenceid = data.get('referenceid')

#         if utils.check_empty(kioskid):
#             return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_EMPTY'], 'details': ''})
        
#         if utils.check_empty(referenceid):
#             return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['REF_ID_EMPTY'], 'details': ''})
        
#         check_kiosk = utils.check_kiosk(kioskid)
#         if not check_kiosk:
#             return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_INVALID'], 'details': ''})
#         slots = utils.get_slot(kioskid, 3, single_row=True)
#         chamber = ChamberStockInventory.objects.filter(id=slots['chamber_id']).values('chamber').first()
#         cylinder_tracking_door1_url = API_ENDPOINTS['KIOSK_URL'] + 'InvokeAITracking?timeout=45&doorToTrack='+ str(slots['slot_number'])
#         empty = EmptyCollect.objects.filter(kiosk_id=check_kiosk['id']).values('response_at').last()
#         if empty['response_at'] is None:
#             return utils.send_response({
#                 'status': API_RESPONSE['FAILED'],
#                 'message': API_RESPONSE['EMPTY_COLLECT_FAILED'],
#                 'details': 'Cylinder collection validation already in progress. Please wait.'
#             })
#         empty_collect = EmptyCollect.objects.create(kiosk_id=check_kiosk['id'], reference_id=referenceid, slot_id=slots['id'], chamber_id=slots['chamber_id'])
#         try:
#             tracking_success = requests.get(cylinder_tracking_door1_url, request.data)
#             tracking_data = tracking_success.json() 
#             EmptyCollect.objects.filter(reference_id=referenceid).update(response_at=timezone.now(), tracking_data=tracking_data)
#             if tracking_success:
#                 if tracking_data['isTrackingValid'] == True:
#                     ChamberSlots.objects.filter(id=empty_collect.slot_id).update(status=0)
#                     return utils.send_response({
#                         'status': API_RESPONSE['SUCCESS'],
#                         'message': API_RESPONSE['EMPTY_COLLECT_SUCCESS'],
#                         'details': 'Validated empty cylinder collected in chamber'
#                     })
#                 else:
#                     return utils.send_response({
#                         'status': API_RESPONSE['FAILED'],
#                         'message': API_RESPONSE['EMPTY_COLLECT_FAILED'],
#                         'details': tracking_data['trackingDetails']
#                     })
#             else:
#                 return utils.send_response({
#                     'status': API_RESPONSE['FAILED'],
#                     'message': API_RESPONSE['EMPTY_COLLECT_FAILED'],
#                     'details': 'System Error. Cylinder collection failed'
#                 })
#         except Exception as e:
#             return utils.send_response({
#                 'status': API_RESPONSE['FAILED'],
#                 'message': API_RESPONSE['EMPTY_COLLECT_FAILED'],
#                 'details': 'System Error. Cylinder collection failed'
#             })




# Live Tracking for Cylinder Placement
class InvokeCylinderPlacement(APIView):       
    def post(self,request):
        if 'Authorization' in request.headers:
            return ({'doorToOpen': 1,'date': '<datetime>'})
        else:
            return ({'doorToOpen': 2,'message':'Authentication is required'})
        
class PlacementValidation(APIView):       
    def post(self,request):
        if 'IsValidatedCylinder' in request and request.data['IsValidatedCylinder'] is True:
            if 'validationDetails' in request.data:
                return ({'responseCode': 1,'IsValidatedCylinder': True,'validationDetails': 'Cylinder placed successfully','date': '<datetime>'})
            else:
                return ({'responseCode': 2,'IsValidatedCylinder': False,'validationDetails': 'Cylinder is not validated'})
        else:

            return ({'responseCode': 2,'IsValidatedCylinder': False,'validationDetails': 'Validation Fails.Try Again'})
        
# Filled Cylinder Dispensing
class FilledCylinder(APIView):       
    def post(self,request):
        data=request.data
        if 'KioskID' in data and data['KioskID'] is not None and data['KioskID'] !='':
            if 'CylinderVariantID' in data and data['CylinderVariantID'] is not None and data['CylinderVariantID'] !='':
                if 'TransactionType' in data and data['TransactionType'] is not None and data['TransactionType'] !='':
                    if 'ChamberID' in data and data['ChamberID'] is not None and data['ChamberID'] !='':
                        if 'CylinderVariant' in data and data['CylinderVariant'] is not None and data['CylinderVariant'] !='':
                            return ({'status': 'Dispensed','transactionDetailsID': '<long>'})
                        else:
                            return ({'status': 'NotDispensed','message': 'CylinderVariant is missing'})
                    else:
                        return ({'status': 'NotDispensed','message': 'ChamberID is missing'})
                else:
                    return ({'status': 'NotDispensed','message': 'TransactionType is missing'})
            else:
                return ({'status': 'NotDispensed','message': 'CylinderVariantID is missing'})
        else:
            return ({'status': 'NotDispensed','message': 'Kiosk Id is missing'})
        
# Transaction Completion & Inventory Update
class consumertransaction(APIView):       
    def post(self,request):
        data=request.data
        if 'TransactionDetailID' in data and data['TransactionDetailID'] is not None and data['TransactionDetailID'] !='':
            if 'TransactionType' in data and data['TransactionType'] is not None and data['TransactionType'] !='':
                if 'PaymentAmount' in data and data['PaymentAmount'] is not None and data['PaymentAmount'] !='':
                    if 'PaymentStatus' in data and data['PaymentStatus'] is not None and data['PaymentStatus'] !='':                   
                            return ({'status': 'Completed','updatedInventory': [{ 'SKU': '<string>', 'quantity': '<integer>' }]})
                    else:
                        return ({'status': 'InCompleted','message':'PaymentStatus is missing'})
                else:
                    return ({'status': 'InCompleted','message':'PaymentAmount is missing'})
            else:
                return ({'status': 'InCompleted','message':'TransactionType is missing'})
        else:
            return ({'status': 'InCompleted','message':'TransactionDetailID is missing'})

class GetMacAddress(APIView):   
    def post(self,request):
        mac = hex(uuid.getnode()).replace('0x', '').zfill(12)
        mac_address = ':'.join(mac[i:i+2] for i in range(0, 12, 2))  
        data = {'machine_id': mac_address}
        response = JsonResponse(data)       
        return response

class GenerateAuthToken(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self,request):
        kiosk_id = request.data.get('kioskid')
        if utils.check_empty(kiosk_id):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
        else:
            current_time =  datetime.now()
            kioskid = request.data['kioskid']
            machine = utils.check_kiosk(kioskid)
            if not machine:
                return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})

            token = AuthToken.objects.filter(kiosk_id=machine['id'], is_active=True).values().last()
            if token:
                #if current_time >= token['expire_at'].astimezone(timezone.utc).replace(tzinfo=None):
                AuthToken.objects.filter(kiosk_id=machine['id'], is_active=True).update(is_active=False, updated_at=current_time)

            to_be_expire = current_time + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
            auth_token = AccessToken() 
            auth_token['kiosk_id'] = kioskid
            AuthToken.objects.create(kiosk_id=machine['id'],auth_token=auth_token,is_active=True,expire_at=to_be_expire)

            return utils.send_response({'status':'success','message' : 'Token Created Successfully','details':{'token':str(auth_token)}})


class CheckStockSummaryView(APIView):
    # permission_classes = []
    def post(self, request, sku_value=None):
        kiosk_id = request.data.get('kioskid')
        if utils.check_empty(kiosk_id):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
        check_kiosk = utils.check_kiosk(kiosk_id)

        if not check_kiosk:
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})
        response_data = []
        related_stock = StockInventory.objects.filter(kiosk__machine_code=kiosk_id)

        if sku_value:
            related_stock = related_stock.filter(sku__variant_sku=sku_value)

        if not related_stock.exists():
            return utils.send_response({
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['STOCK_EMPTY'],
                'details':''
            })

        empty_slots = utils.get_slot(check_kiosk['id'], 3, single_row=False)  
        empty_slot_count = len(empty_slots) if empty_slots else 0
            
        for sku_item in related_stock:
            response_data.append({
                'sku': sku_item.sku.variant_sku,
                'stock': {
                    'empty': sku_item.empty_stock,
                    'filled': sku_item.filled_stock
                }
            })
        response_data.append({
            'sku': 'EMPTY_SLOT',
            'stock': {
                'empty': empty_slot_count,
                'filled': 0
            }
        })
        return utils.send_response({'status':API_RESPONSE['SUCCESS'],'message':'Stock details fetched','details':'stock details fetched successfully','response_data':response_data})

class PcbResponse(APIView):
    def get(self,request):
        response=request.get(API_ENDPOINTS['KIOSK_URL']+'Process/GetPcbResponse')
        return utils.send_response(response)

    def post(self, request):
        data = json.load(request.body)
    
        kiosk_id = data.get('kioskid')  
        if utils.check_empty(kiosk_id):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
        check_kiosk = utils.check_kiosk(kiosk_id)

        if not check_kiosk:
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})

        rotation = data.get('rotation')
        chamber_door_1 = data.get('chamber_door_1')
        chamber_door_2 = data.get('chamber_door_2')
        reset_alarm = data.get('reset_alarm')
        
        
        if rotation is None:
            return Response({'status': API_RESPONSE['FAILED'],'message': API_RESPONSE['ROTATION_REQUIRED'],'details':''}, status=status.HTTP_200_OK)
        if chamber_door_1 is None:
            return Response({'status': API_RESPONSE['FAILED'],'message': API_RESPONSE['CHAMBER_DOOR_1'],'details':''},status=status.HTTP_200_OK)
        if chamber_door_2 is None:
            return Response({'status': API_RESPONSE['FAILED'],'message': API_RESPONSE['CHAMBER_DOOR_2'],'details':''},status=status.HTTP_200_OK)
        if reset_alarm is None:
            return Response({'status': API_RESPONSE['FAILED'],'message': API_RESPONSE['RESET_ALARM'],'details':''}, status=status.HTTP_200_OK)

        data = {
            'rotation': rotation,
            'chamber_door_1': chamber_door_1,
            'chamber_door_2': chamber_door_2,
            'reset_alarm'   : reset_alarm
        }
        response=requests.post(API_ENDPOINTS['PCB_URL']+'/Process/UpdatePCB',data) 
        return utils.send_response(response)
    
# class ReturnEmptyView(APIView): 
#     permission_classes = []
#     def post(self, request):
#         data = request.data
#         kioskid = data.get('kioskid')
#         referenceid = data.get('referenceid')
#         if utils.check_empty(kioskid):
#             return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
#         if utils.check_empty(referenceid):
#             return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['REF_ID_EMPTY'],'details':''})
#         check_kiosk = utils.check_kiosk(kioskid)
#         if not check_kiosk:
#             return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})
#         ReturnEmpty.objects.create(kiosk_id=check_kiosk['id'], reference_id=referenceid)
#         cylinder_reverse_tracking_chambernumber = API_ENDPOINTS['KIOSK_URL'] + 'InvokeReverseTracking?timeout=45&chamberNumber=2'
#         try:
#             reverse_tracking_success = requests.post(cylinder_reverse_tracking_chambernumber,request.data)
#             if reverse_tracking_success:
#                 reverse_tracking_data = reverse_tracking_success.json()
#                 ReturnEmpty.objects.filter(reference_id=referenceid).update(response_at=datetime.now(),tracking_data=reverse_tracking_data)
#                 if reverse_tracking_data['isTrackingValid'] == True:
#                     return utils.send_response({'status':API_RESPONSE['SUCCESS'],'message':API_RESPONSE['EMPTY_CYLINDER_RETURNED'],'details':'empty cylinder returned to consumer'})   
#                 else:
#                     return utils.send_response({
#                         'status': API_RESPONSE['FAILED'],
#                         'message': API_RESPONSE['RETURN_EMPTY_COLLECT_FAILED'],
#                         'details': reverse_tracking_data['trackingDetails']
#                     })
#             else:
#                 return utils.send_response({
#                     'status':  API_RESPONSE['FAILED'],
#                     'message': API_RESPONSE['RETURN_EMPTY_COLLECT_FAILED'],
#                     'details': 'System Error. Return empty cylinder collection failed' 
#                 })
#         except Exception as e:
#             return JsonResponse({
#                 'status': API_RESPONSE['FAILED'],
#                 'message': str(e),
#                 'details': 'An unexpected error occurred'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PcbIntegration(APIView):
    def post(self, request):
        kioskid = request.data.get("kioskid")

        if utils.check_empty(kioskid):
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_EMPTY'], 'details': ''})

        check_kiosk = utils.check_kiosk(kioskid)

        if not check_kiosk:
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_INVALID'], 'details': ''})

        stock_inventories = StockInventory.objects.filter(kiosk__machine_code=kioskid)

        if not stock_inventories:
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': 'No stock inventory found for this kiosk', 'details': ''})

        chamber_stock_inventories = ChamberStockInventory.objects.filter(stock_inventory__in=stock_inventories)

        if not chamber_stock_inventories:
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': 'No chamber stock inventory found', 'details': ''})

        combined_data = []
        
        for chamber_number in chamber_stock_inventories:
            chamber_data = {
                'chamber': chamber_number.chamber
            }

            chamber_slots = ChamberSlots.objects.filter(chamber=chamber_number)
            slots_data = []
            for chamber_slot in chamber_slots:
                slot_datas = {
                    'slot_number': chamber_slot.slot_number,
                    'status': chamber_slot.status,
                } 
                slots_data.append(slot_datas)
            chamber_data['slots'] = slots_data
            combined_data.append(chamber_data)

        return utils.send_response({
            'status': API_RESPONSE['SUCCESS'],
            'message': 'Chamber stock and slots retrieved successfully',
            'details': combined_data
        }) 

# class DispenseFilledView(APIView):
#     # permission_classes = []
#     def post(Self, request):
#         data = request.data
#         kioskid = data.get('kioskid')
#         referenceid = data.get('referenceid') 
#         if utils.check_empty(kioskid):
#             return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
#         if utils.check_empty(referenceid):
#             return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['REF_ID_EMPTY'],'details':''})
#         check_kiosk = utils.check_kiosk(kioskid)
#         if not check_kiosk:
#             return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})
#         DispenseFilled.objects.create(kiosk_id=check_kiosk['id'], reference_id=referenceid)
#         dispense_filled = API_ENDPOINTS['KIOSK_URL'] + 'InvokeReverseTracking?timeout=45&chamberNumber=2'
#         try:
#             dispense_filled_success = requests.get(dispense_filled,request.data)
#             if dispense_filled_success:
#                 reverse_tracking_data = dispense_filled_success.json()
#                 DispenseFilled.objects.filter(reference_id=referenceid).update(response_at=datetime.now(),tracking_data=reverse_tracking_data)
#                 if reverse_tracking_data['isTrackingValid'] == True:
#                     return utils.send_response({'status':API_RESPONSE['SUCCESS'],'message':API_RESPONSE['DISPENSED_FILLED'],'details':'Dispensed cylinder collected'})   
#                 else:
#                     return utils.send_response({
#                         'status': API_RESPONSE['FAILED'],
#                         'message': API_RESPONSE['DISPENSED_FILLED_COLLECT_FAILED'],
#                         'details': reverse_tracking_data['trackingDetails']
#                     })
#             else:
#                 return utils.send_response({
#                     'status':  API_RESPONSE['FAILED'],
#                     'message': API_RESPONSE['DISPENSED_FILLED_COLLECT_FAILED'],
#                     'details': 'System Error. Dispensed cylinder collection failed' 
#                 })
#         except Exception as e:
#             return JsonResponse({
#                 'status': API_RESPONSE['FAILED'],
#                 'message': API_RESPONSE['DISPENSED_FILLED_COLLECT_FAILED'],
#                 'details': 'System Error. Dispensed cylinder collection failed'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FilledCylinderValidation(APIView):
    def post(self,request):
        return utils.init_bda_transaction(1, request)

class FilledCylinderReceive(APIView):
    def post(self,request):
        return utils.init_bda_transaction(2, request)

class CollectEmptyCylinder(APIView):
    def post(self,request):
        return utils.init_bda_transaction(3, request)

class CollectFilledCylinder(APIView):
    def post(self,request):
        return utils.init_bda_transaction(4, request)

class EmptyCollection(APIView):
    def post(self,request):
        return utils.customer_transaction(2, request)
    
class ReturnEmptyView(APIView):
    def post(self,request):
        return utils.customer_transaction(3, request)    

class DispenseFilledView(APIView):
    def post(self,request):
        return utils.customer_transaction(4, request)        
    
class InitiateAIValidtion(APIView):
    def post(self,request):
        kioskid = request.data.get('kioskid')
        type = request.data.get('type')
        if utils.check_empty(kioskid):
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_EMPTY'], 'details': ''})
        if utils.check_empty(type):
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': 'Type is empty', 'details': ''})
        kiosk = utils.check_kiosk(kioskid)
        if not kiosk:
            return utils.send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_INVALID'], 'details': ''})
        if type == 1:
            customer_transaction = Customer_Transactions.objects.filter(kiosk_id=kiosk['id'],slot_id__isnull=True,response_at__isnull=True).values('id','txn_type','reference_id').order_by('id').first()
            if customer_transaction:
                """ customer_transaction['current_slot'] = kiosk['current_slot']
                slots = utils.get_slot(kiosk['id'],3,True)
                customer_transaction['slot'] = slots['slot_number']
                customer_transaction['slot_id'] = slots['id']
                customer_transaction['transaction'] = 'customer'
                
                print('customer_transaction',customer_transaction) """

                current_slot = kiosk['current_slot']
                customer_transaction['current_slot'] = current_slot
                slots = utils.get_slot(kiosk['id'],3,True)
                slot = slots['slot_number']
                customer_transaction['slot'] = slot
                rotation, chamber = utils.get_nearest_rotation(current_slot, slot, 9)
                customer_transaction['rotation'] = rotation
                customer_transaction['chamber'] = chamber
                customer_transaction['slot_id'] = slots['id']
                customer_transaction['transaction'] = 'customer'
                return utils.send_response({
                    'status': API_RESPONSE['SUCCESS'],
                    'message': API_RESPONSE['VALIDATION_PROGRESS'],
                    'details': 'Validation in progress',
                    'response_data':  customer_transaction,
                })
            else:
                bda_transaction = BDA_Transactions.objects.filter(kiosk_id=kiosk['id'],response_at__isnull=True,slot_id__isnull=True).values('id','txn_type','reference_id').order_by('id').first()
                if bda_transaction:
                    current_slot = kiosk['current_slot']
                    bda_transaction['current_slot'] = current_slot
                    slots = utils.get_slot(kiosk['id'],3,True)
                    slot = slots['slot_number']
                    bda_transaction['slot'] = slot
                    rotation, chamber = utils.get_nearest_rotation(current_slot, slot, 9)
                    bda_transaction['rotation'] = rotation
                    bda_transaction['chamber'] = chamber
                    bda_transaction['slot_id'] = slots['id']
                    bda_transaction['transaction'] = 'bda'
                    return utils.send_response({
                        'status': API_RESPONSE['SUCCESS'],
                        'message': API_RESPONSE['VALIDATION_PROGRESS'],
                        'details': 'Validation in progress',
                        'response_data': bda_transaction,
                    })
                else:
                    return utils.send_response({
                        'status': API_RESPONSE['SUCCESS'],
                        'message': API_RESPONSE['VALIDATION_PROGRESS'],
                        'details': 'Validation in progress',
                        'response_data': [],
                    })
        elif type == 2:
            response_data = request.data.get('response_data')
            response_data[0]['isValidCylinder'] = True
            if response_data and (response_data[0]['isValidCylinder'] or response_data[0]['isTrackingValid']) == True:
                validResponse = True
            else:
                validResponse = False
            update_data = {
                'response_at': timezone.make_aware(datetime.now()),
                'validate_data': request.data.get('response_data'),
            }
            if validResponse:
                update_data['txn_complete'] = 1
                update_data['slot_id'] = request.data.get('slot_id')
                utils.update_slot(kiosk['id'], request.data.get('slot_id'), 1)
                # ChamberSlots.objects.filter(id=update_data['slot_id']).update(status=1)
            else:
                update_data['txn_complete'] = 0
            if request.data.get('transaction') == 'customer':       
                Customer_Transactions.objects.filter(id=request.data.get('id')).update(**update_data)
            elif request.data.get('transaction') == 'bda':
                BDA_Transactions.objects.filter(id=request.data.get('id')).update(**update_data)
            else:
                return utils.send_response({
                    'status': API_RESPONSE['FAILED'],
                    'message': API_RESPONSE['VALIDATION_FAILED'],
                    'details': 'Invalid transaction '
                })
            return utils.send_response({
                'status': API_RESPONSE['SUCCESS'],
                'message': API_RESPONSE['TRANSACTION_SUCCESS'],
                'details': 'Transaction is completed'
            })

class GetKioskInfo(APIView):
    def post(self,request):
        data = request.data
        mac = data.get('mac','')

        if utils.check_empty(mac):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':'MAC Address not provided','details':''})
        machine_info = utils.get_machine_info({'machine_id':mac})
        if not machine_info:
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':'MAC Address not registered','details':''})
        try:
            return utils.send_response({
                'status': API_RESPONSE['SUCCESS'],
                'message': 'Kiosk id fetched successfully',
                'details': 'Kiosk id fetched successfully',
                'response_data': [{
                    'kioskid': machine_info['machine_code'],
                }]
            })
        except Exception as e:
            return utils.send_response({
                'status': API_RESPONSE['FAILED'],
                'message': 'MAC Address Fetching Error',
                'details': 'System Error. Unable to fetch MAC address'
            })
        
class ResetStock(APIView):
    def post(self,request):
        data = request.data
        kioskid = data.get('kioskid')
        if utils.check_empty(kioskid):
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_EMPTY'],'details':''})
        check_kiosk = utils.check_kiosk(kioskid)

        if not check_kiosk:
            return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})
        
        sku_id = data.get('sku_id', 0)
        filled = data.get('filled', 0)
        empty = data.get('empty', 0)

        stock_inventory = StockInventory.objects.filter(kiosk__machine_code=kioskid)
        chamber_slot = ChamberSlots.objects.filter(kiosk__machine_code=kioskid)
        
        if sku_id:
            stock_inventory = stock_inventory.filter(sku__id=sku_id)
            stock_inventory.update(empty_stock=empty, filled_stock=filled)

            chamber_slot = chamber_slot.filter(sku_id__isnull=True)
        
            for chamber in chamber_slot[:filled + empty]:
                print(chamber.id)
                if filled > 0:
                    filled -= 1
                    chamber.status = 1  # Assuming 1 indicates filled
                    chamber.sku_id = sku_id
                    chamber.save()
                elif empty > 0:
                    empty -= 1
                    chamber.status = 0  # Assuming 0 indicates empty
                    chamber.sku_id = sku_id
                    chamber.save()
        if not sku_id:
            chamber_slot.update(status=3,sku_id=None)
            stock_inventory.update(empty_stock=0, filled_stock=0)
        #ChamberStockInventory.objects.filter(stock_inventory__kiosk__machine_code=kioskid).update(empty_stock=0, filled_stock=0)       
        
        return utils.send_response({
            'status': API_RESPONSE['SUCCESS'],
            'message': 'Stock reset successfully',
            'details': 'All stock and chamber slots have been reset to empty state'
        })
