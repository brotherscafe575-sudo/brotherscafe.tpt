# Brothers Cafe — bug fix pass

## How to deploy

```bash
python manage.py migrate      # applies 0020 + 0021, and repairs existing orders
python manage.py runserver
```

Migration `0020` does three things to your existing data:

1. Links old combo order-lines to the real `Combo` using the note they saved
   (`🎁 Combo: <name>`). All 8 historical combo lines were matched.
2. Marks zero-priced lines as free-offer items.
3. Recomputes every order total so the parcel charge is included and flat
   cart-offer discounts are no longer lost.

Migration `0021` adds a per-order `access_token` and gives every existing order
its own unique value.

Nothing is deleted. Both migrations are reversible on the schema side.

---

## 1. POS — items invisible in the right-hand order panel

**Symptom:** panel showed "3 items" and a subtotal of ₹2615, but the item list
was blank.

**Cause:** the items *were* rendering — into a container with no height.

```css
.op-body{flex:1; ... min-height:0}   /* item list  */
.op-foot{... flex-shrink:0}          /* everything below it */
```

`.op-foot` holds the dine-in/takeaway toggle, customer fields, offer banners,
cart offers, totals and buttons, and it is not allowed to shrink. Once it grew
taller than the panel, `.op-body` was squeezed to 0px.

**Fix** (`pos_terminal.html`): `.op-body` gets `min-height:132px`, `.op-foot`
gets `max-height:62vh; overflow-y:auto` so it scrolls instead of crushing the
list.

## 2. No confirmation when adding an offer-banner item

**Symptom:** clicking **+ Add** in the offer panel gave no feedback, and the
panel stayed open.

**Cause:** `pos_terminal.html` defines `toast()`, but `addPosOfferItem()`,
`applyPosOffer()` and `removePosOffer()` all call `showToast()` — which was
never defined in that file. Every call threw `ReferenceError`, aborting the rest
of the handler. The item was added (that line runs first), but the toast never
showed and `modal.remove()` never ran.

**Fix:** added a `showToast()` wrapper that delegates to `toast()`.

## 3. "Free Cheese Chicken Zinger Burger" free-item offer

Two independent problems.

**Layout:** the reward button used `white-space:nowrap`, so a long label ran
off the edge of the card. Now wraps, capped at 55% width.

**Billing — the serious one:** the free line was sent to the server as
`{id, qty}` with no price marker. `place_order` read that as "no price supplied"
and charged **full menu price**. The customer saw FREE and was billed ₹115.

**Fix:** the client now sends `free_offer: true`, and the server grants ₹0 only
after re-checking the item against the claimed offer's `free_item` and its
`min_cart_value`. If the offer wasn't genuinely earned, the free line is removed
rather than silently charged. Same fix applied to the POS path.

## 4. Combos showed the wrong name on bills

**Symptom:** a combo appeared as `1× Chicken Hot Wings (3 pc) — ₹510`.

**Cause:** a combo was stored as an `OrderItem` pointing at the combo's *first*
menu item, with the combo name only in a free-text note. Every bill rendered
`item.menu_item.name`.

**Fix:**
- `OrderItem.combo` — a real FK to `Combo` (nullable; `menu_item` is kept so
  sales reports still have something to group by).
- `OrderItem.display_name` / `.is_combo` / `.combo_components` properties.
- Migration backfills historical rows from the old notes.
- Updated everywhere: `bill.html`, `print_bill.html` (thermal + A4),
  `order_status.html`, `customer_home.html`, `customer_history.html`,
  `staff_portal.html`, `partials/order_card.html`, plus the `live_order`,
  `order_status`, `bill_view`, `print_bill` and `staff_order_items_get` views.

Bills now read **All in One Bucket [COMBO]** with the contents listed beneath.

## 5. Staff portal discount vs. customer offers

The complete-order modal now shows a banner naming the offer the customer
already earned, and the dropdown's first option reads *"Keep customer's offer /
no discount"*. Selecting `0` no longer wipes a flat cart offer — only choosing a
real discount replaces it.

---

## Total / discount errors found while checking the money

### `calculate_totals()` dropped the parcel charge

```python
self.total_amount = self.subtotal - self.discount_amount   # no parcel
```

