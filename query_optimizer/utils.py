from django.db.models import ForeignKey
from graphene import Connection
from graphene.types.definitions import GrapheneObjectType
from graphene_django import DjangoObjectType
from graphql import GraphQLNonNull, GraphQLOutputType, SelectionNode
from graphql.execution.execute import get_field_def

from .typing import Collection, GQLInfo, ModelField, ToManyField, ToOneField, TypeGuard, TypeVar

__all__ = [
    "get_field_type",
    "get_selections",
    "get_underlying_type",
    "is_foreign_key_id",
    "is_to_many",
    "is_to_one",
    "unique",
]


T = TypeVar("T")


def is_foreign_key_id(model_field: ModelField, name: str) -> bool:
    return isinstance(model_field, ForeignKey) and model_field.name != name and model_field.get_attname() == name


def get_underlying_type(field_type: GraphQLOutputType) -> GrapheneObjectType:
    while hasattr(field_type, "of_type"):
        field_type = field_type.of_type
    return field_type


def is_to_many(model_field: ModelField) -> TypeGuard[ToManyField]:
    return bool(model_field.one_to_many or model_field.many_to_many)


def is_to_one(model_field: ModelField) -> TypeGuard[ToOneField]:
    return bool(model_field.many_to_one or model_field.one_to_one)


def get_field_type(info: GQLInfo) -> GrapheneObjectType:
    field_node = info.field_nodes[0]
    field_def = get_field_def(info.schema, info.parent_type, field_node)
    return get_underlying_type(field_def.type)


def get_selections(info: GQLInfo) -> tuple[SelectionNode, ...]:
    field_node = info.field_nodes[0]
    selection_set = field_node.selection_set
    return () if selection_set is None else selection_set.selections


def unique(items: Collection[T]) -> list[T]:
    return list(dict.fromkeys(items))


def can_optimize(info: GQLInfo) -> bool:
    return_type = info.return_type
    if isinstance(return_type, GraphQLNonNull):
        return_type = return_type.of_type

    return isinstance(return_type, GrapheneObjectType) and (
        issubclass(return_type.graphene_type, (DjangoObjectType, Connection))
    )
