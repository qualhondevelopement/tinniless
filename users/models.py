from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin

class Business(models.Model):
    CLINIC = "CLINIC"
    RESELLER = "RESELLER"
    BUSINESS_TYPE_CHOICES = [
        (CLINIC,CLINIC),
        (RESELLER,"RESELLER")
    ]
    business_type = models.CharField(max_length= 25, choices= BUSINESS_TYPE_CHOICES, default= CLINIC)
    organization_name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    search_string = search_string = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        self.search_string = f" {self.organization_name} {self.description}"
        super().save(*args, **kwargs)


class UserAccount(AbstractUser):

    ADMIN = "ADMIN"
    PATIENT = "PATIENT"
    OPERATOR = "OPERATOR"
    RESELLER = "RESELLER"
    
    USER_TYPE_CHOICES = [
        (ADMIN,"ADMIN"),
        (PATIENT, "PATIENT"),
        (OPERATOR, "OPERATOR"),
        (RESELLER,"RESELLER")
    ]

    user_type = models.CharField(max_length=25, choices= USER_TYPE_CHOICES, default = PATIENT)
    full_name = models.CharField(max_length=55)
    dob = models.DateField()
    business = models.ForeignKey(Business, null=True, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_string = models.TextField(blank=True, null=True)
    prefered_time_zone = models.CharField(max_length = 25, default = "CDT")
    

    def save(self, *args, **kwargs):

        f_name = self.first_name if self.first_name else ""
        l_name = self.last_name if self.last_name else ""
        self.full_name  = f"{f_name} {l_name}"
        self.username = self.email

        self.search_string = f"{f_name} {l_name} {self.email} {self.user_type}"
        if self.business:
            self.business.search_string += self.search_string
            self.business.save()

        super().save(*args, **kwargs)

class Address(models.Model):

    business = models.ForeignKey(Business, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, null=True, on_delete=models.CASCADE)
    line_1 = models.TextField()
    line_2 = models.TextField(null=True, blank=True)
    landmark = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    region = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=50)
    postal_code = models.IntegerField(unique=True)
    is_deleted = models.BooleanField(default=False)


class ContactNumber(models.Model):

    business = models.ForeignKey(Business, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, null=True, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=5)
    number = models.BigIntegerField(unique=True)
    is_deleted = models.BooleanField(default=False)

class CardDetails(models.Model):

    number = models.BigIntegerField()
    expiry_date = models.DateField()
    type = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)