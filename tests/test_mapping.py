from copy import deepcopy
from datetime import date

import pytest

from pymapme.exceptions import PyMapMelValidationError
from tests.conftest import DummyMappingModel, DummyModel, Skill


def test_from_model(mapped_model):
    assert mapped_model.model_dump() == DummyMappingModel(
        name="John",
        surname="Smith",
        non_existing=None,
        nickname="baobab",
        previous_companies=["Google", "Amazon"],
        current_work_started_since="10-10-2022",
        is_working="False",
        age=None,
        full_name="John Smith",
        skills=[Skill(name="Python"), Skill(name="Js")],
    ).model_dump()


def test_from_model_default(test_data):
    data = deepcopy(test_data)
    data["user_info"].pop("first_name")
    mapped_model = DummyMappingModel.build_from_model(DummyModel(**data))

    assert mapped_model == DummyMappingModel(
        surname="Smith",
        nickname="baobab",
        is_working="False",
        documents=[],
        previous_companies=["Google", "Amazon"],
        field_with_default_value="default_value",
        current_work_started_since="10-10-2022",
        non_existing=None,
        age=None,
        full_name="NoFullName",
        skills=[Skill(name="Python"), Skill(name="Js")],
    )


def test_from_model_with_context(mapped_model_with_context):
    dummy_model = DummyMappingModel(
        name="John",
        surname="Smith",
        non_existing=None,
        nickname="baobab",
        previous_companies=["Google", "Amazon"],
        current_work_started_since="10-10-2022",
        is_working="False",
        age=27,
        full_name="John Smith",
        skills=[Skill(name="Python"), Skill(name="Js")],
        documents=[],
    )
    assert mapped_model_with_context.model_dump() == dummy_model.model_dump()


def test_from_model_failed_to_map_validation_error(actual_model):
    actual_model.user_info = "John Smith"
    with pytest.raises(
        PyMapMelValidationError, match="'str' object has no attribute 'first_name'"
    ):
        DummyMappingModel.build_from_model(actual_model)


def test_from_model_model_validation_error(actual_model):
    actual_model.work_profile.current_job.since = date(day=10, month=10, year=2022)
    with pytest.raises(PyMapMelValidationError) as excinfo:
        DummyMappingModel.build_from_model(actual_model)
    assert "current_work_started_since" in str(excinfo)


def test_dump(mapped_model):
    assert (
        mapped_model.model_dump_json()
        == '{"name":"John","surname":"Smith","nickname":"baobab","is_working":false,"documents":[],"previous_companies":["Google","Amazon"],"field_with_default_value":"default_value","current_work_started_since":"10-10-2022","non_existing":null,"age":null,"full_name":"John Smith","skills":[{"name":"Python"},{"name":"Js"}]}'
    )
