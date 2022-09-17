from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientRecipeAmount, Recipe, ShoppingCart, Tag
)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'color', 'slug',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'
    list_per_page = 50


class IngredientInline(admin.TabularInline):
    model = IngredientRecipeAmount
    extra = 1
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'tags', 'starred_count',)
    search_fields = ('name', 'author', 'tags')
    list_filter = ('name', 'author', 'tags',)
    empty_value_display = '-пусто-'
    inlines = (IngredientInline,)

    def starred_count(self, obj):
        result = Favorite.objects.filter(recipe=obj).count()
        return result


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'recipe',
    )
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


class IngredientRecipeAmountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'recipe', 'amount'
    )
    search_fields = ('recipe',)
    empty_value_display = '-пусто-'
    list_per_page = 50


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(IngredientRecipeAmount, IngredientRecipeAmountAdmin)
