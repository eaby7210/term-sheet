import json
import base64
import logging
import time
from datetime import datetime, timezone, timedelta
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from .models import Contact, WebhookLog
from .serializers import ContactSerializer

PUBLIC_KEY='''-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAokvo/r9tVgcfZ5DysOSC
Frm602qYV0MaAiNnX9O8KxMbiyRKWeL9JpCpVpt4XHIcBOK4u3cLSqJGOLaPuXw6
dO0t6Q/ZVdAV5Phz+ZtzPL16iCGeK9po6D6JHBpbi989mmzMryUnQJezlYJ3DVfB
csedpinheNnyYeFXolrJvcsjDtfAeRx5ByHQmTnSdFUzuAnC9/GepgLT9SM4nCpv
uxmZMxrJt5Rw+VUaQ9B8JSvbMPpez4peKaJPZHBbU3OdeCVx5klVXXZQGNHOs8gF
3kvoV5rTnXV0IknLBXlcKKAQLZcY/Q9rG6Ifi9c+5vqlvHPCUJFT5XUGG5RKgOKU
J062fRtN+rLYZUV+BjafxQauvC8wSWeYja63VSUruvmNj8xkx2zE/Juc+yjLjTXp
IocmaiFeAO6fUtNjDeFVkhf5LNb59vECyrHD2SQIrhgXpO4Q3dVNA5rw576PwTzN
h/AMfHKIjE4xQA1SZuYJmNnmVZLIZBlQAF9Ntd03rfadZ+yDiOXCCs9FkHibELhC
HULgCsnuDJHcrGNd5/Ddm5hxGQ0ASitgHeMZ0kcIOwKDOzOU53lDza6/Y09T7sYJ
PQe7z0cvj7aE4B+Ax1ZoZGPzpJlZtGXCsu9aTEGEnKzmsFqwcSsnw3JB31IGKAyk
T1hhTiaCeIY/OwwwNUY2yvcCAwEAAQ==
-----END PUBLIC KEY-----'''

# Create your views here.
logger = logging.getLogger(__name__)
class ContactPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 50  # Limit max page size

# Contact ViewSet
class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    pagination_class = ContactPagination  

    filter_backends = [filters.SearchFilter]
    search_fields = ["first_name", "last_name", "email","id"]








class ContactWebhookView(APIView):
    """
    Handles incoming webhook events from GoHighLevel.
    """

    def verify_signature(self, signature, timestamp):
        """Verify webhook signature"""
        if not signature or not timestamp:
            return False
        
        timestamp_dt = datetime
    
    def post(self, request):
        """
        Process webhook events.
        """
        print("sdfadf")
        payload = request.data
        webhook_id = payload.get("webhookId")
        event_type = payload.get("type")
        timestamp = payload.get("timestamp")
        signature = request.headers.get("x-wh-signature")
        
        if not self.verify_signature(payload, signature, timestamp):
            return Response({"error": "Invalid Signature or Expired timestamp"})
        
        if WebhookLog.objects.filter(webhook_id=webhook_id).exists():
            return Response({"error": "Duplicate webhook detected"}, status=status.HTTP_409_CONFLICT)
        
        WebhookLog.objects.create(webhook_id=webhook_id, received_at=now())
        contact_data = {
            "id":payload.get("id"),
            "firstName":payload.get("firstName",""),
            "lastName":payload.get("lastName",""),
            "email":payload.get("email"),
            "phone":payload.get("phone",""),
            
            }



        print(f"webhook: {webhook_id} \npayload",contact_data,event_type)
        # Process events
        if event_type == "ContactCreate":
            self.create_contact(contact_data)
        elif event_type == "ContactDelete":
            self.delete_contact(contact_data)
        elif event_type == "ContactUpdate":
            self.update_contact(contact_data)
        elif event_type == "ContactDndUpdate":
            self.update_contact_dnd(contact_data)
        elif event_type == "ContactTagUpdate":
            self.update_contact_tags(contact_data)
        # elif event_type == "NoteCreate":
        #     self.create_note(contact_data)
        # elif event_type == "NoteDelete":
        #     self.delete_note(contact_data)
        # elif event_type == "TaskCreate":
        #     self.create_task(contact_data)
        # elif event_type == "TaskDelete":
        #     self.delete_task(contact_data)

        return Response({"message": "Webhook processed successfully"}, status=status.HTTP_200_OK)

    def create_contact(self, data):
        """ Creates a new contact """
        Contact.objects.create(
            id=data["id"],
            first_name=data.get("firstName", ""),
            last_name=data.get("lastName", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
        )
    
    def update_contact(self, data):
        """ Updates a contact """
        contact = Contact.objects.filter(id=data["id"]).first()
        if contact:
            contact.first_name = data.get("firstName", contact.first_name)
            contact.last_name = data.get("lastName", contact.last_name)
            contact.email = data.get("email", contact.email)
            contact.phone = data.get("phone", contact.phone)
            contact.save()
            logger.info(f"Updated contact: {data['id']}")
        else:
            logger.warning(f"Contact {data['id']} not found for update")

    def delete_contact(self, data):
        """ Deletes a contact """
        Contact.objects.filter(id=data["id"]).delete()
