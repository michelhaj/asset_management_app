from django.contrib import admin

# Register your models here.
from .models import Computers,printers,monitors,docking_stations

admin.site.register(Computers)
admin.site.register(printers)
admin.site.register(monitors)
admin.site.register(docking_stations)