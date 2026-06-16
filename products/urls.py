from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('seller/products/', views.seller_products, name='seller_products'),
    path('seller/add-product/', views.add_product, name='add_product'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('faq/', views.faq_page, name='faq'),
    path('newsletter/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_wishlist, name='add_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_wishlist, name='remove_wishlist'),
    path('rating/add/<int:product_id>/', views.add_rating, name='add_rating'),
    path('coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('flash-sales/', views.flash_sales, name='flash_sales'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('seller/rate/<int:seller_id>/', views.rate_seller, name='rate_seller'),
    path('coupon/remove/', views.remove_coupon, name='remove_coupon'),
]