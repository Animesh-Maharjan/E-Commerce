# E-Commerce Platform with ML Sentiment Analytics

A modular, extensible Django 5.2 E‑Commerce platform featuring multi‑role user accounts (customers & sellers), product catalog & reviews, shopping cart, order management workflow, payment scaffolding, and an integrated Machine Learning sentiment analysis pipeline for customer feedback insights.

---
## Table of Contents
1. Overview
2. Key Features
3. Tech Stack
4. Architecture & Apps
5. Data Model Summary
6. Machine Learning (Sentiment Analysis)
7. Project Structure
8. Setup & Installation
9. Running the Application
10. Management Commands
11. Testing & Quality
12. Environment & Configuration
13. Extensibility Roadmap
14. Security & Hardening Notes
15. Performance & Scaling Considerations
16. Contribution Guidelines
17. Troubleshooting
18. License / Usage

---
## 1. Overview
This project implements a foundational e‑commerce system built with Django. It includes a custom ML layer (TF‑IDF + Naive Bayes) that performs automated sentiment classification of product reviews to help sellers monitor customer satisfaction and prioritize actions.

---
## 2. Key Features
- Authentication with custom user model (`accounts.CustomUser`) supporting `customer` & `seller` roles.
- Product catalog with categories, inventory tracking, and average rating aggregation.
- Customer reviews with optional seller replies.
- Automated ML sentiment analysis on reviews (signal-based + batch processing + dashboard UI).
- Seller dashboards: product performance & review sentiment insights.
- Shopping cart with per‑user cart + item quantity management.
- Order pipeline with statuses (pending → confirmed → processing → shipped → delivered / cancelled).
- Shipping methods & basic address models for fulfillment flows.
- Payment models (Stripe / PayPal placeholders) with history tracking (domain scaffold for future integration).
- Management commands for model training & sentiment backfill.
- Modular app structure for future recommendation engines, demand forecasting, etc.

---
## 3. Tech Stack
| Layer | Technology |
|-------|------------|
| Language | Python 3.13 (virtualenv) |
| Framework | Django 5.2.5 |
| Database | SQLite (dev) – pluggable (MySQL dependency present) |
| ML / NLP | scikit-learn, pandas, numpy, nltk, joblib |
| Supporting | stripe (future payments), python-dotenv, Pillow |
| Frontend UI | Django templates + Bootstrap icons (light usage) |

---
## 4. Architecture & Apps
| App | Purpose |
|-----|---------|
| `accounts` | Custom user model with role separation (seller vs customer) & dashboards. |
| `store` | Catalog: categories, products, reviews, inventory, product detail logic. |
| `cart` | Per-customer cart + items with quantity & total price helpers. |
| `orders` | Order lifecycle, shipping methods, addresses, order items, cancellation logic. |
| `payments` | Payment + status history scaffolding (Stripe/PayPal integration ready). |
| `ml_analytics` | Centralized ML feature hub (sentiment pipeline, models, dashboards, APIs). |

All ML-related logic is intentionally isolated inside `ml_analytics` to simplify future expansion (e.g., recommendations, LTV scoring, fraud signals).

---
## 5. Data Model Summary
Core entities (abridged):
- `accounts.CustomUser(username, role)` – Extends `AbstractUser`.
- `store.Category(name, slug)`
- `store.Product(seller, category, name, price, stock, available, created)` with computed `average_rating`.
- `store.Review(product, customer, rating, comment, reply, created)`.
- `store.Inventory(product, quantity)`.
- `cart.Cart(user, created)` / `cart.CartItem(cart, product, quantity)`.
- `orders.Order(user, status, total_amount, shipping_method, billing_address, delivery_address, order_date)` + `OrderItem(order, product, quantity, price)`.
- `orders.ShippingMethod(name, cost, delivery_time, is_active)`.
- `orders.Address(customer_name, address, city, state, country, phone_number, email)`.
- `payments.Payment(user, order, amount, payment_method, status, identifiers...)` + `PaymentHistory(payment, previous_status, new_status, notes)`.
- `ml_analytics.ReviewSentiment(review, sentiment_score, sentiment_label, confidence_score, positive_score, negative_score, neutral_score, analyzed_at)`.
- `ml_analytics.SentimentTrainingData(text, sentiment_label, is_validated)`.
- `ml_analytics.ModelTrainingLog(training_started_at, training_completed_at, accuracy_score, precision_score, recall_score, f1_score, notes)`.

