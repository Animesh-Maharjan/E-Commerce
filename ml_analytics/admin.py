from django.contrib import admin
from .models import ReviewSentiment, SentimentTrainingData, ModelTrainingLog


@admin.register(ReviewSentiment)
class ReviewSentimentAdmin(admin.ModelAdmin):
    list_display = [
        'review', 'sentiment_label', 'sentiment_score', 
        'confidence_score', 'analyzed_at'
    ]
    list_filter = ['sentiment_label', 'analyzed_at', 'review__product__category']
    search_fields = [
        'review__product__name', 'review__customer__username', 
        'review__comment'
    ]
    readonly_fields = ['analyzed_at', 'updated_at']
    list_per_page = 25
    
    fieldsets = (
        ('Review Information', {
            'fields': ('review',)
        }),
        ('Sentiment Analysis Results', {
            'fields': (
                'sentiment_label', 'sentiment_score', 'confidence_score',
                'positive_score', 'negative_score', 'neutral_score'
            )
        }),
        ('Timestamps', {
            'fields': ('analyzed_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['review']
        return self.readonly_fields


@admin.register(SentimentTrainingData)
class SentimentTrainingDataAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'sentiment_label', 'is_validated', 'created_at']
    list_filter = ['sentiment_label', 'is_validated', 'created_at']
    search_fields = ['text']
    list_editable = ['sentiment_label', 'is_validated']
    list_per_page = 25
    
    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(ModelTrainingLog)
class ModelTrainingLogAdmin(admin.ModelAdmin):
    list_display = [
        'model_version', 'training_started_at', 'training_completed_at',
        'training_samples_count', 'accuracy_score', 'f1_score'
    ]
    list_filter = ['model_version', 'training_started_at']
    readonly_fields = [
        'training_started_at', 'training_completed_at',
        'accuracy_score', 'precision_score', 'recall_score', 'f1_score'
    ]
    
    fieldsets = (
        ('Training Information', {
            'fields': ('model_version', 'training_samples_count', 'notes')
        }),
        ('Training Results', {
            'fields': (
                'accuracy_score', 'precision_score', 'recall_score', 'f1_score'
            )
        }),
        ('Timestamps', {
            'fields': ('training_started_at', 'training_completed_at')
        }),
    )
