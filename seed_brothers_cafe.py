import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brothers_cafe.settings')
django.setup()

from decimal import Decimal
from restaurant.models import ShopSettings, Table, Category, MenuItem, Combo, ComboItem

print("Seeding Brothers Cafe (menu poster edition)...")

ShopSettings.objects.all().delete()
ShopSettings.objects.create(
    shop_name="Brothers Cafe", location="Tirupattur",
    address="Tirupattur, Tamil Nadu", phone="",
    gstin="", fssai_number="",
    default_discount_percent=Decimal("0"),
    default_parcel_charge=Decimal("0"),
)
print("  Shop Settings created")

Table.objects.all().delete()
for n in range(1, 6):
    Table.objects.create(number=n, name=f"Table {n}", capacity=4, is_active=True)
print("  5 Tables created")

Category.objects.all().delete()
MenuItem.objects.all().delete()

def cat(name, icon, order):
    return Category.objects.create(name=name, icon=icon, order=order, is_active=True)

def item(c, name, price, t='veg', o=0):
    return MenuItem.objects.create(
        category=c, name=name, price=Decimal(str(price)),
        item_type=t, is_available=True, order=o)

# HOT DRINKS
c = cat("Hot Drinks","☕",1)
item(c,"Coffee",25,'beverage',0); item(c,"Boost",30,'beverage',1)
item(c,"Horlicks",30,'beverage',2); item(c,"Hot Chocolate",89,'beverage',3)

# COOL DRINKS
c = cat("Cool Drinks","🥤",2)
item(c,"Cold Coffee",89,'beverage',0); item(c,"Rose Milk",45,'beverage',1)
item(c,"Rose Milk with Ice Cream",65,'beverage',2)

# MILK SHAKES  (Pista dropped — not on the poster)
c = cat("Milk Shakes","🥛",3)
shakes=[("Vanilla",89,119),("Strawberry",89,119),("Chocolate",99,129),
        ("Butterscotch",99,129),("Mango",99,129),
        ("Oreo",109,139),("Kit-Kat",109,139),("Boost",109,139),
        ("Horlicks",109,139),("Brownie",129,169),("Dry Fruits",139,179)]
for i,(n,mini,reg) in enumerate(shakes):
    item(c,f"{n} Milkshake (Mini)",mini,'beverage',i*2)
    item(c,f"{n} Milkshake (Regular)",reg,'beverage',i*2+1)

# MOJITO
c = cat("Mojito","🍹",4)
mojitos=[("Virgin",59,89),("Strawberry",59,89),("Blue Curacao",69,99),("Green Apple",69,99)]
for i,(n,mini,reg) in enumerate(mojitos):
    item(c,f"{n} Mojito (Mini)",mini,'beverage',i*2)
    item(c,f"{n} Mojito (Regular)",reg,'beverage',i*2+1)

# ICE CREAM  (Pista dropped — not on the poster)
c = cat("Ice Cream","🍨",5)
for i,(n,p) in enumerate([("Vanilla",69),("Strawberry",69),("Mango",79),
                           ("Chocolate",89),("Butterscotch",89)]):
    item(c,f"{n} Ice Cream",p,'veg',i)

# SUNDAE
c = cat("Sundae","🍧",6)
for i,(n,p) in enumerate([("Fruit Sundae",169),("Cookies Monster Sundae",159),
                           ("Brownie Sundae",169),("Dry Fruit Sundae",179)]):
    item(c,n,p,'veg',i)

# FALOODA  (Strawberry Falooda dropped, "Rayal" corrected to "Royal")
c = cat("Falooda","🍓",7)
for i,(n,p) in enumerate([("Classic Falooda",119),("Dry Fruit Falooda",159),
                           ("Royal Falooda",169),("Mango Falooda",149)]):
    item(c,n,p,'veg',i)

# BROWNIE
c = cat("Brownie","🍫",8)
for i,(n,p) in enumerate([("Dark Choco Brownie",69),("Triple Choco Brownie",99),
                           ("Brownie with Ice Cream",99),("Sizzling Brownie Plate",119)]):
    item(c,n,p,'veg',i)

