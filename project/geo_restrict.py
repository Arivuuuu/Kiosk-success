from django.http import HttpResponseForbidden
from ipware import get_client_ip
from django.contrib.gis.geoip2 import GeoIP2

class CountryRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.geo = GeoIP2()

    def __call__(self, request):
        client_ip, _ = get_client_ip(request)
        print("client_ip", client_ip)

        # ✅ Allow local/dev IPs directly
        if client_ip in ('127.0.0.1', '::1', None):
            return self.get_response(request)

        # ✅ Optionally allow your internal/private LAN IP range (for testing)
        if client_ip.startswith(('192.168.', '10.', '172.16.')):
            return self.get_response(request)

        try:
            country = self.geo.country(client_ip)
            country_code = country.get('country_code')
            print("Country code:", country_code)
        except Exception as e:
            print("GeoIP lookup failed:", e)
            return HttpResponseForbidden("Access denied: Cannot resolve location")

        # ✅ Allow only India (IN)
        if country_code != 'IN':
            return HttpResponseForbidden("Access restricted to India only")

        return self.get_response(request)
