from django.contrib import admin

from .models import MessageTemplate, Partner, Promotion


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'slug', 'allowed_domains')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'partner', 'current_price', 'status', 'source', 'updated_at')
    list_filter = ('status', 'source', 'partner')
    search_fields = ('title', 'original_url', 'affiliate_url')
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('partner',)


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('partner', 'channel', 'is_active', 'updated_at')
    list_filter = ('channel', 'is_active')
    search_fields = ('partner__name', 'body')