from __future__ import annotations

import ast
import textwrap

from flake8_init_return import MSG
from flake8_init_return import Plugin


def _results(s: str) -> set[str]:
    tree = ast.parse(s)
    plugin = Plugin(tree)
    return {f'{line}:{col} {msg}' for line, col, msg, _ in plugin.run()}


def test_incorrect_init_return():
    ret = _results(
        textwrap.dedent("""\
        class A:
            def __init__(name: str):
                self.name = name
        """),
    )
    assert ret == {f'2:4 {MSG}'}


def test_incorrect_init_return_nested():
    ret = _results(
        textwrap.dedent("""\
        class A:
            class B:
                def __init__(name: str):
                    pass
        """),
    )
    assert ret == {f'3:8 {MSG}'}


def test_incorrect_init_return_complicated():
    ret = _results(
        textwrap.dedent("""\
        class A:
            class B:
                class C:
                    ...
                class D:
                    def __init__(name: str):
                        pass
        def __init__():
            ...
        """),
    )
    assert ret == {f'6:12 {MSG}'}


def test_correct_init_return():
    ret = _results(
        textwrap.dedent("""\
        class A:
            def __init__() -> None:
                pass
        """),
    )
    assert ret == set()


def test_contextual_init_return():
    """Make sure that only __init__s in a class are considered."""
    ret = _results(
        textwrap.dedent("""\
        class A:
            def __init__(name: str) -> None:
                self.name = name

        def __init__():
            return 1
        """),
    )
    assert ret == set()
