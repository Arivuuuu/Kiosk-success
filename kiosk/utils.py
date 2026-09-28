from datetime import datetime, time
import os
from django.utils.timezone import make_aware
import json
from django.http import JsonResponse
import requests
from rest_framework import status
from django.http import JsonResponse
from kiosk.constants import API_RESPONSE, IS_LIVE
import vending.models as vmodels
import kiosk.models as kmodels
from .constants import API_ENDPOINTS, API_RESPONSE
from django.utils import timezone  
from datetime import datetime
import time as sleep_time


def check_empty(value):
    if type(value) != int and value is not None:
        value = value.strip()
    return value in ['',0,'0',None,'undefined','null']

def check_empty_finish(value):
    if type(value) != int and value is not None:
        value = value.strip()
    return value in ['','0',None,'undefined','null']


def send_response(data):
    if 'response_data' not in data:
        data['response_data'] = []
    return JsonResponse(data, status=status.HTTP_200_OK)

def get_random_resp():
    import random 
    rand = random.randint(5,100)
    print('rand',rand, rand % 2, (rand % 2 == 0))
    return True

def check_kiosk(kiosk):
    kiosk_info = vmodels.Machine.objects.filter(machine_code=kiosk, is_active=1).values().first()
    if kiosk_info is None:
        return None
    return kiosk_info

def get_slot(kiosk,status,single_row=True):
    if single_row:
        chamber_slots = kmodels.ChamberSlots.objects.filter(kiosk_id=kiosk,status=status).values('chamber_id','id','slot_number').first()
    else:
        chamber_slots = kmodels.ChamberSlots.objects.filter(kiosk_id=kiosk,status=status).values('chamber_id','id')
    return chamber_slots


def get_transaction_count(referenceid, type):
    if type == 1:
        return kmodels.BDA_Transactions.objects.filter(reference_id=referenceid, status=1).exclude(txn_type=1).count()
    elif type == 2:
        return kmodels.Customer_Transactions.objects.filter(reference_id=referenceid, status=1).exclude(txn_type=1).count()
    else:
        return send_response({"status": API_RESPONSE['INVALID_TRANSACTION_TYPE'], "message": "Invalid transaction type."})

