from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'stock', 'is_approved', 'is_featured', 'views')
    list_filter = ('is_approved', 'is_featured', 'category')
    search_fields = ('name', 'seller__username', 'seller__business_name')
    list_editable = ('is_approved', 'is_featured', 'price')
    readonly_fields = ('views', 'created_at')