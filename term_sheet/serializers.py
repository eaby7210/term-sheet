from rest_framework import serializers
from contacts.serializers import ContactSerializer
from .models import TermData,Pipeline, Opportunity, TermSheet
from contacts.models import Contact

class TermDataSerializers(serializers.ModelSerializer):
    class Meta:
        model = TermData
        fields = [
            # Basic Info
            "borrower", "property_address",
            
            # Deal Structure
            "loan_purpose", "as_is_value", "loan_amount", "rehab_cost",
            "loan_to_value", "after_repaired_value",

            # Loan Terms
            "loan_type", "interest_rate", "monthly_payment", "prepayment_penalty",

            # Loan Fees
            "origination_cost", "cash_to_from_borrower", "lender_fee",
            "additional_liquidity", "processing_fee",

            # Property & Borrower Info
            "property_type", "annual_taxes", "fico_score", "annual_insurance",
            "fair_market_rent", "annual_flood_insurance", "property_designation",
            "annual_hoa_dues",

            # Borrower History
            "bankruptcy_last_3yrs", "current_dscr", "foreclosures_last_3yrs",
            "felonies_crimes",
            "opportunity",
        ]
        



class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = ["id", "ghl_id", "name", "date_added", "date_updated"]


class OpportunitySerializer(serializers.ModelSerializer):
    pipeline = PipelineSerializer(read_only=True)
    pipeline_id = serializers.PrimaryKeyRelatedField(
        queryset=Pipeline.objects.all(), source="pipeline", write_only=True
    )
    contact = ContactSerializer(read_only=True)
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), source="contact", write_only=True, allow_null=True
    )

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "ghl_id",
            "name",
            "pipeline",
            "pipeline_id",
            "contact",
            "contact_id",
            "status",
            "created_at",
            "updated_at",
        ]


class TermSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermSheet
        fields = ["id", "term_data", "pdf_file"]