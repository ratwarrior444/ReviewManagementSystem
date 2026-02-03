from django.urls import path

from .views import (
    PublicReviewListView,
    PublicReviewDetailView,
    ReviewCreateView,
    ReviewImageUploadView,
    ReviewVoteView,

    PendingReviewListView,
    ReviewModerationView,
    BusinessResponseCreateView,
    ReviewSoftDeleteView,

    ReviewStatsView,
)

urlpatterns = [
    

    path(
        'reviews/',
        PublicReviewListView.as_view(),
        name='public-review-list'
    ),

    path(
        'reviews/<int:pk>/',
        PublicReviewDetailView.as_view(),
        name='public-review-detail'
    ),

    path(
        'reviews/create/',
        ReviewCreateView.as_view(),
        name='review-create'
    ),

    path(
        'reviews/<int:review_id>/images/',
        ReviewImageUploadView.as_view(),
        name='review-image-upload'
    ),

    path(
        'reviews/<int:review_id>/vote/',
        ReviewVoteView.as_view(),
        name='review-vote'
    ),

    #  Admin APIs

    path(
        'admin/reviews/pending/',
        PendingReviewListView.as_view(),
        name='admin-pending-reviews'
    ),

    path(
        'admin/reviews/<int:review_id>/moderate/',
        ReviewModerationView.as_view(),
        name='admin-review-moderate'
    ),

    path(
        'admin/reviews/<int:review_id>/respond/',
        BusinessResponseCreateView.as_view(),
        name='admin-review-respond'
    ),

    path(
        'admin/reviews/<int:review_id>/',
        ReviewSoftDeleteView.as_view(),
        name='admin-review-delete'
    ),

    # -------- Analytics --------

    path(
        'reviews/stats/',
        ReviewStatsView.as_view(),
        name='review-stats'
    ),
]
