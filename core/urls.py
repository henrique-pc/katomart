from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, CourseViewSet, ModuleViewSet, LessonViewSet, FileViewSet, ConfigViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'files', FileViewSet)
router.register(r'config', ConfigViewSet)

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/', include(router.urls)),
] 