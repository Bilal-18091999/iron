from django.shortcuts import render, redirect,get_object_or_404
from .forms import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
# from bb_id_gen_app.scripts import simple_unique_id_generation
import json

import uuid

def simple_unique_id_generation():
    return str(uuid.uuid4())

def dashboard(request):
    return render(request, 'dashboard.html')

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.password = make_password(form.cleaned_data.get('password'))
            obj.save()
            return redirect('user_list')  # Redirect to a success page after registration
    else:
        form = UserRegistrationForm()

    context = {
        'form': form, 'user_registration': 'active', 'user_registration_show': 'show',
    }
    return render(request, 'UserManagement/user_registration.html', context)


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
                print('Invalid username or password')
                form.add_error(None, 'Invalid username or password')
        else:
            print('form', form.errors)
    else:
        form = LoginForm()

    context = {
        'form': form
    }
    return render(request, 'Auth/login.html', context)

def user_list(request):
    records = User.objects.filter(is_active=True)
    context = {
        'user_list': 'active', 'user_list_show': 'show', 'records': records
    }
    return render(request, 'UserManagement/user_list.html', context)

def user_edit(request,pk):
    try:
        record=User.objects.get(pk=pk)
        if request.method == 'POST':
            form = UserRegistrationForm(request.POST,instance=record)
            if form.is_valid():
                obj=form.save()
                return redirect('user_list') 
        else:
            form = UserRegistrationForm(instance=record)

        context = {
            'form': form, 'user_edit': 'active', 'user_edit_show': 'show',
        }
        # return render(request,'UserManagement/create.html',context)

        return render(request, 'UserManagement/user_registration.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})

def user_view(request,pk):
    try:
        record=User.objects.get(pk=pk)
        form = UserRegistrationForm(instance=record)

        context = {
            'user_list': 'active', 'user_list_show': 'show', 'form': form,'screen_name':'User'
        }
        return render(request, 'UserManagement/user_view.html', context)
    except Exception as error:
        return render(request, '500.html', {'error': error})
    
def user_delete(request,pk):
    try:
        obj=User.objects.get(pk=pk)
        obj.is_active=False
        obj.save()
        return redirect('user_list')          
        #records = User.objects.all()
    except Exception as error:
        return render(request, '500.html', {'error': error})

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('user_login')
    else:
        return redirect('user_login')

def roles(request):
    try:
        records=Role.objects.all()
        context={
            'records':records,'roles': 'active', 'roles_show': 'show'
        }
        return render(request,'UserManagement/roles.html',context)
    except Exception as error:
        return render(request, '500.html', {'error': error})

def roles_create(request):
    try:
        form = RoleForm()
        if request.method=='POST':
            form = RoleForm(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.created_by = request.user
                obj.updated_by = request.user
                obj.save()
                return redirect('roles')
        context={
            'roles': 'active', 'roles_show': 'show','form':form,'screen_name':"Roles"
        }
        return render(request,'UserManagement/create.html',context)
    except Exception as error:
        return render(request, '500.html', {'error': error})

def roles_edit(request,pk):
    try:
        record = Role.objects.get(pk=pk)
        form = RoleForm(instance=record)
        if request.method=='POST':
            form = RoleForm(request.POST,instance=record)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.updated_by = request.user
                obj.save()
                return redirect('roles')
        context={
            'roles': 'active', 'roles_show': 'show','form':form,'screen_name':"Roles"
        }
        return render(request,'UserManagement/create.html',context)
    except Exception as error:
        return render(request, '500.html', {'error': error})

def roles_delete(request,pk):
    try:
        Role.objects.get(pk=pk).delete()
        return redirect('roles')
    except Exception as error:
        return render(request, '500.html', {'error': error})
    

def permission(request, pk):
    try:
        # Fetch all Function objects
        records = Function.objects.all()
        role_obj = Role.objects.get(pk=pk)
        permission_records = role_obj.permissions.all()
        permission_id_list = [data.id for data in permission_records]
        print('permission_records',permission_id_list)
        if request.method == 'POST':
   
            
            # Fetch permissions from POST data
            permission_ids = request.POST.getlist('permission')
            if permission_ids:
                # Assuming permissions field is a ManyToManyField related to Function
                role_obj.permissions.set(permission_ids)  # Use set() instead of add() for a fresh list
            
            role_obj.save()
            return redirect('roles')

        # Prepare the context for rendering
        context = {
            'roles': 'active', 
            'roles_show': 'show', 
            'screen_name': "Permission",
            'records': records,'permission_id_list':permission_id_list
        }
        return render(request, 'UserManagement/permission.html', context)
    
    except Exception as error:
        return render(request, '500.html', {'error': str(error)})


# Load the function names from the configuration file
def load_function_names_from_config(config_path='config/function_config.json'):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
        return config.get('functions', [])

# Example usage in a view:
def function_setup(request):
    try:
        user = request.user  # Use the currently logged-in user
        function_names = load_function_names_from_config()  # Load from the configuration file
        records_list = []

        for function_name in function_names:
            # Check if the function already exists
            if not Function.objects.filter(function_name=function_name).exists():
                # Create a new function
                function = Function.objects.create(
                    function_name=function_name,
                    description=None,  # You can modify this to add descriptions if needed
                    created_by=user
                )
                # Assign a unique ID to the function
                function.function_id = simple_unique_id_generation("FUN", function.id)
                function.save()  # Save only if it's a new record
                records_list.append(function.function_name)
            else:
                # Log if the function already exists
                print(f"Function '{function_name}' already exists.")

        # Return the success response and redirect
        print('Added functions:', records_list)
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    except Exception as error:
        # Render a 500 error page with the exception details
        return render(request, '500.html', {'error': str(error)})