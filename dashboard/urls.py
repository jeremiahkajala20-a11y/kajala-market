from django.urls import path
from . import views

urlpatterns = [
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/sellers/', views.admin_sellers, name='admin_sellers'),
    path('admin/sellers/approve/<int:user_id>/', views.approve_seller, name='approve_seller'),
    path('admin/products/', views.admin_products, name='admin_products'),
    path('admin/products/approve/<int:product_id>/', views.approve_product, name='approve_product'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
]