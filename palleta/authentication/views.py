from django.shortcuts import render
from venv import logger
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.cache import cache_control
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import SetPasswordForm
from palleta.settings import EMAIL_HOST_USER
from store.models import *





#signup:
@cache_control(no_cache=True, must_revalidate=True, no_store=True   , max_age=0)
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please try another username.")
            return redirect("signup")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists! Please try another email.")
            return redirect("signup")
        
        
        myuser = User.objects.create_user(username=username,email=email, password=password)
        myuser.is_active = False
        myuser.save()

        

        messages.success(request, "Your account has been successfully created.")

        # welcoming email

        subject = "Welcome to Palleta !!"
        message = " Hello " + myuser.username +" !! \n" + "Welcome to Palleta !! \n Thank you for visiting our website \n We have also sent you  a confirmation email, please confirm your email address in order to activate your account . \n\n Thanking You \n Abin R "
        from_email = settings.EMAIL_HOST_USER
        to_list =[myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Generate verification token
        token = default_token_generator.make_token(myuser)

        # Build verification URL
        current_site = get_current_site(request)
        uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
        verification_url = reverse('verify_email', kwargs={'uidb64': uidb64, 'token': token})
        verification_url = f"{request.scheme}://{current_site}{verification_url}"

        # Send verification email
        mail_subject = 'Activate your account'
        message = render_to_string('authentication/verification_email.html', {
            'user': myuser,
            'verification_url': verification_url
        })
        send_mail(mail_subject, message, 'palletacompany@gmail.com', [email])
        

        
        return redirect('email_confirmation')

    return render(request, "authentication/signup.html")


#verify email:
@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('signin')

    # Handle invalid token or user not found
    return render(request, 'verification_failed.html')


#signin:
@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def signin(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        users = User.objects.filter(email=email)

        if users.exists():
            user = users.first()  # Retrieve the first user from the QuerySet

            # Authenticate using the retrieved user object and provided password
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                username = user.username
                return redirect( 'home')
            else:
                messages.error(request, "Bad credentials!")
        else:
            messages.error(request, "User does not exist!")

    return render(request, 'authentication/signin.html')

#otp:
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def otp(request):
    # Add your logic here
    return render(request, 'authentication/otp.html')



#signout:
@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def signout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('signin')



#password reset:
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Get the user associated with the provided email
            try:
                myuser = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, 'password_authentication/reset_password_form.html', {'form': form, 'error': 'Invalid email'})

             # Generate the password reset token
            token = default_token_generator.make_token(myuser)

            # Build the password reset URL
            current_site = get_current_site(request)
            uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
            reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
            reset_url = f"{request.scheme}://{current_site}{reset_url}"
            # uidb64 = urlsafe_base64_encode(force_bytes(myuser.pk))
            
            # password_reset_confirm_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

            # Send the password reset email
            mail_subject = 'Reset your password'
            message = render_to_string('password_authentication/reset_password.html', {
                'user': myuser,
                'reset_url': reset_url
            })
            send_mail(mail_subject, message, 'palletacompany@gmail.com', [email])

            # Redirect to a success page or show a success message
            return redirect('reset_confirmation')

    else:
        form = PasswordResetForm()

    return render(request, 'password_authentication/reset_password_form.html', {'form': form})



#password reset confirm:
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def password_reset_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        

        myuser = User.objects.get(pk=uid)
        request.session['user_pk'] = myuser.pk
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        if request.method == 'POST':
            form = SetPasswordForm(myuser, request.POST)
            if form.is_valid():
                form.save()
                return redirect('signin')
        else:
            form = SetPasswordForm(myuser)
        return render(request, 'password_authentication/reset_password_confirm_form.html', {'form': form})
    else:
        # Handle invalid token
        return redirect('signup')



#update password:
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_password(request):
    user_id = request.session.get('user_pk')
    try:
        myuser = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        # Handle the case where the user doesn't exist
        return redirect('signin')  # Or any other appropriate action

    if request.method == 'POST':
        password = request.POST['password']
        new_password = password
        myuser.set_password(new_password)
        username = myuser.username
        myuser.save()
        user = authenticate(username=username, password=new_password) 
        login(request, user)
        return render(request,'authentication/signin.html')
    else:
        return render(request, 'password_authentication/password_reset_confirm.html')


#email-confirmation
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def email_confirmation(request):
    return render(request, 'authentication/email_confirmation.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def reset_confirmation(request):
    return render(request, 'password_authentication/reset_confirmation.html')
from django.shortcuts import render

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def terms_and_condition(request):
    # Add your logic here
    return render(request, 'authentication/terms_and_conditions.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def privacy_policy(request):
    # Add your logic here
    return render(request, 'authentication/privacy_policy.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def admins(request):
    if request.user.is_superuser:
        if request.GET.get('search') is not None:
            search = request.GET.get('search')
            users = User.objects.filter(username__contains=search)
        else:
            users = User.objects.all()  # Corrected line here
        context = {
            'users': users
        }
        return render(request, 'admin/admin.html', context)
    else:
        return redirect('home')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def edit_user(request,user_id):
    if request.user.is_superuser:

        user=User.objects.get(id=user_id)
        
        if request.method == 'POST':
            username=request.POST['username']
            email=request.POST['email']
            password=request.POST['password']
            
            user.username=username
            user.email=email
            user.set_password=password
            
            user.save()
            messages.success(request,'Updated succesfully')
            
            return redirect('admins')
        
        return render(request,'admin/edit.html',{'user':user  })
        
    else:
        return redirect('home')


        

@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def delete_user(request,user_id):
    if request.user.is_superuser:
        
        user=User.objects.get(id=user_id)
        
        if request.method == 'POST':

            user.delete()
            messages.success(request,'user has succesfully deleted')
            return redirect('admins')
        
        
    else:
        return redirect('admins')

@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def add_user(request):
    if request.user.is_superuser:

        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']

            myuser = User.objects.create_user(username,email,password)
            
            myuser.save()
            messages.success(request,'Account has succesfully created')
            return redirect('admins')
        
        return render(request , 'admin/add_user.html')
    else:
        return redirect('home')


def custom_signin(request):
   
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            guest_cart_id = request.session.get('cart_id')
            if guest_cart_id:
                try:
                    guest_cart = Cart.objects.get(id=guest_cart_id)
                    user_cart, created = Cart.objects.get_or_create(user_id=user)

                    for guest_item in guest_cart.cartitem_set.all():
                        
                        try:
                            
                            user_item = CartItem.objects.get(cart=user_cart, productvariant= guest_item.productvariant)
                            # Check if the item is already in the cart
                            # If yes, update the quantity
                            available_stock = guest_item.productvariant.stock - user_item.quantity
                            if guest_item.quantity <= available_stock:
                                user_item.quantity += guest_item.quantity
                                user_item.save()
                            else:
                                # Display an error message if the requested quantity exceeds the available stock
                                messages.error(request, f"Requested quantity for '{guest_item.product}' exceeds available stock.")
                        except CartItem.DoesNotExist:
                            # If the item is not in the cart, create a new cart item
                            CartItem.objects.create(
                                cart=user_cart,
                                productvariant=guest_item.productvariant,
                                quantity=guest_item.quantity,
                                price=guest_item.productvariant.price
                            )

                    # Delete the guest cart after merging
                    guest_cart.delete()
                    # Clear the cart_id from the session since the guest cart is no longer needed
                    del request.session['cart_id']

                except Cart.DoesNotExist:
                    # Handle the case when the guest cart does not exist or is already deleted
                    pass

            return redirect('cart')

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'authentication/custom_signin.html')



# Create your views here.
