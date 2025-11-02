from celery import shared_task
from django.core.mail import send_mail
from .models import Order
from django.conf import settings


@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return None

    recipient = getattr(order.user.user, 'email', None)

    subject = f"Order Confirmation - {order.order_number}"
    message = (f"Thank you for your order {order.user.get_full_name()}. "
               f"Order number: {order.order_number}. "
               f"Total: {order.total_amount}")

    if recipient:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    return True


@shared_task
def update_order_status(order_id=None):
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if order.status == "pending":
                order.status = "processing"
                order.save()
        except Order.DoesNotExist:
            return
    else:
        Order.objects.filter(status="pending").update(status="processing")


def handle_new_order(order):
    send_order_confirmation_email.delay(order.id)
    update_order_status.apply_async((order.id,), countdown=300) #5 წუთში შეიცვალოს სტატუსი