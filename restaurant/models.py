import uuid

from django.db import models
from django.utils import timezone
import json


class ShopSettings(models.Model):
    shop_name = models.CharField(max_length=200, default="Brothers Cafe")
    location = models.CharField(max_length=200, default="Tirupattur")
    gstin = models.CharField(max_length=50, default="", blank=True, help_text='GSTIN number')
    fssai_number = models.CharField(max_length=50, default="", blank=True, help_text='FSSAI License Number (Food Safety)')
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='shop/', blank=True, null=True)
    upi_qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True, 
                                     help_text="Upload QR code image for online payments")
    upi_id = models.CharField(max_length=100, blank=True, help_text="e.g. brotherscafe@upi")
    default_discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                    help_text="Default discount % shown on bills")
    default_parcel_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                                 help_text="Default parcel charge per item for takeaway orders (overridden by item-level charge)")
    show_water_bottle_in_cart = models.BooleanField(default=True, help_text="Show Water Bottle quick-add in customer cart")
    water_bottle_item = models.ForeignKey('MenuItem', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='+', limit_choices_to={'is_water_bottle': True},
        help_text="Which water bottle the cart quick-add uses. Only items marked as a water bottle can be chosen.")
    water_bottle_cart_price = models.DecimalField(max_digits=6, decimal_places=2, default=0, blank=True,
                                                   help_text="Override water bottle price shown in cart (0 = use menu item price)")
    class Meta:
        verbose_name = "Shop Settings"
        verbose_name_plural = "Shop Settings"

    def __str__(self):
        return self.shop_name


