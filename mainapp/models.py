
from django.db import models
from user_management.models import User

class Store(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']

from django.core.validators import MinValueValidator  # Add this line
from decimal import Decimal  # Add this line
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    PRICE_TYPE = (
        ('piece', 'Per Piece'),
        ('dozen', 'Per Dozen'),
    )
    price_type = models.CharField(max_length=10, choices=PRICE_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field
    
    def __str__(self):
        return self.name
    

from django.utils import timezone
class Bill(models.Model):
    bill_number = models.CharField(max_length=50, unique=True, editable=False)
    date = models.DateField(default=timezone.now)   # ✅ ADD THIS LINE

    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='bills')
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.bill_number:
            # Generate bill number: BILL/YYYY/MM/XXXX
            from django.utils import timezone
            now = timezone.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            last_bill = Bill.objects.filter(created_at__year=now.year, created_at__month=now.month).order_by('-id').first()
            if last_bill:
                last_number = int(last_bill.bill_number.split('/')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            self.bill_number = f"BILL/{year}/{month}/{str(new_number).zfill(4)}"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        items = self.items.all()
        self.total_amount = sum(item.total_price for item in items)
        self.grand_total = self.total_amount - self.discount + self.tax
        self.save()
    
    def __str__(self):
        return f"{self.bill_number} - {self.store.name}"


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_type = models.CharField(max_length=10, choices=[('piece', 'Piece'), ('dozen', 'Dozen')])
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):

    # Only auto-set price if not manually provided
        if not self.price_per_unit:

            if self.product.price_type == 'dozen' and self.unit_type == 'piece':
                self.price_per_unit = self.product.price / Decimal('12')

            elif self.product.price_type == 'piece' and self.unit_type == 'dozen':
                self.price_per_unit = self.product.price * Decimal('12')

            else:
                self.price_per_unit = self.product.price

        # Always calculate total
        self.total_price = self.price_per_unit * self.quantity

        super().save(*args, **kwargs)

        # Update bill totals
        self.bill.calculate_totals()
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity} {self.unit_type}"


class Payment(models.Model):

    PAYMENT_TYPE = (
        ('cash', 'Cash'),
        ('Gpay', 'Gpay'),
      
    )

    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.store.name} - {self.amount}"

    class Meta:
        ordering = ['-date']




class Patient(models.Model):
	name = models.CharField(max_length=100, blank=True, null=True)
	case_number = models.CharField(max_length=20, unique=True)
	age = models.CharField(max_length=50, blank=True, null=True)
	gender = models.CharField(
		max_length=10,
		blank=True,
		null=True,
		choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
	)
	chief_complaint = models.TextField(blank=True, null=True)
	diagnosis = models.TextField(blank=True, null=True)
	reference = models.CharField(max_length=50, blank=True, null=True)
	contact = models.CharField(max_length=50, blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name or "Patient"

	class Meta:
		ordering = ['-created_at']


class DailySheet(models.Model):
	patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True, null=True)
	date = models.DateField(blank=True, null=True,default="timezone.now", )
	name = models.CharField(max_length=200,blank=True, null=True ,)
	case_number = models.CharField(max_length=20,blank=True, null=True ,unique=False ,)
	diagnosis = models.TextField(blank=True, null=True,)
	charge = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,)
	received = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,)
	payment_status = models.CharField(max_length=20,blank=True, null=True ,choices=[('paid', 'Paid'), ('partially_paid', 'Partially_paid'), ('not_paid', 'Not_paid')],)
	payment_type = models.CharField(max_length=10,blank=True, null=True ,choices=[('qr', 'Qr'), ('cash', 'Cash')],)
	payment_frequency = models.CharField(max_length=20,blank=True, null=True ,choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],)
	in_time = models.TimeField(blank=True, null=True,)
	out_time = models.TimeField(blank=True, null=True,)
	explain_treatment = models.TextField(blank=True, null=True)
	feedback = models.TextField(blank=True, null=True)
	
	treatment_1 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	treatment_2 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	treatment_3 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	treatment_4 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	therapist_1 = models.CharField(max_length=20,blank=True, null=True ,choices=[('Basidh', 'Basidh'), ('Visitra', 'Visitra'), ('Bharatiselvi', 'Bharatiselvi')],)
	therapist_2 = models.CharField(max_length=20,blank=True, null=True ,choices=[('Basidh', 'Basidh'), ('Visitra', 'Visitra'), ('Bharatiselvi', 'Bharatiselvi')],)
	created_at=models.DateTimeField(auto_now_add=True)
	updated_at=models.DateTimeField(auto_now=True)
	def __str__(self):
		return f'{self.date}'

class PCList(models.Model):
	patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE, blank=True, null=True)
	date = models.DateField(blank=True, null=True,default="timezone.now", )
	name = models.CharField(max_length=200,blank=True, null=True ,)
	case_number = models.CharField(max_length=20,blank=True, null=True ,unique=False ,)
	diagnosis = models.TextField(blank=True, null=True,)
	charge = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,)
	received = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True,)
	payment_status = models.CharField(max_length=20,blank=True, null=True ,choices=[('paid', 'Paid'), ('partially_paid', 'Partially_paid'), ('not_paid', 'Not_paid')],)
	payment_type = models.CharField(max_length=10,blank=True, null=True ,choices=[('qr', 'Qr'), ('cash', 'Cash')],)
	payment_frequency = models.CharField(max_length=20,blank=True, null=True ,choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],)
	in_time = models.TimeField(blank=True, null=True,)
	out_time = models.TimeField(blank=True, null=True,)
	explain_treatment = models.TextField(blank=True, null=True)
	feedback = models.TextField(blank=True, null=True)

	treatment_1 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	treatment_2 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	treatment_3 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	treatment_4 = models.CharField(max_length=30,blank=True, null=True ,choices=[('exercise', 'Exercise'), ('cycling', 'Cycling'), ('manual_therapy', 'Manual_therapy'), ('consultation', 'Consultation'), ('arm_ergometer', 'Arm_ergometer'), ('passive_stretching', 'Passive_stretching'), ('crepe_bandage', 'Crepe_bandage'),('tens', 'TENS'),('ultrasound', 'Ultrasound'),('electricl_stimulation', 'Electricl_stimulation')],)
	therapist_1 = models.CharField(max_length=20,blank=True, null=True ,choices=[('Basidh', 'Basidh'), ('Visitra', 'Visitra'), ('Bharatiselvi', 'Bharatiselvi'),('Suthish', 'Suthish')],)
	# therapist_2 = models.CharField(max_length=20,blank=True, null=True ,choices=[('Basidh', 'Basidh'), ('Visitra', 'Visitra'), ('Bharatiselvi', 'Bharatiselvi')],)
	created_at=models.DateTimeField(auto_now_add=True)
	updated_at=models.DateTimeField(auto_now=True)
	def __str__(self):
		return f'{self.date}'
	
