from __future__ import annotations

import decimal
import typing

from django_filters import (
    Filter,
    BooleanFilter,
    ChoiceFilter,
    DateFilter,
    DateFromToRangeFilter,
    DateTimeFilter,
    DateTimeFromToRangeFilter,
    NumberFilter,
    TimeFilter,
    TypedChoiceFilter,
    MultipleChoiceFilter,
    TypedMultipleChoiceFilter,
)


def _get_filter_schema_choice(
    filter_field: typing.Union[
        ChoiceFilter, MultipleChoiceFilter, TypedChoiceFilter, TypedMultipleChoiceFilter
    ]
) -> dict:
    choice_type = 'string'

    try:
        choices = filter_field.field.choices
    except KeyError:
        return {'type': choice_type}

    for type_, repr_ in (
        (bool, 'boolean'),
        (int, 'integer'),
        ((int, float, decimal.Decimal), 'number'),
    ):
        if all(isinstance(choice, type_) for choice, _ in choices):
            choice_type = repr_
            break

    return {'type': choice_type, 'enum': [c[0] for c in choices]}


FILTER_MAP = {
    BooleanFilter: {'type': 'boolean'},
    ChoiceFilter: _get_filter_schema_choice,
    MultipleChoiceFilter: _get_filter_schema_choice,
    TypedChoiceFilter: _get_filter_schema_choice,
    TypedMultipleChoiceFilter: _get_filter_schema_choice,
    DateFilter: {'type': 'string', 'format': 'date'},
    DateFromToRangeFilter: {'type': 'string', 'format': 'date'},
    DateTimeFilter: {'type': 'string', 'format': 'date-time'},
    DateTimeFromToRangeFilter: {'type': 'string', 'format': 'date-time'},
    NumberFilter: {'type': 'number'},
    TimeFilter: {'type': 'string', 'format': 'time'},
}


def get_filter_schema(filter_field: Filter, filter_map: dict = None) -> dict:
    filter_map = filter_map or FILTER_MAP
    field_parents = type(filter_field).mro()

    schema: dict | typing.Callable = {'type': 'string'}
    for field_parent in field_parents[:-1]:
        try:
            schema = filter_map[field_parent]
            break
        except KeyError:
            pass

    if callable(schema):
        schema = schema(filter_field)
    return schema
