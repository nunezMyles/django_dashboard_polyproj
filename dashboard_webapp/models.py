from django.db import models

# Create your models here.
"""
class Shelter(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    def __str__(self):
        return self.name
"""


class Raspberry(models.Model):
    serial_id = models.CharField(max_length=200, unique=True)
    smoke_sensor_id = models.IntegerField(unique=True) 
    rgb_cam_id = models.IntegerField(unique=True) 
    thermal_cam_id = models.IntegerField(unique=True) 
    def __str__(self):
        return f'{self.serial_id}'


class Raspberry_location(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    hdb_block = models.CharField(max_length=200)  
    unit_number = models.CharField(max_length=200)
    room_name = models.CharField(max_length=200)
    area = models.CharField(max_length=200)
    postal_code = models.IntegerField()
    def __str__(self):
        return f'{self.raspberry.serial_id}, {self.hdb_block} {self.unit_number}'


class SmokeReading(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    smoke_value = models.IntegerField()
    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.raspberry.serial_id}, {self.smoke_value}'


class ThermalCaptures(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    image_link = models.CharField(max_length=200)
    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.raspberry.serial_id}, {self.image_link}'


class RGBCaptures(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    image_link = models.CharField(max_length=200)
    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.raspberry.serial_id}, {self.image_link}'


#rgb_cam_reading = models.IntegerField(max_length=6)
#thermal_cam_reading = models.IntegerField(max_length=6)