from django.core.management.base import BaseCommand
from django.utils import timezone
from store.models import Review
from ml_analytics.models import ReviewSentiment
from ml_analytics.sentiment_analyzer import analyze_review_sentiment


class Command(BaseCommand):
    help = 'Analyze sentiment for all existing reviews'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-analyze all reviews, even those already analyzed',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of reviews to analyze',
        )

    def handle(self, *args, **options):
        force = options['force']
        limit = options['limit']
        
        self.stdout.write(
            self.style.SUCCESS('Starting sentiment analysis for reviews...')
        )
        
        # Get reviews to analyze
        if force:
            reviews = Review.objects.all()
            self.stdout.write(f"Force mode: analyzing all {reviews.count()} reviews")
        else:
            reviews = Review.objects.filter(reviewsentiment__isnull=True)
            self.stdout.write(f"Analyzing {reviews.count()} reviews without sentiment data")
        
        if limit:
            reviews = reviews[:limit]
            self.stdout.write(f"Limited to {limit} reviews")
        
        if not reviews.exists():
            self.stdout.write(
                self.style.WARNING('No reviews found to analyze.')
            )
            return
        
        analyzed_count = 0
        errors_count = 0
        
        for review in reviews:
            try:
                self.stdout.write(f"Analyzing review {review.id}: {review.comment[:50]}...")
                
                # Analyze sentiment
                result = analyze_review_sentiment(review.comment)
                
                if force and hasattr(review, 'reviewsentiment'):
                    # Update existing sentiment
                    sentiment = review.reviewsentiment
                    sentiment.sentiment_score = result['sentiment_score']
                    sentiment.sentiment_label = result['sentiment_label']
                    sentiment.confidence_score = result['confidence_score']
                    sentiment.positive_score = result['positive_score']
                    sentiment.negative_score = result['negative_score']
                    sentiment.neutral_score = result['neutral_score']
                    sentiment.save()
                    self.stdout.write(f"  Updated: {result['sentiment_label']} (confidence: {result['confidence_score']:.2f})")
                else:
                    # Create new sentiment analysis
                    ReviewSentiment.objects.create(
                        review=review,
                        sentiment_score=result['sentiment_score'],
                        sentiment_label=result['sentiment_label'],
                        confidence_score=result['confidence_score'],
                        positive_score=result['positive_score'],
                        negative_score=result['negative_score'],
                        neutral_score=result['neutral_score'],
                    )
                    self.stdout.write(f"  Created: {result['sentiment_label']} (confidence: {result['confidence_score']:.2f})")
                
                analyzed_count += 1
                
            except Exception as e:
                errors_count += 1
                self.stdout.write(
                    self.style.ERROR(f"Error analyzing review {review.id}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSentiment analysis complete!\n'
                f'Successfully analyzed: {analyzed_count} reviews\n'
                f'Errors: {errors_count} reviews'
            )
        )