class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
    ]
    number = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=50, help_text="e.g. Table 1, VIP Table")
    capacity = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField(blank=True, help_text="Optional: location description like 'Near window'")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"{self.name} (#{self.number})"

    @property
    def current_order(self):
        return self.orders.filter(status__in=['pending', 'accepted', 'preparing', 'ready']).first()


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji icon e.g. 🍕")
    image = models.ImageField(upload_to='category_images/', blank=True, null=True, help_text='Category banner image shown on menu page')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('beverage', 'Beverage'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='veg')
    is_available = models.BooleanField(default=True, help_text='(Deprecated: use Dine In Active / Takeaway Active below)')
    is_available_dine_in = models.BooleanField(default=True, help_text='Item available for dine-in orders')
    is_available_takeaway = models.BooleanField(default=True, help_text='Item available for takeaway orders')
    is_featured = models.BooleanField(default=False)
    preparation_time = models.PositiveIntegerField(default=15, help_text="Minutes")
    order = models.PositiveIntegerField(default=0)
    is_water_bottle = models.BooleanField(default=False,
        help_text="Mark this as a water bottle so it can be used for the cart quick-add card")
    parcel_charge = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                          help_text='Extra charge for takeaway parcel packaging')

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

    def is_available_for_order_type(self, order_type):
        """Check if item is available for the given order type ('dine_in' or 'takeaway')"""
        if order_type == 'takeaway':
            return self.is_available_takeaway
        else:  # dine_in
            return self.is_available_dine_in


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS = [
        ('unpaid', 'Unpaid'),
        ('online_pending', 'Online Payment Pending'),
        ('paid_online', 'Paid Online'),
        ('paid_offline', 'Paid Offline'),
    ]

    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, related_name='orders')
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    special_instructions = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    payment_method = models.CharField(max_length=20, blank=True)  # 'online' or 'offline'
    cash_received = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    order_type = models.CharField(max_length=20, default='dine_in',
        choices=[('dine_in', 'Dine In'), ('takeaway', 'Takeaway')])
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    parcel_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Total parcel charge for takeaway orders')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    access_token = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True,
        help_text='Unguessable key so a bill can be shared by link without exposing every other order')
    discount_is_flat = models.BooleanField(default=False,
        help_text='True when discount_amount came from a flat cart offer, not a percentage')
    offer_title = models.CharField(max_length=200, blank=True, default='',
        help_text='Name of the cart offer / combo offer applied to this order')
    staff_notified = models.BooleanField(default=False)
    parent_order = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='reorders', help_text='If this is a reorder, points to the original order')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer_name} - {self.table}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"BC{timezone.now().strftime('%Y%m%d')}{random.randint(1000,9999)}"
        # Recalculate totals only if NOT called right after an explicit .update()
        # Skip_recalc kwarg lets views bypass this when they have already called calculate_totals()
        if self.pk and not kwargs.pop('skip_recalc', False):
            self.calculate_totals()
        super().save(*args, **kwargs)
        # Update table status
        if self.status in ['pending', 'accepted', 'preparing', 'ready']:
            if self.table:
                Table.objects.filter(pk=self.table.pk).update(status='occupied')
        elif self.status in ['completed', 'cancelled']:
            if self.table:
                # Only free if no other active orders
                active = Order.objects.filter(
                    table=self.table,
                    status__in=['pending', 'accepted', 'preparing', 'ready']
                ).exclude(pk=self.pk).exists()
                if not active:
                    Table.objects.filter(pk=self.table.pk).update(status='available')

    def calculate_totals(self):
        """Recompute subtotal / discount / total.

        Two rules that were previously broken and silently corrupted bills:
          * parcel_charge MUST be part of total_amount, otherwise every
            takeaway order loses its parcel money on the next save().
          * a flat cart-offer discount has no percentage behind it, so it must
            be preserved rather than reset to 0.00.
        """
        from decimal import Decimal, ROUND_HALF_UP
        items = list(self.items.all())
        self.subtotal = sum((item.total_price for item in items), Decimal('0.00'))

        if self.discount_is_flat or (self.offer_title and not self.discount_percent):
            # Flat offer, or an offer whose percentage isn't recorded: keep the
            # rupee amount rather than resetting it, but never exceed the cart.
            self.discount_amount = min(self.discount_amount or Decimal('0.00'), self.subtotal)
        elif self.subtotal and self.discount_percent:
            self.discount_amount = (self.subtotal * self.discount_percent / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.discount_amount = Decimal('0.00')

        self.total_amount = self.subtotal + (self.parcel_charge or Decimal('0.00')) - self.discount_amount
        if self.total_amount < 0:
            self.total_amount = Decimal('0.00')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    # When this line is a combo, `combo` is set and `menu_item` is only a
    # representative row (needed for reporting). Always render `display_name`.
    combo = models.ForeignKey('Combo', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='order_items',
                              help_text='Set when this line is a combo, not a single item')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_free = models.BooleanField(default=False, help_text='Free item granted by a cart offer')
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.display_name}"

    @property
    def display_name(self):
        """Name shown on every bill / status screen / staff card."""
        if self.combo_id and self.combo:
            return self.combo.name
        return self.menu_item.name

    @property
    def is_combo(self):
        return bool(self.combo_id)

    @property
    def combo_components(self):
        """['2x Chicken Hot Wings', '1x Pepsi'] — shown as sub-lines on bills."""
        if not self.combo_id or not self.combo:
            return []
        return [f"{ci.quantity}x {ci.menu_item.name}" for ci in self.combo.combo_items.all()]

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)


class Discount(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Festival Offer, Weekend Special")
    percent = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.percent}%"

    class Meta:
        ordering = ['-is_active', 'name']


class CustomerProfile(models.Model):
    """Customer identified by phone number — created on first login via QR scan."""
    name          = models.CharField(max_length=100)
    phone         = models.CharField(max_length=15, unique=True, db_index=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    last_visit    = models.DateTimeField(auto_now=True)
    visit_count   = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['-last_visit']
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.name} ({self.phone})"

    @property
    def total_orders(self):
        return Order.objects.filter(customer_phone=self.phone, parent_order__isnull=True).count()

    @property
    def total_spent(self):
        from decimal import Decimal
        from django.db.models import Sum
        result = Order.objects.filter(
            customer_phone=self.phone,
            status='completed',
            parent_order__isnull=True
        ).aggregate(total=Sum('total_amount'))['total']
        return result or Decimal('0')


