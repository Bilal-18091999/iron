
from django import forms
from .models import *
from django.forms import DateInput, DateTimeInput, TimeInput, CheckboxInput, Textarea, TextInput 
from django.db.models.functions import ExtractYear

class LoginForm(forms.Form):
    email=forms.CharField()
    password=forms.CharField()

from django import forms
from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'price_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price', 'step': '0.01'}),
            'price_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


class ProductFilterForm(forms.Form):
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by product name'
    }))
    price_min = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Min Price',
        'step': '0.01'
    }))
    price_max = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Max Price',
        'step': '0.01'
    }))
    price_type = forms.ChoiceField(required=False, choices=[('', 'All')] + list(Product.PRICE_TYPE), widget=forms.Select(attrs={
        'class': 'form-select'
    }))

from django import forms
from .models import Bill, BillItem, Store, Product

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['store']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-select store-select'}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Phone'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Discount amount'}),
            'tax': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Tax amount'}),
        }


class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['product', 'quantity', 'unit_type']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select product-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Quantity'}),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['unit_type'].choices = [('piece', 'Piece'), ('dozen', 'Dozen')]


class BillFilterForm(forms.Form):
    bill_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Bill Number'
    }))
    store = forms.ModelChoiceField(required=False, queryset=Store.objects.all(), widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    customer_name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Customer Name'
    }))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))

from django import forms
from .models import Payment, Store
from django.utils import timezone

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['store', 'amount', 'payment_type', 'date']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount', 'step': '0.01'}),
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class PaymentFilterForm(forms.Form):
    store = forms.ModelChoiceField(required=False, queryset=Store.objects.all(), widget=forms.Select(attrs={
        'class': 'form-select',
        'placeholder': 'Select Store'
    }))
    payment_type = forms.ChoiceField(required=False, choices=[('', 'All')] + list(Payment.PAYMENT_TYPE), widget=forms.Select(attrs={
        'class': 'form-select'
    }))
    amount_min = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Min Amount',
        'step': '0.01'
    }))
    amount_max = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Max Amount',
        'step': '0.01'
    }))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'class': 'form-control',
        'type': 'date'
    }))

class GenericModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GenericModelForm, self).__init__(*args, **kwargs)
        
        # Loop through each field in the form
        for field_name, field in self.fields.items():
            field_type = type(field)
            
            # Generic CSS class for all fields
            field.widget.attrs['class'] = 'form-control'

            # Custom widgets for specific field types
            if isinstance(field, forms.DateField):
                field.widget = DateInput(attrs={'class': 'form-control', 'type': 'date'})
            elif isinstance(field, forms.DateTimeField):
                field.widget = DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
            elif isinstance(field, forms.TimeField):
                field.widget = TimeInput(attrs={'class': 'form-control', 'type': 'time'})
            elif isinstance(field, forms.BooleanField):
                field.widget = CheckboxInput()
            elif isinstance(field, forms.CharField) and isinstance(field.widget, forms.Textarea):
                field.widget = Textarea(attrs={'class': 'form-control', 'rows': 3})
            elif isinstance(field, forms.CharField):
                field.widget = TextInput(attrs={'class': 'form-control'})


# class PCListForm(forms.ModelForm):
#     class Meta:
#         model = PCList
#         fields = '__all__'
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'in_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
#             'out_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
#             # Add other field widgets as needed
#         }

# class PatientForm(GenericModelForm):
#     class Meta:
#         model = Patient
#         fields = '__all__'


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'case_number', 'age', 'gender', 'diagnosis','chief_complaint', 'reference', 'contact', 'address']
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'rows': 2}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_case_number(self):
        """Validate that case number is unique"""
        case_number = self.cleaned_data.get('case_number')

        if case_number and not (case_number.startswith('UM') or case_number.startswith('PC')):
            raise forms.ValidationError("Case number must start with 'UM' or 'PC'.")
        
        # Check if this is an update (instance exists) or create (new instance)
        if self.instance.pk:
            # Update: exclude current instance from uniqueness check
            if Patient.objects.filter(case_number=case_number).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(f"Case number '{case_number}' already exists. Please use a different case number.")
        else:
            # Create: check if case number exists
            if Patient.objects.filter(case_number=case_number).exists():
                raise forms.ValidationError(f"Case number '{case_number}' already exists. Please use a different case number.")
        
        return case_number


class PatientFilterForm(forms.Form):
    """Form for filtering patient records"""
    case_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by case number'
        })
    )
    
    name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name'
        })
    )
    
    gender = forms.ChoiceField(
        choices=[('', 'All Genders'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    year = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate year choices based on existing records
        from django.db.models.functions import ExtractYear
        years = Patient.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('-year')
        year_choices = [('', 'All Years')] + [(str(year), str(year)) for year in years if year]
        self.fields['year'].choices = year_choices

class UploadFileForm(forms.Form):
    file = forms.FileField()



class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='Upload Excel File',
        help_text='Upload an Excel file (.xlsx, .xls)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )



class DailySheetForm(GenericModelForm):
    class Meta:
        model = DailySheet
        fields = '__all__'

class DailySheetFilterForm(forms.Form):
    case_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Case Number'
    }))
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Patient Name'
    }))
    year = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    payment_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + DailySheet._meta.get_field('payment_status').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate year choices based on existing records
        from django.db.models.functions import ExtractYear
        years = Patient.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('-year')
        year_choices = [('', 'All Years')] + [(str(year), str(year)) for year in years if year]
        self.fields['year'].choices = year_choices





class PCListForm(forms.ModelForm):
    class Meta:
        model = PCList
        fields = '__all__'
        


class PCListFilterForm(forms.Form):
    case_number = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Case Number'
    }))
   
    name = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Patient Name'
    }))
    year = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    payment_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All')] + PCList._meta.get_field('payment_status').choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control'
    }))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        years = PCList.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('-year')
        year_choices = [('', 'All Years')] + [(str(year), str(year)) for year in years if year]
        self.fields['year'].choices = year_choices


 
   