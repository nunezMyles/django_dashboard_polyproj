from django.db import models

# Create your models here.


class Raspberry(models.Model):
    mac_address = models.CharField(max_length=200, unique=True)  
    #smoke_sensor_id = models.IntegerField(unique=True) 
    #rgb_cam_id = models.IntegerField(unique=True) 
    #thermal_cam_id = models.IntegerField(unique=True) 
    def __str__(self):
        return f'{self.mac_address}'


class Flat_info(models.Model):
    flat_type = models.CharField(max_length=6)
    area = models.CharField(max_length=200)
    street_name = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.flat_type}, {self.area} {self.street_name}'


class Sensor_threshold(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    
    co = models.IntegerField()
    nh3 = models.IntegerField()
    ch2o = models.IntegerField()
    hcn = models.IntegerField()
    voc = models.IntegerField()

    def __str__(self):
        return f'{self.raspberry.mac_address}'


class Raspberry_location(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    hdb_block = models.CharField(max_length=200)  
    unit_number = models.CharField(max_length=200)  
    room_name = models.CharField(max_length=200)
    #flat_info = models.ForeignKey(Flat_info, on_delete=models.CASCADE)
    flat_type = models.CharField(max_length=6)
    area = models.CharField(max_length=200)
    street_name = models.CharField(max_length=200)
    #postal_code = models.IntegerField()

    def __str__(self):
        return f'{self.raspberry.mac_address}, {self.hdb_block}, {self.unit_number}'


class SmokeReading(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    smoke_value = models.IntegerField(blank=True, null=True) # nullable
    
    co = models.IntegerField()
    nh3 = models.IntegerField()
    ch2o = models.IntegerField()
    hcn = models.IntegerField()
    voc = models.IntegerField()

    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.raspberry.mac_address}, {self.captured_date}'


class ThermalCaptures(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    #image_path = models.CharField(max_length=255)
    image = models.BinaryField()
    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.raspberry.mac_address}, {self.captured_date}'


class RGBCaptures(models.Model):
    raspberry = models.ForeignKey(Raspberry, on_delete=models.CASCADE)
    #image_path = models.CharField(max_length=255)
    image = models.BinaryField()
    captured_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.raspberry.mac_address}, {self.captured_date}'


#rgb_cam_reading = models.IntegerField(max_length=6)
#thermal_cam_reading = models.IntegerField(max_length=6)