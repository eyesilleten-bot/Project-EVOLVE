from __future__ import annotations

from dataclasses import dataclass

from generated_python_runner import (
    GeneratedPythonRunner,
)


@dataclass
class DualExecutionResult:

    organism_id: str

    ast_fitness: float
    python_fitness: float

    fitness_difference: float

    matched: bool

    source_fingerprint: str

    generation: int | None = None

    error: str | None = None


class _GeneratedOrganismProxy:

    def __init__(
        self,
        original,
        runner: GeneratedPythonRunner,
    ) -> None:

        self._original = original
        self._runner = runner

        self.genome = original.genome

        self.fitness = 0.0
        self.error = float("inf")
        self.task_errors = {}

    def run(
        self,
        input_value: float,
        context_id: int,
    ) -> float:

        return self._runner.run(
            self._original,
            input_value,
            context_id,
        )

    def __getattr__(
        self,
        name,
    ):

        return getattr(
            self._original,
            name,
        )


class _GeneratedArchitectureProxy:

    def __init__(
        self,
        original,
        runner: GeneratedPythonRunner,
    ) -> None:

        self._original = original
        self._runner = runner

        self.genome = original.genome

        self.fitness = 0.0
        self.error = float("inf")
        self.task_errors = {}

    def run(
        self,
        input_value: float,
        context_id: int,
    ) -> float:

        return (
            self._runner.run_architecture(
                self._original,
                input_value,
                context_id,
            )
        )

    def __getattr__(
        self,
        name,
    ):

        return getattr(
            self._original,
            name,
        )


