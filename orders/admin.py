from django.contrib import admin
from .models import Order, OrderItem, Rating, Wishlist, Coupon, SellerRating, RecentlyViewed, FlashSale, BlogPost

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'final_amount', 'status', 'payment_option', 'created_at')
    list_filter = ('status', 'payment_option', 'created_at')
    search_fields = ('order_number', 'buyer__username', 'buyer_email')
    list_editable = ('status',)
    inlines = [OrderItemInline]

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('buyer__username', 'product__name')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'product', 'added_at')
    list_filter = ('added_at',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'minimum_order', 'valid_to', 'is_valid', 'used_count')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to')
    search_fields = ('code',)

@admin.register(SellerRating)
class SellerRatingAdmin(admin.ModelAdmin):
    list_display = ('buyer', 'seller', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('title', 'discount_percentage', 'start_time', 'end_time', 'is_running', 'is_active')
    list_filter = ('is_active', 'start_time', 'end_time')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'views', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('created_at',)
    search_fields = ('title', 'content')