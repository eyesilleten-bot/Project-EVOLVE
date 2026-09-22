from __future__ import annotations

from config import (
    AST_EXECUTION_BUDGET,
    MAX_AST_DEPTH,
    MAX_AST_NODES,
    MAX_MODULE_CALL_DEPTH,
)


class GeneratedRuntime:

    def __init__(
        self,
        genome,
        architecture_mode: bool = False,
    ) -> None:

        self.genome = genome

        self.architecture_mode = (
            architecture_mode
        )

        # =================================================
        # STRUCTURAL LIMITS
        # =================================================

        if architecture_mode:

            architecture = (
                genome.program_architecture
            )

            if architecture is None:

                raise RuntimeError(
                    "Genome has no program architecture."
                )

            programs = [
                architecture.main
            ]

            programs.extend(
                function.program
                for function
                in architecture.functions.values()
            )

            language = getattr(
                genome,
                "evolved_language",
                None,
            )

            if language is not None:

                programs.extend(
                    opcode.program
                    for opcode
                    in language.opcodes.values()
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

        else:

            if genome.ast_program is None:

                raise RuntimeError(
                    "Genome has no AST program."
                )

            if (
                genome.ast_program.node_count()
                > MAX_AST_NODES
            ):

                raise RuntimeError(
                    "AST node limit exceeded."
                )

            if (
                genome.ast_program.depth()
                > MAX_AST_DEPTH
            ):

                raise RuntimeError(
                    "AST depth limit exceeded."
                )

        self.ast_step_counter = [0]

        self.step_counter = [0]

        self.max_steps = max(
            40,
            genome.total_instruction_count()
            * 6,
        )

    # =====================================================
    # AST EXECUTION STEP
    # =====================================================

    def ast_step(
        self,
    ) -> None:

        self.ast_step_counter[0] += 1

        if (
            self.ast_step_counter[0]
            > AST_EXECUTION_BUDGET
        ):

            raise RuntimeError(
                "AST execution budget exceeded."
            )

    def enter_evolved_function(
        self,
        function_id: str,
        call_depth: int,
        function_stack: list[str],
    ) -> list[str]:

        if (
            call_depth
            > MAX_MODULE_CALL_DEPTH
        ):

            raise RuntimeError(
                "Maximum AST call depth exceeded."
            )

        if (
            function_id
            in function_stack
        ):

            raise RuntimeError(
                "Recursive evolved function call."
            )

        return (
            list(function_stack)
            + [function_id]
        )

    def enter_evolved_opcode(
        self,
        opcode_id: str,
        call_depth: int,
        opcode_stack: list[str],
    ) -> list[str]:

        if (
            call_depth
            > MAX_MODULE_CALL_DEPTH
        ):

            raise RuntimeError(
                "Maximum AST call depth exceeded."
            )

        if (
            opcode_id
            in opcode_stack
        ):

            raise RuntimeError(
                "Recursive evolved opcode call."
            )

        return (
            list(opcode_stack)
            + [opcode_id]
        )

    # =====================================================
    # LEGACY MAIN
    # =====================================================

    def call_legacy_main(
        self,
        value: float,
        context_id: int,
        call_depth: int = 1,
    ) -> float:

        return self.genome._execute_sequence(
            sequence=self.genome.instructions,
            value=float(value),
            context_id=context_id,
            step_counter=self.step_counter,
            max_steps=self.max_steps,
            call_depth=call_depth,
        )

    # =====================================================
    # MODULE
    # =====================================================

    def call_module(
        self,
        module_id: int,
        value: float,
        context_id: int,
        call_depth: int = 1,
    ) -> float:

        if module_id not in self.genome.modules:

            raise RuntimeError(
                "Generated Python requested "
                f"missing module {module_id}."
            )

        return self.genome._execute_sequence(
            sequence=self.genome.modules[
                module_id
            ],
            value=float(value),
            context_id=context_id,
            step_counter=self.step_counter,
            max_steps=self.max_steps,
            call_depth=call_depth,
        )

    # =====================================================
    # MACRO
    # =====================================================

    def call_macro(
        self,
        macro_id: int,
        value: float,
        context_id: int,
        call_depth: int = 1,
    ) -> float:

        if macro_id not in self.genome.macros:

            raise RuntimeError(
                "Generated Python requested "
                f"missing macro {macro_id}."
            )

        return self.genome._execute_sequence(
            sequence=self.genome.macros[
                macro_id
            ],
            value=float(value),
            context_id=context_id,
            step_counter=self.step_counter,
            max_steps=self.max_steps,
            call_depth=call_depth,
        )
