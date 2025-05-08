from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import CustomField
from .models import TermSheet, PreApprovalSheet
from .services import OpportunityServices, PreApproveServices
from contacts.services import ContactServices

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

@receiver(post_save, sender=PreApprovalSheet)
def upload_pdf_and_update_contact(sender, instance :PreApprovalSheet, **kwargs):
    """
    Signal triggered after saving or updating a TermSheet.
    It uploads the PDF to GoHighLevel and updates the opportunity.
    """
    
    if not instance.pdf_file:
        print(f"PreApproval {instance.id} has no PDF file to upload.")
        return
    print(f"Uploading PDF for PreApprovalSheet {instance.id}...")
    
    customfield = CustomField.objects.get(field_key="contact.preapproval_template_pdf")
    upload_response = PreApproveServices.upload_pdf(preapprove_sheet=instance, custom_field_id=customfield.id)
    
    if upload_response:
        contact =instance.pre_approval.opportunity.contact
        print(f"Updating Contact {contact.first_name} {contact.last_name} with uploaded PDF details...")

        ContactServices.update_contact_with_pdf(contact, upload_response, customfield)
    else:
        print(f"Failed to upload PDF for TermSheet {instance.id}.")