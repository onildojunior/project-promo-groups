from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Partner(models.Model):
    name = models.CharField('nome', max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    allowed_domains = models.TextField(
        'dominios permitidos',
        help_text='Um dominio por linha, sem protocolo. Ex.: amazon.com.br',
    )
    affiliate_url_template = models.CharField(
        'modelo de URL afiliada',
        max_length=500,
        blank=True,
        help_text='Use {url} como marcador para a URL original.',
    )
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'parceiro'
        verbose_name_plural = 'parceiros'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def allowed_domain_list(self):
        return [domain.strip().lower() for domain in self.allowed_domains.splitlines() if domain.strip()]

    def clean(self):
        super().clean()
        if self.affiliate_url_template and '{url}' not in self.affiliate_url_template:
            raise ValidationError({'affiliate_url_template': 'O modelo deve conter o marcador {url}.'})


class Promotion(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        REVIEWED = 'reviewed', 'Revisada'
        SCHEDULED = 'scheduled', 'Agendada'
        PUBLISHED = 'published', 'Publicada'
        CANCELLED = 'cancelled', 'Cancelada'

    class Source(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        URL_IMPORT = 'url_import', 'Importacao por URL'

    partner = models.ForeignKey(Partner, verbose_name='parceiro', on_delete=models.PROTECT, related_name='promotions')
    original_url = models.URLField('URL original')
    affiliate_url = models.URLField('URL afiliada', blank=True)
    title = models.CharField('titulo', max_length=255)
    image_url = models.URLField('URL da imagem', blank=True)
    current_price = models.DecimalField('preco atual', max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    previous_price = models.DecimalField('preco anterior', max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField('moeda', max_length=3, default='BRL')
    description = models.TextField('descricao', blank=True)
    status = models.CharField('status', max_length=16, choices=Status.choices, default=Status.DRAFT)
    source = models.CharField('origem', max_length=16, choices=Source.choices, default=Source.MANUAL)
    reviewed_at = models.DateTimeField('revisada em', blank=True, null=True)
    created_at = models.DateTimeField('criada em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizada em', auto_now=True)

    class Meta:
        verbose_name = 'promocao'
        verbose_name_plural = 'promocoes'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.previous_price is not None and self.previous_price <= self.current_price:
            raise ValidationError({'previous_price': 'O preco anterior deve ser maior que o preco atual.'})
        if self.status in {self.Status.REVIEWED, self.Status.SCHEDULED, self.Status.PUBLISHED} and not self.affiliate_url:
            raise ValidationError({'affiliate_url': 'Uma promocao revisada ou posterior precisa de uma URL afiliada.'})


class MessageTemplate(models.Model):
    class Channel(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        TELEGRAM = 'telegram', 'Telegram'

    partner = models.ForeignKey(Partner, verbose_name='parceiro', on_delete=models.CASCADE, related_name='message_templates', blank=True, null=True)
    channel = models.CharField('canal', max_length=16, choices=Channel.choices)
    body = models.TextField(
        'modelo',
        help_text='Campos disponiveis: {title}, {current_price}, {previous_price}, {description}, {affiliate_url}.',
    )
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'modelo de mensagem'
        verbose_name_plural = 'modelos de mensagem'
        constraints = [
            models.UniqueConstraint(fields=('partner', 'channel'), name='unique_partner_channel_template'),
        ]

    def __str__(self):
        partner_name = self.partner.name if self.partner else 'Padrao'
        return f'{partner_name} - {self.get_channel_display()}'