It runs automatically inside `Order.save()`, so *any* later save on a takeaway
order silently deleted the parcel money. The codebase was already fighting this
— there's a comment at the `.update()` workaround saying totals must be written
directly "so they are never overwritten by model.save() re-calc", and a whole
`fix_totals` command written to repair the damage (which reproduced the same
formula, repairing orders into a still-wrong state).

Verified: ₹120 takeaway total stays ₹120 after `save()`. Previously ₹100.

### Flat cart offers were erased on recalculation

A "Flat ₹400 OFF" has no percentage behind it, so `calculate_totals()` reset
`discount_amount` to ₹0 and *raised* the customer's bill. Added
`Order.discount_is_flat` so the rupee amount is preserved (clamped to subtotal).

### POS ignored `cart_offer_flat`

The terminal sent `cart_offer_flat` and `cart_offer_title`; `pos_save_order`
read neither. Flat offers vanished on save. Now honoured and persisted.

### Same broken formula in three more places

- `print_bill` — no parcel, flat discounts re-derived from a 0% figure.
- `_revenue_from_items` (dashboard/stats revenue) — same.
- `fix_totals` management command — same.

All three fixed.

### Reorder merging

Child items merged into the root order matched on `menu_item` alone, so two
different combos sharing a representative item merged into a single line. Now
keyed on `menu_item + combo + unit_price + is_free`. The child's parcel charge
is also carried onto the root bill instead of being dropped.

### `Order.offer_title`

New field recording which cart offer produced the discount, so bills and the
staff modal can name it.

---

## Security holes closed

These were reachable by anyone with the QR link.

| Issue | Before | Now |
|---|---|---|
| `discount_percent` from client | `discount_percent: 90` → 90% off, ₹100 became ₹10 | validated against active `Discount` rows + shop default |
| `unit_price` from client | any value ≥ 0 accepted with a fake `offer_label` — cart could be zeroed | recomputed server-side from the real `OfferBanner` |
| Free items | client could declare anything free | re-checked against the offer's `free_item` and minimum |
| Combo price | taken from the POS terminal | always read from the database |
| `/staff/orders/pending/` | no auth | staff login required |
| `/staff/orders/live/` | no auth | staff login required |
| `/staff/order/<id>/items/` | no auth — read any order | staff login required |
| `/staff/order/<id>/edit-items/` | no auth — **edit any order's items** | staff login required |

---

## Verification

- `manage.py check` — clean.
- Migration `0020` applied; all 8 historical combo lines recovered correctly.
- End-to-end suite passing:
  - combo renders as the combo name with components
  - legitimately earned free item lands at ₹0
  - spoofed `free_offer` with no cart offer → charged full price
  - spoofed ₹1 `unit_price` → falls back to real price
  - spoofed 90% discount → rejected (₹100 total, not ₹10)
  - legitimate 20% discount → still applies
  - takeaway parcel survives `save()`
  - flat ₹200 offer survives `calculate_totals()`
- All customer and staff pages render 200; unauthenticated staff APIs return 302.

---

---

## Security — round two

The four items below were on the outstanding list in the first pass. They are
now fixed and verified.

### Bills were readable by anyone

`bill_view`, `order_status`, `print_bill`, `reorder`, `reorder_menu` and
`live_order_data` all took a sequential integer id with no ownership check.
Walking `/order/1/bill/` upward exposed every customer's name, phone number,
items and totals.

New helper `_can_view_order()` allows access when **any** of these hold:

- the requester is logged-in staff;
- the session's `customer_phone` matches the order (or its root order);
- the URL carries `?t=<access_token>` matching that order.

`Order.access_token` is a random UUID per order, so a bill can still be shared
by link without that link revealing anything about other orders. Denied requests
get a friendly 403 page (`order_not_found.html`), or JSON for API callers.

Note on the migration: Django evaluates a callable default **once** during
`AddField`, so all existing rows would otherwise have shared a single token,
making it useless as a key. `0021` includes a `RunPython` step assigning each
order its own — verified 10 orders, 10 distinct tokens.

### `?reorder_from=<id>` leaked customer details

