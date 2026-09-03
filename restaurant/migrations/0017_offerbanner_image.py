from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0016_offerbanner_upgrade'),
    ]

    operations = [
        migrations.AddField(
            model_name='offerbanner',
            name='image',
            field=models.ImageField(blank=True, help_text='Upload banner image', null=True, upload_to='offer_banners/'),
        ),
    ]
