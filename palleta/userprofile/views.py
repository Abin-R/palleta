from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from store.models import *

@login_required
def profile(request):
    if request.method == 'POST':
        # Get the submitted form data
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')  # Add phone_number field
        
        # Update the user object with the new information
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email
        user.phone_number = phone_number  # Save phone number
        user.save()

        # Redirect back to the user profile page or any other desired page
        return redirect('profile')

    return render(request, 'profile/profile.html')
from django.contrib.auth.decorators import login_required

@login_required
def address(request):
    user = request.user
    addresses = Address.objects.filter(user=user).order_by('id')

    context = {
        'addresses': addresses,
    }

    return render(request, 'profile/address.html', context)



def add_address(request):
    if request.method == 'POST':
        # Get form data from the request
        branch = request.POST.get('branch')
        house_name = request.POST.get('house_name')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        address = Address(
            user=request.user,  # Assuming the request has a logged-in user
            branch=branch,
            house_name=house_name,
            city=city,
            district=district,
            state=state,
            zip_code=zip_code,
            country=country
        )
        address.save()
        
        
            
        return redirect('address')
        

    return render(request, 'profile/add_address.html')

def add_address_checkout(request):
    if request.method == 'POST':
        # Get form data from the request
        branch = request.POST.get('branch')
        house_name = request.POST.get('house_name')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        address = Address(
            user=request.user,  # Assuming the request has a logged-in user
            branch=branch,
            house_name=house_name,
            city=city,
            district=district,
            state=state,
            zip_code=zip_code,
            country=country
        )
        address.save()
        
        
            
        return redirect('checkout')
        

    return render(request, 'profile/add_address_checkout.html')

def edit_address(request, address_id):
    # Get the existing address object or return a 404 page if not found
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        # Get form data from the request
        branch = request.POST.get('branch')
        house_name = request.POST.get('house_name')
        city = request.POST.get('city')
        district = request.POST.get('district')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        country = request.POST.get('country')

        # Update the existing address with the new information
        address.branch = branch
        address.house_name = house_name
        address.city = city
        address.district = district
        address.state = state
        address.zip_code = zip_code
        address.country = country
        address.save()

        return redirect('address')
        
    # Pass the address object to the template for pre-filling the form fields
    return render(request, 'profile/edit_address.html', {'address': address})

@login_required
def change_password(request):
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        # Verify the current password
        if not request.user.check_password(current_password):
            messages.error(request, 'Invalid current password. Please try again.')
            return redirect('change_password')

        # Check if the new password and confirm password match
        if new_password != confirm_new_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('change_password')

        # Update the password
        request.user.password = make_password(new_password)
        request.user.save()

        # Update the session authentication hash to keep the user logged in
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Your password was successfully updated!')
        return redirect('profile')

    return render(request, 'profile/change_password.html')

def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        return redirect('address')
    
    return render(request, 'profile/delete_address.html', {'address': address})

@login_required
def wallet_view(request):
    user_wallet = Wallet.objects.get(user=request.user)
    context = {'wallet': user_wallet}
    return render(request, 'profile/wallet.html', context)