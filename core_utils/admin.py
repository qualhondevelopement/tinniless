from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Currency)
admin.site.register(CurrencyValueMapping)
admin.site.register(Settings)
admin.site.register(Feedback)
admin.site.register(MusicCategory)
admin.site.register(MusicFiles)