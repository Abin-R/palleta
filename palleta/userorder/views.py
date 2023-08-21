from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import razorpay
from store.models import OrderItem
from django.shortcuts import render
from userprofile.models import Address
from decimal import Decimal
from django.shortcuts import render
from store.models import *
from django.shortcuts import render, redirect
from django.conf import settings





def order(request):
    user = request.user
    order = Order.objects.filter(user=user)
    order_items = OrderItem.objects.filter(order__user=user)
    context = {
        'order':order,
        'order_items': order_items,
    }
    return render(request, 'order.html', context)



def checkout(request):
    user = request.user
    addresses = Address.objects.filter(user=user).order_by('id')
    cart_items = CartItem.objects.filter(cart__user=user)
    wallet = Wallet.objects.filter(user=request.user)  # Filter cart items associated with the current user

    cart = Cart.objects.get(user=user)  # Get the user's cart
    total_price = cart.get_total_price()
    
    if 'total_price' in request.session:
        total_price = request.session['total_price']
    

    context = {
        'addresses': addresses,
        'wallet':wallet,
        'cart' : cart,
        'cart_items': cart_items,
        'total_price': total_price,  # Pass the overall total_price to the template
    }

    return render(request, 'checkout/checkout.html', context)


def place_order(request, address_id):
    user = request.user
    try:
        wallet = Wallet.objects.get(user=user)
    except Wallet.DoesNotExist:
        # Handle the case where the user's wallet doesn't exist
        wallet = None
    
    address = Address.objects.get(id=address_id)
    try:
        cart = Cart.objects.get(user=user)
        cart_items = cart.cartitem_set.all()  # Retrieve all cart items for the user's cart
        total_price = cart.get_total_price()
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0
    
    if 'total_price' in request.session:
        total_price = request.session['total_price']
    
    total_price = float(total_price) 
    
    context = {
        'cart': cart,
        'wallet':wallet,
        'cart_items': cart_items,  # Add the cart items to the context
        'total_price': total_price,
        'address': address,
    }
    
    
    return render(request, 'checkout/proceed.html', context)


def cash_order(request,address_id):
    # Create and save the Order object
    user = request.user
    cart = Cart.objects.get(user=user)
    total_price = cart.get_total_price()
    address = Address.objects.get(id=address_id)

   
    order = Order.objects.create(
        user=user, 
        total_price=total_price,
        shipping_address = address_id)

    if 'total_price' in request.session:
        total_price = request.session['total_price']

    order = Order.objects.create(
        user=request.user,
        address= address,
        total_price=total_price,
        payment_status='ORDERED',
        payment_method='CASH_ON_DELIVERY',
        # applied_coupon=applied_coupon,
    )

    # Transfer cart items to the order (order items)
    for cart_item in cart.cartitem_set.all():
        order_item = OrderItem.objects.create(
            order=order,
            product_variant=cart_item.productvariant,  # Change the argument name here
            quantity=cart_item.quantity,
            price=cart_item.price,
        )
        price=cart_item.price,
       

        product_variant = cart_item.productvariant
        product_variant.stock -= cart_item.quantity
        product_variant.save()
    # Clear the cart
    cart.cartitem_set.all().delete()

    return render(request,'order_confirmation.html')


def order_remove(request,order_id): 
    order = Order.objects.filter(id=order_id).first()
    order.delete()
    return redirect('/',order_id)

def initiate_payment(request):
    if request.method == 'POST':
        # Retrieve the total price and other details from the backend
        cart = Cart.objects.get(user_id=request.user)
        cart_items = cart.cartitem_set.all()
        if 'total_price' in request.session:
            total_price = request.session['total_price']
            total_price = Decimal(total_price)

        # total_cart_price = cart.cartitem_set.aggregate(total_price=Sum('price', field='price * quantity'))['total_price'] or 0

        total_amount_in_cents = int( total_price*100)
        

        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.KEY_SECRET))
        payment = client.order.create({

            'amount': total_amount_in_cents,
            'currency': 'INR',
            'payment_capture': 1

        })

        response_data = {
            'order_id': payment['id'],
            'amount': payment['amount'],
            'currency': payment['currency'],
            'key': settings.RAZOR_KEY_ID,

        }
        return JsonResponse(response_data)

    # Return an error response if the request method is not POST
    return JsonResponse({'error': 'Invalid request method'})

