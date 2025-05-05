import requests, json
from django.utils.timezone import now
from django.db import transaction
from datetime import timedelta, datetime
from .models import OAuthToken, CustomField
from core.models import GHLUser
from django.conf import settings



TOKEN_URL = 'https://services.leadconnectorhq.com/oauth/token'
LIMIT_PER_PAGE = 100
BASE_URL = 'https://services.leadconnectorhq.com'
API_VERSION = "2021-07-28"


class OAuthTokenError(Exception):
    '''Custom exeption for Oauth token-related errors'''

class CustomFieldServiceError(Exception):
    "Exeption for Contact api's"
    pass

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
        payload = {
            'grant_type': 'refresh_token',
            'client_id': settings.CLIENT_ID,
            'client_secret': settings.CLIENT_SECRET,
            'refresh_token': token_obj.refresh_token
        }
        print(f"payload: {payload}")
        response = requests.post(TOKEN_URL, data=payload)

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


class CustomfieldServices:

    @staticmethod
    def get_customfields(location_id, model=None):
        """
        Fetch custom fields from GoHighLevel API for a specific location_id.
        """
        model = model or "all"
        print(f"getting custom fields of {model}")
        token_obj = OAuthServices.get_valid_access_token_obj()
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Content-Type": "application/json",
            "Version": API_VERSION,
        }

        url = f"{BASE_URL}/locations/{token_obj.LocationId}/customFields"
        params = {
            "model": model,
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise CustomFieldServiceError(f"API request failed: {response.status_code}")

    @staticmethod
    def pull_customfields(model):
        """
        Pull custom fields for all locations and save them.
        """
        location_ids = OAuthToken.objects.values_list('LocationId', flat=True)
        import_summary = []

        for location_id in location_ids:
            try:
                response_data = CustomfieldServices.get_customfields(location_id=location_id, model=model)
                custom_fields = response_data.get("customFields", [])
                CustomfieldServices._save_customfields(custom_fields)
                import_summary.append(f"{location_id}: Imported {len(custom_fields)} custom fields")
            except CustomFieldServiceError as e:
                import_summary.append(f"{location_id}: Failed to import custom fields - {str(e)}")

        return import_summary

    @staticmethod
    def _save_customfields(fields):
        """
        Save or update custom fields in the database.
        """
        for field in fields:
            CustomField.objects.update_or_create(
                id=field["id"],
                defaults={
                    "name": field["name"],
                    "model_name": field["model"],
                    "field_key": field["fieldKey"],
                    "placeholder": field.get("placeholder", ""),
                    "data_type": field["dataType"],
                    "parent_id": field["parentId"],
                    "location_id": field["locationId"],
                    "date_added": datetime.fromisoformat(field["dateAdded"].replace("Z", "+00:00")),
                }
            )


class UserServicesError(Exception):
    "Exeption for Contact api's"
    pass


class UserServices:
    
    @staticmethod
    def get_users(limit=LIMIT_PER_PAGE):
        token_obj = OAuthServices.get_valid_access_token_obj()
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Version": API_VERSION,
        }

       
        url = f"{BASE_URL}/users/"
        params = {
            # "limit": limit,
            # "companyId":token_obj.companyId
            "locationId":token_obj.LocationId
            
        }
        response = requests.get(url, headers=headers, params=params)
        print(json.dumps(response.json(), indent=4))
        if response.status_code == 200:
            return response.json()
        else:
            raise UserServicesError(f"API request failed: {response.status_code}")

    @staticmethod
    @transaction.atomic
    def pull_users():
        data = UserServices.get_users()
        UserServices.save_users(data)
        return data.get("users", [])

    @staticmethod
    @transaction.atomic
    def save_users(data):
        for user in data.get("users", []):
            GHLUser.objects.update_or_create(
                id=user["id"],
                defaults={
                    "first_name": user.get("firstName"),
                    "last_name": user.get("lastName"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "role_type": user.get("roles", {}).get("type"),
                    "role": user.get("roles", {}).get("role"),
                }
            )

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None
    
