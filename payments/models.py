from django.db import models
from django.conf import settings


class Payment(models.Model):
	PAYMENT_METHODS = [
		('stripe', 'Stripe'),
		('paypal', 'PayPal'),
		('card', 'Credit Card'),
		('cash', 'Cash on Delivery'),
	]

	STATUS_CHOICES = [
		('pending', 'Pending'),
		('completed', 'Completed'),
		('failed', 'Failed'),
		('refunded', 'Refunded'),
	]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
	amount = models.DecimalField(max_digits=10, decimal_places=2)
	payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
	stripe_client_secret = models.CharField(max_length=255, null=True, blank=True)
	transaction_id = models.CharField(max_length=255, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Payment #{self.id} - {self.get_payment_method_display()} - {self.status}"


class PaymentHistory(models.Model):
	payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='history')
	previous_status = models.CharField(max_length=20)
	new_status = models.CharField(max_length=20)
	notes = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"History for Payment #{self.payment_id} at {self.timestamp}"
