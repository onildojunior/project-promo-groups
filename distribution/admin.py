from django.contrib import admin

from .models import BatchTarget, DistributionBatch, DistributionGroup


@admin.register(DistributionGroup)
class DistributionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform', 'is_active', 'updated_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('name', 'external_reference')


class BatchTargetInline(admin.TabularInline):
    model = BatchTarget
    extra = 1
    min_num = 1


@admin.register(DistributionBatch)
class DistributionBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'promotion', 'scheduled_for', 'status', 'created_by')
    list_filter = ('status',)
    search_fields = ('promotion__title', 'message_snapshot')
    list_select_related = ('promotion', 'created_by')
    readonly_fields = ('created_at', 'updated_at')
    inlines = (BatchTargetInline,)


@admin.register(BatchTarget)
class BatchTargetAdmin(admin.ModelAdmin):
    list_display = ('batch', 'group', 'status', 'sent_at', 'updated_at')
    list_filter = ('status', 'group__platform')
    search_fields = ('batch__promotion__title', 'group__name')
    list_select_related = ('batch', 'group')