class Combo(models.Model):
    """Staff-defined combo meals shown on the categories page."""
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Short description shown to customers")
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    image       = models.ImageField(upload_to='combo_images/', blank=True, null=True)
    icon        = models.CharField(max_length=50, blank=True, default='🎁', help_text="Emoji icon e.g. 🎁")
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0, help_text="Display order")
    items       = models.ManyToManyField(MenuItem, through='ComboItem', related_name='combos')

    # ── Combo Offer ──────────────────────────────────────────────────────
    # A combo flagged as an offer is managed in its own "Combo Offers" table in
    # the Menu Manager and shown in a highlighted strip at the top of the
    # customer menu, above everything else.
    is_offer    = models.BooleanField(default=False,
                    help_text="Show this as a Combo Offer at the top of the customer menu")
    offer_tag   = models.CharField(max_length=40, blank=True, default='',
                    help_text="Small badge text, e.g. LIMITED TIME")
    valid_from  = models.DateField(null=True, blank=True,
                    help_text="Optional: offer starts on this date")
    valid_to    = models.DateField(null=True, blank=True,
                    help_text="Optional: offer ends after this date")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Combo"
        verbose_name_plural = "Combos"

    def __str__(self):
        return f"{self.name} — ₹{self.price}"

    @property
    def item_count(self):
        return self.combo_items.count()

    @property
    def items_value(self):
        """What the contents would cost bought separately."""
        from decimal import Decimal
        return sum((ci.menu_item.price * ci.quantity for ci in self.combo_items.all()),
                   Decimal('0.00'))

    @property
    def savings(self):
        from decimal import Decimal
        return max(Decimal('0.00'), self.items_value - self.price)

    @property
    def savings_percent(self):
        value = self.items_value
        if not value:
            return 0
        return int(round((value - self.price) / value * 100))

    @property
    def is_live_offer(self):
        """Active, flagged as an offer, and inside its date window."""
        from django.utils import timezone
        if not (self.is_active and self.is_offer):
            return False
        today = timezone.localdate()   # local date, not UTC
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_to and today > self.valid_to:
            return False
        return True


class ComboItem(models.Model):
    """Through table: links a MenuItem to a Combo with quantity."""
    combo     = models.ForeignKey(Combo, on_delete=models.CASCADE, related_name='combo_items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['menu_item__name']
        verbose_name = "Combo Item"
        verbose_name_plural = "Combo Items"

    def __str__(self):
        return f"{self.quantity}× {self.menu_item.name}"


class PosDraft(models.Model):
    """POS saved draft orders - stored in DB, exportable to Excel."""
    draft_number  = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=100, blank=True, default='Walk-in')
    customer_phone= models.CharField(max_length=15,  blank=True, default='')
    table_name    = models.CharField(max_length=50,  blank=True, default='Takeaway')
    items_json    = models.TextField(help_text='JSON list of items')
    subtotal      = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_pct  = models.DecimalField(max_digits=5,  decimal_places=2, default=0)
    total_amount  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    note          = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    is_deleted    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.draft_number} - {self.table_name} - ₹{self.total_amount}"


class DateWindowMixin(models.Model):
    """Shared 'runs from / runs until' window for anything promotional."""
    valid_from = models.DateField(null=True, blank=True,
                    help_text="Optional: starts on this date. Blank = runs immediately.")
    valid_to = models.DateField(null=True, blank=True,
                    help_text="Optional: ends after this date. Blank = runs indefinitely.")

    class Meta:
        abstract = True

    @property
    def is_in_window(self):
        from django.utils import timezone
        # Use local date (respects TIME_ZONE setting), not UTC date.
        # At midnight IST (UTC+5:30) the UTC date is still yesterday, which
        # made offers starting "today" appear to not have started yet.
        today = timezone.localdate()
        if self.valid_from and today < self.valid_from:
            return False
        if self.valid_to and today > self.valid_to:
            return False
        return True

    @property
    def window_label(self):
        if not self.valid_from and not self.valid_to:
            return 'Always'
        f = self.valid_from.strftime('%d %b') if self.valid_from else '—'
        t = self.valid_to.strftime('%d %b') if self.valid_to else '—'
        return f'{f} → {t}'