The menu view explicitly skipped the login check when `reorder_from` was
present, then copied that order's customer name and phone into the page. Any id
worked. Now gated by the same ownership check.

### Anyone could mark any order paid

`confirm_payment` accepted an unauthenticated POST and set
`payment_status='paid_online'` on any order. It now requires POST, requires
ownership, and — for a customer — records only `online_pending`. Staff still
confirm the actual payment from the portal. `pay_online` also stopped mutating
state on a plain GET from a stranger, and no longer downgrades an
already-paid order.

### Customers could complete their own order without paying

`place_order` honoured `payment_method` straight from the request body, so
posting `'offline'` produced a `completed` + `paid_offline` order. It is now
honoured only when the request comes from authenticated staff, which is how the
POS pages use it. A customer order always starts `pending` / `unpaid`.

Verified: staff POS orders still save as completed + paid; a customer sending
the same payload gets `status=pending`, `payment_status=unpaid`.

---

## Verification (full suite)

**Access control**

| Check | Result |
|---|---|
| stranger opens `/order/8/bill/`, `/status/`, `/print-bill/`, `/reorder/`, `/live-order/data/` | 403, no phone number in body |
| stranger POSTs `confirm-payment` | 403, payment status unchanged |
| customer posts `payment_method:'offline'` | `pending` / `unpaid` |
| owner opens their own status + live data | 200 |
| `?t=<correct token>` | 200 |
| `?t=<another order's token>` | 403 |
| staff open any bill, print bill, portal, POS | 200 |
| staff POS order with `payment_method:'offline'` | completed + paid |

**Money and display**

| Check | Result |
|---|---|
| combo renders as combo name + components | pass |
| earned free item | ₹0 |
| spoofed `free_offer`, no offer behind it | charged full price |
| spoofed ₹1 `unit_price` | real price used |
| spoofed 90% discount | rejected |
| legitimate 20% discount | applies |
| takeaway parcel after `save()` | preserved |
| flat ₹200 offer after `calculate_totals()` | preserved |

`manage.py check` clean, `makemigrations --check` reports no pending changes,
and the shipped database still holds the original 10 orders, 8 combo lines and
149 menu items.

---

---

# Round three

## 1. POS terminal bill now matches the staff bill

The POS "🖨️ Bill" button produced a plain monospace text receipt built with
string padding, which looked nothing like the styled bill at
`/order/<id>/print-bill/`. `showPrint()` now emits the same HTML and the same
CSS as `print_bill.html`, so both come off the thermal printer identically —
including the shop header block, the `Customer / Phone / Table` rows, combo
lines with their contents underneath, and the `🎁 Offer: <name>` discount line.

The customer copy and the staff KOT copy are still printed as two separate jobs
so the printer cuts between them.

**Rounding mismatch found while checking this.** The terminal rounded offer
discounts to whole rupees (`Math.round`) while the server stores them to two
decimals. On a ₹469 cart with 50% off, the POS screen and its printed bill said
₹234 while the saved order and the customer's bill said ₹234.50. All three now
agree: discounts round to paise, and the totals show paise whenever there are
any.

## 2. The offer vanished when staff completed the order

This is the bug in the uploaded receipt: an order placed at ₹234.50 with
"Offer: ewq" reverted to the full ₹469 the moment staff billed it.

Two causes, both fixed:

**`place_order` never stored the percentage.** For a percentage cart offer the
view computed `discount_amount` from a local variable but left
`order.discount_percent` at whatever the browser happened to send — zero, if it
sent nothing. The order was saved with a discount *amount* and no percentage
behind it, so the next `calculate_totals()` had nothing to recompute from and
reset it to zero. The percentage actually used is now written onto the order,
and `calculate_totals()` additionally refuses to erase a discount belonging to a
named offer.

**The complete-order modal always sent `discount_percent: 0`**, which the view
read as "staff set the discount to nothing". The dropdown now distinguishes
three intents:

| Option | Sent | Effect |
|---|---|---|
| Keep as ordered *(default)* | `0` | customer's offer untouched |
| A named discount | its % | replaces the customer's offer |
| ❌ Remove all discounts | `-1` | clears everything |

Verified: ₹500 cart with a 50% offer stays at ₹250 through accept → prepare →
ready → complete; picking 10% gives ₹450; choosing remove gives ₹500.

