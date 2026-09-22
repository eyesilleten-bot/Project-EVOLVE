# ast_program.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------
# ALLOWED AST NODE TYPES
# ---------------------------------------------------------

AST_NODE_TYPES = (
    "SEQUENCE",
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "ABS",
    "IF_CONTEXT",
    "CALL_MODULE",
    "CALL_MACRO",
    "CALL_LEGACY_MAIN",
    "CALL_FUNCTION",
    "CALL_OPCODE",
)


# ---------------------------------------------------------
# AST NODE
# ---------------------------------------------------------

@dataclass
class ASTNode:

    node_type: str

    value: float = 0.0
    context: int = 0

    module_id: int | None = None
    macro_id: int | None = None
    function_id: str | None = None
    opcode_id: str | None = None

    children: list["ASTNode"] = field(
        default_factory=list
    )

    def __post_init__(
        self,
    ) -> None:

        if self.node_type not in AST_NODE_TYPES:

            raise ValueError(
                f"Unsupported AST node type: "
                f"{self.node_type}"
            )

    # -----------------------------------------------------
    # CLONE
    # -----------------------------------------------------

    def clone(
        self,
    ) -> "ASTNode":

        return ASTNode(
            node_type=self.node_type,
            value=self.value,
            context=self.context,
            module_id=self.module_id,
            macro_id=self.macro_id,
            function_id=self.function_id,
            opcode_id=self.opcode_id,
            children=[
                child.clone()
                for child in self.children
            ],
        )

    # -----------------------------------------------------
    # SIZE
    # -----------------------------------------------------

    def node_count(
        self,
    ) -> int:

        return (
            1
            + sum(
                child.node_count()
                for child in self.children
            )
        )

    # -----------------------------------------------------
    # DEPTH
    # -----------------------------------------------------

    def depth(
        self,
    ) -> int:

        if not self.children:
            return 1

        return (
            1
            + max(
                child.depth()
                for child in self.children
            )
        )

    # -----------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "node_type":
                self.node_type,

            "value":
                self.value,

            "context":
                self.context,

            "module_id":
                self.module_id,

            "macro_id":
                self.macro_id,

            "function_id":
                self.function_id,

            "opcode_id": self.opcode_id,

            "children": [
                child.to_dict()
                for child in self.children
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ASTNode":

        return cls(
            node_type=data["node_type"],

            value=float(
                data.get(
                    "value",
                    0.0,
                )
            ),

            context=int(
                data.get(
                    "context",
                    0,
                )
            ),

            module_id=(
                data.get(
                    "module_id"
                )
            ),

            macro_id=(
                data.get(
                    "macro_id"
                )
            ),

            function_id=(
                data.get(
                    "function_id"
                )
            ),

            opcode_id=data.get(
                "opcode_id"
            ),

            children=[
                cls.from_dict(child)
                for child in data.get(
                    "children",
                    [],
                )
            ],
        )

    # -----------------------------------------------------
    # DESCRIPTION
    # -----------------------------------------------------

    def describe(
        self,
    ) -> str:

        if self.node_type == "SEQUENCE":

            return (
                "SEQ("
                + ", ".join(
                    child.describe()
                    for child in self.children
                )
                + ")"
            )

        if self.node_type == "ADD":
            return f"ADD({self.value:.4f})"

        if self.node_type == "SUBTRACT":
            return (
                f"SUBTRACT({self.value:.4f})"
            )

        if self.node_type == "MULTIPLY":
            return (
                f"MULTIPLY({self.value:.4f})"
            )

        if self.node_type == "ABS":
            return "ABS"

        if self.node_type == "IF_CONTEXT":

            body = (
                self.children[0].describe()
                if self.children
                else "<EMPTY>"
            )

            return (
                f"IF_CONTEXT({self.context}, "
                f"{body})"
            )

        if self.node_type == "CALL_MODULE":

            return (
                f"CALL_MODULE("
                f"M{self.module_id:03d})"
            )

        if self.node_type == "CALL_MACRO":

            return (
                f"CALL_MACRO("
                f"K{self.macro_id:03d})"
            )

        if self.node_type == "CALL_FUNCTION":

            return (
                "CALL_FUNCTION("
                f"{self.function_id})"
            )

        if (
            self.node_type
            == "CALL_OPCODE"
        ):

            return (
                "CALL_OPCODE("
                f"{self.opcode_id}"
                ")"
            )

        if self.node_type == "CALL_LEGACY_MAIN":
            return "CALL_LEGACY_MAIN"

        return self.node_type


# ---------------------------------------------------------
# AST PROGRAM
# ---------------------------------------------------------

@dataclass
class ASTProgram:

    root: ASTNode

    origin: str = "MANUAL"
    birth_generation: int = 0

    def clone(
        self,
    ) -> "ASTProgram":

        return ASTProgram(
            root=self.root.clone(),
            origin=self.origin,
            birth_generation=(
                self.birth_generation
            ),
        )

    def node_count(
        self,
    ) -> int:

        return self.root.node_count()

    def depth(
        self,
    ) -> int:

        return self.root.depth()

    def describe(
        self,
    ) -> str:

        return self.root.describe()

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return {
            "origin":
                self.origin,

            "birth_generation":
                self.birth_generation,

            "root":
                self.root.to_dict(),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ASTProgram":

        return cls(
            root=ASTNode.from_dict(
                data["root"]
            ),

            origin=data.get(
                "origin",
                "UNKNOWN",
            ),

            birth_generation=int(
                data.get(
                    "birth_generation",
                    0,
                )
            ),
        )