def online_payment_order(request, add_id):
    if request.method == 'POST':
        payment_id = request.POST.getlist('payment_id')[0]
        orderId = request.POST.getlist('orderId')[0]
        signature = request.POST.getlist('signature')[0]
        user_address = get_object_or_404(Address, id=add_id, user=request.user)
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cartitem_set.all()

        if 'total_price' in request.session:
            total_price = request.session['total_price']

        total_price = request.session.get('total_price', Decimal('0.00'))
        applied_coupon = request.session.get('applied_coupon', None)



        order = Order.objects.create(
            user=request.user,
            address=user_address,
            total_price=total_price,
            payment_status='PAID',
            payment_method='RAZORPAY',
            order_status='ORDERED',
            razor_pay_payment_id=payment_id,
            razor_pay_payment_signature=signature,
            razor_pay_order_id=orderId,
            
        )

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_variant=cart_item.productvariant,
                price=cart_item.price,
                quantity=cart_item.quantity
            )
            variant = cart_item.productvariant
            variant.stock -= cart_item.quantity
            variant.save()

        cart_items.delete()
        orderId = order.id


        return JsonResponse({'message': 'Order placed successfully', 'orderId': orderId})
    else:
        # Handle invalid request method (GET, etc.)
        return JsonResponse({'error': 'Invalid request method'})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

def pay_wallet(request, address_id):
    user = request.user
    address = get_object_or_404(Address, id=address_id, user=user)
    cart = Cart.objects.get(user=user)
    cart_items = cart.cartitem_set.all()
    
    total_price = cart.get_total_price()
    
    # You might need additional calculations here based on your logic
    
    user_wallet = Wallet.objects.get(user=user)
    
    if user_wallet.balance >= total_price:
        try:
            with transaction.atomic():
                # Deduct the payment amount from the user's wallet
                user_wallet.balance -= total_price
                user_wallet.save()

                # Create a wallet transaction record
                transaction_type = 'PURCHASE'
                WalletTransaction.objects.create(
                    wallet=user_wallet,
                    amount=-total_price,
                    order_id=None,  # No related order for direct wallet payment
                    transaction_type=transaction_type,
                )

                # Create an order
                order = Order.objects.create(
                    user=user,
                    address=address,
                    total_price=total_price,
                    payment_status='PAID',  # Adjust payment status based on your logic
                    payment_method='WALLET',  # Adjust payment method based on your logic
                    # Add other relevant fields
                )

                # Transfer cart items to the order (order items)
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product_variant=cart_item.productvariant,
                        quantity=cart_item.quantity,
                        price=cart_item.price,
                    )

                    product_variant = cart_item.productvariant
                    product_variant.stock -= cart_item.quantity
                    product_variant.save()



                # Clear the cart
                cart_items.delete()

                messages.success(request, 'Payment successful using wallet!')
                return render(request,'order_confirmation.html')
                
        except Exception as e:
            # Handle any exception that might occur during the transaction
            messages.error(request, 'An error occurred during payment.')

    else:
        messages.error(request, 'Insufficient wallet balance.')

    return redirect('/')  # Replace with the actual view name


def order_success(request):
    return render(request,'order_confirmation.html')

def order_view(request,order_id):
    orders = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=orders)
    total_price = sum(item.price * item.quantity for item in items)

   

    context = {
        'orders':orders,
        'items':items,
        'total_price':total_price
    }
   

    return render(request,"order/order_view.html",context)
    