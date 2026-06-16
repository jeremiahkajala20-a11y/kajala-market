from django.db import models
from accounts.models import User
from products.models import Product
import random
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_CHOICES = (
        ('prepaid', 'Pay Before Delivery (M-Pesa/Airtel/Tigo/CRDB/NMB)'),
        ('cod', 'Pay After Delivery (Cash on Delivery)'),
    )
    
    order_number = models.CharField(max_length=20, unique=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_option = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='prepaid')
    delivery_address = models.TextField()
    city = models.CharField(max_length=100, default='Dodoma')
    phone_number = models.CharField(max_length=15)
    buyer_name = models.CharField(max_length=200)
    buyer_email = models.EmailField()
    buyer_message = models.TextField(blank=True, null=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"KJ{random.randint(100000, 999999)}"
        self.final_amount = self.total_amount - self.discount_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.order_number} - {self.buyer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.price * self.quantity

# ==================== RATING & REVIEW ====================
class Rating(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)
    images = models.ImageField(upload_to='reviews/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('buyer', 'product')

    def __str__(self):
        return f"{self.buyer.username} rated {self.product.name} - {self.rating}★"

# ==================== WISHLIST ====================
class Wishlist(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'product')

    def __str__(self):
        return f"{self.buyer.username} - {self.product.name}"

# ==================== COUPON / DISCOUNT CODE ====================
class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('percentage', 'Percentage (%)'),
        ('fixed', 'Fixed Amount (Tsh)'),
    )
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        return (self.is_active and 
                self.valid_from <= timezone.now() <= self.valid_to and 
                self.used_count < self.usage_limit)

    def calculate_discount(self, amount):
        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / 100)
            if self.max_discount:
                discount = min(discount, self.max_discount)
        else:
            discount = self.discount_value
        return min(discount, amount)

# ==================== SELLER RATING ====================
class SellerRating(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_ratings')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received', limit_choices_to={'role': 'seller'})
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('buyer', 'seller')

    def __str__(self):
        return f"{self.buyer.username} rated {self.seller.username} - {self.rating}★"

# ==================== RECENTLY VIEWED ====================
class RecentlyViewed(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']
        unique_together = ('buyer', 'product')

    def __str__(self):
        return f"{self.buyer.username} viewed {self.product.name}"

# ==================== FLASH SALE ====================
class FlashSale(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    products = models.ManyToManyField(Product, related_name='flash_sales')
    discount_percentage = models.IntegerField(default=10)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def is_running(self):
        from django.utils import timezone
        return self.start_time <= timezone.now() <= self.end_time

# ==================== BLOG POST ====================
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField()
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True})
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title