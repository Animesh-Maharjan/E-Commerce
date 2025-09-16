from django.core.management.base import BaseCommand
from ml_analytics.sentiment_analyzer import sentiment_analyzer
from ml_analytics.models import ModelTrainingLog
from django.utils import timezone


class Command(BaseCommand):
    help = 'Train or retrain the sentiment analysis model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retrain',
            action='store_true',
            help='Force retrain the model even if it already exists',
        )

    def handle(self, *args, **options):
        retrain = options['retrain']
        
        self.stdout.write(
            self.style.SUCCESS('Training sentiment analysis model...')
        )
        
        # Create training log entry
        training_log = ModelTrainingLog.objects.create(
            model_version='1.0',
            notes='Training via management command'
        )
        
        try:
            # Train the model
            metrics = sentiment_analyzer.train_model(retrain=retrain)
            
            # Handle case where metrics might be None
            if metrics is None:
                metrics = {
                    'accuracy': 0.0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'f1_score': 0.0,
                    'cv_mean': 0.0,
                    'cv_std': 0.0,
                    'status': 'failed'
                }
            
            # Update training log with results
            training_log.training_completed_at = timezone.now()
            training_log.accuracy_score = metrics.get('accuracy', 0)
            training_log.precision_score = metrics.get('precision', 0)
            training_log.recall_score = metrics.get('recall', 0)
            training_log.f1_score = metrics.get('f1_score', 0)
            training_log.training_samples_count = 50  # Our training data size
            training_log.notes = f"Status: {metrics.get('status', 'completed')}"
            training_log.save()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nModel training complete!\n'
                    f'Status: {metrics.get("status", "completed")}\n'
                    f'Accuracy: {metrics.get("accuracy", 0):.3f}\n'
                    f'Precision: {metrics.get("precision", 0):.3f}\n'
                    f'Recall: {metrics.get("recall", 0):.3f}\n'
                    f'F1-Score: {metrics.get("f1_score", 0):.3f}\n'
                    f'CV Mean: {metrics.get("cv_mean", 0):.3f} (+/- {metrics.get("cv_std", 0):.3f})'
                )
            )
            
        except Exception as e:
            training_log.notes = f'Training failed: {str(e)}'
            training_log.save()
            
            self.stdout.write(
                self.style.ERROR(f'Model training failed: {e}')
            )
            
        # Show model info
        model_info = sentiment_analyzer.get_model_info()
        self.stdout.write(f"\nModel Info: {model_info}")
        
        # Test the model with a sample
        sample_text = "This product is amazing! I love it so much!"
        result = sentiment_analyzer.analyze_sentiment(sample_text)
        self.stdout.write(
            f"\nSample Analysis:\n"
            f"Text: '{sample_text}'\n"
            f"Sentiment: {result['sentiment_label']}\n"
            f"Score: {result['sentiment_score']:.2f}\n"
            f"Confidence: {result['confidence_score']:.2f}"
        )