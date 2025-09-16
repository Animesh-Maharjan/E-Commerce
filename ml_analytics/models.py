from django.db import models
from store.models import Review


class ReviewSentiment(models.Model):
    """Model to store sentiment analysis results for reviews"""
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    
    review = models.OneToOneField(
        Review, 
        on_delete=models.CASCADE, 
        related_name='reviewsentiment'
    )
    sentiment_score = models.FloatField(
        help_text="Sentiment score ranging from -1 (very negative) to 1 (very positive)"
    )
    sentiment_label = models.CharField(
        max_length=10, 
        choices=SENTIMENT_CHOICES,
        help_text="Predicted sentiment label"
    )
    confidence_score = models.FloatField(
        help_text="Confidence score of the prediction (0 to 1)"
    )
    positive_score = models.FloatField(
        default=0.0,
        help_text="Probability of positive sentiment"
    )
    negative_score = models.FloatField(
        default=0.0,
        help_text="Probability of negative sentiment"
    )
    neutral_score = models.FloatField(
        default=0.0,
        help_text="Probability of neutral sentiment"
    )
    analyzed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def sentiment_color_class(self):
        """Return Bootstrap color class for sentiment"""
        if self.sentiment_label == 'positive':
            return 'success'
        elif self.sentiment_label == 'negative':
            return 'danger'
        else:
            return 'secondary'
    
    @property
    def sentiment_icon(self):
        """Return Bootstrap icon class for sentiment"""
        if self.sentiment_label == 'positive':
            return 'bi bi-emoji-smile'
        elif self.sentiment_label == 'negative':
            return 'bi bi-emoji-frown'
        else:
            return 'bi bi-emoji-neutral'
    
    class Meta:
        verbose_name = "Review Sentiment Analysis"
        verbose_name_plural = "Review Sentiment Analyses"
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return f"{self.review.product.name} - {self.sentiment_label} ({self.confidence_score:.2f})"
    
    @property
    def sentiment_emoji(self):
        """Return emoji representation of sentiment"""
        emoji_map = {
            'positive': '😊',
            'negative': '😞',
            'neutral': '😐'
        }
        return emoji_map.get(self.sentiment_label, '😐')
    
    @property
    def sentiment_color_class(self):
        """Return Bootstrap color class for sentiment"""
        color_map = {
            'positive': 'success',
            'negative': 'danger',
            'neutral': 'secondary'
        }
        return color_map.get(self.sentiment_label, 'secondary')
    
    @property
    def sentiment_icon(self):
        """Return Bootstrap icon for sentiment"""
        icon_map = {
            'positive': 'bi-emoji-smile',
            'negative': 'bi-emoji-frown',
            'neutral': 'bi-emoji-neutral'
        }
        return icon_map.get(self.sentiment_label, 'bi-emoji-neutral')


class SentimentTrainingData(models.Model):
    """Model to store training data for sentiment analysis model"""
    text = models.TextField(help_text="Review text for training")
    sentiment_label = models.CharField(
        max_length=10,
        choices=ReviewSentiment.SENTIMENT_CHOICES,
        help_text="Manually labeled sentiment"
    )
    is_validated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Sentiment Training Data"
        verbose_name_plural = "Sentiment Training Data"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sentiment_label}: {self.text[:50]}..."


class ModelTrainingLog(models.Model):
    """Model to track sentiment analysis model training sessions"""
    training_started_at = models.DateTimeField(auto_now_add=True)
    training_completed_at = models.DateTimeField(null=True, blank=True)
    training_samples_count = models.PositiveIntegerField(default=0)
    accuracy_score = models.FloatField(null=True, blank=True)
    precision_score = models.FloatField(null=True, blank=True)
    recall_score = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    model_version = models.CharField(max_length=20, default='1.0')
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Model Training Log"
        verbose_name_plural = "Model Training Logs"
        ordering = ['-training_started_at']
    
    def __str__(self):
        status = "Completed" if self.training_completed_at else "In Progress"
        return f"Training {self.model_version} - {status}"
