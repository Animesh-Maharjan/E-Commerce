from django.apps import AppConfig


class MlAnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ml_analytics'
    verbose_name = 'ML Analytics'
    
    def ready(self):
        """Initialize the app and import signals"""
        try:
            # Import signals to register them
            import ml_analytics.signals
            
            # Initialize sentiment analyzer (this will train the model if needed)
            from .sentiment_analyzer import sentiment_analyzer
            
            print("ML Analytics app initialized successfully")
            print(f"Sentiment analyzer status: {sentiment_analyzer.get_model_info()}")
            
        except Exception as e:
            print(f"Error initializing ML Analytics app: {e}")
            # Don't raise the exception to avoid breaking the entire application
