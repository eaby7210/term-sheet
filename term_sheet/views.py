from django.apps import apps
from django.urls import reverse_lazy
from datetime import datetime
from django.views.generic.edit import FormView
from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from contacts.services import ContactServices
from .services import PipelineServices
from .forms import TermForm
from .models import Opportunity,TermData, TermSheet,Pipeline
from .serializers import (
    OpportunitySerializer,TermDataSerializers,TermSheetSerializer,
    TermDataRetriveSerializers)


class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['status']
    search_fields = ['ghl_id', 'name']
    lookup_field = "ghl_id"
    
    @action(detail=False,methods=["POST"], url_path='webhook')
    def webhook(self, request):
        try:
            data = request.data
            ghl_id = data.get("id")
            name = data.get("name")
            pipeline_id = data.get("pipelineId")
            contact_id = data.get("contactId")
            status_value = data.get("status")
            created_at = data.get("dateAdded")
            
            if not all([ghl_id, name, pipeline_id, status_value, created_at]):
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            pipeline = Pipeline.objects.filter(ghl_id=pipeline_id).first()
            if not pipeline:
                PipelineServices.pull_pipelines()
                pipeline = Pipeline.objects.filter(ghl_id=pipeline_id).first()
                if not pipeline:
                    return Response({"error": "Pipeline not found"}, status=status.HTTP_400_BAD_REQUEST)
            
            Contact = apps.get_model('contacts', 'Contact')
            contact = None
            if contact_id:
                contact = Contact.objects.filter(ghl_id=contact_id).first()
                if not contact:
                    contact_data = ContactServices.retrieve_contact(contact_id)
                    if contact_data:
                        contact = Contact.objects.create(
                            ghl_id=contact_data.get("id"),
                            first_name=contact_data.get("firstName", ""),
                            last_name=contact_data.get("lastName", ""),
                            email=contact_data.get("email", ""),
                            phone=contact_data.get("phone", ""),
                            country=contact_data.get("country", ""),
                            location_id=contact_data.get("locationId", ""),
                            type=contact_data.get("type", "lead"),
                            date_added=datetime.fromisoformat(contact["dateAdded"].replace("Z", "+00:00")) if contact.get("dateAdded") else None,
                            date_updated=datetime.fromisoformat(contact["dateUpdated"].replace("Z", "+00:00")) if contact.get("dateUpdated") else None,
                            dnd=contact_data.get("dnd", False),
                        )
            
            opportunity, created = Opportunity.objects.update_or_create(
                ghl_id=ghl_id,
                defaults={
                    "name": name,
                    "pipeline": pipeline,
                    "contact": contact,
                    "status": status_value,
                    "created_at": created_at,
                },
            )
            
            return Response({"message": "Opportunity processed", "created": created}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     


class TermSheetView(FormView):
    template_name = "pages/term_sheet.html"  
    form_class = TermForm
    success_url = reverse_lazy("term_sheet") 

    def form_valid(self, form):
        form.save()  # Save form data to database
        return super().form_valid(form)

class TermDataViewSet(viewsets.ModelViewSet):
    queryset = TermData.objects.all()
    # serializer_class = TermDataSerializers
    lookup_field = "opportunity"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["loan_purpose", "loan_type", "property_type", "fico_score", "opportunity__ghl_id"]
    search_fields = ["borrower", "property_address", "opportunity__ghl_id"]
    ordering_fields = ["loan_amount", "interest_rate", "created_at"]
    
    def get_serializer_class(self):
        if hasattr(self, 'action') and self.action in ['list', 'retrieve']:
            return TermDataRetriveSerializers
        elif hasattr(self, 'action') and self.action in ['create', 'update']:
            return TermDataSerializers
        return TermDataSerializers  

        
    
class TermSheetViewSet(viewsets.ModelViewSet):
    queryset = TermSheet.objects.all()
    serializer_class = TermSheetSerializer
    lookup_field = "term_data__opportunity__ghl_id"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["term_data__opportunity__ghl_id"]
    search_fields = ["term_data__borrower"]