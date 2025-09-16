from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Review
from .models import ReviewSentiment
from .sentiment_analyzer import analyze_review_sentiment
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
def analyze_review_sentiment_signal(sender, instance, created, **kwargs):
    """
    Automatically analyze sentiment when a review is created or updated
    """
    try:
        # Check if sentiment analysis already exists
        existing_sentiment = getattr(instance, 'reviewsentiment', None)
        
        # Only analyze if it's a new review or if sentiment doesn't exist
        if created or not existing_sentiment:
            logger.info(f"Analyzing sentiment for review {instance.id}")
            
            # Analyze sentiment
            result = analyze_review_sentiment(instance.comment)
            
            if existing_sentiment:
                # Update existing sentiment analysis
                existing_sentiment.sentiment_score = result['sentiment_score']
                existing_sentiment.sentiment_label = result['sentiment_label']
                existing_sentiment.confidence_score = result['confidence_score']
                existing_sentiment.positive_score = result['positive_score']
                existing_sentiment.negative_score = result['negative_score']
                existing_sentiment.neutral_score = result['neutral_score']
                existing_sentiment.save()
                logger.info(f"Updated sentiment for review {instance.id}: {result['sentiment_label']}")
            else:
                # Create new sentiment analysis
                ReviewSentiment.objects.create(
                    review=instance,
                    sentiment_score=result['sentiment_score'],
                    sentiment_label=result['sentiment_label'],
                    confidence_score=result['confidence_score'],
                    positive_score=result['positive_score'],
                    negative_score=result['negative_score'],
                    neutral_score=result['neutral_score'],
                )
                logger.info(f"Created sentiment for review {instance.id}: {result['sentiment_label']}")
                
    except Exception as e:
        logger.error(f"Error analyzing sentiment for review {instance.id}: {e}")
        # Don't raise the exception to avoid breaking the review creation process
