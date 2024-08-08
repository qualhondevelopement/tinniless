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

