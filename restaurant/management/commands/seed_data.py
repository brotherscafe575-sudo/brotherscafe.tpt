from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from restaurant.models import (
    ShopSettings, Table, Category, MenuItem, Discount, Combo, ComboItem
)


class Command(BaseCommand):
    help = 'Seeds the database with the real Brothers Cafe menu and combo offers'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding Brothers Cafe database...')

        # ── Shop Settings ───────────────────────────────────────────────
        shop, _ = ShopSettings.objects.get_or_create(id=1, defaults={
            'shop_name': 'Brothers Cafe',
            'location': 'Tirupattur',
            'gstin': '23278537256752',
            'phone': '+91 98765 43210',
            'address': '123 Main Street, Tirupattur, Tamil Nadu - 635601',
            'upi_id': 'brotherscafe@upi',
            'default_discount_percent': 0,
            'default_parcel_charge': 5,
        })
        # Force the parcel charge to ₹5 even if ShopSettings already existed
        # from a previous seed run - this is a deliberate app-wide default.
        if shop.default_parcel_charge != 5:
            shop.default_parcel_charge = 5
            shop.save(update_fields=['default_parcel_charge'])
        self.stdout.write(self.style.SUCCESS('✅ Shop settings created (default parcel charge: ₹5)'))

        # ── Tables ──────────────────────────────────────────────────────
        tables_data = [
            (1, 'Table 1', 4, ''),
            (2, 'Table 2', 4, ''),
            (3, 'Table 3', 4, ''),
            (4, 'Table 4', 4, ''),
        ]
        for num, name, cap, desc in tables_data:
            Table.objects.get_or_create(number=num, defaults={
                'name': name, 'capacity': cap, 'description': desc
            })
        self.stdout.write(self.style.SUCCESS('✅ 4 tables created'))

        # ── Categories (matches the printed menu board order) ──────────
        cats = [
            ('Hot Drinks',      '☕', 1),
            ('Cool Drinks',     '🧊', 2),
            ('Milk Shakes',     '🥤', 3),
            ('Mojito',          '🍃', 4),
            ('Falooda',         '🍧', 5),
            ('Waffles',         '🧇', 6),
            ('Brownie',         '🍫', 7),
            ('Sundae',          '🍨', 8),
            ('Ice-Cream',       '🍦', 9),
            ('Bun',             '🥐', 10),
            ('Bread Omelette',  '🍳', 11),
            ('Sandwich',        '🥪', 12),
            ('Pizza',           '🍕', 13),
            ('Burger',          '🍔', 14),
            ('Wrap',            '🌯', 15),
            ('Fried Chicken',   '🍗', 16),
            ('French Fries',    '🍟', 17),
            ('Rice Bowl',       '🍚', 18),
            ('Coca-Cola',       '🥤', 19),
        ]
        cat_objs = {}
        for name, icon, order in cats:
            c, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'order': order})
            cat_objs[name] = c
        self.stdout.write(self.style.SUCCESS(f'✅ {len(cats)} categories created'))

        # ── Menu Items ───────────────────────────────────────────────────
        # (category, name, price, item_type, featured)
        # item_type: 'veg' | 'nonveg' | 'beverage'
        items = [
            # Hot Drinks
            ('Hot Drinks', 'Coffee', 25, 'beverage', True),
            ('Hot Drinks', 'Boost', 30, 'beverage', False),
            ('Hot Drinks', 'Horlicks', 30, 'beverage', False),
            ('Hot Drinks', 'Hot Chocolate', 89, 'beverage', True),

            # Cool Drinks
            ('Cool Drinks', 'Cold Coffee', 89, 'beverage', True),
            ('Cool Drinks', 'Rose Milk', 45, 'beverage', False),
            ('Cool Drinks', 'Rose Milk with Ice Cream', 65, 'beverage', False),

            # Milk Shakes (Mini / Regular -> two items each)
            ('Milk Shakes', 'Vanilla Milkshake (Mini)', 89, 'beverage', False),
            ('Milk Shakes', 'Vanilla Milkshake (Regular)', 119, 'beverage', False),
            ('Milk Shakes', 'Strawberry Milkshake (Mini)', 89, 'beverage', False),
            ('Milk Shakes', 'Strawberry Milkshake (Regular)', 119, 'beverage', False),
            ('Milk Shakes', 'Chocolate Milkshake (Mini)', 99, 'beverage', True),
            ('Milk Shakes', 'Chocolate Milkshake (Regular)', 129, 'beverage', True),
            ('Milk Shakes', 'Butterscotch Milkshake (Mini)', 99, 'beverage', False),
            ('Milk Shakes', 'Butterscotch Milkshake (Regular)', 129, 'beverage', False),
            ('Milk Shakes', 'Mango Milkshake (Mini)', 99, 'beverage', False),
            ('Milk Shakes', 'Mango Milkshake (Regular)', 129, 'beverage', False),
            ('Milk Shakes', 'Oreo Milkshake (Mini)', 109, 'beverage', False),
            ('Milk Shakes', 'Oreo Milkshake (Regular)', 139, 'beverage', False),
            ('Milk Shakes', 'Kit-Kat Milkshake (Mini)', 109, 'beverage', False),
            ('Milk Shakes', 'Kit-Kat Milkshake (Regular)', 139, 'beverage', False),
            ('Milk Shakes', 'Boost Milkshake (Mini)', 109, 'beverage', False),
            ('Milk Shakes', 'Boost Milkshake (Regular)', 139, 'beverage', False),
            ('Milk Shakes', 'Horlicks Milkshake (Mini)', 109, 'beverage', False),
            ('Milk Shakes', 'Horlicks Milkshake (Regular)', 139, 'beverage', False),
            ('Milk Shakes', 'Brownie Milkshake (Mini)', 129, 'beverage', True),
            ('Milk Shakes', 'Brownie Milkshake (Regular)', 169, 'beverage', True),
            ('Milk Shakes', 'Dry Fruits Milkshake (Mini)', 139, 'beverage', False),
            ('Milk Shakes', 'Dry Fruits Milkshake (Regular)', 179, 'beverage', False),

            # Mojito (Mini / Regular)
            ('Mojito', 'Virgin Mojito (Mini)', 59, 'beverage', False),
            ('Mojito', 'Virgin Mojito (Regular)', 89, 'beverage', False),
            ('Mojito', 'Strawberry Mojito (Mini)', 59, 'beverage', False),
            ('Mojito', 'Strawberry Mojito (Regular)', 89, 'beverage', False),
            ('Mojito', 'Blue Curacao Mojito (Mini)', 69, 'beverage', True),
            ('Mojito', 'Blue Curacao Mojito (Regular)', 99, 'beverage', True),
            ('Mojito', 'Green Apple Mojito (Mini)', 69, 'beverage', False),
            ('Mojito', 'Green Apple Mojito (Regular)', 99, 'beverage', False),

            # Falooda
            ('Falooda', 'Classic Falooda', 119, 'veg', True),
            ('Falooda', 'Dry Fruit Falooda', 159, 'veg', False),
            ('Falooda', 'Royal Falooda', 169, 'veg', False),
            ('Falooda', 'Mango Falooda', 149, 'veg', False),

            # Waffles
            ('Waffles', 'Milk Choco Waffle', 79, 'veg', True),
            ('Waffles', 'White Choco Waffle', 79, 'veg', False),
            ('Waffles', 'Dark Choco Waffle', 89, 'veg', True),
            ('Waffles', 'Triple Choco Waffle', 99, 'veg', True),
            ('Waffles', 'Cookies & Cream Waffle', 119, 'veg', False),
            ('Waffles', 'Kit-Kat Crunch Waffle', 109, 'veg', False),
            ('Waffles', 'Oreo Fantasy Waffle', 109, 'veg', False),
            ('Waffles', 'Naughty Nutella Waffle', 129, 'veg', True),
            ('Waffles', 'Red Velvet Waffle', 119, 'veg', False),
            ('Waffles', 'Brownie Waffle White', 119, 'veg', False),
            ('Waffles', 'Brownie Waffle Dark', 119, 'veg', False),

            # Brownie
            ('Brownie', 'Dark Choco Brownie', 69, 'veg', True),
            ('Brownie', 'Triple Choco Brownie', 99, 'veg', False),
            ('Brownie', 'Brownie with Ice Cream', 99, 'veg', True),
            ('Brownie', 'Sizzling Brownie Plate', 119, 'veg', True),

            # Sundae
            ('Sundae', 'Fruit Sundae', 169, 'veg', False),
            ('Sundae', 'Cookies Monster Sundae', 159, 'veg', True),
            ('Sundae', 'Brownie Sundae', 169, 'veg', True),
            ('Sundae', 'Dry Fruit Sundae', 179, 'veg', False),

            # Ice-Cream
            ('Ice-Cream', 'Vanilla Ice-Cream', 69, 'veg', False),
            ('Ice-Cream', 'Strawberry Ice-Cream', 69, 'veg', False),
            ('Ice-Cream', 'Mango Ice-Cream', 79, 'veg', False),
            ('Ice-Cream', 'Chocolate Ice-Cream', 89, 'veg', True),
            ('Ice-Cream', 'Butterscotch Ice-Cream', 89, 'veg', False),

            # Bun
            ('Bun', 'Bun Butter Jam', 29, 'veg', False),
            ('Bun', 'Dark Choco Bun', 39, 'veg', False),
            ('Bun', 'Milk Choco Bun', 39, 'veg', False),
            ('Bun', 'White Choco Bun', 49, 'veg', False),
            ('Bun', 'Triple Choco Bun', 59, 'veg', True),
            ('Bun', 'Cookies & Cream Bun', 69, 'veg', False),

            # Bread Omelette (contains egg -> nonveg)
            ('Bread Omelette', 'Bread Omelette', 59, 'nonveg', False),
            ('Bread Omelette', 'Cheese Bread Omelette', 79, 'nonveg', True),
            ('Bread Omelette', 'Chicken Bread Omelette', 99, 'nonveg', False),
            ('Bread Omelette', 'Cheese Chicken Bread Omelette', 119, 'nonveg', True),

            # Sandwich (Normal / Cheese where applicable)
            ('Sandwich', 'Veg Sandwich', 59, 'veg', False),
            ('Sandwich', 'Veg Sandwich (Cheese)', 79, 'veg', False),
            ('Sandwich', 'Sweet Corn Sandwich', 79, 'veg', False),
            ('Sandwich', 'Sweet Corn Sandwich (Cheese)', 99, 'veg', False),
            ('Sandwich', 'Chocolate Sandwich', 89, 'veg', False),
            ('Sandwich', 'Mushroom Sandwich', 99, 'veg', False),
            ('Sandwich', 'Mushroom Sandwich (Cheese)', 119, 'veg', False),
            ('Sandwich', 'Paneer Sandwich', 109, 'veg', True),
            ('Sandwich', 'Paneer Sandwich (Cheese)', 129, 'veg', True),
            ('Sandwich', 'Egg Sandwich', 69, 'nonveg', False),
            ('Sandwich', 'Egg Sandwich (Cheese)', 89, 'nonveg', False),
            ('Sandwich', 'Chicken Sandwich', 99, 'nonveg', True),
            ('Sandwich', 'Chicken Sandwich (Cheese)', 119, 'nonveg', True),

            # Pizza
            ('Pizza', 'Margherita Pizza', 139, 'veg', True),
            ('Pizza', 'Veg Pizza', 159, 'veg', False),
            ('Pizza', 'Sweet Corn Pizza', 169, 'veg', False),
            ('Pizza', 'Mushroom Pizza', 189, 'veg', False),
            ('Pizza', 'Paneer Pizza', 219, 'veg', True),
            ('Pizza', 'Fried Chicken Pizza', 209, 'nonveg', True),
            ('Pizza', 'Pepper Chicken Pizza', 219, 'nonveg', True),

            # Burger
            ('Burger', 'Mini Chicken Burger (4)', 119, 'nonveg', True),
            ('Burger', 'Chicken Zinger Burger', 139, 'nonveg', True),
            ('Burger', 'Cheese Chicken Zinger Burger', 159, 'nonveg', True),
            ('Burger', 'No Bun Chicken Burger', 189, 'nonveg', False),
            ('Burger', 'Cheese No Bun Burger', 209, 'nonveg', False),

            # Wrap
            ('Wrap', 'Paneer Wrap', 149, 'veg', True),
            ('Wrap', 'Chicken Wrap', 129, 'nonveg', True),

            # Fried Chicken (Normal / Peri Peri)
            ('Fried Chicken', 'Hot & Crispy Chicken (2pc)', 109, 'nonveg', True),
            ('Fried Chicken', 'Hot & Crispy Chicken Peri Peri (2pc)', 119, 'nonveg', False),
            ('Fried Chicken', 'Crispy Chicken Strips (3pc)', 119, 'nonveg', True),
            ('Fried Chicken', 'Crispy Chicken Strips Peri Peri (3pc)', 129, 'nonveg', False),
            ('Fried Chicken', 'Chicken Hot Wings (3pc)', 119, 'nonveg', False),
            ('Fried Chicken', 'Chicken Hot Wings Peri Peri (3pc)', 129, 'nonveg', False),
            ('Fried Chicken', 'Chicken Leg (1pc)', 89, 'nonveg', False),
            ('Fried Chicken', 'Chicken Leg Peri Peri (1pc)', 99, 'nonveg', False),
            ('Fried Chicken', 'Chicken Popcorn', 119, 'nonveg', True),
            ('Fried Chicken', 'Chicken Popcorn Peri Peri', 129, 'nonveg', False),
            # Bucket SKUs (only shown as part of Small/Large Bucket combos on the
            # board - no standalone price was printed, so these are set as
            # reasonable ala-carte estimates; adjust in Admin/Menu Manager if needed)
            ('Fried Chicken', 'Fried Chicken Bucket (6pc)', 259, 'nonveg', True),
            ('Fried Chicken', 'Fried Chicken Bucket (12pc)', 489, 'nonveg', True),

            # French Fries
            ('French Fries', 'French Fries', 79, 'veg', True),
            ('French Fries', 'Peri Peri French Fries', 89, 'veg', False),
            ('French Fries', 'Chicken Loaded Fries', 149, 'nonveg', True),

            # Rice Bowl
            ('Rice Bowl', 'Chicken Rice Bowl', 149, 'nonveg', True),
            ('Rice Bowl', 'Paneer Rice Bowl', 179, 'veg', False),
            ('Rice Bowl', 'Fried Chicken Rice Bowl', 199, 'nonveg', True),

            # Coca-Cola (price not printed on the board - set a standard placeholder;
            # update it in Admin/Menu Manager if your actual price differs)
            ('Coca-Cola', 'Coca-Cola', 30, 'beverage', False),
        ]

        # Handle the rename: old board said "Hot Chocolate Coffee", new board
        # says "Hot Chocolate" - rename the existing row instead of creating
        # a duplicate, so any past orders referencing it stay linked.
        MenuItem.objects.filter(name='Hot Chocolate Coffee').update(name='Hot Chocolate')

        order_counter = 1
        item_lookup = {}
        for cat_name, name, price, itype, featured in items:
            mi, _ = MenuItem.objects.update_or_create(name=name, defaults={
                'category': cat_objs[cat_name],
                'price': price,
                'item_type': itype,
                'is_featured': featured,
                'preparation_time': 10 if itype == 'beverage' else 15,
                'order': order_counter,
            })
            item_lookup[name] = mi
            order_counter += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {len(items)} menu items created/updated'))

        # ── Combo Offers (matches the updated "COMBO OFFERS" board) ────
        # (name, price, [(menu_item_name, qty), ...])
        combos = [
            ('Waffle Treat', 159, [('Triple Choco Waffle', 1), ('Cold Coffee', 1)]),
            ('Chicken Burger Combo', 219, [('Chicken Zinger Burger', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Pizza Combo', 229, [('Margherita Pizza', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Chicken Pizza Combo', 289, [('Pepper Chicken Pizza', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Wrap Combo', 209, [('Chicken Wrap', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Dessert Combo', 169, [('Brownie with Ice Cream', 1), ('Cold Coffee', 1)]),
            ('Crispy Chicken Combo', 189, [('Hot & Crispy Chicken (2pc)', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Chicken Strips Combo', 199, [('Crispy Chicken Strips (3pc)', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Chicken Wings Combo', 199, [('Chicken Hot Wings (3pc)', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Couple Combo', 399, [('Chicken Zinger Burger', 2), ('French Fries', 1), ('Coca-Cola', 2)]),
            ('Couple Waffle Combo', 299, [('Milk Choco Waffle', 2), ('Cold Coffee', 2)]),
            ('Friends Combo', 399, [('Pepper Chicken Pizza', 1), ('Chicken Loaded Fries', 1), ('Coca-Cola', 2)]),
            ('Brothers Special', 449, [('Chicken Zinger Burger', 1), ('Chicken Loaded Fries', 1),
                                        ('Cold Coffee', 1), ('Brownie with Ice Cream', 1)]),
            ('Small Bucket Combo', 349, [('Fried Chicken Bucket (6pc)', 1), ('French Fries', 1), ('Coca-Cola', 1)]),
            ('Large Bucket Combo', 599, [('Fried Chicken Bucket (12pc)', 1), ('French Fries', 1), ('Coca-Cola', 2)]),
        ]

        # These 3 combos are no longer on the board - remove them if present
        # from an earlier seed run.
        Combo.objects.filter(name__in=['Coffee Buddy', 'Choco Lover', 'Chicken Snack Combo']).delete()

        combo_order = 1
        combo_names = [c[0] for c in combos]
        for name, price, combo_items in combos:
            combo, _ = Combo.objects.update_or_create(name=name, defaults={
                'description': ', '.join(f'{qty}× {iname}' for iname, qty in combo_items),
                'price': price,
                'icon': '🎁',
                'is_active': True,
                'order': combo_order,
            })
            # Refresh the combo's item list every run so quantity/composition
            # changes on the board are picked up, not just left stale.
            ComboItem.objects.filter(combo=combo).delete()
            for iname, qty in combo_items:
                mi = item_lookup.get(iname)
                if mi:
                    ComboItem.objects.create(combo=combo, menu_item=mi, quantity=qty)
            combo_order += 1
        self.stdout.write(self.style.SUCCESS(f'✅ {len(combos)} combo offers created/updated'))

        # ── Discounts ───────────────────────────────────────────────────
        discounts = [
            ('Weekend Special', 10, 'Enjoy 10% off every weekend!'),
            ('Festival Offer', 21, 'Special 21% festival discount'),
            ('Student Discount', 5, '5% off for students with ID'),
            ('Loyalty Offer', 15, '15% off for regular customers'),
        ]
        for name, pct, desc in discounts:
            Discount.objects.get_or_create(name=name, defaults={'percent': pct, 'description': desc, 'is_active': False})
        self.stdout.write(self.style.SUCCESS('✅ 4 discounts created'))

        # ── Admin user ──────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@brotherscafe.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('✅ Admin user: admin / admin123'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Brothers Cafe setup complete!'))
        self.stdout.write('📱 Customer URL: http://localhost:8000/')
        self.stdout.write('👨‍🍳 Staff Portal: http://localhost:8000/staff/')
        self.stdout.write('⚙️  Admin Panel: http://localhost:8000/admin/')
        self.stdout.write('🔑 Admin login: admin / admin123')
