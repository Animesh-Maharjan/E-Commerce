"""
Test script for sentiment analysis functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from ml_analytics.sentiment_analyzer import sentiment_analyzer

def test_sentiment_analysis():
    """Test the sentiment analysis functionality"""
    
    print("🧠 Testing Sentiment Analysis System")
    print("=" * 50)
    
    # Test cases
    test_reviews = [
        ("This product is amazing! I love it so much!", "positive"),
        ("Terrible quality, waste of money!", "negative"),
        ("It's okay, nothing special.", "neutral"),
        ("Excellent quality and fast shipping!", "positive"),
        ("Poor customer service and defective product.", "negative"),
        ("Average product for the price.", "neutral"),
    ]
    
    print("\n📊 Individual Test Results:")
    print("-" * 30)
    
    for text, expected in test_reviews:
        result = sentiment_analyzer.analyze_sentiment(text)
        
        status = "✅" if result['sentiment_label'] == expected else "❌"
        
        print(f"{status} Text: '{text[:40]}...'")
        print(f"   Expected: {expected}")
        print(f"   Predicted: {result['sentiment_label']}")
        print(f"   Score: {result['sentiment_score']:.2f}")
        print(f"   Confidence: {result['confidence_score']:.2f}")
        print()
    
    # Test model info
    print("\n🔧 Model Information:")
    print("-" * 20)
    model_info = sentiment_analyzer.get_model_info()
    for key, value in model_info.items():
        print(f"   {key}: {value}")
    
    print("\n✅ Sentiment analysis test completed!")

if __name__ == "__main__":
    test_sentiment_analysis()