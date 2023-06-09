# Generated by Django 4.2 on 2023-04-29 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_item_delete_inventoryitem"),
    ]

    operations = [
        migrations.CreateModel(
            name="Barcode",
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
                ("barcode_format", models.CharField(max_length=255)),
                ("barcode_text", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.DeleteModel(
            name="Item",
        ),
    ]
