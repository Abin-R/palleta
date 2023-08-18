from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from userprofile.models import *
from django.utils import timezone
from multiselectfield import MultiSelectField



class Category(models.Model):
    name = models.CharField(max_length=100, null=False)
    image = models.ImageField(upload_to='category_images', null=True, blank=True)
    enabled = models.BooleanField(default=True) 
    # other fields...

    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ""
        return url


class Artist(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100,unique=True)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True)
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    # size = models.CharField(max_length=50, null=True, blank=True)
    medium = models.CharField(max_length=50, null=True, blank=True)
    style = models.CharField(max_length=50, null=True, blank=True)
    created_in = models.PositiveIntegerField(null=True, blank=True)
    seller = models.CharField(max_length=50, null=True, blank=True)
    enabled = models.BooleanField(default=True)
    
    

    # Add more fields as needed

    def __str__(self):
        return self.name




class Size(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    category =  models.ForeignKey(Category,on_delete=models.CASCADE,null=True, blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True, blank=True)
    discount_percentage = models.PositiveIntegerField(null=True,blank=True)
    size = models.ForeignKey(Size,on_delete=models.CASCADE,null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0) 

    
    def __str__(self):
        return f"{self.product.name} - {self.size.name if self.size else 'No Size'} - ${self.price} - {'Active' if self.is_active else 'Inactive'}"
    
    @property
    def get_discount_price(self):

        Product_discount = self.discount_percentage if self.discount_percentage else 0
        discounted_price = Decimal(self.price)-Decimal(self.price) * (Decimal(Product_discount)/100)

        

        return round(discounted_price,0)

class Image(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images',null=True,blank=True)
    image = models.ImageField(upload_to='product_images')
    # Add any other relevant fields

    def __str__(self):
        return f"Image for {self.variant.product.name}"

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=8, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    minimum_order_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    single_use_per_user = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    coupon =  models.ForeignKey(Coupon,on_delete=models.CASCADE,null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True, blank=True)

    def __str__(self):
        return f"Cart #{self.pk} for {self.user.username}"
    
    def get_total_price(self):
        return self.cartitem_set.aggregate(total_price=Sum('price'))['total_price']

    def get_discounted_total_price(self):
        total_price = self.get_total_price()
        if self.coupon:
            total_price -= self.coupon.discount
        return total_price
    # User = get_user_model()

@receiver(post_save, sender=User)
def create_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)
    


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    productvariant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.productvariant.product.name} ({self.quantity})"
    
    @property
    def subtotal(self):
        return self.quantity * self.price
    @property
    def item_price(self):
        return Decimal(self.quantity) * self.productvariant.price

    @property
    def get_discount_price(self):
        result = self.productvariant.get_discount_price
        discount_price  = self.productvariant.get_discount_price

        return Decimal(self.quantity) * Decimal(discount_price)


    
    def get_item_price(self):
        return Decimal(self.price) * Decimal(self.quantity)
   


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING','pending'),
        ('PAID','paid')]
    
    ORDER_STATUS_CHOICES =[
        ('CANCELLED', 'cancelled'),
        ('DELIVERED', 'Delivered'),
        ('SHIPPED', 'Shipped'),
        ('RETURNED', 'Returned'),
        ('ORDERED', 'Ordered'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('RAZORPAY', 'razorpay'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    ]


    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,null=True, blank=True)
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='ordered')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES,default='Cash on Delivery')
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Ordered')
    message = models.TextField(null=True, blank=True)
    tracking_no = models.CharField(max_length=150,null=True ,blank=True)
    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField(blank=True, null=True)
    applied_coupon = models.CharField(max_length=50, blank=True, null=True)
    razor_pay_order_id = models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()


    def __str__(self):
        return f"Order #{self.pk} for {self.user.username}"
    
    @property
    def return_period_expired(self):
        return_period_end_date = self.delivery_date + timezone.timedelta(days=5)
        return timezone.now() > return_period_end_date
    def _str_(self):
        return f"{self.id, self.tracking_no}", f"{self.id}  {self.user.username}"

    def save(self, *args, **kwargs):
        if not self.order_date:
            self.order_date = timezone.now()  # Set the order date to the current time if it's not set
        if not self.delivery_date:
            self.delivery_date = self.order_date + timedelta(hours=24)
        super().save(*args, **kwargs)


    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product_variant.product.name} ({self.quantity})"
    
    def get_item_price(self):
        return Decimal(self.price) * Decimal(self.quantity)


class Wishlist(models.Model):
     user = models.ForeignKey(User,on_delete=models.CASCADE)

     def __str__(self):
         return f"Wishlist for {self.user.username}"
     
class Wishlistitem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)

    def get_item_price(self):
        return self.product.price               
     

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def str(self):
        return f"{self.user.username}'s Wallet: {self.balance}"

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

class WalletTransaction(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE,blank=True, null=True)
    transaction_type = models.CharField(max_length=20, choices=(
        ('PURCHASE', 'Purchase'),
        ('CANCEL', 'Cancel'),
        ('RETURN', 'Return'),
    ))

    def _str_(self):
        return f"Wallet Transaction: {self.amount} - {self.date}"
    

from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100,blank=True, null=True) 
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Offer(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def _str_(self):
        return f"{self.category} - {self.discount_percentage}% Off"