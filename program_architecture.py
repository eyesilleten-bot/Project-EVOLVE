from __future__ import annotations

from dataclasses import dataclass, field

from ast_program import ASTProgram


@dataclass
class ProgramFunction:

    function_id: str
    program: ASTProgram

    created_generation: int = 0
    origin: str = "UNKNOWN"

    # =====================================================
    # CLONE
    # =====================================================

    def clone(
        self,
    ) -> "ProgramFunction":

        return ProgramFunction(
            function_id=self.function_id,

            program=ASTProgram.from_dict(
                self.program.to_dict()
            ),

            created_generation=(
                self.created_generation
            ),

            origin=self.origin,
        )

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(
        self,
    ) -> dict:

        return {
            "function_id":
                self.function_id,

            "program":
                self.program.to_dict(),

            "created_generation":
                self.created_generation,

            "origin":
                self.origin,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ProgramFunction":

        return cls(
            function_id=str(
                data["function_id"]
            ),

            program=ASTProgram.from_dict(
                data["program"]
            ),

            created_generation=int(
                data.get(
                    "created_generation",
                    0,
                )
            ),

            origin=str(
                data.get(
                    "origin",
                    "UNKNOWN",
                )
            ),
        )

    # =====================================================
    # REPORT
    # =====================================================

    def describe(
        self,
    ) -> str:

        return (
            f"{self.function_id}: "
            f"{self.program.describe()}"
        )


@dataclass
class ProgramArchitecture:

    main: ASTProgram

    functions: dict[
        str,
        ProgramFunction,
    ] = field(
        default_factory=dict
    )

    next_function_id: int = 1

    birth_generation: int = 0
    origin: str = "UNKNOWN"

    # =====================================================
    # FUNCTION IDS
    # =====================================================

    def allocate_function_id(
        self,
    ) -> str:

        function_id = (
            f"F{self.next_function_id:03d}"
        )

        self.next_function_id += 1

        return function_id

    # =====================================================
    # ADD FUNCTION
    # =====================================================

    def add_function(
        self,
        program: ASTProgram,
        generation: int,
        origin: str = "CREATED",
    ) -> str:

        function_id = (
            self.allocate_function_id()
        )

        self.functions[
            function_id
        ] = ProgramFunction(
            function_id=function_id,
            program=program,
            created_generation=generation,
            origin=origin,
        )

        return function_id

    # =====================================================
    # REMOVE FUNCTION
    # =====================================================

    def remove_function(
        self,
        function_id: str,
    ) -> bool:

        if (
            function_id
            not in self.functions
        ):

            return False

        del self.functions[
            function_id
        ]

        return True

    # =====================================================
    # GET
    # =====================================================

    def get_function(
        self,
        function_id: str,
    ) -> ProgramFunction | None:

        return self.functions.get(
            function_id
        )

    # =====================================================
    # METRICS
    # =====================================================

    def function_count(
        self,
    ) -> int:

        return len(
            self.functions
        )

    def total_node_count(
        self,
    ) -> int:

        total = (
            self.main.node_count()
        )

        for function in (
            self.functions.values()
        ):

            total += (
                function.program
                .node_count()
            )

        return total

    def maximum_depth(
        self,
    ) -> int:

        depths = [
            self.main.depth()
        ]

        depths.extend(
            function.program.depth()
            for function
            in self.functions.values()
        )

        return max(depths)

    # =====================================================
    # CLONE
    # =====================================================

    def clone(
        self,
    ) -> "ProgramArchitecture":

        return (
            ProgramArchitecture.from_dict(
                self.to_dict()
            )
        )

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(
        self,
    ) -> dict:

        return {
            "main":
                self.main.to_dict(),

            "functions": {
                function_id:
                    function.to_dict()

                for function_id, function
                in self.functions.items()
            },

            "next_function_id":
                self.next_function_id,

            "birth_generation":
                self.birth_generation,

            "origin":
                self.origin,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "ProgramArchitecture":

        architecture = cls(
            main=ASTProgram.from_dict(
                data["main"]
            ),

            next_function_id=int(
                data.get(
                    "next_function_id",
                    1,
                )
            ),

            birth_generation=int(
                data.get(
                    "birth_generation",
                    0,
                )
            ),

            origin=str(
                data.get(
                    "origin",
                    "UNKNOWN",
                )
            ),
        )

        architecture.functions = {
            str(function_id):
                ProgramFunction.from_dict(
                    function_data
                )

            for function_id, function_data
            in data.get(
                "functions",
                {},
            ).items()
        }

        return architecture

    # =====================================================
    # DESCRIPTION
    # =====================================================

    def describe(
        self,
    ) -> str:

        parts = [
            (
                "MAIN: "
                f"{self.main.describe()}"
            )
        ]

        for function_id in sorted(
            self.functions
        ):

            parts.append(
                self.functions[
                    function_id
                ].describe()
            )

        return "\n".join(parts)