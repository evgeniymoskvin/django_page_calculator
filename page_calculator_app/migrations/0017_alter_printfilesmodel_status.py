# Generated by Django 4.2.13 on 2024-07-16 06:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('page_calculator_app', '0016_printfilesmodel_mark_print_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printfilesmodel',
            name='status',
            field=models.IntegerField(choices=[(0, 'Отменен'), (1, 'Актуален'), (2, 'В работе'), (3, 'Готов')], default=1, verbose_name='Статус номера'),
        ),
    ]
