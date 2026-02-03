from rest_framework import serializers
from django.db.models import Avg

from .models import (
    Review,
    ReviewImage,
    HelpfulVote,
    BusinessResponse
)

class ReviewListSerializer(serializers.ModelSerializer):
    helpful_count = serializers.IntegerField(read_only=True)
    not_helpful_count = serializers.IntegerField(read_only=True)
    has_images = serializers.BooleanField(read_only=True)
    has_response = serializers.BooleanField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'product_id',
            'customer_name',
            'rating',
            'title',
            'comment',
            'is_verified_purchase',
            'created_at',
            'helpful_count',
            'not_helpful_count',
            'has_images',
            'has_response',
        ]
class ReviewCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            'product_id',
            'customer_email',
            'customer_name',
            'rating',
            'title',
            'comment',
            'is_verified_purchase',
        ]

    def validate_title(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "Title must be at least 10 characters long."
            )
        return value

    def validate_comment(self, value):
        if value and len(value) > 2000:
            raise serializers.ValidationError(
                "Comment cannot exceed 2000 characters."
            )
        return value

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        email = attrs.get('customer_email')

        if Review.objects.filter(
            product_id=product_id,
            customer_email=email
        ).exists():
            raise serializers.ValidationError(
                "You have already reviewed this product."
            )

        return attrs
class ReviewImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewImage
        fields = ['image']

    def validate_image(self, image):
        max_size = 5 * 1024 * 1024  # 5MB

        if image.size > max_size:
            raise serializers.ValidationError("Image size must be ≤ 5MB.")

        valid_types = ['image/jpeg', 'image/png']
        if image.content_type not in valid_types:
            raise serializers.ValidationError(
                "Only JPG and PNG images are allowed."
            )

        return image
class HelpfulVoteSerializer(serializers.Serializer):
    voter_email = serializers.EmailField()
    is_helpful = serializers.BooleanField()

    def validate(self, attrs):
        review = self.context['review']
        voter_email = attrs['voter_email']

        if review.customer_email == voter_email:
            raise serializers.ValidationError(
                "You cannot vote on your own review."
            )

        return attrs
class BusinessResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessResponse
        fields = ['response_text', 'responder_name']

    def validate_response_text(self, value):
        if len(value) < 20:
            raise serializers.ValidationError(
                "Response must be at least 20 characters long."
            )
        return value
class AdminReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            'id',
            'product_id',
            'customer_email',
            'rating',
            'title',
            'comment',
            'is_verified_purchase',
            'status',
            'created_at',
        ]
        read_only_fields = [
            'product_id',
            'customer_email',
            'rating',
            'title',
            'comment',
            'created_at',
        ]
