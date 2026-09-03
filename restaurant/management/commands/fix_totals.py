"""
Management command to repair orders where total_amount / subtotal is 0
but the order has items. Run once after deploying the fix:

    python manage.py fix_totals
"""
from django.core.management.base import BaseCommand
from restaurant.models import Order
from decimal import Decimal, ROUND_HALF_UP


class Command(BaseCommand):
    help = 'Recalculate and save subtotal/discount_amount/total_amount for all orders'

    def handle(self, *args, **options):
        orders = Order.objects.prefetch_related('items').all()
        fixed = 0
        for order in orders:
            items = list(order.items.all())
            if not items:
                continue
            subtotal = sum((i.unit_price * i.quantity for i in items), Decimal('0'))
            parcel = order.parcel_charge or Decimal('0')
            if order.discount_is_flat:
                # Flat cart offer — there is no percentage to derive it from.
                disc = min(order.discount_amount or Decimal('0'), subtotal)
            elif order.discount_percent:
                disc = (subtotal * order.discount_percent / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
            else:
                disc = Decimal('0')
            total = max(Decimal('0'), subtotal + parcel - disc)
            if (order.subtotal != subtotal or order.total_amount != total
                    or order.discount_amount != disc):
                Order.objects.filter(pk=order.pk).update(
                    subtotal=subtotal,
                    discount_amount=disc,
                    total_amount=total,
                )
                fixed += 1
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed} orders out of {orders.count()} total.'))
