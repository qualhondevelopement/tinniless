from rest_framework import serializers
from .models import *
from django.db import transaction
from django.core.exceptions import ValidationError

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class UserAccountSerializer(serializers.ModelSerializer):
    added_by = serializers.SerializerMethodField()
    price_per_unit = serializers.SerializerMethodField()
    class Meta:
        model = UserAccount
        fields = ['id','username','profile_image','prefix','first_name','middle_name','last_name','email','user_type','full_name','status',
                  'gender','dob','age','preferred_time_zone','added_by','price_per_unit','remark']
        
    def get_added_by(self,obj):
        return obj.added_by.first_name if obj.added_by else None
    
    def get_price_per_unit(self,obj):
        # return obj.price_per_unit:05.2f
        return obj.price_per_unit

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ContactNumberSerializer(serializers.ModelSerializer):
    country_code = serializers.SerializerMethodField()
    class Meta:
        model = ContactNumber
        fields = '__all__'
        
    def get_country_code(self,obj):
        return "+" + str(obj.country_code)

class CardDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardDetails
        fields = '__all__'
        
class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['tinnitus_start_date','ears','tinnitus_type','patient']
        
class UserTreatmentMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTreatmentMapping
        fields = ('treatment_type','user')

class LanguageSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    class Meta:
        model = Language
        fields = '__all__'
        
    def get_value(self,obj):
        return obj.language_name
    def get_label(self,obj):
        return obj.language_name

# class PatientSerializer(serializers.Serializer):
#     first_name = serializers.CharField()
#     middle_name = serializers.CharField(allow_blank=True, required=False)
#     last_name = serializers.CharField()
#     phone_number = serializers.CharField()
#     email = serializers.EmailField()
#     dob = serializers.DateField()
#     age = serializers.IntegerField()
#     lang = serializers.CharField()
    
#     tinnitus_start_date = serializers.DateField(allow_null=True, required=False)
#     ears = serializers.CharField(allow_blank=True, required=False)
#     tinnitus_type = serializers.CharField(allow_blank=True, required=False)
#     treatment = serializers.CharField(allow_blank=True, required=False)
    
#     address1 = serializers.CharField()
#     address2 = serializers.CharField(allow_blank=True, required=False)
#     country = serializers.CharField()
#     state = serializers.CharField()
#     city = serializers.CharField()
#     post_code = serializers.CharField()

#     def create(self, validated_data):
        
#         try:
#             with transaction.atomic():
#                 user_obj = UserAccount.objects.create(
#                     user_type = UserAccount.PATIENT,
#                     first_name = validated_data.first_name,
#                     last_name = validated_data.middle_name + validated_data.last_name,
#                     email = validated_data.email,
#                     dob = validated_data.dob,
#                     age = validated_data.age,
#                     preferred_language = validated_data.lang
#                 )
#                 contact_obj = ContactNumber.objects.create(
#                     user = user_obj,
#                     country_code = validated_data.phone_number.country_code,
#                     number = validated_data.phone_number.number
#                 )
#                 mediacal_record_obj = MedicalRecord.objects.create(
#                     tinnitus_start_date = validated_data.tinnitus_start_date,
#                     ears = validated_data.ears,
#                     tinnitus_type = validated_data.tinnitus_type,
#                     patient  = user_obj
#                 )
#                 for i in validated_data.treatment:
#                     treatment = UserTreatmentMapping.objects.create(
#                         treatment_type = i,
#                         user = user_obj
#                     )
#         except ValidationError as exc:
#             raise ValidationError(exc)
            
#     def update(self, instance, validated_data):
#         # Update and return an existing instance of your model, or handle PUT/PATCH logic
#         pass


def patient_group_serializer_func(user_obj):
    # user_obj = UserAccount.objects.get(id= id)
    contact_obj = ContactNumber.objects.get(user = user_obj,is_deleted = False)
    medical_record_obj = MedicalRecord.objects.get(patient = user_obj,is_deleted = False)
    add_obj = Address.objects.filter(user = user_obj,is_deleted = False)
    treatments = UserTreatmentMapping.objects.filter(user = user_obj,is_deleted = False)
        
    user_serializer = UserAccountSerializer(user_obj)
    contact_serializer = ContactNumberSerializer(contact_obj)
    medical_record_serializer = MedicalRecordSerializer(medical_record_obj)
    treatment_serializer = UserTreatmentMappingSerializer(treatments,many = True)
    address_serializer = AddressSerializer(add_obj,many = True)
    mappings = UserLaguageMapping.objects.filter(user = user_obj)
    lang_objs = [i.language for i in mappings]
    language_serializer  = LanguageSerializer(lang_objs,many = True)
    data = {
        "user":user_serializer.data,
        "language":language_serializer.data,
        "contact":contact_serializer.data,
        "medical_record":medical_record_serializer.data,
        "treatment":treatment_serializer.data,
        "address":address_serializer.data
    }
    return data

def operator_group_serializer_func(user_obj):
    # user_obj = UserAccount.objects.get(id= id)
    business_obj = user_obj.business
    mappings = UserLaguageMapping.objects.filter(user = user_obj)
    lang_objs = [i.language for i in mappings]
    
    contact_obj = ContactNumber.objects.get(business = business_obj,is_deleted = False)
    add_obj = Address.objects.filter(business = business_obj,is_deleted = False)
    
    business_serializer =BusinessSerializer(business_obj)
    user_serializer = UserAccountSerializer(user_obj)
    contact_serializer = ContactNumberSerializer(contact_obj)
    address_serializer = AddressSerializer(add_obj,many = True)
    language_serializer  = LanguageSerializer(lang_objs,many = True)
    data = {
        "user":user_serializer.data,
        "business":business_serializer.data,
        "language":language_serializer.data,
        "contact":contact_serializer.data,
        "address":address_serializer.data
    }
    return data

def reseller_group_serializer_func(user_obj):

    business_obj = user_obj.business
    
    personal_contact_obj = ContactNumber.objects.get(user = user_obj,is_deleted = False)
    business_contact_obj = ContactNumber.objects.get(business = business_obj,is_deleted = False)
    add_objs = Address.objects.filter(business = business_obj,is_deleted = False)
    
    user_serializer = UserAccountSerializer(user_obj)
    business_serializer = BusinessSerializer(business_obj)
    personal_contact_serializer = ContactNumberSerializer(personal_contact_obj)
    business_contact_serializer = ContactNumberSerializer(business_contact_obj)
    address_serializer = AddressSerializer(add_objs,many = True)
    data = {
        "user":user_serializer.data,
        "business":business_serializer.data,
        "personal_contact":personal_contact_serializer.data,
        "business_contact":business_contact_serializer.data,
        "address":address_serializer.data
    }
    return data

def retailer_group_serializer_func(user_obj):

    mappings = UserLaguageMapping.objects.filter(user = user_obj)
    lang_objs = [i.language for i in mappings]
    
    contact_obj = ContactNumber.objects.get(user = user_obj,is_deleted = False)
    add_obj = Address.objects.filter(user = user_obj,is_deleted = False)
    
    user_serializer = UserAccountSerializer(user_obj)
    contact_serializer = ContactNumberSerializer(contact_obj)
    address_serializer = AddressSerializer(add_obj,many = True)
    language_serializer  = LanguageSerializer(lang_objs,many = True)
    data = {
        "user":user_serializer.data,
        "language":language_serializer.data,
        "contact":contact_serializer.data,
        "address":address_serializer.data
    }
    return data
