# Generated by Django 5.2 on 2025-05-15 21:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fintrack', '0002_tag_financialrecord_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField()),
                ('expense_limit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('income_target', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-month'],
                'unique_together': {('user', 'month')},
            },
        ),
    ]
