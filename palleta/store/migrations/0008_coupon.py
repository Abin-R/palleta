# Generated by Django 4.2.3 on 2023-07-29 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_wishlist_wishlistitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('valid_from', models.DateTimeField()),
                ('valid_to', models.DateTimeField()),
                ('minimum_order_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('single_use_per_user', models.BooleanField(default=False)),
                ('quantity', models.PositiveIntegerField(default=1)),
            ],
        ),
    ]