---
## 6. Machine Learning (Sentiment Analysis)
### 6.1 Pipeline
Implemented in `ml_analytics/sentiment_analyzer.py`:
- Preprocessing: lowercasing, URL & mention removal, punctuation filtering, whitespace normalization, min-length token filtering.
- Feature Extraction: `TfidfVectorizer` (bigrams, max_features=5000, stop words, min_df=2, max_df=0.8).
- Model: `MultinomialNB` (alpha=1.0).
- Train/Test Split + weighted precision/recall/F1 + 5-fold cross-validation.
- Persistence: Serialized with joblib to `ml_models/` (pipeline, vectorizer, model artifacts).

### 6.2 Training Data
Synthetic curated e‑commerce review phrases (positive / negative / neutral + mild mixed context) embedded directly in code (extensible by loading additional labeled data into `SentimentTrainingData`).

### 6.3 Execution Modes
- Auto analysis: `post_save` signal on `store.Review` (creates or updates `ReviewSentiment`).
- Batch processing: `python manage.py analyze_sentiment [--force] [--limit N]`.
- Training: `python manage.py train_sentiment_model [--retrain]` (returns metrics & logs to `ModelTrainingLog`).

### 6.4 Model Info & Reuse
Utility wrapper provides `analyze_sentiment(text)` and product-/review-level helpers used by dashboards (`sentiment_dashboard` + product detail overlays).

### 6.5 Dashboard
Route: `/ml/sentiment-dashboard/` (seller-only) shows:
- Aggregate positive / neutral / negative distribution.
- Per-product sentiment breakdown & weak performers (sorted by avg sentiment score ascending).
- Recent negative reviews to prioritize.
- Quick links to product-level detail pages: `/ml/product-sentiment/<id>/`.

---
## 7. Project Structure (Key Paths)
```
E-commerce/
  manage.py
  requirements.txt
  ecommerce/
    settings.py
    urls.py
  accounts/
  store/
  cart/
  orders/
  payments/
  ml_analytics/
    sentiment_analyzer.py
    management/commands/
  media/products/
  static/
```
(Additional template directories under each app + global `templates/`.)

---
## 8. Setup & Installation
### 8.1 Prerequisites
- Python 3.12+ (project currently using 3.13 virtual environment).
- pip / venv.
- (Optional) MySQL server if switching from SQLite (see `mysqlclient`).

### 8.2 Steps
```bash
# Clone repository
git clone <your-repo-url>
cd E-commerce

# Create & activate virtual environment (Windows PowerShell)
python -m venv env
./env/Scripts/Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# (Optional) Train sentiment model explicitly
python manage.py train_sentiment_model

# Start development server
python manage.py runserver
```

Access: http://127.0.0.1:8000/

---
## 9. Running the Application
- Storefront home: `/` (products)
- Shop listing: `/shop/`
- Product detail: `/product/<slug>/`
- Cart: `/cart/`
- Checkout & orders: `/orders/`, `/checkout/`, seller order views under `/orders/` namespace.
- Accounts: `/accounts/login/`, `/accounts/register/`.
- Seller dashboards: `/seller/dashboard/` and ML at `/ml/sentiment-dashboard/`.
- Admin: `/admin/`.

---
## 10. Management Commands
| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `train_sentiment_model` | Train or retrain ML pipeline | `--retrain` force rebuild |
| `analyze_sentiment` | Analyze existing reviews | `--force`, `--limit <N>` |

