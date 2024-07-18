from django.shortcuts import render
from users.models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.response import Response
# Create your views here.

class AdminManagePatient(APIView):
    
    def get(self,request,format = None):
        id = request.query_params.get('id')
        try:
            user_obj = UserAccount.objects.get(id= id)
        except UserAccount.DoesNotExist:
            return Response(
                {
                    "error":"user with given id does not exist"
                },
                400
            )
        contact_obj = ContactNumber.objects.get(user = user_obj)
        medical_record_obj = MedicalRecord.objects.get(patient = user_obj)
        add_obj = Address.objects.filter(user = user_obj)
        treatments = UserTreatmentMapping.objects.filter(user = user_obj)
            
        user_serializer = UserAccountSerializer(user_obj)
        contact_serializer = ContactNumberSerializer(contact_obj)
        medical_record_serializer = MedicalRecordSerializer(medical_record_obj)
        treatment_serializer = UserTreatmentMappingSerializer(treatments,many = True)
        address_serializer = AddressSerializer(add_obj,many = True)
        resp_data = {
            "user":user_serializer.data,
            "contact":contact_serializer.data,
            "medical_record":medical_record_serializer.data,
            "treatment":treatment_serializer.data,
            "address":address_serializer.data
        }
        return Response(
            resp_data,
            200
        )
            
            
    def post(self,request,format = None):
            
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email")
        dob = request.data.get("dob")
        age = request.data.get("age")
        lang=  request.data.get("lang") 
        
        tinnitus_start_date = request.data.get("tinnitus_start_date")
        ears = request.data.get("ears")
        tinnitus_type = request.data.get("tinnitus_type")
        treatment = request.data.get("treatment")
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")
        
        
        try:
            with transaction.atomic():
                user_obj = UserAccount.objects.create(
                    user_type = UserAccount.PATIENT,
                    first_name = first_name,
                    middle_name = middle_name,
                    last_name = last_name,
                    email = email,
                    dob = dob,
                    age = age,
                    preferred_language = lang
                )
                print(phone_number)
                contact_obj = ContactNumber.objects.create(
                    user = user_obj,
                    country_code = phone_number["country_code"],
                    number = phone_number["number"]
                )
                mediacal_record_obj = MedicalRecord.objects.create(
                    tinnitus_start_date = tinnitus_start_date,
                    ears = ears,
                    tinnitus_type = tinnitus_type,
                    patient  = user_obj
                )
                for i in treatment:
                    treatment_obj = UserTreatmentMapping.objects.create(
                        treatment_type = i,
                        user = user_obj
                    )
                treatments=  UserTreatmentMapping.objects.filter(user = user_obj)
                add_obj = Address.objects.create(
                    user = user_obj,
                    line_1 = address1,
                    line_2 = address2,
                    country = country,
                    state = state,
                    city = city,
                    postal_code = post_code
                )
                user_serializer = UserAccountSerializer(user_obj)
                contact_serializer = ContactNumberSerializer(contact_obj)
                medical_record_serializer = MedicalRecordSerializer(mediacal_record_obj)
                treatment_serializer = UserTreatmentMappingSerializer(treatments,many = True)
                address_serializer = AddressSerializer(add_obj)
                resp_data = {
                    "user":user_serializer.data,
                    "contact":contact_serializer.data,
                    "medical_record":medical_record_serializer.data,
                    "treatment":treatment_serializer.data,
                    "address":address_serializer.data
                }
                return Response(
                    resp_data,
                    200
                )
                
        except Exception as e:
            print(str(e))
            return Response(
                {
                    "error":f"Failed to create the user because of \n {str(e)}"
                },
                400
            )
    
    def patch(self, request, format = None):
        
        user_id = request.data.get("user_id")
        
        first_name = request.data.get("first_name",None)
        middle_name = request.data.get("middle_name",None)
        last_name = request.data.get("last_name",None)
        phone_number = request.data.get("phone_number",None)
        email = request.data.get("email",None)
        dob = request.data.get("dob",None)
        age = request.data.get("age",None)
        lang=  request.data.get("lang",None) 
        
        tinnitus_start_date = request.data.get("tinnitus_start_date",None)
        ears = request.data.get("ears",None)
        tinnitus_type = request.data.get("tinnitus_type",None)
        treatment = request.data.get("treatment",None)
        
        address1 = request.data.get("address1",None)
        address2 = request.data.get("address2",None)
        country = request.data.get("country",None)
        state = request.data.get("state",None)
        city = request.data.get("city",None)
        post_code = request.data.get("post_code",None)
        
        try:
            user_obj = UserAccount.objects.get(id = user_id)
        except UserAccount.DoesNotExist:
            return Response(
                {
                    "error":"User with given id does not exists"
                },
                400
            )
            
        if first_name:
            user_obj.first_name = first_name
        if middle_name:
            user_obj.middle_name = middle_name
        if last_name:
            user_obj.last_name = last_name
        if email:
            user_obj.email = email
        if dob:
            user_obj.dob = dob
        if age:
            user_obj.age = age
        if lang:
            user_obj.preferred_language = lang
        user_obj.save()
        
        if phone_number:
            contact_obj = ContactNumber.objects.filter(user = user_obj).first()
            contact_obj.country_code = phone_number.country_code
            contact_obj.number = phone_number.number
            contact_obj.save()
          
          
        medical_obj = MedicalRecord.objects.get(patient = user_obj)  
        if tinnitus_start_date: 
            medical_obj.tinnitus_start_date = tinnitus_start_date
        if ears:
            medical_obj.ears = ears
        if tinnitus_type:
            medical_obj.tinnitus_type = tinnitus_type
        medical_obj.save()
        
        if treatment:
            treatments = UserTreatmentMapping.objects.filter(user = user_obj)
            treatments.delete()
            for i in treatment:
                UserTreatmentMapping.objects.create(
                    treatment_type = i,
                    user = user_obj
                )
        add_obj = Address.objects.filter(user = user_obj).first()
        if address1:
            add_obj.line_1 = address1
        if address2:
            add_obj.line_2 = address2
        if city:
            add_obj.city = city
        if state:
            add_obj.state = state
        if country:
            add_obj.country=  country
        if post_code:
            add_obj.postal_code = post_code
        add_obj.save()
        
        return Response(
            {
                "data":patient_group_serializer_func(user_obj)
            },
            200
        )
        
    def delete(self, request,format = None):
        id = request.data.get("user_id")
        user_obj = UserAccount.objects.get(id = id)
        user_obj.is_deleted = True
        user_obj.save()
        contact_objs = ContactNumber.objects.filter(user = user_obj)
        contact_objs.update(is_deleted = True)
        add_objs = Address.objects.filter(user = user_obj)
        add_objs.update(is_deleted = True)
        treatments = UserTreatmentMapping.objects.filter(user = user_obj)
        treatments.update(is_deleted = False)
        medical_obj = MedicalRecord.objects.get(patient = user_obj)
        medical_obj.is_deleted = True
        medical_obj.save()
        
        return Response(
            {
                "success":"The Patient has been deleted"
            },
            200
        )
        
        
class AdminListPatient(APIView):
    def get(self, request, format = None):
        users = UserAccount.objects.filter(
            user_type = UserAccount.PATIENT,
            is_archived = False,
            is_deleted = False
        ).order_by("created_at")
        resp_data= []
        for u in users:
            resp_data.append(patient_group_serializer_func(u))
            
        return Response(
            {
                "data":resp_data
            },
            200
        )
        


