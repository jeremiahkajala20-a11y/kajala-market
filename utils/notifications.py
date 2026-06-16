import requests
import urllib.parse
from django.conf import settings
from django.core.mail import send_mail

# ==================== EMAIL NOTIFICATIONS ====================
def send_email_notification(to_email, subject, message, html_message=None):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_order_confirmation_email(order, buyer):
    subject = f"Order Confirmation - #{order.order_number} - Kajala Market"
    created_date = order.created_at.strftime('%B %d, %Y %H:%M')
    
    message = f"""
Hello {buyer.get_full_name() or buyer.username},

Thank you for shopping at Kajala Market!

Order Details:
-----------------
Order Number: {order.order_number}
Order Date: {created_date}
Total Amount: Tsh {order.total_amount:,.0f}
Payment Method: {order.get_payment_option_display()}

Delivery Address: {order.delivery_address}, {order.city}
Phone: {order.phone_number}

Kajala Market Team
0748755636 | jeremiahkajala20@gmail.com
"""
    return send_email_notification(buyer.email, subject, message)

def send_new_order_to_seller_email(order, seller):
    subject = f"New Order Received - #{order.order_number} - Kajala Market"
    created_date = order.created_at.strftime('%B %d, %Y %H:%M')
    
    message = f"""
Hello {seller.business_name or seller.username},

New order received!

Order: #{order.order_number}
Date: {created_date}
Buyer: {order.buyer_name}
Amount: Tsh {order.total_amount:,.0f}
Payment: {order.get_payment_option_display()}

Login: http://127.0.0.1:8000/dashboard/seller/
"""
    return send_email_notification(seller.email, subject, message)

# ==================== WHATSAPP NOTIFICATIONS ====================
def send_whatsapp_notification(phone_number, message):
    if not phone_number:
        print("No phone number for WhatsApp")
        return None
    phone_number = str(phone_number).strip()
    if phone_number.startswith('0'):
        phone_number = '255' + phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{phone_number}?text={encoded}"

def send_whatsapp_order_confirmation(order, buyer_phone, buyer_name):
    if not buyer_phone:
        return None
    message = f"🛒 Kajala Market: Order #{order.order_number} received! Total: Tsh {order.total_amount:,.0f}"
    return send_whatsapp_notification(buyer_phone, message)

def send_whatsapp_to_admin(message):
    return send_whatsapp_notification(settings.ADMIN_PHONE, message)

# ==================== SMS NOTIFICATIONS ====================
def send_sms_notification(phone_number, message):
    if not phone_number:
        print("No phone number for SMS")
        return False
    phone_number = str(phone_number).strip()
    if phone_number.startswith('0'):
        phone_number = '255' + phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]
    print(f"[SMS to {phone_number}]: {message}")
    return True

def send_sms_order_confirmation(order, buyer_phone, buyer_name):
    if not buyer_phone:
        return False
    message = f"Kajala Market: Order #{order.order_number} received! Total: Tsh {order.total_amount:,.0f}"
    return send_sms_notification(buyer_phone, message)

def send_sms_to_admin(message):
    return send_sms_notification(settings.ADMIN_PHONE, message)

# ==================== UNIFIED FUNCTION ====================
def send_all_notifications(order, buyer, seller, notification_type='order_placed'):
    results = {'email': False, 'whatsapp': False, 'sms': False}
    
    if notification_type == 'order_placed':
        results['email'] = send_order_confirmation_email(order, buyer)
        
        if buyer.phone:
            send_whatsapp_order_confirmation(order, buyer.phone, buyer.get_full_name() or buyer.username)
            send_sms_order_confirmation(order, buyer.phone, buyer.get_full_name() or buyer.username)
        
        if seller and seller.email:
            send_new_order_to_seller_email(order, seller)
        
        admin_msg = f"New order #{order.order_number} from {buyer.username}. Amount: Tsh {order.total_amount:,.0f}"
        send_whatsapp_to_admin(admin_msg)
        send_sms_to_admin(admin_msg)
        
    return results

# ==================== ADD MISSING FUNCTIONS ====================

def send_order_status_update_email(order, buyer, status):
    """Send order status update email to buyer"""
    status_messages = {
        'confirmed': 'Your order has been confirmed and is being prepared.',
        'processing': 'Your order is now being processed.',
        'shipped': 'Your order has been shipped and is on the way!',
        'delivered': 'Your order has been delivered. Thank you for shopping with us!',
        'cancelled': 'Your order has been cancelled.'
    }
    message = status_messages.get(status, f'Your order status has been updated to {status}')
    
    subject = f"Order Status Update - #{order.order_number} - {status.upper()}"
    message_full = f"""
Hello {buyer.get_full_name() or buyer.username},

{message}

Order Number: {order.order_number}
Status: {status.upper()}

Track your order: http://127.0.0.1:8000/orders/track/{order.order_number}/

Kajala Market Team
"""
    return send_email_notification(buyer.email, subject, message_full)


def send_whatsapp_order_confirmation(order, buyer_phone, buyer_name):
    """Send order confirmation via WhatsApp"""
    if not buyer_phone:
        return None
    message = f"""🛒 *Kajala Market - Order Confirmation*

Hello {buyer_name},

Thank you for your order!

📦 Order: #{order.order_number}
💰 Total: Tsh {order.total_amount:,.0f}
🚚 Payment: {order.get_payment_option_display()}

We will notify you when your order is shipped.

Questions? Call us: 0748755636

*Kajala Market*"""
    return send_whatsapp_notification(buyer_phone, message)


def send_whatsapp_new_order_to_seller(seller_phone, seller_name, order):
    """Send new order notification to seller via WhatsApp"""
    if not seller_phone:
        return None
    message = f"""🛍️ *NEW ORDER ALERT - Kajala Market*

Hello {seller_name},

You have received a new order!

📦 Order: #{order.order_number}
👤 Buyer: {order.buyer_name}
💰 Amount: Tsh {order.total_amount:,.0f}
💳 Payment: {order.get_payment_option_display()}

Login: http://127.0.0.1:8000/dashboard/seller/

*Kajala Market*"""
    return send_whatsapp_notification(seller_phone, message)


def send_sms_order_shipped(order, buyer_phone):
    """Send order shipped SMS to buyer"""
    if not buyer_phone:
        return False
    message = f"""Kajala Market: Your order #{order.order_number} has been shipped! Expected delivery: 1-3 days. Track: http://127.0.0.1:8000/orders/track/{order.order_number}/"""
    return send_sms_notification(buyer_phone, message)


def send_sms_payment_confirmation(order, buyer_phone):
    """Send payment confirmation SMS to buyer"""
    if not buyer_phone:
        return False
    message = f"""Kajala Market: Payment of Tsh {order.total_amount:,.0f} for order #{order.order_number} confirmed! Thank you!"""
    return send_sms_notification(buyer_phone, message)


def send_sms_new_order_to_seller(seller_phone, order):
    """Send new order notification SMS to seller"""
    if not seller_phone:
        return False
    message = f"""Kajala Market: New order #{order.order_number}! Amount: Tsh {order.total_amount:,.0f}. Login: http://127.0.0.1:8000/dashboard/seller/"""
    return send_sms_notification(seller_phone, message)


def send_sms_order_confirmation(order, buyer_phone, buyer_name):
    """Send order confirmation SMS to buyer"""
    if not buyer_phone:
        return False
    message = f"""Kajala Market: Order #{order.order_number} received! Total: Tsh {order.total_amount:,.0f}. We'll notify you when shipped. Contact: 0748755636"""
    return send_sms_notification(buyer_phone, message)