from django import forms
from .models import TermData

class TermForm(forms.ModelForm):
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
        ]
        widgets = {
            'borrower': forms.TextInput(attrs={'class': 'form-control'}),
            'property_address': forms.TextInput(attrs={'class': 'form-control'}),
            'loan_purpose': forms.Select(attrs={'class': 'form-select'}),
            'as_is_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'rehab_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_to_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'after_repaired_value': forms.NumberInput(attrs={'class': 'form-control'}),
            'loan_type': forms.TextInput(attrs={'class': 'form-control'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'monthly_payment': forms.NumberInput(attrs={'class': 'form-control'}),
            'prepayment_penalty': forms.NumberInput(attrs={'class': 'form-control'}),
            'origination_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'cash_to_from_borrower': forms.NumberInput(attrs={'class': 'form-control'}),
            'lender_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'additional_liquidity': forms.NumberInput(attrs={'class': 'form-control'}),
            'processing_fee': forms.NumberInput(attrs={'class': 'form-control'}),
            'property_type': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_taxes': forms.NumberInput(attrs={'class': 'form-control'}),
            'fico_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'annual_insurance': forms.NumberInput(attrs={'class': 'form-control'}),
            'fair_market_rent': forms.NumberInput(attrs={'class': 'form-control'}),
            'annual_flood_insurance': forms.NumberInput(attrs={'class': 'form-control'}),
            'property_designation': forms.TextInput(attrs={'class': 'form-control'}),
            'annual_hoa_dues': forms.NumberInput(attrs={'class': 'form-control'}),
            'bankruptcy_last_3yrs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'current_dscr': forms.NumberInput(attrs={'class': 'form-control'}),
            'foreclosures_last_3yrs': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'felonies_crimes': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            "cash_to_from_borrower": (
                "Cash to or from borrower listed above does not include appraisal, closing, legal, "
                "title, and escrow related fees - for an estimation of these costs, contact the loan officer directly."
            )
        }
