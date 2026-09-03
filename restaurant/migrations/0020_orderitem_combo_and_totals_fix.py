"""Link OrderItem rows to the Combo they came from, mark free items, and
repair every existing order whose total lost its parcel charge or its flat
cart-offer discount.
"""
from decimal import Decimal
import re

from django.db import migrations, models
import django.db.models.deletion


COMBO_NOTE_RE = re.compile(r'\U0001F381?\s*Combo:\s*(.+?)\s*$')


def backfill(apps, schema_editor):
    Order = apps.get_model('restaurant', 'Order')
    OrderItem = apps.get_model('restaurant', 'OrderItem')
    Combo = apps.get_model('restaurant', 'Combo')

    combos = {c.name.strip().lower(): c for c in Combo.objects.all()}

    # 1. Attach combos to historical order lines using the note they wrote.
    for oi in OrderItem.objects.exclude(notes='').iterator(chunk_size=200):
        m = COMBO_NOTE_RE.search(oi.notes or '')
        if not m:
            continue
        combo = combos.get(m.group(1).strip().lower())
        if combo:
            OrderItem.objects.filter(pk=oi.pk).update(combo=combo)

    # 2. Mark zero-priced lines as free-offer items.
    OrderItem.objects.filter(unit_price=0).update(is_free=True)

    # 3. Repair totals: parcel charge was dropped and flat discounts erased.
    for order in Order.objects.prefetch_related('items').iterator(chunk_size=200):
        items = list(order.items.all())
        if not items:
            continue
        subtotal = sum((i.unit_price * i.quantity for i in items), Decimal('0.00'))
        parcel = order.parcel_charge or Decimal('0.00')
        discount = order.discount_amount or Decimal('0.00')

        # A discount with no percentage behind it must have been a flat offer.
        is_flat = bool(discount > 0 and not order.discount_percent)
        if order.discount_percent:
            discount = (subtotal * order.discount_percent / Decimal('100')).quantize(Decimal('0.01'))
        discount = min(discount, subtotal)

        total = subtotal + parcel - discount
        if total < 0:
            total = Decimal('0.00')

        Order.objects.filter(pk=order.pk).update(
            subtotal=subtotal,
            discount_amount=discount,
            discount_is_flat=is_flat,
            total_amount=total,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0019_shopsettings_waterbottle'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='combo',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='order_items', to='restaurant.combo',
                help_text='Set when this line is a combo, not a single item'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='is_free',
            field=models.BooleanField(default=False, help_text='Free item granted by a cart offer'),
        ),
        migrations.AddField(
            model_name='order',
            name='discount_is_flat',
            field=models.BooleanField(
                default=False,
                help_text='True when discount_amount came from a flat cart offer, not a percentage'),
        ),
        migrations.AddField(
            model_name='order',
            name='offer_title',
            field=models.CharField(
                blank=True, default='', max_length=200,
                help_text='Name of the cart offer / combo offer applied to this order'),
        ),
        migrations.RunPython(backfill, noop),
    ]
