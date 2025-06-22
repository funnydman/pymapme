import re
from copy import deepcopy
from datetime import date
from typing import Any

import pytest
from pydantic import BaseModel, Field

from pymapme.exceptions import PyMapMeValidationError
from pymapme.models.mapping import MappingModel


class UserInfo(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class CurrentJob(BaseModel):
    has_project: bool | None
    since: str | None


class Skill(BaseModel):
    name: str


class WorkProfile(BaseModel):
    title: str | None
    worked_for: list | None
    current_job: CurrentJob | None
    skills: list[Skill] | None


class DummyModel(BaseModel):
    nickname: str | None
    user_info: UserInfo | None
    work_profile: WorkProfile | None


TEST_DATA = {
    "nickname": "baobab",
    "user_info": {"first_name": "John", "last_name": "Smith"},
    "work_profile": {
        "title": "Developer",
        "salary": "",
        "worked_for": ["Google", "Amazon"],
        "current_job": {"has_project": False, "since": "10-10-2022", "documents": [], "salary": ""},
        "skills": [{"name": "Python"}, {"name": "Js"}],
    },
}


class DummyMappingModel(MappingModel):
    name: str | None = Field(default=None, json_schema_extra={"source": "user_info.first_name"})
    surname: str | None = Field(json_schema_extra={"source": "user_info.last_name"})
    nickname: str | None = Field(json_schema_extra={"source": "nickname"})
    is_working: bool | None = Field(json_schema_extra={"source": "work_profile.current_job.has_project"})
    documents: list | None = Field(default=None, json_schema_extra={"source": "work_profile.current_job.documents"})
    previous_companies: list | None = Field(json_schema_extra={"source": "work_profile.worked_for"})
    field_with_default_value: str | None = "default_value"
    current_work_started_since: str | None = Field(json_schema_extra={"source": "work_profile.current_job.since"})
    non_existing: str | None = Field(default=None, json_schema_extra={"source": "no_such_field_or_model"})
    age: int | None = Field(json_schema_extra={"source_func": "_get_age"})
    full_name: str | None = Field(default="NoFullName", json_schema_extra={"source_func": "_get_full_name"})
    skills: list | None = Field(default=[], json_schema_extra={"source": "work_profile.skills"})

    @staticmethod
    def _get_age(model: DummyModel, default: Any, age: int | None = None) -> int | None:
        del model
        del default
        return age

    @staticmethod
    def _get_full_name(model: DummyModel, default: Any) -> str:
        if user_info := model.user_info:
            if user_info.first_name and user_info.last_name:
                return user_info.first_name + " " + user_info.last_name
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
        context = {"age": 27}
        yield DummyMappingModel.build_from_model(actual_model, context=context)

    def test_from_model(self, mapped_model):
        assert mapped_model == DummyMappingModel(
            name="John",
            surname="Smith",
            non_existing=None,
            nickname="baobab",
            previous_companies=["Google", "Amazon"],
            current_work_started_since="10-10-2022",
            is_working=False,
            age=None,
            full_name="John Smith",
            skills=[Skill(name="Python"), Skill(name="Js")],
        )

    def test_from_model_default(self):
        data = deepcopy(TEST_DATA)
        data["user_info"].pop("first_name")
        mapped_model = DummyMappingModel.build_from_model(DummyModel(**data))

        assert mapped_model == DummyMappingModel(
            name=None,
            surname="Smith",
            nickname="baobab",
            is_working=False,
            documents=None,
            previous_companies=["Google", "Amazon"],
            field_with_default_value="default_value",
            current_work_started_since="10-10-2022",
            non_existing=None,
            age=None,
            full_name="NoFullName",
            skills=[Skill(name="Python"), Skill(name="Js")],
        )

    def test_from_model_with_context(self, mapped_model_with_context):
        assert mapped_model_with_context == DummyMappingModel(
            name="John",
            surname="Smith",
            non_existing=None,
            nickname="baobab",
            previous_companies=["Google", "Amazon"],
            current_work_started_since="10-10-2022",
            is_working=False,
            age=27,
            full_name="John Smith",
            skills=[Skill(name="Python"), Skill(name="Js")],
        )

    def test_from_model_failed_to_map_validation_error(self, actual_model):
        actual_model.user_info = "John Smith"

        with pytest.raises(PyMapMeValidationError, match="'str' object has no attribute 'first_name'"):
            DummyMappingModel.build_from_model(actual_model)

    def test_from_model_model_validation_error(self, actual_model):
        actual_model.work_profile.current_job.since = date(day=10, month=10, year=2022)

        with pytest.raises(
            PyMapMeValidationError,
            match=re.escape(
                "1 validation error for DummyMappingModel\n"
                "current_work_started_since\n"
                "  Input should be a valid string [type=string_type, input_value=datetime.date(2022, 10, 10), input_type=date]"
            ),
        ):
            DummyMappingModel.build_from_model(actual_model)

    def test_dump(self, mapped_model):
        expected_json = mapped_model.model_dump_json()
        assert expected_json == '{"name":"John","surname":"Smith","nickname":"baobab","is_working":false,"documents":null,"previous_companies":["Google","Amazon"],"field_with_default_value":"default_value","current_work_started_since":"10-10-2022","non_existing":null,"age":null,"full_name":"John Smith","skills":[{"name":"Python"},{"name":"Js"}]}'

    def test_non_callable_source_func(self):
        class TestModel(BaseModel):
            name: str = "test"

        class MappingWithNonCallableFunc(MappingModel):
            # This will trigger the non-callable path in utils.py line 45
            # Using a non-string, non-callable value
            result: str | None = Field(
                default=None,
                json_schema_extra={"source_func": 123},  # Not callable, not a string
            )

        source = TestModel()
        mapped = MappingWithNonCallableFunc.build_from_model(source)

        # Should use default value when source_func is not callable
        assert mapped.result is None
