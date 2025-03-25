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