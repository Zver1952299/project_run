from django.core.serializers import serialize
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .models import Run, AthleteInfo, Challenge
from .serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer


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
        qs = super().get_queryset().filter(is_superuser=False)

        qs = qs.annotate(
            runs_finished=Count(
                'runs',
                filter=Q(runs__status=Run.Status.FINISHED)
            )
        )

        user_type = self.request.query_params.get('type', None)
        if user_type == 'athlete':
            qs = qs.filter(is_staff=False)
        elif user_type == 'coach':
            qs = qs.filter(is_staff=True)
        return qs


class RunStatusUpdateView(APIView):
    allowed_transitions = {
        'start': (Run.Status.INIT, Run.Status.IN_PROGRESS),
        'stop': (Run.Status.IN_PROGRESS, Run.Status.FINISHED)
    }

    def post(self, request, id, action):
        if action not in self.allowed_transitions:
            return Response({"detail": 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        expected_status, new_status = self.allowed_transitions[action]
        run = get_object_or_404(Run, id=id)

        if run.status != expected_status:
            return Response(
                {
                    "detail": f"The run status isn't '{expected_status}'",
                    "current_status": run.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        run.status = new_status
        run.save()

        if action == 'stop':
            user = (
                User.objects
                .annotate(
                    runs_finished=Count(
                        'runs',
                        filter=Q(runs__status=Run.Status.FINISHED)
                    )
                )
                .get(id=run.athlete_id)
            )
            if user.runs_finished == 10:
                Challenge.objects.create(full_name="Сделай 10 Забегов!", athlete=user)

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AthleteInfoView(APIView):
    def get_user_or_404(self, id):
        return get_object_or_404(User, id=id)

    def validate_weight(self, weight):
        if weight is None:
            return True
        try:
            weight = int(weight)
        except (TypeError, ValueError):
            return False
        return 0 < weight < 900

    def get_or_create_athlete_info(self, user_id):
        self.get_user_or_404(user_id)

        obj, created = AthleteInfo.objects.get_or_create(
            user_id=user_id,
            defaults={'goals': '', 'weight': None}
        )
        return obj, created

    def build_response(self, obj, created, is_update=False):
        serializer = AthleteInfoSerializer(obj)
        status_code = status.HTTP_201_CREATED if created and is_update else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def get(self, request, id):
        obj, created = self.get_or_create_athlete_info(id)
        return self.build_response(obj, created)

    def put(self, request, id):
        self.get_user_or_404(id)

        weight = request.data.get('weight', None)
        if not self.validate_weight(weight):
            return Response({'detail': 'Weight must be > 0 and < 900'}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = AthleteInfo.objects.update_or_create(
            user_id=id,
            defaults={
                'goals': request.data.get('goals', ''),
                'weight': weight
            }
        )
        return self.build_response(obj, created, is_update=True)


class ChallengeView(APIView):
    def get(self, request):
        qs = Challenge.objects.all()
        athlete = request.query_params.get('athlete')
        if athlete:
            qs = qs.filter(athlete=athlete)
        challenges_list = ChallengeSerializer(qs, many=True).data
        return Response(challenges_list)