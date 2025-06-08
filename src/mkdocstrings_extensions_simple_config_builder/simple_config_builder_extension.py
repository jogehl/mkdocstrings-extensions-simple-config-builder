"""Griffe extension to enhance documentation of config classes."""

from __future__ import annotations

import ast
import inspect
from typing import Any

import griffe
from _griffe.agents.inspector import Inspector
from _griffe.agents.nodes.runtime import ObjectNode
from _griffe.agents.visitor import Visitor
from _griffe.models import Class, Object
from griffe import Extension, dynamic_import

logger = griffe.get_logger(__name__)


def parse_config_field(node: ast.Call) -> dict:
    """Return keyword arguments of a ``config_field`` call."""
    attrs: dict[str, Any] = {}
    for kw in node.keywords:
        value = kw.value
        if isinstance(value, ast.Constant):
            attrs[kw.arg] = value.value
        elif isinstance(value, ast.List):
            attrs[kw.arg] = [elt.id for elt in value.elts]
    return attrs


class SimpleConfigBuilderExtension(Extension):
    """Extension for the griffe library."""

    def on_instance(
        self,
        *,
        node: ast.AST | ObjectNode,
        obj: Object,
        agent: Visitor | Inspector,
        **kwargs: Any,
    ) -> None:
        """Modify classes decorated with ``@configclass``."""
        if isinstance(node, ObjectNode):
            return
        if not isinstance(obj, Class):
            return
        for decorator in getattr(node, "decorator_list", []):
            if getattr(decorator, "id", None) == "configclass":
                try:
                    runtime_obj = dynamic_import(obj.path)
                except ImportError:
                    logger.error("Could not import %s", obj.path)
                    return
                docstring = inspect.cleandoc(
                    getattr(runtime_obj, "__doc__", "")
                )
                if not obj.docstring:
                    obj.docstring = griffe.Docstring(
                        value=docstring,
                        parent=obj,
                    )
                docstring_value = f"@ConfigClass\n\n{obj.docstring.value}"
                fields: list[dict[str, Any]] = []
                for stmt in node.body:
                    if not isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                        continue
                    data: dict[str, Any] = {}
                    if isinstance(stmt, ast.Assign):
                        data["name"] = stmt.targets[0].id
                        if (
                            isinstance(stmt.value, ast.Call)
                            and getattr(
                                stmt.value.func,
                                "id",
                                "",
                            )
                            == "config_field"
                        ):
                            data["attrs"] = parse_config_field(stmt.value)
                        else:
                            data["attrs"] = {"default": stmt.value.value}
                    if isinstance(stmt, ast.AnnAssign):
                        data["name"] = stmt.target.id
                        if (
                            isinstance(stmt.value, ast.Call)
                            and getattr(
                                stmt.value.func,
                                "id",
                                "",
                            )
                            == "config_field"
                        ):
                            data["attrs"] = parse_config_field(stmt.value)
                        else:
                            data["attrs"] = {
                                "default": getattr(
                                    stmt.value,
                                    "value",
                                    stmt.value,
                                )
                            }
                        data["type"] = getattr(stmt.annotation, "id", "Any")
                    fields.append(data)
                docstring_value += "\n\nParams:\n"
                for field in fields:
                    docstring_value += (
                        f"\n    {field['name']}: {field.get('type', 'Any')}"
                    )
                    if "attrs" in field:
                        docstring_value += "\n    Constraints:"
                        for key, value in field["attrs"].items():
                            docstring_value += f"\n        {key}: {value}"
                    docstring_value += "\n"
                obj.docstring = griffe.Docstring(value=docstring_value)
