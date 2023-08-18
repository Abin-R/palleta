
from django.contrib import admin
from django.urls import path,include, re_path
from . import views

urlpatterns = [
    
    #signup:
    path('signup/',views.signup ,name='signup' ),

    #signin:
    path('signin/',views.signin ,name='signin' ),
    path('custom_signin/',views.custom_signin ,name='custom_signin' ),

    #signout:
    path('signout/',views.signout ,name='signout' ),

    #terms and conditions:
    path('terms-and-condition/', views.terms_and_condition, name='terms-and-condition'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),

    #password:
    path('password_reset/',views.password_reset ,name='password_reset' ),
    path('password_reset_confirm/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('update_password/',views.update_password ,name='update_password' ),
    path('reset_confirmation/',views.reset_confirmation ,name='reset_confirmation' ),
    

    #email:
    path('email_confirmation/',views.email_confirmation ,name='email_confirmation' ),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),

    #otp:
    path('otplogin/', views.otp, name='otplogin'),

   
    
    

    
    # path('admins/',views.admins ,name='admins' ),
    # path('edit_user/<int:user_id>/', views.edit_user , name='edit_user'),
    # path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    # path('add_user/',views.add_user ,name='add_user' ),
       
    
]
