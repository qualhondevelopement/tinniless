from django.shortcuts import render
from users.models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes,force_str
from django.urls import reverse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from .utils import *
import json
#===USER_AUTH===========================================================================================================

class LoginAPI(APIView):
    def get_user(self, email):
        try:
            return UserAccount.objects.get(email=email,is_archived = False)
        except UserAccount.DoesNotExist:
            return None

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        if email is None or password is None:
            return Response(
                {'error': 'Please provide both email and password'},
                status = 400
            )

        user = self.get_user(email)

        if user is None:
            return Response(
                {'error': 'Invalid email or password'},
                status=400
            )

        if not user.check_password(password):
            return Response(
                {'error': 'Invalid email or password'},
                status=400
            )
        
        if user.is_archived:
            return Response(
                {"error":"Your Account is Archived"},
                status=400
            )
            
        if not user.is_active:
            return Response(
                {"error":"Your Account is not active"},
                status=400
            )
            
        ip =  get_client_ip(request=request)
        if not ip:
            return Response(
                {"error":"Failed to get the IP address"},
                status=400
            )
        
        if user.user_type == UserAccount.ADMIN:
            old_sessions  = UserLoginSession.objects.filter(
                ip = ip,
                logout_date_time = None,
                user = user
            )
            if old_sessions.exists():
                old_sessions.update(logout_date_time = timezone.now())
            
            jwt_token = create_login_session(request,user,ip)
        else:
            old_sessions  = UserLoginSession.objects.filter(
                logout_date_time = None,
                user = user
            )
            if old_sessions.exists():
                old_sessions.update(logout_date_time = timezone.now())
            
            jwt_token = create_login_session(request,user,ip)
            
        return Response(
            {
                "success":"User has been Logged in",
                "token":jwt_token,
                "user_details":UserAccountSerializer(user).data
            },
            200
        )
                             
class LogoutAPIView(APIView):
    def get(self, request, format=None):
        try:
            token= request.GET.get('token')
            from .utils import update_logout_session
            is_successful,message,code = update_logout_session(token)
            if is_successful == False:
                return Response({"error":message},code)

            return Response({'success': 'Logged out successfully.'})
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token.'}, status=403)

