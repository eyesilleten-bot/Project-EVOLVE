# ast_evolution_tracker.py

from __future__ import annotations


class ASTEvolutionTracker:

    def __init__(self):

        self.events: list[dict] = []
        self.last_events: list[dict] = []

        self.baseline_generation = None

        self.first_birth_seen = False
        self.first_survival_seen = False

        self.first_param_seen = False
        self.first_replace_seen = False
        self.first_insert_seen = False
        self.first_delete_seen = False
        self.first_duplicate_seen = False

        self.thresholds_seen = {
            20: False,
            30: False,
            40: False,
            50: False,
        }

        self.first_ast_champion_seen = False

        self.first_bridge_seen = False
        self.first_bridge_survival_seen = False

        self.first_hybrid_seen = False
        self.first_hybrid_survival_seen = False

        self.first_pure_seen = False
        self.first_pure_survival_seen = False

        self.first_pure_champion_seen = False

        self.first_pure_from_bridge_seen = False
        self.first_pure_from_bridge_survival_seen = False

        self.pure_thresholds_seen = {
            20: False,
            30: False,
            40: False,
            50: False,
        }

        self.known_ast_organisms: set[str] = set()

        self.previous_ast_ids: set[str] = set()

        self.previous_bridge_ids: set[str] = set()
        self.previous_hybrid_ids: set[str] = set()
        self.previous_pure_ids: set[str] = set()
        self.previous_pure_from_bridge_ids: set[str] = set()

        self.ast_presence_last_generation = False

        self.last_population_report = {
            "generation": 0,
            "population_size": 0,
            "ast_count": 0,
            "ast_fraction": 0.0,
            "bridge_count": 0,
            "hybrid_count": 0,
            "pure_count": 0,
            "best_ast_fitness": None,
            "best_ast_id": None,
            "max_nodes": 0,
            "max_depth": 0,
            "oldest_birth_generation": None,
        }

    # -----------------------------------------------------
    # EVENT
    # -----------------------------------------------------

    def _record(
        self,
        event_type: str,
        generation: int,
        **data,
    ) -> dict:

        event = {
            "event_type": event_type,
            "generation": generation,
            **data,
        }

        self.events.append(event)
        self.last_events.append(event)

        return event

    # -----------------------------------------------------
    # HELPERS
    # -----------------------------------------------------

    @staticmethod
    def _ast_organisms(
        population,
    ):

        return [
            organism
            for organism in population
            if (
                organism.genome.ast_program
                is not None
                and organism.genome.execution_mode
                == "AST"
            )
        ]

    @staticmethod
    def _classify_ast(
        organism,
    ) -> str:

        genome = organism.genome

        if genome.ast_program is None:
            return "NONE"

        if genome.execution_mode != "AST":
            return "NONE"

        if genome.ast_is_pure():
            return "PURE"

        if genome.ast_is_hybrid():
            return "HYBRID"

        if genome.ast_uses_legacy_main():
            return "BRIDGE"

        return "AST"

    @staticmethod
    def _is_pure_from_bridge(
        organism,
    ) -> bool:

        genome = organism.genome

        return (
            genome.execution_mode == "AST"
            and genome.ast_program is not None
            and genome.ast_is_pure()
            and genome.ast_program.origin
            == "BRIDGE_SEED"
        )

    @staticmethod
    def _ast_snapshot(
        organism,
    ) -> dict:

        program = organism.genome.ast_program

        return {
            "organism_id":
                organism.id,

            "fitness":
                organism.fitness,

            "parent_id":
                organism.parent_id,

            "lineage_depth":
                organism.lineage_depth,

            "birth_mutations":
                list(
                    organism.birth_mutations
                ),

            "ast_class":
                ASTEvolutionTracker
                ._classify_ast(
                    organism
                ),

            "ast_origin":
                program.origin,

            "ast_birth_generation":
                program.birth_generation,

            "nodes":
                program.node_count(),

            "depth":
                program.depth(),

            "ast":
                program.describe(),

            "ast_program":
                program.to_dict(),
        }

    # -----------------------------------------------------
    # BASELINE
    # -----------------------------------------------------

    def bootstrap(
        self,
        population,
        generation: int,
    ) -> None:

        self.baseline_generation = (
            generation
        )

        ast_population = (
            self._ast_organisms(
                population
            )
        )

        bridge_population = [
            o
            for o in ast_population
            if self._classify_ast(o)
            == "BRIDGE"
        ]

        hybrid_population = [
            o
            for o in ast_population
            if self._classify_ast(o)
            == "HYBRID"
        ]

        pure_population = [
            o
            for o in ast_population
            if self._classify_ast(o)
            == "PURE"
        ]

        self.previous_ast_ids = {
            organism.id
            for organism in ast_population
        }

        self.previous_bridge_ids = {
            o.id
            for o in bridge_population
        }

        self.previous_hybrid_ids = {
            o.id
            for o in hybrid_population
        }

        self.previous_pure_ids = {
            o.id
            for o in pure_population
        }

        self.known_ast_organisms.update(
            self.previous_ast_ids
        )

        if ast_population:

            self.first_birth_seen = True
            self.first_survival_seen = True

        if bridge_population:
            self.first_bridge_seen = True

        if hybrid_population:
            self.first_hybrid_seen = True

        if pure_population:
            self.first_pure_seen = True

        for organism in ast_population:

            fitness = organism.fitness

            for threshold in (
                20,
                30,
                40,
                50,
            ):

                if fitness >= threshold:
                    self.thresholds_seen[
                        threshold
                    ] = True

            if (
                self._classify_ast(organism)
                == "PURE"
            ):

                for threshold in (
                    20,
                    30,
                    40,
                    50,
                ):

                    if fitness >= threshold:
                        self.pure_thresholds_seen[
                            threshold
                        ] = True

        self._update_population_report(
            population,
            generation,
        )

        self.ast_presence_last_generation = bool(
            ast_population
        )

    # -----------------------------------------------------
    # MUTATION HISTORY
    # -----------------------------------------------------

    def _inspect_mutations(
        self,
        organism,
        generation: int,
    ) -> None:

        mutations = (
            organism.birth_mutations
            or []
        )

        for mutation in mutations:

            if (
                mutation.startswith(
                    "AST_"
                )
                and not mutation.startswith(
                    "CREATE_AST"
                )
            ):

                self._record(
                    "AST_MUTATION",
                    generation,
                    mutation=mutation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if mutation.startswith(
                "CREATE_AST"
            ):

                snapshot = (
                    self._ast_snapshot(
                        organism
                    )
                )

                self._record(
                    "AST_BIRTH",
                    generation,
                    mutation=mutation,
                    **snapshot,
                )

                if not self.first_birth_seen:

                    self.first_birth_seen = True

                    self._record(
                        "FIRST_AST_BIRTH",
                        generation,
                        mutation=mutation,
                        **snapshot,
                    )

            if (
                (
                    mutation.startswith(
                        "AST_PARAM"
                    )
                    or mutation.startswith(
                        "AST_CONTEXT"
                    )
                )
                and not self.first_param_seen
            ):

                self.first_param_seen = True

                self._record(
                    "FIRST_AST_PARAMETER_MUTATION",
                    generation,
                    mutation=mutation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                mutation.startswith(
                    "AST_REPLACE"
                )
                and not self.first_replace_seen
            ):

                self.first_replace_seen = True

                self._record(
                    "FIRST_AST_REPLACEMENT",
                    generation,
                    mutation=mutation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                mutation.startswith(
                    "AST_INSERT"
                )
                and not self.first_insert_seen
            ):

                self.first_insert_seen = True

                self._record(
                    "FIRST_AST_INSERTION",
                    generation,
                    mutation=mutation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                mutation.startswith(
                    "AST_DELETE"
                )
                and not self.first_delete_seen
            ):

                self.first_delete_seen = True

                self._record(
                    "FIRST_AST_DELETION",
                    generation,
                    mutation=mutation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                mutation.startswith(
                    "AST_DUPLICATE"
                )
                and not self.first_duplicate_seen
            ):

                self.first_duplicate_seen = True

                self._record(
                    "FIRST_AST_DUPLICATION",
                    generation,
                    mutation=mutation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

    # -----------------------------------------------------
    # POPULATION REPORT
    # -----------------------------------------------------

    def _update_population_report(
        self,
        population,
        generation: int,
    ) -> None:

        ast_population = (
            self._ast_organisms(
                population
            )
        )

        if ast_population:

            best = max(
                ast_population,
                key=lambda o: o.fitness,
            )

            max_nodes = max(
                organism.genome
                .ast_node_count()

                for organism
                in ast_population
            )

            max_depth = max(
                organism.genome
                .ast_depth()

                for organism
                in ast_population
            )

            births = [
                organism.genome
                .ast_program
                .birth_generation

                for organism
                in ast_population
            ]

            oldest = min(births)

            best_fitness = (
                best.fitness
            )

            best_id = best.id

        else:

            max_nodes = 0
            max_depth = 0
            oldest = None
            best_fitness = None
            best_id = None

        bridge_count = sum(
            1
            for o in ast_population
            if self._classify_ast(o)
            == "BRIDGE"
        )

        hybrid_count = sum(
            1
            for o in ast_population
            if self._classify_ast(o)
            == "HYBRID"
        )

        pure_count = sum(
            1
            for o in ast_population
            if self._classify_ast(o)
            == "PURE"
        )

        size = len(population)

        self.last_population_report = {
            "generation":
                generation,

            "population_size":
                size,

            "ast_count":
                len(ast_population),

            "ast_fraction":
                (
                    len(ast_population)
                    / size
                    if size
                    else 0.0
                ),

            "bridge_count":
                bridge_count,

            "hybrid_count":
                hybrid_count,

            "pure_count":
                pure_count,

            "best_ast_fitness":
                best_fitness,

            "best_ast_id":
                best_id,

            "max_nodes":
                max_nodes,

            "max_depth":
                max_depth,

            "oldest_birth_generation":
                oldest,
        }

    # -----------------------------------------------------
    # INSPECTION
    # -----------------------------------------------------

    def inspect_population(
        self,
        population,
        generation: int,
    ) -> None:

        self.last_events = []

        ast_population = (
            self._ast_organisms(
                population
            )
        )

        bridge_population = [
            o
            for o in ast_population
            if self._classify_ast(o)
            == "BRIDGE"
        ]

        hybrid_population = [
            o
            for o in ast_population
            if self._classify_ast(o)
            == "HYBRID"
        ]

        pure_population = [
            o
            for o in ast_population
            if self._classify_ast(o)
            == "PURE"
        ]

        pure_from_bridge_population = [
            o
            for o in ast_population
            if self._is_pure_from_bridge(o)
        ]

        current_ids = {
            organism.id
            for organism
            in ast_population
        }

        current_presence = bool(
            ast_population
        )

        if (
            self.ast_presence_last_generation
            and not current_presence
        ):

            self._record(
                "AST_EXTINCTION",
                generation,
            )

        elif (
            not self.ast_presence_last_generation
            and current_presence
            and self.first_birth_seen
        ):

            self._record(
                "AST_REAPPEARANCE",
                generation,
            )

        # ---------------------------------------------
        # NEW AST ORGANISMS / MUTATION EVENTS
        # ---------------------------------------------

        for organism in ast_population:

            if (
                organism.id
                not in self.known_ast_organisms
            ):

                self._inspect_mutations(
                    organism,
                    generation,
                )

                self.known_ast_organisms.add(
                    organism.id
                )

            ast_class = (
                self._classify_ast(
                    organism
                )
            )

            if (
                ast_class == "BRIDGE"
                and not self.first_bridge_seen
            ):

                self.first_bridge_seen = True

                self._record(
                    "FIRST_BRIDGE_AST",
                    generation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                ast_class == "HYBRID"
                and not self.first_hybrid_seen
            ):

                self.first_hybrid_seen = True

                self._record(
                    "FIRST_HYBRID_AST",
                    generation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                ast_class == "PURE"
                and not self.first_pure_seen
            ):

                self.first_pure_seen = True

                self._record(
                    "FIRST_PURE_AST",
                    generation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

            if (
                self._is_pure_from_bridge(
                    organism
                )
                and not self.first_pure_from_bridge_seen
            ):

                self.first_pure_from_bridge_seen = True

                self._record(
                    "FIRST_PURE_AST_FROM_BRIDGE_LINEAGE",
                    generation,
                    **self._ast_snapshot(
                        organism
                    ),
                )

        # ---------------------------------------------
        # FIRST SURVIVAL
        #
        # AST organism existed previous generation and
        # AST lineage still exists now through parent_id.
        # ---------------------------------------------

        if (
            not self.first_survival_seen
            and self.previous_ast_ids
        ):

            surviving = [
                organism

                for organism
                in ast_population

                if (
                    organism.parent_id
                    in self.previous_ast_ids
                )
            ]

            if surviving:

                best = max(
                    surviving,
                    key=lambda o: o.fitness,
                )

                self.first_survival_seen = True

                self._record(
                    "FIRST_AST_LINEAGE_SURVIVAL",
                    generation,
                    **self._ast_snapshot(
                        best
                    ),
                )

        if (
            not self.first_bridge_survival_seen
            and self.previous_bridge_ids
        ):

            survivors = [
                o
                for o in bridge_population
                if o.parent_id
                in self.previous_bridge_ids
            ]

            if survivors:

                best = max(
                    survivors,
                    key=lambda o: o.fitness,
                )

                self.first_bridge_survival_seen = True

                self._record(
                    "FIRST_BRIDGE_SURVIVAL",
                    generation,
                    **self._ast_snapshot(
                        best
                    ),
                )

        if (
            not self.first_hybrid_survival_seen
            and self.previous_hybrid_ids
        ):

            survivors = [
                o
                for o in hybrid_population
                if o.parent_id
                in self.previous_hybrid_ids
            ]

            if survivors:

                best = max(
                    survivors,
                    key=lambda o: o.fitness,
                )

                self.first_hybrid_survival_seen = True

                self._record(
                    "FIRST_HYBRID_SURVIVAL",
                    generation,
                    **self._ast_snapshot(
                        best
                    ),
                )

        if (
            not self.first_pure_survival_seen
            and self.previous_pure_ids
        ):

            survivors = [
                o
                for o in pure_population
                if o.parent_id
                in self.previous_pure_ids
            ]

            if survivors:

                best = max(
                    survivors,
                    key=lambda o: o.fitness,
                )

                self.first_pure_survival_seen = True

                self._record(
                    "FIRST_PURE_AST_SURVIVAL",
                    generation,
                    **self._ast_snapshot(
                        best
                    ),
                )

        if (
            not self.first_pure_from_bridge_survival_seen
            and self.previous_pure_from_bridge_ids
        ):

            survivors = [
                o
                for o
                in pure_from_bridge_population
                if o.parent_id
                in self.previous_pure_from_bridge_ids
            ]

            if survivors:

                best = max(
                    survivors,
                    key=lambda o: o.fitness,
                )

                self.first_pure_from_bridge_survival_seen = True

                self._record(
                    "FIRST_PURE_FROM_BRIDGE_SURVIVAL",
                    generation,
                    **self._ast_snapshot(
                        best
                    ),
                )

        # ---------------------------------------------
        # FITNESS THRESHOLDS
        # ---------------------------------------------

        for threshold in (
            20,
            30,
            40,
            50,
        ):

            if self.thresholds_seen[
                threshold
            ]:
                continue

            candidates = [
                organism

                for organism
                in ast_population

                if (
                    organism.fitness
                    >= threshold
                )
            ]

            if not candidates:
                continue

            best = max(
                candidates,
                key=lambda o: o.fitness,
            )

            self.thresholds_seen[
                threshold
            ] = True

            self._record(
                f"FIRST_AST_ABOVE_{threshold}",
                generation,
                threshold=threshold,
                **self._ast_snapshot(
                    best
                ),
            )

        for threshold in (
            20,
            30,
            40,
            50,
        ):

            if self.pure_thresholds_seen[
                threshold
            ]:
                continue

            candidates = [
                o
                for o in pure_population
                if o.fitness >= threshold
            ]

            if not candidates:
                continue

            best = max(
                candidates,
                key=lambda o: o.fitness,
            )

            self.pure_thresholds_seen[
                threshold
            ] = True

            self._record(
                f"FIRST_PURE_AST_ABOVE_{threshold}",
                generation,
                threshold=threshold,
                **self._ast_snapshot(
                    best
                ),
            )

        # ---------------------------------------------
        # FIRST AST POPULATION CHAMPION
        # ---------------------------------------------

        if (
            ast_population
            and not self.first_ast_champion_seen
        ):

            overall_best = max(
                population,
                key=lambda o: o.fitness,
            )

            if (
                overall_best.genome
                .execution_mode
                == "AST"
                and overall_best.genome
                .ast_program
                is not None
            ):

                self.first_ast_champion_seen = (
                    True
                )

                self._record(
                    "FIRST_AST_POPULATION_CHAMPION",
                    generation,
                    **self._ast_snapshot(
                        overall_best
                    ),
                )

        if (
            pure_population
            and not self.first_pure_champion_seen
        ):

            overall_best = max(
                population,
                key=lambda o: o.fitness,
            )

            if (
                self._classify_ast(
                    overall_best
                )
                == "PURE"
            ):

                self.first_pure_champion_seen = True

                self._record(
                    "FIRST_PURE_AST_POPULATION_CHAMPION",
                    generation,
                    **self._ast_snapshot(
                        overall_best
                    ),
                )

        self._update_population_report(
            population,
            generation,
        )

        self.previous_ast_ids = (
            current_ids
        )

        self.previous_bridge_ids = {
            o.id
            for o in bridge_population
        }

        self.previous_hybrid_ids = {
            o.id
            for o in hybrid_population
        }

        self.previous_pure_ids = {
            o.id
            for o in pure_population
        }

        self.previous_pure_from_bridge_ids = {
            o.id
            for o
            in pure_from_bridge_population
        }

        self.ast_presence_last_generation = (
            current_presence
        )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    def report(
        self,
    ) -> dict:

        return {
            "baseline_generation":
                self.baseline_generation,

            "event_count":
                len(self.events),

            "flags": {
                "first_birth_seen":
                    self.first_birth_seen,

                "first_survival_seen":
                    self.first_survival_seen,

                "first_param_seen":
                    self.first_param_seen,

                "first_replace_seen":
                    self.first_replace_seen,

                "first_insert_seen":
                    self.first_insert_seen,

                "first_delete_seen":
                    self.first_delete_seen,

                "first_duplicate_seen":
                    self.first_duplicate_seen,

                "first_ast_champion_seen":
                    self.first_ast_champion_seen,

                "first_bridge_seen":
                    self.first_bridge_seen,

                "first_bridge_survival_seen":
                    self.first_bridge_survival_seen,

                "first_hybrid_seen":
                    self.first_hybrid_seen,

                "first_hybrid_survival_seen":
                    self.first_hybrid_survival_seen,

                "first_pure_seen":
                    self.first_pure_seen,

                "first_pure_survival_seen":
                    self.first_pure_survival_seen,

                "first_pure_champion_seen":
                    self.first_pure_champion_seen,

                "first_pure_from_bridge_seen":
                    self.first_pure_from_bridge_seen,

                "first_pure_from_bridge_survival_seen":
                    self.first_pure_from_bridge_survival_seen,

                "thresholds_seen":
                    dict(
                        self.thresholds_seen
                    ),

                "pure_thresholds_seen":
                    dict(
                        self.pure_thresholds_seen
                    ),
            },

            "population":
                dict(
                    self.last_population_report
                ),

            "recent_events":
                list(
                    self.last_events
                ),

            "events":
                list(
                    self.events
                ),
        }

    # -----------------------------------------------------
    # SAVE / LOAD
    # -----------------------------------------------------

    def to_state(
        self,
    ) -> dict:

        return {
            "events":
                list(self.events),

            "baseline_generation":
                self.baseline_generation,

            "first_birth_seen":
                self.first_birth_seen,

            "first_survival_seen":
                self.first_survival_seen,

            "first_param_seen":
                self.first_param_seen,

            "first_replace_seen":
                self.first_replace_seen,

            "first_insert_seen":
                self.first_insert_seen,

            "first_delete_seen":
                self.first_delete_seen,

            "first_duplicate_seen":
                self.first_duplicate_seen,

            "first_ast_champion_seen":
                self.first_ast_champion_seen,

            "first_bridge_seen":
                self.first_bridge_seen,

            "first_bridge_survival_seen":
                self.first_bridge_survival_seen,

            "first_hybrid_seen":
                self.first_hybrid_seen,

            "first_hybrid_survival_seen":
                self.first_hybrid_survival_seen,

            "first_pure_seen":
                self.first_pure_seen,

            "first_pure_survival_seen":
                self.first_pure_survival_seen,

            "first_pure_champion_seen":
                self.first_pure_champion_seen,

            "first_pure_from_bridge_seen":
                self.first_pure_from_bridge_seen,

            "first_pure_from_bridge_survival_seen":
                self.first_pure_from_bridge_survival_seen,

            "thresholds_seen":
                {
                    str(key): value
                    for key, value
                    in self.thresholds_seen.items()
                },

            "pure_thresholds_seen":
                {
                    str(k): v
                    for k, v
                    in self.pure_thresholds_seen.items()
                },

            "known_ast_organisms":
                sorted(
                    self.known_ast_organisms
                ),

            "previous_ast_ids":
                sorted(
                    self.previous_ast_ids
                ),

            "previous_bridge_ids":
                sorted(
                    self.previous_bridge_ids
                ),

            "previous_hybrid_ids":
                sorted(
                    self.previous_hybrid_ids
                ),

            "previous_pure_ids":
                sorted(
                    self.previous_pure_ids
                ),

            "previous_pure_from_bridge_ids":
                sorted(
                    self.previous_pure_from_bridge_ids
                ),

            "ast_presence_last_generation":
                self.ast_presence_last_generation,

            "last_population_report":
                dict(
                    self.last_population_report
                ),
        }

    def load_state(
        self,
        data: dict,
    ) -> None:

        self.events = list(
            data.get(
                "events",
                [],
            )
        )

        self.last_events = []

        self.baseline_generation = (
            data.get(
                "baseline_generation"
            )
        )

        self.first_birth_seen = bool(
            data.get(
                "first_birth_seen",
                False,
            )
        )

        self.first_survival_seen = bool(
            data.get(
                "first_survival_seen",
                False,
            )
        )

        self.first_param_seen = bool(
            data.get(
                "first_param_seen",
                False,
            )
        )

        self.first_replace_seen = bool(
            data.get(
                "first_replace_seen",
                False,
            )
        )

        self.first_insert_seen = bool(
            data.get(
                "first_insert_seen",
                False,
            )
        )

        self.first_delete_seen = bool(
            data.get(
                "first_delete_seen",
                False,
            )
        )

        self.first_duplicate_seen = bool(
            data.get(
                "first_duplicate_seen",
                False,
            )
        )

        self.first_ast_champion_seen = bool(
            data.get(
                "first_ast_champion_seen",
                False,
            )
        )

        self.first_bridge_seen = bool(
            data.get(
                "first_bridge_seen",
                False,
            )
        )

        self.first_bridge_survival_seen = bool(
            data.get(
                "first_bridge_survival_seen",
                False,
            )
        )

        self.first_hybrid_seen = bool(
            data.get(
                "first_hybrid_seen",
                False,
            )
        )

        self.first_hybrid_survival_seen = bool(
            data.get(
                "first_hybrid_survival_seen",
                False,
            )
        )

        self.first_pure_seen = bool(
            data.get(
                "first_pure_seen",
                False,
            )
        )

        self.first_pure_survival_seen = bool(
            data.get(
                "first_pure_survival_seen",
                False,
            )
        )

        self.first_pure_champion_seen = bool(
            data.get(
                "first_pure_champion_seen",
                False,
            )
        )

        self.first_pure_from_bridge_seen = bool(
            data.get(
                "first_pure_from_bridge_seen",
                False,
            )
        )

        self.first_pure_from_bridge_survival_seen = bool(
            data.get(
                "first_pure_from_bridge_survival_seen",
                False,
            )
        )

        raw_thresholds = data.get(
            "thresholds_seen",
            {},
        )

        self.thresholds_seen = {
            threshold:
                bool(
                    raw_thresholds.get(
                        str(threshold),
                        raw_thresholds.get(
                            threshold,
                            False,
                        ),
                    )
                )

            for threshold in (
                20,
                30,
                40,
                50,
            )
        }

        raw_pure_thresholds = data.get(
            "pure_thresholds_seen",
            {},
        )

        self.pure_thresholds_seen = {
            threshold:
                bool(
                    raw_pure_thresholds.get(
                        str(threshold),
                        raw_pure_thresholds.get(
                            threshold,
                            False,
                        ),
                    )
                )

            for threshold in (
                20,
                30,
                40,
                50,
            )
        }

        self.known_ast_organisms = set(
            data.get(
                "known_ast_organisms",
                [],
            )
        )

        self.previous_ast_ids = set(
            data.get(
                "previous_ast_ids",
                [],
            )
        )

        self.previous_bridge_ids = set(
            data.get(
                "previous_bridge_ids",
                [],
            )
        )

        self.previous_hybrid_ids = set(
            data.get(
                "previous_hybrid_ids",
                [],
            )
        )

        self.previous_pure_ids = set(
            data.get(
                "previous_pure_ids",
                [],
            )
        )

        self.previous_pure_from_bridge_ids = set(
            data.get(
                "previous_pure_from_bridge_ids",
                [],
            )
        )

        self.last_population_report = dict(
            data.get(
                "last_population_report",
                self.last_population_report,
            )
        )

        self.ast_presence_last_generation = bool(
            data.get(
                "ast_presence_last_generation",
                bool(
                    self.previous_ast_ids
                ),
            )
        )