# WAFFLES  (only the 11 shown on the poster — 5 old variants dropped:
# White & Dark, Milk & White, Dark & Milk, Cotton Candy, Lotus Biscoff)
c = cat("Waffles","🧇",9)
for i,(n,p) in enumerate([("Milk Choco Waffle",79),("White Choco Waffle",79),
    ("Dark Choco Waffle",89),("Triple Choco Waffle",99),("Cookies & Cream Waffle",119),
    ("Kit-Kat Crunch Waffle",109),("Oreo Fantasy Waffle",109),("Naughty Nutella Waffle",129),
    ("Red Velvet Waffle",119),("Brownie Waffle White",119),("Brownie Waffle Dark",119)]):
    item(c,n,p,'veg',i)

# BUN  (Cotton Candy Bun dropped — not on the poster)
c = cat("Bun","🍞",10)
for i,(n,p) in enumerate([("Bun Butter Jam",29),("Dark Choco Bun",39),("Milk Choco Bun",39),
    ("White Choco Bun",49),("Triple Choco Bun",59),("Cookies and Cream Bun",69)]):
    item(c,n,p,'veg',i)

# BREAD OMELETTE
c = cat("Bread Omelette","🍳",11)
item(c,"Bread Omelette",59,'veg',0); item(c,"Cheese Bread Omelette",79,'veg',1)
item(c,"Chicken Bread Omelette",99,'nonveg',2); item(c,"Cheese Chicken Bread Omelette",119,'nonveg',3)

# SANDWICH  (Normal / Cheese columns on the poster)
c = cat("Sandwich","🥪",12)
for i,(n,p,t) in enumerate([
    ("Veg Sandwich",59,'veg'),("Veg Cheese Sandwich",79,'veg'),
    ("Sweet Corn Sandwich",79,'veg'),("Sweet Corn Cheese Sandwich",99,'veg'),
    ("Chocolate Sandwich",89,'veg'),                       # no cheese variant on poster
    ("Mushroom Sandwich",99,'veg'),("Mushroom Cheese Sandwich",119,'veg'),
    ("Paneer Sandwich",109,'veg'),("Paneer Cheese Sandwich",129,'veg'),
    ("Egg Sandwich",69,'veg'),("Egg Cheese Sandwich",89,'veg'),
    ("Chicken Sandwich",99,'nonveg'),("Chicken Cheese Sandwich",119,'nonveg')]):
    item(c,n,p,t,i)

# MAGGI  (not shown on the new poster at all — kept as-is from the old
# seed since it may still be sold; prices unverified against a poster,
# remove this block if Maggi is no longer on the menu)
c = cat("Maggi","🍜",13)
for i,(n,p,t) in enumerate([
    ("Plain Maggi",45,'veg'),("Plain Maggi Cheese",65,'veg'),
    ("Veg Maggi",55,'veg'),("Veg Maggi Cheese",75,'veg'),
    ("Peri Peri Maggi",60,'veg'),("Peri Peri Maggi Cheese",80,'veg'),
    ("Szechwan Maggi",85,'veg'),("Szechwan Maggi Cheese",105,'veg'),
    ("Sweet Corn Maggi",65,'veg'),("Sweet Corn Maggi Cheese",85,'veg'),
    ("Mushroom Maggi",85,'veg'),("Mushroom Maggi Cheese",105,'veg'),
    ("Egg Maggi",65,'veg'),("Egg Maggi Cheese",85,'veg'),
    ("Chicken Maggi",95,'nonveg'),("Chicken Maggi Cheese",115,'nonveg')]):
    item(c,n,p,t,i)