import time
def init_bda_transaction(txn_type, request):
    kioskid = request.data.get('kioskid')
    referenceid = request.data.get('referenceid')
    sku = request.data.get('sku')
    total_count = request.data.get('total_count')
    is_finish = request.data.get('is_finish') or 0

    if check_empty(kioskid):
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_EMPTY'], 'details': ''})
    if check_empty(referenceid):
        return send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['REF_ID_EMPTY'],'details':''})
    if check_empty(sku):
        return send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['SKU_EMPTY'],'details':''})
    if check_empty(total_count) and txn_type not in [1,'1']:
        return send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['TOTAL_COUNT'],'details':''})
    if check_empty_finish('is_finish'):
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['FINISH_STATUS'], 'details': ''})

    kiosk = check_kiosk(kioskid)
    if not kiosk:
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_INVALID'], 'details': ''})   

    sku_instance = vmodels.sku.objects.filter(variant_sku=sku).values('id','variant_sku','variant_type').first()
    if not sku_instance:
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['VARIANT_SKU']})
    sku_id = sku_instance['id']

    bdaModel = kmodels.BDA_Transactions
    txn_info = bdaModel.objects.filter(reference_id=referenceid)

    """ if txn_info:
        if txn_type != 2:
            return send_response({'status': API_RESPONSE['SUCCESS'], 'message': API_RESPONSE['DUPLICATE_REF_ID'], 'details': 'Duplicate reference id'})
    el """

    if txn_info.filter(txn_complete = 1):
        return send_response({'status': API_RESPONSE['SUCCESS'], 'message': API_RESPONSE['TRANSACTION_ALREADY_COMPLETED'], 'details': 'Validation has already been completed'})
    
    if txn_type in [1,2]:
        sku_check = check_cylinder_validated(referenceid, sku_id, txn_type, bdaModel)
        if sku_check.get('status') != API_RESPONSE['SUCCESS']:
            return send_response(sku_check)

    count = get_transaction_count(referenceid, 1)
    if is_finish == 1 and count > 0:
        txn_info.update(txn_complete=is_finish)
        return send_response({
            'status': API_RESPONSE['SUCCESS'],
            'message': API_RESPONSE['TRANSACTION_SUCCESS'],
            'details': 'Transaction successfully completed and marked as finalized',
            'response_data':[{
                "validation_details":'The transaction was successfully completed',
                'count': count
            }]
        })

    bda_tnx = bdaModel.objects.filter(kiosk_id=kiosk['id']).order_by('-response_at').last()
    if bda_tnx and bda_tnx.response_at is None:
        return send_response({
            'status': API_RESPONSE['FAILED'],
            'message': API_RESPONSE['VALIDATION_PROGRESS'],
            'details': 'Validation already in progress. Please wait.'
        })

    lastTxnStatus = 0
    if bda_tnx is not None:
        lastTxnStatus = bda_tnx.status

    ref = bdaModel.objects.create(kiosk_id=kiosk['id'], reference_id=referenceid,sku_id=sku_id,total_count = total_count,txn_type=txn_type,txn_complete=is_finish)

    #count = get_transaction_count(referenceid, 1)
    kiosk_id = kiosk['id']
    if txn_type == 1:
        status = 3
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}GetAIResponse?timeout=45&ref_id={ref.id}"
        success_key = 'VALIDATION_SUCCESS'
        failure_key = 'VALIDATION_FAILED'

        detail_success = 'Cylinder validation success'
        failure_detail = 'Cylinder validation failed'
    elif txn_type == 2:
        status = 3
        update_status = 1
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}InvokeAITracking?timeout=45&doorToTrack=1&ref_id={ref.id}"
        success_key = 'FILLED_CYLINDER_COLLECT'
        failure_key = 'VALIDATION_FAILED'

        detail_success = 'Validated filled cylinder collected in chamber'
        failure_detail = 'Filled cylinder tracking failed'

    elif txn_type == 3:
        status = 0
        update_status = 3
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}InvokeAITracking?timeout=45&doorToTrack=1&ref_id={ref.id}"
        success_key = 'EMPTY_COLLECT_SUCCESS'
        failure_key = 'VALIDATION_FAILED'

        detail_success = 'Empty cylinder successfully collected by BDA'
        failure_detail = 'Empty cylinder tracking failed'
    elif txn_type == 4:
        status = 1
        update_status = 3
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}InvokeAITracking?timeout=45&doorToTrack=1&ref_id={ref.id}"
        success_key = 'FILLED_CYLINDER'
        failure_key = 'VALIDATION_FAILED'

        detail_success = 'Filled cylinder successfully collected by BDA'
        failure_detail = 'Filled cylinder tracking failed'
    else:
        return send_response({"status": API_RESPONSE['INVALID_TRANSACTION_TYPE'], "message": "Invalid transaction type."})
    slots = None
    if txn_type in [1, 2, 3, 4]:
        slots = get_slot(kiosk_id,status,True)
        slot_id = 0
        if slots is not None:
            slot_id = slots['id']
        #update_json_file('rotation',slots['slot_number'])

    try:
        if slot_id == 0:
            return send_response({"status": API_RESPONSE['FAILED'], "message": API_RESPONSE['STOCK'], "details": "No stock available"})
        if IS_LIVE:
            validation_request = requests.get(kiosk_url)
            data = validation_request.json()
        else:
            validation_request = True
            data = {'ref_id':ref.id,'isValidCylinder':True,'ValidationDetails':'Success','isTrackingValid':True,'trackingDetails':'Success'}
            if txn_type == 1:
                data['ValidationDetails'] = 'Cylinder validated successfully'
                data['skuDetails'] = {'variant':sku_instance['variant_type'],'sku':sku_instance['variant_sku']}
        if validation_request:
            #time.sleep(120)
            ref_id = data.get('ref_id')
            if txn_type == 1:   
                validResponse = data.get('isValidCylinder', False)
                validation_details = data.get('ValidationDetails', '') 
            elif txn_type in [2,3,4]:
                validResponse = data.get('isTrackingValid', False)
                validation_details = data.get('trackingDetails', '')

            if not IS_LIVE:
                validResponse = False if lastTxnStatus == 0 else get_random_resp()
                validResponse = True
                if not validResponse:
                    validation_details = failure_detail
            update_data = {
                'validate_data': data,
                'response_at': datetime.now(),
                'reference_id': referenceid
            }
            if validResponse: 
                update_data['status'] = 1
                update_data['ref_id'] = ref_id
                if txn_type in [2, 3, 4]:
                    update_data['slot'] = slot_id

                    chamber_data = {}
                    chamber_data['status'] = update_status
                    chamber_data['sku_id'] = None
                    if txn_type in [2]:
                        chamber_data['sku_id'] = sku_id

                    kmodels.ChamberSlots.objects.filter(id=slot_id).update(**chamber_data)
                    vmodels.Machine.objects.filter(id=kiosk_id).update(current_slot=slot_id)
                    update_stock_status(txn_type, sku_id, kiosk_id)
            else:
                update_data['status'] = 0
            bdaModel.objects.filter(id=ref.id).update(**update_data)
            response_status = API_RESPONSE['SUCCESS'] if validResponse else API_RESPONSE['FAILED']
            response_message = API_RESPONSE[success_key] if validResponse else API_RESPONSE[failure_key]
            response_details = detail_success if validResponse else validation_details

            return send_response({
                'status': response_status,
                'message': response_message,
                'details': response_details,
                'response_data': [{
                    "validation_details": validation_details,
                    'count': count
                }]
            })
        else:
            data = {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE[failure_key],
                'details': failure_detail,
                'response_data': [{
                    'count': count
                }]
            }
            bdaModel.objects.filter(id=ref.id).update(validate_data=data,response_at=datetime.now())
            return send_response(data)
    except Exception as e:
        data = {
            'status': API_RESPONSE['FAILED'],
            'message': API_RESPONSE['VALIDATION_FAILED'],
            'details': 'System Error. Cylinder validation failed'+str(e) ,
            'response_data':[{
                "validation_details": 'System Error. Cylinder validation failed',
                'count':count
            }]
        }
        bdaModel.objects.filter(id=ref.id).update(validate_data=data,response_at=datetime.now())
        return send_response(data)

