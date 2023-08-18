from django.contrib import admin
from django.urls import path,include, re_path
from . import views

urlpatterns = [
    

    #cart:
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),

]