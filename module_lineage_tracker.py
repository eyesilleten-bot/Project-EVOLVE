# module_lineage_tracker.py

from __future__ import annotations

from organism import Organism


class ModuleLineageTracker:

    def __init__(self):

        self.archive: dict[
            str,
            dict,
        ] = {}

    # ========================================================
    # INSPECTION
    # ========================================================

    def inspect_organism(
        self,
        organism: Organism,
    ) -> None:

        genome = organism.genome

        for (
            module_id,
            module,
        ) in genome.modules.items():

            metadata = (
                genome.module_meta.get(
                    module_id
                )
            )

            if metadata is None:
                continue

            uid = metadata["uid"]

            if uid in self.archive:
                continue

            body = " | ".join(
                instruction.describe()
                for instruction
                in module
            )

            parent_uid = (
                metadata.get(
                    "parent_uid"
                )
            )

            parent_uids = list(
                metadata.get(
                    "parent_uids",
                    [],
                )
            )

            # Normal mutation / duplication için
            # tek parent varsa ancestry listesine
            # onu da dahil ediyoruz.
            if (
                parent_uid is not None
                and parent_uid
                not in parent_uids
            ):

                parent_uids.insert(
                    0,
                    parent_uid,
                )

            self.archive[uid] = {
                "uid":
                    uid,

                "parent_uid":
                    parent_uid,

                "parent_uids":
                    parent_uids,

                "birth_generation":
                    metadata[
                        "birth_generation"
                    ],

                "origin":
                    metadata[
                        "origin"
                    ],

                "first_seen_organism":
                    organism.id,

                "local_module_id":
                    module_id,

                "body":
                    body,
            }

    def inspect_population(
        self,
        population: list[Organism],
    ) -> None:

        for organism in population:

            self.inspect_organism(
                organism
            )

    # ========================================================
    # LINEAR LINEAGE
    # ========================================================

    def trace(
        self,
        module_uid: str,
        max_depth: int = 20,
    ) -> list[dict]:
        """
        Geleneksel tek-soylu çizgiyi takip eder.

        MUTATION / DUPLICATION gibi olaylarda kullanılır.

        COMPOSITION yeni bir family root olduğu için
        parent_uid=None noktasında durur.
        """

        lineage = []

        current_uid: str | None = (
            module_uid
        )

        while (
            current_uid is not None
            and len(lineage)
            < max_depth
        ):

            record = (
                self.archive.get(
                    current_uid
                )
            )

            if record is None:
                break

            lineage.append(
                record
            )

            current_uid = (
                record.get(
                    "parent_uid"
                )
            )

        return lineage

    # ========================================================
    # FULL ANCESTRY GRAPH
    # ========================================================

    def trace_ancestry(
        self,
        module_uid: str,
        max_depth: int = 20,
    ) -> list[dict]:
        """
        Composite modüller dahil bütün ancestry graph'ını
        döndürür.

        Aynı ancestor birden fazla yoldan ulaşılsa bile
        yalnızca bir kez raporlanır.
        """

        results: list[dict] = []

        visited: set[str] = set()

        stack: list[
            tuple[str, int]
        ] = [
            (
                module_uid,
                0,
            )
        ]

        while stack:

            uid, depth = (
                stack.pop()
            )

            if (
                uid in visited
                or depth > max_depth
            ):
                continue

            visited.add(
                uid
            )

            record = (
                self.archive.get(
                    uid
                )
            )

            if record is None:
                continue

            copied = dict(
                record
            )

            copied[
                "ancestry_depth"
            ] = depth

            results.append(
                copied
            )

            parents = list(
                record.get(
                    "parent_uids",
                    [],
                )
            )

            for parent_uid in reversed(
                parents
            ):

                if parent_uid is None:
                    continue

                stack.append(
                    (
                        parent_uid,
                        depth + 1,
                    )
                )

        return results

    # ========================================================
    # METRICS
    # ========================================================

    def total_module_lineages(
        self,
    ) -> int:

        return len(
            self.archive
        )

    def population_summary(
        self,
        population: list[Organism],
    ) -> dict:

        current_uids = set()

        composite_variants = 0

        for organism in population:

            for metadata in (
                organism
                .genome
                .module_meta
                .values()
            ):

                current_uids.add(
                    metadata["uid"]
                )

                if (
                    metadata.get(
                        "origin"
                    )
                    == "COMPOSITION"
                ):

                    composite_variants += 1

        return {
            "archived_module_variants":
                len(
                    self.archive
                ),

            "current_module_variants":
                len(
                    current_uids
                ),

            "current_composite_instances":
                composite_variants,
        }