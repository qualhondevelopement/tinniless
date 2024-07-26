from datetime import datetime, timedelta
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import jwt
from .models import *
from django.utils.translation import gettext_lazy as _
secret_key = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"

def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if not x_forwarded_for or not request.META.get('REMOTE_ADDR'):
            return None
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        print(ip)
        return ip
    except:
        print(ip)
        return None
    
    
def create_login_session(request, user, ip):
    
    payload = {
        'user_id': user.id,
        'ip_address': ip,
        'exp': datetime.now() + timedelta(days=365.25 * 100)  # Set expiration to 0 for unlimited expiration
    }

    # Generate a JWT token with the payload
    jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')

    login_session = UserLoginSession.objects.create(
            user=user,
            jwt_token=jwt_token,
            ip=ip
        )
    return jwt_token,True


class JwtAuthentication(BaseAuthentication):
    def authenticate(self, request):

        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            print(token)
            if not token:
                return None,None

            try:
                payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            except Exception as e:
                print("invalid token")
                msg = 'Expired or Invalid Token'
                raise exceptions.AuthenticationFailed({"error":msg},code = 401)

            exp = payload.get('exp')
            # Check token expiration
            if exp and exp < datetime.now().timestamp():
                print("expired_token")
                msg = _('Expired or Invalid Token')
                raise exceptions.AuthenticationFailed({"error":msg})

            # Set the user in the request
            user_id = payload.get('user_id')
            ip_address = payload.get("ip_address")

            if user_id is None:
                return None,None
            device_ip = get_client_ip(request=request)
            if device_ip != ip_address:
                print("different ip",device_ip,"\t",ip_address)
                msg = _('   Token from different Device')
                raise exceptions.AuthenticationFailed({"error":msg})

            user = UserAccount.objects.get(id=user_id)

            if UserLoginSession.objects.filter(user = user, ip= ip_address,logout_date_time= None).count() == 0:
                msg = 'Expired or Invalid Token'
                raise exceptions.AuthenticationFailed({"error":msg},code = 403)

            return user, None
        except:
            msg = 'Unauthorized'
            raise exceptions.AuthenticationFailed({"error":msg},code = 403)


def update_logout_session(jwt_token, **kwargs):
    # Retrieve the JWT token from the request header

    # Decode the JWT token to get user ID and IP address
    decoded_token = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
    user_id = decoded_token['user_id']
    ip_address = decoded_token['ip_address']

    # Find the corresponding LoginSession instance
    try:
        login_session = UserLoginSession.objects.get(user__id=user_id, ip=ip_address, logout_date_time=None)
    except UserLoginSession.DoesNotExist:
        return False,"Already Logged Out",401
    except UserLoginSession.MultipleObjectsReturned:
        login_sessions = UserLoginSession.objects.filter(user__id=user_id, ip=ip_address, logout_date_time=None)
        login_sessions.update(logout_date_time = datetime.now())
    # Update the LoginSession instance with logout datetime and expire the token
    else:
        login_session.logout_date_time = datetime.now()
        login_session.save()
    return True,"Log Out Successfull",200