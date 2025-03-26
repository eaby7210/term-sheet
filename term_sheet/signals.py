from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TermSheet
from .services import OpportunityServices

@receiver(post_save, sender=TermSheet)
def upload_pdf_and_update_opportunity(sender, instance, **kwargs):
    """
    Signal triggered after saving or updating a TermSheet.
    It uploads the PDF to GoHighLevel and updates the opportunity.
    """
    if not instance.pdf_file:
        print(f"TermSheet {instance.id} has no PDF file to upload.")
        return

    print(f"Uploading PDF for TermSheet {instance.id}...")

    custom_field_id = "dT1F35z9pjIK3BhAYJy7"
    upload_response = OpportunityServices.upload_pdf(term_sheet=instance, custom_field_id=custom_field_id)

    if upload_response:
        print(f"Updating opportunity {instance.term_data.opportunity.ghl_id} with uploaded PDF details...")

        opportunity_id = instance.term_data.opportunity.ghl_id
        OpportunityServices.update_opportunity_with_pdf(opportunity_id, upload_response, custom_field_id)
    else:
        print(f"Failed to upload PDF for TermSheet {instance.id}.")
