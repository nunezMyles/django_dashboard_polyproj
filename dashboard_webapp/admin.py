from django.contrib import admin
from .models import Raspberry, Raspberry_location, SmokeReading, ThermalCaptures, RGBCaptures

# Register your models here.
admin.site.register([Raspberry, Raspberry_location, SmokeReading, ThermalCaptures, RGBCaptures])