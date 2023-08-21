from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from .models import *
from django.views.decorators.cache import cache_control
from django.shortcuts import render, redirect
from django.db.models import F
from .models import Cart, CartItem
from django.db.models import Sum
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count



@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    productvariant = ProductVariant.objects.all()
    banner = Banner.objects.all()

    if request.user.is_authenticated:
        wishlist_items = Wishlistitem.objects.filter(wishlist__user = request.user)
        product_in_wishlist = [item.product.product for item in wishlist_items]
    else:
        product_in_wishlist =[]
    
    
    top_selling_products = Product.objects.annotate(sales_count=Count('productvariant__orderitem')).order_by('-sales_count')[:4]
    
    context = {
        'categories': categories,
        'products': products,
        'productvariant':productvariant,
        'banner':banner,
        'product_in_wishlist':product_in_wishlist,
        'top_selling_products':top_selling_products,
    }
    
    if request.user.is_authenticated:
        return render(request, 'store/index.html',context )
    
    return render(request, 'store/index.html', context)




#filter:
def product_filter(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Validate and convert min_price and max_price to Decimal
    min_price = Decimal(min_price) if min_price else None
    max_price = Decimal(max_price) if max_price else None

    products = Product.objects.filter(enabled=True)
    if min_price is not None:
        products = products.filter(productvariant__price__gte=min_price)
    if max_price is not None:
        products = products.filter(productvariant__price__lte=max_price)
       
    products = products.distinct('name')

    

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'store/index.html', context)

def product_filters(request):
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Validate and convert min_price and max_price to Decimal
    min_price = Decimal(min_price) if min_price else None
    max_price = Decimal(max_price) if max_price else None

    products = Product.objects.filter(enabled=True)
    if min_price is not None:
        products = products.filter(productvariant__price__gte=min_price)
    if max_price is not None:
        products = products.filter(productvariant__price__lte=max_price)
       
    products = products.distinct('name')

    

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'store/product_page.html', context)


#category view
def product_page(request):
    categories = Category.objects.all()
    sort_option = request.GET.get('sort')

    if sort_option == 'low_to_high':
        products = Product.objects.order_by('productvariant__price')
    elif sort_option == 'high_to_low':
        products = Product.objects.order_by('-productvariant__price')
    elif sort_option == 'newness':
        products = Product.objects.order_by('-created_in')
    elif sort_option == 'popularity':
        products = Product.objects.annotate(sales_count=Count('productvariant__orderitem')).order_by('-sales_count')
    else:
        products = Product.objects.all()

    

    context = {
        'categories': categories,
        'products': products,
    }
    return render(request,'store/product_page.html',context)

from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from .models import Product, Offer

def product(request, id):
    product = get_object_or_404(Product, pk=id)  # Fetch the Product object
    selected_variant = product.productvariant_set.first()

    if request.method == 'POST':
        selected_variant_id = request.POST.get('variant_id')
        selected_variant = product.productvariant_set.get(id=selected_variant_id)

    variants = product.productvariant_set.all()

    variant_discount_percentage = selected_variant.discount_percentage if selected_variant else None

    category_discount_percentage = 0
    try:
        category_discount = Offer.objects.get(category=product.category)
        category_discount_percentage = category_discount.discount_percentage
    except Offer.DoesNotExist:
        pass

    # Calculate the discounted price based on the higher discount percentage (variant or category)
    original_price = selected_variant.price if selected_variant else product.price
    if variant_discount_percentage is not None and category_discount_percentage is not None:
        max_discount_percentage = max(variant_discount_percentage, category_discount_percentage)
    elif variant_discount_percentage is not None:
        max_discount_percentage = variant_discount_percentage
    elif category_discount_percentage is not None:
        max_discount_percentage = category_discount_percentage
    else:
        max_discount_percentage = 0

    discounted_price = original_price - (original_price * Decimal(max_discount_percentage / 100))

    context = {
        'product': product,
        'selected_variant': selected_variant,
        'variants': variants,
        'discounted_price': discounted_price,
    }

    return render(request, 'product/product_view.html', context)




def base(request):
    return render(request,'store/base.html')










# views.py



def add_to_wishlistt(request,variant_id):
        

  
        product = ProductVariant.objects.get(id =variant_id)
        wishlist,created = Wishlist.objects.get_or_create(user=request.user)
        

        item = wishlist.wishlistitem_set.filter(product=product).first()

        if not item:
            
            item = Wishlistitem(wishlist=wishlist,product=product)
            item.save()
        
        referring_page = request.META.get('HTTP_REFERER')
    # Redirect back to the referring page
        return redirect(referring_page)

def wishlist(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get or create the user's wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        # Get all WishlistItem objects associated with the user's wishlist
        items = Wishlistitem.objects.filter(wishlist=wishlist)
        cart_items = CartItem.objects.filter(cart__user=request.user)
        
        # Create a set of product variant IDs that are in the cart
        cart_item_ids = set(cart_item.productvariant.id for cart_item in cart_items)

        # Pass the 'items' variable to the template context
        context = {
            'items': items,
            'cart_item_ids': cart_item_ids,
        }
    else:
        context = {}

    return render(request, 'wishlist/wishlist.html', context)


def remove_from_wishlist(request, item_id):
   
    # Get the WishlistItem object with the given item_id
    try:
        item = Wishlistitem.objects.get(pk=item_id)
    except Wishlistitem.DoesNotExist:
        # Item not found, handle the error as per your requirement
        return redirect('wishlist')  # Redirect back to the wishlist

    # Check if the item belongs to the current user's wishlist
    if item.wishlist.user == request.user:
        item.delete()
    
    referring_page = request.META.get('HTTP_REFERER')
    # Redirect back to the referring page
    return redirect(referring_page)

from django.db.models import Q
from .models import Category, Product

def search(request):
    categories = Category.objects.all()  # Get all categories

    if request.method == "GET":
        query = request.GET.get('query')
        
        if query:
            products = Product.objects.filter(name__icontains=query)
            
            if products.exists():
                return render(request, 'store/product_page.html', {'products': products, 'categories': categories})
            else:
                messages.info(request, 'No results found.')
        
        else:
            messages.info(request, 'Please enter a search query.')

    return render(request, 'store/product_page.html', {'categories': categories})


def autocomplete(request):
    if 'term' in request.GET:
        qs = Product.objects.filter(name__icontains=request.GET.get('term'))
        names = list(qs.values_list('name', flat=True))
        return JsonResponse(names, safe=False)
    return render(request, 'catagory.html')


def custom_404_view(request, exception):
    return render(request, 'store/error_page.html', status=404)
