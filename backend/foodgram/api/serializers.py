from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, IngredientRecipeAmount, Recipe, ShoppingCart, Tag
)
from users.serializers import CustomUserSerializer

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'color')
        lookup_field = 'slug'


class CreatTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id')
        lookup_field = 'slug'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('__all__')
        lookup_field = 'id'


class RecipeIngredient(serializers.ModelSerializer):
    class Meta:
        model = IngredientRecipeAmount
        fields = ('id', 'amount',)
        read_only_fields = ('measurement_units', 'name',)
        lookup_field = 'id'


class RecipeIngredientSerializerTest(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipeAmount
        fields = ('id', 'amount', 'measurement_unit', 'name',)
        read_only_fields = ('measurement_unit', 'name',)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializerTest(
        many=True,
        source='ingredient_amount'
    )
    author = CustomUserSerializer()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_anonymous:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)
    ingredients = IngredientRecipeCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name',
                  'text', 'cooking_time', 'author')

    def validate(self, data):
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один ингредиент!'
            )
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_obj = get_object_or_404(Ingredient, id=ingredient['id'])
            amount = ingredient.get('amount')
            if int(amount) <= 0:
                raise serializers.ValidationError(
                    'Убедитесь, что значение количества '
                    f'ингредиента "{ingredient_obj.name}" больше 0'
                )
            if ingredient_obj.id in ingredients_list:
                raise serializers.ValidationError(
                    f'Ингредиент "{ingredient_obj.name}" '
                    'в рецепте не должен повторяться.'
                )
            ingredients_list.append(ingredient_obj.id)
        return data

    def _add_ingredients(self, recipe, ingredients_data):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient_item.get('id')
                ),
                recipe=recipe,
                amount=ingredient_item.get('amount')
            ) for ingredient_item in ingredients_data]
        )

    def get_ingredients(self, obj):
        ingredients = IngredientRecipe.objects.filter(recipe=obj)
        return IngredientRecipeListSerializer(ingredients).data

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.ingredients.clear()
        for tag in tags_data:
            tag_id = tag.id
            tag_object = get_object_or_404(Tag, id=tag_id)
            instance.tags.add(tag_object)
        self._add_ingredients(instance, ingredients_data)
        return instance

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context=self.context
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelField):
    class Meta:
        model = Favorite
        fields = '__all__'


class FavoritRecipeSerializer(RecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowUserSerializer(CustomUserSerializer):
    recipes = FavoritRecipeSerializer(many=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count',
        )


class FollowUserCreateSerializer(FollowUserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )


class ShoppingCartRecipeSerializer(FavoritRecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image',)
