from django.urls import path
from . import views

urlpatterns = [
    # Customer
    path('', views.table_selection, name='table_selection'),
    path('takeaway/', views.takeaway_menu, name='takeaway'),
    path('table/<int:table_id>/menu/', views.menu_view, name='menu'),
    path('order/place/', views.place_order, name='place_order'),
    path('order/<int:order_id>/status/', views.order_status, name='order_status'),
    path('order/<int:order_id>/bill/', views.bill_view, name='bill'),
    path('order/<int:order_id>/bill/download/', views.download_bill, name='download_bill'),
    path('order/<int:order_id>/pay-online/', views.pay_online, name='pay_online'),
    path('order/<int:order_id>/confirm-payment/', views.confirm_payment, name='confirm_payment'),
    path('order/<int:order_id>/reorder/', views.reorder, name='reorder'),
    path('order/<int:order_id>/reorder-menu/', views.reorder_menu, name='reorder_menu'),
    path('order/<int:order_id>/add-items/', views.add_items_to_order, name='add_items_to_order'),
    path('order/<int:order_id>/print-bill/', views.print_bill, name='print_bill'),

    # Customer auth & history
    path('customer/guest/', views.guest_login, name='guest_login'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/start/', views.order_type_select, name='order_type_select'),
    path('customer/home/', views.customer_history, name='customer_home'),
    path('customer/logout/', views.customer_logout, name='customer_logout'),
    path('customer/history/', views.customer_history, name='customer_history'),

    # Live Order page
    path('live-order/', views.live_order, name='live_order'),
    path('live-order/data/', views.live_order_data, name='live_order_data'),
    path('combo/<int:combo_id>/detail/', views.combo_detail_api, name='combo_detail'),

    # POS Terminal
    path('pos/', views.pos_portal, name='pos_portal'),
    path('pos/terminal/', views.pos_terminal, name='pos_terminal'),
    path('pos/save-draft/', views.pos_save_draft, name='pos_save_draft'),
    path('pos/save-order/', views.pos_save_order, name='pos_save_order'),
    path('pos/save-draft-no-auth/', views.pos_save_draft_no_auth, name='pos_save_draft_no_auth'),
    path('pos/drafts/', views.pos_get_drafts, name='pos_get_drafts'),
    path('pos/draft/<int:draft_id>/delete/', views.pos_delete_draft, name='pos_delete_draft'),

    # Staff
    path('staff/', views.staff_portal, name='staff_portal'),
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/order/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('staff/order/<int:order_id>/items/', views.staff_order_items_get, name='staff_order_items_get'),
    path('staff/order/<int:order_id>/edit-items/', views.staff_edit_order_items, name='staff_edit_order_items'),
    path('staff/orders/pending/', views.pending_orders_api, name='pending_orders_api'),
    path('staff/orders/live/', views.live_pos_orders_api, name='live_pos_orders_api'),
    path('pos/cart-live/', views.pos_cart_live_push, name='pos_cart_live_push'),
    path('staff/orders/reorders/', views.reorder_notification_api, name='reorder_notification_api'),
    path('staff/export/excel/', views.export_excel, name='export_excel'),
    path('staff/export/daily/', views.export_daily_excel, name='export_daily_excel'),
    path('staff/export/weekly/', views.export_weekly_excel, name='export_weekly_excel'),
    path('staff/export/monthly/', views.export_monthly_excel, name='export_monthly_excel'),
    path('staff/export/range/', views.export_range_excel, name='export_range_excel'),
    path('staff/qr-codes/', views.download_qr_codes, name='download_qr_codes'),

    # Items Portal (Zomato/Swiggy-style menu management)
    path('staff/items/', views.items_portal, name='items_portal'),
    path('staff/items/<int:item_id>/toggle/', views.items_portal_toggle, name='items_portal_toggle'),
    path('staff/items/<int:item_id>/price/', views.items_portal_update_price, name='items_portal_update_price'),
    path('staff/items/<int:item_id>/delete/', views.items_portal_delete_item, name='items_portal_delete_item'),
    # Items Portal — inline add/edit/image
    path('staff/items/add/', views.items_portal_add_item, name='items_portal_add'),
    path('staff/items/<int:item_id>/edit/', views.items_portal_edit_item, name='items_portal_edit'),
    path('staff/items/<int:item_id>/get/', views.items_portal_get_item, name='items_portal_get'),

    # Menu Manager — main page
    path('manage/', views.menu_manager, name='menu_manager'),

    # Menu Manager APIs
    path('manage/api/categories/', views.mm_categories, name='mm_categories'),
    path('manage/api/categories/save/', views.mm_category_save, name='mm_category_add'),
    path('manage/api/categories/<int:cat_id>/save/', views.mm_category_save, name='mm_category_edit'),
    path('manage/api/categories/<int:cat_id>/toggle/', views.mm_category_toggle, name='mm_category_toggle'),
    path('manage/api/categories/<int:cat_id>/delete/', views.mm_category_delete, name='mm_category_delete'),

    path('manage/api/combos/', views.mm_combos, name='mm_combos'),
    path('manage/api/combos/save/', views.mm_combo_save, name='mm_combo_add'),
    path('manage/api/combos/<int:combo_id>/save/', views.mm_combo_save, name='mm_combo_edit'),
    path('manage/api/combos/<int:combo_id>/toggle/', views.mm_combo_toggle, name='mm_combo_toggle'),
    path('manage/api/combos/<int:combo_id>/delete/', views.mm_combo_delete, name='mm_combo_delete'),

    path('manage/api/discounts/', views.mm_discounts, name='mm_discounts'),
    path('manage/api/discounts/save/', views.mm_discount_save, name='mm_discount_add'),
    path('manage/api/discounts/<int:disc_id>/save/', views.mm_discount_save, name='mm_discount_edit'),
    path('manage/api/discounts/<int:disc_id>/delete/', views.mm_discount_delete, name='mm_discount_delete'),

    path('manage/api/offers/', views.mm_offers, name='mm_offers'),
    path('manage/api/offers/save/', views.mm_offer_save, name='mm_offer_add'),
    path('manage/api/offers/<int:offer_id>/save/', views.mm_offer_save, name='mm_offer_edit'),
    path('manage/api/offers/<int:offer_id>/toggle/', views.mm_offer_toggle, name='mm_offer_toggle'),
    path('offer/<int:offer_id>/', views.offer_page, name='offer_page'),
    path('manage/api/offers/<int:offer_id>/delete/', views.mm_offer_delete, name='mm_offer_delete'),

    path('manage/api/cart-offers/', views.mm_cart_offers, name='mm_cart_offers'),
    path('manage/api/cart-offers/save/', views.mm_cart_offer_save, name='mm_cart_offer_add'),
    path('manage/api/cart-offers/<int:cart_offer_id>/save/', views.mm_cart_offer_save, name='mm_cart_offer_edit'),
    path('manage/api/cart-offers/<int:cart_offer_id>/delete/', views.mm_cart_offer_delete, name='mm_cart_offer_delete'),

    path('manage/api/tables/', views.mm_tables, name='mm_tables'),
    path('manage/api/tables/save/', views.mm_table_save, name='mm_table_add'),
    path('manage/api/tables/<int:table_id>/save/', views.mm_table_save, name='mm_table_edit'),
    path('manage/api/tables/<int:table_id>/delete/', views.mm_table_delete, name='mm_table_delete'),

    path('manage/api/customers/', views.mm_customers, name='mm_customers'),
    path('manage/api/shop/', views.mm_shop_settings, name='mm_shop_settings'),
    path('manage/api/shop/save/', views.mm_shop_settings_save, name='mm_shop_settings_save'),

    path('manage/api/orders/', views.mm_orders, name='mm_orders'),

    # Drag-and-drop reorder APIs
    path('manage/api/categories/reorder/', views.mm_category_reorder, name='mm_category_reorder'),
    path('manage/api/categories/<int:cat_id>/items/', views.mm_items_by_category, name='mm_items_by_category'),
    path('manage/api/items/reorder/', views.mm_items_reorder, name='mm_items_reorder'),
]