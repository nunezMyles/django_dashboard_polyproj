from django.contrib import admin
from .models import HdbBlock, Household, ModuleStand, SmokeReading

# Register your models here.
admin.site.register([HdbBlock, Household, ModuleStand, SmokeReading])