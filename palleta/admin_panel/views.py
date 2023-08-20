from datetime import date
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import  logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from psycopg2 import IntegrityError
from admin_panel.forms import *
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import user_passes_test, login_required


def is_superuser(user):
    return user.is_superuser

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def admin_signin(request):
   
   if request.user.is_authenticated and request.user.is_superuser:
       
       return redirect('dashboard')
   if request.method == 'POST':
    
      username = request.POST["username"]
     
      pass1 = request.POST['pass1']
    
      user = authenticate(username = username, password = pass1)

      if user is not None and user.is_superuser :
        
          login(request,user)
          return redirect('dashboard')
      else:
          return redirect('admin_signin')
      
   return render(request,'admin/admin_signin.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def dashboard(request):
    if request.method == 'GET':
     
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if not start_date and not end_date:
            # Calculate the current date
            current_date = timezone.now().date()

            # Calculate the date 30 days back from the current date
            default_start_date = current_date - timedelta(days=30)
            default_end_date = current_date

            # Convert to string format (YYYY-MM-DD)
            start_date = default_start_date.strftime('%Y-%m-%d')
            end_date = default_end_date.strftime('%Y-%m-%d')

        if start_date and end_date:
            # Corrected query filter for start_date and end_date using 'date' lookup
            order_count_date = Order.objects.filter(
                Q(order_date__date__gte=start_date) | Q(order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__isnull=True)
            ).exclude(payment_status='CANCELLED').count()

            total_price_date = Order.objects.filter(
                Q(order_date__date__gte=start_date) | Q(order_date__date__lte=end_date) |
                Q(order_date__date=end_date, order_date__isnull=True)
            ).exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            daily_totals = Order.objects.filter(
                Q(order_date__date__gte=start_date) & Q(order_date__date__lte=end_date) 
            ).exclude(payment_status='CANCELLED').annotate(date=TruncDate('order_date')).values('date').annotate(
                total=Sum('total_price')).order_by('date')

            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']
            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)
            recent_orders = Order.objects.order_by('-order_date')[:3]

            # Corrected query for top_selling_products using 'product_id' and 'product__name'
            top_selling_products = OrderItem.objects.values('product_variant__product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]

            

            categories = Category.objects.all()
            data = [Product.objects.filter(category=category).count() for category in categories]
           
            context = {
                'order_count_date': order_count_date,
                'total_price_date': total_price_date,
                'start_date': start_date,
                'end_date': end_date,
                'daily_totals': daily_totals,
                'order_count': order_count,
                'total_price': total_price,
                'categories': categories,
                'data': data,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }

            return render(request, 'admin/dashboard.html', context)

        else:
            order_count = Order.objects.exclude(payment_status='CANCELLED').count()
            total_price = Order.objects.exclude(payment_status='CANCELLED').aggregate(total=Sum('total_price'))['total']

            today = timezone.now().date()
            today_orders = Order.objects.filter(order_date__date=today)
            order_count_today = today_orders.count()
            total_price_today = sum(order.total_price for order in today_orders)

            categories = Category.objects.all()
            data = [Product.objects.filter(category=category).count() for category in categories]

            recent_orders = Order.objects.order_by('-order_date')[:3]

            # Corrected query for top_selling_products using 'product_id' and 'product__name'
            top_selling_products = OrderItem.objects.values('product__name').annotate(
                total_quantity=Sum('quantity')
            ).order_by('-total_quantity')[:5]

            context = {
                'order_count': order_count,
                'total_price': total_price,
                'start_date': start_date,
                'end_date': end_date,
                'order_count_today': order_count_today,
                'total_price_today': total_price_today,
                'categories': categories,
                'data': data,
                'recent_orders': recent_orders,
                'top_selling_products': top_selling_products,
            }

            return render(request, 'dashboard.html', context)

    return HttpResponseBadRequest("Invalid request method.")


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def download_order_pdf_sales(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's totals
    today_orders = Order.objects.filter(order_date__date=today)
    order_count_today = today_orders.count()
    total_price_today = today_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Weekly totals
    week_orders = Order.objects.filter(order_date__date__range=[week_ago, today])
    order_count_week = week_orders.count()
    total_price_week = week_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Monthly totals
    month_orders = Order.objects.filter(order_date__date__range=[month_ago, today])
    order_count_month = month_orders.count()
    total_price_month = month_orders.aggregate(Sum('total_price'))['total_price__sum']

    # Top selling products
    # Assuming your Orderlist model has a foreign key to the ProductVariant model
    top_selling_products_today = OrderItem.objects.values('product_variant__product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_week = OrderItem.objects.filter(order__order_date__date__range=[week_ago, today]).values('product_variant__product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
    top_selling_products_month = OrderItem.objects.filter(order__order_date__date__range=[month_ago, today]).values('product_variant__product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]

    context = {
        'order_count_today': order_count_today,
        'total_price_today': total_price_today,
        'order_count_week': order_count_week,
        'total_price_week': total_price_week,
        'order_count_month': order_count_month,
        'total_price_month': total_price_month,
        'top_selling_products_today': top_selling_products_today,
        'top_selling_products_week': top_selling_products_week,
        'top_selling_products_month': top_selling_products_month,
    }

    # Render the HTML content using the 'sales.html' template and the provided context
    html_content = render_to_string('admin/sales.html', context)

    # Set the response content type as 'application/pdf' to indicate that it's a PDF file
    response = HttpResponse(content_type='application/pdf')

    # Set the filename for the downloaded file
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    # Generate the PDF content from the HTML using xhtml2pdf
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), response)
    
    if pdf.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
# user list:
def user_list(request):
        if request.GET.get('search') is not None:
            search = request.GET.get('search')
            users = User.objects.order_by('username')
        else:
            users = User.objects.all().order_by('username')  # Corrected line here
        context = {
            'users': users
        }
        return render(request, 'admin/user_list.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#Block User:
def block_user(request,user_id):

    if request.user.is_superuser:

        user = User.objects.get(id=user_id)

        user.is_active = False
        user.save()
        return redirect('user_list')
    else:
        return redirect('user_list')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#Unblock User:
def unblock_user(request,user_id):
    if request.user.is_superuser:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        return redirect('user_list')
    else:
        return redirect('user_list')
    
from store.models import *


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#categories
def categories(request):
    categories = Category.objects.all().order_by('id')
    return render(request, 'admin/categories.html', {'categories': categories})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#add categories
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()

    return render(request, 'admin/add_category.html', {'form': form})


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#delete category
def disable_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.enabled = False
    category.save()
    return redirect('categories')

def enable_category(request, category_id):
    category = Category.objects.get(id=category_id)
    category.enabled = True
    category.save()
    return redirect('categories')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
# edit category
def edit_category(request, category_id):
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES,instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin/edit_category.html', {'form': form})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#products
def product(request):
    product = Product.objects.all().order_by('id')
    return render(request, 'admin/products.html', {'product': product})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def product_variant(request,product_id):
    product = get_object_or_404(Product,id = product_id)
    variant = ProductVariant.objects.filter(product=product)
    context={
        'products':product,
        'variants':variant,
        
    }
    return render(request, 'admin/product_detail.html',context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#add products
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, prefix='product')
        variant_form = ProductVariantForm(request.POST, prefix='variant')
        
        if product_form.is_valid() and variant_form.is_valid():
            product = product_form.save()
            variant = variant_form.save(commit=False)
            variant.product = product
            variant.save()

        images = request.FILES.getlist('images')
        try:
            for image in images:
                Image.objects.create(variant=variant, image=image)
        except IntegrityError as e:
            

            return redirect('product')
        else:
            
            return redirect('/')
    else:
        product_form = ProductForm(prefix='product')
        variant_form = ProductVariantForm(prefix='variant')

    return render(request, 'admin/add_product.html', {'product_form': product_form, 'variant_form': variant_form})


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#delete product
def disable_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.enabled = False
    product.save()
    return redirect('product')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def enable_product(request, product_id):
    product = Product.objects.get(id=product_id)
    product.enabled = True
    product.save()
    return redirect('product')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#edit product
def edit_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin/edit_product.html', {'form': form})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#order list
def order_list(request):
    orders = Order.objects.all().order_by('-id')
    order_item = OrderItem.objects.all().order_by('-id')
    context = {
        'orders': orders,
        'order_item':order_item,
    }
    return render(request, 'admin/order_details.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
#order view
def order_view(request, order_id):
    # Retrieve the order object using the provided order_id
    order = Order.objects.get(id=order_id)

    # Assuming the order model has a related OrderItem model, you can access the ordered items using the related_name.
    ordered_items = order.orderitem_set.all()

    context = {
        'order': order,
        'ordered_items': ordered_items,
    }

    return render(request, 'order_view.html', context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def order_shipped(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
        order.order_status = 'Shipped'
        order.shipping_date=timezone.now()
        order.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request, 'home.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def order_delivered(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)

        # Make sure the order is in the 'SHIPPED' status before marking it as 'DELIVERED'
        if order.order_status == 'Shipped':
            order.order_status = 'Delivered'
            order.delivery_date=timezone.now()
            order.return_period_expired=timezone.now()+timezone.timedelta(days=5)
            if order.payment_status=='Pending':
                order.payment_status='Paid'
            order.save()
           

    return redirect(request.META.get('HTTP_REFERER'))

# def admin_order_cancel(request, order_id):
#     if request.user.is_superuser:
#         order = get_object_or_404(Order, id=order_id)
#         user = order.user
#         if order.order_status != 'Delivered' and order.order_status != 'Returned'and order.order_status !='Cancelled' and order.order_status != 'Requested for return ':
#             order_items = OrderItem.objects.filter(order=order)
#             for item in order_items:
#                 variant = item.product
#                 variant.stock += item.quantity
#                 variant.save()
#             if order.payment_method in ['Net banking', 'Wallet pay']:
#                 user_wallet = Wallet.objects.get(user=user)
#                 # Refund the amount to the user's wallet
#                 refund_amount = order.total_price  # Assuming you want to refund the full amount
#                 user_wallet.balance += Decimal(refund_amount)
#                 user_wallet.save()
#                 transaction_type = 'Cancelled'
#                 WalletTransaction.objects.create(
#                     wallet=user_wallet,
#                     amount=refund_amount,
#                     order_id=order,
#                     transaction_type=transaction_type,
#                 )
#             if order.payment_status=='Pending':
#                 order.payment_status='No payment'
#             else:
#                 order.payment_status='Refunded'
#             order.order_status='Cancelled'
#             Order.cancelled_date=timezone.now()
#             order.save()

#         return redirect(request.META.get('HTTP_REFERER'))

#     else:
#         return render(request, 'home.html')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def return_orders(request, order_id):
    if request.user.is_superuser:
        order = get_object_or_404(Order, id=order_id)
        user = order.user
        user_wallet, created = Wallet.objects.get_or_create(user=user)
        refund_amount = order.total_price  # Assuming you want to refund the full amount
        user_wallet.balance += Decimal(refund_amount)
        user_wallet.save()
        transaction_type = 'Return'
        WalletTransaction.objects.create(
            wallet=user_wallet,
            amount=refund_amount,
            order_id=order,
            transaction_type=transaction_type,
        )
        if order.order_status != 'Cancelled':
            order.payment_status = 'Refunded'
            order.order_status = 'Returned'
            order.returned_date=timezone.now()
            order.save()

        return redirect(request.META.get('HTTP_REFERER'))

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def banner_view(request):
    
    active_banners = Banner.objects.filter(
        active=True,
        start_date__lte=date.today(),
        end_date__gte=date.today()
    )
    
    return render(request, 'admin/banner.html', {'active_banners': active_banners})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def add_banner(request):
    
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('banner')  # Redirect to the add_banner page after successful submission
    else:
        form = BannerForm()

    context = {'form': form}
    return render(request, 'admin/add_banner.html', context)


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def change_status(request, order_id):
    if request.user.is_superuser:
        order = Order.objects.get(id=order_id)
        if request.method == 'POST':
            status = request.POST['status']
            order.order_status = str(status)
            order.save()

            return redirect('order_list')

        context = {
            'order': order
        }
        return render(request, 'admin/change-status.html', context)

from django.shortcuts import get_object_or_404, redirect


from django.shortcuts import get_object_or_404, redirect
# from .models import Order, OrderItem, ProductVariant

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def admin_order_cancel(request, order_id):
 
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        if order.order_status != 'CANCELLED':
            order.order_status = 'CANCELLED'
            order.save()

            for item in order.orderitem_set.all():
                product_variant = item.product_variant
                product_variant.stock += item.quantity
                product_variant.save()

            return JsonResponse({'message': 'Order cancelled successfully'})
        else:
            return JsonResponse({'message': 'Order is already cancelled'})

    return JsonResponse({'message': 'Invalid request'}) # Updated redirection to the order list view


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def coupon(request):
    coupons = Coupon.objects.all()
    context ={
        'coupons' : coupons,
    }
    return render(request,'admin/coupon.html' ,context)

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def add_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coupon')  # Redirect to the list of coupons
    else:
        form = CouponForm()
    return render(request, 'admin/add_coupon.html', {'form': form})


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def artist_list(request):
    artists = Artist.objects.all()
    return render(request, 'admin/artist_list.html', {'artists': artists})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def add_artist(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('artist_list')
    else:
        form = ArtistForm()
    return render(request, 'admin/add_artist.html', {'form': form})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def size_list(request):
    sizes = Size.objects.all()
    return render(request, 'admin/size_list.html', {'sizes': sizes})

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url='admin_signin')  # This ensures that the user is logged in before accessing the view.
@user_passes_test(is_superuser, login_url='admin_signin') 
def size_create(request):
    if request.method == 'POST':
        form = SizeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('size-list')
    else:
        form = SizeForm()
    
    return render(request, 'your_app/size_create.html', {'form': form})
#signout:  
@cache_control(no_cache=True, must_revalidate=True, no_store=True, max_age=0)
def signout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('signin')




def main(request):
     return render(request,'admin/main.html')