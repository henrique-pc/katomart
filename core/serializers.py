from rest_framework import serializers
from .models import Course, Module, Lesson, File, SystemConfig, PlatformAuth, UserFormattedName, Platform, UserConfig
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    internal_id = serializers.ReadOnlyField()
    katomart_id = serializers.ReadOnlyField()
    external_id = serializers.ReadOnlyField()
    class Meta:
        model = Course
        fields = '__all__'

class ModuleSerializer(serializers.ModelSerializer):
    internal_id = serializers.ReadOnlyField()
    katomart_id = serializers.ReadOnlyField()
    external_id = serializers.ReadOnlyField()
    class Meta:
        model = Module
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    internal_id = serializers.ReadOnlyField()
    katomart_id = serializers.ReadOnlyField()
    external_id = serializers.ReadOnlyField()
    class Meta:
        model = Lesson
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    internal_id = serializers.ReadOnlyField()
    katomart_id = serializers.ReadOnlyField()
    external_id = serializers.ReadOnlyField()
    class Meta:
        model = File
        fields = '__all__'

class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'

class PlatformAuthSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    platform = serializers.PrimaryKeyRelatedField(queryset=Platform.objects.all())  # type: ignore[attr-defined]
    password = serializers.CharField(write_only=True, required=False)
    token = serializers.CharField(write_only=True, required=False, allow_blank=True)
    session_cookie = serializers.CharField(write_only=True, required=False, allow_blank=True)
    refresh_token = serializers.CharField(write_only=True, required=False, allow_blank=True)
    passphrase = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = PlatformAuth
        fields = [
            'id', 'user', 'platform', 'username', 'password', 'token', 'session_cookie', 'refresh_token',
            'token_type', 'state', 'expires_at', 'extra_data', 'passphrase'
        ]
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        passphrase = validated_data.pop('passphrase')
        password = validated_data.pop('password', None)
        token = validated_data.pop('token', None)
        session_cookie = validated_data.pop('session_cookie', None)
        refresh_token = validated_data.pop('refresh_token', None)
        user = self.context['request'].user
        obj = PlatformAuth(**validated_data)
        obj.user = user
        obj.set_credentials(password or '', token, session_cookie, refresh_token, passphrase)
        obj.save()
        return obj

    def update(self, instance, validated_data):
        passphrase = validated_data.pop('passphrase', None)
        password = validated_data.pop('password', None)
        token = validated_data.pop('token', None)
        session_cookie = validated_data.pop('session_cookie', None)
        refresh_token = validated_data.pop('refresh_token', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if passphrase and (password or token or session_cookie or refresh_token):
            instance.set_credentials(password or '', token, session_cookie, refresh_token, passphrase)
        instance.save()
        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Remove sensitive fields
        rep.pop('password', None)
        rep.pop('token', None)
        rep.pop('session_cookie', None)
        rep.pop('refresh_token', None)
        rep.pop('passphrase', None)
        return rep

class UserFormattedNameSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = UserFormattedName
        fields = ['id', 'user', 'content_type', 'object_id', 'formatted_name']
        read_only_fields = ['id', 'user']

class UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserConfig
        fields = '__all__'
        read_only_fields = ['user']
