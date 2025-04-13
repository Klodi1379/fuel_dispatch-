# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('fuelstation', '0002_rename_station_fueltank_fuel_station_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fuelstation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fuelstation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
