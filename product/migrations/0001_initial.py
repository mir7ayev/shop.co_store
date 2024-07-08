# Generated by Django 5.0.6 on 2024-07-05 00:29

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductColor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='ProductSize',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=120)),
                ('gender', models.IntegerField(choices=[(1, 'Men'), (2, 'Women'), (3, 'Baby')], default=1)),
                ('image', models.ImageField(upload_to='products/')),
                ('description', ckeditor.fields.RichTextField()),
                ('price', models.FloatField()),
                ('discount', models.IntegerField(default=0)),
                ('price_with_discount', models.FloatField(blank=True, default=0, null=True)),
                ('is_available', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productcategory')),
                ('color', models.ManyToManyField(blank=True, to='product.productcolor')),
                ('size', models.ManyToManyField(blank=True, to='product.productsize')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]