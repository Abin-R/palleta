from .models import Cart, Wishlist  # Import your Cart and Wishlist models here

def cart_and_wishlist_counts(request):
    cart_items_count = 0
    wishlist_items_count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items_count = sum([item.quantity for item in cart.cartitem_set.all()])
        
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist_items_count = wishlist.wishlistitem_set.count()  # Count wishlist items

    return {
        'cart_items_count': cart_items_count,
        'wishlist_items_count': wishlist_items_count,
    }
