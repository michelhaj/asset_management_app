# Generated by Django 4.2 on 2023-04-29 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0002_inventoryitem_delete_barcode"),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("barcode", models.CharField(max_length=100)),
                ("quantity", models.IntegerField()),
            ],
        ),
        migrations.DeleteModel(
            name="InventoryItem",
        ),
    ]