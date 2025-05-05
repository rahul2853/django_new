from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Cart functionality
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:food_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:food_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:food_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    
    
    # payments
     path('payment/create/', views.create_payment, name='create_payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('payment/cancel/', views.cancel_payment, name='cancel_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failed, name='payment_failure'),
    
    path('create_payment/', views.create_payment, name='create_payment'),
    path('execute_payment/', views.execute_payment, name='execute_payment'),
]
