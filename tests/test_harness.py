"""tests/test_harness.py — Testes do Harness de tarefas."""

import pytest
from src.harness.tasks import Harness, NBSTaskCatalog, Task, TaskStatus


def _dummy_task(value: str = "ok", **_) -> str:
    return f"resultado: {value}"


def _failing_task(**_):
    raise RuntimeError("Falha simulada")


@pytest.fixture
def catalog():
    c = NBSTaskCatalog()
    c.register(Task(name="ok_task", description="Tarefa que funciona", fn=_dummy_task,
                    params={"value": "teste"}))
    c.register(Task(name="fail_task", description="Tarefa que falha", fn=_failing_task,
                    retry=2))
    return c


@pytest.fixture
def harness(catalog):
    return Harness(catalog, context={})


def test_run_success(harness):
    result = harness.run("ok_task")
    assert result.status == TaskStatus.SUCCESS
    assert "resultado" in result.output


def test_run_unknown_task(harness):
    result = harness.run("tarefa_inexistente")
    assert result.status == TaskStatus.FAILED
    assert "não encontrada" in result.error


def test_run_failing_task(harness):
    result = harness.run("fail_task")
    assert result.status == TaskStatus.FAILED
    assert result.error is not None


def test_run_sequence_stops_on_failure(harness):
    results = harness.run_sequence(["ok_task", "fail_task", "ok_task"])
    assert len(results) == 2  # para na falha
    assert results[0].status == TaskStatus.SUCCESS
    assert results[1].status == TaskStatus.FAILED


def test_catalog_list(catalog):
    tasks = catalog.list_tasks()
    assert "ok_task" in tasks
    assert "fail_task" in tasks


def test_catalog_summary(catalog):
    summary = catalog.summary()
    assert "ok_task" in summary
    assert "Tarefa que funciona" in summary
