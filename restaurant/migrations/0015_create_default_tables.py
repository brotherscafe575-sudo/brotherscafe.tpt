from django.db import migrations


def create_default_tables(apps, schema_editor):
    """Ensure Tables 1–5 exist (for QR codes / dine-in ordering).
    Safe on existing databases: only creates missing table numbers."""
    Table = apps.get_model('restaurant', 'Table')
    for n in range(1, 6):
        Table.objects.get_or_create(
            number=n,
            defaults={
                'name': f'Table {n}',
                'capacity': 4,
                'status': 'available',
                'is_active': True,
            },
        )


def noop(apps, schema_editor):
    pass  # keep tables on rollback


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0014_offerbanner'),
    ]

    operations = [
        migrations.RunPython(create_default_tables, noop),
    ]