def customer_transaction(txn_type, request):
    
    kioskid = request.data.get('kioskid')
    referenceid = request.data.get('referenceid')
    sku = request.data.get('sku')
    is_finish = request.data.get('is_finish') or 0

    if check_empty(kioskid):
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_EMPTY'], 'details': ''})
    if check_empty(referenceid):
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['REF_ID_EMPTY'], 'details': ''})
    if check_empty(sku):
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['SKU_EMPTY'], 'details': ''})
    kiosk = check_kiosk(kioskid)
    #current_slot(kiosk_id)
    if not kiosk:
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['KIOSK_INVALID'], 'details': ''})

    kiosk_id = kiosk['id']
    customerModel = kmodels.Customer_Transactions
    #customerModel.objects.filter(kiosk_id=kiosk_id,response_at__isnull=True).update(response_at=datetime.now())
    customer_tnx = customerModel.objects.filter(kiosk_id=kiosk_id).values().last()
    if customer_tnx is not None and customer_tnx['response_at'] is None:
        return send_response({
            'status': API_RESPONSE['FAILED'],
            'message': API_RESPONSE['VALIDATION_PROGRESS'],
            'details': 'Validation already in progress. Please wait.'
        })
    elif customer_tnx:
        lastTxnStatus = customer_tnx['status']

    sku_instance = vmodels.sku.objects.filter(variant_sku=sku).values('id','variant_type','variant_sku').first()
    if not sku_instance:
        return send_response({'status': API_RESPONSE['FAILED'], 'message': API_RESPONSE['VARIANT_SKU'], 'details': ''})
    sku_id = sku_instance['id']

    if txn_type in [1, 2]:
        check_slot = get_slot(kiosk_id,1, True)
        if check_slot is None:
            return send_response({"status": API_RESPONSE['FAILED'], "message": API_RESPONSE['STOCK'], "details": "Stock not available"})

    sku_check = check_sku_consistency(referenceid, sku_id, txn_type ,customerModel)
    if sku_check.get('status') != API_RESPONSE['SUCCESS']:
        return send_response(sku_check)

    ref = customerModel.objects.create(kiosk_id=kiosk_id, reference_id=referenceid, sku_id=sku_id, txn_type=txn_type)

    if txn_type == 1:
        update_status = 0
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}GetAIResponse?timeout=45&ref_id={ref.id}"
        success_key = 'VALIDATION_SUCCESS'
        failure_key ='VALIDATION_FAILED'

        detail_success = 'Cylinder validated successfully'
        failure_detail = 'Cylinder not placed in validation zone'

    elif txn_type == 2:
        update_status = 0
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}InvokeAITracking?doorToTrack=1&timeout=45&ref_id={ref.id}"
        success_key = 'EMPTY_COLLECT_SUCCESS'
        failure_key ='EMPTY_COLLECT_FAILED'

        detail_success = 'Validated empty cylinder collected in chamber'
        failure_detail = 'Cylinder out of visibility'
        status = 3

    elif txn_type == 3:
        update_status = 3
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}InvokeAITracking?doorToTrack=1&timeout=45&ref_id={ref.id}"
        success_key = 'EMPTY_CYLINDER_RETURNED'
        failure_key= 'RETURN_EMPTY_COLLECT_FAILED'

        detail_success = 'Empty cylinder returned to consumer'
        failure_detail= 'Cylinder not placed into chamber'
        status = 0

    elif txn_type == 4:
        update_status = 3
        kiosk_url = f"{API_ENDPOINTS['KIOSK_URL']}InvokeAITracking?doorToTrack=1&timeout=45&ref_id={ref.id}"
        success_key = 'DISPENSED_FILLED'
        failure_key = 'DISPENSED_FILLED_COLLECT_FAILED'

        detail_success = 'Dispensed cylinder collected'
        failure_detail = 'Dispensing error'
        status = 1
    else:
        return send_response({
            "status": API_RESPONSE['INVALID_TRANSACTION_TYPE'],
            "message": "Invalid transaction type.",
            'details': ''
        })
    if txn_type in [2, 3, 4]:
        slots = get_slot(kiosk_id,status,True)
        if slots is not None:
            slot_id = slots['id']
        else:
            return send_response({"status": API_RESPONSE['FAILED'], "message":API_RESPONSE['STOCK'], "details": "No stock available"})
    #update_json_file('rotation',slots['slot_number'])
    # response_time = datetime.now()

    if is_finish == 0:
        try:
            data = {}
            if IS_LIVE:
                validation_request = requests.get(kiosk_url)
                data = validation_request.json()
            else:
                validation_request = True
                data = {'ref_id':ref.id,'isValidCylinder':True,'ValidationDetails':'Success','isTrackingValid':True,'trackingDetails':'Success'}
                if txn_type == 1:
                    if not IS_LIVE:
                        data['ValidationDetails'] = 'Cylinder validated successfully'
                        data['skuDetails'] = {'variant':sku_instance['variant_type'],'sku':sku_instance['variant_sku']}
                isSuccess = get_random_resp()

            if validation_request:
                if not isSuccess:
                    data['ValidationDetails'] = failure_detail
                """ if isSuccess:
                    if not IS_LIVE:
                        response_status, response_message, response_details, validation_details = fetch_response(ref.id, success_key, detail_success, failure_key, failure_detail)
                        return send_response({
                            'status': response_status,
                            'message': response_message,
                            'details': response_details,
                            'response_data': [{"validation_details": validation_details}]
                        }) """
                ref_id = data.get('ref_id')
                if txn_type == 1:   
                    validResponse = data.get('isValidCylinder', False) 
                    validation_details = data.get('ValidationDetails', '') 
                elif txn_type in [2,3,4]:
                    validResponse = data.get('isTrackingValid', False)
                    validation_details = data.get('trackingDetails', '')       
                validResponse = True
                update_data = {
                    "validate_data": data,
                    "response_at": datetime.now(),
                    "reference_id": referenceid
                }
                if validResponse:
                    if txn_type != 1:
                        cus_txn_type = txn_type
                        if txn_type == 2:
                            cus_txn_type = 5
                        update_stock_status(cus_txn_type, sku_id, kiosk_id)

                    update_data["status"] = 1
                    update_data["txn_complete"] = 0
                    update_data["ref_id"] = ref_id
                    if txn_type and txn_type not in [1,'1']:
                        update_data["slot_id"] = slot_id
                        chamber_data = {}
                        chamber_data['status'] = update_status
                        chamber_data['sku_id'] = None
                        if txn_type in [2]:
                            chamber_data['sku_id'] = sku_id
                        kmodels.ChamberSlots.objects.filter(id=slot_id).update(**chamber_data)
                else:
                    update_data["status"] = 0

                customerModel.objects.filter(id=ref_id).update(**update_data)
                count = get_transaction_count(referenceid, 2)
                response_status = API_RESPONSE['SUCCESS'] if validResponse else API_RESPONSE['FAILED']
                response_message = API_RESPONSE[success_key] if validResponse else API_RESPONSE[failure_key]
                response_details = validation_details
                if not IS_LIVE:	
                    # response_status, response_message, response_details, validation_details = fetch_response(ref.id,success_key, detail_success, failure_key, failure_detail)
                    response_status = API_RESPONSE['SUCCESS']
                    response_message = API_RESPONSE[success_key]
                    response_details = detail_success

                """ while wait_until_field_updated(ref.id):
                    continue
                while ref.response_at is not None:
                    continue """

                return send_response({
                    'status': response_status,
                    'message': response_message,
                    'details': response_details,
                    'response_data': [{
                        "validation_details": validation_details,
                        'count': count
                    }]
                })
            else:
                return send_response({
                    'status': API_RESPONSE['FAILED'],
                    'message': API_RESPONSE['VALIDATION_ERROR'],
                    'details': 'Tracking system error'
                })
        except Exception as e:
            data = {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE[failure_key],
                'details': str(e),
                'response_data': [{"validation_details": str(e)}]
            }
            customerModel.objects.filter(reference_id=referenceid,id=ref.id).update(validate_data=data,response_at=datetime.now())         
            return send_response(data)
    elif is_finish==1:
        customerModel.objects.filter(reference_id=referenceid, ).update(txn_complete=1, status=1)
        count = get_transaction_count(referenceid,2)
        return send_response({
            'status': API_RESPONSE['SUCCESS'],
            'message': API_RESPONSE['TRANSACTION_SUCCESS'],
            'details': 'Transaction completed and marked as finished',
            'response_data':[{
                "validation_details":'Transaction completed successfully',
                'count': count
            }]
        })
    else:
        return send_response({
            'status': API_RESPONSE['FAILED'],
            'message': API_RESPONSE['TRANSACTION_TYPE'],
            'details': 'There was an error processing your transaction.'
        })

