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
from .models import Run
from .serializers import RunSerializer, UserSerializer


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
    queryset = User.objects.all().filter(is_superuser=False)
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['date_joined']

    def get_queryset(self):
        qs = self.queryset
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
            return  Response(
                {
                    "detail": f"The run status isn't '{expected_status}'",
                    "current_status": run.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        run.status = new_status
        run.save()
        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)