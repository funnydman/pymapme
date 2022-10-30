# PyMapMe

Map one model into another, for example:

### Example

```
from typing import Any

from pydantic import BaseModel, Field
from pymapme.models.mapping import MappingModel


class Person(BaseModel):
    name: str
    surname: str


class Profile(BaseModel):
    nickname: str
    person: Person


class User(MappingModel):
    nickname: str = Field(source='nickname')
    first_name: str = Field(source='person.name')
    surname: str = Field(source='person.surname')
    full_name: str = Field(source_func='_get_full_name')

    @staticmethod
    def _get_full_name(model: Profile, default: Any):
        return model.person.name + ' ' + model.person.surname


profile = Profile(nickname='baobab', person=Person(name='John', surname='Smith'))
user = User.map_from_model(profile)
print(user.dict())  # {'nickname': 'baobab', 'first_name': 'John', 'surname': 'Smith', 'full_name': 'John Smith'}
```