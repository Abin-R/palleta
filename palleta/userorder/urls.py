from django.contrib import admin
from django.urls import path,include, re_path
from . import views

urlpatterns = [
    
    #order:
    path('order/',views.order ,name='order' ),

    path('order_view/<int:order_id>/', views.order_view , name='order_view'),

    #checkout:
    path('checkout',views.checkout ,name='checkout' ),

    #placeorder:
    path('place_order/<int:address_id>/', views.place_order, name='place_order'),

    path('delete/<int:order_id>', views.order_remove, name="delete_order"),

    path('initiate_payment/', views.initiate_payment, name='initiate_payment'),

    path('online_payment_order/<int:add_id>',views.online_payment_order,name='online_payment_order'),

    path('order_success/', views.order_success,name='order_success'),

    path('cash_order/<int:address_id>/', views.cash_order, name='cash_order'),

    path('pay_wallet/<int:address_id>/', views.pay_wallet, name='pay_wallet'),

    

    

]