# module_ablation.py

from __future__ import annotations

from evaluator import Evaluator
from organism import Organism


class ModuleAblationTester:

    def __init__(
        self,
        evaluator: Evaluator,
    ):

        self.evaluator = evaluator

    # ========================================================
    # REMOVE REFERENCES
    # ========================================================

    @staticmethod
    def _remove_module_references(
        genome,
        module_id: int,
    ) -> dict:

        main_removed = 0
        nested_removed = 0

        # MAIN -> target
        new_main = []

        for instruction in (
            genome.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                == module_id
            ):

                main_removed += 1
                continue

            new_main.append(
                instruction
            )

        genome.instructions = (
            new_main
        )

        # MODULE -> target
        for (
            owner_id,
            module,
        ) in genome.modules.items():

            if owner_id == module_id:
                continue

            new_body = []

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    == module_id
                ):

                    nested_removed += 1
                    continue

                new_body.append(
                    instruction
                )

            genome.modules[
                owner_id
            ] = new_body

        return {
            "main_calls_removed":
                main_removed,

            "nested_calls_removed":
                nested_removed,

            "total_calls_removed":
                (
                    main_removed
                    + nested_removed
                ),
        }

    # ========================================================
    # TEST ONE MODULE
    # ========================================================

    def test_module(
        self,
        organism: Organism,
        module_id: int,
    ) -> dict:

        if (
            module_id
            not in organism
            .genome
            .modules
        ):

            return {
                "module_id":
                    module_id,

                "valid":
                    False,

                "reason":
                    "MODULE_NOT_FOUND",
            }

        # -------------------------
        # BASELINE
        # -------------------------

        baseline = (
            organism
            .genome
            .clone()
        )

        baseline_organism = (
            Organism(
                genome=baseline,
                generation=(
                    organism.generation
                ),
            )
        )

        self.evaluator.evaluate(
            baseline_organism
        )

        baseline_fitness = (
            baseline_organism
            .fitness
        )

        baseline_error = (
            baseline_organism
            .error
        )

        # -------------------------
        # ABLATION
        # -------------------------

        ablated_genome = (
            organism
            .genome
            .clone()
        )

        removal_report = (
            self
            ._remove_module_references(
                ablated_genome,
                module_id,
            )
        )

        if (
            removal_report[
                "total_calls_removed"
            ]
            == 0
        ):

            return {
                "module_id":
                    module_id,

                "valid":
                    False,

                "reason":
                    "MODULE_NOT_REACHABLE",

                **removal_report,
            }

        # MAIN'in boşalması execution açısından
        # aslında güvenlidir: input olduğu gibi döner.
        # Dolayısıyla eski "empty main = invalid"
        # kuralını kaldırıyoruz.

        ablated_organism = (
            Organism(
                genome=(
                    ablated_genome
                ),

                generation=(
                    organism.generation
                ),
            )
        )

        self.evaluator.evaluate(
            ablated_organism
        )

        fitness_loss = (
            baseline_fitness
            - ablated_organism
            .fitness
        )

        error_change = (
            ablated_organism.error
            - baseline_error
        )

        return {
            "module_id":
                module_id,

            "valid":
                True,

            "baseline_fitness":
                baseline_fitness,

            "ablated_fitness":
                ablated_organism
                .fitness,

            "fitness_loss":
                fitness_loss,

            "baseline_error":
                baseline_error,

            "ablated_error":
                ablated_organism
                .error,

            "error_change":
                error_change,

            "main_calls_removed":
                removal_report[
                    "main_calls_removed"
                ],

            "nested_calls_removed":
                removal_report[
                    "nested_calls_removed"
                ],

            "total_calls_removed":
                removal_report[
                    "total_calls_removed"
                ],

            "task_errors":
                dict(
                    ablated_organism
                    .task_errors
                ),
        }

    # ========================================================
    # ALL MODULES
    # ========================================================

    def test_all_modules(
        self,
        organism: Organism,
    ) -> list[dict]:

        results = []

        for module_id in sorted(
            organism
            .genome
            .modules
        ):

            result = (
                self.test_module(
                    organism,
                    module_id,
                )
            )

            results.append(
                result
            )

        return results