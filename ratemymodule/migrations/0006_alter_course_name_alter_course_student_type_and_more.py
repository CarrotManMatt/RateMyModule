# Generated by Django 4.2.11 on 2024-03-18 06:25

import django.core.validators
from django.db import migrations, models
import ratemymodule.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ('ratemymodule', '0005_alter_othertag_name_alter_tooltag_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='name',
            field=models.CharField(max_length=60, validators=[django.core.validators.MinLengthValidator(3), ratemymodule.models.validators.UnicodePropertiesRegexValidator("\\A[\\p{L}\\p{N}!?¿¡' &()-]+\\Z", message='Enter a valid value: cannot contain full-stops.')], verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='course',
            name='student_type',
            field=models.CharField(max_length=60, validators=[django.core.validators.MinLengthValidator(3), ratemymodule.models.validators.UnicodePropertiesRegexValidator("\\A[\\p{L}!?¿¡' &()-]+\\Z", message='Enter a valid value: cannot contain full-stops.')], verbose_name='Student Type'),
        ),
        migrations.AlterField(
            model_name='module',
            name='code',
            field=models.CharField(help_text='The unique reference code of this module within its university', max_length=60, validators=[django.core.validators.MinLengthValidator(2), ratemymodule.models.validators.UnicodePropertiesRegexValidator("\\A[\\p{L}0-9!?¿¡' &()-]+\\Z", message='Enter a valid value: cannot contain full-stops.')], verbose_name='Reference Code'),
        ),
        migrations.AlterField(
            model_name='module',
            name='name',
            field=models.CharField(max_length=60, validators=[django.core.validators.MinLengthValidator(3), ratemymodule.models.validators.UnicodePropertiesRegexValidator("\\A[\\p{L}\\p{N}!?¿¡' &()-]+\\Z", message='Enter a valid value: cannot contain full-stops.')], verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='university',
            name='name',
            field=models.CharField(max_length=60, unique=True, validators=[django.core.validators.MinLengthValidator(2), ratemymodule.models.validators.UnicodePropertiesRegexValidator("\\A[\\p{L}!?¿¡' &()-]+\\Z", message='Enter a valid value: cannot contain full-stops.')], verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='university',
            name='short_name',
            field=models.CharField(max_length=8, validators=[django.core.validators.MinLengthValidator(2), ratemymodule.models.validators.UnicodePropertiesRegexValidator("\\A[\\p{L}!?¿¡'-]+\\Z", message='Enter a valid value: cannot contain full-stops.')], verbose_name='Short Name'),
        ),
    ]
