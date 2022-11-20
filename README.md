# PyMapMe

**PyMapMe** is a tiny library for mapping [pydantic](https://github.com/pydantic/pydantic) models, it might be useful when you have some model and want to represent it using different structure.

Supported functionality:
- nested mapping
- using helper functions with the access to InModel (see `_get_full_name`)
- using context data, when you need to extend your model with some extra data 

### Getting started

```python
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
    age: int = Field(source_func='_get_age_from_context')

    @staticmethod
    def _get_full_name(model: Profile, default: Any):
        return model.person.name + ' ' + model.person.surname

    @staticmethod
    def _get_age_from_context(model: Profile, default: Any, age: int):
        return age


extra = {'age': 35}
profile = Profile(nickname='baobab', person=Person(name='John', surname='Smith'))
user = User.build_from_model(profile, context=extra)
print(user.dict())
# {'nickname': 'baobab', 'first_name': 'John', 'surname': 'Smith', 'full_name': 'John Smith', 'age': 35}

```

### Development

Run tests:

```
make run-unit-tests
```

Run static analysis:

```
make run-static-analysis
```

Build package:

```
make build-package
```

### Installation

It is recommended to use Poetry:

```
poetry add pymapme
```
