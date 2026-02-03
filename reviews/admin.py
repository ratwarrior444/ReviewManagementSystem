from django.contrib import admin
from .models import Review, ReviewImage, BusinessResponse, HelpfulVote


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    max_num = 5


class BusinessResponseInline(admin.StackedInline):
    model = BusinessResponse
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product_id", "rating", "status", "created_at")
    list_filter = ("status", "rating", "is_verified_purchase")
    search_fields = ("title", "comment", "customer_email")

    inlines = [ReviewImageInline, BusinessResponseInline]


admin.site.register(HelpfulVote)
