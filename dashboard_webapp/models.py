from django.db import models

# Create your models here.
class Shelter(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class HdbBlock(models.Model):
    block = models.CharField(max_length=200)
    postal_code = models.IntegerField()
    def __str__(self):
        return self.block

class Household(models.Model):
    block = models.ForeignKey(HdbBlock, on_delete=models.CASCADE)
    unit_number = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.unit_number}, {self.block}'

class ModuleStand(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE)
    stand_name = models.CharField(max_length=200)
    smoke_value = models.IntegerField()
    captured_date = models.DateTimeField(auto_now_add=True)
    #rgb_cam_reading = models.IntegerField(max_length=6)
    #thermal_cam_reading = models.IntegerField(max_length=6)
    def __str__(self):
        return f'{self.stand_name}, {self.household.unit_number}, {self.household.block}'