from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0017_offerbanner_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='e.g. Mega Saver Deal', max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=250)),
                ('min_cart_value', models.DecimalField(decimal_places=2, default=0, help_text='Minimum cart total to unlock this offer', max_digits=8)),
                ('reward_type', models.CharField(choices=[('percent', '% Discount'), ('flat', 'Flat ₹ Discount'), ('free_item', 'Free Item')], default='percent', max_length=20)),
                ('percent_off', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('flat_off', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('free_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cart_offers', to='restaurant.menuitem')),
                ('emoji', models.CharField(default='🎁', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Cart Offer',
                'verbose_name_plural': 'Cart Offers',
                'ordering': ['min_cart_value', 'order'],
            },
        ),
    ]
