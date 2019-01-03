# Generated by Django 2.1 on 2018-08-18 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='future_alert',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='semester',
            field=models.CharField(choices=[('spr', 'Spring'), ('sum', 'Summer'), ('fal', 'Fall'), ('win', 'Winter')], max_length=10),
        ),
        migrations.AlterField(
            model_name='course',
            name='year',
            field=models.PositiveSmallIntegerField(choices=[(2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019)], default=2018),
        ),
    ]