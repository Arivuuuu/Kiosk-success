
API_ENDPOINTS = {
    'KIOSK_URL': 'http://localhost:5000/',
    'PCB_URL'  : 'http://localhost:12919/'
}
IS_LIVE = False
API_RESPONSE = {
    'SUCCESS'           : 'success',
    'FAILED'            : 'failure',
    'AUTH_EMPTY'        : 'Authorize token not provided',
    'AUTH_INVALID'      : 'Authorization token failed',
    'KIOSK_EMPTY'       : 'Kiosk Id not provided',
    'KIOSK_INVALID'     : 'Kiosk Id is invalid',
    'REF_ID_EMPTY'      : 'Reference id not provided',
    'REF_ID_INVALID'    : 'Reference id is invalid',
    'TRACKING_ERROR'    : 'Tracking system error',
    'COLLECTION_TIMEOUT': 'Cylinder not collected from chamber within time',
    'DISPENSE_ERROR'    : 'Error while dispensing the cylinder',
    'STOCK_EMPTY'       : 'Stock not available for the given kiosk',
    'SKU_EMPTY'         : 'SKU not provied',
    'SKU_INVALID'       : 'SKU is invalid',
    'VARIANT_EMPTY'     : 'Variant not provided',

    #CYLINDEER VALIDATION
    'VALIDATION_SUCCESS' : 'Cylinder validated successfully',
    'VALIDATION_FAILED' : 'Cylinder validation failed',
    
    #EMPTYCOLLECT
    'EMPTY_COLLECT_SUCCESS' : 'Empty cylinder collected',
    'EMPTY_COLLECT_FAILED'  : 'Empty collection failed',    
    'CYLINDER_OUT_OF_VIEW'    : 'Cylinder is out of visibility',
    'PROCESS_TIMEOUT' : 'Process timed out after 45 seconds',
    'MULTIPLE_CYLINDERS_DETECTED' : 'Multiple cylinders found',
    'SYSTEM_FAILURE'      : 'System failure occurred',

    #RETURNEMPTYY
    'EMPTY_CYLINDER_RETURNED'      : 'Empty cylinder returned',
    'RETURN_EMPTY_COLLECT_FAILED'  : 'Return Empty collection failed',

    # DispenseFilled
    'DISPENSED_FILLED'      : 'Dispensed cylinder collected',
    'DISPENSED_FILLED_COLLECT_FAILED'  : 'Dispensed collection failed',

    # 'NO_CYLINDER_IN_CHAMBER'       : 'No cylinder in chamber to remove',
    # 'PROCESS_TIMEOUT'               : 'Process timeout',
    # 'CAMERA_SYSTEM_ERROR'           : 'Camera system error',
    # 'MULTIPLE_CYLINDERS_DETECTED'   : 'Multiple cylinders detected in validation area',
    # 'CHAMBER_NUMBER_MISSING'        : 'Chamber number missing',
    # 'INVALID_CHAMBER_NUMBER'        : 'Invalid chamber number',
    # 'INVALID_TIMEOUT_VALUE'         : 'Invalid timeout value',
    # 'SYSTEM_INITIALIZATION_ERROR'   : 'System initialization error',
    # 'CAMERAS_NOT_CONFIGURED'        : 'Cameras not configured',
    # 'CLOSE_DOOR_BEFORE_TRACKING'    : 'First close chamber door before starting tracking',
    # 'DOOR_STATUS_CHECK_FAILED'      : 'Door status check failed',
    'ROTATION_REQUIRED' : 'Rotation is required',
    'CHAMBER_DOOR_1'    : 'Chamber_door_1 is required',
    'CHAMBER_DOOR_2'    : 'Chamber_door_2 is required',
    'RESET_ALARM'       : 'Reset_alarm is required',

    'EMPTY_COLLECT_FAILED' : 'Empty Cyclinder Failed',

    #filled dispensed
    'FILLED_CYLINDER'   : 'Filled cylinder successfully dispensed',
    'FILLED_CYLINDER_FAILED' : 'Receive Filled Cylinder Failed',
    'TOTAL_COUNT'       : 'Total count not provided',
    'INVALID_TRANSACTION_TYPE':  'Invalid transaction type',
    'FINISH_STATUS' : 'Finish status is empty',
    'VALIDATION_PROGRESS': 'Validation Already in Progress',
    'TRANSACTION_ALREADY_COMPLETED': 'Validation has already been completed',
    'VARIANT_SKU':'Variant with the sku is not available',
    'TRANSACTION_SUCCESS':'Transaction completed Successfully',
    'TRANSACTION_TYPE':'Invalid transaction type or unhandled error',
    'FILLED_CYLINDER_COLLECT':'Filled cylinder successfully collected',
    'VALIDATION_ERROR' : 'System Error',
    'MISSED_FILLED_VALIDATION': 'Complete cylinder validation to continue',
    'MISSED_FILLED_DETAILS': 'Validation required. Please validate the cylinder to continue',
    'DUPLICATE_REF_ID': 'Duplicate reference id',
    'VALIDATION_EXITS':'Cylinder validation already completed',
    'TRANSACTION_EXISTS':'Transaction has already been completed for this reference ID',
    'COLLECTION_ALREADY_DONE': 'Already collected for this reference ID',
    'SKU_MISMATCH':'SKU mismatch',
    'SKU_MISMATCHS':'The SKU does not match the one used during cylinder validation',
    'SKU_CONSISTENT':'The SKU is Consistent',
    'STOCK': 'Stock Not Available',
}
