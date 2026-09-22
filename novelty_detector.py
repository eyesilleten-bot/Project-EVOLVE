# novelty_detector.py

from __future__ import annotations

from organism import Organism


class NoveltyDetector:

    def __init__(self):

        self.known_structures: set[
            tuple
        ] = set()

        self.structure_archive: dict[
            tuple,
            dict,
        ] = {}

        self.novel_events: list[
            dict
        ] = []

    @staticmethod
    def structural_instruction(
        instruction,
    ) -> tuple:

        if instruction.operation in (
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
        ):

            return (
                instruction.operation,
            )

        if instruction.operation == (
            "JUMP_IF_CONTEXT_NE"
        ):

            return (
                instruction.operation,
                instruction.context,
                instruction.offset,
            )

        if instruction.operation == "JUMP":

            return (
                instruction.operation,
                instruction.offset,
            )

        if instruction.operation == (
            "CALL_MODULE"
        ):

            return (
                instruction.operation,
                instruction.module_id,
            )

        if instruction.operation == (
            "CALL_MACRO"
        ):

            return (
                instruction.operation,
                instruction.macro_id,
            )

        return (
            instruction.operation,
        )

    @classmethod
    def structural_signature(
        cls,
        organism: Organism,
    ) -> tuple:

        genome = organism.genome

        main_signature = tuple(
            cls.structural_instruction(
                instruction
            )
            for instruction
            in genome.instructions
        )

        module_signature = tuple(
            (
                module_id,
                tuple(
                    cls.structural_instruction(
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
                    cls.structural_instruction(
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

    def inspect(
        self,
        organism: Organism,
    ) -> dict | None:

        signature = (
            self.structural_signature(
                organism
            )
        )

        if (
            signature
            in self.known_structures
        ):
            return None

        self.known_structures.add(
            signature
        )

        record = {
            "organism_id":
                organism.id,

            "generation":
                organism.generation,

            "signature":
                signature,

            "genome":
                organism.genome.describe(),

            "genome_length":
                organism
                .genome
                .total_instruction_count(),

            "module_count":
                organism
                .genome
                .module_count(),
        }

        self.structure_archive[
            signature
        ] = record

        self.novel_events.append(
            record
        )

        return record

    def inspect_population(
        self,
        population: list[Organism],
    ) -> list[dict]:

        events = []

        for organism in population:

            event = self.inspect(
                organism
            )

            if event is not None:
                events.append(
                    event
                )

        return events

    def total_structures(
        self,
    ) -> int:

        return len(
            self.known_structures
        )

    def recent_events(
        self,
        count: int = 5,
    ) -> list[dict]:

        return self.novel_events[
            -count:
        ]