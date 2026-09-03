from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0024_menuitem_is_water_bottle'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ring_count',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Incremented each time staff manually rings/vibrates the customer phone'),
        ),
    ]
