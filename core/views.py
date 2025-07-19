from django.shortcuts import render, redirect
from django.utils import translation
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Course, Module, Lesson, File, SystemConfig, PlatformAuth, UserFormattedName, UserConfig
from .serializers import CourseSerializer, ModuleSerializer, LessonSerializer, FileSerializer, SystemConfigSerializer, PlatformAuthSerializer, UserFormattedNameSerializer, UserConfigSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def change_language(request, language_code):
    """Change the language and redirect back to the previous page"""
    translation.activate(language_code)
    request.session[settings.LANGUAGE_SESSION_KEY] = language_code
    
    # Get the referer URL or default to admin index
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return HttpResponseRedirect(referer)
    else:
        return redirect('admin:index')

class IsOwnerOrSuperuser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, PlatformAuth):
            return obj.user == request.user
        if isinstance(obj, UserFormattedName):
            return obj.user == request.user
        return False

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

class SystemConfigViewSet(viewsets.ModelViewSet):
    queryset = SystemConfig.objects.all()  # type: ignore[attr-defined]
    serializer_class = SystemConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

class PlatformAuthViewSet(viewsets.ModelViewSet):
    queryset = PlatformAuth.objects.none()  # type: ignore[attr-defined]
    serializer_class = PlatformAuthSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperuser]

    def get_queryset(self):
        user = self.request.user
        return PlatformAuth.objects.filter(user=user)  # type: ignore[attr-defined]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserFormattedNameViewSet(viewsets.ModelViewSet):
    queryset = UserFormattedName.objects.none()  # type: ignore[attr-defined]
    serializer_class = UserFormattedNameSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperuser]

    def get_queryset(self):
        return UserFormattedName.objects.filter(user=self.request.user)  # type: ignore[attr-defined]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserConfigViewSet(viewsets.ModelViewSet):
    queryset = UserConfig.objects.none()  # type: ignore[attr-defined]
    serializer_class = UserConfigSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserConfig.objects.filter(user=self.request.user)  # type: ignore[attr-defined]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
