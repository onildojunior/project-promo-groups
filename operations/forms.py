from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from distribution.models import BatchTarget, DistributionBatch, DistributionGroup
from promotions.models import MessageTemplate, Partner, Promotion


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = (
            'partner',
            'title',
            'original_url',
            'affiliate_url',
            'image_url',
            'current_price',
            'previous_price',
            'currency',
            'description',
            'source',
            'status',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class DistributionGroupForm(forms.ModelForm):
    class Meta:
        model = DistributionGroup
        fields = ('name', 'platform', 'external_reference', 'is_active', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class DistributionBatchForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=DistributionGroup.objects.filter(is_active=True).order_by('platform', 'name'),
        required=True,
        label='Grupos de destino',
    )

    class Meta:
        model = DistributionBatch
        fields = ('promotion', 'scheduled_for', 'status', 'message_snapshot')
        widgets = {
            'scheduled_for': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'message_snapshot': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            selected_groups = DistributionGroup.objects.filter(
                batch_targets__batch=self.instance
            ).order_by('platform', 'name')
            self.fields['groups'].queryset = (
                DistributionGroup.objects.filter(is_active=True) | selected_groups
            ).distinct().order_by('platform', 'name')
            self.fields['groups'].initial = selected_groups

    @transaction.atomic
    def save(self, user, commit=True):
        batch = super().save(commit=False)
        if not batch.pk:
            batch.created_by = user
        if commit:
            batch.save()
            selected_groups = list(self.cleaned_data['groups'])
            existing_targets = {target.group_id: target for target in batch.targets.select_related('group')}

            for group in selected_groups:
                if group.id not in existing_targets:
                    BatchTarget.objects.create(batch=batch, group=group)

            selected_ids = {group.id for group in selected_groups}
            for group_id, target in existing_targets.items():
                if group_id not in selected_ids:
                    target.delete()

        return batch


class MessageTemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ('partner', 'channel', 'body', 'is_active')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 5}),
        }


class QuickCreateForm(forms.Form):
    partner = forms.ModelChoiceField(queryset=Partner.objects.filter(is_active=True).order_by('name'), label='Parceiro')
    title = forms.CharField(max_length=255, label='Titulo')
    original_url = forms.URLField(label='URL original')
    affiliate_url = forms.URLField(label='URL afiliada')
    image_url = forms.URLField(required=False, label='URL da imagem')
    current_price = forms.DecimalField(max_digits=10, decimal_places=2, label='Preco atual')
    previous_price = forms.DecimalField(max_digits=10, decimal_places=2, required=False, label='Preco anterior')
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Descricao')
    promotion_status = forms.ChoiceField(choices=Promotion.Status.choices, initial=Promotion.Status.REVIEWED, label='Status da promocao')
    source = forms.ChoiceField(choices=Promotion.Source.choices, initial=Promotion.Source.MANUAL, label='Origem')
    scheduled_for = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), label='Agendar lote para')
    batch_status = forms.ChoiceField(choices=DistributionBatch.Status.choices, initial=DistributionBatch.Status.DRAFT, label='Status do lote')
    message_snapshot = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), label='Mensagem congelada')
    groups = forms.ModelMultipleChoiceField(
        queryset=DistributionGroup.objects.filter(is_active=True).order_by('platform', 'name'),
        label='Grupos de destino',
    )

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data

        promotion = Promotion(
            partner=cleaned_data['partner'],
            title=cleaned_data['title'],
            original_url=cleaned_data['original_url'],
            affiliate_url=cleaned_data['affiliate_url'],
            image_url=cleaned_data['image_url'],
            current_price=cleaned_data['current_price'],
            previous_price=cleaned_data['previous_price'],
            description=cleaned_data['description'],
            status=cleaned_data['promotion_status'],
            source=cleaned_data['source'],
        )

        try:
            promotion.full_clean()
        except ValidationError as error:
            for field, messages in error.message_dict.items():
                form_field = 'promotion_status' if field == 'status' else field
                for message in messages:
                    self.add_error(form_field, message)

        if not self.errors:
            batch = DistributionBatch(
                promotion=promotion,
                scheduled_for=cleaned_data['scheduled_for'],
                status=cleaned_data['batch_status'],
                message_snapshot=cleaned_data['message_snapshot'],
                created_by=None,
            )
            try:
                batch.full_clean(exclude=['created_by'])
            except ValidationError as error:
                for field, messages in error.message_dict.items():
                    form_field = 'batch_status' if field == 'status' else field
                    for message in messages:
                        self.add_error(form_field, message)

        return cleaned_data

    @transaction.atomic
    def save(self, user):
        promotion = Promotion(
            partner=self.cleaned_data['partner'],
            title=self.cleaned_data['title'],
            original_url=self.cleaned_data['original_url'],
            affiliate_url=self.cleaned_data['affiliate_url'],
            image_url=self.cleaned_data['image_url'],
            current_price=self.cleaned_data['current_price'],
            previous_price=self.cleaned_data['previous_price'],
            description=self.cleaned_data['description'],
            status=self.cleaned_data['promotion_status'],
            source=self.cleaned_data['source'],
        )
        promotion.save()

        batch = DistributionBatch(
            promotion=promotion,
            scheduled_for=self.cleaned_data['scheduled_for'],
            status=self.cleaned_data['batch_status'],
            message_snapshot=self.cleaned_data['message_snapshot'],
            created_by=user,
        )
        batch.save()

        BatchTarget.objects.bulk_create(
            [BatchTarget(batch=batch, group=group) for group in self.cleaned_data['groups']]
        )

        return promotion, batch
