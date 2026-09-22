# organism.py

from __future__ import annotations

from genome import Genome


class Organism:

    _next_id = 1

    def __init__(
        self,
        genome: Genome,
        generation: int,
        parent_id: str | None = None,
        birth_mutations: list[str] | None = None,
        lineage_depth: int = 0,
        organism_id: str | None = None,
    ):

        if organism_id is None:

            self.id = (
                f"EV-"
                f"{Organism._next_id:06d}"
            )

            Organism._next_id += 1

        else:

            self.id = organism_id

        self.genome = genome

        self.generation = generation

        self.parent_id = parent_id

        self.birth_mutations = (
            birth_mutations or []
        )

        self.lineage_depth = (
            lineage_depth
        )

        self.fitness = 0.0
        self.error = float("inf")

        self.task_errors: dict[
            str,
            float
        ] = {}

    def run(
        self,
        input_value: float,
        context_id: int,
    ) -> float:

        return self.genome.execute(
            input_value,
            context_id,
        )

    def create_child(
        self,
        generation: int,
    ) -> "Organism":

        child_genome = (
            self.genome.clone()
        )

        mutations = (
            child_genome.mutate(
                generation=generation
            )
        )

        return Organism(
            genome=child_genome,
            generation=generation,
            parent_id=self.id,
            birth_mutations=mutations,
            lineage_depth=(
                self.lineage_depth + 1
            ),
        )

    @classmethod
    def get_next_id(
        cls,
    ) -> int:

        return cls._next_id

    @classmethod
    def set_next_id(
        cls,
        next_id: int,
    ) -> None:

        cls._next_id = max(
            1,
            int(next_id),
        )