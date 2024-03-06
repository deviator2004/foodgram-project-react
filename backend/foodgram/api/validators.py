from django.core.exceptions import ValidationError


def tags_ingredients_validator(field, Model, value=None):
    if value is None or len(value) == 0:
        raise ValidationError(f'Должен быть хотя бы один {field}')
    elements = set()
    for element in value:
        if not Model.objects.filter(id=element['id']).exists():
            raise ValidationError(f'Нет {field}а c id {element["id"]}')
        elements.add(element['id'])
    if len(value) > len(elements):
        raise ValidationError(f'Введен повторяющийся {field}')
    return value
