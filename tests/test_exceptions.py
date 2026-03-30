import pytest
from pydantic_ai_web_models.exceptions import (
    JSONParseError,
    TemporalConnectionError,
    WebModelError,
    WorkflowExecutionError,
)


def test_web_model_error_is_exception():
    with pytest.raises(WebModelError):
        raise WebModelError("base error")


def test_temporal_connection_error_inherits_web_model_error():
    err = TemporalConnectionError("connect failed")
    assert isinstance(err, WebModelError)
    assert str(err) == "connect failed"


def test_workflow_execution_error_stores_workflow_id():
    err = WorkflowExecutionError("execution failed", workflow_id="wf-abc-123")
    assert err.workflow_id == "wf-abc-123"
    assert str(err) == "execution failed"
    assert isinstance(err, WebModelError)


def test_workflow_execution_error_default_workflow_id_is_none():
    err = WorkflowExecutionError("execution failed")
    assert err.workflow_id is None


def test_json_parse_error_stores_raw_text():
    err = JSONParseError("could not parse JSON", raw_text="not valid json {{")
    assert err.raw_text == "not valid json {{"
    assert str(err) == "could not parse JSON"
    assert isinstance(err, WebModelError)


def test_exception_hierarchy():
    assert issubclass(TemporalConnectionError, WebModelError)
    assert issubclass(WorkflowExecutionError, WebModelError)
    assert issubclass(JSONParseError, WebModelError)
    assert issubclass(WebModelError, Exception)
