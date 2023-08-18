# Generated by Django 4.2.3 on 2023-08-11 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_productvariant_discount_percentage_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('CANCELLED', 'cancelled'), ('DELIVERED', 'Delivered'), ('SHIPPED', 'Shipped'), ('RETURNED', 'Returned'), ('ORDERED', 'Ordered')], default='Ordered', max_length=20),
        ),
    ]