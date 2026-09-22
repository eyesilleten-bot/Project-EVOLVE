# evolution_event_detector.py

from __future__ import annotations

from organism import Organism


class EvolutionEventDetector:
    """
    Anlamlı evrimsel sıçramaları ERA bazında yakalar.

    Bir major event için:
    - yapı novel olmalı
    - aynı ERA içindeki önceki en iyi fitness'tan
      belirgin şekilde iyi olmalı

    Farklı environment'ların fitness rekorları
    birbirleriyle karıştırılmaz.
    """

    def __init__(
        self,
        minimum_fitness_gain: float = 0.25,
    ) -> None:

        self.minimum_fitness_gain = (
            minimum_fitness_gain
        )

        # Eski sürüm uyumluluğu için tutuluyor.
        self.best_fitness_seen = 0.0

        # Yeni gerçek referans.
        self.best_fitness_seen_by_era: dict[
            int,
            float,
        ] = {}

        self.events: list[dict] = []

    # ========================================================
    # INSPECT
    # ========================================================

    def inspect(
        self,
        organism: Organism,
        is_novel: bool,
        *,
        era_id: int,
        era_name: str,
    ) -> dict | None:

        if not is_novel:
            return None

        # Generation Zero insan tarafından verilen
        # başlangıç noktasıdır; evrimsel sıçrama değildir.
        if organism.generation == 0:

            self.update_best_without_event(
                organism.fitness,
                era_id=era_id,
            )

            return None

        era_best = (
            self.best_fitness_seen_by_era
            .get(
                era_id,
                0.0,
            )
        )

        improvement = (
            organism.fitness
            - era_best
        )

        if (
            improvement
            < self.minimum_fitness_gain
        ):
            return None

        event = {
            "era_id":
                era_id,

            "era_name":
                era_name,

            "generation":
                organism.generation,

            "organism_id":
                organism.id,

            "fitness":
                organism.fitness,

            "fitness_gain":
                improvement,

            "error":
                organism.error,

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

            "task_errors":
                dict(
                    organism.task_errors
                ),

            "birth_mutations":
                list(
                    organism.birth_mutations
                ),
        }

        self.events.append(
            event
        )

        self.best_fitness_seen_by_era[
            era_id
        ] = organism.fitness

        self.best_fitness_seen = max(
            self.best_fitness_seen,
            organism.fitness,
        )

        return event

    # ========================================================
    # RECORD BASELINE WITHOUT EVENT
    # ========================================================

    def update_best_without_event(
        self,
        fitness: float,
        *,
        era_id: int,
    ) -> None:

        previous = (
            self.best_fitness_seen_by_era
            .get(
                era_id,
                0.0,
            )
        )

        if fitness > previous:

            self.best_fitness_seen_by_era[
                era_id
            ] = fitness

        if fitness > self.best_fitness_seen:

            self.best_fitness_seen = (
                fitness
            )

    # ========================================================
    # MIGRATION / BOOTSTRAP
    # ========================================================

    def set_era_baseline(
        self,
        era_id: int,
        fitness: float,
    ) -> None:

        if fitness <= 0:
            return

        self.best_fitness_seen_by_era[
            era_id
        ] = float(
            fitness
        )

        self.best_fitness_seen = max(
            self.best_fitness_seen,
            fitness,
        )

    # ========================================================
    # REPORTING
    # ========================================================

    def recent_events(
        self,
        count: int = 5,
        era_id: int | None = None,
    ) -> list[dict]:

        if era_id is None:

            return self.events[
                -count:
            ]

        filtered = [
            event
            for event
            in self.events
            if event.get(
                "era_id"
            ) == era_id
        ]

        return filtered[
            -count:
        ]

    def total_events(
        self,
        era_id: int | None = None,
    ) -> int:

        if era_id is None:

            return len(
                self.events
            )

        return sum(
            1
            for event
            in self.events
            if event.get(
                "era_id"
            ) == era_id
        )