# Generated by Django 2.2.12 on 2021-10-24 10:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('quant', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='ohlcv',
            unique_together={('exchange', 'symbol', 'period')},
        ),
        migrations.AlterIndexTogether(
            name='ohlcv',
            index_together={('exchange', 'symbol', 'period')},
        ),
        migrations.AddField(
            model_name='coinposition',
            name='coin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quant.Coin'),
        ),
        migrations.AddField(
            model_name='coin',
            name='strategy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quant.Strategy'),
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='signal',
            index=models.Index(fields=['symbol', 'period'], name='quant_signa_symbol_92507b_idx'),
        ),
        migrations.AddIndex(
            model_name='signal',
            index=models.Index(fields=['symbol', 'strategy'], name='quant_signa_symbol_4f33d5_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='coinposition',
            unique_together={('coin', 'position')},
        ),
        migrations.AlterUniqueTogether(
            name='coin',
            unique_together={('exchange', 'symbol', 'spot_symbol')},
        ),
    ]
