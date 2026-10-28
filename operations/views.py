from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import QueryDict
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView

from distribution.models import BatchTarget, DistributionBatch, DistributionGroup
from promotions.models import MessageTemplate, Partner, Promotion

from .forms import (
    DistributionBatchForm,
    DistributionGroupForm,
    MessageTemplateForm,
    PromotionForm,
    QuickCreateForm,
)


class HomeRedirectView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect('operations:dashboard')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'operations/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['promotion_totals'] = (
            Promotion.objects.values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        context['recent_promotions'] = Promotion.objects.select_related('partner')[:5]
        context['recent_batches'] = DistributionBatch.objects.select_related('promotion', 'created_by')[:5]
        context['target_status_totals'] = (
            BatchTarget.objects.values('status')
            .annotate(total=Count('id'))
            .order_by('status')
        )
        context['failed_targets'] = BatchTarget.objects.select_related(
            'batch__promotion', 'group'
        ).filter(status=BatchTarget.Status.FAILED)[:8]
        return context


class PromotionListView(LoginRequiredMixin, ListView):
    model = Promotion
    template_name = 'operations/promotions/list.html'
    context_object_name = 'promotions'
    paginate_by = 25

    def get_queryset(self):
        queryset = Promotion.objects.select_related('partner')
        query = self.request.GET.get('q', '').strip()
        status = self.request.GET.get('status', '').strip()
        source = self.request.GET.get('source', '').strip()
        partner = self.request.GET.get('partner', '').strip()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(original_url__icontains=query)
                | Q(affiliate_url__icontains=query)
            )
        if status:
            queryset = queryset.filter(status=status)
        if source:
            queryset = queryset.filter(source=source)
        if partner:
            queryset = queryset.filter(partner_id=partner)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Promotion.Status.choices
        context['source_choices'] = Promotion.Source.choices
        context['partners'] = Partner.objects.order_by('name')
        context['filters'] = {
            'q': self.request.GET.get('q', '').strip(),
            'status': self.request.GET.get('status', '').strip(),
            'source': self.request.GET.get('source', '').strip(),
            'partner': self.request.GET.get('partner', '').strip(),
        }
        context['querystring'] = _querystring_without_page(self.request.GET)
        return context


class PromotionCreateView(LoginRequiredMixin, CreateView):
    model = Promotion
    form_class = PromotionForm
    template_name = 'operations/promotions/form.html'
    success_url = reverse_lazy('operations:promotions-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Promocao criada com sucesso.')
        return response


class PromotionUpdateView(LoginRequiredMixin, UpdateView):
    model = Promotion
    form_class = PromotionForm
    template_name = 'operations/promotions/form.html'
    success_url = reverse_lazy('operations:promotions-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Promocao atualizada com sucesso.')
        return response


class PromotionDetailView(LoginRequiredMixin, DetailView):
    model = Promotion
    template_name = 'operations/promotions/detail.html'
    context_object_name = 'promotion'


class PromotionDeleteView(LoginRequiredMixin, DeleteView):
    model = Promotion
    template_name = 'operations/confirm_delete.html'
    success_url = reverse_lazy('operations:promotions-list')

    def form_valid(self, form):
        messages.success(self.request, 'Promocao excluida com sucesso.')
        return super().form_valid(form)


class DistributionGroupListView(LoginRequiredMixin, ListView):
    model = DistributionGroup
    template_name = 'operations/groups/list.html'
    context_object_name = 'groups'
    paginate_by = 25

    def get_queryset(self):
        queryset = DistributionGroup.objects.all()
        query = self.request.GET.get('q', '').strip()
        platform = self.request.GET.get('platform', '').strip()
        is_active = self.request.GET.get('is_active', '').strip()
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(external_reference__icontains=query))
        if platform:
            queryset = queryset.filter(platform=platform)
        if is_active in {'true', 'false'}:
            queryset = queryset.filter(is_active=(is_active == 'true'))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['platform_choices'] = DistributionGroup.Platform.choices
        context['filters'] = {
            'q': self.request.GET.get('q', '').strip(),
            'platform': self.request.GET.get('platform', '').strip(),
            'is_active': self.request.GET.get('is_active', '').strip(),
        }
        context['querystring'] = _querystring_without_page(self.request.GET)
        return context


class DistributionGroupCreateView(LoginRequiredMixin, CreateView):
    model = DistributionGroup
    form_class = DistributionGroupForm
    template_name = 'operations/groups/form.html'
    success_url = reverse_lazy('operations:groups-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Grupo criado com sucesso.')
        return response


