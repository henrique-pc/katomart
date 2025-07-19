from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, CourseViewSet, ModuleViewSet, LessonViewSet, FileViewSet, SystemConfigViewSet, PlatformAuthViewSet, UserFormattedNameViewSet, UserConfigViewSet, change_language

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'files', FileViewSet)
router.register(r'systemconfig', SystemConfigViewSet)
router.register(r'platformauth', PlatformAuthViewSet)
router.register(r'formattednames', UserFormattedNameViewSet)
router.register(r'userconfig', UserConfigViewSet)

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='api-login'),
    path('api/', include(router.urls)),
    path('language/<str:language_code>/', change_language, name='change_language'),
] 