def get_nearest_rotation(current_slot, target_slot, total_slots):
    chamber =  1
    if current_slot > total_slots:
        current_slot = current_slot - total_slots

    if target_slot > total_slots:
        chamber = 2
        target_slot = target_slot - total_slots

    # Calculate clockwise rotation
    clockwise_rotation = (target_slot - current_slot + total_slots) % total_slots

    # Calculate counterclockwise rotation
    anticlockwise_rotation = (total_slots - clockwise_rotation) % total_slots

    # Determine the nearest rotation
    if clockwise_rotation <= anticlockwise_rotation:
        return clockwise_rotation, chamber
    else:
        return -anticlockwise_rotation, chamber


def current_slot(kiosk):
    bdatransaction = kmodels.BDA_Transactions.objects.filter(kiosk_id=kiosk,txn_complete=1,response_at__isnull=False,slot_id__isnull=False).values().order_by('-response_at').first()
    customertransaction = kmodels.Customer_Transactions.objects.filter(kiosk_id=kiosk,slot_id__isnull=False,response_at__isnull=False).values().order_by('-response_at').first()
    bda_time = bdatransaction['response_at'] if bdatransaction else None
    customer_time = customertransaction['response_at'] if customertransaction else None
    if bda_time and customer_time:
        latest_transaction = bdatransaction if bda_time > customer_time else customertransaction
    elif bda_time:
        latest_transaction = bdatransaction
    elif customer_time:
        latest_transaction = customertransaction
    else:
        latest_transaction = None  # No valid transactions found
    latest_slot_id = latest_transaction['slot_id'] if latest_transaction else None
    return latest_slot_id

