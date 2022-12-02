from django.contrib import admin
from .models import Household, ModuleStand, SmokeReading

# Register your models here.
admin.site.register([Household, ModuleStand, SmokeReading])