## 3. Scroll position when returning from items to categories

Going into a category and coming back — by button, browser back, or swipe —
jumped to the top of the category list.

The restore was a single `window.scrollTo()` fired 20 ms after the page switch.
At that point the restored page has not finished laying out, so the browser
clamps the target to the current (short) document height and the customer lands
at the top. Replaced with `restoreScrollTo()`, which retries across animation
frames until the position actually sticks (or gives up after ~30 frames), tops
up again on `window.load` once images have changed the page height, and blocks
the scroll listener from recording a half-way position while it settles.

The categories position is now also persisted to `sessionStorage` the way the
items position already was, so it survives a reload.

## 4. Combo builder in Menu Manager

The combos section let staff set a name, price, icon and description — but there
was **no way to choose what was in the combo**. `ComboItem` rows could only be
created from Django admin, so combos built from the manager shipped empty.

Added a two-pane picker inside the combo modal:

- left pane lists every menu item with live search and a category filter;
- right pane is the combo's contents, each line with −/+ quantity and remove;
- the footer shows **items value**, **combo price**, and what the customer
  saves — turning red if the combo is priced above the sum of its parts;
- **Use items value** fills the price with the un-discounted total as a
  starting point.

`mm_combo_save` now persists the selection (`update_or_create` per line, orphans
removed), rejects a blank name or a negative price, and returns the stored
contents. Editing a combo pre-loads its current items instead of silently
wiping them. The combos table flags any combo that still has no items.

Verified end to end: create a 3-item combo at ₹399, edit it down to a single
item at ₹250, order it, and the bill reads *Test Family Box* at ₹250 with its
contents listed.

---

---

# Round four

## 1. "Add Combo" was broken — my bug from round three

Clicking **+ Add Combo** did nothing. The cause was in the code I added last
round:

```django
{{ picker_items_json|json_script:"picker-items" }}
```

`json_script` JSON-encodes whatever it is handed. I handed it a string that was
*already* JSON, so the page carried a double-encoded value and `JSON.parse`
returned a **string** instead of an array. `cbInitCats()` then threw
`CB_ITEMS.map is not a function`, and because that ran first, the modal never
opened.

Fixed by passing the plain Python list and letting `json_script` do the
encoding. Verified by loading the real rendered page in a headless DOM and
clicking the button: the modal opens with all 149 menu items in the picker.

I should have caught this last round — my test checked that the markup was
*present* in the HTML, not that the page actually ran.

## 2. New "Combo Offers" table

Added as its own section in the Menu Manager, with its own sidebar entry
(🏷️ Combo Offers), its own table, and its own **+ Add Combo Offer** button.

Staff pick the items and set one fixed price, exactly as with combos, plus:

- **Badge text** — e.g. `LIMITED TIME`, shown on the customer card;
- **Runs from / Runs until** — optional; blank means it runs indefinitely.

The table shows the contents, what they'd cost separately, the offer price, the
saving in ₹ and %, the date window, and a warning when an active offer is
outside its dates ("Not live today").

**On the customer side** these appear in a highlighted strip at the very top of
the menu — above the offer banners and above the ordinary combos carousel —
with the crossed-out original price and a `SAVE ₹x` badge. Offers outside their
date window are hidden. A combo flagged as an offer no longer also appears in
the plain combos carousel below, so it isn't shown twice.

### A note on the design

Rather than create a second near-identical model, this reuses `Combo` with an
`is_offer` flag plus the badge and date fields. The two are the same thing to
the rest of the system — same item picker, same pricing, same `OrderItem.combo`
link, same behaviour on every bill — so duplicating the model would have meant
duplicating all of that plumbing and the ordering code with it. You get two
separate tables in the Menu Manager and two separate places on the customer
page, which is what matters in use.

Verified end to end: create an offer via the manager, confirm it lands in the
Combo Offers table and not the Combos table, confirm it renders at the top of
the customer menu and not in the combos carousel, confirm a future start date
hides it, order it and see it billed as *Weekend Family Feast* at the fixed
price, and confirm a reversed date range is rejected with a 400.

## 3. Malformed CSS on the customer menu

