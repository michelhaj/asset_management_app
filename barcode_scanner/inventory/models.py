from django.db import models

class Computers(models.Model):
    id = models.CharField(primary_key=True, max_length=255,blank=True,null=False)
    asset_tag = models.CharField(max_length=255,blank=True,null=True, unique=True)
    service_tag=models.CharField(max_length=255,blank=True,null=True,unique=True)
    department=models.CharField(max_length=255,blank=True,null=True)
    computer_name=models.CharField(max_length=255,blank=True,null=True)
    user= models.CharField(max_length=255,blank=True,null=True)
    make = models.CharField(max_length=255,blank=True,null=True)
    model=models.CharField(max_length=255,blank=True,null=True)
    storage = models.CharField(max_length=255,blank=True,null=True)
    cpu = models.CharField(max_length=255,blank=True,null=True)
    ram = models.CharField(max_length=255,blank=True,null=True)
    # printer = models.BooleanField(max_length=3,blank=True,null=True) 
    # docking_station = models.BooleanField(max_length=3,blank=True,null=True)
    # monitor = models.BooleanField(max_length=3,blank=True,null=True)
    printers = models.ManyToManyField('printers', related_name='Computers', blank=True,null=True)

    def __str__(self):
        return f"{self.make} - {self.asset_tag} - {self.id}"
    class Meta:
        verbose_name = "Computer"
        verbose_name_plural = "Computers"
        
    
class printers(models.Model):
    id = models.CharField(primary_key=True, max_length=255,blank=True,null=False)
    service_tag =  models.CharField(max_length=255, unique=True)
    make = models.CharField(max_length=255,blank=True,null=True)
    description = models.CharField(max_length=255,blank=True,null=True)


    def __str__(self):
        return f"{self.service_tag} - {self.description} - {self.id}"
    class Meta:
        verbose_name = "Printer"
        verbose_name_plural = "Printers"
       
    
class docking_stations (models.Model):
    id = models.CharField(primary_key=True, max_length=255,blank=True,null=False)
    asset_tag = models.CharField(max_length=255,blank=True,null=True, unique=True)
    service_tag=models.CharField(max_length=255,blank=True,null=True)
    make = models.CharField(max_length=255,blank=True,null=True)
    computer = models.ForeignKey(Computers, on_delete=models.SET_NULL,blank=True,null=True, related_name='docking_stations')  

    def __str__(self):
        return f"{self.asset_tag} - {self.make} - {self.id}"
    class Meta:
        verbose_name = "Docking Station"
        verbose_name_plural = "Docking Stations"
        


class monitors(models.Model):
    id = models.CharField(primary_key=True, max_length=255,blank=True,null=False)
    asset_tag = models.CharField(max_length=255, blank=True,null=True,unique=True)
    service_tag=models.CharField(max_length=255,blank=True,null=True,unique=True)
    make = models.CharField(max_length=255,blank=True,null=True)
    computer = models.ForeignKey(Computers, on_delete=models.SET_NULL,blank=True,null=True, related_name='monitors')  

    def __str__(self):
        return f"{self.asset_tag} - {self.make} - {self.id}"
    class Meta:
        verbose_name = "Monitor"
        verbose_name_plural = "Monitors"
        