from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.contrib.auth.models import User

from .models import Run, Position, CollectibleItem
from .serializers import RunSerializer, UserSerializer, PositionSerializer, CollectibleItemSerializer

from .services.run_service import RunService
from .services.athlete_info_service import AthleteInfoService
from .services.position_service import PositionService
from .services.collectible_item_service import CollectibleItemService
from .services.subscribe_service import SubscribeService
from .services.challenge_summary_service import ChallengeSummaryService
from .services.rating_service import RatingService
from .services.analytic_service import AnalyticsService
from .services.user_service import UserService
from .services.challenge_service import ChallengeService


@api_view(['GET'])
def company_details(request):
    details = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)


class RunPagination(PageNumberPagination):
    page_size_query_param = 'size'


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    pagination_class = RunPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'athlete']
    ordering_fields = ['created_at']


class UserPagination(PageNumberPagination):
    page_size_query_param = 'size'


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        user_type = self.request.query_params.get('type', None)
        return UserService.get_filtered_users(user_type)

    def get_serializer_class(self):
        user = self.get_object() if self.action == 'retrieve' else None
        return UserService.get_serializer_for_user(user, self.action)


class RunStatusUpdateView(APIView):
    def post(self, request, id, action):
        try:
            run = RunService.update_status(id, action)
        except ValueError:
            return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
        except RuntimeError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AthleteInfoView(APIView):
    def get(self, request, id):
        obj, created = AthleteInfoService.get_or_create_athlete_info(id)
        return AthleteInfoService.build_response(obj, created)

    def put(self, request, id):
        try:
            obj, created = AthleteInfoService.update_athlete_info(
                user_id=id,
                goals=request.data.get('goals'),
                weight=request.data.get('weight')
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return AthleteInfoService.build_response(obj, created, is_update=True)


class ChallengeView(APIView):
    def get(self, request):
        athlete = request.query_params.get('athlete')
        qs = ChallengeService.get_challenges(athlete)
        challenges_list = ChallengeService.serialize_challenges(qs)
        return Response(challenges_list)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['run']

    def perform_create(self, serializer):
        position = serializer.save()
        PositionService.update_collectibles_and_stats(position)


class CollectibleItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CollectibleItem.objects.all()
    serializer_class = CollectibleItemSerializer


class UploadFileView(APIView):
    def post(self, request):
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({'detail': 'No file uploaded'}, status=400)
        broken_rows = CollectibleItemService.import_from_excel(uploaded_file)

        return Response(broken_rows)


class SubscribeView(APIView):
    def post(self, request, id):
        athlete_id = request.data.get('athlete')
        try:
            SubscribeService.subscribe(athlete_id, id)
        except ValueError as e:
            return Response({'detail': str(e)}, status=400)
        return Response({'detail': 'Subscribed successfully'})


class ChallengeSummaryView(APIView):
    def get(self, request):
        data = ChallengeSummaryService.get_grouped_challenges()
        return Response(data)


class RatingView(APIView):
    def post(self, request, coach_id):
        athlete_id = request.data.get('athlete')
        rating = request.data.get('rating')
        result = RatingService.rate_athlete(coach_id, athlete_id, rating)

        if 'error' in result:
            return Response({'detail': result['error']}, status=result.get('status', status.HTTP_400_BAD_REQUEST))
        return Response({'detail': result['success']})


class AnalyticView(APIView):
    def get(self, request, coach_id):
        data = AnalyticsService.get_coach_analytics(coach_id)
        return Response(data)