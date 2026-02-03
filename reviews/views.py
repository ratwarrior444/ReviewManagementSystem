from django.db.models import Count, Avg, Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Review, ReviewImage, HelpfulVote, BusinessResponse
from .serializers import (
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewImageSerializer,
    HelpfulVoteSerializer,
    BusinessResponseSerializer,
    AdminReviewSerializer
)

class PublicReviewListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer

    def get_queryset(self):
        queryset = Review.objects.filter(status=Review.STATUS_APPROVED)

        product_id = self.request.query_params.get('product_id')
        rating = self.request.query_params.get('rating')
        verified = self.request.query_params.get('verified_purchase')

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if rating:
            queryset = queryset.filter(rating=rating)

        if verified is not None:
            if verified.lower() == 'true':
                queryset = queryset.filter(is_verified_purchase=True)
            elif verified.lower() == 'false':
                queryset = queryset.filter(is_verified_purchase=False)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(comment__icontains=search) |
                Q(customer_name__icontains=search)
            )

        ordering = self.request.query_params.get('ordering')
        if ordering in ['created_at', '-created_at', 'rating', '-rating']:
            queryset = queryset.order_by(ordering)
            
        return queryset
    
    
    
class PublicReviewDetailView(generics.RetrieveAPIView):
    serializer_class = ReviewListSerializer

    def get_queryset(self):
        return Review.objects.filter(status=Review.STATUS_APPROVED)
    
    
    
class ReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewCreateSerializer
    
    

class ReviewImageUploadView(APIView):

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        if review.images.count() >= 5:
            return Response(
                {"error": "Maximum 5 images allowed per review."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ReviewImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ReviewImage.objects.create(
            review=review,
            image=serializer.validated_data['image']
        )

        return Response(
            {"message": "Image uploaded successfully."},
            status=status.HTTP_201_CREATED
        )


class ReviewVoteView(APIView):

    def post(self, request, review_id):
        review = get_object_or_404(
            Review,
            id=review_id,
            status=Review.STATUS_APPROVED
        )

        serializer = HelpfulVoteSerializer(
            data=request.data,
            context={'review': review}
        )
        serializer.is_valid(raise_exception=True)

        vote, created = HelpfulVote.objects.update_or_create(
            review=review,
            voter_email=serializer.validated_data['voter_email'],
            defaults={
                'is_helpful': serializer.validated_data['is_helpful']
            }
        )

        return Response(
            {"message": "Vote recorded."},
            status=status.HTTP_200_OK
        )


class ReviewVoteView(APIView):

    def post(self, request, review_id):
        review = get_object_or_404(
            Review,
            id=review_id,
            status=Review.STATUS_APPROVED
        )

        serializer = HelpfulVoteSerializer(
            data=request.data,
            context={'review': review}
        )
        serializer.is_valid(raise_exception=True)

        vote, created = HelpfulVote.objects.update_or_create(
            review=review,
            voter_email=serializer.validated_data['voter_email'],
            defaults={
                'is_helpful': serializer.validated_data['is_helpful']
            }
        )

        return Response(
            {"message": "Vote recorded."},
            status=status.HTTP_200_OK
        )



class PendingReviewListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(status=Review.STATUS_PENDING)



class ReviewModerationView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        status_value = request.data.get('status')
        if status_value not in [
            Review.STATUS_APPROVED,
            Review.STATUS_REJECTED
        ]:
            return Response(
                {"error": "Status must be approved or rejected."},
                status=status.HTTP_400_BAD_REQUEST
            )

        review.status = status_value
        review.save()

        return Response(
            {"message": f"Review {status_value}."},
            status=status.HTTP_200_OK
        )


class BusinessResponseCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        review = get_object_or_404(
            Review,
            id=review_id,
            status=Review.STATUS_APPROVED
        )

        if hasattr(review, 'business_response'):
            return Response(
                {"error": "Response already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BusinessResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        BusinessResponse.objects.create(
            review=review,
            **serializer.validated_data
        )

        return Response(
            {"message": "Response added."},
            status=status.HTTP_201_CREATED
        )


class ReviewSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        review.status = Review.STATUS_REJECTED
        review.save()

        return Response(
            {"message": "Review rejected."},
            status=status.HTTP_200_OK
        )


class ReviewStatsView(APIView):

    def get(self, request):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response(
                {"error": "product_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reviews = Review.objects.filter(
            product_id=product_id,
            status=Review.STATUS_APPROVED
        )

        total_reviews = reviews.count()
        average_rating = reviews.aggregate(
            avg=Avg('rating')
        )['avg']

        rating_distribution = (
            reviews.values('rating')
            .annotate(count=Count('id'))
        )

        data = {
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "rating_distribution": rating_distribution,
            "verified_purchase_count": reviews.filter(
                is_verified_purchase=True
            ).count(),
            "with_images_count": reviews.filter(
                images__isnull=False
            ).distinct().count(),
            "with_response_count": reviews.filter(
                business_response__isnull=False
            ).count(),
        }

        return Response(data, status=status.HTTP_200_OK)
