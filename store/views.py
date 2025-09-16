from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, Category, Review
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count

def home(request):
    products = Product.objects.filter(available=True)[:6]
    return render(request, 'store/home.html', {'products': products})

def shop(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category__slug=selected_category)
    return render(request, 'store/shop.html', {'products': products, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    
    # Get sentiment analysis data
    sentiment_data = {}
    reviews_with_sentiment = reviews.filter(reviewsentiment__isnull=False)
    if reviews_with_sentiment.exists():
        sentiment_counts = reviews_with_sentiment.values('reviewsentiment__sentiment_label').annotate(
            count=Count('id')
        )
        total_sentiment_reviews = reviews_with_sentiment.count()
        
        for item in sentiment_counts:
            label = item['reviewsentiment__sentiment_label']
            count = item['count']
            percentage = round((count / total_sentiment_reviews) * 100, 1) if total_sentiment_reviews > 0 else 0
            sentiment_data[label] = {
                'count': count,
                'percentage': percentage
            }
    
    if request.method == "POST" and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        # The Review model expects `customer` (not `user`)
        Review.objects.create(product=product, customer=request.user, rating=rating, comment=comment)
        return redirect('product-detail', slug=slug)
    
    context = {
        'product': product, 
        'reviews': reviews,
        'sentiment_data': sentiment_data,
        'reviews_with_sentiment': reviews_with_sentiment
    }
    return render(request, 'store/product_detail.html', context)

@login_required
def add_product(request):
    if request.user.role != "seller":
        return redirect('store-home')

    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST['name']
        slug = request.POST['slug']
        description = request.POST['description']
        price = request.POST['price']
        stock = request.POST['stock']
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id) if category_id else None
        image = request.FILES.get('image')

        # If no category selected, allow seller to create a new one
        new_category_name = request.POST.get('new_category')
        if not category and new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name, slug=new_category_name.lower().replace(' ', '-'))

        Product.objects.create(
            seller=request.user,
            name=name,
            slug=slug,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image
        )
        return redirect('seller-products')

    return render(request, 'store/add_product.html', {'categories': categories})

@login_required
def seller_products(request):
    if request.user.role != "seller":
        return redirect('store-home')
    products = Product.objects.filter(seller=request.user)
    return render(request, 'store/seller_products.html', {'products': products})

@login_required
def all_seller_reviews(request):
    if request.user.role != "seller":
        return redirect('store-home')
    products = Product.objects.filter(seller=request.user)
    reviews = []
    for product in products:
        reviews.extend(product.reviews.all())
    return render(request, 'store/all_seller_reviews.html', {'reviews': reviews})

@login_required
def seller_reviews(request, product_id):
    if request.user.role != "seller":
        return redirect('store-home')
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    reviews = product.reviews.all()
    if request.method == "POST":
        review_id = request.POST.get('review_id')
        reply = request.POST.get('reply')
        review = Review.objects.get(id=review_id, product=product)
        review.reply = reply
        review.save()
    return render(request, 'store/seller_reviews.html', {'product': product, 'reviews': reviews})

@login_required
def update_product(request, product_id):
    if request.user.role != "seller":
        return redirect('store-home')
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST['name']
        product.slug = request.POST['slug']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        category_id = request.POST.get('category')
        product.category = Category.objects.get(id=category_id) if category_id else product.category
        image = request.FILES.get('image')
        if image:
            product.image = image
        product.save()
        return redirect('seller-products')

    return render(request, 'store/update_product.html', {'product': product, 'categories': categories})

@require_POST
@login_required
def delete_product(request, product_id):
    if request.user.role != "seller":
        return redirect('store-home')
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    return redirect('seller-products')


