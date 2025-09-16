from django.urls import path
from . import views

app_name = 'ml_analytics'

urlpatterns = [
    # Main sentiment dashboard
    path('sentiment-dashboard/', views.sentiment_dashboard, name='sentiment-dashboard'),
    
    # Product-specific sentiment analysis
    path('product-sentiment/<int:product_id>/', views.product_sentiment_detail, name='product-sentiment-detail'),
    
    # AJAX endpoints for sentiment analysis
    path('reanalyze-review/<int:review_id>/', views.reanalyze_review_sentiment, name='reanalyze-review'),
    path('analyze-all-reviews/', views.analyze_all_reviews, name='analyze-all-reviews'),
    
    # API endpoints
    path('api/sentiment-stats/', views.sentiment_api_stats, name='sentiment-api-stats'),
]