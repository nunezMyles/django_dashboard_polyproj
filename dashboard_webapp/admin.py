from django.contrib import admin
from .models import Shelter, HdbBlock, Household, ModuleStand

# Register your models here.
admin.site.register([Shelter, HdbBlock, Household, ModuleStand])