from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'get_full_name', 'account_type', 'balance', 'status', 'email', 'phone', 'created_at']
    list_filter = ['account_type', 'status', 'created_at']
    search_fields = ['account_number', 'first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['account_number', 'created_at', 'updated_at']
    fieldsets = (
        ('Account Information', {
            'fields': ('account_number', 'account_type', 'balance', 'status')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth')
        }),
        ('Security', {
            'fields': ('pin',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
