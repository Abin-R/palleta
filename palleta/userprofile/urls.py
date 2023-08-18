
from django.contrib import admin
from django.urls import path,include, re_path
from . import views

urlpatterns = [

    
    path('profile/',views.profile,name="profile"),
    path('address/',views.address,name="address"),
    path('add-address/',views.add_address,name="add_address"),
    path('add_address_checkout/',views.add_address_checkout,name="add_address_checkout"),
    path('delete-address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('edit-address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('change-password/',views.change_password,name="change_passsword"),
    path('wallet/', views.wallet_view, name='wallet'),

    
    


]