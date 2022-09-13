from recipes.models import IngredientRecipeAmount, ShoppingCart


def generate_shopping_list(user):
    ingredient_list = {}
    text = f'Ваш список покупок: \n\n'
    recipes_in_shopping_cart = ShoppingCart.objects.filter(user=user)
    for recipe in recipes_in_shopping_cart:
        ingredient_recipe = IngredientRecipeAmount.objects.filter(
            recipe=recipe.recipe
        )
        for element in ingredient_recipe:
            if element.ingredient.name in ingredient_list:
                ingredient_list[element.ingredient.name]['Количество'] += (
                    element.amount
                )
            else:
                ingredient_list.update(
                    {
                        element.ingredient.name: {
                            'Количество': element.amount,
                            'Единицы': element.ingredient.measurement_unit
                        }
                    }
                )
    for ingredient in ingredient_list:
        amount = ingredient_list[ingredient]['Количество']
        unit = ingredient_list[ingredient]['Единицы']
        text += f'{ingredient} {amount} {unit} \n'
    return text
