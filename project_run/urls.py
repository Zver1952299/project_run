from django.contrib import admin
from django.urls import path, include

from app_run.views import company_details
from rest_framework.routers import DefaultRouter
from app_run.views import RunViewSet, UserViewSet, RunStatusUpdateView, AthleteInfoView, ChallengeView, PositionViewSet, CollectibleItemViewSet, UploadFileView, SubscribeView, ChallengeSummaryView, RatingView, AnalyticView
# from rest_framework.authtoken import views as drf_auth_views


router = DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)
router.register('api/positions', PositionViewSet)
router.register('api/collectible_item', CollectibleItemViewSet)

urlpatterns = ([
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:id>/<str:action>/', RunStatusUpdateView.as_view()),
    path('api/athlete_info/<int:id>/', AthleteInfoView.as_view()),
    path('api/challenges/', ChallengeView.as_view()),
    path('api/challenges_summary/', ChallengeSummaryView.as_view()),
    path('api/upload_file/', UploadFileView.as_view()),
    path('api/subscribe_to_coach/<int:id>/', SubscribeView.as_view()),
    path('api/rate_coach/<int:coach_id>/', RatingView.as_view()),
    path('api/analytics_for_coach/<int:coach_id>/', AnalyticView.as_view()),
    # path('api/token/', drf_auth_views.obtain_auth_token),
    path('', include(router.urls))
])