import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='nome')),
                ('platform', models.CharField(choices=[('whatsapp', 'WhatsApp'), ('telegram', 'Telegram')], max_length=16, verbose_name='plataforma')),
                ('external_reference', models.CharField(blank=True, max_length=255, verbose_name='referencia externa')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
                ('notes', models.TextField(blank=True, verbose_name='observacoes')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={'verbose_name': 'grupo de distribuicao', 'verbose_name_plural': 'grupos de distribuicao', 'ordering': ('platform', 'name')},
        ),
        migrations.CreateModel(
            name='DistributionBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_for', models.DateTimeField(default=django.utils.timezone.now, verbose_name='agendado para')),
                ('status', models.CharField(choices=[('draft', 'Rascunho'), ('scheduled', 'Agendado'), ('processing', 'Em processamento'), ('completed', 'Concluido'), ('cancelled', 'Cancelado')], default='draft', max_length=16, verbose_name='status')),
                ('message_snapshot', models.TextField(blank=True, verbose_name='mensagem congelada')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_distribution_batches', to=settings.AUTH_USER_MODEL, verbose_name='criado por')),
                ('promotion', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='distribution_batches', to='promotions.promotion', verbose_name='promocao')),
            ],
            options={'verbose_name': 'lote de distribuicao', 'verbose_name_plural': 'lotes de distribuicao', 'ordering': ('-scheduled_for',)},
        ),
        migrations.CreateModel(
            name='BatchTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pendente'), ('sent', 'Enviado'), ('failed', 'Falhou'), ('skipped', 'Ignorado')], default='pending', max_length=16, verbose_name='status')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='enviado em')),
                ('error_message', models.TextField(blank=True, verbose_name='erro')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='targets', to='distribution.distributionbatch', verbose_name='lote')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='batch_targets', to='distribution.distributiongroup', verbose_name='grupo')),
            ],
            options={'verbose_name': 'destino de lote', 'verbose_name_plural': 'destinos de lote'},
        ),
        migrations.AddConstraint(
            model_name='distributiongroup',
            constraint=models.UniqueConstraint(fields=('platform', 'name'), name='unique_group_name_per_platform'),
        ),
        migrations.AddConstraint(
            model_name='batchtarget',
            constraint=models.UniqueConstraint(fields=('batch', 'group'), name='unique_group_per_batch'),
        ),
    ]