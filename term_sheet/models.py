from django.db import models

class Pipeline(models.Model):
    ghl_id = models.CharField(max_length=50, unique=True, db_index=True,primary_key=True)
    name = models.CharField(max_length=255)
    LocationId = models.CharField(max_length=100,  null=True, blank=True,)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Pipeline {self.ghl_id} - {self.name}"


class PipelineStage(models.Model):
    id = models.CharField(max_length=100, primary_key=True)  # Stage ID from API
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name="stages")
    name = models.CharField(max_length=255)
    position = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} (Pipeline: {self.pipeline.name})"

class Opportunity(models.Model):
    ghl_id = models.CharField(max_length=50, unique=True, db_index=True,primary_key=True)  # GHL Opportunity ID
    name = models.CharField(max_length=255)
    opp_value= models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stage = models.ForeignKey(PipelineStage, on_delete=models.SET_NULL, null=True, blank=True, related_name="opportunities")
    pipeline = models.ForeignKey(Pipeline, on_delete=models.PROTECT, related_name="opportunities", null=True, blank=True)
    contact = models.ForeignKey('contacts.Contact', on_delete=models.SET_DEFAULT, null=True, blank=True,default=None)
    status = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(db_index=True)
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return f"Opportunity id:{self.ghl_id} - {self.name}"


class OpportunityCustomFieldValue(models.Model):
    opportunity = models.ForeignKey('Opportunity', on_delete=models.CASCADE, related_name='custom_field_values')
    custom_field = models.ForeignKey('core.CustomField', on_delete=models.CASCADE)
    value = models.JSONField( null=True, blank=True)

    class Meta:
        unique_together = ('opportunity', 'custom_field')

    def __str__(self):
        return f"{self.opportunity.name} - {self.custom_field.name}: {self.value}"


class TermData(models.Model):
    borrower = models.CharField(max_length=255,null=True, blank=True)
    property_address = models.CharField(max_length=500,null=True, blank=True)

    # Deal Structure
    # LOAN_PURPOSE_CHOICES = [
    #     ('fix_flip', 'Fix & Flip'),
    #     ('rental', 'Rental'),
    # ]
    loan_purpose = models.CharField(
        max_length=50,
        db_index=True,
        null=True, blank=True
        # choices=LOAN_PURPOSE_CHOICES
        )
    as_is_value = models.CharField(max_length=50, null=True, blank=True)
    loan_amount = models.CharField(max_length=50, null=True, blank=True)
    rehab_cost = models.CharField(max_length=50, null=True, blank=True)
    loan_to_value = models.CharField(max_length=50, null=True, blank=True)
    after_repaired_value = models.CharField(max_length=50, null=True, blank=True)

    # Loan Terms
    loan_type = models.CharField(max_length=50, db_index=True,null=True, blank=True)
    interest_rate = models.CharField(max_length=50, null=True, blank=True)
    monthly_payment = models.CharField(max_length=50, null=True, blank=True)
    prepayment_penalty = models.CharField(max_length=50, null=True, blank=True)

    # Loan Fees
    origination_cost = models.CharField(max_length=50, null=True, blank=True)
    cash_to_from_borrower = models.CharField(max_length=50, null=True, blank=True)
    lender_fee = models.CharField(max_length=50, null=True, blank=True)
    additional_liquidity = models.CharField(max_length=50, null=True, blank=True)
    processing_fee = models.CharField(max_length=50, null=True, blank=True)

    # Property & Borrower Info
    property_type = models.CharField(max_length=50,null=True, blank=True)
    annual_taxes = models.CharField(max_length=50, null=True, blank=True)
    fico_score = models.CharField(max_length=50, null=True, blank=True)
    annual_insurance = models.CharField(max_length=50, null=True, blank=True)
    fair_market_rent = models.CharField(max_length=50, null=True, blank=True)
    annual_flood_insurance = models.CharField(max_length=50, null=True, blank=True)
    property_designation = models.CharField(max_length=100,null=True, blank=True)
    annual_hoa_dues = models.CharField(max_length=50, null=True, blank=True)

    # Borrower History
    current_dscr = models.CharField(max_length=50, null=True, blank=True)
    bankruptcy_last_3yrs = models.CharField(max_length=255,null=True, blank=True)
    foreclosures_last_3yrs = models.CharField(max_length=255,null=True, blank=True)
    felonies_crimes = models.CharField(max_length=255,null=True, blank=True)
    opportunity = models.OneToOneField(Opportunity, on_delete=models.CASCADE, related_name="term_data")
    # bankruptcy_last_3yrs = models.BooleanField(default=False)
    # foreclosures_last_3yrs = models.BooleanField(default=False)
    # felonies_crimes = models.BooleanField(default=False)
    # pdf_sheet = models.FileField(upload_to='pdf_sheets/', null=True, blank=True)

    def __str__(self):
        return f"Loan Deal {self.id} - {self.borrower}"

class TermSheet(models.Model):
    term_data = models.OneToOneField(TermData, on_delete=models.CASCADE, related_name='term_sheet')
    pdf_file = models.FileField(upload_to='pdf_sheets/',null=True, blank=True)

    def __str__(self):
        return f"PDF for {self.term_data.borrower} {self.term_data.opportunity.ghl_id}"


class PreApproval(models.Model):
    date = models.DateField()
    address = models.CharField(max_length=255,null=True, blank=True)
    llc_name = models.CharField(max_length=255,null=True, blank=True)
    purchase_price = models.CharField(max_length=255,null=True, blank=True)
    loan_type = models.CharField(max_length=255,null=True, blank=True)
    loan_term = models.CharField(max_length=255,null=True, blank=True)  
    loan_amount = models.CharField(max_length=255,null=True, blank=True)
    rate_apr = models.CharField(max_length=255,null=True, blank=True)
    occupancy = models.CharField(max_length=100,null=True, blank=True)
    applicant = models.CharField(max_length=255,null=True, blank=True)
    opportunity = models.OneToOneField(Opportunity, on_delete=models.CASCADE, related_name="preapprovals")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PreApproval for {self.applicant} on {self.date}"
    
class PreApprovalSheet(models.Model):
    pre_approval = models.OneToOneField(PreApproval, on_delete=models.CASCADE, related_name='pre_approval')
    pdf_file = models.FileField(upload_to='pre_approval_pdf_sheets/',null=True, blank=True)
    