from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from core_utils.models import CurrencyValueMapping

class Business(models.Model):
    CLINIC = "CLINIC"
    RESELLER = "RESELLER"
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS_TYPE_CHOICES = [
        (CLINIC,"CLINIC"),
        (RESELLER,"RESELLER"),
        (INDIVIDUAL,"INDIVIDUAL")
    ]
    tax_number = models.CharField(max_length=100)
    tax_document = models.FileField(upload_to='documents', blank = True, null = True)
    business_type = models.CharField(max_length= 25, choices= BUSINESS_TYPE_CHOICES, default= INDIVIDUAL)
    organization_name = models.CharField(max_length=50, blank = True, null = True)
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


class Language(models.Model):
    language_code = models.CharField(max_length=5)
    language_name= models.CharField(max_length=50)

class UserAccount(AbstractUser):

    ADMIN = "ADMIN"
    PATIENT = "PATIENT"
    OPERATOR = "OPERATOR"
    RESELLER = "RESELLER"
    RETAILER = "RETAILER"
    
    USER_TYPE_CHOICES = [
        (ADMIN,"ADMIN"),
        (PATIENT, "PATIENT"),
        (OPERATOR, "OPERATOR"),
        (RESELLER,"RESELLER"),
        (RETAILER,"RETAILER")
    ]
    
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"
    PENDING = "PENDING"

    USER_STATUS_CHOICES = [
        (ACTIVE,ACTIVE),
        (INACTIVE,INACTIVE),
        (BLOCKED,BLOCKED),
        (PENDING,PENDING)
    ]
    
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    
    GENDER_CHOICES = [
        (MALE,"MALE"),
        (FEMALE, "FEMALE"),
        (OTHER,"OTHER")
    ]

    profile_image = models.FileField(upload_to='profile_images', null = True, blank = True)
    prefix = models.CharField(max_length = 5, default = "Mr.", null =True, blank = True)
    status = models.CharField(max_length= 50,choices=USER_STATUS_CHOICES,default=ACTIVE)
    user_type = models.CharField(max_length=25, choices= USER_TYPE_CHOICES, default = PATIENT)
    full_name = models.CharField(max_length=90)
    middle_name = models.CharField(max_length = 25,default = "", blank = True)
    gender = models.CharField(max_length = 25,default= MALE, choices=GENDER_CHOICES, null = True, blank = True)
    dob = models.DateField(blank = True, null = True)
    age = models.IntegerField(blank = True, null = True)
    business = models.ForeignKey(Business, null=True, blank = True,related_name="business_user", on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_string = models.TextField(blank=True, null=True)
    preferred_time_zone = models.CharField(max_length = 25, default = "CDT", null = True, blank = True)
    added_by = models.ForeignKey('self',blank = True, null = True, related_name="added_users",on_delete= models.SET_NULL)    
    price_per_unit = models.ForeignKey(CurrencyValueMapping,default = None, related_name = "price_mapping_user", on_delete= models.CASCADE, null= True, blank = True)
    remark = models.TextField(blank = True, null = True)
    reseller_type = models.CharField(max_length=50,blank = True, null = True)

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
        
        
class UserLaguageMapping(models.Model):
    user = models.ForeignKey(UserAccount,related_name = "user_languages",on_delete = models.CASCADE)
    language = models.ForeignKey(Language,related_name= "language_users",on_delete = models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'language')
    
class UserTreatmentMapping(models.Model):
    SOUND_TREATMENT = "SOUND_TREATMENT"
    RF_LEFT = "RF_LEFT"
    RF_RIGHT = "RF_RIGHT"
    
    TREATMENT_TYPE_CHOICES = [
        (SOUND_TREATMENT,"SOUND_TREATMENT"),
        (RF_RIGHT,"RF_RIGHT"),
        (RF_LEFT,"RF_LEFT")
    ]
    treatment_type = models.CharField(max_length= 25, choices= TREATMENT_TYPE_CHOICES, default= SOUND_TREATMENT)
    user = models.ForeignKey(UserAccount, related_name= "user_treatment",  on_delete= models.CASCADE)
    is_deleted = models.BooleanField(default=False)
        
class MedicalRecord(models.Model):
    
    LEFT_EAR = "LEFT_EAR"
    RIGHT_EAR = "RIGHT_EAR"
    BOTH_EAR = "BOTH_EAR"
    
    EAR_TYPE_CHOICES = [
        (LEFT_EAR,"LEFT_EAR"),
        (RIGHT_EAR,"RIGHT_EAR"),
        (BOTH_EAR,"BOTH_EAR")
    ]
    SUBJECTIVE_TINNITUS = "SUBJECTIVE_TINNITUS"
    OBJECTIVE_TINNITUS = "OBJECTIVE_TINNITUS"
    TONAL_TINNITUS = "TONAL_TINNITUS"
    PULSATILE_TINNITUS = "PULSATILE_TINNITUS"
    MUSCULAR_TINNITUS = "MUSCULAR_TINNITUS"
    NEUROLOGICAL_TINNITUS = "NEUROLOGICAL_TINNITUS"
    SOMATIC_TINNITUS = "SOMATIC_TINNITUS"
    SENSORINEURAL_TINNITUS = "SENSORINEURAL_TINNITUS"

    TINNITUS_TYPE_CHOICES = [
        (SUBJECTIVE_TINNITUS, "SUBJECTIVE_TINNITUS"),
        (OBJECTIVE_TINNITUS, "OBJECTIVE_TINNITUS"),
        (TONAL_TINNITUS, "TONAL_TINNITUS"),
        (PULSATILE_TINNITUS, "PULSATILE_TINNITUS"),
        (MUSCULAR_TINNITUS, "MUSCULAR_TINNITUS"),
        (NEUROLOGICAL_TINNITUS, "NEUROLOGICAL_TINNITUS"),
        (SOMATIC_TINNITUS, "SOMATIC_TINNITUS"),
        (SENSORINEURAL_TINNITUS, "SENSORINEURAL_TINNITUS"),
    ]
    
    tinnitus_start_date = models.DateField(blank= True, null = True)
    ears = models.CharField(max_length= 25, choices= EAR_TYPE_CHOICES, default= BOTH_EAR)
    tinnitus_type = models.CharField(max_length=50, choices= TINNITUS_TYPE_CHOICES, default= SUBJECTIVE_TINNITUS)
    patient = models.ForeignKey(UserAccount, related_name= "medical_record", on_delete= models.CASCADE)
    is_deleted = models.BooleanField(default = False)
    

class Address(models.Model):

    business = models.ForeignKey(Business, null=True, blank = True, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, null=True, blank = True, on_delete=models.CASCADE)
    line_1 = models.TextField()
    line_2 = models.TextField(null=True, blank=True)
    landmark = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    region = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    is_deleted = models.BooleanField(default=False)


class ContactNumber(models.Model):

    business = models.ForeignKey(Business, null=True, blank= True, on_delete=models.CASCADE)
    user = models.ForeignKey(UserAccount, null=True, blank = True, on_delete=models.CASCADE)
    country_code = models.CharField(max_length=5)
    number = models.BigIntegerField()
    is_deleted = models.BooleanField(default=False)

class CardDetails(models.Model):

    number = models.BigIntegerField()
    expiry_date = models.DateField()
    type = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    
    
    
class UserLoginSession(models.Model):
    user = models.ForeignKey(UserAccount, on_delete= models.CASCADE, related_name= "user_sessions")
    ip = models.CharField(max_length=100)
    login_date_time = models.DateTimeField(auto_now_add=True)
    logout_date_time = models.DateTimeField(blank= True, null= True)
    jwt_token = models.CharField(max_length=200)