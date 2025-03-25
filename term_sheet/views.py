from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .forms import TermForm
from .models import Opportunity,TermData, TermSheet
from .serializers import (
    OpportunitySerializer,TermDataSerializers,TermSheetSerializer)


class OpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ['status']
    search_fields = ['ghl_id', 'name']
    lookup_field = "ghl_id"


class TermSheetView(FormView):
    template_name = "pages/term_sheet.html"  
    form_class = TermForm
    success_url = reverse_lazy("term_sheet") 

    def form_valid(self, form):
        form.save()  # Save form data to database
        return super().form_valid(form)

class TermDataViewSet(viewsets.ModelViewSet):
    queryset = TermData.objects.all()
    serializer_class = TermDataSerializers
    lookup_field = "opportunity__ghl_id"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["loan_purpose", "loan_type", "property_type", "fico_score", "opportunity__ghl_id"]
    search_fields = ["borrower", "property_address", "opportunity__ghl_id"]
    ordering_fields = ["loan_amount", "interest_rate", "created_at"]
    
class TermSheetViewSet(viewsets.ModelViewSet):
    queryset = TermSheet.objects.all()
    serializer_class = TermSheetSerializer
    lookup_field = "term_data__opportunity__ghl_id"
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["term_data__opportunity__ghl_id"]
    search_fields = ["term_data__borrower"]