Found while running the page in a real DOM parser:

```css
.offer-card{scroll-snap-align:start;transition:.15s;active{opacity:.85}}
```

The nested `active{...}` is not valid CSS — it caused the browser to discard the
whole rule, so offer cards had no scroll-snap or transition. Split into
`.offer-card{...}` and `.offer-card:active{...}`.

---

---

# Round five

## ⚠️ First: a regression I introduced and then caught

While removing the water-bottle fallback in this round, my edit script cut from
the fallback marker to the next `def`, which swallowed more than intended —
including the module constant `ACTIVE_ORDER_STATUSES`.

That constant is used by `get_active_order_chain()`, which `bill_view`,
`order_status`, `update_order_status` and the reorder merge all call. The result
was an unconditional `NameError` on those paths.

Restored, and then I diffed the whole of `views.py`, `models.py` and `urls.py`
against your original upload to confirm nothing else went missing: 88 original
functions all still present (94 now), no lost model fields, no lost routes, no
lost constants. Regression now covers the reorder chain explicitly — place an
order, add a reorder against it, open bill / status / print-bill / live-data /
reorder-menu, then complete the chain and check the merged totals.

## 1. Images on combos and combo offers

The combo modal now has an image upload with a live preview and a "remove
current image" checkbox, matching the offer-banner modal. `mm_combo_save`
accepts `multipart/form-data` as well as JSON, so the picture, the items and the
price all save in one request.

On the customer menu, a combo offer with a picture shows it in the card; without
one it falls back to the icon as before.

## 2. Run dates on offer banners and cart offers

Both now have **Runs from / Runs until**, the same as combo offers. A new
`DateWindowMixin` gives all three the same `valid_from` / `valid_to` fields plus
`is_in_window` and a `window_label` for display, so the behaviour is identical
everywhere rather than reimplemented three times.

- Two new manager helpers, `active_offer_banners()` and `active_cart_offers()`,
  now feed every customer-facing and POS view — 10 call sites in total.
- Both manager tables gained a **Runs** column showing the window, and flag an
  active-but-out-of-window promotion as "Not live today".
- Reversed date ranges are rejected with a clear 400.
- **Expiry is enforced at checkout too**: `place_order` re-resolves the cart
  offer through `active_cart_offers()`, so replaying an expired offer from a
  stale browser tab gets a ₹0 discount rather than being honoured.

## 3. The cart quick-add card showed Coffee

In your screenshot the "water bottle" card in the cart was offering Coffee at
₹25. Three separate faults:

**It fell back to any beverage.** `get_water_bottle()` tried "water bottle",
then "water", then **any item of type `beverage`** — which found Coffee. It then
went further and *created* a menu item during a page render if nothing matched.
Both fallbacks are gone: staff now name the item explicitly, and if nothing
sensible is configured the card is hidden. Showing the wrong product is worse
than showing none.

**The price could not be edited.** The template context set
`water_bottle_price` twice in the same dict — the second entry (the item's raw
price) silently overrode the shop-configured price, so the field had no effect.
Removed.

**Nothing was ever saved.** `mm_shop_settings_save` didn't handle any of the
water-bottle fields, so the toggle and price in the manager were inert. And the
takeaway page never received `water_bottle_enabled` or `water_bottle_price` at
all.

Shop Settings now has a proper **💧 Water bottle quick-add** block:

| Control | Behaviour |
|---|---|
| Show the card in the cart | on/off; off hides it entirely |
| Which item does it add? | dropdown of every menu item, or auto-detect by name |
| Price shown on the card | overrides the item's menu price; 0 means use the menu price |

New field `ShopSettings.water_bottle_item`. Verified: choosing an item and a
₹15 override renders that item at ₹15; setting the override to 0 falls back to
the item's own ₹20; toggling off removes the card; and with nothing configured
and no water item in the menu, the card is disabled rather than showing Coffee.

---

---

# Round six

## 1. Combo offer card — cramped right-hand side

The card packed price, struck-out price, savings badge and the Add button into a
single flex row. On a phone the "was" price got squeezed to a couple of
characters, which is the garbled `₹€` in your screenshot.