class OfferBanner(DateWindowMixin):
    """Promotional offer banners managed in Menu Manager — shown to customers on the menu page."""
    OFFER_TYPES = [
        ('percent', '% OFF'),
        ('flat', 'Flat ₹ OFF'),
        ('bogo', 'Buy 1 Get 1 Free'),
    ]
    title       = models.CharField(max_length=200, help_text="e.g. Weekend Special")
    subtitle    = models.CharField(max_length=250, blank=True, help_text="Short line shown under the title")
    offer_type  = models.CharField(max_length=10, choices=OFFER_TYPES, default='percent')
    off_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="% OFF (for percent type)")
    flat_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Flat ₹ OFF (for flat type)")
    emoji       = models.CharField(max_length=10, blank=True, default='🎉')
    bg_color    = models.CharField(max_length=20, default='#e74c3c', help_text="Banner colour (hex)")
    image_url   = models.URLField(blank=True, default='', help_text="Banner image URL (optional)")
    image       = models.ImageField(upload_to='offer_banners/', blank=True, null=True, help_text="Upload banner image")
    menu_items  = models.ManyToManyField('MenuItem', blank=True, help_text="Linked menu items for this offer")
    is_active   = models.BooleanField(default=True)
    order       = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Offer Banner"
        verbose_name_plural = "Offer Banners"

    def __str__(self):
        if self.offer_type == 'bogo':
            return f"{self.title} — Buy 1 Get 1"
        elif self.offer_type == 'flat':
            return f"{self.title} — ₹{self.flat_amount} OFF"
        return f"{self.title} — {self.off_percent}% OFF"

    @property
    def offer_label(self):
        if self.offer_type == 'bogo':
            return '1+1 FREE'
        elif self.offer_type == 'flat':
            return f'Flat ₹{int(self.flat_amount)} OFF'
        return f'{int(self.off_percent)}% OFF'

    @property
    def banner_image_url(self):
        """Return the best available image URL (uploaded file or fallback URL)."""
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        return self.image_url or ''


class CartOffer(DateWindowMixin):
    """Conditional cart-level offers shown to customers in the cart page.
    Examples: Spend ₹600 → 20% off | Spend ₹500 → free Rose Milk"""
    REWARD_TYPES = [
        ('percent', '% Discount'),
        ('flat', 'Flat ₹ Discount'),
        ('free_item', 'Free Item'),
    ]
    title           = models.CharField(max_length=200, help_text="e.g. Mega Saver Deal")
    subtitle        = models.CharField(max_length=250, blank=True)
    min_cart_value  = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Minimum cart total to unlock this offer")
    reward_type     = models.CharField(max_length=20, choices=REWARD_TYPES, default='percent')
    percent_off     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    flat_off        = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    free_item       = models.ForeignKey('MenuItem', null=True, blank=True, on_delete=models.SET_NULL, related_name='cart_offers')
    emoji           = models.CharField(max_length=10, default='🎁')
    is_active       = models.BooleanField(default=True)
    order           = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['min_cart_value', 'order']
        verbose_name = "Cart Offer"
        verbose_name_plural = "Cart Offers"

    def __str__(self):
        return f"{self.title} (≥₹{self.min_cart_value})"

    @property
    def reward_label(self):
        if self.reward_type == 'percent':
            return f'{int(self.percent_off)}% OFF'
        elif self.reward_type == 'flat':
            return f'Flat ₹{int(self.flat_off)} OFF'
        elif self.reward_type == 'free_item' and self.free_item:
            return f'Free {self.free_item.name}'
        return 'Special Offer'
