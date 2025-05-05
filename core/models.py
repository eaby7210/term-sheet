from django.db import models
from django.utils.timezone import now


# Create your models here.
class OAuthToken(models.Model):
    access_token = models.CharField(max_length=500)
    token_type = models.CharField(max_length=100, default="Brearer")
    expires_at = models.DateField() #save this from expires_in
    refresh_token = models.CharField(max_length=500)
    scope = models.CharField(max_length=500)
    userType = models.CharField(max_length=500)
    companyId = models.CharField(max_length=500)
    LocationId = models.CharField(max_length=500)
    userId = models.CharField(max_length=500)
    
    def is_expired(self):
        """Check if the access token is expired"""
        return now().date() >= self.expires_at
    
    def __str__(self):
        return f""

class GHLUser(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # UserID from API
    first_name = models.CharField(max_length=100,null=True)
    last_name = models.CharField(max_length=100,null=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=100,null=True, blank=True)
    role_type = models.CharField(max_length=50, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"  

class CustomField(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    model_name = models.CharField(max_length=50)
    field_key = models.CharField(max_length=255)
    placeholder = models.CharField(max_length=255, blank=True)
    data_type = models.CharField(max_length=50)
    parent_id = models.CharField(max_length=100)
    location_id = models.CharField(max_length=100)
    date_added = models.DateTimeField()

    def __str__(self):
        return self.name