class PasswordResetRequestView(APIView):

    def post(self, request):
        email = request.data.get('email')
        user = get_object_or_404(UserAccount, email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f"\
           http://10.10.0.254:8003/api/users/auth/reset-password/{uid}/{token}/"
        
        print("\n\n",reset_link,"\n\n")
        send_mail(
            'Password Reset Request',
            f'Click the link to reset your password: {reset_link}',
            'your-email@example.com',
            [email],
            fail_silently=False,
        )
        return Response({'message': 'Password reset link sent.'})

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_object_or_404(UserAccount, pk=uid)
        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            verify_new_password = request.data.get("verify_new_password")
            if new_password != verify_new_password:
                return Response(
                    {
                        'error': "The password does not match"
                    },
                    status=400
                )
            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset.'})
        else:
            return Response({'message': 'Invalid token.'}, status=400)
        

class GetuserDetail(APIView):
    authentication_classes = (JwtAuthentication,)
    def get(self,request,format = None):
        user = request.user
        print("herer")
        
        serializer = UserAccountSerializer(user)
        print(serializer.data)
        return Response(
                {
                    "success":'User is Logged in',
                    "data":serializer.data
                },
                200
            )
        

class IsExisting(APIView):
    # authentication_classes = (JwtAuthentication,)
    def get(self,request, format = None):
        email = request.query_params.get("email")
        if email:
            if UserAccount.objects.filter(email = email).exists():
                return Response(
                    {
                        "error":"Email Already Exists",
                        "success":False
                    },
                    400
                )
        phone = request.query_params.get("phone")
        
        if phone:
        
            phone = json.loads(phone)
            print(phone)
            if ContactNumber.objects.filter(
                country_code = phone[
                    "country_code"
                ].replace("+",'').replace(" ",''),
                number = int(phone["number"])
            ).exists():
                return Response(
                    {
                        "error":"Phone number already exists"
                    },
                    400
                )
        return Response(
            {
                "message":"credentials can be used",
                "success":True
            },
            200
        )
        

#===PATIENT=============================================================================================================

class AdminManagePatient(APIView):
    
    authentication_classes = [JwtAuthentication,]
    
    def get(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
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
        mappings = UserLaguageMapping.objects.filter(user = user_obj)
        lang_objs = [i.language for i in mappings]
            
        user_serializer = UserAccountSerializer(user_obj)
        contact_serializer = ContactNumberSerializer(contact_obj)
        medical_record_serializer = MedicalRecordSerializer(medical_record_obj)
        treatment_serializer = UserTreatmentMappingSerializer(
            treatments,
            many = True
        )
        address_serializer = AddressSerializer(add_obj,many = True)
        language_serializer  = LanguageSerializer(lang_objs,many = True)
        resp_data = {
            "user":user_serializer.data,
            "contact":contact_serializer.data,
            "language_serializer":language_serializer.data,
            "medical_record":medical_record_serializer.data,
            "treatment":treatment_serializer.data,
            "address":address_serializer.data
        }
        return Response(
            resp_data,
            200
        )
            
            
    def post(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
            
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email")
        gender = request.data.get("gender")
        if gender and gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
        if gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
        
        dob = request.data.get("dob")
        age = request.data.get("age")
        lang=  request.data.get("lang") 
        price_per_unit = request.data.get("price_per_unit")
        
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
        
        if len(post_code)<3 or len(post_code)>9:
            return Response(
                {
                    "  error":"Postal code length is invalid"
                },
                400
            )
        
        date_object = datetime.strptime(dob, "%Y-%m-%d")
        if date_object> datetime.now():
            return Response(
                {
                    'error':"Date of Birth can not be in future"
                },
                400
            )
        if int(age)<0:
            return Response(
                {
                    "error":"Age can not be negative"
                },
                400
            )
        
        # try:
        with transaction.atomic():
            
            
            lang_obj = Language.objects.get(language_name = lang)
            user_obj = UserAccount.objects.create(
                user_type = UserAccount.PATIENT,
                first_name = first_name,
                middle_name = middle_name,
                last_name = last_name,
                email = email,
                gender = gender,
                dob = dob,
                age = age,
                added_by = user,
                price_per_unit = price_per_unit if price_per_unit else 0.00
            )
            mapp = UserLaguageMapping.objects.create(
                user = user_obj,
                language = lang_obj
            )
            contact_obj = ContactNumber.objects.create(
                user = user_obj,
                country_code = phone_number["country_code"].replace('+',''),
                number = int(phone_number["number"])
            )
            if tinnitus_start_date == "":
                tinnitus_start_date = None
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
            treatments=  UserTreatmentMapping.objects.filter(user =user_obj)
            add_obj = Address.objects.create(
                user = user_obj,
                line_1 = address1,
                line_2 = address2,
                country = country,
                state = state,
                city = city,
                postal_code = post_code
            )
            add_objs = Address.objects.filter(
                user = user_obj,
            )
            lang_serializer = LanguageSerializer(lang_obj)
            user_serializer = UserAccountSerializer(user_obj)
            contact_serializer = ContactNumberSerializer(contact_obj)
            medical_record_serializer = MedicalRecordSerializer(
                mediacal_record_obj
            )
            treatment_serializer = UserTreatmentMappingSerializer(
                treatments,
                many = True
            )
            address_serializer = AddressSerializer(add_objs,many = True)
            resp_data = {
                "user":user_serializer.data,
                "language":lang_serializer.data,
                "contact":contact_serializer.data,
                "medical_record":medical_record_serializer.data,
                "treatment":treatment_serializer.data,
            "address":address_serializer.data
            }
            return Response(
                resp_data,
                200
            )
                
        # except Exception as e:
        #     print(str(e))
        #     return Response(
        #         {
        #             "error":f"Failed to create the user because of \n {str(e)}"
        #         },
        #         400
        #     )
    
    def patch(self, request, format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
        user_id = request.data.get("user_id")
        
        first_name = request.data.get("first_name",None)
        middle_name = request.data.get("middle_name",None)
        last_name = request.data.get("last_name",None)
        phone_number = request.data.get("phone_number",None)
        email = request.data.get("email",None)
        dob = request.data.get("dob",None)
        age = request.data.get("age",None)
        lang=  request.data.get("lang",None)
        status = request.data.get("status", None)
        price_per_unit = request.data.get("price_per_unit")
        gender = request.data.get("gender")
        if gender and gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
         
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
        if lang: 
            try:
                lang_obj = Language.objects.get(language_name = lang)
            except:
                return Response(
                    {
                        "error":"Language with given code does not exist",
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
        if price_per_unit:
            user_obj.price_per_unit = price_per_unit
            
        if gender:
            user_obj.gender = gender
        if lang:
            mapping = user_obj.user_languages.all().first()
            if mapping :
                mapping.language = lang_obj
            else:
                mapping = UserLaguageMapping.objects.create(
                    user = user_obj,
                    language = lang_obj
                )
            mapping.save()
        if status:
            user_obj.status = status
        user_obj.save()
        
        if phone_number:
            contact_obj = ContactNumber.objects.filter(user = user_obj).first()
            contact_obj.country_code=phone_number[
                "country_code"
            ].replace("+",'')
            contact_obj.number = int(phone_number["number"])
            contact_obj.save()
          
          
        medical_obj = MedicalRecord.objects.get(patient = user_obj)  
        if  tinnitus_start_date != None:
            if tinnitus_start_date == "":
                tinnitus_start_date = None
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
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
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
    
    authentication_classes = [JwtAuthentication,]
    
    def get(self, request, format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
        users = UserAccount.objects.filter(
            user_type = UserAccount.PATIENT,
            is_archived = False,
            is_deleted = False
        ).order_by("-created_at")
        resp_data= []
        for u in users:
            resp_data.append(patient_group_serializer_func(u))
            
        return Response(
            {
                "data":resp_data
            },
            200
        )
        
#===OPERATOR============================================================================================================

class AdminManageOperator(APIView):
    
    authentication_classes = [JwtAuthentication,]
    
    def get(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
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
        business_obj = user_obj.business
        contact_obj = ContactNumber.objects.get(business = business_obj)
        add_obj = Address.objects.filter(business = business_obj)
        mappings = UserLaguageMapping.objects.filter(user = user_obj)
        lang_objs = [i.language for i in mappings]
        
            
        user_serializer = UserAccountSerializer(user_obj)
        contact_serializer = ContactNumberSerializer(contact_obj)
        address_serializer = AddressSerializer(add_obj,many = True)
        business_serializer = BusinessSerializer(business_obj)
        language_serializer = LanguageSerializer(lang_objs,many = True)
        resp_data = {
            "user":user_serializer.data,
            "contact":contact_serializer.data,
            "address":address_serializer.data,
            "business":business_serializer.data,
            "language":language_serializer.data
        }
        return Response(
            resp_data,
            200
        )
            
            
    def post(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
            
        prefix = request.data.get("prefix")
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        tax_number = request.data.get("tax_number")
        tax_document = request.FILES.get("tax_doc")
        phone_number = json.loads(request.data.get("phone_number"))
        print(phone_number)
        email = request.data.get("email")
        dob = request.data.get("dob")
        age = request.data.get("age")
        gender = request.data.get("gender")
        if gender and gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
        profile_imge = request.FILES.get("profile_image")
        
        lang_array=  json.loads(request.data.get("lang"))
        print(lang_array)
        preferred_time_zone = request.data.get("prefered_time_zone")
        remark = request.data.get("remark")
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")
        
        if len(post_code)<3 or len(post_code)>9:
            return Response(
                {
                    "  error":"Postal code length is invalid"
                },
                400
            )
        
        date_object = datetime.strptime(dob, "%Y-%m-%d")
        if date_object> datetime.now():
            return Response(
                {
                    'error':"Date of Birth can not be in future"
                },
                400
            )
        if int(age)<0:
            return Response(
                {
                    "error":"Age can not be negative"
                },
                400
            )
        
        # try:
        with transaction.atomic():
                print(lang_array)
                lang_array = [i["language_name"] for i in lang_array]
                print(lang_array)
                
                lang_objs = Language.objects.filter(
                    language_name__in = lang_array
                )
                print(lang_objs)
                
                business_obj = Business.objects.create(
                    business_type = Business.INDIVIDUAL,
                    tax_number = tax_number,
                    tax_document = tax_document
                )
                user_obj = UserAccount.objects.create(
                    username = email,
                    user_type = UserAccount.OPERATOR,
                    prefix = prefix,
                    first_name = first_name,
                    middle_name = middle_name,
                    last_name = last_name,
                    email = email,
                    gender = gender,
                    profile_image = profile_imge,
                    dob = dob,
                    age = age,
                    added_by = user,
                    preferred_time_zone = preferred_time_zone,
                    remark = remark,
                    business = business_obj
                )
                lang_mappings = []
                for i in lang_objs:
                    mapping = UserLaguageMapping.objects.create(
                        user = user_obj,
                        language = i 
                    )
                    lang_mappings.append(mapping)

                contact_obj = ContactNumber.objects.create(
                    business = business_obj,
                    country_code = phone_number["country_code"].replace('+',''),
                    number = int(phone_number["number"])
                )
                
                add_obj = Address.objects.create(
                    business = business_obj,
                    line_1 = address1,
                    line_2 = address2,
                    country = country,
                    state = state,
                    city = city,
                    postal_code = post_code
                )
                add_objs = Address.objects.filter(
                    business = business_obj,
                )
                lang_objs = [i.language for i in lang_mappings]
                
                
                lang_serializer = LanguageSerializer(lang_objs, many = True)
                business_serializer =BusinessSerializer(business_obj)
                user_serializer = UserAccountSerializer(user_obj)
                contact_serializer = ContactNumberSerializer(contact_obj)
                address_serializer = AddressSerializer(add_objs,many = True)
                resp_data = {
                    "business":business_serializer.data,
                    "user":user_serializer.data,
                    "language":lang_serializer.data,
                    "contact":contact_serializer.data,
                    "address":address_serializer.data
                }
                return Response(
                    resp_data,
                    200
                )
            
        # except Exception as e:
        #     print(str(e))
        #     return Response(
        #         {
        #             "error":f"Failed to create the user because of \n {str(e)}"
        #         },
        #         400
        #     )
    
    def patch(self, request, format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        user_id = request.data.get("user_id")
        
        prefix = request.data.get("prefix")
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        tax_number = request.data.get("tax_number")
        tax_document = request.FILES.get("tax_doc")
        phone_number = request.data.get("phone_number")
        if phone_number:
            phone_number = json.loads(phone_number)
        email = request.data.get("email")
        dob = request.data.get("dob")
        age = request.data.get("age")
        gender = request.data.get("gender")
        if gender and gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
        profile_imge = request.FILES.get("profile_image")
        status = request.data.get("status")
        
        lang_array=  request.data.get("lang")
        if lang_array:
            lang_array = json.loads(lang_array)
        preferred_time_zone = request.data.get("prefered_time_zone")
        remark = request.data.get("remark")
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")
        
        try:
            user_obj = UserAccount.objects.get(
                id = user_id,
                user_type = UserAccount.OPERATOR
            )
        except UserAccount.DoesNotExist:
            return Response(
                {
                    "error":"User with given id does not exists"
                },
                400
            )
        
        if lang_array:
            lang_array = [i["language_name"] for i in lang_array]
                
            lang_objs = Language.objects.filter(language_name__in = lang_array)
        business_obj  = user_obj.business
            
        if tax_number:
            business_obj.tax_number = tax_number
        if tax_document:
            business_obj.tax_document = tax_document
        business_obj.save()
        
        user_obj = UserAccount.objects.get(business = business_obj)
            
        if prefix:
            user_obj.prefix = prefix
        if first_name:
            user_obj.first_name = first_name
        if middle_name:
            user_obj.middle_name = middle_name
        if last_name:
            user_obj.last_name = last_name
        if email:
            user_obj.email = email
            user_obj.username = email
        if gender:
            user_obj.gender = gender
        if dob:
            user_obj.dob = dob
        if age:
            user_obj.age = age
            
        if status:
            user_obj.status = status
        if lang_array:
            lang_mapping_objs = UserLaguageMapping.objects.filter(
                user = user_obj
            )
            lang_mapping_objs.delete()
            for i in lang_objs:
                UserLaguageMapping.objects.create(
                    user = user_obj,
                    language = i 
                )
        if preferred_time_zone:
            user_obj.preferred_time_zone = preferred_time_zone
        if remark :
            user_obj.remark = remark
        if profile_imge:
            user_obj.profile_image = profile_imge
        user_obj.save()
        
        if phone_number:
            contact_obj = ContactNumber.objects.filter(
                business = business_obj
            ).first()
            contact_obj.country_code = phone_number[
                "country_code"
            ].replace("+",'')
            contact_obj.number = int(phone_number["number"])
            contact_obj.save()
          
        add_obj = Address.objects.filter(business = business_obj).first()
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
                "data":operator_group_serializer_func(user_obj)
            },
            200
        )
        
    def delete(self, request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an Admin"
                },
                400
            )
        
        id = request.data.get("user_id")
        user_obj = UserAccount.objects.get(id = id)
        user_obj.is_deleted = True
        user_obj.save()
        business_obj = user_obj.business
        business_obj.is_deleted = True
        business_obj.save()
        contact_objs = ContactNumber.objects.filter(business = business_obj)
        contact_objs.update(is_deleted = True)
        add_objs = Address.objects.filter(business = business_obj)
        add_objs.update(is_deleted = True)
        user_obj.user_languages.all().delete()
        
        return Response(
            {
                "success":"The Operator has been deleted"
            },
            200
        )
        

class AdminListOperator(APIView):
    
    authentication_classes = [JwtAuthentication,]
    
    def get(self, request, format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
        users = UserAccount.objects.filter(
            user_type = UserAccount.OPERATOR,
            is_archived = False,
            is_deleted = False
        ).order_by("-created_at")
        resp_data= []
        for u in users:
            resp_data.append(operator_group_serializer_func(u))
            
        return Response(
            {
                "data":resp_data
            },
            200
        )
     
#===RETAILER============================================================================================================

class AdminManageRetailer(APIView):
    authentication_classes = (JwtAuthentication,)
    
    def get(self,request,format= None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
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
        business_obj = user_obj.business
        contact_obj = ContactNumber.objects.get(business = business_obj)
        add_obj = Address.objects.filter(business = business_obj)
        mappings = UserLaguageMapping.objects.filter(user = user_obj)
        lang_objs = [i.language for i in mappings]
        
            
        user_serializer = UserAccountSerializer(user_obj)
        contact_serializer = ContactNumberSerializer(contact_obj)
        address_serializer = AddressSerializer(add_obj,many = True)
        business_serializer = BusinessSerializer(business_obj)
        language_serializer = LanguageSerializer(lang_objs,many = True)
        resp_data = {
            "user":user_serializer.data,
            "contact":contact_serializer.data,
            "address":address_serializer.data,
            "business":business_serializer.data,
            "language":language_serializer.data
        }
        return Response(
            resp_data,
            200
        )
    
    def post(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
            
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email")
        dob = request.data.get("dob")
        age = request.data.get("age")
        gender = request.data.get("gender")
        if gender and gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
        price_per_unit = request.data.get("price_per_unit")
        
        lang=  request.data.get("lang")
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")
        
        if len(post_code)< 3 or len(post_code)>9:
            return Response(
                {
                    "  error":"Postal code length is invalid"
                },
                400
            )
        
        date_object = datetime.strptime(dob, "%Y-%m-%d")
        if date_object> datetime.now():
            return Response(
                {
                    'error':"Date of Birth can not be in future"
                },
                400
            )
        if int(age)<0:
            return Response(
                {
                    "error":"Age can not be negative"
                },
                400
            )
        
        # try:
        with transaction.atomic():
                
                lang_obj = Language.objects.get(
                    language_name__in = lang
                )
                
                user_obj = UserAccount.objects.create(
                    username = email,
                    user_type = UserAccount.RETAILER,
                    first_name = first_name,
                    middle_name = middle_name,
                    last_name = last_name,
                    email = email,
                    gender = gender,
                    dob = dob,
                    age = age,
                    added_by = user,
                    price_per_unit = price_per_unit
                )

                mapping = UserLaguageMapping.objects.create(
                    user = user_obj,
                    language = lang_obj
                )

                lang_mappings = [mapping]

                contact_obj = ContactNumber.objects.create(
                    user = user_obj,
                    country_code = phone_number["country_code"].replace('+',''),
                    number = int(phone_number["number"])
                )
                
                add_obj = Address.objects.create(
                    user = user_obj,
                    line_1 = address1,
                    line_2 = address2,
                    country = country,
                    state = state,
                    city = city,
                    postal_code = post_code
                )
                add_objs = Address.objects.filter(
                    user = user_obj,
                )
                lang_objs = [i.language for i in lang_mappings]
                
                
                lang_serializer = LanguageSerializer(lang_objs, many = True)
                user_serializer = UserAccountSerializer(user_obj)
                contact_serializer = ContactNumberSerializer(contact_obj)
                address_serializer = AddressSerializer(add_objs,many = True)
                resp_data = {
                    "user":user_serializer.data,
                    "language":lang_serializer.data,
                    "contact":contact_serializer.data,
                    "address":address_serializer.data
                }
                return Response(
                    resp_data,
                    200
                )
            
        # except Exception as e:
        #     print(str(e))
        #     return Response(
        #         {
        #             "error":f"Failed to create the user because of \n {str(e)}"
        #         },
        #         400
        #     )
    
    def patch(self,request ,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        user_id = request.data.get("user_id")
        
        first_name = request.data.get("first_name")
        middle_name = request.data.get("middle_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")
        email = request.data.get("email")
        dob = request.data.get("dob")
        age = request.data.get("age")
        gender = request.data.get("gender")
        if gender and gender not in [UserAccount.MALE, UserAccount.FEMALE, UserAccount.OTHER]:
            return Response(
                {
                    "error":"Gender is Invalid"
                },
                400
            )
        price_per_unit = request.data.get("price_per_unit")
        status = request.data.get("status")
        
        lang=  request.data.get("lang")
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")
        
        try:
            user_obj = UserAccount.objects.get(
                id = user_id,
                user_type = UserAccount.RETAILER
            )
        except UserAccount.DoesNotExist:
            return Response(
                {
                    "error":"User with given id does not exists"
                },
                400
            )
        
        if lang:
            lang_obj = Language.objects.filter(language_name__in = lang["language_name"])
            
        
        if first_name:
            user_obj.first_name = first_name
        if middle_name:
            user_obj.middle_name = middle_name
        if last_name:
            user_obj.last_name = last_name
        if email:
            user_obj.email = email
            user_obj.username = email
        if gender:
            user_obj.gender = gender
        if dob:
            user_obj.dob = dob
        if age:
            user_obj.age = age
        if price_per_unit:
            user_obj.price_per_unit= price_per_unit
            
        if status:
            user_obj.status = status
        if lang:
            lang_mapping_objs = UserLaguageMapping.objects.filter(
                user = user_obj
            )
            lang_mapping_objs.delete()
            UserLaguageMapping.objects.create(
                user = user_obj,
                language = lang_obj
            )
        user_obj.save()
        
        if phone_number:
            contact_obj = ContactNumber.objects.filter(
                user = user_obj
            ).first()
            contact_obj.country_code = phone_number[
                "country_code"
            ].replace("+",'')
            contact_obj.number = int(phone_number["number"])
            contact_obj.save()
          
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
                "data":retailer_group_serializer_func(user_obj)
            },
            200
        )
        
    
    def delete(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an Admin"
                },
                400
            )
        
        id = request.data.get("user_id")
        user_obj = UserAccount.objects.get(id = id)
        user_obj.is_deleted = True
        user_obj.save()

        contact_objs = ContactNumber.objects.filter(user = user_obj)
        contact_objs.update(is_deleted = True)
        add_objs = Address.objects.filter(user = user_obj)
        add_objs.update(is_deleted = True)
        user_obj.user_languages.all().delete()
        
        return Response(
            {
                "success":"The Operator has been deleted"
            },
            200
        )
    
class AdminListRetailer(APIView):
    authentication_classes = (JwtAuthentication,)
    
    def get(self,request,format= None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
        users = UserAccount.objects.filter(
            user_type = UserAccount.RETAILER,
            is_archived = False,
            is_deleted = False
        ).order_by("-created_at")
        resp_data= []
        for u in users:
            resp_data.append(retailer_group_serializer_func(u))
            
        return Response(
            {
                "data":resp_data
            },
            200
        )
    
    
#===RESELLER============================================================================================================

class AdminManageReseller(APIView):
    authentication_classes = (JwtAuthentication,)
    
    def get(self,request,format= None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
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
        business_obj = user_obj.business
        personal_contact_obj = ContactNumber.objects.get(user = user_obj)
        business_contact_obj = ContactNumber.objects.get(business = business_obj)
        add_obj = Address.objects.filter(business = business_obj)
        
            
        user_serializer = UserAccountSerializer(user_obj)
        personal_contact_serializer = ContactNumberSerializer(personal_contact_obj)
        business_contact_serializer = ContactNumberSerializer(business_contact_obj)
        address_serializer = AddressSerializer(add_obj,many = True)
        business_serializer = BusinessSerializer(business_obj)
        resp_data = {
            "user":user_serializer.data,
            "personal_contact":personal_contact_serializer.data,
            "business_contact":business_contact_serializer.data,
            "address":address_serializer.data,
            "business":business_serializer.data,
        }
        return Response(
            resp_data,
            200
        )
    
    def post(self,request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        first_name = request.data.get("first_name")
        middle_name =request.data.get("middle_name")
        last_name = request.data.get("last_name")    
        personal_phone_number = request.data.get("personal_phone_number")
        business_phone_number = request.data.get("business_phone_number")
        email = request.data.get("email")
        organization_name = request.data.get("organization_name")
        reseller_type = request.data.get("reseller_type")
        tax_number = request.data.get("tax_number")
        price_per_unit = request.data.get("price_per_unit")
        
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")
        
        if len(post_code)< 3 or len(post_code)>9:
            return Response(
                {
                    "  error":"Postal code length is invalid"
                },
                400
            )
        
        
        # try:
        with transaction.atomic():
                
                business_obj = Business.objects.create(
                    business_type = Business.RESELLER,
                    tax_number = tax_number,
                    organization_name = organization_name,
                    
                )
                
                user_obj = UserAccount.objects.create(
                    username = email,
                    user_type = UserAccount.RESELLER,
                    first_name = first_name,
                    middle_name = middle_name,
                    last_name = last_name,
                    email = email,
                    added_by = user,
                    price_per_unit = price_per_unit,
                    business=business_obj,
                    reseller_type = reseller_type
                )
                

                personal_contact_obj = ContactNumber.objects.create(
                    user = user_obj,
                    country_code = personal_phone_number["country_code"].replace('+',''),
                    number = int(personal_phone_number["number"])
                )
                business_contact_obj = ContactNumber.objects.create(
                    business = business_obj,
                    country_code = business_phone_number["country_code"].replace('+',''),
                    number = int(business_phone_number["number"])
                )
                
                add_obj = Address.objects.create(
                    business = business_obj,
                    line_1 = address1,
                    line_2 = address2,
                    country = country,
                    state = state,
                    city = city,
                    postal_code = post_code
                )
                add_objs = Address.objects.filter(
                    business = business_obj,
                )
                
                user_serializer = UserAccountSerializer(user_obj)
                business_serializer = BusinessSerializer(business_obj)
                personal_contact_serializer = ContactNumberSerializer(personal_contact_obj)
                business_contact_serializer = ContactNumberSerializer(business_contact_obj)
                address_serializer = AddressSerializer(add_objs,many = True)
                resp_data = {
                    "user":user_serializer.data,
                    "business":business_serializer.data,
                    "personal_contact":personal_contact_serializer.data,
                    "business_contact":business_contact_serializer.data,
                    "address":address_serializer.data
                }
                return Response(
                    resp_data,
                    200
                )
            
        # except Exception as e:
        #     print(str(e))
        #     return Response(
        #         {
        #             "error":f"Failed to create the user because of \n {str(e)}"
        #         },
        #         400
        #     )
    
    
    def patch(self,request ,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        print(request.data)
        user_id = request.data.get("user_id")
        
        first_name = request.data.get("first_name")
        middle_name= request.data.get("middle_name")
        last_name = request.data.get("last_name")
        
        personal_phone_number = request.data.get("personal_phone_number")
        business_phone_number = request.data.get("business_phone_number")
        email = request.data.get("email")
        organization_name = request.data.get("organization_name")
        reseller_type = request.data.get("reseller_type")
        tax_number = request.data.get("tax_number")
        price_per_unit = request.data.get("price_per_unit")
        status = request.data.get("status")
        
        
        address1 = request.data.get("address1")
        address2 = request.data.get("address2")
        country = request.data.get("country")
        state = request.data.get("state")
        city = request.data.get("city")
        post_code = request.data.get("post_code")

        
        try:
            user_obj = UserAccount.objects.get(
                id = user_id,
                user_type = UserAccount.RESELLER
            )
        except UserAccount.DoesNotExist:
            return Response(
                {
                    "error":"User with given id does not exists"
                },
                400
            )
        

        business_obj  = user_obj.business
            
        if tax_number:
            business_obj.tax_number = tax_number
        if organization_name:
            business_obj.organization_name = organization_name
        business_obj.save()
        
        user_obj = UserAccount.objects.get(business = business_obj)
            

        if first_name :
            user_obj.first_name = first_name
        if middle_name:
            user_obj.middle_name = middle_name
        if last_name:
            user_obj.last_name = last_name
        if email:
            user_obj.email = email
            user_obj.username = email
            
        if status:
            user_obj.status = status
        if reseller_type:
            user_obj.reseller_type = reseller_type
        if price_per_unit:
            user_obj.price_per_unit = price_per_unit
        
        user_obj.save()
        
        if personal_phone_number:
            personal_contact_obj = ContactNumber.objects.filter(
                user = user_obj
            ).first()
            personal_contact_obj.country_code = personal_phone_number[
                "country_code"
            ].replace("+",'')
            personal_contact_obj.number = int(personal_phone_number["number"])
            personal_contact_obj.save()
            
        if business_phone_number:
            business_contact_obj = ContactNumber.objects.filter(
                business = business_obj
            ).first()
            business_contact_obj.country_code = business_phone_number[
                "country_code"
            ].replace("+",'')
            business_contact_obj.number = int(business_phone_number["number"])
            business_contact_obj.save()
          
        add_obj = Address.objects.filter(business = business_obj).first()
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
                "data":reseller_group_serializer_func(user_obj)
            },
            200
        )
        
    def delete(self, request,format = None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an Admin"
                },
                400
            )
        
        id = request.data.get("user_id")
        user_obj = UserAccount.objects.get(id = id)
        user_obj.is_deleted = True
        user_obj.save()
        business_obj = user_obj.business
        business_obj.is_deleted = True
        business_obj.save()
        business_contact_objs = ContactNumber.objects.filter(business = business_obj)
        personal_contact_objs = ContactNumber.objects.filter(user = user_obj)
        business_contact_objs.update(is_deleted = True)
        personal_contact_objs.update(is_deleted = True)
        add_objs = Address.objects.filter(business = business_obj)
        add_objs.update(is_deleted = True)
        
        return Response(
            {
                "success":"The Reseller has been deleted"
            },
            200
        )
        

    
class AdminListReseller(APIView):
    authentication_classes = (JwtAuthentication,)
    
    def get(self,request,format= None):
        user = request.user
        if user.user_type != UserAccount.ADMIN:
            return Response(
                {
                    "error":"User is not an admin"
                },
                400
            )
        
        users = UserAccount.objects.filter(
            user_type = UserAccount.RESELLER,
            is_archived = False,
            is_deleted = False
        ).order_by("-created_at")
        resp_data= []
        for u in users:
            resp_data.append(reseller_group_serializer_func(u))
            
        return Response(
            {
                "data":resp_data
            },
            200
        )
    
    