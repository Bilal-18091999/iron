from django.contrib import admin
from .models import *

# @admin.register(PCList)
# class PCListAdmin(admin.ModelAdmin):
#     list_display = ['date', 'title', 'name', 'case_number', 'diagnosis', 'treatment_1', 'treatment_2', 'treatment_3', 'charge', 'received', 'payment_status', 'payment_type', 'payment_frequency', 'therapist']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'case_number', 'age', 'gender', 'chief_complaint', 'reference', 'contact', 'address']

@admin.register(DailySheet)
class DailySheetAdmin(admin.ModelAdmin):
    list_display = ['date', 'name', 'case_number', 'diagnosis', 'charge', 'received', 'payment_status', 'payment_type', 'payment_frequency', 'in_time', 'out_time', 'treatment_1', 'treatment_2', 'treatment_3', 'treatment_4', 'therapist_1', 'therapist_2']

@admin.register(PCList)
class PCListAdmin(admin.ModelAdmin):
    list_display = ('date', 'case_number', 'charge', 'received', 'therapist_1')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from user_management.models import User, Role


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'phone_number', 'roles', 'is_active')
    list_filter = ('is_active', 'roles')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'phone_number')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'roles')}),
        ('Dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2'),
        }),
    )
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at')
