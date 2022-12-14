from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.pagination import PageNumberPagination

from api.serializers import (
    CreateRecipeSerializer, FollowUserCreateSerializer,
    FollowUserSerializer,
    IngredientSerializer, RecipeSerializer,
    ShoppingCartRecipeSerializer, TagSerializer
)
from recipes.models import (
    Favorite, Follow, Ingredient, Recipe, ShoppingCart, Tag,
)
from .filters import IngredientFilter, RecipeFilter
from .mixins import (
    AllMethodsMixin, CreateDestroyMixin,
    ListCreateDestroyMixin, ListRetreiveMixin,
)
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import FavoritRecipeSerializer
from .utils import generate_shopping_list

User = get_user_model()


class TagsViewSet(ListRetreiveMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(ListRetreiveMixin):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = IngredientFilter
    search_fields = ('name',)


class RecipeViewSet(AllMethodsMixin):
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by('id')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        is_favorited = self.request.query_params.get('is_favorited')
        cart = ShoppingCart.objects.filter(user=self.request.user.id)
        favorite = Favorite.objects.filter(user=self.request.user.id)

        if is_in_shopping_cart == 'true':
            queryset = queryset.filter(cart__in=cart)
        elif is_in_shopping_cart == 'false':
            queryset = queryset.exclude(cart__in=cart)
        if is_favorited == 'true':
            queryset = queryset.filter(favorite__in=favorite)
        elif is_favorited == 'false':
            queryset = queryset.exclude(favorite__in=favorite)
        return queryset.all().order_by('-id')

    def create(self, request, *args, **kwargs):
        serializer = CreateRecipeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.save()

    def get_success_headers(self, data):
        try:
            return {'Location': str(data[api_settings.URL_FIELD_NAME])}
        except (TypeError, KeyError):
            return {}

    def update(self, request, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = CreateRecipeSerializer(
            instance,
            context={'request': request},
            data=request.data,
            partial=partial
        )
        serializer.is_valid()
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class FollowListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)

    def list(self, request):
        user = request.user
        user_subscriptions = Follow.objects.filter(user=user)
        queryset = User.objects.filter(following__in=user_subscriptions)
        page = self.paginate_queryset(queryset)
        serializer = FollowUserSerializer(
            page,
            many=True,
            context={'request': request}
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class FollowCreateDestroyViewSet(CreateDestroyMixin):
    lookup_field = 'id'

    def create(self, request, pk):
        queryset = Follow.objects.all()
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if user == author:
            return Response(
                '???????????? ?????????????????????? ???? ???????????? ????????',
                status=status.HTTP_400_BAD_REQUEST
            )
        if not Follow.objects.filter(user=user, author=author):
            Follow.objects.create(user=user, author=author)
            queryset = author
            serializer = FollowUserCreateSerializer(
                queryset,
                context={
                    'request': request,
                    'pk': pk
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            f'?????? ?????????????????? ???? {author}',
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if not Follow.objects.filter(user=user, author=author):
            return Response(
                f'???? ?????????????????? ???? {author}',
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=user, author=author).delete()
        return Response(
            f'?????????????? ???????????????????? ???? {author.username}',
            status=status.HTTP_204_NO_CONTENT
        )


class FavoriteViewSet(CreateDestroyMixin):
    lookup_field = 'id'
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def create(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if not Favorite.objects.filter(user=user, recipe=recipe):
            Favorite.objects.create(user=user, recipe=recipe)
            queryset = get_object_or_404(Recipe, pk=pk)
            serializer = FavoritRecipeSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(
            f'???? ?????? ???????????????? {recipe.name} ?? ??????????????????',
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            f'???????????? {recipe.name} ???????????? ???? ????????????????????',
            status=status.HTTP_204_NO_CONTENT
        )


class CartViewSet(ListCreateDestroyMixin):
    def list(self, request, *args, **kwargs):
        shopping_list = generate_shopping_list(request.user)
        response = HttpResponse(
            shopping_list,
            status=status.HTTP_200_OK,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="my_shopping_list.txt"'
        )
        return response

    def create(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe):
            ShoppingCart.objects.create(user=user, recipe=recipe)
            queryset = get_object_or_404(Recipe, pk=recipe_id)
            serializer = ShoppingCartRecipeSerializer(queryset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            f'???? ?????? ???????????????? {recipe.name} ?? ??????????????',
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, **kwargs):
        user = request.user
        recipe_id = kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe):
            return Response(
                f'???????????? {recipe.name} ?????????????????????? ?? ??????????????',
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()
        return Response(
            f'???????????? {recipe.name} ?????????????? ???????????? ???? ??????????????',
            status=status.HTTP_204_NO_CONTENT
        )
