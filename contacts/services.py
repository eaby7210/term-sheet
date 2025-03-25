import requests 
from datetime import datetime
from .models import Contact
from core.services import OAuthServices
from django.contrib.contenttypes.models import ContentType
from django.apps import apps



LIMIT_PER_PAGE = 100
BASE_URL = 'https://services.leadconnectorhq.com'
API_VERSION = "2021-07-28"

class ContactServiceError(Exception):
    "Exeption for Contact api's"
    pass

class ContactServices:
    
    @staticmethod
    def get_contacts(query=None, start_after_id=None, limit=LIMIT_PER_PAGE):
        """
        Fetch contacts from GoHighLevel API with given parameters.
        """
        print("get")
        token_obj = OAuthServices.get_valid_access_token_obj()
        print(token_obj.expires_at)
        url = f"{BASE_URL}/contacts/"
        headers = {
            "Authorization": f"Bearer {token_obj.access_token}",
            "Content-Type": "application/json",
            "Version": API_VERSION,
        }
        params = {
            "locationId": token_obj.LocationId,
            "limit": limit,
        }
        if query:
            params["query"] = query
        if start_after_id:
            params["startAfterId"] = start_after_id

        response = requests.get(url, headers=headers, params=params)
        print(response.status_code)
        if response.status_code == 200:
            return response.json().get("contacts", [])
        else:
            raise ContactServiceError(f"API request failed: {response.status_code}")
    
    @staticmethod
    def pull_contacts(query=None):
        """
        Fetch all contacts using pagination and save them to the database.
        """
        all_contacts = []
        start_after_id = None
        i=0
        while True:
            contacts = ContactServices.get_contacts(query, start_after_id)
            print(len(all_contacts),i,end='\n\n')
            
            if not contacts:
                break  # No more contacts

            all_contacts.extend(contacts)
            print(all_contacts[i])
            start_after_id = contacts[-1]["id"]  # Get last contact ID for pagination
            i+=1

        
        ContactServices._save_contacts(all_contacts)
        return f"Imported {len(all_contacts)} contacts"

    @staticmethod
    def _save_contacts(contacts):
        """
        Bulk save contacts to the database.
        """
        unique_contacts = {contact["id"]: contact for contact in contacts}.values()  # Remove duplicates
        contact_objects = [
            Contact(
                id=contact["id"],
                first_name=contact.get("firstName", ""),
                last_name=contact.get("lastName", ""),
                email=contact.get("email", ""),
                phone=contact.get("phone",""),
                country=contact.get("country", ""),
                location_id=contact.get("locationId", ""),
                type=contact.get("type", "lead"),
                date_added=datetime.fromisoformat(contact["dateAdded"].replace("Z", "+00:00")) if contact.get("dateAdded") else None,
                date_updated=datetime.fromisoformat(contact["dateUpdated"].replace("Z", "+00:00")) if contact.get("dateUpdated") else None,
                dnd=contact.get("dnd", False),
            )
            for contact in unique_contacts
        ]

        Contact.objects.bulk_create(
            contact_objects,
            update_conflicts=True,
            unique_fields=["id"],
            update_fields=["first_name", "last_name", "email", "country", "location_id", "type", "date_added", "date_updated", "dnd"],
        )

        ObjectCustomField = apps.get_model("custom_fields", "ObjectCustomField", require_ready=False)

        if ObjectCustomField:
            unique_custom_fields = {(cf["id"], contact["id"]): cf for contact in unique_contacts for cf in contact.get("customFields", [])}.values()

            custom_field_objects = [
                ObjectCustomField(
                    field_id=custom_field.get("id", ""),
                    field_value=custom_field.get("value", ""),
                    content_type=ContentType.objects.get_for_model(Contact),
                    object_id=contact["id"],
                )
                for contact in unique_contacts for custom_field in contact.get("customFields", [])
            ]

            if custom_field_objects:
                ObjectCustomField.objects.bulk_create(
                    custom_field_objects,
                    update_conflicts=True,
                    unique_fields=["field_id", "object_id"],
                    update_fields=["field_value"],
                )