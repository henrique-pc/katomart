from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Course, Module, Lesson, File, Config
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, FileSerializer, ConfigSerializer

# Create your views here.

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'success': True})
        return Response({'success': False, 'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()  # type: ignore[attr-defined]
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()  # type: ignore[attr-defined]
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()  # type: ignore[attr-defined]
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()  # type: ignore[attr-defined]
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

class ConfigViewSet(viewsets.ModelViewSet):
    queryset = Config.objects.all()  # type: ignore[attr-defined]
    serializer_class = ConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
