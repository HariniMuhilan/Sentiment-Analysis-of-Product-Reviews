# Datasets Overview

This project analyzes sentiment across multiple e-commerce platforms. Raw dataset files (~50GB+) are excluded from version control due to GitHub's file size limits.

## Platforms & Data Sources

### 1. Amazon Customer Reviews
- **Format**: TSV / Tab-Separated Values (US Reviews dataset)
- **Categories**:
  - Wireless, Electronics, Mobile Apps, PC
  - Books, Digital Ebook, Digital Video, Video DVD, Music
  - Apparel, Shoes, Beauty, Health & Personal Care
  - Toys, Sports, Outdoors, Tools, Automotive, Home, Pet Products
- **Attributes**: `customer_id`, `review_id`, `product_id`, `product_title`, `star_rating`, `helpful_votes`, `total_votes`, `review_headline`, `review_body`, `review_date`

### 2. Flipkart Reviews
- **Format**: CSV (`Dataset-SA.csv`) / ZIP
- **Attributes**: Product reviews, ratings, user summary, and sentiment annotations.

### 3. Myntra Fashion Reviews
- **Format**: CSV / ZIP
- **Focus**: Apparel, fashion, fit feedback, and clothing ratings.

### 4. Meesho Product Reviews
- **Format**: CSV
- **Focus**: E-commerce customer feedback and value-for-money sentiment.