Rebuilt as two columns: the price block (offer price + struck-out original on
one line, savings badge beneath) takes the space it needs, and the Add button
sits on its own with `flex:0 0 auto` so it can never squash its neighbour. The
badge now reads `SAVE ₹456 · 67%` instead of just the rupee figure.

## 2. Water bottle setting listed every menu item

The dropdown offered all 150 items, so it was possible to point the cart's water
card at Coffee — the original problem in a new form.

Added `MenuItem.is_water_bottle`, with a **💧 This is a water bottle** toggle in
the item modal. The Shop Settings dropdown now lists *only* flagged items, and
the server rejects an attempt to point it at anything unflagged. When nothing is
flagged yet the setting shows a clear prompt instead of an empty list.

Migration `0024` auto-flags any existing item with "water" in its name, so
nothing needs doing by hand if such an item already exists.

Verified: with nothing flagged the dropdown is empty and shows the hint; after
flagging one item it is the only option; Coffee is not selectable and is
rejected with a 400 if posted directly.

## 3. Category cards showed the unfiltered item count

With **Non-Veg** selected, the Sandwich card still read "13 items" while the
category itself only had 2 non-veg items.

`applyCatFilter()` was showing and hiding cards but never touching the count,
which is rendered server-side as the category total. It now recounts against the
active filter, keeps the original in `data-total` to restore when the filter is
cleared, and switches to "1 item" for a single match.

Verified in a real DOM: Sandwich reads 13 → 2 (non-veg) → 11 (veg) → hidden
(beverages) → 13 again.

## 4. Scroll still jumped to the top — the actual cause

My previous two attempts treated the symptom. The real cause is that **the
browser was overwriting our restore**.

Every step of the menu shares one URL (`pushState` with an empty URL), and
`history.scrollRestoration` defaults to `"auto"` — so on back or swipe-back the
browser restores whatever scroll position it remembered for that history entry,
and it does so *after* our handler runs. The page has to opt out explicitly:

```js
if ('scrollRestoration' in history) { history.scrollRestoration = 'manual'; }
```

Three supporting fixes alongside it:

- `selectCat` fired `scrollIntoView({behavior:'smooth'})` when entering a
  category. That animation was often still running when the customer tapped
  back, dragging the freshly restored position away. Replaced with an instant
  scroll.
- The legacy `showStep()` alias called `window.scrollTo({top:0})`
  unconditionally. It now restores the saved position for steps 1 and 2.
- `restoreScrollTo()` keeps re-asserting for ~700 ms after landing rather than
  stopping at the first success, so late layout (images, the categories
  fade-in) can't shift the page out from under it.

Also removed a redundant pair of back-to-back smooth `scrollIntoView` calls in
"add more items", where the second interrupted the first.

Note: `history.scrollRestoration` is not implemented in the headless DOM I test
with, so this specific line is verified by inspection rather than execution. If
the jump somehow persists on your phone, tell me which of the three ways back
(the ← Categories button, the browser back button, or the swipe gesture) still
does it and I'll narrow it down further.

---

---

# Round seven

## ⚠️ "name 'data' is not defined" — my bug, adding items was broken

`items_portal_add_item` reads `request.POST`, but the water-bottle line I added
last round used `data.get(...)`, a name that doesn't exist in that function. Any
attempt to add a new menu item crashed. Fixed to `request.POST.get(...)` and
verified by actually creating an item through the endpoint.

## 1. Water bottle setting is now just on/off + price

Dropped the "which item" dropdown from Shop Settings. The item is chosen by
ticking **💧 This is a water bottle** on the menu item itself; Settings now shows
a read-only "Currently using" line plus the two controls you wanted — the on/off
toggle and the price. A pinned item that later loses its flag is dropped
automatically rather than silently continuing to be used.

## 2. "N offers unlocked" banner covered the header

The banner was `position:fixed; top:0` with the same z-index as the sticky
header, so it sat on top of the header and its back button. Moved to the bottom,
sliding up just above the cart bar, so nothing ever covers the back button.

## 3. Website bill total didn't add up

The discount row was wrapped in `{% if discount_percent > 0 %}`. A **flat** cart
offer has `discount_percent = 0` and only a rupee amount — so the discount was
subtracted from the total but never shown, and the bill looked wrong. It now
renders whenever `discount_amount > 0`, and names the offer.

