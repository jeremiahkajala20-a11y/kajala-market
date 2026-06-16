from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from accounts.models import User
from products.models import Product
from orders.models import Order, OrderItem
from utils.notifications import send_sms_notification, send_whatsapp_notification, send_order_status_update_email

@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('home')
    
    if not request.user.is_approved:
        messages.warning(request, 'Your account is pending admin approval.')
        return redirect('home')
    
    products = Product.objects.filter(seller=request.user)
    total_products = products.count()
    pending_products = products.filter(is_approved=False).count()
    
    order_items = OrderItem.objects.filter(product__seller=request.user)
    total_orders = order_items.values('order').distinct().count()
    total_sales = 0
    for item in order_items:
        total_sales += float(item.price) * item.quantity
    
    # Get recent orders for this seller
    recent_orders = []
    for item in order_items.select_related('order', 'product').order_by('-order__created_at')[:10]:
        recent_orders.append({
            'order_number': item.order.order_number,
            'product_name': item.product.name,
            'quantity': item.quantity,
            'total': item.get_total(),
            'status': item.order.status,
            'payment_option': item.order.get_payment_option_display(),
            'created_at': item.order.created_at,
        })
    
    context = {
        'total_products': total_products,
        'pending_products': pending_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/seller_dashboard.html', context)

@staff_member_required
def admin_dashboard(request):
    total_sellers = User.objects.filter(role='seller').count()
    pending_sellers = User.objects.filter(role='seller', is_approved=False).count()
    total_buyers = User.objects.filter(role='buyer').count()
    total_products = Product.objects.count()
    pending_products = Product.objects.filter(is_approved=False).count()
    total_orders = Order.objects.count()
    prepaid_orders = Order.objects.filter(payment_option='prepaid').count()
    cod_orders = Order.objects.filter(payment_option='cod').count()
    
    context = {
        'total_sellers': total_sellers,
        'pending_sellers': pending_sellers,
        'total_buyers': total_buyers,
        'total_products': total_products,
        'pending_products': pending_products,
        'total_orders': total_orders,
        'prepaid_orders': prepaid_orders,
        'cod_orders': cod_orders,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@staff_member_required
def admin_sellers(request):
    sellers = User.objects.filter(role='seller')
    pending_filter = request.GET.get('pending')
    if pending_filter:
        sellers = sellers.filter(is_approved=False)
    return render(request, 'dashboard/admin_sellers.html', {'sellers': sellers})

@staff_member_required
def approve_seller(request, user_id):
    seller = get_object_or_404(User, id=user_id, role='seller')
    seller.is_approved = True
    seller.save()
    messages.success(request, f'{seller.username} approved as seller!')
    return redirect('admin_sellers')

@staff_member_required
def admin_products(request):
    products = Product.objects.all().order_by('-created_at')
    pending_filter = request.GET.get('pending')
    if pending_filter:
        products = products.filter(is_approved=False)
    return render(request, 'dashboard/admin_products.html', {'products': products})

@staff_member_required
def approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_approved = True
    product.save()
    messages.success(request, f'{product.name} approved!')
    return redirect('admin_products')

@staff_member_required
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/admin_orders.html', {'orders': orders})

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f'Order {order.order_number} status updated to {new_status}')
    return redirect('admin_orders')

@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        old_status = order.status
        order.status = new_status
        order.save()
        
        # Send notifications when status changes
        if new_status != old_status:
            # Send email to buyer
            send_order_status_update_email(order, order.buyer, new_status)
            
            # Send SMS to buyer
            if new_status == 'shipped':
                from utils.notifications import send_sms_order_shipped
                send_sms_order_shipped(order, order.phone_number)
            elif new_status == 'delivered':
                from utils.notifications import send_sms_notification
                msg = f"Kajala Market: Your order #{order.order_number} has been delivered! Thank you for shopping with us!"
                send_sms_notification(order.phone_number, msg)
            
            # Send WhatsApp to buyer (if phone number available)
            if order.phone_number:
                from utils.notifications import send_whatsapp_notification
                whatsapp_msg = f"🛍️ *Kajala Market*\n\nYour order #{order.order_number} status has been updated to: *{new_status.upper()}*\n\nTrack: http://127.0.0.1:8000/orders/track/{order.order_number}/"
                send_whatsapp_notification(order.phone_number, whatsapp_msg)
            
            # Notify admin
            from utils.notifications import send_sms_to_admin, send_whatsapp_to_admin
            admin_msg = f"Order #{order.order_number} status changed from {old_status} to {new_status}"
            send_sms_to_admin(admin_msg)
            send_whatsapp_to_admin(admin_msg)
        
        messages.success(request, f'Order {order.order_number} status updated to {new_status}')
    return redirect('admin_orders')