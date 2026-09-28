from django.db import models
from vending.models import sku,Machine
from django.contrib.postgres.fields import JSONField

# Create your models here.
class AuthToken(models.Model):
    kiosk = models.ForeignKey(Machine,on_delete=models.CASCADE,related_name='machineid',null=True)
    auth_token = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expire_at = models.DateTimeField(auto_now=False)
    is_active = models.SmallIntegerField(choices=((1,'Active'),(2,'Inactive')),null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

class EmptyCollect(models.Model):
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='empty', null=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    tracking_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    response_at = models.DateTimeField(null=True, blank=True)
    slot_id = models.CharField(max_length=100, null=True, blank=True)
    chamber_id = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return self.kiosk
    
class CylinderValidate(models.Model):
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='validate_empty', null=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    sku = models.CharField(max_length=100, null=True, blank=True)
    variant = models.CharField(max_length=100, null=True, blank=True)
    validate_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    response_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.kiosk

class ReturnEmpty(models.Model):
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='returnempty', null=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    response_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.kiosk    
    
class DispenseFilled(models.Model):
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='dispensecylinder', null=True)
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    tracking_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    response_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.kiosk        

class StockInventory(models.Model):
    kiosk = models.ForeignKey(Machine,on_delete=models.CASCADE, related_name='stock_inventories',null=True)
    sku = models.ForeignKey(sku, on_delete=models.CASCADE, related_name='stock_sku')
    empty_stock = models.IntegerField(default=0)
    filled_stock = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=False)

    def __str__(self):
        return f'{self.sku}'  

class ChamberStockInventory(models.Model):
    stock_inventory = models.ForeignKey(StockInventory ,on_delete=models.CASCADE, related_name='chamberinventory', null=True)
    chamber = models.CharField(max_length=50, null=True, blank=True)  
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=False)
    created_ip = models.GenericIPAddressField(null=True)

    def __str__(self):
        return f"Chamber {self.chamber} for Inventory {self.stock_inventory}"


class ChamberSlots(models.Model): 
    chamber = models.ForeignKey(ChamberStockInventory,on_delete=models.CASCADE, related_name='chamberslots', null=True)
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='chamber', null=True)
    sku = models.ForeignKey(sku, on_delete=models.CASCADE, related_name='slot_sku', null=True, blank=True)
    slot_number = models.IntegerField()
    status = models.SmallIntegerField(choices=((0,'Empty'),(1 ,'Filled'),(3,'SlotEmpty'))) 
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class BDA_Transactions(models.Model):
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='bdatransaction', null=True)
    txn_type = models.SmallIntegerField(db_comment='1 - Validation, 2 -Receive Filled, 3 - Return Empty,4 - Return Filled')
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    sku = models.ForeignKey(sku, on_delete=models.CASCADE,related_name='bda_sku', null=True)
    total_count = models.CharField(max_length=100, null=True, blank=True)
    validate_data = models.JSONField(null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    status = models.SmallIntegerField(null=True, db_comment='0 - Failed, 1 - Success')
    response_at = models.DateTimeField(null=True,blank=True) 
    txn_complete = models.SmallIntegerField(null=True, db_comment=',0- Processing , 1 - Finish')
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    slot  = models.ForeignKey(ChamberSlots, on_delete=models.CASCADE,related_name='bdaslot', null=True)

class Customer_Transactions(models.Model):
    kiosk = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='customertransaction', null=True)
    txn_type = models.SmallIntegerField(db_comment='1 - Empty Collect , 2 - Return Empty, 3 - Receive Filled')
    reference_id = models.CharField(max_length=100, null=True, blank=True)
    sku = models.ForeignKey(sku, on_delete=models.CASCADE,related_name='customer_sku', null=True)
    validate_data = models.JSONField(null=True, blank=True)  
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    response_at = models.DateTimeField(null=True,blank=True) 
    slot  = models.ForeignKey(ChamberSlots, on_delete=models.CASCADE,related_name='customerslot', null=True)
    status = models.SmallIntegerField(null=True, db_comment='0 - Failed, 1 - Success')
    txn_complete = models.SmallIntegerField(null=True, db_comment=',0- Processing , 1 - Finish')
    ref_id = models.CharField(max_length=100, null=True, blank=True)
    slot  = models.ForeignKey(ChamberSlots, on_delete=models.CASCADE,related_name='customerslot', null=True)

