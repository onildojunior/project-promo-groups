from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from promotions.models import Promotion


class DistributionGroup(models.Model):
    class Platform(models.TextChoices):
        WHATSAPP = 'whatsapp', 'WhatsApp'
        TELEGRAM = 'telegram', 'Telegram'

    name = models.CharField('nome', max_length=120)
    platform = models.CharField('plataforma', max_length=16, choices=Platform.choices)
    external_reference = models.CharField('referencia externa', max_length=255, blank=True)
    is_active = models.BooleanField('ativo', default=True)
    notes = models.TextField('observacoes', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'grupo de distribuicao'
        verbose_name_plural = 'grupos de distribuicao'
        ordering = ('platform', 'name')
        constraints = [
            models.UniqueConstraint(fields=('platform', 'name'), name='unique_group_name_per_platform'),
        ]

    def __str__(self):
        return f'{self.name} ({self.get_platform_display()})'


class DistributionBatch(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Rascunho'
        SCHEDULED = 'scheduled', 'Agendado'
        PROCESSING = 'processing', 'Em processamento'
        COMPLETED = 'completed', 'Concluido'
        CANCELLED = 'cancelled', 'Cancelado'

    promotion = models.ForeignKey(Promotion, verbose_name='promocao', on_delete=models.PROTECT, related_name='distribution_batches')
    scheduled_for = models.DateTimeField('agendado para', default=timezone.now)
    status = models.CharField('status', max_length=16, choices=Status.choices, default=Status.DRAFT)
    message_snapshot = models.TextField('mensagem congelada', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='criado por', on_delete=models.PROTECT, related_name='created_distribution_batches')
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'lote de distribuicao'
        verbose_name_plural = 'lotes de distribuicao'
        ordering = ('-scheduled_for',)

    def __str__(self):
        return f'Lote #{self.pk or "novo"} - {self.promotion}'

    def clean(self):
        super().clean()
        if self.status in {self.Status.SCHEDULED, self.Status.PROCESSING, self.Status.COMPLETED}:
            if self.promotion.status not in {Promotion.Status.REVIEWED, Promotion.Status.SCHEDULED, Promotion.Status.PUBLISHED}:
                raise ValidationError({'promotion': 'A promocao deve ser revisada antes de agendar ou processar um lote.'})
            if not self.message_snapshot:
                raise ValidationError({'message_snapshot': 'O lote precisa de uma mensagem congelada antes do agendamento.'})


class BatchTarget(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendente'
        SENT = 'sent', 'Enviado'
        FAILED = 'failed', 'Falhou'
        SKIPPED = 'skipped', 'Ignorado'

    batch = models.ForeignKey(DistributionBatch, verbose_name='lote', on_delete=models.CASCADE, related_name='targets')
    group = models.ForeignKey(DistributionGroup, verbose_name='grupo', on_delete=models.PROTECT, related_name='batch_targets')
    status = models.CharField('status', max_length=16, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField('enviado em', blank=True, null=True)
    error_message = models.TextField('erro', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'destino de lote'
        verbose_name_plural = 'destinos de lote'
        constraints = [
            models.UniqueConstraint(fields=('batch', 'group'), name='unique_group_per_batch'),
        ]

    def __str__(self):
        return f'{self.batch} -> {self.group}'