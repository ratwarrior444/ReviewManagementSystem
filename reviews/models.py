from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Review(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    product_id = models.IntegerField()
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    title = models.CharField(max_length=200)
    comment = models.TextField(blank=True, null=True)

    is_verified_purchase = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product_id', 'customer_email'],
                name='unique_review_per_product_per_email'
            )
        ]

    def __str__(self):
        return f"{self.product_id} - {self.customer_email} ({self.rating})"

    # ---------- Business Logic Methods ----------

    def helpful_count(self):
        return self.votes.filter(is_helpful=True).count()

    def not_helpful_count(self):
        return self.votes.filter(is_helpful=False).count()

    def has_images(self):
        return self.images.exists()

    def has_response(self):
        return hasattr(self, 'business_response')

    def clean(self):
        if len(self.title) < 10:
            raise ValidationError("Title must be at least 10 characters long.")

        if self.comment and len(self.comment) > 2000:
            raise ValidationError("Comment cannot exceed 2000 characters.")

class ReviewImage(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='review_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for Review {self.review.id}"


class BusinessResponse(models.Model):
    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,
        related_name='business_response'
    )

    response_text = models.TextField()
    responder_name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if len(self.response_text) < 20:
            raise ValidationError("Response must be at least 20 characters long.")

    def __str__(self):
        return f"Response to Review {self.review.id}"

class HelpfulVote(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='votes'
    )

    voter_email = models.EmailField()
    is_helpful = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['review', 'voter_email'],
                name='unique_vote_per_review_per_email'
            )
        ]

    def __str__(self):
        return f"{self.voter_email} → {self.review.id}"
