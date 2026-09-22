# genome.py

from __future__ import annotations

import math

from dataclasses import dataclass
import random

from ast_program import (
    ASTNode,
    ASTProgram,
)

from program_architecture import (
    ProgramArchitecture,
)

from evolved_language import EvolvedLanguage

from config import (
    ARCH_BODY_MUTATION_WEIGHT,
    ARCH_CREATE_FUNCTION_WEIGHT,
    ARCH_CREATION_RATE,
    ARCH_DELETE_FUNCTION_WEIGHT,
    ARCH_DUPLICATE_FUNCTION_WEIGHT,
    ARCH_INSERT_CALL_WEIGHT,
    ARCH_PARAMETER_MUTATION_SCALE,
    ARCH_RETARGET_CALL_WEIGHT,
    AST_BRIDGE_CREATION_CHANCE,
    AST_CREATION_RATE,
    AST_EXECUTION_BUDGET,
    AST_NODE_REPLACEMENT_RATE,
    AST_PARAMETER_MUTATION_RATE,
    AST_PARAMETER_MUTATION_SCALE,
    AST_SUBTREE_DELETE_RATE,
    AST_SUBTREE_DUPLICATION_RATE,
    AST_SUBTREE_INSERT_RATE,
    AST_STRUCTURE_MUTATION_SHARE,
    COMPOSITE_MODULE_RATE,
    COMPOSITE_REPLACEMENT_CHANCE,
    DERIVED_OPCODE_GENTLE_PROBABILITY,
    DERIVED_OPCODE_PARAMETER_MUTATION_SCALE,
    LANGUAGE_MUTATION_SHARE,
    MACRO_CREATION_RATE,
    MACRO_INSTRUCTION_RATE,
    MACRO_REPLACEMENT_CHANCE,
    MAX_ARCH_FUNCTIONS,
    MAX_AST_DEPTH,
    MAX_AST_NODES,
    MAX_EVOLVED_OPCODES,
    MAX_GENOME_LENGTH,
    MAX_MACROS,
    MAX_MACRO_LENGTH,
    MAX_MODULE_CALL_DEPTH,
    MAX_MODULE_LENGTH,
    MAX_MODULES,
    MIN_GENOME_LENGTH,
    MODULE_CALL_MUTATION_RATE,
    MUTATION_RATE,
    OPCODE_CREATE_WEIGHT,
    OPCODE_DELETE_WEIGHT,
    OPCODE_DERIVE_WEIGHT,
    OPCODE_INSERT_CALL_WEIGHT,
    OPCODE_LOCAL_INSERT_CALL_WEIGHT,
    OPCODE_MUTATE_WEIGHT,
    OPCODE_PARAMETER_MUTATION_SCALE,
    OPCODE_RETARGET_CALL_WEIGHT,
    PARAMETER_MUTATION_SCALE,
)


PRIMITIVE_OPERATIONS = (
    "ADD",
    "SUBTRACT",
    "MULTIPLY",
    "JUMP_IF_CONTEXT_NE",
    "JUMP",
)


@dataclass
class Instruction:
    operation: str

    value: float = 0.0
    context: int = 0
    offset: int = 1
    module_id: int | None = None
    macro_id: int | None = None

    def copy(self) -> "Instruction":
        return Instruction(
            operation=self.operation,
            value=self.value,
            context=self.context,
            offset=self.offset,
            module_id=self.module_id,
            macro_id=self.macro_id,
        )

    def describe(self) -> str:

        if self.operation == "JUMP_IF_CONTEXT_NE":
            return (
                f"JUMP_IF_CONTEXT_NE "
                f"context={self.context} "
                f"offset={self.offset}"
            )

        if self.operation == "JUMP":
            return (
                f"JUMP offset={self.offset}"
            )

        if self.operation == "CALL_MODULE":
            return (
                f"CALL_MODULE M{self.module_id:03d}"
            )

        if self.operation == "CALL_MACRO":
            return (
                f"CALL_MACRO K{self.macro_id:03d}"
            )

        return (
            f"{self.operation} "
            f"{self.value:.4f}"
        )


