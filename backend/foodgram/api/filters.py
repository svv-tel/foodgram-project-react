from django_filters.rest_framework import BaseInFilter, CharFilter, FilterSet
from django.contrib.auth import get_user_model
from recipes.models import Ingredient, Recipe

from django_filters import rest_framework as filters
from recipes.models import Tag

User = get_user_model()


class CharFilterInFilter(BaseInFilter, CharFilter):
    pass



class IngredientFilter(FilterSet):
    name = CharFilter(
        field_name='name',
        lookup_expr='contains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = models.Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if value:
            return models.Recipe.objects.filter(
                favorite_recipe__user=self.request.user
            )
        return models.Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return models.Recipe.objects.filter(
                shopping_cart__user=self.request.user
            )
        return models.Recipe.objects.all()
