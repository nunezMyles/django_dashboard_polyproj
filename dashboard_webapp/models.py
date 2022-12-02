from django.db import models

# Create your models here.
"""
class Shelter(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    def __str__(self):
        return self.name
"""

class Household(models.Model):
    hdb_block = models.CharField(max_length=200)
    postal_code = models.IntegerField(unique=True)
    unit_number = models.CharField(max_length=200)
    area = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.hdb_block} {self.unit_number}, {self.area}'

class ModuleStand(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    raspberry_id = models.CharField(max_length=200, unique=True)
    room_name = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.raspberry_id}, {self.household.hdb_block} {self.household.unit_number}, {self.room_name}'

class SmokeReading(models.Model):
    module_stand = models.ForeignKey(ModuleStand, on_delete=models.CASCADE)
    smoke_value = models.IntegerField()
    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.smoke_value}, {self.module_stand.raspberry_id}'


#rgb_cam_reading = models.IntegerField(max_length=6)
#thermal_cam_reading = models.IntegerField(max_length=6)