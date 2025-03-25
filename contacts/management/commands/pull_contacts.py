from django.core.management.base import BaseCommand
from contacts.services import ContactServices

class Command(BaseCommand):
    help = "Fetch contacts from GoHighLevel API and store them in the database."

    def add_arguments(self, parser):
        parser.add_argument('--query', type=str, help='Optional query to filter contacts')

    def handle(self, *args, **kwargs):
        query = kwargs.get('query')
        try:
            result = ContactServices.pull_contacts(query)
            self.stdout.write(self.style.SUCCESS(result))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