# PIZZA  (Chilli Paneer, Mixed, Peri Peri Chicken dropped — not on the poster)
c = cat("Pizza","🍕",14)
for i,(n,p,t) in enumerate([
    ("Margherita Pizza",139,'veg'),("Veg Pizza",159,'veg'),
    ("Sweet Corn Pizza",169,'veg'),("Mushroom Pizza",189,'veg'),
    ("Paneer Pizza",219,'veg'),("Fried Chicken Pizza",209,'nonveg'),
    ("Pepper Chicken Pizza",219,'nonveg')]):
    item(c,n,p,t,i)

# BURGER
c = cat("Burger","🍔",15)
for i,(n,p,t) in enumerate([
    ("Mini Chicken Burger (4 pc)",119,'nonveg'),("Chicken Zinger Burger",139,'nonveg'),
    ("Cheese Chicken Zinger Burger",159,'nonveg'),("No Bun Chicken Burger",189,'nonveg'),
    ("Cheese No Bun Burger",209,'nonveg')]):
    item(c,n,p,t,i)

# FRENCH FRIES  (Masala French Fries dropped — not on the poster)
c = cat("French Fries","🍟",16)
for i,(n,p,t) in enumerate([("French Fries",79,'veg'),
    ("Peri Peri French Fries",89,'veg'),("Chicken Loaded Fries",149,'nonveg')]):
    item(c,n,p,t,i)

# FRIED CHICKEN  (Normal / Peri Peri columns on the poster)
c = cat("Fried Chicken","🍗",17)
for i,(n,p,t) in enumerate([
    ("Hot & Crispy Chicken (2 pc)",109,'nonveg'),("Hot & Crispy Peri Peri (2 pc)",119,'nonveg'),
    ("Crispy Chicken Strips (3 pc)",119,'nonveg'),("Crispy Strips Peri Peri (3 pc)",129,'nonveg'),
    ("Chicken Hot Wings (3 pc)",119,'nonveg'),("Chicken Hot Wings Peri Peri (3 pc)",129,'nonveg'),
    ("Chicken Leg (1 pc)",89,'nonveg'),("Chicken Leg Peri Peri (1 pc)",99,'nonveg'),
    ("Chicken Popcorn",119,'nonveg'),("Chicken Popcorn Peri Peri",129,'nonveg')]):
    item(c,n,p,t,i)

# WRAP
c = cat("Wrap","🌯",18)
item(c,"Paneer Wrap",149,'veg',0); item(c,"Chicken Wrap",129,'nonveg',1)

# RICE BOWL  (new category — not on the old seed at all)
c = cat("Rice Bowl","🍚",19)
item(c,"Chicken Rice Bowl",149,'nonveg',0); item(c,"Paneer Rice Bowl",179,'veg',1)
item(c,"Fried Chicken Rice Bowl",199,'nonveg',2)

# EXTRAS  (poster's Coca-Cola price wasn't legible — kept the old ₹30;
# confirm and correct if that's changed)
c = cat("Extras","➕",20)
item(c,"Coco Cola",30,'veg',0)

print(f"  {Category.objects.count()} categories, {MenuItem.objects.count()} menu items created")

# ── COMBOS ────────────────────────────────────────────────────────────────────
# Matches the 15 combos on the "Combo Offers" poster. Combo prices are the
# bundle price shown, not the sum of parts. A few combo items don't map to
# an exact catalog item and are noted below:
#   - "Chicken Caesar Wrap" (Wrap Combo) -> mapped to "Chicken Wrap"
#   - "2 Waffles" (Couple Waffle Combo)  -> mapped to "Triple Choco Waffle" x2
#   - "Chicken Pizza" (Friends Combo)    -> mapped to "Fried Chicken Pizza"
#   - "Coke" on the poster                -> mapped to "Coco Cola"
#   - Combos 14 & 15 (Small/Large Bucket) reference "6 pc" / "12 pc" fried
#     chicken buckets and small/large fries that don't exist as separate
#     catalog items yet. They're created with price + description only;
#     add dedicated "Fried Chicken Bucket (6pc)" / "(12pc)" menu items if
#     you want their stock/ingredients tracked individually.
Combo.objects.all().delete()

