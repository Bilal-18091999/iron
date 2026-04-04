
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user_management.models import User
from django.shortcuts import get_object_or_404
from user_management.decorators import check_permission

def user_login(request):
    if request.method == 'POST':
        print('request.POST', request.POST)
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to a success page
            else:
                print('Invalid email or password')
                form.add_error(None, 'Invalid email or password')
        else:
            print('form', form.errors)
    else:
        form = LoginForm()

    context = {
        'form': form
    }
    return render(request, 'Auth/login.html', context)

from django.utils.timezone import now

def dashboard(request):
    records = Store.objects.all()
    today = now().date()
 
    product_count = Product.objects.count()


    return render(request, 'dashboard.html',{'dashboard':'active','store_count': records.count(), 'product_count': product_count})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('user_login')
    else:
        return redirect('user_login')


@login_required(login_url='/')
def store_list(request):
    records = Store.objects.all()

    context = {
        'records': records,
        'screen_name': 'Store',
        'total_count': records.count()
    }

    return render(request, 'store/store_list.html', context)

@login_required(login_url='/')
def store_create(request):
    if request.method == "POST":
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store_list')
    else:
        form = StoreForm()

    context = {
        'form': form,
        'screen_name': 'Store'
    }

    return render(request, 'store/create.html', context)

@login_required(login_url='/')
def store_update(request, pk):
    store = get_object_or_404(Store, pk=pk)

    if request.method == "POST":
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('store_list')
    else:
        form = StoreForm(instance=store)

    context = {
        'form': form,
        'screen_name': 'Store'
    }

    return render(request, 'store/create.html', context)

@login_required(login_url='/')
def store_delete(request, pk):
    store = get_object_or_404(Store, pk=pk)
    store.delete()
    return redirect('store_list')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from .forms import ProductForm, ProductFilterForm

# Add these decorators if you have them, otherwise remove @check_permission
# from your_app.decorators import check_permission

@login_required(login_url='/')
# @check_permission('product_view')  # Uncomment if you have this decorator
def product_list(request):
    """
    Displays a filtered list of Product records with optional filtering
    - Supports filtering by name, price range, and price type
    - Scrollable table (no pagination)
    """
    records = Product.objects.all().order_by('name')
    
    # Initialize filter form with GET parameters
    filter_form = ProductFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        name = filter_form.cleaned_data.get('name')
        if name:
            records = records.filter(name__icontains=name)
        
        price_min = filter_form.cleaned_data.get('price_min')
        if price_min:
            records = records.filter(price__gte=price_min)
        
        price_max = filter_form.cleaned_data.get('price_max')
        if price_max:
            records = records.filter(price__lte=price_max)
        
        price_type = filter_form.cleaned_data.get('price_type')
        if price_type:
            records = records.filter(price_type=price_type)
    
    context = {
        'records': records,
        'products': records,
        'filter_form': filter_form,
        'screen_name': 'Product',
        'total_count': records.count()
    }
    
    return render(request, 'product/product_list.html', context)


