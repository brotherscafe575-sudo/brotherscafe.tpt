from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0025_order_ring_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='ring_count',
        ),
    ]
