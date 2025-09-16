from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from store.models import Product, Review
from .models import ReviewSentiment
from .sentiment_analyzer import SentimentAnalyzer
import json


@login_required
def sentiment_dashboard(request):
    """Main sentiment analysis dashboard for sellers"""
    if request.user.role != 'seller':
        messages.error(request, "Access denied. This page is for sellers only.")
        return render(request, '403.html', status=403)
    
    # Get seller's products and reviews
    seller_products = Product.objects.filter(seller=request.user)
    seller_reviews = Review.objects.filter(product__seller=request.user)
    
    # Get sentiment analysis for seller's reviews
    sentiment_reviews = seller_reviews.filter(
        reviewsentiment__isnull=False
    ).select_related('reviewsentiment', 'product')
    
    # Calculate overall statistics
    total_reviews = sentiment_reviews.count()
    
    if total_reviews > 0:
        # Count sentiment labels
        positive_count = sentiment_reviews.filter(
            reviewsentiment__sentiment_label='positive'
        ).count()
        negative_count = sentiment_reviews.filter(
            reviewsentiment__sentiment_label='negative'
        ).count()
        neutral_count = sentiment_reviews.filter(
            reviewsentiment__sentiment_label='neutral'
        ).count()
        
        # Calculate percentages
        positive_percentage = round((positive_count / total_reviews) * 100, 1)
        negative_percentage = round((negative_count / total_reviews) * 100, 1)
        neutral_percentage = round((neutral_count / total_reviews) * 100, 1)
        
        # Calculate average sentiment score
        sentiment_scores = []
        for review in sentiment_reviews:
            sentiment = review.reviewsentiment
            if sentiment.sentiment_label == 'positive':
                score = sentiment.confidence_score
            elif sentiment.sentiment_label == 'negative':
                score = -sentiment.confidence_score
            else:
                score = 0
            sentiment_scores.append(score)
        
        avg_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
        
        # Determine overall sentiment status
        if avg_sentiment_score > 0.3:
            sentiment_status = 'positive'
            sentiment_message = "Your customers are generally happy with your products!"
        elif avg_sentiment_score < -0.3:
            sentiment_status = 'negative'
            sentiment_message = "Consider addressing customer concerns to improve satisfaction."
        else:
            sentiment_status = 'neutral'
            sentiment_message = "Mixed feedback from customers. Room for improvement."
            
    else:
        positive_count = negative_count = neutral_count = 0
        positive_percentage = negative_percentage = neutral_percentage = 0
        avg_sentiment_score = 0
        sentiment_status = 'neutral'
        sentiment_message = "No sentiment data available yet."
    
    # Get product-wise sentiment analysis
    product_sentiment_data = []
    for product in seller_products:
        product_reviews = sentiment_reviews.filter(product=product)
        if product_reviews.exists():
            product_positive = product_reviews.filter(
                reviewsentiment__sentiment_label='positive'
            ).count()
            product_negative = product_reviews.filter(
                reviewsentiment__sentiment_label='negative'
            ).count()
            product_neutral = product_reviews.filter(
                reviewsentiment__sentiment_label='neutral'
            ).count()
            product_total = product_reviews.count()
            
            # Calculate product sentiment score
            product_scores = []
            for review in product_reviews:
                sentiment = review.reviewsentiment
                if sentiment.sentiment_label == 'positive':
                    score = sentiment.confidence_score
                elif sentiment.sentiment_label == 'negative':
                    score = -sentiment.confidence_score
                else:
                    score = 0
                product_scores.append(score)
            
            product_avg_sentiment = sum(product_scores) / len(product_scores)
            
            product_sentiment_data.append({
                'product': product,
                'total_reviews': product_total,
                'positive_count': product_positive,
                'negative_count': product_negative,
                'neutral_count': product_neutral,
                'positive_percentage': round((product_positive / product_total) * 100, 1),
                'negative_percentage': round((product_negative / product_total) * 100, 1),
                'neutral_percentage': round((product_neutral / product_total) * 100, 1),
                'avg_sentiment_score': product_avg_sentiment,
                'avg_rating': product.average_rating,
            })
    
    # Sort by sentiment score (worst first for attention)
    product_sentiment_data.sort(key=lambda x: x['avg_sentiment_score'])
    
    # Get recent negative reviews for immediate attention
    recent_negative_reviews = sentiment_reviews.filter(
        reviewsentiment__sentiment_label='negative'
    ).order_by('-created')[:10]
    
    # Get top positive reviews for showcasing
    top_positive_reviews = sentiment_reviews.filter(
        reviewsentiment__sentiment_label='positive',
        reviewsentiment__confidence_score__gte=0.8
    ).order_by('-reviewsentiment__confidence_score')[:5]
    
    context = {
        'total_reviews': total_reviews,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'positive_percentage': positive_percentage,
        'negative_percentage': negative_percentage,
        'neutral_percentage': neutral_percentage,
        'avg_sentiment_score': avg_sentiment_score,
        'sentiment_status': sentiment_status,
        'sentiment_message': sentiment_message,
        'product_sentiment_data': product_sentiment_data,
        'recent_negative_reviews': recent_negative_reviews,
        'top_positive_reviews': top_positive_reviews,
        'total_products': seller_products.count(),
    }
    
    return render(request, 'ml_analytics/sentiment_dashboard.html', context)


