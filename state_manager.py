# state_manager.py

from __future__ import annotations

import json
import os
import random
import time
from typing import Any

from genome import (
    Genome,
    Instruction,
)
from ast_program import ASTProgram
from program_architecture import (
    ProgramArchitecture,
)
from evolved_language import EvolvedLanguage
from organism import Organism


STATE_VERSION = "0.2.3"

STATE_FILE = "evolve_state.json"

TEMP_STATE_FILE = (
    "evolve_state.tmp"
)


class StateManager:

    # ---------------------------------------------------------
    # GENERIC HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _tuple_to_list(
        value: Any,
    ) -> Any:

        if isinstance(value, tuple):

            return [
                StateManager._tuple_to_list(
                    item
                )
                for item in value
            ]

        if isinstance(value, list):

            return [
                StateManager._tuple_to_list(
                    item
                )
                for item in value
            ]

        if isinstance(value, dict):

            return {
                key:
                    StateManager
                    ._tuple_to_list(
                        item
                    )

                for key, item
                in value.items()
            }

        return value

    @staticmethod
    def _list_to_tuple(
        value: Any,
    ) -> Any:

        if isinstance(value, list):

            return tuple(
                StateManager
                ._list_to_tuple(
                    item
                )
                for item in value
            )

        return value

    # ---------------------------------------------------------
    # INSTRUCTIONS
    # ---------------------------------------------------------

    @staticmethod
    def instruction_to_dict(
        instruction: Instruction,
    ) -> dict:

        return {
            "operation":
                instruction.operation,

            "value":
                instruction.value,

            "context":
                instruction.context,

            "offset":
                instruction.offset,

            "module_id":
                instruction.module_id,

            "macro_id":
                instruction.macro_id,
        }

    @staticmethod
    def instruction_from_dict(
        data: dict,
    ) -> Instruction:

        return Instruction(
            operation=data[
                "operation"
            ],

            value=data.get(
                "value",
                0.0,
            ),

            context=data.get(
                "context",
                0,
            ),

            offset=data.get(
                "offset",
                1,
            ),

            module_id=data.get(
                "module_id"
            ),

            macro_id=data.get(
                "macro_id"
            ),
        )

    # ---------------------------------------------------------
    # GENOME
    # ---------------------------------------------------------

    @classmethod
    def genome_to_dict(
        cls,
        genome: Genome,
    ) -> dict:

        return {
            "instructions": [
                cls.instruction_to_dict(
                    instruction
                )
                for instruction
                in genome.instructions
            ],

            "modules": {
                str(module_id): [
                    cls.instruction_to_dict(
                        instruction
                    )
                    for instruction
                    in module
                ]

                for module_id, module
                in genome.modules.items()
            },

            "module_meta": {
                str(module_id):
                    dict(metadata)

                for module_id, metadata
                in genome.module_meta.items()
            },

            "macros": {
                str(macro_id): [
                    cls.instruction_to_dict(
                        instruction
                    )

                    for instruction
                    in macro
                ]

                for macro_id, macro
                in genome.macros.items()
            },

            "macro_meta": {
                str(macro_id):
                    dict(metadata)

                for macro_id, metadata
                in genome.macro_meta.items()
            },

            "next_macro_id":
                genome.next_macro_id,

            "next_module_id":
                genome.next_module_id,

            "ast_program": (
                genome.ast_program.to_dict()
                if genome.ast_program
                is not None
                else None
            ),

            "program_architecture": (
                genome
                .program_architecture
                .to_dict()

                if genome
                .program_architecture
                is not None

                else None
            ),

            "evolved_language": (
                genome.evolved_language.to_dict()
                if getattr(
                    genome,
                    "evolved_language",
                    None,
                )
                is not None
                else None
            ),

            "execution_mode":
                genome.execution_mode,
        }

    @classmethod
    def genome_from_dict(
        cls,
        data: dict,
    ) -> Genome:

        instructions = [
            cls.instruction_from_dict(
                item
            )
            for item
            in data[
                "instructions"
            ]
        ]

        modules = {
            int(module_id): [
                cls.instruction_from_dict(
                    item
                )
                for item
                in module
            ]

            for module_id, module
            in data.get(
                "modules",
                {}
            ).items()
        }

        module_meta = {
            int(module_id):
                dict(metadata)

            for module_id, metadata
            in data.get(
                "module_meta",
                {}
            ).items()
        }

        macros = {
            int(macro_id): [
                cls.instruction_from_dict(
                    item
                )

                for item
                in macro
            ]

            for macro_id, macro
            in data.get(
                "macros",
                {}
            ).items()
        }

        macro_meta = {
            int(macro_id):
                dict(metadata)

            for macro_id, metadata
            in data.get(
                "macro_meta",
                {}
            ).items()
        }

        ast_data = data.get(
            "ast_program"
        )

        ast_program = (
            ASTProgram.from_dict(
                ast_data
            )
            if ast_data
            is not None
            else None
        )

        architecture_data = (
            data.get(
                "program_architecture"
            )
        )

        program_architecture = (
            ProgramArchitecture.from_dict(
                architecture_data
            )

            if architecture_data
            is not None

            else None
        )

        genome = Genome(
            instructions=instructions,
            modules=modules,
            module_meta=module_meta,
            macros=macros,
            macro_meta=macro_meta,
            ast_program=ast_program,
            program_architecture=(
                program_architecture
            ),
            evolved_language=(
                EvolvedLanguage.from_dict(
                    data[
                        "evolved_language"
                    ]
                )
                if data.get(
                    "evolved_language"
                )
                is not None
                else None
            ),
            execution_mode=data.get(
                "execution_mode",
                "DSL",
            ),
        )

        genome.next_module_id = (
            data.get(
                "next_module_id",
                genome.next_module_id,
            )
        )

        genome.next_macro_id = (
            data.get(
                "next_macro_id",
                genome.next_macro_id,
            )
        )

        return genome

    # ---------------------------------------------------------
    # ORGANISM
    # ---------------------------------------------------------

    @classmethod
    def organism_to_dict(
        cls,
        organism: Organism,
    ) -> dict:

        return {
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

            "fitness":
                organism.fitness,

            "error":
                organism.error,

            "task_errors":
                dict(
                    organism.task_errors
                ),

            "genome":
                cls.genome_to_dict(
                    organism.genome
                ),
        }

    @classmethod
    def organism_from_dict(
        cls,
        data: dict,
    ) -> Organism:

        organism = Organism(
            genome=cls.genome_from_dict(
                data["genome"]
            ),

            generation=data[
                "generation"
            ],

            parent_id=data.get(
                "parent_id"
            ),

            birth_mutations=list(
                data.get(
                    "birth_mutations",
                    [],
                )
            ),

            lineage_depth=data.get(
                "lineage_depth",
                0,
            ),

            organism_id=data[
                "id"
            ],
        )

        organism.fitness = (
            data.get(
                "fitness",
                0.0,
            )
        )

        organism.error = (
            data.get(
                "error",
                float("inf"),
            )
        )

        organism.task_errors = dict(
            data.get(
                "task_errors",
                {},
            )
        )

        return organism

    # ---------------------------------------------------------
    # SAVE
    # ---------------------------------------------------------

    @classmethod
    def save(
        cls,
        engine,
    ) -> None:

        temp_state_file = (
            f"{STATE_FILE}."
            f"{os.getpid()}.tmp"
        )

        novelty_events = []

        for event in (
            engine
            .novelty_detector
            .novel_events
        ):

            copied = dict(
                event
            )

            copied["signature"] = (
                cls._tuple_to_list(
                    copied[
                        "signature"
                    ]
                )
            )

            novelty_events.append(
                copied
            )

        state = {
            "state_version":
                STATE_VERSION,

            "generation":
                engine.generation,

            "population": [
                cls.organism_to_dict(
                    organism
                )
                for organism
                in engine.population
            ],

            "best_ever": (
                cls.organism_to_dict(
                    engine.best_ever
                )
                if engine.best_ever
                is not None
                else None
            ),

            "organism_next_id":
                Organism.get_next_id(),

            "module_next_uid":
                Genome._next_module_uid,

            "macro_next_uid":
                Genome._next_macro_uid,

            "lineage_archive":
                engine.lineage_archive,

            "novelty": {
                "events":
                    novelty_events,
            },

            "evolution_events": {
                "best_fitness_seen":
                    engine
                    .event_detector
                    .best_fitness_seen,

                "best_fitness_seen_by_era":
                    {
                        str(era_id):
                            fitness

                        for era_id, fitness
                        in engine
                        .event_detector
                        .best_fitness_seen_by_era
                        .items()
                    },

                "events":
                    engine
                    .event_detector
                    .events,
            },

            "module_lineage": {
                "archive":
                    engine
                    .module_lineage_tracker
                    .archive,
            },

            "module_families": {
                "known_families":
                    sorted(
                        engine
                        .module_family_tracker
                        .known_families
                    ),

                "family_first_seen":
                    engine
                    .module_family_tracker
                    .family_first_seen,

                "family_last_seen":
                    engine
                    .module_family_tracker
                    .family_last_seen,

                "family_peak_organisms":
                    engine
                    .module_family_tracker
                    .family_peak_organisms,

                "current_report":
                    engine
                    .module_family_tracker
                    .current_report,
            },

            "family_events": {
                "previous_counts":
                    engine
                    .family_event_detector
                    .previous_counts,

                "previous_alive":
                    sorted(
                        engine
                        .family_event_detector
                        .previous_alive
                    ),

                "max_stage":
                    engine
                    .family_event_detector
                    .max_stage,

                "events":
                    engine
                    .family_event_detector
                    .events,
            },

            "vocabulary_events": (
                engine
                .vocabulary_event_tracker
                .to_state()
            ),

            "ast_evolution": (
                engine
                .ast_evolution_tracker
                .to_state()
            ),

            "dual_execution": (
                engine
                .dual_execution_validator
                .to_state()
            ),

            "generated_provenance": (
                engine
                .generated_provenance_tracker
                .to_state()
            ),

            "adaptation": {
                "current_era_id":
                    engine
                    .adaptation_tracker
                    .current_era_id,

                "era_name":
                    getattr(
                        engine.adaptation_tracker,
                        "era_name",
                        None,
                    ),

                "era_start_generation":
                    engine
                    .adaptation_tracker
                    .era_start_generation,

                "pre_shift_reference":
                    engine
                    .adaptation_tracker
                    .pre_shift_reference,

                "start_fitness":
                    engine
                    .adaptation_tracker
                    .start_fitness,

                "best_fitness":
                    engine
                    .adaptation_tracker
                    .best_fitness,

                "lowest_fitness":
                    engine
                    .adaptation_tracker
                    .lowest_fitness,

                "recovery_generation":
                    engine
                    .adaptation_tracker
                    .recovery_generation,

                "milestones":
                    engine
                    .adaptation_tracker
                    .milestones,

                "history":
                    engine
                    .adaptation_tracker
                    .history,
            },

            "era_champions": {
                str(era_id):
                    cls.organism_to_dict(
                        champion
                    )

                for era_id, champion
                in engine
                .era_champion_tracker
                .champions
                .items()
            },

            "random_state":
                cls._tuple_to_list(
                    random.getstate()
                ),
        }

        with open(
            temp_state_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                state,
                file,
                ensure_ascii=False,
                indent=2,
                allow_nan=True,
            )

        # -----------------------------------------------------
        # WINDOWS-SAFE ATOMIC REPLACE
        # -----------------------------------------------------
        #
        # Windows bazen evolve_state.json dosyasını çok kısa
        # süreliğine kilitleyebilir (Defender, editor,
        # indexing veya başka bir process).
        #
        # Tek seferde vazgeçmek yerine kısa aralıklarla
        # tekrar deniyoruz. Mevcut sağlam save hiçbir zaman
        # önce silinmez.

        replace_error = None

        for attempt in range(20):

            try:

                os.replace(
                    temp_state_file,
                    STATE_FILE,
                )

                replace_error = None
                break

            except PermissionError as error:

                replace_error = error

                time.sleep(
                    0.10
                )

        if replace_error is not None:

            raise RuntimeError(
                "Save file remained locked after "
                "20 replace attempts. "
                f"Original error: {replace_error}"
            )

    # ---------------------------------------------------------
    # LOAD
    # ---------------------------------------------------------

    @classmethod
    def load(
        cls,
        engine,
    ) -> bool:

        if not os.path.exists(
            STATE_FILE
        ):
            return False

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8",
        ) as file:

            state = json.load(
                file
            )

        version = state.get(
            "state_version"
        )

        if version != STATE_VERSION:

            raise RuntimeError(
                "Save version mismatch: "
                f"{version} != "
                f"{STATE_VERSION}"
            )

        engine.generation = (
            state["generation"]
        )

        engine.environment.set_generation(
            engine.generation
        )

        engine.population = [
            cls.organism_from_dict(
                item
            )
            for item
            in state[
                "population"
            ]
        ]

        best_data = state.get(
            "best_ever"
        )

        engine.best_ever = (
            cls.organism_from_dict(
                best_data
            )
            if best_data
            is not None
            else None
        )

        Organism.set_next_id(
            state.get(
                "organism_next_id",
                1,
            )
        )

        Genome._next_module_uid = (
            state.get(
                "module_next_uid",
                1,
            )
        )

        Genome._next_macro_uid = (
            state.get(
                "macro_next_uid",
                1,
            )
        )

        engine.lineage_archive = dict(
            state.get(
                "lineage_archive",
                {},
            )
        )

        # -------------------------
        # NOVELTY
        # -------------------------

        novelty = (
            engine.novelty_detector
        )

        novelty.known_structures = (
            set()
        )

        novelty.structure_archive = (
            {}
        )

        novelty.novel_events = []

        for event in (
            state.get(
                "novelty",
                {}
            ).get(
                "events",
                []
            )
        ):

            record = dict(
                event
            )

            signature = (
                cls._list_to_tuple(
                    record[
                        "signature"
                    ]
                )
            )

            record[
                "signature"
            ] = signature

            novelty.known_structures.add(
                signature
            )

            novelty.structure_archive[
                signature
            ] = record

            novelty.novel_events.append(
                record
            )

        # -------------------------
        # MAJOR EVENTS
        # -------------------------

        event_data = state.get(
            "evolution_events",
            {},
        )

        detector = (
            engine.event_detector
        )

        detector.events = list(
            event_data.get(
                "events",
                [],
            )
        )

        detector.best_fitness_seen = (
            event_data.get(
                "best_fitness_seen",
                0.0,
            )
        )

        saved_era_bests = (
            event_data.get(
                "best_fitness_seen_by_era",
                {}
            )
        )

        detector.best_fitness_seen_by_era = {
            int(era_id):
                float(fitness)

            for era_id, fitness
            in saved_era_bests.items()
        }

        # ---------------------------------------------
        # LEGACY EVENT MIGRATION
        # ---------------------------------------------
        #
        # Eski event kayıtlarında era_id yok.
        # Generation aralığından ERA'yı deterministik
        # şekilde çıkarabiliyoruz.

        for event in detector.events:

            if (
                "era_id"
                in event
            ):
                continue

            generation = (
                event.get(
                    "generation",
                    0,
                )
            )

            if generation <= 1000:

                era_id = 1
                era_name = (
                    "ORIGINAL WORLD"
                )

            elif generation <= 1500:

                era_id = 2
                era_name = (
                    "SHIFTED WORLD"
                )

            elif generation <= 2000:

                era_id = 3
                era_name = (
                    "SECOND SHIFT"
                )

            else:

                era_id = 4
                era_name = (
                    "THIRD SHIFT"
                )

            event[
                "era_id"
            ] = era_id

            event[
                "era_name"
            ] = era_name

        # -------------------------
        # MODULE LINEAGES
        # -------------------------

        engine.module_lineage_tracker.archive = (
            dict(
                state.get(
                    "module_lineage",
                    {},
                ).get(
                    "archive",
                    {},
                )
            )
        )

        # -------------------------
        # MODULE FAMILIES
        # -------------------------

        family_data = state.get(
            "module_families",
            {},
        )

        tracker = (
            engine.module_family_tracker
        )

        tracker.known_families = set(
            family_data.get(
                "known_families",
                [],
            )
        )

        tracker.family_first_seen = dict(
            family_data.get(
                "family_first_seen",
                {},
            )
        )

        tracker.family_last_seen = dict(
            family_data.get(
                "family_last_seen",
                {},
            )
        )

        tracker.family_peak_organisms = (
            dict(
                family_data.get(
                    "family_peak_organisms",
                    {},
                )
            )
        )

        tracker.current_report = dict(
            family_data.get(
                "current_report",
                {},
            )
        )

        # -------------------------
        # FAMILY EVENTS
        # -------------------------

        event_state = state.get(
            "family_events",
            {},
        )

        family_detector = (
            engine.family_event_detector
        )

        family_detector.previous_counts = (
            dict(
                event_state.get(
                    "previous_counts",
                    {},
                )
            )
        )

        family_detector.previous_alive = (
            set(
                event_state.get(
                    "previous_alive",
                    [],
                )
            )
        )

        family_detector.max_stage = dict(
            event_state.get(
                "max_stage",
                {},
            )
        )

        family_detector.events = list(
            event_state.get(
                "events",
                [],
            )
        )

        family_detector.last_events = []

        # -------------------------
        # VOCABULARY EVENTS
        # -------------------------

        vocabulary_state = (
            state.get(
                "vocabulary_events"
            )
        )

        if vocabulary_state:

            engine.vocabulary_event_tracker.load_state(
                vocabulary_state
            )

        else:

            # Bu tracker Gen1551 civarında mevcut
            # tarihsel save'e eklendi.
            #
            # Mevcut K002/K003 gibi yapıları yeni
            # event gibi kaydetmiyoruz. Bunlar yalnızca
            # başlangıç baseline'ı olarak öğreniliyor.
            engine.vocabulary_event_tracker.bootstrap(
                population=engine.population,
                generation=engine.generation,
            )

        # -------------------------
        # AST EVOLUTION HISTORY
        # -------------------------

        ast_state = state.get(
            "ast_evolution"
        )

        if ast_state:

            engine.ast_evolution_tracker.load_state(
                ast_state
            )

        else:

            engine.ast_evolution_tracker.bootstrap(
                population=engine.population,
                generation=engine.generation,
            )

        # -------------------------
        # DUAL EXECUTION HISTORY
        # -------------------------

        dual_execution_state = (
            state.get(
                "dual_execution"
            )
        )

        if dual_execution_state:

            engine.dual_execution_validator.load_state(
                dual_execution_state
            )

        # -------------------------
        # GENERATED PYTHON PROVENANCE
        # -------------------------

        generated_provenance_state = (
            state.get(
                "generated_provenance"
            )
        )

        if generated_provenance_state:

            engine.generated_provenance_tracker.load_state(
                generated_provenance_state
            )

        # -------------------------
        # ADAPTATION
        # -------------------------

        adaptation = state.get(
            "adaptation"
        )

        if adaptation:

            tracker = (
                engine.adaptation_tracker
            )

            tracker.current_era_id = (
                adaptation.get(
                    "current_era_id"
                )
            )

            tracker.era_name = (
                adaptation.get(
                    "era_name",
                    "",
                )
            )

            tracker.era_start_generation = (
                adaptation.get(
                    "era_start_generation",
                    0,
                )
            )

            tracker.pre_shift_reference = (
                adaptation.get(
                    "pre_shift_reference",
                    0.0,
                )
            )

            tracker.start_fitness = (
                adaptation.get(
                    "start_fitness",
                    0.0,
                )
            )

            tracker.best_fitness = (
                adaptation.get(
                    "best_fitness",
                    0.0,
                )
            )

            tracker.lowest_fitness = (
                adaptation.get(
                    "lowest_fitness",
                    float("inf"),
                )
            )

            tracker.recovery_generation = (
                adaptation.get(
                    "recovery_generation"
                )
            )

            tracker.history = list(
                adaptation.get(
                    "history",
                    [],
                )
            )

            tracker.milestones = {
                int(threshold):
                    generation

                for threshold, generation
                in adaptation.get(
                    "milestones",
                    {
                        50: None,
                        75: None,
                        90: None,
                        100: None,
                    },
                ).items()
            }

            if (
                tracker.current_era_id == 2
                and tracker.milestones.get(
                    50
                ) is None
            ):

                tracker.milestones[50] = 1001

        # -------------------------
        # ERA CHAMPIONS
        # -------------------------

        era_champion_data = (
            state.get(
                "era_champions",
                {},
            )
        )

        engine.era_champion_tracker.champions = {
            int(era_id):
                cls.organism_from_dict(
                    champion_data
                )

            for era_id, champion_data
            in era_champion_data.items()
        }

        # Eski save dosyalarında era_champions
        # bulunmayabilir.
        #
        # Şu an Generation 1211'deyiz ve
        # ALL-TIME champion hâlâ ERA 1'den.
        # Bu nedenle mevcut tarihsel veriyi
        # güvenli şekilde bootstrap edebiliriz.

        if (
            1
            not in engine
            .era_champion_tracker
            .champions
            and engine.best_ever
            is not None
            and engine.generation
            >= 1001
        ):

            engine.era_champion_tracker.update(
                era_id=1,
                organism=engine.best_ever,
            )

        # Mevcut ERA'nın en iyi yaşayan
        # organizmasını da ilk archive
        # başlangıcı için koruyoruz.
        #
        # Bundan sonraki nesillerde tracker
        # zaten evaluate_population()
        # içerisinde otomatik güncellenecek.

        if engine.population:

            current_era_id = (
                engine.environment
                .era_report()[
                    "era_id"
                ]
            )

            if (
                current_era_id
                not in engine
                .era_champion_tracker
                .champions
            ):

                current_best = max(
                    engine.population,
                    key=lambda organism:
                        organism.fitness,
                )

                engine.era_champion_tracker.update(
                    era_id=current_era_id,
                    organism=current_best,
                )

        # -------------------------
        # STANDARDIZE ADAPTATION REFERENCE
        # -------------------------

        adaptation_tracker = (
            engine.adaptation_tracker
        )

        current_era = (
            engine.environment
            .era_report()[
                "era_id"
            ]
        )

        previous_era = (
            current_era - 1
        )

        if (
            current_era > 1
            and adaptation_tracker
            .current_era_id
            == current_era
        ):

            previous_champion = (
                engine
                .era_champion_tracker
                .get(
                    previous_era
                )
            )

            if (
                previous_champion
                is not None
            ):

                standardized = (
                    engine
                    .cross_era_tester
                    .test(
                        previous_champion,
                        previous_era,
                    )
                )

                if standardized[
                    "valid"
                ]:

                    adaptation_tracker.rebase_reference(
                        new_reference=(
                            standardized[
                                "fitness"
                            ]
                        ),

                        generation=(
                            engine.generation
                        ),
                    )

        # -------------------------
        # ERA EVENT BASELINES
        # -------------------------

        current_era_id = (
            engine.environment
            .era_report()[
                "era_id"
            ]
        )

        # Historical champion'ları mevcut ortak
        # evaluation standardıyla ölçüp her ERA için
        # detector baseline olarak kullanıyoruz.
        #
        # Böylece migration sonrası sıradaki generation
        # sahte dev bir "major event" üretmez.

        for (
            era_id,
            champion,
        ) in (
            engine
            .era_champion_tracker
            .champions
            .items()
        ):

            standardized = (
                engine
                .cross_era_tester
                .test(
                    champion,
                    era_id,
                )
            )

            if standardized[
                "valid"
            ]:

                detector.set_era_baseline(
                    era_id=era_id,
                    fitness=(
                        standardized[
                            "fitness"
                        ]
                    ),
                )

        # -------------------------
        # RANDOM STATE
        # -------------------------

        saved_random = state.get(
            "random_state"
        )

        if saved_random is not None:

            random.setstate(
                cls._list_to_tuple(
                    saved_random
                )
            )

        return True