The items table also overflowed its card, cutting off the Total column. Given
`table-layout: fixed` with explicit column widths (46/12/20/22%), numeric columns
right-aligned, and long item names wrapping instead of pushing the table wide.

The printed bill had a related gap: **parcel charge was never printed**, so a
takeaway slip didn't reconcile either. Added.

## 4. Cafe logo on customer bills

`ShopSettings.logo` existed but had no upload UI and was never rendered. Added:

- a logo upload with live preview in Shop Settings;
- the logo on the **website bill**, the **printed bill** (staff portal and POS),
  and the **POS terminal receipt** — customer copy only, never the KOT.

Your logo from the screenshot is installed as the current shop logo, so it works
out of the box; replace it any time from Shop Settings.

## 5. Offer banners now auto-scroll, like the combos

The offer carousel only synced its dots on manual scroll. It now advances
left → right every 3.5 s, pauses while the customer is touching or scrolling it
(resuming after 6 s), and stops entirely when the tab is hidden.

## 6. Category scroll — deeper categories still landed at the top

You spotted the pattern: Sandwich came back correctly, categories further down
did not. That fits a **pixel** restore drifting — anything above the grid that
changes height between leaving and returning (the live-order card, the offers
strip, a cart bar appearing) shifts everything below it, and the further down the
customer was, the bigger the error, until it clamps to the top.

Now the position is anchored to the **category card** rather than a pixel offset:
on opening a category the card's id and its offset within the viewport are
stored, and on return that exact card is put back at that exact viewport offset.
The old pixel value is kept only as a fallback.

Verified with a simulated 200px layout shift above the grid: the anchor resolves
to 1100 (correct) where the stored pixel offset would have used a stale 900.

## 7. Reorder printed the original order's bill

The **Print Bill** button on a reorder card called `printBill(orderId)` without
`reorder_only=1`, which the notification flow was already passing — so a manual
print produced the full combined bill of the original order instead of the newly
added items. The button now passes the flag when the order has a parent.

Verified: printing a reorder shows only its own item, with the
"🔄 REORDER ITEMS ONLY" banner.

## 8. Reorder's offer vanished when staff marked it ready

Merging a reorder into its parent copied the items but discarded the child's
discount, so an offer earned on the reorder disappeared the moment staff pressed
ready. The merge now carries it across:

- parent has no offer → adopt the reorder's;
- both flat → the amounts stack, capped at the subtotal;
- both percentage → keep the better one for the customer.

Verified: ₹100 order + ₹200 reorder at 50% off merges to ₹300 subtotal, ₹150
discount, ₹150 total, and survives being billed.

Also removed a dead `reorder_from_id` assignment in `place_order` — the client
sends `parent_order_id`; that variable was read from the payload and never used.

## 9. Offer details on the bill

Both the website bill and the printed bill now name the offer on the discount
line (`🎁 Flat 200 (flat)` / `🎁 ewq (50%)`) instead of a bare "Discount", and
the printed bill no longer depends on a `special_instructions` string match.

## 10. KOT combo lines

Combo contents were printed as a small grey comma-separated run-on. Each
component now gets its own bold line under its combo, prefixed with `└`, so the
kitchen can read them at a glance.

---

## Still outstanding

1. **Customer login is a phone number with no verification** — entering someone
   else's number still shows their order history. This one needs a product
   decision (OTP, or accept the risk), so I left it alone.
2. **Config:** hardcoded `SECRET_KEY` fallback, `ALLOWED_HOSTS = ['*']`, empty
   `AUTH_PASSWORD_VALIDATORS`, admin credentials printed in the README. Rotate
   the key and change the password before going live.
3. **Duplicate project tree** at `brothers_cafe/brothers_cafe/` and
   `brothers_cafe/restaurant/` — an older copy (`views.py` is 1,105 lines there
   vs 3,136 in the live one). Left in place; safe to delete.
4. **No test suite.** The root-level `check_*.py` / `*_test.py` files are ad-hoc
   scripts, not tests.
5. **No `static/` directory** — all CSS and JS is inlined, so `menu_manager.html`
   is 110 KB and nothing is cacheable.
