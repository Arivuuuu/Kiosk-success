from datetime import datetime, timezone
import jwt
import json
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from kiosk.models import AuthToken
from .constants import API_RESPONSE
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from . import utils


User = get_user_model()
class KioskAuthentication():
    permission_classes = []
    def __init__(self, get_response):
        self.get_response = get_response  # Store response callable

    def __call__(self, request):
        '''Process request before passing to the next middleware/view'''
        response = self.get_response(request)  # Call next middleware or view
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        '''Authenticate user before processing the view'''
        origin = request.META.get("HTTP_ORIGIN")
        referer = request.META.get("HTTP_REFERER")
        #if not origin and not referer:
    	    #return JsonResponse({"error": "Direct access blocked"}, status=403)
        if hasattr(view_func, 'view_class') and hasattr(view_func.view_class, 'authentication_classes'):
            if not view_func.view_class.authentication_classes :
                return None # Allow the request to continue without auth

        authorization_header = request.headers.get('Authorization')
        if request.path.startswith('/admin/') or request.path.startswith('/api/v1/kiosk/check-ai-initiation/'):
            return None

        if authorization_header and authorization_header.startswith('Bearer '):
            token_header = authorization_header.split(' ')[1]
            try:
                try:
                    if request.path.startswith('/api/v1/kiosk/get-kiosk-id/'):
                        if token_header == 'kIOsK#@!3':
                            return None
                        else:
                            return JsonResponse({'status': API_RESPONSE['FAILED'], 'message': 'Invalid token. Provide valid token'}, status=200)
                    json_data = json.loads(request.body.decode('utf-8'))
                    kiosk = json_data.get('kioskid')
                    kioskid = utils.check_kiosk(kiosk)
                    if kioskid is None:
                        return utils.send_response({'status':API_RESPONSE['FAILED'],'message':API_RESPONSE['KIOSK_INVALID'],'details':''})
                    current_time = datetime.now()
                    token = AuthToken.objects.filter(kiosk_id=kioskid['id'],auth_token=token_header,is_active=1).values().first()
                    if token:
                        expire_time = token['expire_at'].astimezone(timezone.utc).replace(tzinfo=None)
                        decoded_token = jwt.decode(token_header, options={'verify_signature': False})
                        if decoded_token['kiosk_id'] != kiosk:
                            return JsonResponse({'status': API_RESPONSE['FAILED'], 'message': 'Invalid token. Provide valid token'}, status=200)
                        elif expire_time < current_time:
                            return JsonResponse({'status': API_RESPONSE['FAILED'], 'message': 'Token expired. Regenerate new token'}, status=200)
                        else:
                            return None
                    else:
                        return JsonResponse({'status': API_RESPONSE['FAILED'], 'message': 'Invalid token. Provide valid token'}, status=200)
                except jwt.DecodeError as e:
                    return JsonResponse({'status': API_RESPONSE['FAILED'], 'message': 'Token is invalid','details':str(e)}, status=200)
            except (TokenError, InvalidToken, jwt.ExpiredSignatureError) as e:
                return JsonResponse({'status': API_RESPONSE['FAILED'], 'message':'System error. Try again later','details':str(e)}, status=200)
        else:
            return JsonResponse({'status': API_RESPONSE['FAILED'], 'message':'No authorization token available','details':''}, status=200)

    def __call__(self, request):
        response = self.get_response(request) 
        return response
