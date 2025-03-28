from django.apps import apps
from django.urls import reverse_lazy
from rest_framework.views import APIView
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from datetime import datetime, timezone, timedelta
from django.db import transaction
import pdfkit
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView, UpdateView
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
from xhtml2pdf import pisa
from io import BytesIO


@method_decorator(csrf_exempt, name='dispatch')
class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['status']
    search_fields = ['ghl_id', 'name']
    lookup_field = "ghl_id"
    


class OpportunityWebhookAPIView(APIView):
    """Handles Opportunity webhooks from GHL"""

    def post(self, request):
        try:
            data = request.data
            webhook_id = data.get("webhookId")  
            if not webhook_id:
                print("Missing webhook ID")
                return Response({"error": "Missing webhook ID"}, status=status.HTTP_400_BAD_REQUEST)
            WebhookLog = apps.get_model('contacts', 'WebhookLog')
            if WebhookLog.objects.filter(webhook_id=webhook_id).exists():
                print("Duplicate webhook ID")
                return Response({"error": "Duplicate webhook ID"}, status=status.HTTP_400_BAD_REQUEST)

            timestamp_at = data.get("timestamp")
            if not timestamp_at:
                print("Missing timestamp")
                return Response({"error": "Missing timestamp"}, status=status.HTTP_400_BAD_REQUEST)
            
            timestamp_at_dt = parse_datetime(timestamp_at)
            if not timestamp_at_dt:
                return Response({"error": "Invalid timestamp format"}, status=status.HTTP_400_BAD_REQUEST)

            timestamp_at_dt = timestamp_at_dt.replace(tzinfo=timezone.utc)
            time_difference = datetime.now(timezone.utc) - timestamp_at_dt
            if time_difference > timedelta(minutes=5):
                return Response({"error": "Webhook request is too old"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate required fields
            ghl_id = data.get("id")
            name = data.get("name")
            pipeline_id = data.get("pipelineId")
            contact_id = data.get("contactId")
            status_value = data.get("status")
            created_at = data.get("dateAdded")
            created_at_dt = parse_datetime(created_at)
            created_at_dt = created_at_dt.replace(tzinfo=timezone.utc)
          
            if not all([ghl_id, name, pipeline_id, status_value]):
                return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():  # Prevent database locking issues
                # Log the webhook ID to prevent duplicate processing
                WebhookLog.objects.create(webhook_id=webhook_id)

                # Get or pull the pipeline
                pipeline = Pipeline.objects.filter(ghl_id=pipeline_id).first()
                if not pipeline:
                    PipelineServices.pull_pipelines()
                    pipeline = Pipeline.objects.filter(ghl_id=pipeline_id).first()
                    if not pipeline:
                        return Response({"error": "Pipeline not found"}, status=status.HTTP_400_BAD_REQUEST)

                # Get or create the contact
                Contact = apps.get_model('contacts', 'Contact')
                contact = None
                if contact_id:
                    contact = Contact.objects.filter(id=contact_id).first()
                    if not contact:
                        contact_data = ContactServices.retrieve_contact(contact_id)
                        if contact_data:
                            contact = Contact.objects.create(
                                id=contact_data.get("id"),
                                first_name=contact_data.get("firstName", ""),
                                last_name=contact_data.get("lastName", ""),
                                email=contact_data.get("email", ""),
                                phone=contact_data.get("phone", ""),
                                country=contact_data.get("country", ""),
                                location_id=contact_data.get("locationId", ""),
                                type=contact_data.get("type", "lead"),
                                date_added=parse_datetime(contact_data.get("dateAdded")),
                                date_updated=parse_datetime(contact_data.get("dateUpdated")),
                                dnd=contact_data.get("dnd", False),
                            )

                # Create or update the Opportunity
                opportunity, created = Opportunity.objects.update_or_create(
                    ghl_id=ghl_id,
                    defaults={
                        "name": name,
                        "pipeline": pipeline,
                        "contact": contact,
                        "status": status_value,
                        "created_at": created_at_dt,
                    },
                )
            print(f"Opportunity {name} processed")
            return Response({"message": "Opportunity processed", "created": created}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TermSheetView(FormView):
    template_name = "pages/term_sheet.html"  
    form_class = TermForm
    success_url = reverse_lazy("term_sheet") 

    def form_valid(self, form):
        form.save()  # Save form data to database
        return super().form_valid(form)
    


class TermSheetUpdateView(UpdateView):
    model = TermData
    form_class = TermForm
    template_name = "pages/term_sheet_val.html"
    success_url = reverse_lazy("term_sheet_list")  # Redirect after successful update
    lookup_field = "opportunity__ghl_id"

    def get_object(self, queryset=None):
        """Fetch the TermData object using the opportunity ID"""
        opportunity_id = self.kwargs.get("opportunity_id")
        return TermData.objects.get(opportunity__ghl_id=opportunity_id)


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
    
    
    @action(detail=True, methods=["POST"], url_path='generate_pdf')
    def generate_pdf(self, request, opportunity=None):
        """Generate and store a PDF using Django's model system."""
        term_data = get_object_or_404(TermData, opportunity__ghl_id=opportunity)
        form = TermForm(instance=term_data)  # Populate form with existing data

        # Render template to HTML
        html_content = render_to_string("pages/term_sheet_val.html", {"form": form, "term_data": term_data})

        # PDF options
        options = {
            "page-size": "A4",
            "margin-top": "0in",
            "margin-right": "0in",
            "margin-bottom": "0in",
            "margin-left": "0in",
            "encoding": "UTF-8",
            "enable-local-file-access": "",
        }

        try:
            # Generate PDF as binary data
            pdf_binary = pdfkit.from_string(html_content, False, options=options)

            # Create or update the TermSheet object
            term_sheet, created = TermSheet.objects.get_or_create(term_data=term_data)

            # Save PDF using Django's FileField (ContentFile)
            pdf_filename = f"pdf_sheets/term_sheet_{opportunity}.pdf"
            term_sheet.pdf_file.save(pdf_filename, ContentFile(pdf_binary), save=True)

            # Serialize the TermSheet object
            serializer = TermSheetSerializer(term_sheet)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class TermSheetViewSet(viewsets.ModelViewSet):
    queryset = TermSheet.objects.all()
    serializer_class = TermSheetSerializer
    lookup_field = "term_data"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["term_data__opportunity__ghl_id"]
    search_fields = ["term_data__borrower"]