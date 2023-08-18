from django.contrib import admin

# Register your models here.
from django.contrib import admin
# from cart.models import *
from .models import *
from store.models import Product
from userprofile.models import *



# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Artist)
admin.site.register(Size)
admin.site.register(Address)
admin.site.register(ProductVariant)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlistitem)
admin.site.register(Wishlist)
admin.site.register(Coupon)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
admin.site.register(Banner)
admin.site.register(Image)
