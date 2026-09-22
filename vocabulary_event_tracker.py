# vocabulary_event_tracker.py

from __future__ import annotations

from module_tracker import ModuleTracker


class VocabularyEventTracker:

    def __init__(self):

        self.events: list[dict] = []

        self.last_events: list[dict] = []

        # Macro local ID yerine UID takip ediyoruz.
        # Çünkü K002 gibi local ID'ler farklı genome'larda
        # teorik olarak farklı soyları ifade edebilir.
        self.known_macro_uids: set[str] = set()

        self.known_nested_macro_uids: set[str] = set()

        self.baseline_generation: int | None = None

        self.flags = {
            "active_macro_seen": False,
            "active_fixation_seen": False,
            "second_vocabulary_seen": False,
            "macro_bearing_module_seen": False,
            "nested_macro_seen": False,
            "active_nested_macro_seen": False,
            "functional_nested_macro_seen": False,
        }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    @staticmethod
    def _macro_uid(
        genome,
        macro_id: int,
    ) -> str | None:

        metadata = (
            genome.macro_meta.get(
                macro_id,
                {}
            )
        )

        return metadata.get(
            "uid"
        )

    @classmethod
    def _called_macro_ids(
        cls,
        sequence,
    ) -> list[int]:

        return [
            instruction.macro_id

            for instruction in sequence

            if (
                instruction.operation
                == "CALL_MACRO"
                and instruction.macro_id
                is not None
            )
        ]

    @classmethod
    def _called_macro_uids(
        cls,
        genome,
        sequence,
    ) -> list[str]:

        result = []

        for macro_id in (
            cls._called_macro_ids(
                sequence
            )
        ):

            uid = cls._macro_uid(
                genome,
                macro_id,
            )

            if uid is not None:
                result.append(uid)

        return result

    @staticmethod
    def _body_text(
        sequence,
    ) -> str:

        return " | ".join(
            instruction.describe()
            for instruction in sequence
        )

    @staticmethod
    def _instruction_snapshot(
        instruction,
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

    @classmethod
    def _genome_snapshot(
        cls,
        genome,
    ) -> dict:

        return {
            "instructions": [
                cls._instruction_snapshot(
                    instruction
                )
                for instruction
                in genome.instructions
            ],

            "modules": {
                str(module_id): [
                    cls._instruction_snapshot(
                        instruction
                    )
                    for instruction
                    in body
                ]

                for module_id, body
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
                    cls._instruction_snapshot(
                        instruction
                    )
                    for instruction
                    in body
                ]

                for macro_id, body
                in genome.macros.items()
            },

            "macro_meta": {
                str(macro_id):
                    dict(metadata)

                for macro_id, metadata
                in genome.macro_meta.items()
            },

            "next_module_id":
                genome.next_module_id,

            "next_macro_id":
                genome.next_macro_id,
        }

    def _record(
        self,
        event_type: str,
        generation: int,
        **data,
    ) -> dict:

        event = {
            "event_type":
                event_type,

            "generation":
                generation,

            **data,
        }

        self.events.append(
            event
        )

        self.last_events.append(
            event
        )

        return event

    # ---------------------------------------------------------
    # BASELINE
    # ---------------------------------------------------------

    def bootstrap(
        self,
        population,
        generation: int,
    ) -> None:
        """
        Tracker eski save'e ilk kez eklendiğinde mevcut
        durum tarihsel bir 'yeni olay' gibi yazılmasın.

        Yalnızca mevcut state'i baseline olarak öğrenir.
        """

        self.baseline_generation = (
            generation
        )

        if not population:
            return

        distinct_macro_uids: set[str] = set()

        active_macro_organisms = 0

        precursor_present = False
        nested_present = False
        active_nested_present = False

        for organism in population:

            genome = organism.genome

            active_macro_ids = (
                ModuleTracker
                .reachable_macros(
                    organism
                )
            )

            if active_macro_ids:
                active_macro_organisms += 1

            for macro_id in genome.macros:

                uid = self._macro_uid(
                    genome,
                    macro_id,
                )

                if uid is not None:

                    self.known_macro_uids.add(
                        uid
                    )

                    distinct_macro_uids.add(
                        uid
                    )

            # module -> macro precursor
            for module in (
                genome.modules.values()
            ):

                if self._called_macro_ids(
                    module
                ):

                    precursor_present = True

            # macro -> macro
            for macro_id, body in (
                genome.macros.items()
            ):

                called = (
                    self._called_macro_ids(
                        body
                    )
                )

                if not called:
                    continue

                nested_present = True

                uid = self._macro_uid(
                    genome,
                    macro_id,
                )

                if uid is not None:
                    self.known_nested_macro_uids.add(
                        uid
                    )

                if (
                    macro_id
                    in active_macro_ids
                ):

                    active_nested_present = True

        self.flags[
            "active_macro_seen"
        ] = (
            active_macro_organisms > 0
        )

        self.flags[
            "active_fixation_seen"
        ] = (
            active_macro_organisms
            == len(population)
        )

        self.flags[
            "second_vocabulary_seen"
        ] = (
            len(
                distinct_macro_uids
            )
            >= 2
        )

        self.flags[
            "macro_bearing_module_seen"
        ] = precursor_present

        self.flags[
            "nested_macro_seen"
        ] = nested_present

        self.flags[
            "active_nested_macro_seen"
        ] = active_nested_present

    # ---------------------------------------------------------
    # POPULATION INSPECTION
    # ---------------------------------------------------------

    def inspect_population(
        self,
        population,
        generation: int,
    ) -> list[dict]:

        self.last_events = []

        if not population:
            return self.last_events

        distinct_macro_uids: set[str] = set()

        active_macro_organisms = 0

        # -----------------------------------------------------
        # PER ORGANISM
        # -----------------------------------------------------

        for organism in population:

            genome = organism.genome

            active_macro_ids = (
                ModuleTracker
                .reachable_macros(
                    organism
                )
            )

            if active_macro_ids:
                active_macro_organisms += 1

            # -------------------------------------------------
            # NEW VOCABULARY ITEMS
            # -------------------------------------------------

            for macro_id, body in (
                genome.macros.items()
            ):

                uid = self._macro_uid(
                    genome,
                    macro_id,
                )

                if uid is not None:

                    distinct_macro_uids.add(
                        uid
                    )

                    if (
                        uid
                        not in self.known_macro_uids
                    ):

                        metadata = (
                            genome
                            .macro_meta
                            .get(
                                macro_id,
                                {}
                            )
                        )

                        self._record(
                            "NEW_MACRO",
                            generation,

                            organism_id=(
                                organism.id
                            ),

                            fitness=(
                                organism.fitness
                            ),

                            macro_id=(
                                macro_id
                            ),

                            macro_uid=uid,

                            birth_generation=(
                                metadata.get(
                                    "birth_generation"
                                )
                            ),

                            origin=(
                                metadata.get(
                                    "origin"
                                )
                            ),

                            body=(
                                self._body_text(
                                    body
                                )
                            ),

                            genome=(
                                genome.describe()
                            ),
                        )

                        self.known_macro_uids.add(
                            uid
                        )

            # -------------------------------------------------
            # MODULE CONTAINING MACRO
            # -------------------------------------------------

            if not self.flags[
                "macro_bearing_module_seen"
            ]:

                for module_id, body in (
                    genome.modules.items()
                ):

                    called_ids = (
                        self._called_macro_ids(
                            body
                        )
                    )

                    if not called_ids:
                        continue

                    self._record(
                        "FIRST_OBSERVED_MACRO_BEARING_MODULE",
                        generation,

                        organism_id=(
                            organism.id
                        ),

                        fitness=(
                            organism.fitness
                        ),

                        module_id=(
                            module_id
                        ),

                        called_macro_ids=(
                            called_ids
                        ),

                        called_macro_uids=(
                            self._called_macro_uids(
                                genome,
                                body,
                            )
                        ),

                        body=(
                            self._body_text(
                                body
                            )
                        ),

                        genome=(
                            genome.describe()
                        ),
                    )

                    self.flags[
                        "macro_bearing_module_seen"
                    ] = True

                    break

            # -------------------------------------------------
            # MACRO CONTAINING MACRO
            # -------------------------------------------------

            for macro_id, body in (
                genome.macros.items()
            ):

                called_ids = (
                    self._called_macro_ids(
                        body
                    )
                )

                if not called_ids:
                    continue

                macro_uid = (
                    self._macro_uid(
                        genome,
                        macro_id,
                    )
                )

                called_uids = (
                    self._called_macro_uids(
                        genome,
                        body,
                    )
                )

                if not self.flags[
                    "nested_macro_seen"
                ]:

                    self._record(
                        "FIRST_OBSERVED_NESTED_MACRO",
                        generation,

                        organism_id=(
                            organism.id
                        ),

                        fitness=(
                            organism.fitness
                        ),

                        macro_id=(
                            macro_id
                        ),

                        macro_uid=(
                            macro_uid
                        ),

                        called_macro_ids=(
                            called_ids
                        ),

                        called_macro_uids=(
                            called_uids
                        ),

                        active=(
                            macro_id
                            in active_macro_ids
                        ),

                        body=(
                            self._body_text(
                                body
                            )
                        ),

                        genome=(
                            genome.describe()
                        ),

                        genome_snapshot=(
                            self._genome_snapshot(
                                genome
                            )
                        ),
                    )

                    self.flags[
                        "nested_macro_seen"
                    ] = True

                if (
                    macro_uid is not None
                    and macro_uid
                    not in self.known_nested_macro_uids
                ):

                    self._record(
                        "NEW_NESTED_MACRO",
                        generation,

                        organism_id=(
                            organism.id
                        ),

                        fitness=(
                            organism.fitness
                        ),

                        macro_id=(
                            macro_id
                        ),

                        macro_uid=(
                            macro_uid
                        ),

                        called_macro_ids=(
                            called_ids
                        ),

                        called_macro_uids=(
                            called_uids
                        ),

                        active=(
                            macro_id
                            in active_macro_ids
                        ),

                        body=(
                            self._body_text(
                                body
                            )
                        ),

                        genome=(
                            genome.describe()
                        ),

                        genome_snapshot=(
                            self._genome_snapshot(
                                genome
                            )
                        ),
                    )

                    self.known_nested_macro_uids.add(
                        macro_uid
                    )

                if (
                    macro_id
                    in active_macro_ids
                    and not self.flags[
                        "active_nested_macro_seen"
                    ]
                ):

                    self._record(
                        "FIRST_OBSERVED_ACTIVE_NESTED_MACRO",
                        generation,

                        organism_id=(
                            organism.id
                        ),

                        fitness=(
                            organism.fitness
                        ),

                        macro_id=(
                            macro_id
                        ),

                        macro_uid=(
                            macro_uid
                        ),

                        called_macro_ids=(
                            called_ids
                        ),

                        called_macro_uids=(
                            called_uids
                        ),

                        body=(
                            self._body_text(
                                body
                            )
                        ),

                        genome=(
                            genome.describe()
                        ),

                        genome_snapshot=(
                            self._genome_snapshot(
                                genome
                            )
                        ),
                    )

                    self.flags[
                        "active_nested_macro_seen"
                    ] = True

        # -----------------------------------------------------
        # POPULATION-LEVEL EVENTS
        # -----------------------------------------------------

        if (
            active_macro_organisms > 0
            and not self.flags[
                "active_macro_seen"
            ]
        ):

            self._record(
                "FIRST_OBSERVED_ACTIVE_MACRO",
                generation,

                active_organisms=(
                    active_macro_organisms
                ),

                population_size=(
                    len(population)
                ),
            )

            self.flags[
                "active_macro_seen"
            ] = True

        if (
            active_macro_organisms
            == len(population)
            and not self.flags[
                "active_fixation_seen"
            ]
        ):

            self._record(
                "FIRST_OBSERVED_ACTIVE_MACRO_FIXATION",
                generation,

                population_size=(
                    len(population)
                ),
            )

            self.flags[
                "active_fixation_seen"
            ] = True

        if (
            len(distinct_macro_uids) >= 2
            and not self.flags[
                "second_vocabulary_seen"
            ]
        ):

            self._record(
                "FIRST_OBSERVED_SECOND_VOCABULARY_ITEM",
                generation,

                distinct_macro_uids=(
                    sorted(
                        distinct_macro_uids
                    )
                ),
            )

            self.flags[
                "second_vocabulary_seen"
            ] = True

        return list(
            self.last_events
        )

    # ---------------------------------------------------------
    # MANUAL SCIENTIFIC CONFIRMATION
    # ---------------------------------------------------------

    def mark_functional_nested_macro(
        self,
        generation: int,
        organism_id: str,
        macro_id: int,
        macro_uid: str | None,
        baseline_fitness: float,
        ablated_fitness: float,
    ) -> dict | None:
        """
        Functional nested vocabulary otomatik varsayılmaz.

        Ablation testi gerçekten yapıldıktan sonra
        bu metod çağrılarak kalıcı tarih kaydı oluşturulur.
        """

        if self.flags[
            "functional_nested_macro_seen"
        ]:
            return None

        fitness_loss = (
            baseline_fitness
            - ablated_fitness
        )

        event = self._record(
            "FIRST_FUNCTIONAL_NESTED_MACRO",
            generation,

            organism_id=(
                organism_id
            ),

            macro_id=(
                macro_id
            ),

            macro_uid=(
                macro_uid
            ),

            baseline_fitness=(
                baseline_fitness
            ),

            ablated_fitness=(
                ablated_fitness
            ),

            fitness_loss=(
                fitness_loss
            ),
        )

        self.flags[
            "functional_nested_macro_seen"
        ] = True

        return event

    # ---------------------------------------------------------
    # REPORT / STATE
    # ---------------------------------------------------------

    def report(
        self,
    ) -> dict:

        return {
            "baseline_generation":
                self.baseline_generation,

            "event_count":
                len(
                    self.events
                ),

            "last_events":
                list(
                    self.last_events
                ),

            "recent_events":
                self.events[-10:],

            "flags":
                dict(
                    self.flags
                ),
        }

    def to_state(
        self,
    ) -> dict:

        return {
            "events":
                list(
                    self.events
                ),

            "known_macro_uids":
                sorted(
                    self.known_macro_uids
                ),

            "known_nested_macro_uids":
                sorted(
                    self.known_nested_macro_uids
                ),

            "baseline_generation":
                self.baseline_generation,

            "flags":
                dict(
                    self.flags
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

        self.known_macro_uids = set(
            data.get(
                "known_macro_uids",
                [],
            )
        )

        self.known_nested_macro_uids = set(
            data.get(
                "known_nested_macro_uids",
                [],
            )
        )

        self.baseline_generation = (
            data.get(
                "baseline_generation"
            )
        )

        saved_flags = dict(
            data.get(
                "flags",
                {},
            )
        )

        for key in self.flags:

            if key in saved_flags:
                self.flags[key] = bool(
                    saved_flags[key]
                )