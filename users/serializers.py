from rest_framework import serializers
from .models import *
from django.db import transaction
from django.core.exceptions import ValidationError

class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id','username','first_name','middle_name','last_name','email','user_type','full_name',
                  'dob','age','preferred_time_zone','preferred_language']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ContactNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNumber
        fields = '__all__'

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
    data = {
        "user":user_serializer.data,
        "contact":contact_serializer.data,
        "medical_record":medical_record_serializer.data,
        "treatment":treatment_serializer.data,
        "address":address_serializer.data
    }
    return data