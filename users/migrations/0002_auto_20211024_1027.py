# Generated by Django 2.2.12 on 2021-10-24 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='certification',
            name='user',
        ),
        migrations.RemoveField(
            model_name='reward',
            name='user',
        ),
        migrations.RemoveField(
            model_name='withdraw',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='smscaptcha',
            options={},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_points',
            field=models.IntegerField(default=0, verbose_name='累计积分'),
        ),
        migrations.DeleteModel(
            name='Billing',
        ),
        migrations.DeleteModel(
            name='Certification',
        ),
        migrations.DeleteModel(
            name='Reward',
        ),
        migrations.DeleteModel(
            name='Withdraw',
        ),
    ]
