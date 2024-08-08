from django.db import models

# Create your models here.

class Currency(models.Model):
    currency_name = models.CharField(max_length=50)
    currency_symbol = models.CharField(max_length=50)
    euro_equivalent = models.FloatField(default=1)


class CurrencyValueMapping(models.Model):
    currency = models.ForeignKey(Currency,on_delete=models.CASCADE)
    value = models.FloatField(default = 0)
    euro_equivalent_value = models.FloatField(default = 0)

    def save(self,*args,**kwargs):
        if not self.value:
            self.value = 0
        equivalent_value = self.value * self.currency.euro_equivalent
        self.euro_equivalent_value = equivalent_value
        super().save(*args, **kwargs)


class Settings(models.Model):
    notch_percentage = models.FloatField(null=True, blank= True)
    notch_db = models.BigIntegerField(null=True, blank= True)
    session_done_percentage = models.FloatField(null=True, blank= True)
    sound_therapy = models.IntegerField(null=True, blank= True)
    pause_duration = models.FloatField(null=True, blank= True)
    too_hot_pause = models.FloatField(null=True, blank= True)
    rf_session_day = models.IntegerField(null=True, blank= True)
    rf_session_length = models.IntegerField(null=True, blank= True)
    pause_limit = models.IntegerField(null=True, blank= True)
    power_changing_time = models.IntegerField(null=True, blank= True)
    hear_tinnitus = models.IntegerField(null=True, blank= True)
    frequency_test_diffrence = models.IntegerField(null=True, blank= True)
    beep_time = models.FloatField(null=True, blank= True)
    reseller_product_price = models.FloatField(null=True, blank= True)
    patient_product_price = models.FloatField(null=True, blank= True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class Feedback(models.Model):
    BEFORE_SESSION = "BEFORE_SESSION"
    AFTER_SESSION = "AFTER_SESSION"
    ASKED_QUESTION_CHOICES = [
        (BEFORE_SESSION,"BEFORE_SESSION"),
        (AFTER_SESSION,"AFTER_SESSION"),
    ]

    QUESTION = "QUESTION"
    FEEDBACK = "FEEDBACK"
    QUESTION_TYPE_CHOICES = [
        (QUESTION,"QUESTION"),
        (FEEDBACK,"FEEDBACK"),
    ]
    question = models.CharField(max_length=255)
    asked_question = models.CharField(max_length= 30, choices= ASKED_QUESTION_CHOICES)
    question_type = models.CharField(max_length= 30, choices= QUESTION_TYPE_CHOICES)
    question_reoccurrence_time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class MusicCategory(models.Model):
    image = models.FileField(upload_to='category_images', blank = True, null = True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class MusicFiles(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='music_files', blank = True, null = True)
    category = models.ForeignKey(MusicCategory, null=True, blank = True,related_name="music_category",on_delete=models.CASCADE)
    music_length = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)