# era_champion_tracker.py

from __future__ import annotations

from organism import Organism


class EraChampionTracker:

    def __init__(self) -> None:

        self.champions: dict[
            int,
            Organism
        ] = {}

    def update(
        self,
        era_id: int,
        organism: Organism,
    ) -> None:

        existing = (
            self.champions.get(
                era_id
            )
        )

        if (
            existing is None
            or organism.fitness
            > existing.fitness
        ):

            # Organizmanın o anki halini
            # bağımsız olarak saklıyoruz.
            snapshot = Organism(
                genome=(
                    organism
                    .genome
                    .clone()
                ),

                generation=(
                    organism.generation
                ),

                parent_id=(
                    organism.parent_id
                ),

                birth_mutations=list(
                    organism.birth_mutations
                ),

                lineage_depth=(
                    organism.lineage_depth
                ),

                organism_id=(
                    organism.id
                ),
            )

            snapshot.fitness = (
                organism.fitness
            )

            snapshot.error = (
                organism.error
            )

            snapshot.task_errors = dict(
                organism.task_errors
            )

            self.champions[
                era_id
            ] = snapshot

    def get(
        self,
        era_id: int,
    ) -> Organism | None:

        return (
            self.champions.get(
                era_id
            )
        )

    def report(
        self,
    ) -> dict:

        return {
            era_id: {
                "organism_id":
                    champion.id,

                "generation":
                    champion.generation,

                "fitness":
                    champion.fitness,

                "error":
                    champion.error,
            }

            for era_id, champion
            in self.champions.items()
        }