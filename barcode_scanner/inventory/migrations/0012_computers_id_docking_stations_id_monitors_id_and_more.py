# Generated by Django 4.2 on 2023-05-04 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0011_alter_docking_stations_computer_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="computers",
            name="id",
            field=models.CharField(
                blank=True, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AddField(
            model_name="docking_stations",
            name="id",
            field=models.CharField(
                blank=True, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AddField(
            model_name="monitors",
            name="id",
            field=models.CharField(
                blank=True, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AddField(
            model_name="printers",
            name="id",
            field=models.CharField(
                blank=True, max_length=255, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="computers",
            name="asset_tag",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="computers",
            name="service_tag",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="docking_stations",
            name="asset_tag",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="monitors",
            name="asset_tag",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="monitors",
            name="service_tag",
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="printers",
            name="service_tag",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