class Genome:

    _next_module_uid = 1
    _next_macro_uid = 1

    @classmethod
    def _new_module_uid(
        cls,
    ) -> str:

        uid = (
            f"MOD-"
            f"{cls._next_module_uid:06d}"
        )

        cls._next_module_uid += 1

        return uid

    @classmethod
    def _new_macro_uid(
        cls,
    ) -> str:

        uid = (
            f"MAC-"
            f"{cls._next_macro_uid:06d}"
        )

        cls._next_macro_uid += 1

        return uid

    def __init__(
        self,
        instructions: list[Instruction] | None = None,
        modules: dict[
            int,
            list[Instruction]
        ] | None = None,
        module_meta: dict[
            int,
            dict
        ] | None = None,
        macros: dict[
            int,
            list[Instruction]
        ] | None = None,
        macro_meta: dict[
            int,
            dict
        ] | None = None,

        ast_program: ASTProgram | None = None,

        program_architecture:
            ProgramArchitecture | None = None,

        evolved_language:
            EvolvedLanguage | None = None,

        execution_mode: str = "DSL",
    ):

        self.instructions = (
            instructions or []
        )

        self.modules = (
            modules or {}
        )

        self.module_meta = (
            module_meta or {}
        )

        self.next_module_id = (
            max(
                self.modules.keys(),
                default=0,
            )
            + 1
        )

        self.macros = (
            macros or {}
        )

        self.macro_meta = (
            macro_meta or {}
        )

        self.next_macro_id = (
            max(
                self.macros.keys(),
                default=0,
            )
            + 1
        )

        self.ast_program = ast_program

        self.program_architecture = (
            program_architecture
        )

        self.evolved_language = (
            evolved_language
        )

        if execution_mode not in (
            "DSL",
            "AST",
            "ARCH",
        ):
            raise ValueError(
                f"Invalid execution mode: "
                f"{execution_mode}"
            )

        self.execution_mode = (
            execution_mode
        )

    @classmethod
    def create_generation_zero(
        cls,
    ) -> "Genome":

        operation = random.choice(
            (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            )
        )

        return cls(
            instructions=[
                Instruction(
                    operation=operation,
                    value=random.uniform(
                        -1.0,
                        1.0,
                    ),
                )
            ],
            modules={},
        )

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    def execute(
        self,
        input_value: float,
        context_id: int,
    ) -> float:

        # =================================================
        # ARCHITECTURE
        # =================================================

        if self.execution_mode == "ARCH":

            if self.program_architecture is None:

                raise RuntimeError(
                    "ARCH execution mode selected "
                    "without program architecture."
                )

            return (
                self.execute_program_architecture(
                    input_value=input_value,
                    context_id=context_id,
                )
            )

        # =================================================
        # AST
        # =================================================

        if self.execution_mode == "AST":

            if self.ast_program is None:

                raise RuntimeError(
                    "AST execution mode selected "
                    "without AST program."
                )

            return self.execute_ast(
                input_value=input_value,
                context_id=context_id,
            )

        # =================================================
        # DSL
        # =================================================

        step_counter = [0]

        max_steps = max(
            40,
            self.total_instruction_count()
            * 6,
        )

        return self._execute_sequence(
            sequence=self.instructions,
            value=float(input_value),
            context_id=context_id,
            step_counter=step_counter,
            max_steps=max_steps,
            call_depth=0,
        )

    def _execute_sequence(
        self,
        sequence: list[Instruction],
        value: float,
        context_id: int,
        step_counter: list[int],
        max_steps: int,
        call_depth: int,
    ) -> float:

        if (
            call_depth
            > MAX_MODULE_CALL_DEPTH
        ):
            raise RuntimeError(
                "Maximum module call depth exceeded."
            )

        pc = 0

        while (
            0 <= pc < len(sequence)
        ):

            step_counter[0] += 1

            if step_counter[0] > max_steps:
                raise RuntimeError(
                    "Instruction budget exceeded."
                )

            instruction = sequence[pc]

            operation = instruction.operation

            if operation == "ADD":
                value += instruction.value
                pc += 1

            elif operation == "SUBTRACT":
                value -= instruction.value
                pc += 1

            elif operation == "MULTIPLY":
                value *= instruction.value
                pc += 1

            elif operation == "JUMP_IF_CONTEXT_NE":

                if (
                    context_id
                    != instruction.context
                ):
                    pc += max(
                        1,
                        instruction.offset,
                    )
                else:
                    pc += 1

            elif operation == "JUMP":

                pc += max(
                    1,
                    instruction.offset,
                )

            elif operation == "CALL_MODULE":

                module_id = (
                    instruction.module_id
                )

                if (
                    module_id is None
                    or module_id
                    not in self.modules
                ):
                    raise RuntimeError(
                        "Invalid module call."
                    )

                value = self._execute_sequence(
                    sequence=self.modules[
                        module_id
                    ],
                    value=value,
                    context_id=context_id,
                    step_counter=step_counter,
                    max_steps=max_steps,
                    call_depth=(
                        call_depth + 1
                    ),
                )

                pc += 1

            elif operation == "CALL_MACRO":

                macro_id = (
                    instruction.macro_id
                )

                if (
                    macro_id is None
                    or macro_id
                    not in self.macros
                ):
                    raise RuntimeError(
                        "Invalid macro call."
                    )

                value = self._execute_sequence(
                    sequence=self.macros[
                        macro_id
                    ],
                    value=value,
                    context_id=context_id,
                    step_counter=step_counter,
                    max_steps=max_steps,
                    call_depth=(
                        call_depth + 1
                    ),
                )

                pc += 1

            else:
                raise ValueError(
                    f"Bilinmeyen instruction: "
                    f"{operation}"
                )

        return value

    # ---------------------------------------------------------
    # V0.7 AST EXECUTION
    # ---------------------------------------------------------

    def execute_ast(
        self,
        input_value: float,
        context_id: int,
    ) -> float:

        if self.ast_program is None:

            raise RuntimeError(
                "Genome has no AST program."
            )

        if (
            self.ast_program.node_count()
            > MAX_AST_NODES
        ):

            raise RuntimeError(
                "AST node limit exceeded."
            )

        if (
            self.ast_program.depth()
            > MAX_AST_DEPTH
        ):

            raise RuntimeError(
                "AST depth limit exceeded."
            )

        ast_budget = [0]

        # -------------------------------------------------
        # SHARED EMBEDDED DSL BUDGET
        #
        # AST içindeki bütün legacy/module/macro çağrıları
        # aynı instruction counter'ı paylaşır.
        # -------------------------------------------------

        dsl_step_counter = [0]

        dsl_max_steps = max(
            40,
            self.total_instruction_count()
            * 6,
        )

        return self._execute_ast_node(
            node=self.ast_program.root,
            value=float(input_value),
            context_id=context_id,
            budget=ast_budget,
            dsl_step_counter=dsl_step_counter,
            dsl_max_steps=dsl_max_steps,
            call_depth=0,
        )

    def _execute_ast_node(
        self,
        node: ASTNode,
        value: float,
        context_id: int,
        budget: list[int],
        dsl_step_counter: list[int],
        dsl_max_steps: int,
        call_depth: int,
    ) -> float:

        budget[0] += 1

        if (
            budget[0]
            > AST_EXECUTION_BUDGET
        ):

            raise RuntimeError(
                "AST execution budget exceeded."
            )

        if (
            call_depth
            > MAX_MODULE_CALL_DEPTH
        ):

            raise RuntimeError(
                "Maximum AST call depth exceeded."
            )

        node_type = node.node_type

        # -----------------------------------------------------
        # SEQUENCE
        # -----------------------------------------------------

        if node_type == "SEQUENCE":

            for child in node.children:

                value = self._execute_ast_node(
                    node=child,
                    value=value,
                    context_id=context_id,
                    budget=budget,
                    dsl_step_counter=dsl_step_counter,
                    dsl_max_steps=dsl_max_steps,
                    call_depth=call_depth,
                )

            return value

        # -----------------------------------------------------
        # PRIMITIVES
        # -----------------------------------------------------

        if node_type == "ADD":
            return value + node.value

        if node_type == "SUBTRACT":
            return value - node.value

        if node_type == "MULTIPLY":
            return value * node.value

        if node_type == "ABS":
            return abs(value)

        # -----------------------------------------------------
        # STRUCTURED CONTROL FLOW
        # -----------------------------------------------------

        if node_type == "IF_CONTEXT":

            if context_id == node.context:

                if node.children:

                    return self._execute_ast_node(
                        node=node.children[0],
                        value=value,
                        context_id=context_id,
                        budget=budget,
                        dsl_step_counter=dsl_step_counter,
                        dsl_max_steps=dsl_max_steps,
                        call_depth=call_depth,
                    )

            return value

        # -----------------------------------------------------
        # LEGACY MAIN CALL
        # -----------------------------------------------------

        if node_type == "CALL_LEGACY_MAIN":

            return self._execute_sequence(
                sequence=self.instructions,
                value=value,
                context_id=context_id,
                step_counter=dsl_step_counter,
                max_steps=dsl_max_steps,
                call_depth=call_depth + 1,
            )

        # -----------------------------------------------------
        # EXISTING MODULE CALL
        # -----------------------------------------------------

        if node_type == "CALL_MODULE":

            module_id = node.module_id

            if (
                module_id is None
                or module_id
                not in self.modules
            ):

                raise RuntimeError(
                    "Invalid AST module call."
                )

            return self._execute_sequence(
                sequence=self.modules[
                    module_id
                ],
                value=value,
                context_id=context_id,
                step_counter=dsl_step_counter,
                max_steps=dsl_max_steps,
                call_depth=(
                    call_depth + 1
                ),
            )

        # -----------------------------------------------------
        # EXISTING EVOLVED VOCABULARY CALL
        # -----------------------------------------------------

        if node_type == "CALL_MACRO":

            macro_id = node.macro_id

            if (
                macro_id is None
                or macro_id
                not in self.macros
            ):

                raise RuntimeError(
                    "Invalid AST macro call."
                )

            return self._execute_sequence(
                sequence=self.macros[
                    macro_id
                ],
                value=value,
                context_id=context_id,
                step_counter=dsl_step_counter,
                max_steps=dsl_max_steps,
                call_depth=(
                    call_depth + 1
                ),
            )

        raise RuntimeError(
            f"Unknown AST node: {node_type}"
        )

    def execute_program_architecture(
        self,
        input_value: float,
        context_id: int,
    ) -> float:

        architecture = (
            self.program_architecture
        )

        if architecture is None:

            raise RuntimeError(
                "Genome has no program architecture."
            )

        # ---------------------------------------------
        # Her AST function mevcut AST güvenlik
        # limitlerine ayrı ayrı uymalı.
        # ---------------------------------------------

        programs = [
            architecture.main
        ]

        programs.extend(
            function.program
            for function
            in architecture.functions.values()
        )

        for program in programs:

            if (
                program.node_count()
                > MAX_AST_NODES
            ):

                raise RuntimeError(
                    "AST node limit exceeded."
                )

            if (
                program.depth()
                > MAX_AST_DEPTH
            ):

                raise RuntimeError(
                    "AST depth limit exceeded."
                )

        language = (
            self.evolved_language
        )

        if language is not None:

            for opcode in (
                language.opcodes.values()
            ):

                program = (
                    opcode.program
                )

                if (
                    program.node_count()
                    > MAX_AST_NODES
                ):

                    raise RuntimeError(
                        "AST node limit exceeded."
                    )

                if (
                    program.depth()
                    > MAX_AST_DEPTH
                ):

                    raise RuntimeError(
                        "AST depth limit exceeded."
                    )

        # Bütün function çağrıları aynı AST
        # execution budget'ını paylaşır.
        ast_budget = [0]

        # Embedded DSL calls da bütün architecture
        # boyunca aynı counter'ı paylaşır.
        dsl_step_counter = [0]

        dsl_max_steps = max(
            40,
            self.total_instruction_count()
            * 6,
        )

        return (
            self._execute_architecture_node(
                node=architecture.main.root,
                value=float(input_value),
                context_id=context_id,
                budget=ast_budget,
                dsl_step_counter=dsl_step_counter,
                dsl_max_steps=dsl_max_steps,
                call_depth=0,
                function_stack=[],
                opcode_stack=[],
            )
        )

    def _execute_evolved_opcode(
        self,
        opcode_id: str,
        value: float,
        context_id: int,
        budget: list[int],
        dsl_step_counter: list[int],
        dsl_max_steps: int,
        call_depth: int,
        function_stack: list[str],
        opcode_stack: list[str],
    ) -> float:

        language = (
            self.evolved_language
        )

        if language is None:

            raise RuntimeError(
                "Invalid evolved opcode call."
            )

        opcode = (
            language.get_opcode(
                opcode_id
            )
        )

        if opcode is None:

            raise RuntimeError(
                "Invalid evolved opcode call."
            )

        if opcode_id in opcode_stack:

            raise RuntimeError(
                "Recursive evolved opcode call."
            )

        return (
            self._execute_architecture_node(
                node=opcode.program.root,
                value=value,
                context_id=context_id,
                budget=budget,
                dsl_step_counter=(
                    dsl_step_counter
                ),
                dsl_max_steps=dsl_max_steps,
                call_depth=(
                    call_depth + 1
                ),
                function_stack=(
                    function_stack
                ),
                opcode_stack=(
                    opcode_stack
                    + [opcode_id]
                ),
            )
        )

    def _execute_architecture_node(
        self,
        node: ASTNode,
        value: float,
        context_id: int,
        budget: list[int],
        dsl_step_counter: list[int],
        dsl_max_steps: int,
        call_depth: int,
        function_stack: list[str],
        opcode_stack: list[str],
    ) -> float:

        budget[0] += 1

        if (
            budget[0]
            > AST_EXECUTION_BUDGET
        ):

            raise RuntimeError(
                "AST execution budget exceeded."
            )

        if (
            call_depth
            > MAX_MODULE_CALL_DEPTH
        ):

            raise RuntimeError(
                "Maximum AST call depth exceeded."
            )

        node_type = node.node_type

        # =================================================
        # SEQUENCE
        # =================================================

        if node_type == "SEQUENCE":

            for child in node.children:

                value = (
                    self._execute_architecture_node(
                        node=child,
                        value=value,
                        context_id=context_id,
                        budget=budget,
                        dsl_step_counter=(
                            dsl_step_counter
                        ),
                        dsl_max_steps=(
                            dsl_max_steps
                        ),
                        call_depth=call_depth,
                        function_stack=(
                            function_stack
                        ),
                        opcode_stack=(
                            opcode_stack
                        ),
                    )
                )

            return value

        # =================================================
        # PRIMITIVES
        # =================================================

        if node_type == "ADD":
            return value + node.value

        if node_type == "SUBTRACT":
            return value - node.value

        if node_type == "MULTIPLY":
            return value * node.value

        if node_type == "ABS":
            return abs(value)

        # =================================================
        # CONTROL FLOW
        # =================================================

        if node_type == "IF_CONTEXT":

            if (
                context_id
                == node.context
                and node.children
            ):

                return (
                    self._execute_architecture_node(
                        node=node.children[0],
                        value=value,
                        context_id=context_id,
                        budget=budget,
                        dsl_step_counter=(
                            dsl_step_counter
                        ),
                        dsl_max_steps=(
                            dsl_max_steps
                        ),
                        call_depth=call_depth,
                        function_stack=(
                            function_stack
                        ),
                        opcode_stack=(
                            opcode_stack
                        ),
                    )
                )

            return value

        # =================================================
        # EVOLVED FUNCTION
        # =================================================

        if node_type == "CALL_FUNCTION":

            function_id = (
                node.function_id
            )

            if (
                function_id is None
            ):

                raise RuntimeError(
                    "Invalid evolved function call."
                )

            architecture = (
                self.program_architecture
            )

            if (
                architecture is None
                or function_id
                not in architecture.functions
            ):

                raise RuntimeError(
                    "Invalid evolved function call."
                )

            # ---------------------------------------------
            # Recursion currently forbidden.
            #
            # F001 → F001
            # F001 → F002 → F001
            # are both rejected.
            # ---------------------------------------------

            if (
                function_id
                in function_stack
            ):

                raise RuntimeError(
                    "Recursive evolved function call."
                )

            function = (
                architecture.functions[
                    function_id
                ]
            )

            return (
                self._execute_architecture_node(
                    node=function.program.root,
                    value=value,
                    context_id=context_id,
                    budget=budget,
                    dsl_step_counter=(
                        dsl_step_counter
                    ),
                    dsl_max_steps=(
                        dsl_max_steps
                    ),
                    call_depth=(
                        call_depth + 1
                    ),
                    function_stack=(
                        function_stack
                        + [function_id]
                    ),
                    opcode_stack=(
                        opcode_stack
                    ),
                )
            )

        # =================================================
        # EVOLVED OPCODE
        # =================================================

        if (
            node.node_type
            == "CALL_OPCODE"
        ):

            if node.opcode_id is None:

                raise RuntimeError(
                    "Invalid evolved opcode call."
                )

            return (
                self._execute_evolved_opcode(
                    opcode_id=(
                        node.opcode_id
                    ),
                    value=value,
                    context_id=context_id,
                    budget=budget,
                    dsl_step_counter=(
                        dsl_step_counter
                    ),
                    dsl_max_steps=(
                        dsl_max_steps
                    ),
                    call_depth=(
                        call_depth
                    ),
                    function_stack=(
                        function_stack
                    ),
                    opcode_stack=(
                        opcode_stack
                    ),
                )
            )

        # =================================================
        # LEGACY MAIN
        # =================================================

        if node_type == "CALL_LEGACY_MAIN":

            return self._execute_sequence(
                sequence=self.instructions,
                value=value,
                context_id=context_id,
                step_counter=dsl_step_counter,
                max_steps=dsl_max_steps,
                call_depth=(
                    call_depth + 1
                ),
            )

        # =================================================
        # MODULE
        # =================================================

        if node_type == "CALL_MODULE":

            module_id = node.module_id

            if (
                module_id is None
                or module_id
                not in self.modules
            ):

                raise RuntimeError(
                    "Invalid AST module call."
                )

            return self._execute_sequence(
                sequence=self.modules[
                    module_id
                ],
                value=value,
                context_id=context_id,
                step_counter=dsl_step_counter,
                max_steps=dsl_max_steps,
                call_depth=(
                    call_depth + 1
                ),
            )

        # =================================================
        # MACRO
        # =================================================

        if node_type == "CALL_MACRO":

            macro_id = node.macro_id

            if (
                macro_id is None
                or macro_id
                not in self.macros
            ):

                raise RuntimeError(
                    "Invalid AST macro call."
                )

            return self._execute_sequence(
                sequence=self.macros[
                    macro_id
                ],
                value=value,
                context_id=context_id,
                step_counter=dsl_step_counter,
                max_steps=dsl_max_steps,
                call_depth=(
                    call_depth + 1
                ),
            )

        raise RuntimeError(
            f"Unknown AST node: {node_type}"
        )

    # ---------------------------------------------------------
    # AST TRAVERSAL
    # ---------------------------------------------------------

    def _walk_ast_nodes(
        self,
    ):

        if self.ast_program is None:
            return

        stack = [
            self.ast_program.root
        ]

        while stack:

            node = stack.pop()

            yield node

            stack.extend(
                reversed(
                    node.children
                )
            )

    def _walk_program_nodes(
        self,
        program: ASTProgram,
    ):

        stack = [
            program.root
        ]

        while stack:

            node = stack.pop()

            yield node

            stack.extend(
                reversed(
                    node.children
                )
            )

    def _ast_child_slots(
        self,
    ):

        if self.ast_program is None:
            return

        stack = [
            self.ast_program.root
        ]

        while stack:

            parent = stack.pop()

            for index, child in enumerate(
                parent.children
            ):

                yield (
                    parent,
                    index,
                    child,
                )

                stack.append(
                    child
                )

    def _ast_sequence_nodes(
        self,
    ) -> list[ASTNode]:

        if self.ast_program is None:
            return []

        return [
            node
            for node in self._walk_ast_nodes()
            if node.node_type == "SEQUENCE"
        ]

    # ---------------------------------------------------------
    # CLONING
    # ---------------------------------------------------------

    def clone(
        self,
    ) -> "Genome":

        cloned_modules = {
            module_id: [
                instruction.copy()
                for instruction
                in module
            ]
            for module_id, module
            in self.modules.items()
        }

        cloned_meta = {
            module_id:
                dict(metadata)

            for module_id, metadata
            in self.module_meta.items()
        }

        cloned_macros = {
            macro_id: [
                instruction.copy()
                for instruction
                in macro
            ]

            for macro_id, macro
            in self.macros.items()
        }

        cloned_macro_meta = {
            macro_id:
                dict(metadata)

            for macro_id, metadata
            in self.macro_meta.items()
        }

        clone = Genome(
            instructions=[
                instruction.copy()
                for instruction
                in self.instructions
            ],
            modules=cloned_modules,
            module_meta=cloned_meta,
            macros=cloned_macros,
            macro_meta=cloned_macro_meta,

            ast_program=(
                self.ast_program.clone()
                if self.ast_program
                is not None
                else None
            ),

            program_architecture=(
                self.program_architecture
                .clone()

                if self.program_architecture
                is not None

                else None
            ),

            evolved_language=(
                self.evolved_language.clone()
                if self.evolved_language
                is not None
                else None
            ),

            execution_mode=(
                self.execution_mode
            ),
        )

        clone.next_module_id = (
            self.next_module_id
        )

        clone.next_macro_id = (
            self.next_macro_id
        )

        return clone

    # ---------------------------------------------------------
    # RANDOM INSTRUCTIONS
    # ---------------------------------------------------------

    def create_random_primitive(
        self,
    ) -> Instruction:

        operation = random.choice(
            PRIMITIVE_OPERATIONS
        )

        if operation in (
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
        ):

            return Instruction(
                operation=operation,
                value=random.uniform(
                    -3.0,
                    3.0,
                ),
            )

        if operation == "JUMP_IF_CONTEXT_NE":

            return Instruction(
                operation=operation,
                context=random.randint(
                    -1,
                    4,
                ),
                offset=random.randint(
                    1,
                    5,
                ),
            )

        return Instruction(
            operation="JUMP",
            offset=random.randint(
                1,
                5,
            ),
        )

    def create_random_main_instruction(
        self,
    ) -> Instruction:

        if (
            self.macros
            and random.random()
            < MACRO_INSTRUCTION_RATE
        ):

            macro_id = random.choice(
                list(
                    self.macros.keys()
                )
            )

            return Instruction(
                operation="CALL_MACRO",
                macro_id=macro_id,
            )

        # Modül varsa bazen CALL_MODULE üretilebilir.
        if (
            self.modules
            and random.random() < 0.20
        ):

            module_id = random.choice(
                list(
                    self.modules.keys()
                )
            )

            return Instruction(
                operation="CALL_MODULE",
                module_id=module_id,
            )

        return self.create_random_primitive()

    # ---------------------------------------------------------
    # V0.7 RANDOM AST CREATION
    # ---------------------------------------------------------

    def create_random_ast_leaf(
        self,
    ) -> ASTNode:

        choices = [
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
            "ABS",
        ]

        if self.modules:
            choices.append(
                "CALL_MODULE"
            )

        if self.macros:
            choices.append(
                "CALL_MACRO"
            )

        node_type = random.choice(
            choices
        )

        if node_type in (
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
        ):

            return ASTNode(
                node_type=node_type,

                value=random.uniform(
                    -3.0,
                    3.0,
                ),
            )

        if node_type == "ABS":

            return ASTNode(
                node_type="ABS",
            )

        if node_type == "CALL_MODULE":

            return ASTNode(
                node_type="CALL_MODULE",

                module_id=random.choice(
                    list(
                        self.modules.keys()
                    )
                ),
            )

        return ASTNode(
            node_type="CALL_MACRO",

            macro_id=random.choice(
                list(
                    self.macros.keys()
                )
            ),
        )

    def create_random_ast_node(
        self,
        allow_structure: bool = True,
    ) -> ASTNode:

        if (
            allow_structure
            and random.random() < 0.25
        ):

            return ASTNode(
                node_type="IF_CONTEXT",

                context=random.randint(
                    -1,
                    4,
                ),

                children=[
                    self.create_random_ast_leaf()
                ],
            )

        return self.create_random_ast_leaf()

    def _mutate_ast_parameters(
        self,
        mutations: list[str],
    ) -> None:

        if self.ast_program is None:
            return

        if self.execution_mode != "AST":
            return

        for index, node in enumerate(
            self._walk_ast_nodes()
        ):

            if (
                node.node_type
                in (
                    "ADD",
                    "SUBTRACT",
                    "MULTIPLY",
                )
            ):

                if (
                    random.random()
                    >= AST_PARAMETER_MUTATION_RATE
                ):
                    continue

                old_value = node.value

                node.value += random.gauss(
                    0.0,
                    AST_PARAMETER_MUTATION_SCALE,
                )

                mutations.append(
                    (
                        f"AST_PARAM[{index}] "
                        f"{node.node_type} "
                        f"{old_value:.4f} -> "
                        f"{node.value:.4f}"
                    )
                )

            elif (
                node.node_type
                == "IF_CONTEXT"
            ):

                if (
                    random.random()
                    >= AST_PARAMETER_MUTATION_RATE
                ):
                    continue

                old_context = node.context

                node.context = random.randint(
                    -1,
                    4,
                )

                mutations.append(
                    (
                        f"AST_CONTEXT[{index}] "
                        f"{old_context} -> "
                        f"{node.context}"
                    )
                )

    def _mutate_ast_node_replace(
        self,
        mutations: list[str],
    ) -> None:

        if self.ast_program is None:
            return

        if self.execution_mode != "AST":
            return

        if (
            random.random()
            >= AST_NODE_REPLACEMENT_RATE
        ):
            return

        slots = list(
            self._ast_child_slots()
        )

        # -------------------------------------------------
        # TRANSITION SAFETY
        #
        # Saf bridge'in tek CALL_LEGACY_MAIN düğümünü
        # doğrudan replacement ile yok etmiyoruz.
        #
        # Önce AST'nin başka computation geliştirmesi
        # gerekiyor.
        # -------------------------------------------------

        if self.ast_uses_legacy_main():

            non_legacy_nodes = [
                node
                for node in self._walk_ast_nodes()
                if node.node_type not in (
                    "SEQUENCE",
                    "CALL_LEGACY_MAIN",
                )
            ]

            if not non_legacy_nodes:

                slots = [
                    (
                        parent,
                        index,
                        child,
                    )
                    for (
                        parent,
                        index,
                        child,
                    )
                    in slots
                    if child.node_type
                    != "CALL_LEGACY_MAIN"
                ]

        if not slots:
            return

        parent, index, old_node = (
            random.choice(
                slots
            )
        )

        new_node = (
            self.create_random_ast_node(
                allow_structure=True,
            )
        )

        old_description = (
            old_node.describe()
        )

        new_description = (
            new_node.describe()
        )

        # Önce geçici olarak değiştir.
        parent.children[index] = (
            new_node
        )

        # Güvenlik sınırlarını aşıyorsa
        # mutation'ı geri al.
        if (
            self.ast_program.node_count()
            > MAX_AST_NODES
            or self.ast_program.depth()
            > MAX_AST_DEPTH
        ):

            parent.children[index] = (
                old_node
            )

            return

        mutations.append(
            (
                "AST_REPLACE "
                f"{old_description} -> "
                f"{new_description}"
            )
        )

    def _mutate_ast_subtree_insert(
        self,
        mutations: list[str],
    ) -> None:

        if self.ast_program is None:
            return

        if self.execution_mode != "AST":
            return

        if (
            random.random()
            >= AST_SUBTREE_INSERT_RATE
        ):
            return

        sequences = (
            self._ast_sequence_nodes()
        )

        if not sequences:
            return

        parent = random.choice(
            sequences
        )

        new_node = (
            self.create_random_ast_node(
                allow_structure=True,
            )
        )

        position = random.randint(
            0,
            len(parent.children),
        )

        parent.children.insert(
            position,
            new_node,
        )

        # Yeni subtree sınırları aşıyorsa
        # mutation'ı geri al.
        if (
            self.ast_program.node_count()
            > MAX_AST_NODES
            or self.ast_program.depth()
            > MAX_AST_DEPTH
        ):

            del parent.children[
                position
            ]

            return

        mutations.append(
            (
                "AST_INSERT "
                f"position={position} "
                f"{new_node.describe()}"
            )
        )

    def _mutate_ast_subtree_delete(
        self,
        mutations: list[str],
    ) -> None:

        if self.ast_program is None:
            return

        if self.execution_mode != "AST":
            return

        if (
            random.random()
            >= AST_SUBTREE_DELETE_RATE
        ):
            return

        sequences = [
            node
            for node
            in self._ast_sequence_nodes()
            if len(node.children) > 1
        ]

        if not sequences:
            return

        parent = random.choice(
            sequences
        )

        position = random.randrange(
            len(parent.children)
        )

        removed = parent.children[
            position
        ]

        del parent.children[
            position
        ]

        mutations.append(
            (
                "AST_DELETE "
                f"position={position} "
                f"{removed.describe()}"
            )
        )

    def _mutate_ast_subtree_duplicate(
        self,
        mutations: list[str],
    ) -> None:

        if self.ast_program is None:
            return

        if self.execution_mode != "AST":
            return

        if (
            random.random()
            >= AST_SUBTREE_DUPLICATION_RATE
        ):
            return

        # Root'un kendisini kopyalamıyoruz.
        # Root altındaki herhangi bir subtree
        # kaynak olabilir.
        source_nodes = [
            node
            for (
                _parent,
                _index,
                node,
            )
            in self._ast_child_slots()
            if node.node_type
            != "CALL_LEGACY_MAIN"
        ]

        if not source_nodes:
            return

        destination_sequences = (
            self._ast_sequence_nodes()
        )

        if not destination_sequences:
            return

        source = random.choice(
            source_nodes
        )

        destination = random.choice(
            destination_sequences
        )

        duplicate = source.clone()

        position = random.randint(
            0,
            len(destination.children),
        )

        destination.children.insert(
            position,
            duplicate,
        )

        # Complexity / safety sınırları
        if (
            self.ast_program.node_count()
            > MAX_AST_NODES
            or self.ast_program.depth()
            > MAX_AST_DEPTH
        ):

            del destination.children[
                position
            ]

            return

        mutations.append(
            (
                "AST_DUPLICATE "
                f"position={position} "
                f"nodes={duplicate.node_count()} "
                f"{duplicate.describe()}"
            )
        )

    def _mutate_ast_structure(
        self,
        mutations: list[str],
    ) -> None:

        ast_mutation_start = len(
            mutations
        )

        # ---------------------------------------------
        # 1. PARAMETER MUTATION
        # ---------------------------------------------

        self._mutate_ast_parameters(
            mutations
        )

        ast_changed = any(
            mutation.startswith(
                "AST_"
            )
            for mutation
            in mutations[
                ast_mutation_start:
            ]
        )

        # ---------------------------------------------
        # 2. NODE REPLACEMENT
        # ---------------------------------------------

        if not ast_changed:

            self._mutate_ast_node_replace(
                mutations
            )

        ast_changed = any(
            mutation.startswith(
                "AST_"
            )
            for mutation
            in mutations[
                ast_mutation_start:
            ]
        )

        # ---------------------------------------------
        # 3. SUBTREE INSERT
        # ---------------------------------------------

        if not ast_changed:

            self._mutate_ast_subtree_insert(
                mutations
            )

        ast_changed = any(
            mutation.startswith(
                "AST_"
            )
            for mutation
            in mutations[
                ast_mutation_start:
            ]
        )

        # ---------------------------------------------
        # 4. SUBTREE DELETE
        # ---------------------------------------------

        if not ast_changed:

            self._mutate_ast_subtree_delete(
                mutations
            )

        ast_changed = any(
            mutation.startswith(
                "AST_"
            )
            for mutation
            in mutations[
                ast_mutation_start:
            ]
        )

        # ---------------------------------------------
        # 5. SUBTREE DUPLICATION
        # ---------------------------------------------

        if not ast_changed:

            self._mutate_ast_subtree_duplicate(
                mutations
            )

    def _maybe_create_ast(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        if self.ast_program is not None:
            return

        if (
            random.random()
            >= AST_CREATION_RATE
        ):
            return

        # -------------------------------------------------
        # PATH A — NEAR-NEUTRAL REPRESENTATION BRIDGE
        # -------------------------------------------------

        if (
            self.instructions
            and random.random()
            < AST_BRIDGE_CREATION_CHANCE
        ):

            program = ASTProgram(
                origin="BRIDGE_SEED",
                birth_generation=generation,

                root=ASTNode(
                    node_type="SEQUENCE",

                    children=[
                        ASTNode(
                            node_type="CALL_LEGACY_MAIN"
                        )
                    ],
                ),
            )

        # -------------------------------------------------
        # PATH B — DE NOVO RANDOM AST
        # -------------------------------------------------

        else:

            child_count = random.randint(
                1,
                4,
            )

            program = ASTProgram(
                origin="RANDOM_SEED",
                birth_generation=generation,

                root=ASTNode(
                    node_type="SEQUENCE",

                    children=[
                        self.create_random_ast_node()
                        for _ in range(
                            child_count
                        )
                    ],
                ),
            )

        if (
            program.node_count()
            > MAX_AST_NODES
            or program.depth()
            > MAX_AST_DEPTH
        ):
            return

        self.ast_program = program
        self.execution_mode = "AST"

        mutations.append(
            (
                "CREATE_AST "
                f"origin={program.origin} "
                f"nodes={program.node_count()} "
                f"depth={program.depth()} "
                f"{program.describe()}"
            )
        )

    def _architecture_program_entries(
        self,
    ) -> list[tuple[str, ASTProgram]]:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return []

        entries = [
            (
                "MAIN",
                architecture.main,
            )
        ]

        entries.extend(
            (
                function_id,
                function.program,
            )

            for function_id, function
            in architecture.functions.items()
        )

        return entries

    def _active_architecture_program_entries(
        self,
    ) -> list[tuple[str, ASTProgram]]:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return []

        (
            reachable_function_ids,
            _,
            _,
        ) = (
            self
            ._reachable_architecture_code()
        )

        entries: list[
            tuple[str, ASTProgram]
        ] = [
            (
                "MAIN",
                architecture.main,
            )
        ]

        entries.extend(
            (
                function_id,
                architecture
                .functions[
                    function_id
                ]
                .program,
            )

            for function_id
            in sorted(
                reachable_function_ids
            )

            if function_id
            in architecture.functions
        )

        return entries

    def _reachable_architecture_function_ids(
        self,
    ) -> set[str]:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return set()

        reachable: set[str] = set()

        pending: list[ASTProgram] = [
            architecture.main
        ]

        while pending:

            program = pending.pop()

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    != "CALL_FUNCTION"
                ):
                    continue

                function_id = (
                    node.function_id
                )

                if function_id is None:
                    continue

                if (
                    function_id
                    not in architecture.functions
                ):
                    continue

                if (
                    function_id
                    in reachable
                ):
                    continue

                reachable.add(
                    function_id
                )

                pending.append(
                    architecture
                    .functions[
                        function_id
                    ]
                    .program
                )

        return reachable

    def _reachable_architecture_code(
        self,
    ) -> tuple[
        set[str],
        set[str],
        bool,
    ]:

        architecture = (
            self.program_architecture
        )

        language = (
            self.evolved_language
        )

        if architecture is None:

            return (
                set(),
                set(),
                False,
            )

        reachable_functions: set[str] = set()

        reachable_opcodes: set[str] = set()

        uses_legacy_main = False

        pending_programs: list[
            ASTProgram
        ] = [
            architecture.main
        ]

        while pending_programs:

            program = (
                pending_programs.pop()
            )

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                # =====================================
                # LEGACY MAIN
                # =====================================

                if (
                    node.node_type
                    == "CALL_LEGACY_MAIN"
                ):

                    uses_legacy_main = True

                    continue

                # =====================================
                # FUNCTION
                # =====================================

                if (
                    node.node_type
                    == "CALL_FUNCTION"
                ):

                    function_id = (
                        node.function_id
                    )

                    if (
                        function_id is None
                        or function_id
                        not in architecture.functions
                        or function_id
                        in reachable_functions
                    ):

                        continue

                    reachable_functions.add(
                        function_id
                    )

                    pending_programs.append(
                        architecture
                        .functions[
                            function_id
                        ]
                        .program
                    )

                    continue

                # =====================================
                # OPCODE
                # =====================================

                if (
                    node.node_type
                    == "CALL_OPCODE"
                ):

                    opcode_id = (
                        node.opcode_id
                    )

                    if (
                        language is None
                        or opcode_id is None
                        or opcode_id
                        not in language.opcodes
                        or opcode_id
                        in reachable_opcodes
                    ):

                        continue

                    reachable_opcodes.add(
                        opcode_id
                    )

                    pending_programs.append(
                        language
                        .opcodes[
                            opcode_id
                        ]
                        .program
                    )

        return (
            reachable_functions,
            reachable_opcodes,
            uses_legacy_main,
        )

    def _evolved_opcode_program_entries(
        self,
    ) -> list[tuple[str, ASTProgram]]:

        language = self.evolved_language

        if language is None:
            return []

        return [
            (
                opcode_id,
                opcode.program,
            )
            for opcode_id, opcode
            in language.opcodes.items()
        ]


    def _evolved_language_is_valid(
        self,
    ) -> bool:

        language = self.evolved_language

        if language is None:
            return True

        if (
            language.opcode_count()
            > MAX_EVOLVED_OPCODES
        ):
            return False

        opcode_ids = set(
            language.opcodes.keys()
        )

        for (
            _opcode_id,
            program,
        ) in self._evolved_opcode_program_entries():

            if program.root is None:
                return False

            if (
                program.node_count()
                > MAX_AST_NODES
            ):
                return False

            if (
                program.depth()
                > MAX_AST_DEPTH
            ):
                return False

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_OPCODE"
                    and
                    node.opcode_id
                    not in opcode_ids
                ):
                    return False

        return True

    def _create_random_opcode_program(
        self,
        generation: int,
    ) -> ASTProgram:

        child_count = random.randint(
            1,
            3,
        )

        return ASTProgram(
            root=ASTNode(
                node_type="SEQUENCE",
                children=[
                    self
                    ._create_random_architecture_node(
                        allow_function_calls=False
                    )

                    for _ in range(
                        child_count
                    )
                ],
            ),
            origin="EVOLVED_OPCODE",
            birth_generation=generation,
        )

    def _language_create_opcode(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        if self.evolved_language is None:

            self.evolved_language = (
                EvolvedLanguage(
                    birth_generation=generation,
                    origin="EVOLVED_LANGUAGE",
                )
            )

        language = self.evolved_language

        if (
            language.opcode_count()
            >= MAX_EVOLVED_OPCODES
        ):
            return

        program = (
            self._create_random_opcode_program(
                generation
            )
        )

        opcode_id = language.add_opcode(
            program=program,
            generation=generation,
            origin="EVOLVED_CREATE",
        )

        if not self._evolved_language_is_valid():

            language.remove_opcode(
                opcode_id
            )

            return

        mutations.append(
            (
                "LANG_CREATE_OPCODE "
                f"{opcode_id} "
                f"{program.describe()}"
            )
        )

    def _language_derive_opcode(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        language = (
            self.evolved_language
        )

        if (
            language is None
            or not language.opcodes
            or language.opcode_count()
            >= MAX_EVOLVED_OPCODES
        ):
            return

        parent_opcode = random.choice(
            list(
                language.opcodes.values()
            )
        )

        parent_opcode.ensure_lineage_metadata()

        child_program = (
            parent_opcode
            .program
            .clone()
        )

        child_opcode_id = (
            language.add_opcode(
                program=child_program,
                generation=generation,
                origin="EVOLVED_DERIVATION",
                parent_opcode_id=(
                    parent_opcode.opcode_id
                ),
                lineage_root_id=(
                    parent_opcode
                    .lineage_root_id
                ),
            )
        )

        child_opcode = (
            language.opcodes[
                child_opcode_id
            ]
        )

        child_mutations: list[str] = []

        if (
            random.random()
            <
            DERIVED_OPCODE_GENTLE_PROBABILITY
        ):

            derivation_mode = "GENTLE"

            self._language_mutate_derived_opcode(
                mutations=child_mutations,
                generation=generation,
                opcode_id=(
                    child_opcode_id
                ),
            )

        else:

            derivation_mode = "UNRESTRICTED"

            self._language_mutate_opcode(
                mutations=child_mutations,
                generation=generation,
                target_opcode_id=(
                    child_opcode_id
                ),
            )

        if not child_mutations:

            language.remove_opcode(
                child_opcode_id
            )

            return

        if (
            not self
            ._evolved_language_is_valid()
        ):

            language.remove_opcode(
                child_opcode_id
            )

            return

        mutations.append(
            (
                "LANG_DERIVE_OPCODE "
                f"{parent_opcode.opcode_id} "
                f"-> {child_opcode_id} "
                f"root="
                f"{child_opcode.lineage_root_id} "
                f"revision="
                f"{child_opcode.revision} "
                f"mode={derivation_mode} "
                f"{child_mutations[0]}"
            )
        )

    def _language_mutate_opcode(
        self,
        mutations: list[str],
        generation: int,
        target_opcode_id: str | None = None,
    ) -> None:

        language = self.evolved_language

        if (
            language is None
            or not language.opcodes
        ):
            return

        if target_opcode_id is not None:

            if (
                target_opcode_id
                not in language.opcodes
            ):
                return

            opcode_id = (
                target_opcode_id
            )

        else:

            opcode_id = random.choice(
                list(
                    language.opcodes.keys()
                )
            )

        opcode = (
            language.opcodes[
                opcode_id
            ]
        )

        program = opcode.program

        backup = program.to_dict()

        nodes = list(
            self._walk_program_nodes(
                program
            )
        )

        mutable_parameters = [
            node
            for node in nodes
            if node.node_type in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
                "IF_CONTEXT",
            )
        ]

        sequences = [
            node
            for node in nodes
            if node.node_type
            == "SEQUENCE"
        ]

        action = random.random()

        description = None

        # =============================================
        # PARAMETER MUTATION
        # =============================================

        if (
            action < 0.50
            and mutable_parameters
        ):

            node = random.choice(
                mutable_parameters
            )

            if node.node_type in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            ):

                old = node.value

                node.value += random.gauss(
                    0.0,
                    OPCODE_PARAMETER_MUTATION_SCALE,
                )

                description = (
                    f"{node.node_type} "
                    f"{old:.4f} -> "
                    f"{node.value:.4f}"
                )

            else:

                old = node.context

                node.context = (
                    random.randint(
                        -1,
                        4,
                    )
                )

                description = (
                    "IF_CONTEXT "
                    f"{old} -> "
                    f"{node.context}"
                )

        # =============================================
        # INSERT
        # =============================================

        elif (
            action < 0.80
            and sequences
        ):

            parent = random.choice(
                sequences
            )

            new_node = (
                self
                ._create_random_architecture_node(
                    allow_function_calls=False
                )
            )

            position = random.randint(
                0,
                len(parent.children),
            )

            parent.children.insert(
                position,
                new_node,
            )

            description = (
                f"INSERT "
                f"{new_node.describe()}"
            )

        # =============================================
        # DELETE
        # =============================================

        else:

            candidates = [
                node
                for node in sequences
                if len(node.children) > 1
            ]

            if not candidates:
                return

            parent = random.choice(
                candidates
            )

            position = random.randrange(
                len(parent.children)
            )

            removed = (
                parent.children[
                    position
                ]
            )

            del parent.children[
                position
            ]

            description = (
                f"DELETE "
                f"{removed.describe()}"
            )

        if description is None:
            return

        if not self._evolved_language_is_valid():

            opcode.program = (
                ASTProgram.from_dict(
                    backup
                )
            )

            return

        opcode.record_semantic_revision(
            generation=generation,
            event="MUTATED",
            description=description,
            previous_program=backup,
        )

        mutations.append(
            (
                "LANG_MUTATE_OPCODE "
                f"{opcode_id} "
                f"revision={opcode.revision} "
                f"{description}"
            )
        )

    def _language_mutate_derived_opcode(
        self,
        mutations: list[str],
        generation: int,
        opcode_id: str,
    ) -> None:

        language = (
            self.evolved_language
        )

        if (
            language is None
            or opcode_id
            not in language.opcodes
        ):
            return

        opcode = (
            language.opcodes[
                opcode_id
            ]
        )

        program = opcode.program

        backup = program.to_dict()

        nodes = list(
            self._walk_program_nodes(
                program
            )
        )

        numeric_parameters = [
            node

            for node in nodes

            if node.node_type in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            )
        ]

        if not numeric_parameters:
            return

        node = random.choice(
            numeric_parameters
        )

        old_value = node.value

        delta = random.gauss(
            0.0,
            DERIVED_OPCODE_PARAMETER_MUTATION_SCALE,
        )

        node.value += delta

        if (
            abs(
                node.value
                - old_value
            )
            <= 1e-12
        ):

            opcode.program = (
                ASTProgram.from_dict(
                    backup
                )
            )

            return

        description = (
            f"{node.node_type} "
            f"{old_value:.4f} -> "
            f"{node.value:.4f} "
            f"delta={delta:.4f}"
        )

        if not self._evolved_language_is_valid():

            opcode.program = (
                ASTProgram.from_dict(
                    backup
                )
            )

            return

        opcode.record_semantic_revision(
            generation=generation,
            event=(
                "DERIVED_PARAMETER_MUTATION"
            ),
            description=description,
            previous_program=backup,
        )

        mutations.append(
            (
                "LANG_MUTATE_DERIVED_OPCODE "
                f"{opcode_id} "
                f"revision="
                f"{opcode.revision} "
                f"{description}"
            )
        )

    def _language_delete_opcode(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        language = self.evolved_language

        if (
            language is None
            or not language.opcodes
        ):
            return

        referenced: set[str] = set()

        # ---------------------------------------------
        # Architecture -> opcode references
        # ---------------------------------------------

        for (
            _name,
            program,
        ) in self._architecture_program_entries():

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_OPCODE"
                    and node.opcode_id
                    is not None
                ):

                    referenced.add(
                        node.opcode_id
                    )

        # ---------------------------------------------
        # Opcode -> opcode references
        # ---------------------------------------------

        for (
            _opcode_id,
            program,
        ) in self._evolved_opcode_program_entries():

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_OPCODE"
                    and node.opcode_id
                    is not None
                ):

                    referenced.add(
                        node.opcode_id
                    )

        candidates = [
            opcode_id

            for opcode_id
            in language.opcodes

            if opcode_id
            not in referenced
        ]

        if not candidates:
            return

        opcode_id = random.choice(
            candidates
        )

        opcode = (
            language.opcodes[
                opcode_id
            ]
        )

        description = (
            opcode.program.describe()
        )

        revision = (
            opcode.revision
        )

        lineage_root_id = (
            opcode.lineage_root_id
        )

        archived = (
            language
            .archive_and_remove_opcode(
                opcode_id=opcode_id,
                generation=generation,
                reason=(
                    "EVOLVED_DELETION"
                ),
            )
        )

        if archived is None:
            return

        mutations.append(
            (
                "LANG_DELETE_OPCODE "
                f"{opcode_id} "
                f"root={lineage_root_id} "
                f"revision={revision} "
                f"generation={generation} "
                f"{description}"
            )
        )

    def _language_insert_opcode_call(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        language = (
            self.evolved_language
        )

        if (
            architecture is None
            or language is None
            or not language.opcodes
        ):
            return

        all_entries = (
            self._architecture_program_entries()
        )

        active_entries = (
            self
            ._active_architecture_program_entries()
        )

        active_program_ids = {
            id(program)

            for _, program
            in active_entries
        }

        # =============================================
        # DORMANT LANGUAGE WIRING
        #
        # Bu mutation phenotype'a do?rudan
        # dokunmayan programlarda CALL_OPCODE
        # ba?lant?lar? kurar.
        #
        # Semantic shock burada kullan?lmaz;
        # dormant program?n ??kt?s? hen?z
        # organizman?n davran???na ba?l? de?ildir.
        #
        # Function daha sonra aktifle?irse
        # G7 gentle activation b?t?n birle?ik
        # davran??? ?l?er.
        # =============================================

        dormant_sequences: list[
            tuple[str, ASTNode]
        ] = []

        for (
            name,
            program,
        ) in all_entries:

            if (
                id(program)
                in active_program_ids
            ):
                continue

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "SEQUENCE"
                ):

                    dormant_sequences.append(
                        (
                            name,
                            node,
                        )
                    )

        # Hi? dormant program kalmad?ysa global
        # mutation bo?a gitmesin; active gentle
        # activation yoluna d??s?n.
        if not dormant_sequences:

            self._language_insert_local_opcode_call(
                mutations
            )

            return

        name, parent = random.choice(
            dormant_sequences
        )

        opcode_id = random.choice(
            list(
                language.opcodes.keys()
            )
        )

        position = random.randint(
            0,
            len(parent.children),
        )

        node = ASTNode(
            node_type="CALL_OPCODE",
            opcode_id=opcode_id,
        )

        parent.children.insert(
            position,
            node,
        )

        if (
            not self._architecture_is_valid()
            or
            not self._evolved_language_is_valid()
        ):

            del parent.children[
                position
            ]

            return

        mutations.append(
            (
                "LANG_INSERT_OPCODE_DORMANT "
                f"{name} -> {opcode_id} "
                f"position={position} "
                f"dormant_sequences="
                f"{len(dormant_sequences)}"
            )
        )


    def _language_insert_local_opcode_call(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        language = (
            self.evolved_language
        )

        if (
            architecture is None
            or language is None
            or not language.opcodes
        ):
            return

        baseline_outputs = (
            self
            ._measure_current_architecture_behavior()
        )

        if baseline_outputs is None:
            return

        sequences: list[
            tuple[str, ASTNode]
        ] = []

        for (
            name,
            program,
        ) in (
            self
            ._active_architecture_program_entries()
        ):

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "SEQUENCE"
                ):

                    sequences.append(
                        (
                            name,
                            node,
                        )
                    )

        if not sequences:
            return

        opcode_ids = sorted(
            language.opcodes.keys()
        )

        if not opcode_ids:
            return

        # =============================================
        # ACTIVE PHENOTYPE SEARCH SPACE
        # =============================================

        search_space = []

        for (
            name,
            parent,
        ) in sequences:

            for opcode_id in opcode_ids:

                for position in range(
                    len(parent.children) + 1
                ):

                    search_space.append(
                        (
                            name,
                            parent,
                            opcode_id,
                            position,
                        )
                    )

        if not search_space:
            return

        total_search_space = len(
            search_space
        )

        max_candidates = 128

        if (
            total_search_space
            <= max_candidates
        ):

            candidate_specs = (
                search_space
            )

            search_mode = (
                "EXHAUSTIVE"
            )

        else:

            candidate_specs = []

            # Her opcode en az bir kez temsil edilir.
            for opcode_id in opcode_ids:

                matching = [
                    item

                    for item
                    in search_space

                    if item[2]
                    == opcode_id
                ]

                if matching:

                    candidate_specs.append(
                        random.choice(
                            matching
                        )
                    )

            remaining = (
                max_candidates
                - len(candidate_specs)
            )

            if remaining > 0:

                selected_keys = {
                    (
                        item[0],
                        id(item[1]),
                        item[2],
                        item[3],
                    )

                    for item
                    in candidate_specs
                }

                pool = [
                    item

                    for item
                    in search_space

                    if (
                        item[0],
                        id(item[1]),
                        item[2],
                        item[3],
                    )
                    not in selected_keys
                ]

                if pool:

                    candidate_specs.extend(
                        random.sample(
                            pool,
                            k=min(
                                remaining,
                                len(pool),
                            ),
                        )
                    )

            search_mode = (
                "STRATIFIED"
            )

        # =============================================
        # FULL-PROGRAM SEMANTIC SHOCK
        # =============================================

        candidates = []

        for (
            name,
            parent,
            opcode_id,
            position,
        ) in candidate_specs:

            node = ASTNode(
                node_type="CALL_OPCODE",
                opcode_id=opcode_id,
            )

            parent.children.insert(
                position,
                node,
            )

            valid = (
                self._architecture_is_valid()
                and
                self._evolved_language_is_valid()
            )

            if valid:

                shock = (
                    self
                    ._activation_semantic_shock(
                        baseline_outputs
                    )
                )

            else:

                shock = float(
                    "inf"
                )

            del parent.children[
                position
            ]

            if not math.isfinite(
                shock
            ):
                continue

            candidates.append(
                {
                    "name":
                        name,

                    "parent":
                        parent,

                    "position":
                        position,

                    "opcode_id":
                        opcode_id,

                    "shock":
                        shock,
                }
            )

        if not candidates:
            return

        min_shock = min(
            candidate["shock"]
            for candidate
            in candidates
        )

        # =============================================
        # GENTLE + EXPLORATION
        #
        # %80 semantic-shock bias
        # %20 uniform exploration
        #
        # Hard threshold yok.
        # Fitness / task target yok.
        # =============================================

        exploration_probability = 0.20

        if (
            random.random()
            < exploration_probability
        ):

            selected = random.choice(
                candidates
            )

            selection_mode = (
                "EXPLORE"
            )

        else:

            weights = [
                1.0
                / (
                    1.0
                    + candidate["shock"]
                )

                for candidate
                in candidates
            ]

            selected = random.choices(
                candidates,
                weights=weights,
                k=1,
            )[0]

            selection_mode = (
                "GENTLE"
            )

        node = ASTNode(
            node_type="CALL_OPCODE",
            opcode_id=(
                selected[
                    "opcode_id"
                ]
            ),
        )

        selected[
            "parent"
        ].children.insert(
            selected[
                "position"
            ],
            node,
        )

        if (
            not self._architecture_is_valid()
            or
            not self._evolved_language_is_valid()
        ):

            del selected[
                "parent"
            ].children[
                selected[
                    "position"
                ]
            ]

            return

        mutations.append(
            (
                "LANG_INSERT_LOCAL_OPCODE_CALL_GENTLE "
                f"{selected['name']} "
                f"-> {selected['opcode_id']} "
                f"position="
                f"{selected['position']} "
                f"shock="
                f"{selected['shock']:.12f} "
                f"min_shock="
                f"{min_shock:.12f} "
                f"tested="
                f"{len(candidates)} "
                f"space="
                f"{total_search_space} "
                f"search="
                f"{search_mode} "
                f"selection="
                f"{selection_mode}"
            )
        )


    def _language_retarget_opcode_call(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        language = (
            self.evolved_language
        )

        if (
            architecture is None
            or language is None
            or len(language.opcodes) < 2
        ):
            return

        all_entries = (
            self._architecture_program_entries()
        )

        active_entries = (
            self
            ._active_architecture_program_entries()
        )

        active_program_ids = {
            id(program)

            for _, program
            in active_entries
        }

        calls = []

        for (
            name,
            program,
        ) in all_entries:

            program_is_active = (
                id(program)
                in active_program_ids
            )

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_OPCODE"
                    and node.opcode_id
                    is not None
                ):

                    calls.append(
                        (
                            name,
                            program,
                            node,
                            program_is_active,
                        )
                    )

        if not calls:
            return

        (
            name,
            program,
            node,
            program_is_active,
        ) = random.choice(
            calls
        )

        old_target = (
            node.opcode_id
        )

        target_ids = [
            opcode_id

            for opcode_id
            in language.opcodes

            if opcode_id != old_target
        ]

        if not target_ids:
            return

        # =============================================
        # DORMANT RETARGET
        # =============================================

        if not program_is_active:

            new_target = random.choice(
                target_ids
            )

            node.opcode_id = (
                new_target
            )

            if (
                not self._architecture_is_valid()
                or
                not self._evolved_language_is_valid()
            ):

                node.opcode_id = (
                    old_target
                )

                return

            mutations.append(
                (
                    "LANG_RETARGET_OPCODE_DORMANT "
                    f"{name}: "
                    f"{old_target} -> "
                    f"{new_target}"
                )
            )

            return

        # =============================================
        # ACTIVE RETARGET
        # =============================================

        baseline_outputs = (
            self
            ._measure_current_architecture_behavior()
        )

        if baseline_outputs is None:
            return

        candidates = []

        for new_target in target_ids:

            node.opcode_id = (
                new_target
            )

            if (
                not self._architecture_is_valid()
                or
                not self._evolved_language_is_valid()
            ):

                node.opcode_id = (
                    old_target
                )

                continue

            shock = (
                self
                ._activation_semantic_shock(
                    baseline_outputs
                )
            )

            node.opcode_id = (
                old_target
            )

            if not math.isfinite(
                shock
            ):
                continue

            candidates.append(
                {
                    "target":
                        new_target,

                    "shock":
                        shock,
                }
            )

        node.opcode_id = (
            old_target
        )

        if not candidates:
            return

        min_shock = min(
            candidate["shock"]

            for candidate
            in candidates
        )

        if random.random() < 0.20:

            selected = random.choice(
                candidates
            )

            selection_mode = (
                "EXPLORE"
            )

        else:

            weights = [
                1.0
                / (
                    1.0
                    + candidate["shock"]
                )

                for candidate
                in candidates
            ]

            selected = random.choices(
                candidates,
                weights=weights,
                k=1,
            )[0]

            selection_mode = (
                "GENTLE"
            )

        node.opcode_id = (
            selected["target"]
        )

        if (
            not self._architecture_is_valid()
            or
            not self._evolved_language_is_valid()
        ):

            node.opcode_id = (
                old_target
            )

            return

        mutations.append(
            (
                "LANG_RETARGET_OPCODE_GENTLE "
                f"{name}: "
                f"{old_target} -> "
                f"{selected['target']} "
                f"shock="
                f"{selected['shock']:.12f} "
                f"min_shock="
                f"{min_shock:.12f} "
                f"candidates="
                f"{len(candidates)} "
                f"selection="
                f"{selection_mode}"
            )
        )


    def _mutate_evolved_language(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        language = self.evolved_language

        # Vocabulary henüz yoksa ilk mutation
        # doğrudan ilk opcode'u oluşturur.
        if (
            language is None
            or language.opcode_count() == 0
        ):

            self._language_create_opcode(
                mutations,
                generation,
            )

            return

        roll = random.random()

        boundary = (
            OPCODE_CREATE_WEIGHT
        )

        if roll < boundary:

            self._language_create_opcode(
                mutations,
                generation,
            )

            return

        boundary += (
            OPCODE_DERIVE_WEIGHT
        )

        if roll < boundary:

            self._language_derive_opcode(
                mutations,
                generation,
            )

            return

        boundary += (
            OPCODE_MUTATE_WEIGHT
        )

        if roll < boundary:

            self._language_mutate_opcode(
                mutations,
                generation,
            )

            return

        boundary += (
            OPCODE_DELETE_WEIGHT
        )

        if roll < boundary:

            self._language_delete_opcode(
                mutations,
                generation,
            )

            return

        boundary += (
            OPCODE_INSERT_CALL_WEIGHT
        )

        if roll < boundary:

            self._language_insert_opcode_call(
                mutations
            )

            return

        boundary += (
            OPCODE_LOCAL_INSERT_CALL_WEIGHT
        )

        if roll < boundary:

            self._language_insert_local_opcode_call(
                mutations
            )

            return

        self._language_retarget_opcode_call(
            mutations
        )

    def _architecture_is_valid(
        self,
    ) -> bool:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return False

        if (
            architecture.function_count()
            > MAX_ARCH_FUNCTIONS
        ):
            return False

        # =================================================
        # STRUCTURAL LIMITS
        # =================================================

        for (
            _name,
            program,
        ) in self._architecture_program_entries():

            if (
                program.node_count()
                > MAX_AST_NODES
            ):
                return False

            if (
                program.depth()
                > MAX_AST_DEPTH
            ):
                return False

        function_ids = set(
            architecture.functions.keys()
        )

        # =================================================
        # ALL FUNCTION REFERENCES MUST EXIST
        # =================================================

        for (
            _name,
            program,
        ) in self._architecture_program_entries():

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_FUNCTION"
                ):

                    if (
                        node.function_id
                        not in function_ids
                    ):
                        return False

                if (
                    node.node_type
                    == "CALL_OPCODE"
                ):

                    language = (
                        self.evolved_language
                    )

                    if (
                        language is None
                        or node.opcode_id
                        not in language.opcodes
                    ):

                        return False

        # =================================================
        # FUNCTION CALL GRAPH
        #
        # Recursion is not permitted yet.
        # =================================================

        graph: dict[
            str,
            set[str],
        ] = {
            function_id: set()
            for function_id
            in function_ids
        }

        for (
            function_id,
            function,
        ) in architecture.functions.items():

            for node in (
                self._walk_program_nodes(
                    function.program
                )
            ):

                if (
                    node.node_type
                    == "CALL_FUNCTION"
                    and node.function_id
                    is not None
                ):

                    graph[
                        function_id
                    ].add(
                        node.function_id
                    )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(
            function_id: str,
        ) -> bool:

            if function_id in visiting:
                return False

            if function_id in visited:
                return True

            visiting.add(
                function_id
            )

            for target in graph[
                function_id
            ]:

                if not visit(
                    target
                ):
                    return False

            visiting.remove(
                function_id
            )

            visited.add(
                function_id
            )

            return True

        for function_id in function_ids:

            if not visit(
                function_id
            ):
                return False

        return True

    def _create_random_architecture_leaf(
        self,
        allow_function_calls: bool = True,
    ) -> ASTNode:

        choices = [
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
            "ABS",
        ]

        if self.modules:
            choices.append(
                "CALL_MODULE"
            )

        if self.macros:
            choices.append(
                "CALL_MACRO"
            )

        architecture = (
            self.program_architecture
        )

        if (
            allow_function_calls
            and architecture is not None
            and architecture.functions
        ):

            choices.append(
                "CALL_FUNCTION"
            )

        node_type = random.choice(
            choices
        )

        if node_type in (
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
        ):

            return ASTNode(
                node_type=node_type,
                value=random.uniform(
                    -3.0,
                    3.0,
                ),
            )

        if node_type == "ABS":

            return ASTNode(
                node_type="ABS",
            )

        if node_type == "CALL_MODULE":

            return ASTNode(
                node_type="CALL_MODULE",
                module_id=random.choice(
                    list(
                        self.modules.keys()
                    )
                ),
            )

        if node_type == "CALL_MACRO":

            return ASTNode(
                node_type="CALL_MACRO",
                macro_id=random.choice(
                    list(
                        self.macros.keys()
                    )
                ),
            )

        return ASTNode(
            node_type="CALL_FUNCTION",
            function_id=random.choice(
                list(
                    architecture
                    .functions.keys()
                )
            ),
        )

    def _create_random_architecture_node(
        self,
        allow_function_calls: bool = True,
    ) -> ASTNode:

        if random.random() < 0.25:

            return ASTNode(
                node_type="IF_CONTEXT",
                context=random.randint(
                    -1,
                    4,
                ),
                children=[
                    self
                    ._create_random_architecture_leaf(
                        allow_function_calls=(
                            allow_function_calls
                        )
                    )
                ],
            )

        return (
            self._create_random_architecture_leaf(
                allow_function_calls=(
                    allow_function_calls
                )
            )
        )

    def _maybe_create_architecture(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        if (
            self.program_architecture
            is not None
        ):
            return

        if (
            random.random()
            >= ARCH_CREATION_RATE
        ):
            return

        # =================================================
        # AST → ARCH
        #
        # Existing evolved AST becomes architecture MAIN.
        # =================================================

        if (
            self.execution_mode == "AST"
            and self.ast_program is not None
        ):

            main = (
                self.ast_program.clone()
            )

            origin = (
                "AST_ARCH_BRIDGE"
            )

        # =================================================
        # DSL → ARCH
        #
        # Near-neutral representation bridge.
        # =================================================

        elif self.instructions:

            main = ASTProgram(
                root=ASTNode(
                    node_type="SEQUENCE",
                    children=[
                        ASTNode(
                            node_type=(
                                "CALL_LEGACY_MAIN"
                            )
                        )
                    ],
                ),
                origin="DSL_ARCH_BRIDGE",
                birth_generation=generation,
            )

            origin = (
                "DSL_ARCH_BRIDGE"
            )

        # =================================================
        # DE NOVO
        # =================================================

        else:

            child_count = random.randint(
                1,
                3,
            )

            main = ASTProgram(
                root=ASTNode(
                    node_type="SEQUENCE",
                    children=[
                        self
                        ._create_random_architecture_node(
                            allow_function_calls=False
                        )

                        for _ in range(
                            child_count
                        )
                    ],
                ),
                origin="ARCH_RANDOM_SEED",
                birth_generation=generation,
            )

            origin = (
                "ARCH_RANDOM_SEED"
            )

        architecture = (
            ProgramArchitecture(
                main=main,
                birth_generation=generation,
                origin=origin,
            )
        )

        self.program_architecture = (
            architecture
        )

        self.execution_mode = "ARCH"

        if not self._architecture_is_valid():

            self.program_architecture = None

            return

        mutations.append(
            (
                "CREATE_ARCHITECTURE "
                f"origin={origin} "
                f"nodes="
                f"{architecture.total_node_count()} "
                f"functions="
                f"{architecture.function_count()} "
                f"{architecture.main.describe()}"
            )
        )

    def _architecture_create_function(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return

        if (
            architecture.function_count()
            >= MAX_ARCH_FUNCTIONS
        ):
            return

        # ============================================================
        # NEUTRAL FUNCTION INCUBATION
        #
        # Yeni abstraction davranışı rastgele ve büyük bir
        # semantic jump ile başlamaz.
        #
        # Üç identity-equivalent seed:
        #
        #   ADD(0.0)
        #   SUBTRACT(0.0)
        #   MULTIPLY(1.0)
        #
        # Fitness kullanılmaz.
        # Task target kullanılmaz.
        # Function başlangıçta dormant kalır.
        # ============================================================

        seed_type = random.choice(
            (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            )
        )

        if seed_type == "MULTIPLY":

            seed_value = 1.0

        else:

            seed_value = 0.0

        seed_node = ASTNode(
            node_type=seed_type,
            value=seed_value,
        )

        program = ASTProgram(
            root=ASTNode(
                node_type="SEQUENCE",
                children=[
                    seed_node
                ],
            ),
            origin=(
                "ARCH_CREATE_FUNCTION_NEUTRAL"
            ),
            birth_generation=generation,
        )

        function_id = (
            architecture.add_function(
                program=program,
                generation=generation,
                origin=(
                    "EVOLVED_CREATE_NEUTRAL"
                ),
            )
        )

        if not self._architecture_is_valid():

            architecture.remove_function(
                function_id
            )

            return

        mutations.append(
            (
                "ARCH_CREATE_FUNCTION_NEUTRAL "
                f"{function_id} "
                f"seed={seed_type}"
                f"({seed_value}) "
                f"{program.describe()}"
            )
        )

    def _architecture_duplicate_function(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        architecture = (
            self.program_architecture
        )

        if (
            architecture is None
            or not architecture.functions
            or architecture.function_count()
            >= MAX_ARCH_FUNCTIONS
        ):
            return

        source_id = random.choice(
            list(
                architecture
                .functions.keys()
            )
        )

        source = (
            architecture.functions[
                source_id
            ]
        )

        new_id = (
            architecture.add_function(
                program=(
                    source.program.clone()
                ),
                generation=generation,
                origin=(
                    f"DUPLICATED_FROM_"
                    f"{source_id}"
                ),
            )
        )

        if not self._architecture_is_valid():

            architecture.remove_function(
                new_id
            )

            return

        mutations.append(
            (
                "ARCH_DUPLICATE_FUNCTION "
                f"{source_id} -> {new_id}"
            )
        )

    def _architecture_delete_function(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        if (
            architecture is None
            or not architecture.functions
        ):
            return

        referenced: set[str] = set()

        for (
            _name,
            program,
        ) in self._architecture_program_entries():

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_FUNCTION"
                    and node.function_id
                    is not None
                ):

                    referenced.add(
                        node.function_id
                    )

        candidates = [
            function_id

            for function_id
            in architecture.functions

            if function_id
            not in referenced
        ]

        if not candidates:
            return

        function_id = random.choice(
            candidates
        )

        architecture.remove_function(
            function_id
        )

        mutations.append(
            (
                "ARCH_DELETE_FUNCTION "
                f"{function_id}"
            )
        )

    def _architecture_mutate_body(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return

        entries = (
            self._architecture_program_entries()
        )

        if not entries:
            return

        active_entries = (
            self
            ._active_architecture_program_entries()
        )

        active_program_ids = {
            id(program)

            for _, program
            in active_entries
        }

        name, program = random.choice(
            entries
        )

        program_is_active = (
            id(program)
            in active_program_ids
        )

        backup = (
            program.to_dict()
        )

        baseline_outputs = None

        if program_is_active:

            baseline_outputs = (
                self
                ._measure_current_architecture_behavior()
            )

            if baseline_outputs is None:
                return

        nodes = list(
            self._walk_program_nodes(
                program
            )
        )

        mutable_parameters = [
            node

            for node in nodes

            if node.node_type in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
                "IF_CONTEXT",
            )
        ]

        action = random.random()

        # =================================================
        # PARAMETER MUTATION
        #
        # Genel numeric/context mutation davran???na
        # dokunmuyoruz.
        # =================================================

        if (
            action < 0.50
            and mutable_parameters
        ):

            node = random.choice(
                mutable_parameters
            )

            if node.node_type in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            ):

                old = node.value

                node.value += random.gauss(
                    0.0,
                    ARCH_PARAMETER_MUTATION_SCALE,
                )

                description = (
                    f"{node.node_type} "
                    f"{old:.4f} -> "
                    f"{node.value:.4f}"
                )

            else:

                old = node.context

                node.context = random.randint(
                    -1,
                    4,
                )

                description = (
                    "IF_CONTEXT "
                    f"{old} -> "
                    f"{node.context}"
                )

        # =================================================
        # INSERT NODE
        # =================================================

        else:

            sequences = [
                node

                for node in nodes

                if (
                    node.node_type
                    == "SEQUENCE"
                )
            ]

            new_node = (
                self
                ._create_random_architecture_node(
                    allow_function_calls=True
                )
            )

            # Yeni subtree i?inde CALL_FUNCTION var m??
            #
            # _create_random_architecture_node ?u anda
            # yaln?z iki bi?im ?retebilir:
            #
            #   LEAF
            #   IF_CONTEXT(LEAF)
            #
            # Bu y?zden generic genome walker kullanm?yoruz;
            # yaln?z olu?turulan subtree'yi yerel olarak
            # inceliyoruz.

            inserted_nodes = [
                new_node
            ]

            if (
                new_node.node_type
                == "IF_CONTEXT"
            ):

                inserted_nodes.extend(
                    new_node.children
                )

            inserted_function_calls = [
                node

                for node in inserted_nodes

                if (
                    node.node_type
                    == "CALL_FUNCTION"
                )
            ]

            if sequences:

                sequence = random.choice(
                    sequences
                )

                position = random.randint(
                    0,
                    len(sequence.children),
                )

                sequence.children.insert(
                    position,
                    new_node,
                )

                description = (
                    f"INSERT {new_node.describe()}"
                )

            else:

                old_root = (
                    program.root
                )

                program.root = ASTNode(
                    node_type="SEQUENCE",
                    children=[
                        old_root,
                        new_node,
                    ],
                )

                description = (
                    f"WRAP_INSERT "
                    f"{new_node.describe()}"
                )

            # =============================================
            # ACTIVE FUNCTION-ACTIVATION GUARD
            #
            # Sadece aktif phenotype'a eklenen yeni
            # CALL_FUNCTION subtree'leri burada korunur.
            #
            # Dormant body mutation serbesttir.
            # Normal arithmetic/module/macro insertleri
            # bu filtreden ge?mez.
            # =============================================

            if (
                program_is_active
                and inserted_function_calls
            ):

                shock = (
                    self
                    ._activation_semantic_shock(
                        baseline_outputs
                    )
                )

                if not math.isfinite(
                    shock
                ):

                    restored = (
                        ASTProgram.from_dict(
                            backup
                        )
                    )

                    if name == "MAIN":

                        architecture.main = (
                            restored
                        )

                    else:

                        architecture.functions[
                            name
                        ].program = restored

                    return

                accept_probability = (
                    1.0
                    / (
                        1.0
                        + shock
                    )
                )

                if (
                    random.random()
                    > accept_probability
                ):

                    restored = (
                        ASTProgram.from_dict(
                            backup
                        )
                    )

                    if name == "MAIN":

                        architecture.main = (
                            restored
                        )

                    else:

                        architecture.functions[
                            name
                        ].program = restored

                    return

                description += (
                    " "
                    f"GENTLE_FUNCTION_ACTIVATION "
                    f"shock={shock:.12f} "
                    f"accept_p="
                    f"{accept_probability:.12f}"
                )

        if not self._architecture_is_valid():

            restored = (
                ASTProgram.from_dict(
                    backup
                )
            )

            if name == "MAIN":

                architecture.main = (
                    restored
                )

            else:

                architecture.functions[
                    name
                ].program = restored

            return

        mutations.append(
            (
                "ARCH_BODY_MUTATION "
                f"{name} "
                f"{description}"
            )
        )


    def _activation_probe_cases(
        self,
    ) -> tuple[tuple[float, int], ...]:

        # V1.2.0G ? Target-free semantic probes.
        #
        # Bunlar task target veya fitness bilgisi de?ildir.
        # Sadece mevcut program davran???n?n bir mutation
        # taraf?ndan ne kadar de?i?tirildi?ini ?l?mek i?in
        # sabit davran?? ?rnekleridir.

        inputs = (
            -8.0,
            -4.0,
            -2.0,
            0.0,
            2.0,
            4.0,
            8.0,
        )

        contexts = (
            0,
            1,
            2,
        )

        return tuple(
            (
                input_value,
                context_id,
            )

            for context_id in contexts

            for input_value in inputs
        )


    def _measure_current_architecture_behavior(
        self,
    ) -> list[float] | None:

        if (
            self.program_architecture
            is None
        ):
            return None

        outputs: list[float] = []

        try:

            for (
                input_value,
                context_id,
            ) in self._activation_probe_cases():

                output = (
                    self.execute_program_architecture(
                        input_value,
                        context_id,
                    )
                )

                if not math.isfinite(
                    output
                ):
                    return None

                outputs.append(
                    float(output)
                )

        except (
            RuntimeError,
            ValueError,
            OverflowError,
            ZeroDivisionError,
        ):

            return None

        return outputs


    def _activation_semantic_shock(
        self,
        baseline_outputs: list[float],
    ) -> float:

        candidate_outputs = (
            self
            ._measure_current_architecture_behavior()
        )

        if (
            candidate_outputs is None
            or
            len(candidate_outputs)
            != len(baseline_outputs)
        ):

            return float("inf")

        shifts = [
            abs(
                candidate
                - baseline
            )

            for baseline, candidate
            in zip(
                baseline_outputs,
                candidate_outputs,
            )
        ]

        if not shifts:
            return float("inf")

        return (
            sum(shifts)
            / len(shifts)
        )


    def _architecture_insert_function_call(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        if (
            architecture is None
            or not architecture.functions
        ):
            return

        baseline_outputs = (
            self
            ._measure_current_architecture_behavior()
        )

        if baseline_outputs is None:
            return

        sequences: list[
            tuple[str, ASTNode]
        ] = []

        for (
            name,
            program,
        ) in (
            self
            ._active_architecture_program_entries()
        ):

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "SEQUENCE"
                ):

                    sequences.append(
                        (
                            name,
                            node,
                        )
                    )

        if not sequences:
            return

        function_ids = sorted(
            architecture.functions.keys()
        )

        if not function_ids:
            return

        # ============================================================
        # BUILD CONTEXT-GATED ACTIVATION SEARCH SPACE
        # ============================================================

        context_ids = [
            0,
            1,
            2,
        ]

        search_space = []

        for (
            name,
            parent,
        ) in sequences:

            for target_id in function_ids:

                for context_id in context_ids:

                    for position in range(
                        len(parent.children) + 1
                    ):

                        search_space.append(
                            (
                                name,
                                parent,
                                target_id,
                                context_id,
                                position,
                            )
                        )

        if not search_space:
            return

        total_search_space = len(
            search_space
        )

        max_candidates = 128

        if (
            total_search_space
            <= max_candidates
        ):

            candidate_specs = (
                search_space
            )

            search_mode = (
                "EXHAUSTIVE"
            )

        else:

            candidate_specs = []

            # Her function en az bir kez temsil edilsin.
            for target_id in function_ids:

                matching = [
                    item

                    for item
                    in search_space

                    if item[2]
                    == target_id
                ]

                if matching:

                    candidate_specs.append(
                        random.choice(
                            matching
                        )
                    )

            remaining = (
                max_candidates
                - len(candidate_specs)
            )

            if remaining > 0:

                selected_keys = {
                    (
                        item[0],
                        id(item[1]),
                        item[2],
                        item[3],
                        item[4],
                    )

                    for item
                    in candidate_specs
                }

                pool = [
                    item

                    for item
                    in search_space

                    if (
                        item[0],
                        id(item[1]),
                        item[2],
                        item[3],
                        item[4],
                    )
                    not in selected_keys
                ]

                if pool:

                    candidate_specs.extend(
                        random.sample(
                            pool,
                            k=min(
                                remaining,
                                len(pool),
                            ),
                        )
                    )

            search_mode = (
                "STRATIFIED"
            )

        # ============================================================
        # MEASURE FULL-PROGRAM SEMANTIC SHOCK
        # ============================================================

        candidates = []

        for (
            name,
            parent,
            target_id,
            context_id,
            position,
        ) in candidate_specs:

            call_node = ASTNode(
                node_type="CALL_FUNCTION",
                function_id=target_id,
            )

            gated_node = ASTNode(
                node_type="IF_CONTEXT",
                context=context_id,
                children=[
                    call_node
                ],
            )

            parent.children.insert(
                position,
                gated_node,
            )

            valid = (
                self._architecture_is_valid()
            )

            if valid:

                shock = (
                    self
                    ._activation_semantic_shock(
                        baseline_outputs
                    )
                )

            else:

                shock = float(
                    "inf"
                )

            del parent.children[
                position
            ]

            if not math.isfinite(
                shock
            ):
                continue

            candidates.append(
                {
                    "name":
                        name,

                    "parent":
                        parent,

                    "position":
                        position,

                    "target_id":
                        target_id,

                    "context_id":
                        context_id,

                    "shock":
                        shock,
                }
            )

        if not candidates:
            return

        min_shock = min(
            candidate["shock"]
            for candidate
            in candidates
        )

        # ============================================================
        # SOFT GENTLE SELECTION
        #
        # Fitness yok.
        # Task target yok.
        # Hard threshold yok.
        # ============================================================

        weights = [
            1.0
            / (
                (
                    1.0
                    + candidate["shock"]
                )
                ** 2
            )

            for candidate
            in candidates
        ]

        selected = random.choices(
            candidates,
            weights=weights,
            k=1,
        )[0]

        call_node = ASTNode(
            node_type="CALL_FUNCTION",
            function_id=(
                selected[
                    "target_id"
                ]
            ),
        )

        gated_node = ASTNode(
            node_type="IF_CONTEXT",
            context=(
                selected[
                    "context_id"
                ]
            ),
            children=[
                call_node
            ],
        )

        selected[
            "parent"
        ].children.insert(
            selected[
                "position"
            ],
            gated_node,
        )

        if not self._architecture_is_valid():

            del selected[
                "parent"
            ].children[
                selected[
                    "position"
                ]
            ]

            return

        mutations.append(
            (
                "ARCH_INSERT_CALL_CONTEXT_GENTLE "
                f"{selected['name']} "
                f"-> {selected['target_id']} "
                f"context="
                f"{selected['context_id']} "
                f"position="
                f"{selected['position']} "
                f"shock="
                f"{selected['shock']:.12f} "
                f"min_shock="
                f"{min_shock:.12f} "
                f"tested="
                f"{len(candidates)} "
                f"space="
                f"{total_search_space} "
                f"mode="
                f"{search_mode}"
            )
        )


    def _architecture_retarget_function_call(
        self,
        mutations: list[str],
    ) -> None:

        architecture = (
            self.program_architecture
        )

        if (
            architecture is None
            or len(
                architecture.functions
            ) < 2
        ):
            return

        all_entries = (
            self._architecture_program_entries()
        )

        active_entries = (
            self
            ._active_architecture_program_entries()
        )

        active_program_ids = {
            id(program)

            for _, program
            in active_entries
        }

        calls: list[
            tuple[
                str,
                ASTProgram,
                ASTNode,
                bool,
            ]
        ] = []

        for (
            name,
            program,
        ) in all_entries:

            program_is_active = (
                id(program)
                in active_program_ids
            )

            for node in (
                self._walk_program_nodes(
                    program
                )
            ):

                if (
                    node.node_type
                    == "CALL_FUNCTION"
                    and
                    node.function_id
                    is not None
                ):

                    calls.append(
                        (
                            name,
                            program,
                            node,
                            program_is_active,
                        )
                    )

        if not calls:
            return

        (
            name,
            program,
            node,
            program_is_active,
        ) = random.choice(
            calls
        )

        old_target = (
            node.function_id
        )

        target_ids = [
            function_id

            for function_id
            in architecture.functions

            if (
                function_id
                != old_target
            )
        ]

        if not target_ids:
            return

        # =============================================
        # DORMANT RETARGET
        #
        # Phenotype'a ba?l? de?ilse serbest?e
        # retarget edilir. Daha sonra function
        # aktive olursa G7 full-program guard
        # devreye girecektir.
        # =============================================

        if not program_is_active:

            new_target = random.choice(
                target_ids
            )

            node.function_id = (
                new_target
            )

            if not self._architecture_is_valid():

                node.function_id = (
                    old_target
                )

                return

            mutations.append(
                (
                    "ARCH_RETARGET_CALL_DORMANT "
                    f"{name}: "
                    f"{old_target} -> "
                    f"{new_target}"
                )
            )

            return

        # =============================================
        # ACTIVE RETARGET
        #
        # Baseline = mevcut phenotype.
        # Her alternatif target ge?ici denenir.
        # Fitness / task target kullan?lmaz.
        # =============================================

        baseline_outputs = (
            self
            ._measure_current_architecture_behavior()
        )

        if baseline_outputs is None:
            return

        candidates = []

        for new_target in target_ids:

            node.function_id = (
                new_target
            )

            if not self._architecture_is_valid():

                node.function_id = (
                    old_target
                )

                continue

            shock = (
                self
                ._activation_semantic_shock(
                    baseline_outputs
                )
            )

            node.function_id = (
                old_target
            )

            if not math.isfinite(
                shock
            ):
                continue

            candidates.append(
                {
                    "target":
                        new_target,

                    "shock":
                        shock,
                }
            )

        node.function_id = (
            old_target
        )

        if not candidates:
            return

        min_shock = min(
            candidate["shock"]

            for candidate
            in candidates
        )

        # %80 gentle, %20 exploration.
        # High-shock targetlar tamamen yasaklanmaz.

        if random.random() < 0.20:

            selected = random.choice(
                candidates
            )

            selection_mode = (
                "EXPLORE"
            )

        else:

            weights = [
                1.0
                / (
                    (
                        1.0
                        + candidate["shock"]
                    )
                    ** 2
                )

                for candidate
                in candidates
            ]

            selected = random.choices(
                candidates,
                weights=weights,
                k=1,
            )[0]

            selection_mode = (
                "GENTLE"
            )

        node.function_id = (
            selected["target"]
        )

        if not self._architecture_is_valid():

            node.function_id = (
                old_target
            )

            return

        mutations.append(
            (
                "ARCH_RETARGET_CALL_GENTLE "
                f"{name}: "
                f"{old_target} -> "
                f"{selected['target']} "
                f"shock="
                f"{selected['shock']:.12f} "
                f"min_shock="
                f"{min_shock:.12f} "
                f"candidates="
                f"{len(candidates)} "
                f"selection="
                f"{selection_mode}"
            )
        )


    def _mutate_architecture(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        roll = random.random()

        boundary = (
            ARCH_CREATE_FUNCTION_WEIGHT
        )

        if roll < boundary:

            self._architecture_create_function(
                mutations,
                generation,
            )

            return

        boundary += (
            ARCH_DUPLICATE_FUNCTION_WEIGHT
        )

        if roll < boundary:

            self._architecture_duplicate_function(
                mutations,
                generation,
            )

            return

        boundary += (
            ARCH_DELETE_FUNCTION_WEIGHT
        )

        if roll < boundary:

            self._architecture_delete_function(
                mutations
            )

            return

        boundary += (
            ARCH_BODY_MUTATION_WEIGHT
        )

        if roll < boundary:

            self._architecture_mutate_body(
                mutations
            )

            return

        boundary += (
            ARCH_INSERT_CALL_WEIGHT
        )

        if roll < boundary:

            self._architecture_insert_function_call(
                mutations
            )

            return

        self._architecture_retarget_function_call(
            mutations
        )

    # ---------------------------------------------------------
    # MUTATION
    # ---------------------------------------------------------

    def mutate(
        self,
        generation: int,
    ) -> list[str]:

        mutations: list[str] = []

        # =================================================
        # V0.9 — ARCHITECTURE REPRESENTATION
        # =================================================

        if (
            self.program_architecture
            is None
        ):

            self._maybe_create_architecture(
                mutations,
                generation,
            )

            # Architecture bu doğumda oluştuysa
            # başka mutation yapma.
            if (
                self.program_architecture
                is not None
            ):

                return mutations

        # =================================================
        # EXISTING ARCHITECTURE ORGANISM
        # =================================================

        if (
            self.execution_mode
            == "ARCH"
        ):

            mutate_language = (
                random.random()
                < LANGUAGE_MUTATION_SHARE
            )

            if mutate_language:

                self._mutate_evolved_language(
                    mutations,
                    generation,
                )

            else:

                self._mutate_architecture(
                    mutations,
                    generation,
                )

            if not mutations:

                mutations.append(
                    "NO_MUTATION"
                )

            return mutations

        # =================================================
        # PHASE 1 — REPRESENTATION BIRTH
        # =================================================

        if self.ast_program is None:

            self._maybe_create_ast(
                mutations,
                generation,
            )

            # AST bu doğumda ilk kez oluştuysa
            # representation mutation tek başına kalır.
            if self.ast_program is not None:

                return mutations

            # ---------------------------------------------
            # NORMAL DSL EVOLUTION
            # ---------------------------------------------

            self._mutate_main_program(
                mutations
            )

            self._mutate_existing_module(
                mutations,
                generation,
            )

            self._maybe_create_module(
                mutations,
                generation,
            )

            self._maybe_duplicate_module(
                mutations,
                generation,
            )

            self._maybe_create_composite_module(
                mutations,
                generation,
            )

            self._maybe_create_macro(
                mutations,
                generation,
            )

            self._maybe_duplicate_module_call(
                mutations
            )

            self._maybe_delete_unused_module(
                mutations
            )

            self._maybe_delete_unused_macro(
                mutations
            )

            if not mutations:

                mutations.append(
                    "NO_MUTATION"
                )

            return mutations

        # =================================================
        # PHASE 2 — EXISTING AST ORGANISM
        #
        # Tek child içinde tek mutation domain.
        # =================================================

        mutate_ast_structure = (
            random.random()
            < AST_STRUCTURE_MUTATION_SHARE
        )

        # -------------------------------------------------
        # DOMAIN A — AST STRUCTURE
        # -------------------------------------------------

        if mutate_ast_structure:

            self._mutate_ast_structure(
                mutations
            )

        # -------------------------------------------------
        # DOMAIN B — LEGACY / SUPPORT SYSTEM
        # -------------------------------------------------

        else:

            uses_legacy = (
                self.ast_uses_legacy_main()
            )

            # Pure AST artık MAIN kullanmıyorsa,
            # dormant MAIN'i boş yere mutate etmiyoruz.
            if uses_legacy:

                self._mutate_main_program(
                    mutations
                )

            # Modules/macros AST tarafından da
            # çağrılabildiği için yaşamaya devam eder.
            self._mutate_existing_module(
                mutations,
                generation,
            )

            self._maybe_duplicate_module(
                mutations,
                generation,
            )

            self._maybe_create_composite_module(
                mutations,
                generation,
            )

            self._maybe_create_macro(
                mutations,
                generation,
            )

            self._maybe_delete_unused_module(
                mutations
            )

            self._maybe_delete_unused_macro(
                mutations
            )

        if not mutations:

            mutations.append(
                "NO_MUTATION"
            )

        return mutations

    def _mutate_main_program(
        self,
        mutations: list[str],
    ) -> None:

        # Parameter mutation
        for index, instruction in enumerate(
            self.instructions
        ):

            if (
                random.random()
                >= MUTATION_RATE
            ):
                continue

            if instruction.operation in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            ):

                old_value = (
                    instruction.value
                )

                instruction.value += (
                    random.gauss(
                        0.0,
                        PARAMETER_MUTATION_SCALE,
                    )
                )

                mutations.append(
                    f"MAIN_PARAM[{index}] "
                    f"{old_value:.4f} -> "
                    f"{instruction.value:.4f}"
                )

            elif (
                instruction.operation
                == "JUMP_IF_CONTEXT_NE"
            ):

                if random.random() < 0.5:

                    old = instruction.context

                    instruction.context = (
                        random.randint(
                            -1,
                            4,
                        )
                    )

                    mutations.append(
                        f"MAIN_CONTEXT[{index}] "
                        f"{old} -> "
                        f"{instruction.context}"
                    )

                else:

                    old = instruction.offset

                    instruction.offset = (
                        random.randint(
                            1,
                            5,
                        )
                    )

                    mutations.append(
                        f"MAIN_OFFSET[{index}] "
                        f"{old} -> "
                        f"{instruction.offset}"
                    )

            elif instruction.operation == "JUMP":

                old = instruction.offset

                instruction.offset = (
                    random.randint(
                        1,
                        5,
                    )
                )

                mutations.append(
                    f"MAIN_OFFSET[{index}] "
                    f"{old} -> "
                    f"{instruction.offset}"
                )

            elif (
                instruction.operation
                == "CALL_MODULE"
                and self.modules
            ):

                if random.random() < 0.25:

                    old = (
                        instruction.module_id
                    )

                    instruction.module_id = (
                        random.choice(
                            list(
                                self.modules.keys()
                            )
                        )
                    )

                    mutations.append(
                        f"MODULE_TARGET[{index}] "
                        f"M{old} -> "
                        f"M{instruction.module_id}"
                    )

        # Replace
        if (
            self.instructions
            and random.random()
            < MUTATION_RATE * 0.30
        ):

            index = random.randrange(
                len(self.instructions)
            )

            old = self.instructions[index]

            new = (
                self.create_random_main_instruction()
            )

            self.instructions[index] = new

            mutations.append(
                f"MAIN_REPLACE[{index}] "
                f"{old.describe()} -> "
                f"{new.describe()}"
            )

        # Insert
        if (
            len(self.instructions)
            < MAX_GENOME_LENGTH
            and random.random()
            < MUTATION_RATE * 0.45
        ):

            instruction = (
                self.create_random_main_instruction()
            )

            position = random.randint(
                0,
                len(self.instructions),
            )

            self.instructions.insert(
                position,
                instruction,
            )

            mutations.append(
                f"MAIN_INSERT[{position}] "
                f"{instruction.describe()}"
            )

        # Delete
        if (
            len(self.instructions)
            > MIN_GENOME_LENGTH
            and random.random()
            < MUTATION_RATE * 0.15
        ):

            position = random.randrange(
                len(self.instructions)
            )

            deleted = (
                self.instructions[position]
            )

            del self.instructions[
                position
            ]

            mutations.append(
                f"MAIN_DELETE[{position}] "
                f"{deleted.describe()}"
            )

        # Block duplication
        if (
            len(self.instructions) >= 2
            and len(self.instructions)
            < MAX_GENOME_LENGTH
            and random.random()
            < MUTATION_RATE * 0.12
        ):

            start = random.randrange(
                len(self.instructions)
            )

            max_block = min(
                3,
                len(self.instructions) - start,
            )

            block_length = random.randint(
                1,
                max_block,
            )

            block = [
                instruction.copy()
                for instruction
                in self.instructions[
                    start:
                    start + block_length
                ]
            ]

            available = (
                MAX_GENOME_LENGTH
                - len(self.instructions)
            )

            block = block[:available]

            if block:

                insert_at = random.randint(
                    0,
                    len(self.instructions),
                )

                self.instructions[
                    insert_at:insert_at
                ] = block

                mutations.append(
                    f"MAIN_DUPLICATE_BLOCK "
                    f"start={start} "
                    f"length={len(block)} "
                    f"insert={insert_at}"
                )

    # ---------------------------------------------------------
    # MODULE CREATION
    # ---------------------------------------------------------

    def _maybe_create_module(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        # İlk proto-module mekanizması.
        # Ana programdaki 2-4 instruction'lık bir blok
        # ayrı modüle taşınır ve yerine CALL_MODULE gelir.

        if (
            len(self.instructions) < 3
            or len(self.modules) >= MAX_MODULES
            or random.random()
            >= MUTATION_RATE * 0.10
        ):
            return

        start = random.randrange(
            len(self.instructions) - 1
        )

        max_length = min(
            4,
            len(self.instructions) - start,
        )

        block_length = random.randint(
            2,
            max_length,
        )

        block = self.instructions[
            start:
            start + block_length
        ]

        # İlk sürümde modül içinde başka modül çağrısı
        # olmasına izin vermiyoruz.
        if any(
            instruction.operation
            == "CALL_MODULE"
            for instruction in block
        ):
            return

        module_id = (
            self.next_module_id
        )

        self.next_module_id += 1

        self.modules[module_id] = [
            instruction.copy()
            for instruction in block
        ]

        module_uid = (
            self._new_module_uid()
        )

        self.module_meta[
            module_id
        ] = {
            "uid":
                module_uid,

            "parent_uid":
                None,

            "birth_generation":
                generation,

            "origin":
                "EXTRACTION",
        }

        self.instructions[
            start:
            start + block_length
        ] = [
            Instruction(
                operation="CALL_MODULE",
                module_id=module_id,
            )
        ]

        mutations.append(
            f"CREATE_MODULE "
            f"M{module_id:03d} "
            f"{module_uid} "
            f"from main[{start}:"
            f"{start + block_length}]"
        )

    def _branch_module_lineage(
        self,
        module_id: int,
        generation: int,
        mutations: list[str],
    ) -> None:

        old_meta = (
            self.module_meta.get(
                module_id
            )
        )

        if old_meta is None:

            old_uid = None

        else:

            old_uid = (
                old_meta["uid"]
            )

        new_uid = (
            self._new_module_uid()
        )

        self.module_meta[
            module_id
        ] = {
            "uid":
                new_uid,

            "parent_uid":
                old_uid,

            "birth_generation":
                generation,

            "origin":
                "MUTATION",
        }

        mutations.append(
            f"MODULE_LINEAGE "
            f"{old_uid} -> "
            f"{new_uid}"
        )

    # ---------------------------------------------------------
    # MODULE MUTATION
    # ---------------------------------------------------------

    def _mutate_existing_module(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        if (
            not self.modules
            or random.random()
            >= MUTATION_RATE * 0.35
        ):
            return

        module_id = random.choice(
            list(
                self.modules.keys()
            )
        )

        module = self.modules[
            module_id
        ]

        if not module:
            return

        mutation_type = random.choice(
            (
                "PARAM",
                "REPLACE",
                "INSERT",
                "DELETE",
            )
        )

        self._branch_module_lineage(
            module_id,
            generation,
            mutations,
        )

        if mutation_type == "PARAM":

            index = random.randrange(
                len(module)
            )

            instruction = module[index]

            if instruction.operation in (
                "ADD",
                "SUBTRACT",
                "MULTIPLY",
            ):

                old = instruction.value

                instruction.value += (
                    random.gauss(
                        0.0,
                        PARAMETER_MUTATION_SCALE,
                    )
                )

                mutations.append(
                    f"M{module_id:03d}_PARAM"
                    f"[{index}] "
                    f"{old:.4f} -> "
                    f"{instruction.value:.4f}"
                )

            elif instruction.operation == (
                "JUMP_IF_CONTEXT_NE"
            ):

                old = (
                    instruction.context
                )

                instruction.context = (
                    random.randint(
                        -1,
                        4,
                    )
                )

                mutations.append(
                    f"M{module_id:03d}_CONTEXT"
                    f"[{index}] "
                    f"{old} -> "
                    f"{instruction.context}"
                )

            elif instruction.operation == "JUMP":

                old = instruction.offset

                instruction.offset = (
                    random.randint(
                        1,
                        5,
                    )
                )

                mutations.append(
                    f"M{module_id:03d}_OFFSET"
                    f"[{index}] "
                    f"{old} -> "
                    f"{instruction.offset}"
                )

            elif (
                instruction.operation
                == "CALL_MODULE"
            ):

                possible_targets = [
                    candidate_id

                    for candidate_id
                    in self.modules

                    if (
                        candidate_id
                        < module_id
                    )
                ]

                if (
                    possible_targets
                    and random.random()
                    < MODULE_CALL_MUTATION_RATE
                ):

                    old = (
                        instruction.module_id
                    )

                    instruction.module_id = (
                        random.choice(
                            possible_targets
                        )
                    )

                    mutations.append(
                        (
                            f"M{module_id:03d}_CALL_TARGET"
                            f"[{index}] "
                            f"M{old:03d} -> "
                            f"M{instruction.module_id:03d}"
                        )
                    )

        elif mutation_type == "REPLACE":

            index = random.randrange(
                len(module)
            )

            old = module[index]

            possible_targets = [
                candidate_id

                for candidate_id
                in self.modules

                if (
                    candidate_id
                    < module_id
                )
            ]

            if (
                possible_targets
                and random.random() < 0.25
            ):

                new = Instruction(
                    operation="CALL_MODULE",
                    module_id=(
                        random.choice(
                            possible_targets
                        )
                    ),
                )

            else:

                new = (
                    self.create_random_primitive()
                )

            module[index] = new

            mutations.append(
                f"M{module_id:03d}_REPLACE"
                f"[{index}] "
                f"{old.describe()} -> "
                f"{new.describe()}"
            )

        elif mutation_type == "INSERT":

            if (
                len(module)
                >= MAX_MODULE_LENGTH
            ):
                return

            position = random.randint(
                0,
                len(module),
            )

            possible_targets = [
                candidate_id

                for candidate_id
                in self.modules

                if (
                    candidate_id
                    < module_id
                )
            ]

            if (
                possible_targets
                and random.random() < 0.30
            ):

                new = Instruction(
                    operation="CALL_MODULE",
                    module_id=(
                        random.choice(
                            possible_targets
                        )
                    ),
                )

            else:

                new = (
                    self.create_random_primitive()
                )

            module.insert(
                position,
                new,
            )

            mutations.append(
                f"M{module_id:03d}_INSERT"
                f"[{position}] "
                f"{new.describe()}"
            )

        elif mutation_type == "DELETE":

            if len(module) <= 1:
                return

            position = random.randrange(
                len(module)
            )

            old = module[position]

            del module[position]

            mutations.append(
                f"M{module_id:03d}_DELETE"
                f"[{position}] "
                f"{old.describe()}"
            )

    # ---------------------------------------------------------
    # HIERARCHICAL MODULE COMPOSITION
    # ---------------------------------------------------------

    def _maybe_create_composite_module(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:
        """
        MAIN içindeki ardışık CALL_MODULE bloklarını
        daha yüksek seviyeli tek bir modül halinde
        paketleyebilir.

        Örnek:

        MAIN[
            CALL M001
            CALL M004
            CALL M002
        ]

        ->

        M007[
            CALL M001
            CALL M004
            CALL M002
        ]

        MAIN[
            CALL M007
        ]

        Yeni modül yalnızca kendisinden daha eski
        modülleri çağırdığı için dependency graph
        yönlü ve cycle-free kalır.
        """

        if (
            len(self.modules) < 2
            or len(self.modules) >= MAX_MODULES
            or random.random()
            >= COMPOSITE_MODULE_RATE
        ):
            return

        # MAIN içinde ardışık CALL_MODULE
        # dizilerini bul.
        runs: list[
            tuple[int, int]
        ] = []

        start: int | None = None

        for index, instruction in enumerate(
            self.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
            ):

                if start is None:
                    start = index

            else:

                if start is not None:

                    length = (
                        index - start
                    )

                    if length >= 2:
                        runs.append(
                            (
                                start,
                                length,
                            )
                        )

                    start = None

        if start is not None:

            length = (
                len(self.instructions)
                - start
            )

            if length >= 2:

                runs.append(
                    (
                        start,
                        length,
                    )
                )

        if not runs:
            return

        run_start, run_length = (
            random.choice(
                runs
            )
        )

        max_length = min(
            run_length,
            4,
            MAX_MODULE_LENGTH,
        )

        block_length = random.randint(
            2,
            max_length,
        )

        if run_length > block_length:

            block_start = random.randint(
                run_start,
                (
                    run_start
                    + run_length
                    - block_length
                ),
            )

        else:

            block_start = run_start

        block = [
            instruction.copy()

            for instruction
            in self.instructions[
                block_start:
                block_start
                + block_length
            ]
        ]

        # Güvenlik: bütün çağrılan modüller
        # gerçekten mevcut olmalı.
        referenced_ids = [
            instruction.module_id

            for instruction
            in block

            if (
                instruction.operation
                == "CALL_MODULE"
            )
        ]

        if (
            not referenced_ids
            or any(
                module_id is None
                or module_id
                not in self.modules

                for module_id
                in referenced_ids
            )
        ):
            return

        new_id = (
            self.next_module_id
        )

        self.next_module_id += 1

        # Yeni ID tüm eski modüllerden büyük.
        # Dolayısıyla M_new -> M_old ilişkisi
        # cycle yaratamaz.
        self.modules[
            new_id
        ] = block

        new_uid = (
            self._new_module_uid()
        )

        parent_uids = []

        for module_id in referenced_ids:

            metadata = (
                self.module_meta.get(
                    module_id
                )
            )

            if metadata is not None:

                parent_uids.append(
                    metadata[
                        "uid"
                    ]
                )

        self.module_meta[
            new_id
        ] = {
            "uid":
                new_uid,

            "parent_uid":
                None,

            "parent_uids":
                parent_uids,

            "birth_generation":
                generation,

            "origin":
                "COMPOSITION",
        }

        mutations.append(
            (
                f"CREATE_COMPOSITE_MODULE "
                f"M{new_id:03d} "
                f"{new_uid} "
                f"calls="
                + ",".join(
                    f"M{module_id:03d}"
                    for module_id
                    in referenced_ids
                )
            )
        )

        # Çoğu zaman abstraction gerçekten
        # MAIN tarafından kullanılmaya başlasın.
        if (
            random.random()
            < COMPOSITE_REPLACEMENT_CHANCE
        ):

            self.instructions[
                block_start:
                block_start
                + block_length
            ] = [
                Instruction(
                    operation="CALL_MODULE",
                    module_id=new_id,
                )
            ]

            mutations.append(
                (
                    f"ABSTRACT_MAIN_BLOCK "
                    f"[{block_start}:"
                    f"{block_start + block_length}] "
                    f"-> M{new_id:03d}"
                )
            )

    # ---------------------------------------------------------
    # EVOLVED VOCABULARY
    # ---------------------------------------------------------

    def _maybe_create_macro(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:
        """
        Aktif ve hierarchical bir module body,
        yeni atomik vocabulary item'ına dönüşebilir.

        Macro'nun anlamını insan belirlemez.
        İçerik mevcut evrimsel koddan alınır.

        CALL_MACRO daha sonra tek instruction olarak
        mutasyonlarda yeniden kullanılabilir.
        """

        if (
            not self.modules
            or len(self.macros) >= MAX_MACROS
            or random.random()
            >= MACRO_CREATION_RATE
        ):
            return

        # Önce MAIN tarafından erişilebilen
        # modülleri buluyoruz.
        reachable: set[int] = set()

        stack = [
            instruction.module_id

            for instruction
            in self.instructions

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                in self.modules
            )
        ]

        while stack:

            module_id = stack.pop()

            if (
                module_id is None
                or module_id in reachable
            ):
                continue

            reachable.add(
                module_id
            )

            for instruction in (
                self.modules[
                    module_id
                ]
            ):

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    in self.modules
                ):

                    stack.append(
                        instruction.module_id
                    )

        # İlk macro adayları özellikle
        # composite/hierarchical modüller olsun.
        candidates = []

        for module_id in reachable:

            body = (
                self.modules[
                    module_id
                ]
            )

            if (
                len(body) < 2
                or len(body)
                > MAX_MACRO_LENGTH
            ):
                continue

            has_abstraction = any(
                instruction.operation
                in (
                    "CALL_MODULE",
                    "CALL_MACRO",
                )

                for instruction in body
            )

            if not has_abstraction:
                continue

            candidates.append(
                module_id
            )

        if not candidates:
            return

        source_module_id = (
            random.choice(
                candidates
            )
        )

        source_body = (
            self.modules[
                source_module_id
            ]
        )

        macro_id = (
            self.next_macro_id
        )

        self.next_macro_id += 1

        macro_uid = (
            self._new_macro_uid()
        )

        self.macros[
            macro_id
        ] = [
            instruction.copy()

            for instruction
            in source_body
        ]

        source_meta = (
            self.module_meta.get(
                source_module_id,
                {}
            )
        )

        self.macro_meta[
            macro_id
        ] = {
            "uid":
                macro_uid,

            "source_module_id":
                source_module_id,

            "source_module_uid":
                source_meta.get(
                    "uid"
                ),

            "birth_generation":
                generation,

            "origin":
                "PROMOTED_ABSTRACTION",
        }

        mutations.append(
            (
                f"CREATE_MACRO "
                f"K{macro_id:03d} "
                f"{macro_uid} "
                f"from M{source_module_id:03d}"
            )
        )

        # -----------------------------------------------------
        # TRUE VOCABULARY PROMOTION
        # -----------------------------------------------------
        #
        # Macro sadece source module'un bir kopyası olarak
        # kalmamalı. Aksi halde aynı davranış için iki ayrı
        # body saklanır ve complexity penalty oluşur.
        #
        # Bu nedenle bütün source-module referanslarını
        # yeni macro'ya çeviriyoruz ve eski module'u
        # genomdan kaldırıyoruz.
        #
        # Semantik:
        #
        #     CALL_MODULE M007
        #
        # ->
        #
        #     CALL_MACRO K001
        #
        # M007 body ise artık K001 body'dir.

        if (
            random.random()
            >= MACRO_REPLACEMENT_CHANCE
        ):
            return

        replacements = 0

        # MAIN references
        for instruction in (
            self.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                == source_module_id
            ):

                instruction.operation = (
                    "CALL_MACRO"
                )

                instruction.macro_id = (
                    macro_id
                )

                instruction.module_id = (
                    None
                )

                replacements += 1

        # MODULE -> source references
        for (
            owner_id,
            module,
        ) in self.modules.items():

            if (
                owner_id
                == source_module_id
            ):
                continue

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    == source_module_id
                ):

                    instruction.operation = (
                        "CALL_MACRO"
                    )

                    instruction.macro_id = (
                        macro_id
                    )

                    instruction.module_id = (
                        None
                    )

                    replacements += 1

        # Existing MACRO -> source references
        for (
            owner_macro_id,
            macro,
        ) in self.macros.items():

            if (
                owner_macro_id
                == macro_id
            ):
                continue

            for instruction in macro:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    == source_module_id
                ):

                    instruction.operation = (
                        "CALL_MACRO"
                    )

                    instruction.macro_id = (
                        macro_id
                    )

                    instruction.module_id = (
                        None
                    )

                    replacements += 1

        # AST -> source references
        if self.ast_program is not None:

            for node in self._walk_ast_nodes():

                if (
                    node.node_type
                    == "CALL_MODULE"
                    and node.module_id
                    == source_module_id
                ):

                    node.node_type = (
                        "CALL_MACRO"
                    )

                    node.macro_id = (
                        macro_id
                    )

                    node.module_id = None

                    replacements += 1

        # Promotion ancak source module gerçekten
        # kullanılıyorsa anlamlı.
        if replacements == 0:

            del self.macros[
                macro_id
            ]

            del self.macro_meta[
                macro_id
            ]

            return

        source_uid = (
            source_meta.get(
                "uid"
            )
        )

        # Body artık macro tarafından sahipleniliyor.
        # Eski module temsilini kaldırıyoruz.
        del self.modules[
            source_module_id
        ]

        if (
            source_module_id
            in self.module_meta
        ):

            del self.module_meta[
                source_module_id
            ]

        mutations.append(
            (
                f"PROMOTE_MODULE_TO_MACRO "
                f"M{source_module_id:03d} "
                f"({source_uid}) "
                f"-> K{macro_id:03d} "
                f"replacements={replacements}"
            )
        )

    def _maybe_duplicate_module(
        self,
        mutations: list[str],
        generation: int,
    ) -> None:

        if (
            not self.modules
            or len(self.modules) >= MAX_MODULES
            or random.random()
            >= MUTATION_RATE * 0.08
        ):
            return

        source_id = random.choice(
            list(
                self.modules.keys()
            )
        )

        new_id = self.next_module_id
        self.next_module_id += 1

        self.modules[new_id] = [
            instruction.copy()
            for instruction
            in self.modules[source_id]
        ]

        source_meta = (
            self.module_meta.get(
                source_id
            )
        )

        parent_uid = (
            source_meta["uid"]
            if source_meta
            else None
        )

        new_uid = (
            self._new_module_uid()
        )

        self.module_meta[
            new_id
        ] = {
            "uid":
                new_uid,

            "parent_uid":
                parent_uid,

            "birth_generation":
                generation,

            "origin":
                "DUPLICATION",
        }

        mutations.append(
            f"DUPLICATE_MODULE "
            f"M{source_id:03d} "
            f"({parent_uid}) -> "
            f"M{new_id:03d} "
            f"({new_uid})"
        )

        # Bazen ana programdaki bir çağrı
        # yeni kopyaya yönlendirilir.
        call_positions = [
            index
            for index, instruction
            in enumerate(
                self.instructions
            )
            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                == source_id
            )
        ]

        if (
            call_positions
            and random.random() < 0.60
        ):

            position = random.choice(
                call_positions
            )

            self.instructions[
                position
            ].module_id = new_id

            mutations.append(
                f"RETARGET_CALL[{position}] "
                f"M{source_id:03d} -> "
                f"M{new_id:03d}"
            )

    def _maybe_duplicate_module_call(
        self,
        mutations: list[str],
    ) -> None:

        call_positions = [
            index
            for index, instruction
            in enumerate(
                self.instructions
            )
            if instruction.operation
            == "CALL_MODULE"
        ]

        if (
            not call_positions
            or len(self.instructions)
            >= MAX_GENOME_LENGTH
            or random.random()
            >= MUTATION_RATE * 0.10
        ):
            return

        source_position = (
            random.choice(
                call_positions
            )
        )

        source_call = (
            self.instructions[
                source_position
            ]
        )

        new_call = (
            source_call.copy()
        )

        insert_position = (
            random.randint(
                0,
                len(self.instructions),
            )
        )

        self.instructions.insert(
            insert_position,
            new_call,
        )

        mutations.append(
            f"DUPLICATE_MODULE_CALL "
            f"M{new_call.module_id:03d} "
            f"insert={insert_position}"
        )

    def _maybe_delete_unused_module(
        self,
        mutations: list[str],
    ) -> None:

        if (
            not self.modules
            or random.random()
            >= MUTATION_RATE * 0.10
        ):
            return

        referenced: set[int] = set()

        # MAIN references
        for instruction in (
            self.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                is not None
            ):

                referenced.add(
                    instruction.module_id
                )

        # Nested module references
        for module in (
            self.modules.values()
        ):

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    is not None
                ):

                    referenced.add(
                        instruction.module_id
                    )

        # Macro -> module references
        for macro in (
            self.macros.values()
        ):

            for instruction in macro:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    is not None
                ):

                    referenced.add(
                        instruction.module_id
                    )

        # AST -> module references
        if self.ast_program is not None:

            for node in self._walk_ast_nodes():

                if (
                    node.node_type
                    == "CALL_MODULE"
                    and node.module_id
                    is not None
                ):

                    referenced.add(
                        node.module_id
                    )

        unused = [
            module_id

            for module_id
            in self.modules

            if module_id
            not in referenced
        ]

        if not unused:
            return

        module_id = random.choice(
            unused
        )

        del self.modules[
            module_id
        ]

        self.module_meta.pop(
            module_id,
            None,
        )

        mutations.append(
            (
                f"DELETE_UNUSED_MODULE "
                f"M{module_id:03d}"
            )
        )

    def _maybe_delete_unused_macro(
        self,
        mutations: list[str],
    ) -> None:

        if (
            not self.macros
            or random.random()
            >= MUTATION_RATE * 0.10
        ):
            return

        referenced: set[int] = set()

        # MAIN -> macro
        for instruction in (
            self.instructions
        ):

            if (
                instruction.operation
                == "CALL_MACRO"
                and instruction.macro_id
                is not None
            ):

                referenced.add(
                    instruction.macro_id
                )

        # MODULE -> macro
        for module in (
            self.modules.values()
        ):

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MACRO"
                    and instruction.macro_id
                    is not None
                ):

                    referenced.add(
                        instruction.macro_id
                    )

        # MACRO -> macro
        for macro in (
            self.macros.values()
        ):

            for instruction in macro:

                if (
                    instruction.operation
                    == "CALL_MACRO"
                    and instruction.macro_id
                    is not None
                ):

                    referenced.add(
                        instruction.macro_id
                    )

        # AST -> macro references
        if self.ast_program is not None:

            for node in self._walk_ast_nodes():

                if (
                    node.node_type
                    == "CALL_MACRO"
                    and node.macro_id
                    is not None
                ):

                    referenced.add(
                        node.macro_id
                    )

        unused = [
            macro_id

            for macro_id
            in self.macros

            if macro_id
            not in referenced
        ]

        if not unused:
            return

        macro_id = random.choice(
            unused
        )

        metadata = (
            self.macro_meta.get(
                macro_id,
                {}
            )
        )

        uid = metadata.get(
            "uid"
        )

        del self.macros[
            macro_id
        ]

        self.macro_meta.pop(
            macro_id,
            None,
        )

        mutations.append(
            (
                f"DELETE_UNUSED_MACRO "
                f"K{macro_id:03d} "
                f"{uid}"
            )
        )

    # ---------------------------------------------------------
    # METRICS
    # ---------------------------------------------------------

    def total_instruction_count(
        self,
    ) -> int:

        return (
            len(
                self.instructions
            )
            + sum(
                len(module)
                for module
                in self.modules.values()
            )
            + sum(
                len(macro)
                for macro
                in self.macros.values()
            )
        )

    def _is_neutral_architecture_bridge(
        self,
    ) -> bool:

        architecture = (
            self.program_architecture
        )

        if architecture is None:
            return False

        root = (
            architecture.main.root
        )

        # Tam olarak:
        #
        # SEQ(
        #     CALL_LEGACY_MAIN
        # )
        #
        # dışında hiçbir architecture nötr sayılmaz.
        if root.node_type != "SEQUENCE":
            return False

        if len(root.children) != 1:
            return False

        child = root.children[0]

        if (
            child.node_type
            != "CALL_LEGACY_MAIN"
        ):
            return False

        if child.children:
            return False

        return True

    def active_code_size(
        self,
    ) -> int:

        if (
            self.program_architecture
            is not None
        ):

            architecture = (
                self.program_architecture
            )

            # =====================================================
            # REPRESENTATION-NEUTRAL BRIDGE
            # =====================================================

            if (
                self
                ._is_neutral_architecture_bridge()
            ):

                return (
                    len(self.instructions)
                    + sum(
                        len(module)
                        for module
                        in self.modules.values()
                    )
                    + sum(
                        len(macro)
                        for macro
                        in self.macros.values()
                    )
                )

            (
                reachable_function_ids,
                reachable_opcode_ids,
                uses_legacy_main,
            ) = (
                self
                ._reachable_architecture_code()
            )

            language = (
                self.evolved_language
            )

            # =====================================================
            # EFFECTIVE SEMANTIC COMPLEXITY
            #
            # Representation wrappers do not count as computation.
            #
            # Canonical identity operations:
            #
            #   ADD(0)
            #   SUBTRACT(0)
            #   MULTIPLY(1)
            #
            # have zero effective complexity.
            #
            # IF_CONTEXT itself only costs something when the
            # guarded subtree can actually change behavior.
            #
            # Function/opcode bodies are still counted once through
            # the reachable dependency sets below.
            # =====================================================

            function_effect_cache = {}
            opcode_effect_cache = {}

            visiting_functions = set()
            visiting_opcodes = set()

            def program_has_effect(
                program,
            ):

                return node_has_effect(
                    program.root
                )

            def function_has_effect(
                function_id,
            ):

                if (
                    function_id
                    in function_effect_cache
                ):
                    return (
                        function_effect_cache[
                            function_id
                        ]
                    )

                if (
                    function_id
                    in visiting_functions
                ):
                    # Recursive/cyclic dependency is conservatively
                    # treated as meaningful rather than free.
                    return True

                if (
                    function_id
                    not in architecture.functions
                ):
                    return True

                visiting_functions.add(
                    function_id
                )

                result = program_has_effect(
                    architecture
                    .functions[
                        function_id
                    ]
                    .program
                )

                visiting_functions.remove(
                    function_id
                )

                function_effect_cache[
                    function_id
                ] = result

                return result

            def opcode_has_effect(
                opcode_id,
            ):

                if (
                    opcode_id
                    in opcode_effect_cache
                ):
                    return (
                        opcode_effect_cache[
                            opcode_id
                        ]
                    )

                if (
                    opcode_id
                    in visiting_opcodes
                ):
                    return True

                if (
                    language is None
                    or opcode_id
                    not in language.opcodes
                ):
                    return True

                visiting_opcodes.add(
                    opcode_id
                )

                result = program_has_effect(
                    language
                    .opcodes[
                        opcode_id
                    ]
                    .program
                )

                visiting_opcodes.remove(
                    opcode_id
                )

                opcode_effect_cache[
                    opcode_id
                ] = result

                return result

            def node_has_effect(
                node,
            ):

                node_type = (
                    node.node_type
                )

                if node_type == "SEQUENCE":

                    return any(
                        node_has_effect(child)
                        for child in node.children
                    )

                if node_type in (
                    "ADD",
                    "SUBTRACT",
                ):

                    return (
                        node.value != 0.0
                    )

                if node_type == "MULTIPLY":

                    return (
                        node.value != 1.0
                    )

                if node_type == "CALL_FUNCTION":

                    if node.function_id is None:
                        return True

                    return function_has_effect(
                        node.function_id
                    )

                if node_type == "CALL_OPCODE":

                    if node.opcode_id is None:
                        return True

                    return opcode_has_effect(
                        node.opcode_id
                    )

                if node_type == "IF_CONTEXT":

                    return any(
                        node_has_effect(child)
                        for child in node.children
                    )

                if node_type == "CALL_LEGACY_MAIN":

                    return True

                # ABS, macro/module calls and any future unknown
                # operation are conservatively considered meaningful.
                return True

            def effective_node_size(
                node,
            ):

                node_type = (
                    node.node_type
                )

                if node_type == "SEQUENCE":

                    return sum(
                        effective_node_size(
                            child
                        )
                        for child
                        in node.children
                    )

                if node_type in (
                    "ADD",
                    "SUBTRACT",
                ):

                    return (
                        0
                        if node.value == 0.0
                        else 1
                    )

                if node_type == "MULTIPLY":

                    return (
                        0
                        if node.value == 1.0
                        else 1
                    )

                if node_type == "CALL_FUNCTION":

                    if node.function_id is None:
                        return 1

                    return (
                        1
                        if function_has_effect(
                            node.function_id
                        )
                        else 0
                    )

                if node_type == "CALL_OPCODE":

                    if node.opcode_id is None:
                        return 1

                    return (
                        1
                        if opcode_has_effect(
                            node.opcode_id
                        )
                        else 0
                    )

                if node_type == "CALL_LEGACY_MAIN":

                    # Legacy program size is accounted for
                    # separately through legacy_main_size.
                    return 0

                if node_type == "IF_CONTEXT":

                    child_size = sum(
                        effective_node_size(
                            child
                        )
                        for child
                        in node.children
                    )

                    if not node_has_effect(
                        node
                    ):
                        return 0

                    return (
                        1
                        + child_size
                    )

                return (
                    1
                    + sum(
                        effective_node_size(
                            child
                        )
                        for child
                        in node.children
                    )
                )

            def effective_program_size(
                program,
            ):

                return effective_node_size(
                    program.root
                )

            architecture_size = (
                effective_program_size(
                    architecture.main
                )
            )

            architecture_size += sum(
                effective_program_size(
                    architecture
                    .functions[
                        function_id
                    ]
                    .program
                )

                for function_id
                in reachable_function_ids
            )

            opcode_size = 0

            if language is not None:

                opcode_size = sum(
                    effective_program_size(
                        language
                        .opcodes[
                            opcode_id
                        ]
                        .program
                    )

                    for opcode_id
                    in reachable_opcode_ids
                )

            legacy_main_size = (
                len(self.instructions)
                if uses_legacy_main
                else 0
            )

            return (
                architecture_size
                + opcode_size
                + legacy_main_size
                + sum(
                    len(module)
                    for module
                    in self.modules.values()
                )
                + sum(
                    len(macro)
                    for macro
                    in self.macros.values()
                )
            )

        if (
            self.execution_mode == "AST"
            and self.ast_program is not None
        ):

            ast_size = (
                self.ast_program.node_count()
            )

            uses_legacy_main = any(
                node.node_type
                == "CALL_LEGACY_MAIN"

                for node
                in self._walk_ast_nodes()
            )

            legacy_main_size = (
                len(self.instructions)
                if uses_legacy_main
                else 0
            )

            return (
                ast_size
                + legacy_main_size
                + sum(
                    len(module)
                    for module
                    in self.modules.values()
                )
                + sum(
                    len(macro)
                    for macro
                    in self.macros.values()
                )
            )

        return self.total_instruction_count()

    def module_count(
        self,
    ) -> int:

        return len(
            self.modules
        )

    def macro_count(
        self,
    ) -> int:

        return len(
            self.macros
        )

    def ast_node_count(
        self,
    ) -> int:

        if self.ast_program is None:
            return 0

        return (
            self.ast_program
            .node_count()
        )

    def ast_depth(
        self,
    ) -> int:

        if self.ast_program is None:
            return 0

        return (
            self.ast_program
            .depth()
        )

    def ast_uses_legacy_main(
        self,
    ) -> bool:

        if self.ast_program is None:
            return False

        return any(
            node.node_type
            == "CALL_LEGACY_MAIN"

            for node
            in self._walk_ast_nodes()
        )

    def ast_is_pure(
        self,
    ) -> bool:

        return (
            self.ast_program is not None
            and self.execution_mode == "AST"
            and not self.ast_uses_legacy_main()
        )

    def ast_is_hybrid(
        self,
    ) -> bool:

        if (
            self.ast_program is None
            or self.execution_mode != "AST"
            or not self.ast_uses_legacy_main()
        ):
            return False

        return (
            self.ast_program.node_count()
            > 2
        )

    # ---------------------------------------------------------
    # DESCRIPTION
    # ---------------------------------------------------------

    def describe(
        self,
    ) -> str:

        main_text = " | ".join(
            instruction.describe()
            for instruction
            in self.instructions
        )

        if not main_text:
            main_text = "<EMPTY>"

        parts = [
            f"MODE[{self.execution_mode}]",
            f"MAIN[{main_text}]",
        ]

        if self.modules:

            module_texts = []

            for module_id in sorted(
                self.modules
            ):

                body = " | ".join(
                    instruction.describe()
                    for instruction
                    in self.modules[
                        module_id
                    ]
                )

                module_texts.append(
                    f"M{module_id:03d}"
                    f"[{body}]"
                )

            parts.append(
                (
                    "MODULES["
                    + " ; ".join(
                        module_texts
                    )
                    + "]"
                )
            )

        if self.macros:

            macro_texts = []

            for macro_id in sorted(
                self.macros
            ):

                body = " | ".join(
                    instruction.describe()
                    for instruction
                    in self.macros[
                        macro_id
                    ]
                )

                macro_texts.append(
                    f"K{macro_id:03d}"
                    f"[{body}]"
                )

            parts.append(
                (
                    "MACROS["
                    + " ; ".join(
                        macro_texts
                    )
                    + "]"
                )
            )

        if self.ast_program is not None:

            parts.append(
                (
                    "AST["
                    + self.ast_program.describe()
                    + "]"
                )
            )

        return " ".join(
            parts
        )