class DistributionGroupUpdateView(LoginRequiredMixin, UpdateView):
    model = DistributionGroup
    form_class = DistributionGroupForm
    template_name = 'operations/groups/form.html'
    success_url = reverse_lazy('operations:groups-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Grupo atualizado com sucesso.')
        return response


class DistributionGroupDeleteView(LoginRequiredMixin, DeleteView):
    model = DistributionGroup
    template_name = 'operations/confirm_delete.html'
    success_url = reverse_lazy('operations:groups-list')

    def form_valid(self, form):
        messages.success(self.request, 'Grupo excluido com sucesso.')
        return super().form_valid(form)


class DistributionBatchListView(LoginRequiredMixin, ListView):
    model = DistributionBatch
    template_name = 'operations/batches/list.html'
    context_object_name = 'batches'
    paginate_by = 25

    def get_queryset(self):
        queryset = DistributionBatch.objects.select_related('promotion', 'created_by')
        status = self.request.GET.get('status', '').strip()
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = DistributionBatch.Status.choices
        context['filters'] = {
            'status': self.request.GET.get('status', '').strip(),
        }
        context['querystring'] = _querystring_without_page(self.request.GET)
        return context


class DistributionBatchDetailView(LoginRequiredMixin, DetailView):
    model = DistributionBatch
    template_name = 'operations/batches/detail.html'
    context_object_name = 'batch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['targets'] = self.object.targets.select_related('group').order_by('group__platform', 'group__name')
        return context


class DistributionBatchCreateView(LoginRequiredMixin, CreateView):
    model = DistributionBatch
    form_class = DistributionBatchForm
    template_name = 'operations/batches/form.html'
    success_url = reverse_lazy('operations:batches-list')

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        messages.success(self.request, 'Lote criado com sucesso.')
        return redirect(self.success_url)


class DistributionBatchUpdateView(LoginRequiredMixin, UpdateView):
    model = DistributionBatch
    form_class = DistributionBatchForm
    template_name = 'operations/batches/form.html'
    success_url = reverse_lazy('operations:batches-list')

    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        messages.success(self.request, 'Lote atualizado com sucesso.')
        return redirect(self.success_url)


class DistributionBatchDeleteView(LoginRequiredMixin, DeleteView):
    model = DistributionBatch
    template_name = 'operations/confirm_delete.html'
    success_url = reverse_lazy('operations:batches-list')

    def form_valid(self, form):
        messages.success(self.request, 'Lote excluido com sucesso.')
        return super().form_valid(form)


class MessageTemplateListView(LoginRequiredMixin, ListView):
    model = MessageTemplate
    template_name = 'operations/templates/list.html'
    context_object_name = 'message_templates'
    paginate_by = 25

    def get_queryset(self):
        queryset = MessageTemplate.objects.select_related('partner')
        channel = self.request.GET.get('channel', '').strip()
        if channel:
            queryset = queryset.filter(channel=channel)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_choices'] = MessageTemplate.Channel.choices
        context['filters'] = {'channel': self.request.GET.get('channel', '').strip()}
        context['querystring'] = _querystring_without_page(self.request.GET)
        return context


class MessageTemplateCreateView(LoginRequiredMixin, CreateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'operations/templates/form.html'
    success_url = reverse_lazy('operations:templates-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Modelo de mensagem criado com sucesso.')
        return response


class MessageTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = MessageTemplate
    form_class = MessageTemplateForm
    template_name = 'operations/templates/form.html'
    success_url = reverse_lazy('operations:templates-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Modelo de mensagem atualizado com sucesso.')
        return response


class MessageTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = MessageTemplate
    template_name = 'operations/confirm_delete.html'
    success_url = reverse_lazy('operations:templates-list')

    def form_valid(self, form):
        messages.success(self.request, 'Modelo de mensagem excluido com sucesso.')
        return super().form_valid(form)


class QuickCreateView(LoginRequiredMixin, FormView):
    template_name = 'operations/quick_create.html'
    form_class = QuickCreateForm
    success_url = reverse_lazy('operations:dashboard')

    def form_valid(self, form):
        promotion, batch = form.save(user=self.request.user)
        messages.success(
            self.request,
            f'Promocao "{promotion.title}" e lote #{batch.id} criados com sucesso.',
        )
        return super().form_valid(form)


def _querystring_without_page(query_params):
    mutable = QueryDict('', mutable=True)
    for key, value in query_params.items():
        if key != 'page':
            mutable[key] = value
    encoded = mutable.urlencode()
    return f'{encoded}&' if encoded else ''
