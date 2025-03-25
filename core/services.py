import requests
from django.utils.timezone import now
from datetime import timedelta
from .models import OAuthToken
from django.conf import settings



TOKEN_URL = 'https://services.leadconnectorhq.com/oauth/token'

class OAuthTokenError(Exception):
    '''Custom exeption for Oauth token-related errors'''

class OAuthServices:
    
    @staticmethod
    def get_valid_access_token_obj():
        token_obj = OAuthToken.objects.first()  # Assuming one OAuth record, change if one per user
        
        if not token_obj:
            raise OAuthTokenError("OAuth token not found. Please authenticate first")
        
        if token_obj.is_expired():
            OAuthServices.refresh_access_token()
            
        return token_obj
    
    @staticmethod
    def get_fresh_token(auth_code):
        '''Exchange authorization code for a fresh access token'''
        
        headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            'client_id': settings.CLIENT_ID,
            'client_secret' : settings.CLIENT_SECRET,
            'grant_type' : 'authorization_code',
            'code' : auth_code,
        }
        print(payload)
        response =requests.post(TOKEN_URL,headers=headers,data=payload)
        token_data = response.json()
        
        if response.status_code == 200:
            token_obj, created = OAuthToken.objects.update_or_create(
                id=1,  # Assuming a single OAuth record
                defaults={
                    "access_token": token_data["access_token"],
                    "token_type": token_data["token_type"],
                    "expires_at": (now() + timedelta(seconds=token_data["expires_in"])).date(),
                    "refresh_token": token_data["refresh_token"],
                    "scope": token_data["scope"],
                    "userType": token_data["userType"],
                    "companyId": token_data["companyId"],
                    "LocationId": token_data["locationId"],
                    "userId": token_data["userId"],
                }
            )
            return token_obj.access_token
        else:
            raise ValueError(f"Failed to get fresh access token: {token_data}")
    
    
    @staticmethod
    def refresh_access_token():
        """
        Refresh the access token using the refresh token.
        """
        
        token_obj = OAuthToken.objects.first()
        response = requests.post(TOKEN_URL, data={
            'grant_type': 'refresh_token',
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'refresh_token': token_obj.refresh_token
        })

        if response.status_code != 200:
            raise OAuthTokenError(f"Failed to refresh access token: {response.json()}")

        new_tokens = response.json()
        print("New Tokens:", new_tokens)

        token_obj.access_token = new_tokens.get("access_token")
        token_obj.refresh_token = new_tokens.get("refresh_token")
        token_obj.expires_at = now() + timedelta(seconds=new_tokens.get("expires_in"))

        token_obj.scope = new_tokens.get("scope")
        token_obj.userType = new_tokens.get("userType")
        token_obj.companyId = new_tokens.get("companyId")
        token_obj.LocationId = new_tokens.get("locationId")
        token_obj.userId = new_tokens.get("userId")

        token_obj.save()
        return token_obj