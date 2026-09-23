from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nome')),
                ('slug', models.SlugField(unique=True)),
                ('allowed_domains', models.TextField(help_text='Um dominio por linha, sem protocolo. Ex.: amazon.com.br', verbose_name='dominios permitidos')),
                ('affiliate_url_template', models.CharField(blank=True, help_text='Use {url} como marcador para a URL original.', max_length=500, verbose_name='modelo de URL afiliada')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={'verbose_name': 'parceiro', 'verbose_name_plural': 'parceiros', 'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_url', models.URLField(verbose_name='URL original')),
                ('affiliate_url', models.URLField(blank=True, verbose_name='URL afiliada')),
                ('title', models.CharField(max_length=255, verbose_name='titulo')),
                ('image_url', models.URLField(blank=True, verbose_name='URL da imagem')),
                ('current_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='preco atual')),
                ('previous_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='preco anterior')),
                ('currency', models.CharField(default='BRL', max_length=3, verbose_name='moeda')),
                ('description', models.TextField(blank=True, verbose_name='descricao')),
                ('status', models.CharField(choices=[('draft', 'Rascunho'), ('reviewed', 'Revisada'), ('scheduled', 'Agendada'), ('published', 'Publicada'), ('cancelled', 'Cancelada')], default='draft', max_length=16, verbose_name='status')),
                ('source', models.CharField(choices=[('manual', 'Manual'), ('url_import', 'Importacao por URL')], default='manual', max_length=16, verbose_name='origem')),
                ('reviewed_at', models.DateTimeField(blank=True, null=True, verbose_name='revisada em')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criada em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizada em')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='promotions', to='promotions.partner', verbose_name='parceiro')),
            ],
            options={'verbose_name': 'promocao', 'verbose_name_plural': 'promocoes', 'ordering': ('-created_at',)},
        ),
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel', models.CharField(choices=[('whatsapp', 'WhatsApp'), ('telegram', 'Telegram')], max_length=16, verbose_name='canal')),
                ('body', models.TextField(help_text='Campos disponiveis: {title}, {current_price}, {previous_price}, {description}, {affiliate_url}.', verbose_name='modelo')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                ('partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_templates', to='promotions.partner', verbose_name='parceiro')),
            ],
            options={'verbose_name': 'modelo de mensagem', 'verbose_name_plural': 'modelos de mensagem'},
        ),
        migrations.AddConstraint(
            model_name='messagetemplate',
            constraint=models.UniqueConstraint(fields=('partner', 'channel'), name='unique_partner_channel_template'),
        ),
    ]