def update_json_file(key,value):
    try:
        
        JSON_FILE_PATH ='/home/arivu/pcb_response.json'
        if os.path.exists('pcb_response.json') and os.path.getsize('pcb_response.json') > 0:
            with open('pcb_response.json', "r") as file:
                try:
                    data = json.load(file)
                    data[key] = value
                    
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        with open('pcb_response.json', "w") as file:
            json.dump(data,file, indent=4)

        return JsonResponse({"message": "JSON file updated successfully", "data": data})

    except Exception as e:
        print('error')
        return JsonResponse({"error": str(e)}, status=500)
    
def update_slot(kiosk_id, slot_id, status):
    try:
        kmodels.ChamberSlots.objects.filter(id=slot_id).update(status=status)
        slot = kmodels.ChamberSlots.objects.filter(id=slot_id).values('slot_number').first()
        if slot:
            vmodels.Machine.objects.filter(id=kiosk_id).update(current_slot=slot['slot_number'])
        return JsonResponse({"message": "Slot updated successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def fetch_response(id, success_key, success_message, failure_key, failure_message):
    while True:
        ref = kmodels.Customer_Transactions.objects.filter(id=id).values('txn_type','response_at','validate_data').first()
        if ref and ref['response_at'] is not None:
            response_data = ref['validate_data']
            if ref['txn_type'] == 1:
                status = response_data.get('status')
                validation_details = response_data.get('ValidationDetails')
            else:
                status = response_data.get('status')
                validation_details = response_data.get('trackingDetails')

            if status:
                return API_RESPONSE['SUCCESS'], API_RESPONSE[success_key], success_message, validation_details
            else:
                return API_RESPONSE['FAILED'], API_RESPONSE[failure_key], failure_message, validation_details
        sleep_time.sleep(5)  # wait before checking again

def get_machine_info(cond):
    cond['is_active'] = 1
    return vmodels.Machine.objects.filter(**cond).values().first()

def update_stock_status(txn_type, sku, kiosk):
    stock_inventory = kmodels.StockInventory.objects.filter(sku_id=sku,kiosk_id=kiosk)
    stock_data = stock_inventory.first()
    if stock_data is not None:
        stock_update = {}
        if txn_type == 2:
            stock_update['filled_stock'] = stock_data.filled_stock + 1
        elif txn_type == 4:
            stock_update['filled_stock'] = stock_data.filled_stock - 1
        elif txn_type == 3:
            stock_update['empty_stock'] = stock_data.empty_stock - 1
        elif txn_type == 5:
            stock_update['empty_stock'] = stock_data.empty_stock + 1
        stock_inventory.update(**stock_update)

def check_cylinder_validated(referenceid, sku_id, txn_type, model):
    existing_txns = model.objects.filter(reference_id=referenceid)
    if txn_type == 2:
        txn_info = existing_txns.last()
        if txn_info is None:
            return {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['MISSED_FILLED_VALIDATION'],
                'details': API_RESPONSE['MISSED_FILLED_DETAILS']
            }
        if txn_info.txn_type != 1:
            return {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['MISSED_FILLED_VALIDATION'],
                'details': API_RESPONSE['MISSED_FILLED_DETAILS']
            }
        txn = existing_txns.filter(txn_type=1).first()
        if txn:
            if txn.sku_id != sku_id:
                return {
                    'status': API_RESPONSE['FAILED'],
                    'message': API_RESPONSE['SKU_MISMATCH'],
                    'details': API_RESPONSE['SKU_MISMATCHS']
                }
        else:
            return {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['MISSED_FILLED_VALIDATION'],
                'details': API_RESPONSE['MISSED_FILLED_DETAILS']
            }
    return {
        'status': API_RESPONSE['SUCCESS'],
        'message': API_RESPONSE['SKU_CONSISTENT'],
        'details': ''
    }


def check_sku_consistency(referenceid, sku_id, txn_type, model):
    existing_txns = model.objects.filter(reference_id=referenceid)
    if txn_type == 1:
        if existing_txns.filter(txn_type=1).exists():
            return {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['VALIDATION_EXITS'],
                'details': API_RESPONSE['TRANSACTION_EXISTS']
            }
    elif txn_type in [2, 3, 4]:
        txn_completed = existing_txns.filter(txn_type=txn_type).first()
        if txn_completed:
            return {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['COLLECTION_ALREADY_DONE'],
                'details': ''
            }
        txn = existing_txns.filter(txn_type=1).first()
        if txn:
            if txn.sku_id != sku_id:
                return {
                    'status': API_RESPONSE['FAILED'],
                    'message': API_RESPONSE['SKU_MISMATCH'],
                    'details': API_RESPONSE['SKU_MISMATCHS']
                }
        else:
            return {
                'status': API_RESPONSE['FAILED'],
                'message': API_RESPONSE['MISSED_FILLED_VALIDATION'],
                'details': API_RESPONSE['MISSED_FILLED_DETAILS']
            }
    return {
        'status': API_RESPONSE['SUCCESS'],
        'message': API_RESPONSE['SKU_CONSISTENT'],
        'details': ''
    }
