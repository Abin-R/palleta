from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from store.models import *
from django.views.decorators.cache import cache_control
from django.shortcuts import render, redirect
from django.db.models import F
from store.models import Cart, CartItem
from django.db.models import Sum
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist




#add to cart:
def add_to_cart(request, variant_id):

    try:
        variant = ProductVariant.objects.get(id=variant_id)
        user = request.user

        # Check if a cart exists for the user, or create a new one
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id

        # Check if the item is already in the cart
        item = cart.cartitem_set.filter(productvariant=variant).first()
        if item:
            available_stock = variant.stock - item.quantity
            # Check if the requested quantity is available in stock
            requested_quantity = 1
            if requested_quantity <= available_stock:
                item.quantity += requested_quantity  # Increase the quantity by requested_quantity
                item.save()
                messages.success(request, 'Item added to cart.')
            else:
                # Display an error message to the user
                messages.error(request, 'Requested quantity exceeds available stock.')
        else:
            # Check if the requested quantity is available in stock
            if 1 <= variant.stock:
                CartItem.objects.create(cart=cart, productvariant=variant, quantity=1, price=variant.price)
                messages.success(request, 'Item added to cart.')
            else:
                # Display an error message to the user
                messages.error(request, 'Requested quantity exceeds available stock.')
        
        if not user.is_authenticated:
            request.session['cart_id'] = cart_id
        
        response_data = {
            'status': 'success',
            'nameProduct': 'Product Name',  # Replace with the actual product name
        }

    except Exception as e:

         response_data = {
            'status': 'error',
            'message': 'Failed to add item to cart. Please try again later.',
        }
    
    return JsonResponse(response_data)
     


#remove from cart:
def remove_from_cart(request, id):
    try:
        cart_item = CartItem.objects.get(id=id)
        cart_item.delete()
        # Rest of the code

        return redirect('cart')  # Redirect to the cart page after successfully removing the item
    except ObjectDoesNotExist:
        # Handle the case where the CartItem does not exist
        # Display an error message or redirect to a different page
        return HttpResponse("The selected item does not exist in the cart.")

from django.db.models import Sum
def cart_view(request):
    user = request.user

    if user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    
    cartitem = CartItem.objects.all()
    total_item_cost = 0  # Initialize the total item cost
    total_discount = 0 

    if cartitem.exists():
        # Calculate the total price with the discounted price using the property
        total_price = 0
        for cart_item in cart.cartitem_set.all():
            total_item_cost += cart_item.quantity * cart_item.productvariant.price
            total_discount += (cart_item.quantity * cart_item.productvariant.price) - cart_item.get_discount_price

        coupon = request.POST.get('coupon')
        coupon_obj = None

        if request.method == 'POST' and coupon:
            coupon_obj = Coupon.objects.filter(code__icontains=coupon).first()
            if not coupon_obj:
                messages.warning(request, 'Invalid coupon')
            else:
                cart.coupon = coupon_obj
                cart.save()
                messages.success(request, 'Coupon applied')

        total_price = total_item_cost - total_discount
        total_price_str = str(total_price)

        if cart.coupon and coupon_obj:
            total_price -= cart.coupon.discount
            total_price_str = str(total_price)
            coupon_discount = cart.coupon.discount
        else:
            coupon_discount = 0

        request.session['total_price'] = total_price_str

        coupons = Coupon.objects.all()
        context = {
            'cart': cart,
            'total_price': total_price_str,
            'total_item_cost': total_item_cost,
            'total_discount': total_discount,
            'cartitem': cartitem,
            'coupon_discount':coupon_discount,
            'coupons': coupons,
        }

        return render(request, 'cart/cart.html', context)
    
    



#update quantity
def update_quantity(request):
    
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        
        try:
            product = CartItem.objects.get(id=product_id)
            product.quantity = int(quantity)  # Convert to integer

            # Convert product variant price to Decimal before calculation
            product.price = Decimal(product.productvariant.price) * Decimal(product.quantity)
            product.save()

            # Prepare the response data
            response_data = {
                'success': True,
                'message': 'Quantity updated successfully!',
                'price': str(product.price),
                'quantity': str(product.quantity)
            }
            return JsonResponse(response_data)
        
        except (ObjectDoesNotExist, ValueError):
            response_data = {
                'success': False,
                'message': 'Invalid product ID or quantity'
            }
            return JsonResponse(response_data, status=400)

    response_data = {
        'success': False,
        'message': 'Invalid request'
    }
    return JsonResponse(response_data, status=400)