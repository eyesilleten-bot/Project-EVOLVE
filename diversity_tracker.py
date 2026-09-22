# diversity_tracker.py

from __future__ import annotations

from collections import Counter

from organism import Organism


class DiversityTracker:

    @staticmethod
    def instruction_signature(
        instruction,
    ) -> tuple:

        if (
            instruction.operation
            == "CALL_MODULE"
        ):

            return (
                "CALL_MODULE",
                instruction.module_id,
            )

        if (
            instruction.operation
            == "CALL_MACRO"
        ):

            return (
                "CALL_MACRO",
                instruction.macro_id,
            )

        return (
            instruction.operation,
            round(
                instruction.value,
                2,
            ),
            instruction.context,
            instruction.offset,
            instruction.module_id,
        )

    def genome_signature(
        self,
        organism: Organism,
    ) -> tuple:

        genome = organism.genome

        main_signature = tuple(
            self.instruction_signature(
                instruction
            )
            for instruction
            in genome.instructions
        )

        module_signature = tuple(
            (
                module_id,
                tuple(
                    self.instruction_signature(
                        instruction
                    )
                    for instruction
                    in genome.modules[
                        module_id
                    ]
                ),
            )
            for module_id
            in sorted(
                genome.modules
            )
        )

        macro_signature = tuple(
            (
                macro_id,
                tuple(
                    self.instruction_signature(
                        instruction
                    )

                    for instruction
                    in genome.macros[
                        macro_id
                    ]
                ),
            )

            for macro_id
            in sorted(
                genome.macros
            )
        )

        return (
            main_signature,
            module_signature,
            macro_signature,
        )

    def unique_genome_count(
        self,
        population: list[Organism],
    ) -> int:

        signatures = {
            self.genome_signature(
                organism
            )
            for organism
            in population
        }

        return len(
            signatures
        )

    def diversity_ratio(
        self,
        population: list[Organism],
    ) -> float:

        if not population:
            return 0.0

        return (
            self.unique_genome_count(
                population
            )
            / len(population)
        )

    @staticmethod
    def average_genome_length(
        population: list[Organism],
    ) -> float:

        if not population:
            return 0.0

        return (
            sum(
                organism
                .genome
                .total_instruction_count()

                for organism
                in population
            )
            / len(population)
        )

    @staticmethod
    def average_module_count(
        population: list[Organism],
    ) -> float:

        if not population:
            return 0.0

        return (
            sum(
                organism
                .genome
                .module_count()

                for organism
                in population
            )
            / len(population)
        )

    @staticmethod
    def operation_usage(
        population: list[Organism],
    ) -> Counter:

        counter = Counter()

        for organism in population:

            genome = organism.genome

            for instruction in (
                genome.instructions
            ):
                counter[
                    instruction.operation
                ] += 1

            for module in (
                genome.modules.values()
            ):
                for instruction in module:
                    counter[
                        instruction.operation
                    ] += 1

            for macro in (
                organism
                .genome
                .macros
                .values()
            ):

                for instruction in macro:

                    counter[
                        instruction.operation
                    ] += 1

        return counter

    def analyze(
        self,
        population: list[Organism],
    ) -> dict:

        return {
            "unique_genomes":
                self.unique_genome_count(
                    population
                ),

            "diversity_ratio":
                self.diversity_ratio(
                    population
                ),

            "average_genome_length":
                self.average_genome_length(
                    population
                ),

            "average_module_count":
                self.average_module_count(
                    population
                ),

            "operation_usage":
                self.operation_usage(
                    population
                ),
        }