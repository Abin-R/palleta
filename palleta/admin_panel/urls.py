
from django.urls import path
from . import views

urlpatterns = [
    
    #ADMIN 
    path('admin-signin',views.admin_signin ,name='admin_signin' ),
    path('signout/',views.signout ,name='signout' ),
    path('dashboard/',views.dashboard ,name='dashboard' ),
    path('main/',views.main ,name='main' ),

    #artist:
    path('artist-list/',views.artist_list,name='artist_list'),
     path('artists/add/', views.add_artist, name='add_artist'),

    #size
    path('sizes/', views.size_list, name='size-list'),
    path('sizes/create/', views.size_create, name='size-create'),

    #USER 
    path('userlist/',views.user_list ,name='user_list' ),
    path('block_user/<int:user_id>/',views.block_user,name='block_user'),
    path('unblock_user/<int:user_id>/',views.unblock_user,name='unblock_user'),

    #CATEGORIES
    path('categories/',views.categories ,name='categories' ),
    path('add_category/', views.add_category, name='add_category'),
    path('category/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('disable_category/<int:category_id>/', views.disable_category, name='disable_category'),
    path('enable_category/<int:category_id>/', views.enable_category, name='enable_category'),

    #PRDUCT
    path('product/',views.product ,name='product' ),
    path('product-detail/<int:product_id>',views.product_variant ,name='product_detail' ),
    path('add_product/',views.add_product ,name='add_product' ),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('disable_product/<int:product_id>/', views.disable_product, name='disable_product'),
    path('enable_product/<int:product_id>/', views.enable_product, name='enable_product'),

    #ORDER
    path('order-view/<int:order_id>/', views.order_view, name='order_view'), 
    path('orders/', views.order_list, name='order_list'),
    

    path('order_shipped/<int:order_id>/', views.order_shipped, name='order_shipped'),
    path('order_delivered/<int:order_id>/', views.order_delivered, name='order_delivered'),
    path('admin/order/<int:order_id>/cancel/', views.admin_order_cancel, name='admin_order_cancel'),

    path('return_orders/<int:order_id>/', views.return_orders, name='return_orders'),

    #BANNER:
    path('banner/', views.banner_view, name='banner'),
    path('add-banner/', views.add_banner, name='add_banner'),

    path('change_status/<int:order_id>/', views.change_status, name='change_status'),
    path('download_order_pdf_sales/', views.download_order_pdf_sales, name='download_order_pdf_sales'),
    
    path('admin_order_cancel/<int:order_id>', views.admin_order_cancel, name='admin_order_cancel'),

    path('coupon/', views.coupon, name='coupon'),

    path('add_coupon/', views.add_coupon, name='add_coupon'),



]