def get(name):
    return MenuItem.objects.filter(name__icontains=name).first()

combos = [
    ("Waffle Treat", 159, "Triple Choco Waffle + Cold Coffee", "🧇",
        [("Triple Choco Waffle",1),("Cold Coffee",1)]),
    ("Chicken Burger Combo", 219, "Chicken Zinger Burger + French Fries + Coke", "🍔",
        [("Chicken Zinger Burger",1),("French Fries",1),("Coco Cola",1)]),
    ("Pizza Combo", 229, "Margherita Pizza + French Fries + Coke", "🍕",
        [("Margherita Pizza",1),("French Fries",1),("Coco Cola",1)]),
    ("Chicken Pizza Combo", 289, "Pepper Chicken Pizza + French Fries + Coke", "🍕",
        [("Pepper Chicken Pizza",1),("French Fries",1),("Coco Cola",1)]),
    ("Wrap Combo", 209, "Chicken Wrap + French Fries + Coke", "🌯",
        [("Chicken Wrap",1),("French Fries",1),("Coco Cola",1)]),
    ("Dessert Combo", 169, "Brownie with Ice Cream + Cold Coffee", "🍫",
        [("Brownie with Ice Cream",1),("Cold Coffee",1)]),
    ("Crispy Chicken Combo", 189, "Hot & Crispy Chicken (2 pc) + French Fries + Coke", "🍗",
        [("Hot & Crispy Chicken (2 pc)",1),("French Fries",1),("Coco Cola",1)]),
    ("Chicken Strips Combo", 199, "Crispy Chicken Strips (3 pc) + French Fries + Coke", "🍗",
        [("Crispy Chicken Strips (3 pc)",1),("French Fries",1),("Coco Cola",1)]),
    ("Chicken Wings Combo", 199, "Chicken Hot Wings (3 pc) + French Fries + Coke", "🍗",
        [("Chicken Hot Wings (3 pc)",1),("French Fries",1),("Coco Cola",1)]),
    ("Couple Combo", 399, "2 Chicken Zinger Burgers + French Fries + 2 Coke", "🍔",
        [("Chicken Zinger Burger",2),("French Fries",1),("Coco Cola",2)]),
    ("Couple Waffle Combo", 299, "2 Waffles + 2 Cold Coffee", "🧇",
        [("Triple Choco Waffle",2),("Cold Coffee",2)]),
    ("Friends Combo", 399, "Chicken Pizza + Chicken Loaded Fries + 2 Coke", "🍕",
        [("Fried Chicken Pizza",1),("Chicken Loaded Fries",1),("Coco Cola",2)]),
    ("Brothers Special", 449, "Chicken Zinger Burger + Chicken Loaded Fries + Cold Coffee + Brownie with Ice Cream", "⭐",
        [("Chicken Zinger Burger",1),("Chicken Loaded Fries",1),("Cold Coffee",1),("Brownie with Ice Cream",1)]),
    ("Small Bucket Combo", 349, "6 pc Fried Chicken + French Fries (Small) + 1 Coke", "🪣",
        [("Coco Cola",1)]),   # bucket + fries not in catalog yet — see note above
    ("Large Bucket Combo", 599, "12 pc Fried Chicken + French Fries (Large) + 2 Coke", "🪣",
        [("Coco Cola",2)]),   # bucket + fries not in catalog yet — see note above
]

for i, (name, price, desc, icon, parts) in enumerate(combos, start=1):
    combo = Combo.objects.create(
        name=name, price=Decimal(str(price)), description=desc,
        icon=icon, is_active=True, order=i)
    for part_name, qty in parts:
        mi = get(part_name)
        if mi:
            ComboItem.objects.create(combo=combo, menu_item=mi, quantity=qty)

print(f"  {Combo.objects.count()} combos created")
print()
print("Done! Visit /admin/ or /manage/ to add images and fine-tune anything above.")
print("Check the comments in this file for the items that needed a judgment call —")
print("Maggi, the Coca-Cola price, and the two bucket combos in particular.")
