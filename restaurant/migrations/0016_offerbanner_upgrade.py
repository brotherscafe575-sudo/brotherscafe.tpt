from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0015_create_default_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerbanner',
            name='offer_type',
            field=models.CharField(choices=[('percent', '% OFF'), ('flat', 'Flat ₹ OFF'), ('bogo', 'Buy 1 Get 1 Free')], default='percent', max_length=10),
        ),
        migrations.AddField(
            model_name='offerbanner',
            name='flat_amount',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Flat ₹ OFF (for flat type)', max_digits=8),
        ),
        migrations.AddField(
            model_name='offerbanner',
            name='image_url',
            field=models.URLField(blank=True, default='', help_text='Banner image URL (optional)'),
        ),
        migrations.AddField(
            model_name='offerbanner',
            name='menu_items',
            field=models.ManyToManyField(blank=True, help_text='Linked menu items for this offer', to='restaurant.menuitem'),
        ),
    ]
