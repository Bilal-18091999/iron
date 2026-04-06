from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.user_login, name='user_login'),

    path('store/', views.store_list, name='store_list'),
    path('store/new/', views.store_create, name='store_create'),
    path('store/<int:pk>/edit/', views.store_update, name='store_update'),
    path('store/<int:pk>/delete/', views.store_delete, name='store_delete'),

    path('product/', views.product_list, name='product_list'),
    path('product/new/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),


    path('bill/', views.bill_list, name='bill_list'),
    path('bill/new/', views.bill_create, name='bill_create'),
    path('bill/<int:pk>/edit/', views.bill_edit, name='bill_edit'),
    path('bill/<int:pk>/delete/', views.bill_delete, name='bill_delete'),
    path('bill/<int:pk>/view/', views.bill_view, name='bill_view'),
    path('bill/download/<int:pk>/', views.download_bill_as_image, name='download_bill'),
    path('bill/item/<int:pk>/delete/', views.bill_delete_item, name='bill_delete_item'),
    path('bill/item/<int:pk>/update/', views.bill_update_item, name='bill_update_item'),

    # Autocomplete URLs
    path('store-autocomplete/', views.store_autocomplete, name='store_autocomplete'),
    path('product-autocomplete/', views.product_autocomplete, name='product_autocomplete'),
    path('calculate-item-price/', views.calculate_item_price, name='calculate_item_price'),



    # Payment URLs
    path('payment/', views.payment_list, name='payment_list'),
    path('payment/new/', views.payment_create, name='payment_create'),
    path('payment/<int:pk>/edit/', views.payment_update, name='payment_update'),
    path('payment/<int:pk>/delete/', views.payment_delete, name='payment_delete'),



    # Store Ledger URLs
    path('store-ledger/', views.store_ledger_select, name='store_ledger_select'),
    path('store-ledger/<int:store_id>/', views.store_ledger_view, name='store_ledger_view'),


        
    path('patient/', views.patient_list, name='patient_list'),
    path('patient/new/', views.patient_create, name='patient_create'),
    path('patient/<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('patient/<int:pk>/delete/', views.patient_delete, name='patient_delete'),
  


    

]