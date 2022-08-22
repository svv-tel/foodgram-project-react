from django.core.exceptions import ValidationError
from recipes.models import Ingredient


def ingredients_validator(ingredient_list):
    testing_list = []
    for ingr in ingredient_list:
        if ingr['id'] in testing_list:
            failed_ingr = Ingredient.objects.get(pk=ingr['id'])
            raise ValidationError(
                'Нельзя добавлять несколько '
                f'одинаковых ингредиентов {failed_ingr}'
            )
        testing_list.append(ingr['id'])
