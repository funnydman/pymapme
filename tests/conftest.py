from typing import Any, Optional, List

from pydantic import Field, BaseModel
import pytest

from pymapme.models.mapping import MappingModel


class UserInfo(BaseModel):
    first_name: str = Field(default=None)
    last_name: str = Field(default=None)


class CurrentJob(BaseModel):
    has_project: bool = Field(default=None)
    since: str = Field(default=None)
    documents: list = Field(default=lambda: [])
    salary: str = Field(default=None)


class Skill(BaseModel):
    name: str = Field()


class WorkProfile(BaseModel):
    title: str = Field(default=None)
    worked_for: list = Field(default=lambda: [])
    current_job: CurrentJob = Field(default=None)
    skills: List[Skill] = Field(default=lambda: [])


class DummyModel(BaseModel):
    nickname: str = Field(default=None)
    user_info: UserInfo = Field(default=None)
    work_profile: WorkProfile = Field(default=None)


@pytest.fixture
def test_data():
    return {
        "nickname": "baobab",
        "user_info": {"first_name": "John", "last_name": "Smith"},
        "work_profile": {
            "title": "Developer",
            "salary": "",
            "worked_for": ["Google", "Amazon"],
            "current_job": {
                "has_project": False,
                "since": "10-10-2022",
                "documents": [],
                "salary": "",
            },
            "skills": [{"name": "Python"}, {"name": "Js"}],
        },
    }


@pytest.fixture
def actual_model(test_data):
    yield DummyModel(**test_data)


@pytest.fixture
def mapped_model(actual_model):
    yield DummyMappingModel.build_from_model(actual_model)


@pytest.fixture
def mapped_model_with_context(actual_model):
    context = {"age": 27}
    yield DummyMappingModel.build_from_model(actual_model, context=context)


class DummyMappingModel(MappingModel):
    name: str | None = Field(
        json_schema_extra={"source": "user_info.first_name"}, default=None
    )
    surname: str | None = Field(
        json_schema_extra={"source": "user_info.last_name"}, default=None
    )
    nickname: str | None = Field(json_schema_extra={"source": "nickname"}, default=None)
    is_working: Optional[bool] = Field(
        json_schema_extra={"source": "work_profile.current_job.has_project"},
        default=None,
    )
    documents: list = Field(
        json_schema_extra={"source": "work_profile.current_job.documents"}, default=[]
    )
    previous_companies: list = Field(
        json_schema_extra={"source": "work_profile.worked_for"}, default=[]
    )
    field_with_default_value: str = Field(default="default_value")
    current_work_started_since: str = Field(
        json_schema_extra={"source": "work_profile.current_job.since"}, default=None
    )
    non_existing: str | None = Field(
        json_schema_extra={"source": "no_such_field_or_model"}, default=None
    )
    age: int | None = Field(json_schema_extra={"source_func": "_get_age"}, default=None)
    full_name: str | None = Field(
        json_schema_extra={"source_func": "_get_full_name"}, default="NoFullName"
    )
    skills: list = Field(
        json_schema_extra={"source": "work_profile.skills"}, default=[]
    )

    @staticmethod
    def _get_age(model: DummyModel, default: Any, age: int = None) -> Optional[int]:
        return age

    @staticmethod
    def _get_full_name(model: DummyModel, default: Any) -> str:
        if user_info := model.user_info:
            if user_info.first_name and user_info.last_name:
                return user_info.first_name + " " + user_info.last_name
        return default
