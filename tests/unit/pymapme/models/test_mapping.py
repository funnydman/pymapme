import re
from copy import deepcopy
from datetime import date
from typing import Any, Optional, List

import pytest
from pydantic import Field, BaseModel
from pymapme.exceptions import PyMapMelValidationError
from pymapme.models.mapping import MappingModel


class UserInfo(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]


class CurrentJob(BaseModel):
    has_project: Optional[bool]
    since: Optional[str]


class Skill(BaseModel):
    name: str


class WorkProfile(BaseModel):
    title: Optional[str]
    worked_for: Optional[list]
    current_job: Optional[CurrentJob]
    skills: Optional[List[Skill]]


class DummyModel(BaseModel):
    nickname: Optional[str]
    user_info: Optional[UserInfo]
    work_profile: Optional[WorkProfile]


TEST_DATA = {
    'nickname': 'baobab',
    'user_info': {
        'first_name': 'John',
        'last_name': 'Smith'
    },
    'work_profile': {
        'title': 'Developer',
        'salary': '',
        'worked_for': ['Google', 'Amazon'],
        'current_job': {
            'has_project': False,
            'since': '10-10-2022',
            'documents': [],
            'salary': ''
        },
        'skills': [dict(name='Python'), dict(name='Js')]
    }
}


class DummyMappingModel(MappingModel):
    name: Optional[str] = Field(source='user_info.first_name')
    surname: Optional[str] = Field(source='user_info.last_name')
    nickname: Optional[str] = Field(source='nickname')
    is_working: Optional[str] = Field(source='work_profile.current_job.has_project')
    documents: Optional[list] = Field(source='work_profile.current_job.documents')
    previous_companies: Optional[list] = Field(source='work_profile.worked_for')
    field_with_default_value: Optional[str] = 'default_value'
    current_work_started_since: Optional[str] = Field(source='work_profile.current_job.since')
    non_existing: Optional[str] = Field(source='no_such_field_or_model')
    age: Optional[int] = Field(source_func='_get_age')
    full_name: Optional[str] = Field(source_func='_get_full_name', default='NoFullName')
    skills: Optional[list] = Field(source='work_profile.skills', default=[])

    @staticmethod
    def _get_age(model: DummyModel, default: Any, age: int = None) -> Optional[int]:
        del model
        del default
        return age

    @staticmethod
    def _get_full_name(model: DummyModel, default: Any) -> str:
        if user_info := model.user_info:
            if user_info.first_name and user_info.last_name:
                return user_info.first_name + ' ' + user_info.last_name
        return default


class TestMappingModelFromModel:
    @pytest.fixture
    def actual_model(self):
        yield DummyModel(**TEST_DATA)

    @pytest.fixture
    def mapped_model(self, actual_model):
        yield DummyMappingModel.build_from_model(actual_model)

    @pytest.fixture
    def mapped_model_with_context(self, actual_model):
        context = {'age': 27}
        yield DummyMappingModel.build_from_model(actual_model, context=context)

    def test_from_model(self, mapped_model):
        assert mapped_model == DummyMappingModel(
            name='John',
            surname='Smith',
            non_existing=None,
            nickname='baobab',
            previous_companies=['Google', 'Amazon'],
            current_work_started_since='10-10-2022',
            is_working='False',
            age=None,
            full_name='John Smith',
            skills=[Skill(name='Python'), Skill(name='Js')]
        )

    def test_from_model_default(self):
        data = deepcopy(TEST_DATA)
        data['user_info'].pop('first_name')
        mapped_model = DummyMappingModel.build_from_model(DummyModel(**data))

        assert mapped_model == DummyMappingModel(
            surname='Smith',
            nickname='baobab',
            is_working='False',
            documents=None,
            previous_companies=['Google', 'Amazon'],
            field_with_default_value='default_value',
            current_work_started_since='10-10-2022',
            non_existing=None,
            age=None,
            full_name='NoFullName',
            skills=[Skill(name='Python'), Skill(name='Js')]
        )

    def test_from_model_with_context(self, mapped_model_with_context):
        assert mapped_model_with_context == DummyMappingModel(
            name='John',
            surname='Smith',
            non_existing=None,
            nickname='baobab',
            previous_companies=['Google', 'Amazon'],
            current_work_started_since='10-10-2022',
            is_working='False',
            age=27,
            full_name='John Smith',
            skills=[Skill(name='Python'), Skill(name='Js')]
        )

    def test_from_model_failed_to_map_validation_error(self, actual_model):
        actual_model.user_info = 'John Smith'

        with pytest.raises(
                PyMapMelValidationError,
                match="'str' object has no attribute 'first_name'"
        ):
            DummyMappingModel.build_from_model(actual_model)

    def test_from_model_model_validation_error(self, actual_model):
        actual_model.work_profile.current_job.since = date(day=10, month=10, year=2022)

        with pytest.raises(
                PyMapMelValidationError,
                match=re.escape('1 validation error for DummyMappingModel\n'
                                'current_work_started_since\n'
                                '  str type expected (type=type_error.str)')
        ):
            DummyMappingModel.build_from_model(actual_model)

    def test_dump(self, mapped_model):
        assert mapped_model.json() == '{"name": "John", "surname": "Smith", ' \
                                      '"nickname": "baobab", "is_working": "False", ' \
                                      '"documents": null, "previous_companies": ["Google", "Amazon"], ' \
                                      '"field_with_default_value": "default_value", ' \
                                      '"current_work_started_since": "10-10-2022", "non_existing": null, ' \
                                      '"age": null, "full_name": "John Smith", ' \
                                      '"skills": [{"name": "Python"}, {"name": "Js"}]}'
