from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.utils import timezone  # ADD THIS LINE
from .models import Product, Category
from .forms import ProductForm

def home(request):
    featured_products = Product.objects.filter(is_approved=True, is_featured=True)[:8]
    new_products = Product.objects.filter(is_approved=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories
    })

def product_list(request):
    products = Product.objects.filter(is_approved=True)
    categories = Category.objects.all()
    
    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    sort = request.GET.get('sort')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')
    
    return render(request, 'products/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_approved=True)
    product.views += 1
    product.save()
    related_products = Product.objects.filter(category=product.category, is_approved=True).exclude(id=product.id)[:4]
    return render(request, 'products/product_detail.html', {'product': product, 'related_products': related_products})

@login_required
def seller_products(request):
    if request.user.role != 'seller':
        return redirect('home')
    products = Product.objects.filter(seller=request.user)
    return render(request, 'products/seller_products.html', {'products': products})

@login_required
def add_product(request):
    if request.user.role != 'seller' or not request.user.is_approved:
        messages.error(request, 'You need to be an approved seller')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, 'Product submitted for approval!')
            return redirect('seller_products')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})

def about_page(request):
    return render(request, 'pages/about.html')

def contact_page(request):
    return render(request, 'pages/contact.html')

def faq_page(request):
    return render(request, 'pages/faq.html')

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, f'Thank you for subscribing! You will receive updates at {email}')
    return redirect('home')

def contact_submit(request):
    if request.method == 'POST':
        from django.core.mail import send_mail
        from django.conf import settings
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            send_mail(
                f'Contact Form: {subject} from {name}',
                f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{message}",
                settings.ADMIN_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=True,
            )
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
        except:
            messages.success(request, 'Message received! We will contact you soon.')
        return redirect('contact')
    return redirect('contact')

# ==================== RATING & REVIEW ====================
from orders.models import Rating, Wishlist, Coupon, RecentlyViewed, FlashSale, BlogPost, SellerRating

def add_rating(request, product_id):
    if request.method == 'POST' and request.user.is_authenticated:
        product = get_object_or_404(Product, id=product_id)
        rating = int(request.POST.get('rating'))
        review = request.POST.get('review', '')
        
        rating_obj, created = Rating.objects.update_or_create(
            buyer=request.user,
            product=product,
            defaults={'rating': rating, 'review': review}
        )
        
        # Update product average rating
        avg_rating = Rating.objects.filter(product=product).aggregate(models.Avg('rating'))['rating__avg'] or 0
        product.avg_rating = avg_rating
        product.save()
        
        messages.success(request, 'Thank you for your review!')
    return redirect('product_detail', slug=product.slug)

# ==================== WISHLIST ====================
@login_required
def wishlist_view(request):
    wishlist = Wishlist.objects.filter(buyer=request.user).select_related('product')
    return render(request, 'orders/wishlist.html', {'wishlist': wishlist})

@login_required
def add_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(buyer=request.user, product=product)
    if created:
        messages.success(request, f'{product.name} added to wishlist!')
    else:
        messages.info(request, f'{product.name} is already in your wishlist')
    return redirect('product_detail', slug=product.slug)

@login_required
def remove_wishlist(request, product_id):
    Wishlist.objects.filter(buyer=request.user, product_id=product_id).delete()
    messages.success(request, 'Item removed from wishlist')
    return redirect('wishlist')

# ==================== RECENTLY VIEWED ====================
def track_recently_viewed(request, product):
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            buyer=request.user,
            product=product,
            defaults={'viewed_at': timezone.now()}
        )
        # Keep only last 10 items
        recent = RecentlyViewed.objects.filter(buyer=request.user)
        if recent.count() > 10:
            recent.last().delete()

# Update product_detail view to track recently viewed
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_approved=True)
    product.views += 1
    product.save()
    
    # Track recently viewed
    track_recently_viewed(request, product)
    
    # Get recently viewed products
    recently_viewed = []
    if request.user.is_authenticated:
        recently_viewed = RecentlyViewed.objects.filter(
            buyer=request.user
        ).exclude(product=product)[:6]
    
    related_products = Product.objects.filter(category=product.category, is_approved=True).exclude(id=product.id)[:4]
    in_wishlist = Wishlist.objects.filter(buyer=request.user, product=product).exists() if request.user.is_authenticated else False
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'recently_viewed': recently_viewed,
        'in_wishlist': in_wishlist
    })

# ==================== COUPON ====================
def apply_coupon(request):
    if request.method == 'POST':
        from cart.models import Cart
        code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=code, is_active=True)
            from django.utils import timezone
            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                # Get cart total
                cart, created = Cart.objects.get_or_create(user=request.user)
                total = cart.get_total()
                
                # Check minimum order
                if total >= coupon.minimum_order:
                    # Calculate discount
                    discount = coupon.calculate_discount(total)
                    
                    # Store in session
                    request.session['coupon_code'] = code
                    request.session['discount_amount'] = float(discount)
                    
                    messages.success(request, f'Coupon {code} applied! You saved Tsh {discount:,.0f}')
                else:
                    messages.error(request, f'Minimum order of Tsh {coupon.minimum_order:,.0f} required')
            else:
                messages.error(request, 'Coupon has expired')
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code')
    return redirect('cart_view')

# ==================== FLASH SALES ====================
def flash_sales(request):
    now = timezone.now()
    active_sales = FlashSale.objects.filter(is_active=True, start_time__lte=now, end_time__gte=now)
    return render(request, 'products/flash_sales.html', {'flash_sales': active_sales})

# ==================== BLOG ====================
def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    post.views += 1
    post.save()
    return render(request, 'blog/blog_detail.html', {'post': post})

# ==================== SELLER RATING ====================
def rate_seller(request, seller_id):
    if request.method == 'POST' and request.user.is_authenticated:
        seller = get_object_or_404(User, id=seller_id, role='seller')
        rating = int(request.POST.get('rating'))
        review = request.POST.get('review', '')
        
        SellerRating.objects.update_or_create(
            buyer=request.user,
            seller=seller,
            defaults={'rating': rating, 'review': review}
        )
        
        # Update seller average rating
        avg_rating = SellerRating.objects.filter(seller=seller).aggregate(models.Avg('rating'))['rating__avg'] or 0
        seller.avg_rating = avg_rating
        seller.save()
        
        messages.success(request, 'Thank you for rating the seller!')
    return redirect('product_list')

def remove_coupon(request):
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'discount_amount' in request.session:
        del request.session['discount_amount']
    messages.success(request, 'Coupon removed successfully!')
    return redirect('cart_view')