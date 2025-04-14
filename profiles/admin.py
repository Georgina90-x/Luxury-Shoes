from django.contrib import admin
from .models import MarketingEmail, EmailLog


@admin.register(MarketingEmail)
class MarketingEmailAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_at")  # Display subject & timestamp
    search_fields = ("subject",)  # Add search functionality
    ordering = ("-sent_at",)  # Sort by most recent


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "sent_at")  # Display user, email & time
    search_fields = (
        "user__email",
        "email__subject",  # Search by email & subject
    )
    list_filter = ("sent_at",)  # Add filter by date
