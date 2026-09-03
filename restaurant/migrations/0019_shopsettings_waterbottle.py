from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0018_cartoffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopsettings',
            name='show_water_bottle_in_cart',
            field=models.BooleanField(default=True, help_text='Show Water Bottle quick-add in customer cart'),
        ),
        migrations.AddField(
            model_name='shopsettings',
            name='water_bottle_cart_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Override water bottle price shown in cart (0 = use menu item price)', max_digits=6),
        ),
    ]