---
## 11. Testing & Quality
Current repository has limited automated tests stubs (`tests.py` per app). Recommended next steps:
- Add unit tests for: model methods (`average_rating`, order cancellation), ML analyzer predictions, management commands.
- Add integration tests: end-to-end review creation → sentiment creation.
- Potential libraries: `pytest`, `pytest-django`, `factory_boy`.

Sample quick manual ML test: create a review with strongly positive language and verify dashboard label.

---
## 12. Environment & Configuration
Key settings:
- `AUTH_USER_MODEL = 'accounts.CustomUser'`.
- Media uploads: `/media/` served in DEBUG.
- Static assets: `static/` + `STATICFILES_DIRS`.
- Switch DB by editing `DATABASES` in `ecommerce/settings.py`.
- For production: inject `SECRET_KEY`, set `DEBUG = False`, configure `ALLOWED_HOSTS`, static build pipeline, HTTPS, WAF / reverse proxy.

Optional: Create `.env` (not yet wired through `python-dotenv`; you can adapt `env_settings.py`).

---
## 13. Extensibility Roadmap
Short-term:
- Add product recommendation engine (collaborative or content-based) under `ml_analytics`.
- Implement inventory alerts & restock suggestions.
- Improve sentiment model with incremental learning + real labeled data via `SentimentTrainingData`.

Mid-term:
- Integrate Stripe payment intents fully (webhooks, refunds, 3DS support).
- Add order invoice PDFs & email notifications.
- Customer wishlists & recently viewed tracking.

Long-term:
- Demand forecasting for sellers.
- Fraud detection signals (cross-check payment + behavior).
- Multi-vendor marketplace commission tracking.

---
## 14. Security & Hardening Notes
- Rotate & externalize `SECRET_KEY`.
- Enforce strong password validators (already enabled).
- Add rate limiting (e.g., django-ratelimit) to auth endpoints.
- Sanitize user-uploaded images (virus scanning, size limits).
- Add CSP & HTTPS redirects.
- Implement permission checks on seller-only routes (basic role check present; extend with decorators/mixins).

---
## 15. Performance & Scaling Considerations
- Replace SQLite with PostgreSQL/MySQL for concurrency.
- Add caching (Redis) for product lists & aggregated sentiment stats.
- Asynchronous tasks (Celery + Redis) for batch sentiment retraining & heavy analytics.
- Precompute daily sentiment snapshots for dashboards.
- Serve media through CDN / object storage (S3, GCS, Azure Blob).

---
## 16. Contribution Guidelines
1. Fork & feature branch naming: `feature/<short-description>`.
2. Run migrations & tests before PR.
3. Include docstring updates for new public methods.
4. Prefer small, focused PRs (< 400 LOC diff).
5. Add or update README sections if feature touches deployment, ML, or data model.

Coding Style: PEP8 + descriptive model & field names. Keep ML code isolated to `ml_analytics`.

---
## 17. Troubleshooting
| Issue | Cause | Resolution |
|-------|-------|------------|
| `NoReverseMatch accounts:` | Template used namespaced URL not defined | Remove namespace or add `app_name` to accounts URLs. |
| `FieldError created_at` | Review model uses `created` field | Update queries & templates. |
| Missing sentiment badges | Review has no `reviewsentiment` yet | Run `analyze_sentiment` or create new review (signal triggers). |
| Model not retraining | Already trained | Use `python manage.py train_sentiment_model --retrain`. |
| Low accuracy | Synthetic data limited | Add labeled rows into `SentimentTrainingData` & retrain. |

---
## 18. License / Usage
No explicit license provided yet. For open source distribution: add an OSS license (MIT / Apache-2.0) at repository root.

---
### Quick Start (TL;DR)
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py train_sentiment_model
python manage.py runserver
```
Visit `/ml/sentiment-dashboard/` after adding some reviews.

---
### Maintainers
- Original Author: (Add your name / org)
- ML Module: Centralized in `ml_analytics` for future expansion.

---
Feel free to open issues for feature requests or enhancement ideas.
