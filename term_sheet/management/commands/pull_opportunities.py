import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from term_sheet.services import OpportunityServices
from term_sheet.models import Pipeline, Opportunity
from contacts.models import Contact  

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Fetch and store opportunities with a loop-based approach"

    def handle(self, *args, **options):
        pipelines = Pipeline.objects.all()

        for pipeline in pipelines:
            print(f"Processing pipeline: {pipeline.ghl_id} - {pipeline.name}")

            # Fetch and store opportunities
            self.fetch_all_opportunities(pipeline)

    def fetch_all_opportunities(self, pipeline):
        """Fetch opportunities using a loop (not recursion) and store in the DB."""
        
        query = None  # Initial query param (None means first page)
        batch_size = 100  # Control batch size to optimize DB writes

        while True:
            opp_data, meta = OpportunityServices.get_opportunity(query=query)

            if not opp_data:
                break  # Exit if no more data

            print(f"Fetched {len(opp_data)} opportunities from API.")

            contacts_to_create = []
            opportunities_to_create = []
            existing_contact_ids = set(Contact.objects.values_list("id", flat=True))
            existing_opportunity_ids = set(Opportunity.objects.values_list("ghl_id", flat=True))

            for item in opp_data:
                contact = None

                # Process contact
                if "contact" in item and item["contact"]:
                    contact_data = item["contact"]
                    contact_id = str(contact_data["id"])

                    if contact_id not in existing_contact_ids:
                        contact = Contact(
                            id=contact_id,
                            first_name=contact_data.get("name"),
                            email=contact_data.get("email") or "",  
                            phone=contact_data.get("phone"),
                        )
                        contacts_to_create.append(contact)
                        existing_contact_ids.add(contact_id)  # Avoid duplicate inserts
                    else:
                        contact = Contact(id=contact_id)  # Reference existing contact

                # Process opportunity
                opp_id = item["id"]
                if opp_id not in existing_opportunity_ids:
                    opportunity = Opportunity(
                        ghl_id=opp_id,
                        name=item["name"],
                        pipeline=pipeline,
                        status=item["status"],
                        contact=contact if contact else None,
                        created_at=item["createdAt"],
                        updated_at=item["updatedAt"],
                    )
                    opportunities_to_create.append(opportunity)
                    existing_opportunity_ids.add(opp_id)

            # Batch insert contacts & opportunities
            self.bulk_insert_contacts(contacts_to_create)
            self.bulk_insert_opportunities(opportunities_to_create)

            print(f"Total opportunities stored: {Opportunity.objects.count()}")
            print(f"Total contacts stored: {Contact.objects.count()}")

            # Pagination logic
            next_page_url = meta.get("nextPageUrl")
            if not next_page_url:
                break  # Exit loop if no more pages
            
            query = {  # Update query params for next batch
                "startAfter": meta.get("startAfter", ""),
                "startAfterId": meta.get("startAfterId", ""),
            }

    def bulk_insert_contacts(self, contacts):
        """Efficiently insert contacts in bulk."""
        if contacts:
            Contact.objects.bulk_create(contacts, ignore_conflicts=True)
            print(f"Created {len(contacts)} new contacts.")

    def bulk_insert_opportunities(self, opportunities):
        """Efficiently insert opportunities in bulk."""
        if opportunities:
            Opportunity.objects.bulk_create(opportunities, ignore_conflicts=True)
            print(f"Created {len(opportunities)} new opportunities.")
