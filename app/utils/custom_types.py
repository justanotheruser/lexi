from typing import TYPE_CHECKING, Annotated, NewType, TypeAlias, Union

from aiogram.types import ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pydantic import PlainValidator

AnyKeyboard: TypeAlias = Union[
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
]

if TYPE_CHECKING:
    ListStr: TypeAlias = list[str]
else:
    ListStr = NewType("ListStr", list[str])

StringList: TypeAlias = Annotated[ListStr, PlainValidator(func=lambda x: x.split(","))]
Int16: TypeAlias = Annotated[int, 16]
Int32: TypeAlias = Annotated[int, 32]
Int64: TypeAlias = Annotated[int, 64]