@login_required(login_url='/')
# @check_permission('product_create')
def product_create(request):
    """
    Handles creating a new Product record.
    """
    try:
        if request.method == "POST":
            form = ProductForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('product_list')
        else:
            form = ProductForm()
        
        context = {
            'form': form,
            'screen_name': 'Product'
        }
        return render(request, 'product/product_create.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})


@login_required(login_url='/')
# @check_permission('product_update')
def product_update(request, pk):
    """
    Handles updating an existing Product record.
    """
    try:
        product = get_object_or_404(Product, pk=pk)
        
        if request.method == "POST":
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                form.save()
                return redirect('product_list')
        else:
            form = ProductForm(instance=product)
        
        context = {
            'form': form,
            'screen_name': 'Product'
        }
        return render(request, 'product/product_create.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})


@login_required(login_url='/')
# @check_permission('product_delete')
def product_delete(request, pk):
    """
    Handles deletion of a Product record.
    """
    try:
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return redirect('product_list')
    except Exception as error:
        return render(request, '500.html', {'error': error})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.db.models import Q
import json
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
import os
from django.conf import settings

from .models import Bill, BillItem, Store, Product
from .forms import BillForm, BillItemForm, BillFilterForm

# Autocomplete views
@login_required(login_url='/')
def store_autocomplete(request):
    if 'term' in request.GET:
        stores = Store.objects.filter(name__icontains=request.GET.get('term'))[:10]
        results = [{'id': store.id, 'text': store.name, 'phone': store.phone or '', 'address': store.address or ''} for store in stores]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

@login_required(login_url='/')
def product_autocomplete(request):
    if 'term' in request.GET:
        products = Product.objects.filter(name__icontains=request.GET.get('term'))[:10]
        results = [{
            'id': product.id, 
            'text': f"{product.name} - {product.get_price_type_display()} (₹{product.price})",
            'price': str(product.price),
            'price_type': product.price_type
        } for product in products]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

# Bill CRUD views
@login_required(login_url='/')
def bill_list(request):
    records = Bill.objects.all().order_by('-created_at')
    
    filter_form = BillFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        bill_number = filter_form.cleaned_data.get('bill_number')
        if bill_number:
            records = records.filter(bill_number__icontains=bill_number)
        
        store = filter_form.cleaned_data.get('store')
        if store:
            records = records.filter(store=store)
        
        customer_name = filter_form.cleaned_data.get('customer_name')
        if customer_name:
            records = records.filter(customer_name__icontains=customer_name)
        
        date_from = filter_form.cleaned_data.get('date_from')
        if date_from:
            records = records.filter(created_at__date__gte=date_from)
        
        date_to = filter_form.cleaned_data.get('date_to')
        if date_to:
            records = records.filter(created_at__date__lte=date_to)
    
    context = {
        'records': records,
        'filter_form': filter_form,
        'total_count': records.count()
    }
    return render(request, 'bill/bill_list.html', context)

@login_required(login_url='/')
def bill_create(request):
    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save()
            return redirect('bill_edit', pk=bill.pk)  # This line is correct
    else:
        form = BillForm()
    
    context = {
        'form': form,
        'screen_name': 'Bill'
    }
    return render(request, 'bill/bill_create.html', context)

@login_required(login_url='/')
def bill_edit(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    
    if request.method == 'POST':
        if 'update_bill' in request.POST:
            form = BillForm(request.POST, instance=bill)
            if form.is_valid():
                form.save()
                return redirect('bill_list')
        elif 'add_item' in request.POST:
            item_form = BillItemForm(request.POST)
            if item_form.is_valid():
                item = item_form.save(commit=False)
                item.bill = bill
                item.save()
                return redirect('bill_edit', pk=bill.pk)
    else:
        form = BillForm(instance=bill)
    
    item_form = BillItemForm()
    items = bill.items.all()
    
    context = {
        'form': form,
        'item_form': item_form,
        'items': items,
        'bill': bill,
        'screen_name': 'Bill'
    }
    return render(request, 'bill/bill_edit.html', context)

@login_required(login_url='/')
def bill_delete(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    bill.delete()
    return redirect('bill_list')

@login_required(login_url='/')
def bill_view(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    items = bill.items.select_related('product').all()
    
    context = {
        'bill': bill,
        'items': items,
    }
    return render(request, 'bill/bill_view.html', context)

@login_required(login_url='/')
def bill_delete_item(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(BillItem, pk=pk)
        bill_pk = item.bill.pk
        item.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required(login_url='/')
def download_bill_as_image(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    items = bill.items.select_related('product').all()
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Center
        spaceAfter=30
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
    )
    
    # Story elements
    story = []
    
    # Header
    story.append(Paragraph("UNIQUE PHYSIO CARE", title_style))
    story.append(Paragraph("123 Healthcare Street, Medical District", header_style))
    story.append(Paragraph("Phone: +91 98765 43210 | Email: info@uniquephysio.com", header_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Bill details
    bill_info = [
        [Paragraph(f"<b>Bill Number:</b> {bill.bill_number}", styles['Normal']),
         Paragraph(f"<b>Date:</b> {bill.created_at.strftime('%d/%m/%Y %H:%M')}", styles['Normal'])],
        [Paragraph(f"<b>Store:</b> {bill.store.name}", styles['Normal']),
         Paragraph(f"<b>Phone:</b> {bill.store.phone or '-'}", styles['Normal'])],
        [Paragraph(f"<b>Customer:</b> {bill.customer_name or 'Walk-in Customer'}", styles['Normal']),
         Paragraph(f"<b>Phone:</b> {bill.customer_phone or '-'}", styles['Normal'])],
    ]
    
    for row in bill_info:
        t = Table([row], colWidths=[3*inch, 3*inch])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
    
    story.append(Spacer(1, 0.2*inch))
    
    # Items table
    table_data = [['S.No', 'Product', 'Quantity', 'Unit Price (₹)', 'Total (₹)']]
    for idx, item in enumerate(items, 1):
        table_data.append([
            str(idx),
            item.product.name,
            f"{item.quantity} {item.get_unit_type_display()}",
            f"₹{item.price_per_unit:,.2f}",
            f"₹{item.total_price:,.2f}"
        ])
    
    # Add totals
    table_data.append(['', '', '', 'Subtotal:', f"₹{bill.total_amount:,.2f}"])
    if bill.discount > 0:
        table_data.append(['', '', '', 'Discount:', f"-₹{bill.discount:,.2f}"])
    if bill.tax > 0:
        table_data.append(['', '', '', 'Tax:', f"₹{bill.tax:,.2f}"])
    table_data.append(['', '', '', 'Grand Total:', f"<b>₹{bill.grand_total:,.2f}</b>"])
    
    item_table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -5), colors.beige),
        ('GRID', (0, 0), (-1, -5), 1, colors.black),
        ('FONTNAME', (4, -4), (4, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -4), (-1, -1), colors.HexColor('#ecf0f1')),
        ('ALIGN', (3, -4), (4, -1), 'RIGHT'),
        ('SPAN', (0, -4), (2, -4)),
        ('SPAN', (0, -3), (2, -3)),
        ('SPAN', (0, -2), (2, -2)),
        ('SPAN', (0, -1), (2, -1)),
    ]))
    
    story.append(item_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph("Thank you for choosing Unique Physio Care!", footer_style))
    story.append(Paragraph("This is a computer generated bill.", footer_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    # Return as PDF (can be converted to image later)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill.bill_number}.pdf"'
    return response

@csrf_exempt
def calculate_item_price(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = Decimal(data.get('quantity', 0))
        unit_type = data.get('unit_type')
        
        product = get_object_or_404(Product, pk=product_id)
        
        if product.price_type == 'dozen' and unit_type == 'piece':
            price_per_unit = product.price / Decimal('12')
            total_price = price_per_unit * quantity
        elif product.price_type == 'piece' and unit_type == 'dozen':
            price_per_unit = product.price * Decimal('12')
            total_price = price_per_unit * quantity
        else:
            price_per_unit = product.price
            total_price = price_per_unit * quantity
        
        return JsonResponse({
            'success': True,
            'price_per_unit': float(price_per_unit),
            'total_price': float(total_price)
        })
    
    return JsonResponse({'success': False})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from .models import Payment, Store
from .forms import PaymentForm, PaymentFilterForm
from decimal import Decimal

@login_required(login_url='/')
def payment_list(request):
    """
    Displays a filtered list of Payment records
    """
    records = Payment.objects.all().order_by('-date', '-created_at')
    
    # Calculate summary
    total_amount = records.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    cash_total = records.filter(payment_type='cash').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    gpay_total = records.filter(payment_type='Gpay').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    # Initialize filter form with GET parameters
    filter_form = PaymentFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        store = filter_form.cleaned_data.get('store')
        if store:
            records = records.filter(store=store)
        
        payment_type = filter_form.cleaned_data.get('payment_type')
        if payment_type:
            records = records.filter(payment_type=payment_type)
        
        amount_min = filter_form.cleaned_data.get('amount_min')
        if amount_min:
            records = records.filter(amount__gte=amount_min)
        
        amount_max = filter_form.cleaned_data.get('amount_max')
        if amount_max:
            records = records.filter(amount__lte=amount_max)
        
        date_from = filter_form.cleaned_data.get('date_from')
        if date_from:
            records = records.filter(date__gte=date_from)
        
        date_to = filter_form.cleaned_data.get('date_to')
        if date_to:
            records = records.filter(date__lte=date_to)
        
        # Recalculate totals after filtering
        total_amount = records.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        cash_total = records.filter(payment_type='cash').aggregate(total=Sum('amount'))['total'] or Decimal('0')
        gpay_total = records.filter(payment_type='Gpay').aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    context = {
        'records': records,
        'filter_form': filter_form,
        'total_count': records.count(),
        'total_amount': total_amount,
        'cash_total': cash_total,
        'gpay_total': gpay_total,
    }
    return render(request, 'payment/payment_list.html', context)


@login_required(login_url='/')
def payment_create(request):
    """
    Handles creating a new Payment record.
    """
    try:
        if request.method == "POST":
            form = PaymentForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('payment_list')
        else:
            form = PaymentForm()
        
        context = {
            'form': form,
            'screen_name': 'Payment'
        }
        return render(request, 'payment/payment_create.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})


@login_required(login_url='/')
def payment_update(request, pk):
    """
    Handles updating an existing Payment record.
    """
    try:
        payment = get_object_or_404(Payment, pk=pk)
        
        if request.method == "POST":
            form = PaymentForm(request.POST, instance=payment)
            if form.is_valid():
                form.save()
                return redirect('payment_list')
        else:
            form = PaymentForm(instance=payment)
        
        context = {
            'form': form,
            'screen_name': 'Payment'
        }
        return render(request, 'payment/payment_create.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})


@login_required(login_url='/')
def payment_delete(request, pk):
    """
    Handles deletion of a Payment record.
    """
    try:
        payment = get_object_or_404(Payment, pk=pk)
        payment.delete()
        return redirect('payment_list')
    except Exception as error:
        return render(request, '500.html', {'error': error})



from django.db.models import Sum, Q
from decimal import Decimal
from datetime import datetime

@login_required(login_url='/')
def store_ledger_select(request):
    """
    Page to select store for viewing ledger
    """
    stores = Store.objects.all().order_by('name')
    return render(request, 'ledger/store_ledger_select.html', {'stores': stores})

@login_required(login_url='/')
def store_ledger_view(request, store_id):
    """
    Display ledger for selected store with bill and payment transactions
    Bill and payment on same date appear in the same row
    """
    store = get_object_or_404(Store, pk=store_id)
    
    # Get all bills for this store
    bills = Bill.objects.filter(store=store).order_by('date', 'created_at')
    
    # Get all payments for this store
    payments = Payment.objects.filter(store=store).order_by('date', 'created_at')
    
    # Create a dictionary to combine transactions by date
    transactions_by_date = {}
    
    # Add bills
    for bill in bills:
        date_key = bill.date
        if date_key not in transactions_by_date:
            transactions_by_date[date_key] = {
                'date': bill.date,
                'bill_amount': Decimal('0'),
                'payment_amount': Decimal('0'),
                'payment_type': None,
                'transactions': []
            }
        transactions_by_date[date_key]['bill_amount'] += bill.grand_total
        transactions_by_date[date_key]['transactions'].append({
            'type': 'bill',
            'amount': bill.grand_total,
            'obj': bill
        })
    
    # Add payments
    for payment in payments:
        date_key = payment.date
        if date_key not in transactions_by_date:
            transactions_by_date[date_key] = {
                'date': payment.date,
                'bill_amount': Decimal('0'),
                'payment_amount': Decimal('0'),
                'payment_type': None,
                'transactions': []
            }
        transactions_by_date[date_key]['payment_amount'] += payment.amount
        transactions_by_date[date_key]['payment_type'] = payment.payment_type
        transactions_by_date[date_key]['transactions'].append({
            'type': 'payment',
            'amount': payment.amount,
            'payment_type': payment.payment_type,
            'obj': payment
        })
    
    # Sort dates
    sorted_dates = sorted(transactions_by_date.keys())
    
    # Calculate running balance
    balance = Decimal('0')
    ledger_data = []
    
    for date in sorted_dates:
        transaction = transactions_by_date[date]
        
        # Update balance: add bill amount, subtract payment amount
        balance += transaction['bill_amount']
        balance -= transaction['payment_amount']
        
        # For payment type, if there are multiple payments on same day, show first one or 'Multiple'
        payment_type_display = transaction['payment_type']
        if payment_type_display and len([t for t in transaction['transactions'] if t['type'] == 'payment']) > 1:
            payment_type_display = 'Multiple'
        
        ledger_data.append({
            'date': transaction['date'],
            'bill_amount': transaction['bill_amount'] if transaction['bill_amount'] > 0 else '',
            'payment_amount': transaction['payment_amount'] if transaction['payment_amount'] > 0 else '',
            'payment_type': payment_type_display if transaction['payment_amount'] > 0 else '',
            'balance': balance,
        })
    
    context = {
        'store': store,
        'ledger_data': ledger_data,
    }
    return render(request, 'ledger/store_ledger_view.html', context)



@login_required(login_url='/')
@check_permission('patient_create')
def patient_create(request):
    try:
        if request.method == "POST":
            form = PatientForm(request.POST)
            if form.is_valid():
                # Additional case number validation
                case_number = form.cleaned_data.get('case_number')
                if case_number and not (case_number.startswith('UM') or case_number.startswith('PC')):
                    form.add_error('case_number', "Case number must start with 'UM' or 'PC'.")
                else:
                    form.save()
                    return redirect('patient_list')
            # If form is invalid (including duplicate case number), it will show errors
        else:
            form = PatientForm()
        
        context = {
            'form': form,
            'screen_name': 'Patient'
        }
        return render(request, 'create.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
@login_required(login_url='/')
@check_permission('patient_view')
def patient_list(request):
    """
    Displays a filtered list of Patient records with optional filtering
    - Supports filtering by case number, name, gender, year, and date range
    - Scrollable table (no pagination)
    """
    records = Patient.objects.all()
    
    # Initialize filter form with GET parameters
    filter_form = PatientFilterForm(request.GET or None)
    
    if filter_form.is_valid():
        case_number = filter_form.cleaned_data.get('case_number')
        if case_number:
            records = records.filter(case_number__icontains=case_number)
        
        name = filter_form.cleaned_data.get('name')
        if name:
            records = records.filter(name__icontains=name)
        
        gender = filter_form.cleaned_data.get('gender')
        if gender:
            records = records.filter(gender=gender)
        
        year = filter_form.cleaned_data.get('year')
        if year:
            records = records.filter(created_at__year=year)
        
        date_from = filter_form.cleaned_data.get('date_from')
        date_to = filter_form.cleaned_data.get('date_to')
        if date_from:
            records = records.filter(created_at__date__gte=date_from)
        if date_to:
            records = records.filter(created_at__date__lte=date_to)
    
    context = {
        'records': records,       # Full queryset
        'patients': records,      # Alias if needed
        'filter_form': filter_form,
        'screen_name': 'Patient',
        'total_count': records.count()
    }
    
    return render(request, 'patient_list.html', context)

    
@login_required(login_url='/')
@check_permission('patient_update')
def patient_update(request, pk):
    """
    Handles updating an existing Patient record.
    - Validates case number uniqueness (excluding current record)
    """
    try:
        patient = get_object_or_404(Patient, pk=pk)
        
        if request.method == "POST":
            form = PatientForm(request.POST, instance=patient)
            if form.is_valid():
                form.save()
                return redirect('patient_list')
        else:
            form = PatientForm(instance=patient)
        
        context = {
            'form': form,
            'screen_name': 'Patient'
        }
        return render(request, 'create.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})


@login_required(login_url='/')
@check_permission('patient_delete')
def patient_delete(request, pk):
    """
    Handles deletion of a Patient record.
    """
    try:
        patient = get_object_or_404(Patient, pk=pk)
        patient.delete()
        return redirect('patient_list')
    except Exception as error:
        return render(request, '500.html', {'error': error})

