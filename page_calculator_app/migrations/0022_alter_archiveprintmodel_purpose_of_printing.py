# Generated by Django 4.2.13 on 2024-10-16 07:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page_calculator_app', '0021_alter_printfilesmodel_print_from_archive_details'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archiveprintmodel',
            name='purpose_of_printing',
            field=models.IntegerField(choices=[(2, 'Для аннулирования (печать титульного листа и обложки)'), (1, 'Для внесения изменений (печать альбома целиком)')], default=0, verbose_name='Тип вносимых изменений:'),
        ),
    ]
