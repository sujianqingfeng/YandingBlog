#!/usr/bin/env python
# encoding: utf-8


from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_auth.registration.views import (
    LoginView, RegisterView, SocialConnectView, SocialLoginView)


from apps.user.serializers import UserRegisterSerializer, UserGetSerializer, UserPostSerializer

User = get_user_model()



class RegisterViewCustom(RegisterView):
    """
    注册视图取消authentication_class一次避免CSRF校验
    """
    authentication_classes = ()



class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(phone=username))

            if user.check_password(password):
                return user
        except Exception as e:
            return None


class UserViewset(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    '''
    create:
    注册用户

    read:
    得到用户信息

    update:
    修改用户

    partial_update:
    部分修改
    '''

    authentication_classes = [SessionAuthentication, JSONWebTokenAuthentication]

    def get_object(self):
        return self.request.user

    def get_permissions(self):
        if self.action == 'create' or self.action == 'retrieve':
            permission_classes = []
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [premission() for premission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action == 'get':
            return UserGetSerializer
        else:
            return UserPostSerializer

    def get_queryset(self):
        return User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = User.objects.get(id=kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
