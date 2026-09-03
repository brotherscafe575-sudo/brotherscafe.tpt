from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0013_order_cash_received_order_change_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferBanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='e.g. Weekend Special', max_length=200)),
                ('subtitle', models.CharField(blank=True, help_text='Short line shown under the title', max_length=250)),
                ('off_percent', models.DecimalField(decimal_places=2, default=0, help_text='% OFF shown on the banner', max_digits=5)),
                ('emoji', models.CharField(blank=True, default='🎉', max_length=10)),
                ('bg_color', models.CharField(default='#e74c3c', help_text='Banner colour (hex)', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Offer Banner',
                'verbose_name_plural': 'Offer Banners',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