class DualExecutionValidator:

    def __init__(
        self,
        tolerance: float = 1e-12,
    ) -> None:

        self.tolerance = tolerance

        self.runner = (
            GeneratedPythonRunner()
        )

        # ---------------------------------------------
        # ALL-TIME COUNTERS
        # ---------------------------------------------

        self.total_checks = 0
        self.total_matches = 0
        self.total_mismatches = 0
        self.total_errors = 0

        # ---------------------------------------------
        # PYTHON PRIMARY QUALIFICATION
        # ---------------------------------------------

        self.python_primary_checks = 0
        self.python_primary_matches = 0
        self.python_primary_mismatches = 0
        self.python_primary_errors = 0

        self.python_primary_generation_history: list[
            dict
        ] = []

        self.current_python_primary_generation = None
        self.current_python_primary_checks = 0
        self.current_python_primary_matches = 0
        self.current_python_primary_mismatches = 0
        self.current_python_primary_errors = 0

        # ---------------------------------------------
        # CURRENT / LAST GENERATION
        # ---------------------------------------------

        self.last_generation = None

        self.last_generation_checks = 0
        self.last_generation_matches = 0
        self.last_generation_mismatches = 0
        self.last_generation_errors = 0

        # ---------------------------------------------
        # HISTORY
        # ---------------------------------------------

        self.generation_history: list[
            dict
        ] = []

        self.mismatch_history: list[
            dict
        ] = []

        self.error_history: list[
            dict
        ] = []

    # =====================================================
    # GENERATION SNAPSHOT
    # =====================================================

    def _current_generation_snapshot(
        self,
    ) -> dict | None:

        if self.last_generation is None:

            return None

        return {
            "generation":
                self.last_generation,

            "checks":
                self.last_generation_checks,

            "matches":
                self.last_generation_matches,

            "mismatches":
                self.last_generation_mismatches,

            "errors":
                self.last_generation_errors,
        }

    def _archive_current_generation(
        self,
    ) -> None:

        snapshot = (
            self._current_generation_snapshot()
        )

        if snapshot is None:
            return

        if snapshot["checks"] <= 0:
            return

        # Aynı generation'ı iki kez archive etme.
        if (
            self.generation_history
            and self.generation_history[-1][
                "generation"
            ]
            == snapshot["generation"]
        ):

            self.generation_history[-1] = (
                snapshot
            )

            return

        self.generation_history.append(
            snapshot
        )

    # =====================================================
    # GENERATION RESET
    # =====================================================

    def begin_generation(
        self,
        generation: int,
    ) -> None:

        # Aynı generation içinde evaluate_population()
        # tekrar çağrılırsa mevcut sayaçları sıfırlıyoruz,
        # fakat history'ye duplicate generation eklemiyoruz.
        if (
            self.last_generation is not None
            and self.last_generation
            != generation
        ):

            self._archive_current_generation()

        self.last_generation = generation

        self.last_generation_checks = 0
        self.last_generation_matches = 0
        self.last_generation_mismatches = 0
        self.last_generation_errors = 0

    # =====================================================
    # VALIDATE SHADOW
    # =====================================================

    def validate_shadow(
        self,
        organism,
        evaluator,
        generation: int | None = None,
    ) -> DualExecutionResult:

        if (
            organism.genome.execution_mode
            != "AST"
            or organism.genome.ast_program
            is None
        ):

            raise ValueError(
                "Shadow validation requires "
                "an AST organism."
            )

        # PRIMARY phenotype fitness.
        # EvolutionEngine bunu zaten hesapladı.
        ast_fitness = float(
            organism.fitness
        )

        fingerprint = (
            self.runner
            .source_fingerprint_for(
                organism
            )
        )

        proxy = _GeneratedOrganismProxy(
            organism,
            self.runner,
        )

        error_message = None

        try:

            evaluator.evaluate(
                proxy
            )

            python_fitness = float(
                proxy.fitness
            )

            difference = (
                python_fitness
                - ast_fitness
            )

            matched = (
                abs(difference)
                <= self.tolerance
            )

        except Exception as exc:

            python_fitness = float("nan")
            difference = float("nan")
            matched = False

            error_message = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

        result = DualExecutionResult(
            organism_id=organism.id,
            ast_fitness=ast_fitness,
            python_fitness=python_fitness,
            fitness_difference=difference,
            matched=matched,
            source_fingerprint=fingerprint,
            generation=generation,
            error=error_message,
        )

        self.total_checks += 1
        self.last_generation_checks += 1

        if error_message is not None:

            self.total_errors += 1
            self.last_generation_errors += 1

            self.error_history.append(
                {
                    "generation":
                        generation,

                    "organism_id":
                        organism.id,

                    "fingerprint":
                        fingerprint,

                    "error":
                        error_message,

                    "ast":
                        organism.genome
                        .ast_program
                        .describe(),
                }
            )

        elif matched:

            self.total_matches += 1
            self.last_generation_matches += 1

        else:

            self.total_mismatches += 1
            self.last_generation_mismatches += 1

            self.mismatch_history.append(
                {
                    "generation":
                        generation,

                    "organism_id":
                        organism.id,

                    "ast_fitness":
                        ast_fitness,

                    "python_fitness":
                        python_fitness,

                    "difference":
                        difference,

                    "fingerprint":
                        fingerprint,

                    "ast":
                        organism.genome
                        .ast_program
                        .describe(),
                }
            )

        return result

    # =====================================================
    # PYTHON PRIMARY GENERATION HISTORY
    # =====================================================

    def _python_primary_snapshot(
        self,
    ) -> dict | None:

        if (
            self.current_python_primary_generation
            is None
        ):

            return None

        return {
            "generation":
                self.current_python_primary_generation,

            "checks":
                self.current_python_primary_checks,

            "matches":
                self.current_python_primary_matches,

            "mismatches":
                self.current_python_primary_mismatches,

            "errors":
                self.current_python_primary_errors,
        }

    def _archive_python_primary_generation(
        self,
    ) -> None:

        snapshot = (
            self._python_primary_snapshot()
        )

        if snapshot is None:
            return

        if snapshot["checks"] <= 0:
            return

        if (
            self.python_primary_generation_history
            and
            self.python_primary_generation_history[
                -1
            ]["generation"]
            == snapshot["generation"]
        ):

            self.python_primary_generation_history[
                -1
            ] = snapshot

        else:

            self.python_primary_generation_history.append(
                snapshot
            )

    def begin_python_primary_generation(
        self,
        generation: int,
    ) -> None:

        if (
            self.current_python_primary_generation
            is not None
            and
            self.current_python_primary_generation
            != generation
        ):

            self._archive_python_primary_generation()

        self.current_python_primary_generation = (
            generation
        )

        self.current_python_primary_checks = 0
        self.current_python_primary_matches = 0
        self.current_python_primary_mismatches = 0
        self.current_python_primary_errors = 0

    def python_primary_generation_report(
        self,
    ) -> list[dict]:

        history = [
            dict(item)
            for item
            in self.python_primary_generation_history
        ]

        current = (
            self._python_primary_snapshot()
        )

        if (
            current is not None
            and current["checks"] > 0
        ):

            if (
                history
                and history[-1]["generation"]
                == current["generation"]
            ):

                history[-1] = current

            else:

                history.append(
                    current
                )

        return history

    # =====================================================
    # PYTHON PRIMARY / AST SHADOW
    # =====================================================

    def validate_python_primary(
        self,
        organism,
        evaluator,
        generation: int | None = None,
    ) -> DualExecutionResult:

        if (
            organism.genome.execution_mode
            != "AST"
            or organism.genome.ast_program
            is None
        ):

            raise ValueError(
                "Python-primary validation "
                "requires an AST organism."
            )

        fingerprint = (
            self.runner
            .source_fingerprint_for(
                organism
            )
        )

        error_message = None

        # =============================================
        # GENERATED PYTHON = PRIMARY
        # =============================================

        try:

            proxy = _GeneratedOrganismProxy(
                organism,
                self.runner,
            )

            evaluator.evaluate(
                proxy
            )

            python_fitness = float(
                proxy.fitness
            )

            python_error = proxy.error

            python_task_errors = dict(
                proxy.task_errors
            )

            # =========================================
            # AST INTERPRETER = SHADOW
            # =========================================

            evaluator.evaluate(
                organism
            )

            ast_fitness = float(
                organism.fitness
            )

            difference = (
                python_fitness
                - ast_fitness
            )

            matched = (
                abs(difference)
                <= self.tolerance
            )

            # =========================================
            # RESTORE PYTHON PRIMARY RESULT
            # =========================================

            organism.fitness = (
                python_fitness
            )

            organism.error = (
                python_error
            )

            organism.task_errors = (
                python_task_errors
            )

        except Exception as exc:

            python_fitness = float("nan")
            ast_fitness = float("nan")
            difference = float("nan")

            matched = False

            error_message = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

        result = DualExecutionResult(
            organism_id=organism.id,
            ast_fitness=ast_fitness,
            python_fitness=python_fitness,
            fitness_difference=difference,
            matched=matched,
            source_fingerprint=fingerprint,
            generation=generation,
            error=error_message,
        )

        # =============================================
        # PRIMARY COUNTERS
        # =============================================

        self.python_primary_checks += 1
        self.current_python_primary_checks += 1

        if error_message is not None:

            self.python_primary_errors += 1
            self.current_python_primary_errors += 1

            self.error_history.append(
                {
                    "generation":
                        generation,

                    "organism_id":
                        organism.id,

                    "fingerprint":
                        fingerprint,

                    "error":
                        error_message,

                    "ast":
                        organism.genome
                        .ast_program
                        .describe(),

                    "execution_direction":
                        "PYTHON_PRIMARY",
                }
            )

        elif matched:

            self.python_primary_matches += 1
            self.current_python_primary_matches += 1

        else:

            self.python_primary_mismatches += 1
            self.current_python_primary_mismatches += 1

            self.mismatch_history.append(
                {
                    "generation":
                        generation,

                    "organism_id":
                        organism.id,

                    "ast_fitness":
                        ast_fitness,

                    "python_fitness":
                        python_fitness,

                    "difference":
                        difference,

                    "fingerprint":
                        fingerprint,

                    "ast":
                        organism.genome
                        .ast_program
                        .describe(),

                    "execution_direction":
                        "PYTHON_PRIMARY",
                }
            )

        return result


    def validate_architecture_python_primary(
        self,
        organism,
        evaluator,
        generation: int | None = None,
    ) -> DualExecutionResult:

        if (
            organism.genome.execution_mode
            != "ARCH"
            or organism.genome.program_architecture
            is None
        ):

            raise ValueError(
                "Architecture Python-primary "
                "validation requires an "
                "ARCH organism."
            )

        fingerprint = (
            self.runner
            .architecture_source_fingerprint_for(
                organism
            )
        )

        error_message = None

        # =================================================
        # GENERATED ARCHITECTURE PYTHON = PRIMARY
        # =================================================

        try:

            proxy = (
                _GeneratedArchitectureProxy(
                    organism,
                    self.runner,
                )
            )

            evaluator.evaluate(
                proxy
            )

            python_fitness = float(
                proxy.fitness
            )

            python_error = (
                proxy.error
            )

            python_task_errors = dict(
                proxy.task_errors
            )

            # =============================================
            # ARCHITECTURE INTERPRETER = SHADOW
            # =============================================

            evaluator.evaluate(
                organism
            )

            interpreter_fitness = float(
                organism.fitness
            )

            difference = (
                python_fitness
                - interpreter_fitness
            )

            matched = (
                abs(difference)
                <= self.tolerance
            )

            # =============================================
            # RESTORE GENERATED PYTHON PRIMARY
            # =============================================

            organism.fitness = (
                python_fitness
            )

            organism.error = (
                python_error
            )

            organism.task_errors = (
                python_task_errors
            )

        except Exception as exc:

            python_fitness = float("nan")

            interpreter_fitness = (
                float("nan")
            )

            difference = float("nan")

            matched = False

            error_message = (
                f"{type(exc).__name__}: "
                f"{exc}"
            )

        result = DualExecutionResult(
            organism_id=organism.id,
            ast_fitness=(
                interpreter_fitness
            ),
            python_fitness=python_fitness,
            fitness_difference=difference,
            matched=matched,
            source_fingerprint=fingerprint,
            generation=generation,
            error=error_message,
        )

        # =================================================
        # SAME PYTHON-PRIMARY QUALIFICATION COUNTERS
        # =================================================
        #
        # Bu sayaçlar artık:
        #
        #   AST generated Python
        #   +
        #   ARCH generated Python
        #
        # için ortak authoritative-backend
        # qualification istatistiğidir.
        # =================================================

        self.python_primary_checks += 1

        self.current_python_primary_checks += 1

        if error_message is not None:

            self.python_primary_errors += 1

            self.current_python_primary_errors += 1

            self.error_history.append(
                {
                    "generation":
                        generation,

                    "organism_id":
                        organism.id,

                    "fingerprint":
                        fingerprint,

                    "error":
                        error_message,

                    "architecture":
                        organism.genome
                        .program_architecture
                        .describe(),

                    "execution_direction":
                        "ARCH_PYTHON_PRIMARY",
                }
            )

        elif matched:

            self.python_primary_matches += 1

            self.current_python_primary_matches += 1

        else:

            self.python_primary_mismatches += 1

            self.current_python_primary_mismatches += 1

            self.mismatch_history.append(
                {
                    "generation":
                        generation,

                    "organism_id":
                        organism.id,

                    "ast_fitness":
                        interpreter_fitness,

                    "python_fitness":
                        python_fitness,

                    "difference":
                        difference,

                    "fingerprint":
                        fingerprint,

                    "architecture":
                        organism.genome
                        .program_architecture
                        .describe(),

                    "execution_direction":
                        "ARCH_PYTHON_PRIMARY",
                }
            )

        return result

    # =====================================================
    # CONTROLLED TEST API
    # =====================================================

    def validate(
        self,
        organism,
        evaluator,
    ) -> DualExecutionResult:

        evaluator.evaluate(
            organism
        )

        return self.validate_shadow(
            organism=organism,
            evaluator=evaluator,
            generation=getattr(
                organism,
                "generation",
                None,
            ),
        )

    # =====================================================
    # HISTORY
    # =====================================================

    def generation_report(
        self,
    ) -> list[dict]:

        history = [
            dict(item)
            for item in self.generation_history
        ]

        current = (
            self._current_generation_snapshot()
        )

        if (
            current is not None
            and current["checks"] > 0
        ):

            if (
                history
                and history[-1]["generation"]
                == current["generation"]
            ):

                history[-1] = current

            else:

                history.append(
                    current
                )

        return history

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def to_state(
        self,
    ) -> dict:

        return {
            "tolerance":
                self.tolerance,

            "total_checks":
                self.total_checks,

            "total_matches":
                self.total_matches,

            "total_mismatches":
                self.total_mismatches,

            "total_errors":
                self.total_errors,

            "python_primary_checks":
                self.python_primary_checks,

            "python_primary_matches":
                self.python_primary_matches,

            "python_primary_mismatches":
                self.python_primary_mismatches,

            "python_primary_errors":
                self.python_primary_errors,

            "python_primary_generation_history":
                self.python_primary_generation_report(),

            "current_python_primary_generation":
                self.current_python_primary_generation,

            "current_python_primary_checks":
                self.current_python_primary_checks,

            "current_python_primary_matches":
                self.current_python_primary_matches,

            "current_python_primary_mismatches":
                self.current_python_primary_mismatches,

            "current_python_primary_errors":
                self.current_python_primary_errors,

            "last_generation":
                self.last_generation,

            "last_generation_checks":
                self.last_generation_checks,

            "last_generation_matches":
                self.last_generation_matches,

            "last_generation_mismatches":
                self.last_generation_mismatches,

            "last_generation_errors":
                self.last_generation_errors,

            "generation_history":
                self.generation_report(),

            "mismatch_history":
                list(
                    self.mismatch_history
                ),

            "error_history":
                list(
                    self.error_history
                ),
        }

    def load_state(
        self,
        state: dict,
    ) -> None:

        self.tolerance = float(
            state.get(
                "tolerance",
                self.tolerance,
            )
        )

        self.total_checks = int(
            state.get(
                "total_checks",
                0,
            )
        )

        self.total_matches = int(
            state.get(
                "total_matches",
                0,
            )
        )

        self.total_mismatches = int(
            state.get(
                "total_mismatches",
                0,
            )
        )

        self.total_errors = int(
            state.get(
                "total_errors",
                0,
            )
        )

        self.last_generation = (
            state.get(
                "last_generation"
            )
        )

        self.last_generation_checks = int(
            state.get(
                "last_generation_checks",
                0,
            )
        )

        self.last_generation_matches = int(
            state.get(
                "last_generation_matches",
                0,
            )
        )

        self.last_generation_mismatches = int(
            state.get(
                "last_generation_mismatches",
                0,
            )
        )

        self.last_generation_errors = int(
            state.get(
                "last_generation_errors",
                0,
            )
        )

        self.generation_history = [
            dict(item)
            for item in state.get(
                "generation_history",
                [],
            )
        ]

        # Son generation to_state() sırasında history'ye
        # dahil edilmiş olabilir. RAM'de tekrar archive
        # edildiğinde duplicate olmaması için son kaydı
        # burada çıkarıyoruz; current generation ayrı
        # sayaçlarda zaten korunuyor.
        if (
            self.generation_history
            and self.last_generation
            is not None
            and self.generation_history[-1].get(
                "generation"
            )
            == self.last_generation
        ):

            self.generation_history.pop()

        self.mismatch_history = [
            dict(item)
            for item in state.get(
                "mismatch_history",
                [],
            )
        ]

        self.error_history = [
            dict(item)
            for item in state.get(
                "error_history",
                [],
            )
        ]

        self.python_primary_checks = int(
            state.get(
                "python_primary_checks",
                0,
            )
        )

        self.python_primary_matches = int(
            state.get(
                "python_primary_matches",
                0,
            )
        )

        self.python_primary_mismatches = int(
            state.get(
                "python_primary_mismatches",
                0,
            )
        )

        self.python_primary_errors = int(
            state.get(
                "python_primary_errors",
                0,
            )
        )

        self.current_python_primary_generation = (
            state.get(
                "current_python_primary_generation"
            )
        )

        self.current_python_primary_checks = int(
            state.get(
                "current_python_primary_checks",
                0,
            )
        )

        self.current_python_primary_matches = int(
            state.get(
                "current_python_primary_matches",
                0,
            )
        )

        self.current_python_primary_mismatches = int(
            state.get(
                "current_python_primary_mismatches",
                0,
            )
        )

        self.current_python_primary_errors = int(
            state.get(
                "current_python_primary_errors",
                0,
            )
        )

        self.python_primary_generation_history = [
            dict(item)
            for item
            in state.get(
                "python_primary_generation_history",
                [],
            )
        ]

        if (
            self.python_primary_generation_history
            and
            self.current_python_primary_generation
            is not None
            and
            self.python_primary_generation_history[
                -1
            ].get(
                "generation"
            )
            == self.current_python_primary_generation
        ):

            self.python_primary_generation_history.pop()

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> dict:

        return {
            "total_checks":
                self.total_checks,

            "total_matches":
                self.total_matches,

            "total_mismatches":
                self.total_mismatches,

            "total_errors":
                self.total_errors,

            "python_primary_checks":
                self.python_primary_checks,

            "python_primary_matches":
                self.python_primary_matches,

            "python_primary_mismatches":
                self.python_primary_mismatches,

            "python_primary_errors":
                self.python_primary_errors,

            "python_primary_generation_history":
                self.python_primary_generation_report(),

            "last_generation":
                self.last_generation,

            "last_generation_checks":
                self.last_generation_checks,

            "last_generation_matches":
                self.last_generation_matches,

            "last_generation_mismatches":
                self.last_generation_mismatches,

            "last_generation_errors":
                self.last_generation_errors,

            "generation_history":
                self.generation_report(),

            "mismatch_history":
                list(
                    self.mismatch_history
                ),

            "error_history":
                list(
                    self.error_history
                ),
        }