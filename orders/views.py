from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from cart.models import Cart
from orders.models import Order, OrderItem
from utils.notifications import send_all_notifications, send_sms_to_admin, send_whatsapp_to_admin
import threading

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if cart.items.count() == 0:
        messages.error(request, 'Your cart is empty')
        return redirect('cart_view')
    
    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address')
        city = request.POST.get('city')
        phone_number = request.POST.get('phone_number')
        buyer_name = request.POST.get('buyer_name')
        buyer_email = request.POST.get('buyer_email')
        buyer_message = request.POST.get('buyer_message', '')
        payment_option = request.POST.get('payment_option')
        
        total = cart.get_total()
        
        # Create order
        order = Order.objects.create(
            buyer=request.user,
            total_amount=total,
            delivery_address=delivery_address,
            city=city,
            phone_number=phone_number,
            buyer_name=buyer_name,
            buyer_email=buyer_email,
            buyer_message=buyer_message,
            payment_option=payment_option,
            status='pending'
        )
        
        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
        
        # Clear cart
        cart.items.all().delete()
        
        # Get seller (from first product in order)
        seller = order.items.first().product.seller if order.items.exists() else None
        
        # ============ FIX: Send notifications in BACKGROUND (Async) ============
        def send_notifications_async():
            """Send notifications in background to speed up order placement"""
            try:
                # Send all notifications
                send_all_notifications(order, request.user, seller, 'order_placed')
                
                # Send admin alerts
                admin_alert = f"🛒 NEW ORDER! Order #{order.order_number} | Buyer: {buyer_name} | Amount: Tsh {total:,.0f} | Payment: {payment_option}"
                send_whatsapp_to_admin(admin_alert)
                send_sms_to_admin(admin_alert)
            except Exception as e:
                print(f"Notification error: {e}")
        
        # Start background thread (won't block the response)
        thread = threading.Thread(target=send_notifications_async)
        thread.daemon = True
        thread.start()
        # ====================================================================
        
        messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
        return redirect('order_confirmation', order_id=order.id)
    
    # Get seller information for display
    seller_payment_number = settings.SELLER_PAYMENT_NUMBER
    seller_account_name = settings.SELLER_ACCOUNT_NAME
    seller_bank = settings.SELLER_BANK
    seller_account_number = settings.SELLER_ACCOUNT_NUMBER
    
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'seller_payment_number': seller_payment_number,
        'seller_account_name': seller_account_name,
        'seller_bank': seller_bank,
        'seller_account_number': seller_account_number,
    })


@login_required
def order_confirmation(request, order_id):
    """Order confirmation page after successful checkout"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    seller_payment_number = settings.SELLER_PAYMENT_NUMBER
    seller_account_name = settings.SELLER_ACCOUNT_NAME
    seller_bank = settings.SELLER_BANK
    seller_account_number = settings.SELLER_ACCOUNT_NUMBER
    
    return render(request, 'orders/order_confirmation.html', {
        'order': order,
        'seller_payment_number': seller_payment_number,
        'seller_account_name': seller_account_name,
        'seller_bank': seller_bank,
        'seller_account_number': seller_account_number,
    })


@login_required
def my_orders(request):
    """List all orders for the logged-in buyer"""
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_number):
    """Show detailed information for a specific order"""
    order = get_object_or_404(Order, order_number=order_number, buyer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})