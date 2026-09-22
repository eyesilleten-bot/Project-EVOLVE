from __future__ import annotations


class GeneratedProvenanceTracker:

    def __init__(self) -> None:

        # fingerprint -> provenance record
        self.records: dict[str, dict] = {}

        self.total_observations = 0

    # =====================================================
    # OBSERVE
    # =====================================================

    def observe(
        self,
        organism,
        generation: int,
        fingerprint: str,
        module_name: str,
    ) -> None:

        program = (
            organism.genome.ast_program
        )

        if program is None:
            return

        ast_description = (
            program.describe()
        )

        fitness = float(
            organism.fitness
        )

        record = self.records.get(
            fingerprint
        )

        # -------------------------------------------------
        # FIRST OBSERVATION OF THIS GENERATED PHENOTYPE
        # -------------------------------------------------

        if record is None:

            self.records[
                fingerprint
            ] = {
                "fingerprint":
                    fingerprint,

                "python_module":
                    module_name,

                "python_file":
                    (
                        f"generated/"
                        f"{module_name}.py"
                    ),

                "first_seen_generation":
                    generation,

                "last_seen_generation":
                    generation,

                "observations":
                    1,

                "first_organism_id":
                    organism.id,

                "last_organism_id":
                    organism.id,

                "best_organism_id":
                    organism.id,

                "best_fitness":
                    fitness,

                "parent_id":
                    getattr(
                        organism,
                        "parent_id",
                        None,
                    ),

                "lineage_depth":
                    getattr(
                        organism,
                        "lineage_depth",
                        None,
                    ),

                "ast_origin":
                    getattr(
                        program,
                        "origin",
                        None,
                    ),

                "ast_birth_generation":
                    getattr(
                        program,
                        "birth_generation",
                        None,
                    ),

                "first_ast":
                    ast_description,

                "latest_ast":
                    ast_description,

                "birth_mutations":
                    list(
                        getattr(
                            organism,
                            "birth_mutations",
                            [],
                        )
                    ),
            }

            self.total_observations += 1
            return

        # -------------------------------------------------
        # EXISTING GENERATED PHENOTYPE
        # -------------------------------------------------

        record["last_seen_generation"] = (
            generation
        )

        record["last_organism_id"] = (
            organism.id
        )

        record["latest_ast"] = (
            ast_description
        )

        record["observations"] = (
            int(
                record.get(
                    "observations",
                    0,
                )
            )
            + 1
        )

        if (
            fitness
            > float(
                record.get(
                    "best_fitness",
                    float("-inf"),
                )
            )
        ):

            record["best_fitness"] = (
                fitness
            )

            record["best_organism_id"] = (
                organism.id
            )

            record["parent_id"] = (
                getattr(
                    organism,
                    "parent_id",
                    None,
                )
            )

            record["lineage_depth"] = (
                getattr(
                    organism,
                    "lineage_depth",
                    None,
                )
            )

            record["birth_mutations"] = (
                list(
                    getattr(
                        organism,
                        "birth_mutations",
                        [],
                    )
                )
            )

        self.total_observations += 1

    # =====================================================
    # STATE
    # =====================================================

    def to_state(
        self,
    ) -> dict:

        return {
            "total_observations":
                self.total_observations,

            "records":
                self.records,
        }

    def load_state(
        self,
        state: dict,
    ) -> None:

        self.total_observations = int(
            state.get(
                "total_observations",
                0,
            )
        )

        self.records = {
            str(fingerprint):
                dict(record)

            for fingerprint, record
            in state.get(
                "records",
                {},
            ).items()
        }

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> dict:

        records = list(
            self.records.values()
        )

        most_observed = None
        best_record = None

        if records:

            most_observed = max(
                records,
                key=lambda item:
                    item.get(
                        "observations",
                        0,
                    ),
            )

            best_record = max(
                records,
                key=lambda item:
                    item.get(
                        "best_fitness",
                        float("-inf"),
                    ),
            )

        return {
            "unique_generated_phenotypes":
                len(self.records),

            "total_observations":
                self.total_observations,

            "most_observed":
                (
                    dict(most_observed)
                    if most_observed
                    is not None
                    else None
                ),

            "best_generated_phenotype":
                (
                    dict(best_record)
                    if best_record
                    is not None
                    else None
                ),

            "records":
                {
                    fingerprint:
                        dict(record)

                    for fingerprint, record
                    in self.records.items()
                },
        }