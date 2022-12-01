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
    allocated_block = models.ForeignKey(HdbBlock, on_delete=models.CASCADE)
    unit_number = models.CharField(max_length=200)
    def __str__(self):
        return self.unit_number

class ModuleStand(models.Model):
    allocated_home = models.ForeignKey(Household, on_delete=models.CASCADE)
    smoke_value = models.IntegerField()
    #rgb_cam_reading = models.IntegerField(max_length=6)
    #thermal_cam_reading = models.IntegerField(max_length=6)
    def __str__(self):
        return self.smoke_value