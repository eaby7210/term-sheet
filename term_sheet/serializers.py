from rest_framework import serializers
from contacts.serializers import ContactSerializer
from .models import TermData,Pipeline, Opportunity, TermSheet,PreApproval, PreApprovalSheet
from contacts.models import Contact

class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = [ "ghl_id", "name", "date_added", "date_updated"]


class OpportunitySerializer(serializers.ModelSerializer):
    pipeline = PipelineSerializer(read_only=True)
    pipeline_id = serializers.PrimaryKeyRelatedField(
        queryset=Pipeline.objects.all(), source="pipeline", write_only=True
    )
    contact = ContactSerializer(read_only=True)
    contact_id = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), source="contact", write_only=True, allow_null=True
    )
    custom_fields = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
           
            "ghl_id",
            "name",
            "pipeline",
            "pipeline_id",
            "contact",
            "contact_id",
            "status",
            "created_at",
            "updated_at",
            "custom_fields",
        ]
    def get_custom_fields(self, obj):
        custom_fields = {}
        for custom_value in obj.custom_field_values.all():
            field_key = custom_value.custom_field.field_key
            value = custom_value.value
            custom_fields[field_key.split('.')[1]] = value
        return custom_fields


class TermSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermSheet
        fields = ['id', 'pdf_file','term_data']

class TermDataSerializers(serializers.ModelSerializer):
    
    class Meta:
        model = TermData
        fields = [
            # Basic Info
            "id",
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

class TermDataRetriveSerializers(serializers.ModelSerializer):
    opportunity=OpportunitySerializer(read_only=True)
    term_sheet = TermSheetSerializer(read_only=True)
    class Meta:
        model = TermData
        fields = [
              "id",
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
            "term_sheet"
        ]
 

class PreApprovalPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreApprovalSheet
        fields = [
            "id", "pre_approval", "pdf_file"
        ]

       
        
class PreApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreApproval
        fields = [
            'id',
            'date',
            'address',
            'llc_name',
            'purchase_price',
            'loan_type',
            'loan_term',
            'loan_amount',
            'rate_apr',
            'occupancy',
            'applicant',
            'created_at',
            'updated_at',
            'opportunity',
        ]
    def validate_opportunity(self, value):
        # If we're updating and the opportunity is already assigned to this instance, allow it
        instance = getattr(self, 'instance', None)
        if instance and instance.opportunity == value:
            return value
        if PreApproval.objects.filter(opportunity=value).exists():
            raise serializers.ValidationError("pre approval with this opportunity already exists.")
        return value

class PreApprovaRetrieveSerializer(serializers.ModelSerializer):
    opportunity=OpportunitySerializer(read_only=True)
    pre_approval_sheet = PreApprovalPDFSerializer(read_only=True)
    class Meta:
        model = PreApproval
        fields = [
            'id',
            'date',
            'address',
            'llc_name',
            'purchase_price',
            'loan_type',
            'loan_term',
            'loan_amount',
            'rate_apr',
            'occupancy',
            'applicant',
            'created_at',
            'updated_at',
            'opportunity',
            'pre_approval_sheet',
        ]