@login_required
def product_sentiment_detail(request, product_id):
    """Detailed sentiment analysis for a specific product"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    # Get all reviews with sentiment analysis for this product
    reviews_with_sentiment = Review.objects.filter(
        product=product,
        reviewsentiment__isnull=False
    ).select_related('reviewsentiment', 'customer').order_by('-created')
    
    # Calculate sentiment statistics for this product
    total_reviews = reviews_with_sentiment.count()
    
    if total_reviews > 0:
        positive_count = reviews_with_sentiment.filter(
            reviewsentiment__sentiment_label='positive'
        ).count()
        negative_count = reviews_with_sentiment.filter(
            reviewsentiment__sentiment_label='negative'
        ).count()
        neutral_count = reviews_with_sentiment.filter(
            reviewsentiment__sentiment_label='neutral'
        ).count()
        
        positive_percentage = round((positive_count / total_reviews) * 100, 1)
        negative_percentage = round((negative_count / total_reviews) * 100, 1)
        neutral_percentage = round((neutral_count / total_reviews) * 100, 1)
        
        # Calculate average sentiment score
        sentiment_scores = []
        for review in reviews_with_sentiment:
            sentiment = review.reviewsentiment
            if sentiment.sentiment_label == 'positive':
                score = sentiment.confidence_score
            elif sentiment.sentiment_label == 'negative':
                score = -sentiment.confidence_score
            else:
                score = 0
            sentiment_scores.append(score)
        
        avg_sentiment_score = sum(sentiment_scores) / len(sentiment_scores)
    else:
        positive_count = negative_count = neutral_count = 0
        positive_percentage = negative_percentage = neutral_percentage = 0
        avg_sentiment_score = 0
    
    context = {
        'product': product,
        'reviews_with_sentiment': reviews_with_sentiment,
        'total_reviews': total_reviews,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'positive_percentage': positive_percentage,
        'negative_percentage': negative_percentage,
        'neutral_percentage': neutral_percentage,
        'avg_sentiment_score': avg_sentiment_score,
        'avg_rating': product.average_rating,
    }
    
    return render(request, 'ml_analytics/product_sentiment_detail.html', context)


@login_required
@require_POST
def reanalyze_review_sentiment(request, review_id):
    """Re-analyze sentiment for a specific review"""
    try:
        review = get_object_or_404(Review, id=review_id, product__seller=request.user)
        
        # Initialize sentiment analyzer
        analyzer = SentimentAnalyzer()
        
        # Analyze sentiment
        result = analyzer.analyze_sentiment(review.comment)
        
        # Update or create sentiment analysis
        sentiment, created = ReviewSentiment.objects.update_or_create(
            review=review,
            defaults={
                'sentiment_score': result['sentiment_score'],
                'sentiment_label': result['sentiment_label'],
                'confidence_score': result['confidence_score'],
                'positive_score': result['positive_score'],
                'negative_score': result['negative_score'],
                'neutral_score': result['neutral_score'],
            }
        )
        
        return JsonResponse({
            'success': True,
            'sentiment_label': sentiment.sentiment_label,
            'confidence_score': sentiment.confidence_score,
            'sentiment_score': sentiment.sentiment_score,
            'message': 'Sentiment analysis updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def analyze_all_reviews(request):
    """Analyze sentiment for all reviews that don't have sentiment analysis yet"""
    if request.user.role != 'seller':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # Get reviews without sentiment analysis for seller's products
        reviews_without_sentiment = Review.objects.filter(
            product__seller=request.user,
            reviewsentiment__isnull=True
        )
        
        analyzer = SentimentAnalyzer()
        analyzed_count = 0
        
        for review in reviews_without_sentiment:
            try:
                result = analyzer.analyze_sentiment(review.comment)
                
                ReviewSentiment.objects.create(
                    review=review,
                    sentiment_score=result['sentiment_score'],
                    sentiment_label=result['sentiment_label'],
                    confidence_score=result['confidence_score'],
                    positive_score=result['positive_score'],
                    negative_score=result['negative_score'],
                    neutral_score=result['neutral_score'],
                )
                analyzed_count += 1
                
            except Exception as e:
                print(f"Error analyzing review {review.id}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'analyzed_count': analyzed_count,
            'message': f'Successfully analyzed {analyzed_count} reviews'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def sentiment_api_stats(request):
    """API endpoint for sentiment statistics (for AJAX requests)"""
    if not request.user.is_authenticated or request.user.role != 'seller':
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get sentiment statistics for seller's products
    seller_reviews = Review.objects.filter(
        product__seller=request.user,
        reviewsentiment__isnull=False
    )
    
    total = seller_reviews.count()
    
    if total > 0:
        positive = seller_reviews.filter(reviewsentiment__sentiment_label='positive').count()
        negative = seller_reviews.filter(reviewsentiment__sentiment_label='negative').count()
        neutral = seller_reviews.filter(reviewsentiment__sentiment_label='neutral').count()
        
        stats = {
            'total': total,
            'positive': positive,
            'negative': negative,
            'neutral': neutral,
            'positive_percentage': round((positive / total) * 100, 1),
            'negative_percentage': round((negative / total) * 100, 1),
            'neutral_percentage': round((neutral / total) * 100, 1),
        }
    else:
        stats = {
            'total': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'positive_percentage': 0,
            'negative_percentage': 0,
            'neutral_percentage': 0,
        }
    
    return JsonResponse(stats)
