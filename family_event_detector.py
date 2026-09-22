# family_event_detector.py

from __future__ import annotations


class FamilyEventDetector:

    def __init__(self):

        self.previous_counts: dict[
            str,
            int,
        ] = {}

        self.previous_alive: set[
            str
        ] = set()

        self.max_stage: dict[
            str,
            str,
        ] = {}

        self.events: list[
            dict
        ] = []

        self.last_events: list[
            dict
        ] = []

    @staticmethod
    def stage_for(
        organisms: int,
        population_size: int,
    ) -> str:

        if population_size <= 0:
            return "NONE"

        ratio = (
            organisms
            / population_size
        )

        if ratio >= 1.0:
            return "FIXATED"

        if ratio >= 0.75:
            return "DOMINANT"

        if ratio >= 0.25:
            return "SPREAD"

        return "PRESENT"

    @staticmethod
    def stage_rank(
        stage: str,
    ) -> int:

        ranks = {
            "NONE": 0,
            "PRESENT": 1,
            "SPREAD": 2,
            "DOMINANT": 3,
            "FIXATED": 4,
        }

        return ranks.get(
            stage,
            0,
        )

    def _record(
        self,
        generation: int,
        family: str,
        event_type: str,
        organisms: int,
        population_size: int,
    ) -> None:

        percentage = (
            (
                organisms
                / population_size
            )
            * 100.0
            if population_size
            else 0.0
        )

        event = {
            "generation":
                generation,

            "family":
                family,

            "event_type":
                event_type,

            "organisms":
                organisms,

            "population_size":
                population_size,

            "percentage":
                percentage,
        }

        self.events.append(
            event
        )

        self.last_events.append(
            event
        )

    def update(
        self,
        family_report: dict,
        generation: int,
        population_size: int,
    ) -> None:

        self.last_events = []

        current_counts = {
            family["family"]:
                family["organisms"]

            for family
            in family_report.get(
                "families",
                []
            )
        }

        current_alive = set(
            current_counts.keys()
        )

        # -------------------------
        # NEW / SPREAD EVENTS
        # -------------------------

        for (
            family,
            count,
        ) in current_counts.items():

            if (
                family
                not in self.previous_alive
            ):

                self._record(
                    generation,
                    family,
                    "FAMILY_BORN",
                    count,
                    population_size,
                )

            stage = (
                self.stage_for(
                    count,
                    population_size,
                )
            )

            previous_max = (
                self.max_stage.get(
                    family,
                    "NONE",
                )
            )

            if (
                self.stage_rank(stage)
                >
                self.stage_rank(
                    previous_max
                )
            ):

                # PRESENT tek başına
                # özel olay sayılmıyor.
                if stage == "SPREAD":

                    self._record(
                        generation,
                        family,
                        "FAMILY_SPREAD",
                        count,
                        population_size,
                    )

                elif stage == "DOMINANT":

                    self._record(
                        generation,
                        family,
                        "FAMILY_DOMINANT",
                        count,
                        population_size,
                    )

                elif stage == "FIXATED":

                    self._record(
                        generation,
                        family,
                        "FAMILY_FIXATED",
                        count,
                        population_size,
                    )

                self.max_stage[
                    family
                ] = stage

        # -------------------------
        # EXTINCTION
        # -------------------------

        extinct_now = (
            self.previous_alive
            - current_alive
        )

        for family in sorted(
            extinct_now
        ):

            self._record(
                generation,
                family,
                "FAMILY_EXTINCT",
                0,
                population_size,
            )

        self.previous_counts = (
            current_counts
        )

        self.previous_alive = (
            current_alive
        )

    def report(
        self,
    ) -> dict:

        return {
            "total_events":
                len(
                    self.events
                ),

            "new_events":
                list(
                    self.last_events
                ),

            "recent_events":
                self.events[-10:],
        }