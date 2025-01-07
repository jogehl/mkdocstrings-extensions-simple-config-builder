"""Module for the griffe extension."""

import ast
import inspect
from typing import Any

import griffe
from _griffe.agents.inspector import Inspector
from _griffe.agents.nodes.runtime import ObjectNode
from _griffe.agents.visitor import Visitor
from _griffe.models import Class, Object
from griffe import Extension, dynamic_import

# get griffe logger
logger = griffe.get_logger(__name__)


def parse_config_field(node: ast.Call) -> dict:
    """
    Parse the config_field call and returns the field name and the values.

    Args:
        node: the node to parse

    Returns
    -------
        dict: the field name and values
    """
    config_fields = {}
    for keyword in node.keywords:
        value = keyword.value
        if isinstance(value, ast.Constant):
            config_fields[keyword.arg] = value.value
        elif isinstance(value, ast.List):
            config_fields[keyword.arg] = [elt.id for elt in value.elts]
    return config_fields


class SimpleConfigBuilderExtension(Extension):
    """Extension for the griffe library."""

    def __init__(self):
        """Initialize the extension."""
        super().__init__()

    def on_instance(
        self,
        *,
        node: ast.AST | ObjectNode,
        obj: Object,
        agent: Visitor | Inspector,
        **kwargs: Any,
    ) -> None:
        """Is executed on each node in the syntax tree."""
        if isinstance(node, ObjectNode):
            return

        if isinstance(obj, Class):
            # check for decorator configclass
            if hasattr(node, "decorator_list"):
                for decorator in node.decorator_list:
                    if (
                        hasattr(decorator, "id")
                        and decorator.id == "configclass"
                    ):
                        try:
                            runtime_obj = dynamic_import(obj.path)
                        except ImportError:
                            logger.error(f"Could not import {obj.path}")
                            return

                        # get the docstring
                        docstring = inspect.cleandoc(
                            getattr(runtime_obj, "__doc__", "") or ""
                        )
                        if not obj.docstring:
                            obj.docstring = griffe.Docstring(
                                value=docstring, parent=obj
                            )

                        logger.info(obj.docstring.value)
                        logger.info("Found configclass decorator")
                        # change docstring so that it shows configclass
                        docstring_value = f"@ConfigClass\n\n {
                            obj.docstring.value if obj.docstring else ''}"

                        # iterate over all the fields and
                        # add them to the docstring
                        fields = []
                        for stmt in node.body:
                            if not isinstance(
                                stmt, (ast.Assign, ast.AnnAssign)
                            ):
                                continue
                            # check if the statement is an assignment
                            data_dct = {}
                            if isinstance(stmt, ast.Assign):
                                data_dct["name"] = stmt.targets[0].id
                                if isinstance(stmt.value, ast.Call):
                                    if stmt.value.func.id == "config_field":
                                        config_fields = parse_config_field(
                                            stmt.value
                                        )
                                        data_dct["attrs"] = config_fields
                                else:
                                    data_dct["attrs"] = {
                                        "default": stmt.value.value
                                    }

                            if isinstance(stmt, ast.AnnAssign):
                                data_dct["name"] = stmt.target.id
                                if isinstance(stmt.value, ast.Call):
                                    if stmt.value.func.id == "config_field":
                                        config_fields = parse_config_field(
                                            stmt.value
                                        )
                                        data_dct["attrs"] = config_fields
                                else:
                                    data_dct["attrs"] = {
                                        "default": stmt.value.value
                                    }
                                annotation = stmt.annotation
                                data_dct["type"] = annotation.id
                            fields.append(data_dct)

                        docstring_value += "\n\nParams:\n"
                        for field in fields:
                            docstring_value += f"\n    {field['name']}: {
                                                field['type'] 
                                                if 'type' in 
                                                   field else 'Any'}"
                            if "attrs" in field:
                                docstring_value += "\n    Constraints:"
                            for key, value in field["attrs"].items():
                                docstring_value += f"\n        {key}: {value}"
                            docstring_value += "\n"

                        obj.docstring = griffe.Docstring(
                            value=docstring_value,
                        )
