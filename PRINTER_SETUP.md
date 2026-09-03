# 🖨️ Helett POS80 — Direct / Silent Printing Setup

The app now auto-opens the bill and calls print automatically:
- **Staff Portal → Accept order** → bill window opens, prints, and closes itself
- **Staff Portal → 🖨 Print Bill button** → prints directly (`?auto=1`)
- **POS Terminal → 🖨️ Bill button** → prints directly, no preview modal

By default the browser still shows its Print dialog once (the screen in your
screenshot with "Destination: POS80"). To make it print with **ZERO clicks**
(no dialog at all), do this one-time setup on the billing PC:

## Step 1 — Make POS80 the default printer (Windows)
1. Settings → Bluetooth & devices → **Printers & scanners**
2. Turn OFF "Let Windows manage my default printer"
3. Click **POS80** → **Set as default**

## Step 2 — Launch the browser in kiosk-printing mode
Kiosk-printing makes the browser send every print job straight to the
default printer with no dialog.

### Chrome / Edge / Brave shortcut
1. Right-click the browser shortcut on the desktop → **Properties**
2. In **Target**, add ` --kiosk-printing` at the end (note the space):

   Chrome:
   ```
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk-printing
   ```
   Brave:
   ```
   "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --kiosk-printing
   ```
   Edge:
   ```
   "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk-printing
   ```
3. Click OK. **Close ALL browser windows first**, then open the browser
   using this shortcut and log in to the Staff Portal / POS Terminal.

Now every Accept / Print Bill / Bill click prints instantly on the POS80
with no dialog — the popup opens, prints, and closes by itself.

## Step 3 — Paper size (one time, if the receipt looks wrong)
In the printer driver (Printers & scanners → POS80 → Printing preferences),
set paper to **80mm (72.1mm printable) × receipt/continuous**. The bill page
is already styled for 80mm thermal paper (`@page { size: 80mm auto }`).

## Step 4 — AUTO-CUT between customer bill and staff copy ✂️
The customer bill and staff copy print as two separate pages, so the
printer's cutter can cut them apart automatically. Enable it once:

1. Settings → Printers & scanners → **POS80** → **Printing preferences**
2. Look for a tab like **Document Settings / Paper / Advanced**
3. Find the **Paper Cut / Cut Options** setting
4. Change it from "Cut at end of document" to **"Cut per page"**
   (may be called: *Partial cut at end of page*, *Feed & cut per page*,
   or *Cut: Every page*)
5. Click Apply → OK

Now every print = customer bill → CUT → staff copy → CUT. Hand one to
the customer, one to the kitchen.

## Tips
- Allow popups for your site the first time the browser asks
  (Site settings → Pop-ups → Allow) so the bill window can open.
- If a bill window ever stays open, it's safe to close — the job was
  already sent to the printer.
