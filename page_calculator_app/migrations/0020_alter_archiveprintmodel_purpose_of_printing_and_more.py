# Generated by Django 4.2.13 on 2024-10-15 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page_calculator_app', '0019_archiveprintmodel_printfilesmodel_print_from_archive_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archiveprintmodel',
            name='purpose_of_printing',
            field=models.IntegerField(choices=[(2, 'Для аннулирования (печать титульных листов'), (1, 'Для внесения изменений')], default=0, verbose_name='Тип вносимых изменений:'),
        ),
        migrations.AlterField(
            model_name='printfilesmodel',
            name='filename',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Название файла'),
        ),
    ]