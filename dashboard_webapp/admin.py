from django.contrib import admin
from .models import Raspberry, Raspberry_location, SmokeReading, ThermalCaptures, RGBCaptures, Flat_info, Sensor_threshold

# Register your models here.
admin.site.register([Raspberry, Raspberry_location, SmokeReading, ThermalCaptures, RGBCaptures, Flat_info, Sensor_threshold])
