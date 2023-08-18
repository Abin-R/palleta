from django.contrib import admin
from django.urls import path,include, re_path
from . import views
from store.views import custom_404_view

urlpatterns = [
    
    #home:
    path('',views.home ,name='home' ),

    # path('search/', views.search_view, name='search'),

    #category view:
    path('product-display/',views.product_page ,name='products-display' ),

    #product detail view:
    path('product-detail-view/<int:id>',views.product ,name='product-detail-view' ),

    
    #filter:
    path('products/filter/', views.product_filter, name='product_filter'),
    path('products/filters/', views.product_filters, name='product_filters'),
    
    #wishlist:
    path('wishlist/',views.wishlist,name="wishlist"),
    path('add_to_wishlistt/<int:variant_id>/', views.add_to_wishlistt, name='add_to_wishlistt'),
    path('remove_from_wishlist/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    

    

    # URL pattern for the update_quantity view
    
    path('search/', views.search, name='search'),
    
    # URL for the autocomplete view
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    
    
    

]
