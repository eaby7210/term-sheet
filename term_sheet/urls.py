from django.urls import path, include
from .views import (
    TermSheetView,OpportunityViewSet,
    TermDataViewSet,TermSheetViewSet,
    TermSheetUpdateView, OpportunityWebhookAPIView
    )
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'opportunities',OpportunityViewSet, basename= 'opportunity')
router.register(r'termdata',TermDataViewSet, basename="term_data")
router.register(r'termsheet',TermSheetViewSet,basename='taermsheet')

urlpatterns = [
    path("term-sheet/", TermSheetView.as_view(), name="term_sheet"),
    path('api/',include(router.urls)),
    path("term-sheet/<str:opportunity_id>/", TermSheetUpdateView.as_view(), name="term_sheet_update"),
     path("api/opportunity/webhook", OpportunityWebhookAPIView.as_view(), name="opportunity-webhook"),

]