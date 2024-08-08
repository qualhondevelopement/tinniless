# from users.models import UserAccount
# from .models import Currency, CurrencyValueMapping
# def populate_currency_mapping():
#     if not Currency.objects.filter(currency_name = "EURO").exists():
#         cur_obj = Currency.objects.create(
#             currency_name = "EURO",
#             currency_symbol = "€",
#             euro_equivalent = 1.0
#         )
#     else:
#         cur_obj = Currency.objects.get(currency_name = "EURO")
#     us = UserAccount.objects.filter(user_type__in = [UserAccount.PATIENT, UserAccount.RETAILER, UserAccount.RESELLER])
#     for u in us:
#         map = CurrencyValueMapping.objects.create(
#             currency= cur_obj,
#             value = u.price_per_unit,
#             euro_equivalent_value = u.price_per_unit
#         )
#         u.price_mapping = map   
#         u.save()