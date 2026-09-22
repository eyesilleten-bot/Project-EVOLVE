# module_family_tracker.py

from __future__ import annotations

from collections import Counter, defaultdict

from organism import Organism
from module_lineage_tracker import (
    ModuleLineageTracker,
)
from module_tracker import (
    ModuleTracker,
)


class ModuleFamilyTracker:

    def __init__(self):

        self.known_families: set[
            str
        ] = set()

        self.family_first_seen: dict[
            str,
            int,
        ] = {}

        self.family_last_seen: dict[
            str,
            int,
        ] = {}

        self.family_peak_organisms: dict[
            str,
            int,
        ] = {}

        self.current_report: dict = {
            "families_ever_seen": 0,
            "families_alive": 0,
            "families_extinct": 0,
            "dominant_families": [],
            "families": [],
        }

    def find_family_root(
        self,
        module_uid: str,
        lineage_tracker:
            ModuleLineageTracker,
    ) -> str:

        current_uid = module_uid

        visited = set()

        while True:

            if current_uid in visited:
                return current_uid

            visited.add(
                current_uid
            )

            record = (
                lineage_tracker
                .archive
                .get(
                    current_uid
                )
            )

            if record is None:
                return current_uid

            parent_uid = (
                record["parent_uid"]
            )

            if parent_uid is None:
                return current_uid

            current_uid = (
                parent_uid
            )

    def update(
        self,
        population: list[Organism],
        lineage_tracker:
            ModuleLineageTracker,
        generation: int,
    ) -> None:

        organisms_per_family = (
            Counter()
        )

        instances_per_family = (
            Counter()
        )

        variants_per_family = (
            defaultdict(set)
        )

        for organism in population:

            organism_families = set()

            reachable_modules = (
                ModuleTracker
                .reachable_modules(
                    organism
                )
            )

            for module_id in (
                reachable_modules
            ):

                metadata = (
                    organism
                    .genome
                    .module_meta
                    .get(
                        module_id
                    )
                )

                if metadata is None:
                    continue

                uid = metadata[
                    "uid"
                ]

                root = (
                    self.find_family_root(
                        uid,
                        lineage_tracker,
                    )
                )

                organism_families.add(
                    root
                )

                instances_per_family[
                    root
                ] += 1

                variants_per_family[
                    root
                ].add(
                    uid
                )

            for root in (
                organism_families
            ):

                organisms_per_family[
                    root
                ] += 1

        alive_families = set(
            organisms_per_family.keys()
        )

        for family in alive_families:

            self.known_families.add(
                family
            )

            if (
                family
                not in
                self.family_first_seen
            ):

                self.family_first_seen[
                    family
                ] = generation

            self.family_last_seen[
                family
            ] = generation

            current_count = (
                organisms_per_family[
                    family
                ]
            )

            old_peak = (
                self.family_peak_organisms
                .get(
                    family,
                    0,
                )
            )

            if (
                current_count
                > old_peak
            ):

                self.family_peak_organisms[
                    family
                ] = current_count

        extinct_families = (
            self.known_families
            - alive_families
        )

        ranked = sorted(
            alive_families,
            key=lambda family: (
                organisms_per_family[
                    family
                ],
                instances_per_family[
                    family
                ],
            ),
            reverse=True,
        )

        family_details = []

        population_size = len(
            population
        )

        for family in ranked:

            organisms = (
                organisms_per_family[
                    family
                ]
            )

            family_details.append(
                {
                    "family":
                        family,

                    "organisms":
                        organisms,

                    "spread":
                        (
                            organisms
                            / population_size
                            if population_size
                            else 0.0
                        ),

                    "module_instances":
                        instances_per_family[
                            family
                        ],

                    "living_variants":
                        len(
                            variants_per_family[
                                family
                            ]
                        ),

                    "first_seen":
                        self.family_first_seen[
                            family
                        ],

                    "peak_organisms":
                        self.family_peak_organisms[
                            family
                        ],
                }
            )

        # Aynı en yüksek organizma sayısına
        # sahip ailelerin hepsi dominant.
        dominant_families = []

        if family_details:

            maximum = max(
                family[
                    "organisms"
                ]
                for family
                in family_details
            )

            dominant_families = [
                family
                for family
                in family_details
                if family[
                    "organisms"
                ] == maximum
            ]

        self.current_report = {
            "families_ever_seen":
                len(
                    self.known_families
                ),

            "families_alive":
                len(
                    alive_families
                ),

            "families_extinct":
                len(
                    extinct_families
                ),

            "dominant_families":
                dominant_families,

            "families":
                family_details,
        }

    def report(
        self,
    ) -> dict:

        return self.current_report