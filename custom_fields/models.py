from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class ObjectCustomField(models.Model):
    field_id = models.CharField(max_length=50)  # Custom field ID from API
    field_value = models.TextField()
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=50)
    content_object = GenericForeignKey("content_type", "object_id")
    
    class Meta:
        unique_together = ("field_id", "object_id")

    def __str__(self):
        return f"{self.id} - {self.value}"
