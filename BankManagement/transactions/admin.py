from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'amount', 'from_account', 'to_account', 'status', 'balance_after_transaction', 'created_at']
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['from_account__account_number', 'to_account__account_number', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_type', 'amount', 'description', 'status')
        }),
        ('Accounts', {
            'fields': ('from_account', 'to_account')
        }),
        ('Balance', {
            'fields': ('balance_after_transaction',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
