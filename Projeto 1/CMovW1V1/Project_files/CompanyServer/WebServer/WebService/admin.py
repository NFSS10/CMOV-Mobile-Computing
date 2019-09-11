from django.contrib import admin
from WebService.models import User, Performance, Ticket, CafeteriaVoucher, CafeteriaOrder

admin.site.register(User)
admin.site.register(Performance)
admin.site.register(Ticket)
admin.site.register(CafeteriaVoucher)
admin.site.register(CafeteriaOrder)
