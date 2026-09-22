# evolution_engine.py

from __future__ import annotations

import random
import statistics

from config import (
    ELITE_COUNT,
    POPULATION_SIZE,
)

from diversity_tracker import DiversityTracker
from environment import Environment
from evaluator import Evaluator
from evolution_event_detector import (
    EvolutionEventDetector,
)
from family_event_detector import (
    FamilyEventDetector,
)
from genome import Genome
from adaptation_tracker import (
    AdaptationTracker,
)
from cross_era_tester import (
    CrossEraTester,
)
from era_champion_tracker import (
    EraChampionTracker,
)
from module_ablation import (
    ModuleAblationTester,
)
from module_family_tracker import (
    ModuleFamilyTracker,
)
from module_lineage_tracker import (
    ModuleLineageTracker,
)
from module_tracker import ModuleTracker
from novelty_detector import NoveltyDetector
from organism import Organism
from vocabulary_event_tracker import (
    VocabularyEventTracker,
)
from ast_evolution_tracker import (
    ASTEvolutionTracker,
)
from dual_execution_validator import (
    DualExecutionValidator,
)
from generated_provenance_tracker import (
    GeneratedProvenanceTracker,
)


class EvolutionEngine:

    def __init__(self):

        self.generation = 0

        self.environment = Environment()

        self.evaluator = Evaluator(
            self.environment
        )

        self.diversity_tracker = (
            DiversityTracker()
        )

        self.novelty_detector = (
            NoveltyDetector()
        )

        self.event_detector = (
            EvolutionEventDetector(
                minimum_fitness_gain=0.25
            )
        )

        self.module_tracker = (
            ModuleTracker()
        )

        self.module_lineage_tracker = (
            ModuleLineageTracker()
        )

        self.module_family_tracker = (
            ModuleFamilyTracker()
        )

        self.family_event_detector = (
            FamilyEventDetector()
        )

        self.module_ablation_tester = (
            ModuleAblationTester(
                self.evaluator
            )
        )

        self.adaptation_tracker = (
            AdaptationTracker()
        )

        self.cross_era_tester = (
            CrossEraTester(
                self.environment
            )
        )

        self.era_champion_tracker = (
            EraChampionTracker()
        )

        self.vocabulary_event_tracker = (
            VocabularyEventTracker()
        )

        self.ast_evolution_tracker = (
            ASTEvolutionTracker()
        )

        self.dual_execution_validator = (
            DualExecutionValidator()
        )

        self.generated_provenance_tracker = (
            GeneratedProvenanceTracker()
        )

        self.population: list[
            Organism
        ] = []

        self.best_ever: Organism | None = None

        self.lineage_archive: dict[
            str,
            dict,
        ] = {}

        self.last_novel_events: list[
            dict
        ] = []

        self.last_major_events: list[
            dict
        ] = []

    def register_organism(
        self,
        organism: Organism,
    ) -> None:

        self.lineage_archive[
            organism.id
        ] = {
            "id":
                organism.id,

            "generation":
                organism.generation,

            "parent_id":
                organism.parent_id,

            "lineage_depth":
                organism.lineage_depth,

            "birth_mutations":
                list(
                    organism.birth_mutations
                ),

            "genome":
                organism.genome.describe(),
        }

    def create_generation_zero(
        self,
    ) -> None:

        self.population = []

        for _ in range(
            POPULATION_SIZE
        ):

            genome = (
                Genome.create_generation_zero()
            )

            organism = Organism(
                genome=genome,
                generation=0,
                parent_id=None,
                birth_mutations=[
                    "GENERATION_ZERO"
                ],
                lineage_depth=0,
            )

            self.population.append(
                organism
            )

            self.register_organism(
                organism
            )

    def evaluate_population(
        self,
    ) -> None:

        self.environment.set_generation(
            self.generation
        )

        # =================================================
        # V0.8.5 — EXECUTION ROUTING
        # =================================================
        #
        # DSL organisms:
        #     existing DSL interpreter = PRIMARY
        #
        # AST organisms:
        #     generated Python = PRIMARY
        #     AST interpreter   = SHADOW
        #
        # The fitness left on an AST organism after
        # validation is always the generated-Python
        # primary fitness.
        # =================================================

        self.dual_execution_validator.begin_python_primary_generation(
            self.generation
        )

        for organism in self.population:

            is_ast = (
                organism.genome.execution_mode
                == "AST"
                and organism.genome.ast_program
                is not None
            )

            is_arch = (
                organism.genome.execution_mode
                == "ARCH"
                and
                organism.genome
                .program_architecture
                is not None
            )

            # =============================================
            # DSL
            # =============================================

            if (
                not is_ast
                and not is_arch
            ):

                self.evaluator.evaluate(
                    organism
                )

                continue

            # =============================================
            # AST — GENERATED PYTHON PRIMARY
            # =============================================

            if is_ast:

                result = (
                    self.dual_execution_validator
                    .validate_python_primary(
                        organism=organism,
                        evaluator=self.evaluator,
                        generation=self.generation,
                    )
                )

                if (
                    result.error is not None
                    or not result.matched
                ):

                    raise RuntimeError(
                        "Python-primary execution "
                        "validation failed for "
                        f"{organism.id}: "
                        f"error={result.error}, "
                        f"difference="
                        f"{result.fitness_difference}"
                    )

                fingerprint = (
                    result.source_fingerprint
                )

                module_name = (
                    self
                    .dual_execution_validator
                    .runner
                    .module_name_for(
                        organism
                    )
                )

                self.generated_provenance_tracker.observe(
                    organism=organism,
                    generation=self.generation,
                    fingerprint=fingerprint,
                    module_name=module_name,
                )

                continue

            # =============================================
            # ARCH — GENERATED PYTHON PRIMARY
            # =============================================

            result = (
                self.dual_execution_validator
                .validate_architecture_python_primary(
                    organism=organism,
                    evaluator=self.evaluator,
                    generation=self.generation,
                )
            )

            if (
                result.error is not None
                or not result.matched
            ):

                raise RuntimeError(
                    "Architecture Python-primary "
                    "execution validation failed for "
                    f"{organism.id}: "
                    f"error={result.error}, "
                    f"difference="
                    f"{result.fitness_difference}"
                )

        self.module_lineage_tracker.inspect_population(
            self.population
        )

        self.module_family_tracker.update(
            population=self.population,
            lineage_tracker=(
                self.module_lineage_tracker
            ),
            generation=self.generation,
        )

        self.family_event_detector.update(
            family_report=(
                self.module_family_tracker
                .report()
            ),
            generation=self.generation,
            population_size=len(
                self.population
            ),
        )

        self.population.sort(
            key=lambda organism:
                organism.fitness,
            reverse=True,
        )

        self.vocabulary_event_tracker.inspect_population(
            population=self.population,
            generation=self.generation,
        )

        self.ast_evolution_tracker.inspect_population(
            population=self.population,
            generation=self.generation,
        )

        self.last_novel_events = []
        self.last_major_events = []

        environment = (
            self.environment
            .era_report()
        )

        current_era_id = (
            environment[
                "era_id"
            ]
        )

        current_era_name = (
            environment[
                "name"
            ]
        )

        for organism in self.population:

            novelty_event = (
                self.novelty_detector
                .inspect(
                    organism
                )
            )

            is_novel = (
                novelty_event
                is not None
            )

            if novelty_event is not None:
                self.last_novel_events.append(
                    novelty_event
                )

            major_event = (
                self.event_detector
                .inspect(
                    organism,
                    is_novel=is_novel,
                    era_id=current_era_id,
                    era_name=current_era_name,
                )
            )

            if major_event is not None:
                self.last_major_events.append(
                    major_event
                )

        current_best = (
            self.population[0]
        )

        current_era_id = (
            self.environment
            .era_report()[
                "era_id"
            ]
        )

        self.era_champion_tracker.update(
            era_id=current_era_id,
            organism=current_best,
        )

        environment = (
            self.environment
            .era_report()
        )

        previous_era_id = (
            environment[
                "era_id"
            ]
            - 1
        )

        previous_reference = (
            current_best.fitness
        )

        if previous_era_id >= 1:

            previous_champion = (
                self
                .era_champion_tracker
                .get(
                    previous_era_id
                )
            )

            if (
                previous_champion
                is not None
            ):

                standardized = (
                    self.cross_era_tester
                    .test(
                        previous_champion,
                        previous_era_id,
                    )
                )

                if standardized[
                    "valid"
                ]:

                    previous_reference = (
                        standardized[
                            "fitness"
                        ]
                    )

        elif (
            self.best_ever
            is not None
        ):

            previous_reference = (
                current_best.fitness
            )

        self.adaptation_tracker.update(
            era_id=environment[
                "era_id"
            ],

            era_name=environment[
                "name"
            ],

            generation=self.generation,

            current_best_fitness=(
                current_best.fitness
            ),

            previous_reference=(
                previous_reference
            ),
        )

        self.event_detector.update_best_without_event(
            current_best.fitness,
            era_id=current_era_id,
        )

        if (
            self.best_ever is None
            or current_best.fitness
            > self.best_ever.fitness
        ):
            self.best_ever = (
                current_best
            )

    def create_next_generation(
        self,
    ) -> None:

        elites = self.population[
            :ELITE_COUNT
        ]

        next_generation: list[
            Organism
        ] = []

        champion = elites[0]

        champion_child = Organism(
            genome=(
                champion
                .genome
                .clone()
            ),

            generation=(
                self.generation + 1
            ),

            parent_id=champion.id,

            birth_mutations=[
                "ELITE_COPY"
            ],

            lineage_depth=(
                champion.lineage_depth
                + 1
            ),
        )

        next_generation.append(
            champion_child
        )

        self.register_organism(
            champion_child
        )

        while (
            len(next_generation)
            < POPULATION_SIZE
        ):

            parent = random.choice(
                elites
            )

            child = (
                parent.create_child(
                    generation=(
                        self.generation
                        + 1
                    )
                )
            )

            next_generation.append(
                child
            )

            self.register_organism(
                child
            )

        self.population = (
            next_generation
        )

        self.generation += 1

    def average_fitness(
        self,
    ) -> float:

        return statistics.mean(
            organism.fitness
            for organism
            in self.population
        )

    def diversity_report(
        self,
    ) -> dict:

        return (
            self.diversity_tracker
            .analyze(
                self.population
            )
        )

    def novelty_report(
        self,
    ) -> dict:

        return {
            "total_structures":
                self.novelty_detector
                .total_structures(),

            "new_this_generation":
                len(
                    self.last_novel_events
                ),

            "recent_events":
                self.novelty_detector
                .recent_events(5),
        }

    def major_event_report(
        self,
    ) -> dict:

        environment = (
            self.environment_report()
        )

        era_id = (
            environment[
                "era_id"
            ]
        )

        return {
            "era_id":
                era_id,

            "era_name":
                environment[
                    "name"
                ],

            "total_events":
                self.event_detector
                .total_events(),

            "era_events":
                self.event_detector
                .total_events(
                    era_id=era_id
                ),

            "new_this_generation":
                len(
                    self.last_major_events
                ),

            "recent_events":
                self.event_detector
                .recent_events(
                    count=10,
                    era_id=era_id,
                ),

            "all_recent_events":
                self.event_detector
                .recent_events(
                    count=10
                ),

            "era_best_reference":
                self.event_detector
                .best_fitness_seen_by_era
                .get(
                    era_id,
                    0.0,
                ),
        }

    def module_report(
        self,
    ) -> dict:

        return (
            self.module_tracker
            .analyze_population(
                self.population
            )
        )

    def vocabulary_event_report(
        self,
    ) -> dict:

        return (
            self.vocabulary_event_tracker
            .report()
        )

    def ast_evolution_report(
        self,
    ) -> dict:

        return (
            self.ast_evolution_tracker
            .report()
        )

    def dual_execution_report(
        self,
    ) -> dict:

        return (
            self.dual_execution_validator
            .report()
        )

    def generated_provenance_report(
        self,
    ) -> dict:

        return (
            self.generated_provenance_tracker
            .report()
        )

    def organism_module_report(
        self,
        organism: Organism,
    ) -> dict:

        return (
            self.module_tracker
            .analyze_organism(
                organism
            )
        )

    def module_lineage_report(
        self,
    ) -> dict:

        return (
            self.module_lineage_tracker
            .population_summary(
                self.population
            )
        )

    def module_family_report(
        self,
    ) -> dict:

        return (
            self.module_family_tracker
            .report()
        )

    def family_event_report(
        self,
    ) -> dict:

        return (
            self.family_event_detector
            .report()
        )

    def environment_report(
        self,
    ) -> dict:

        self.environment.set_generation(
            self.generation
        )

        return (
            self.environment
            .era_report()
        )

    def adaptation_report(
        self,
    ) -> dict:

        return (
            self.adaptation_tracker
            .report(
                self.generation
            )
        )

    def cross_era_report(
        self,
        organism: Organism,
    ) -> list[dict]:

        self.environment.set_generation(
            self.generation
        )

        current_era = (
            self.environment
            .era_report()[
                "era_id"
            ]
        )

        eras = list(
            range(
                1,
                current_era + 1,
            )
        )

        return (
            self.cross_era_tester
            .compare(
                organism,
                eras,
            )
        )

    def era_transfer_matrix(
        self,
    ) -> list[dict]:

        self.environment.set_generation(
            self.generation
        )

        current_era = (
            self.environment
            .era_report()[
                "era_id"
            ]
        )

        rows = []

        for champion_era in range(
            1,
            current_era + 1,
        ):

            champion = (
                self.era_champion_tracker
                .get(
                    champion_era
                )
            )

            if champion is None:
                continue

            results = (
                self.cross_era_tester
                .compare(
                    champion,
                    list(
                        range(
                            1,
                            current_era + 1,
                        )
                    ),
                )
            )

            rows.append(
                {
                    "champion_era":
                        champion_era,

                    "organism_id":
                        champion.id,

                    "born_generation":
                        champion.generation,

                    "results":
                        results,
                }
            )

        return rows

    def ablation_report(
        self,
        organism: Organism,
    ) -> list[dict]:

        return (
            self.module_ablation_tester
            .test_all_modules(
                organism
            )
        )

    def trace_module_lineage(
        self,
        module_uid: str,
        max_depth: int = 15,
    ) -> list[dict]:

        return (
            self.module_lineage_tracker
            .trace(
                module_uid,
                max_depth=max_depth,
            )
        )

    def trace_lineage(
        self,
        organism_id: str,
        max_depth: int = 15,
    ) -> list[dict]:

        lineage: list[dict] = []

        current_id: str | None = (
            organism_id
        )

        while (
            current_id is not None
            and len(lineage)
            < max_depth
        ):

            record = (
                self.lineage_archive
                .get(
                    current_id
                )
            )

            if record is None:
                break

            lineage.append(
                record
            )

            current_id = (
                record[
                    "parent_id"
                ]
            )

        return lineage

    def archive_size(
        self,
    ) -> int:

        return len(
            self.lineage_archive
        )