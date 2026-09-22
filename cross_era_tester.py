# cross_era_tester.py

from __future__ import annotations

from collections import defaultdict

from environment import Environment
from organism import Organism


class CrossEraTester:

    def __init__(
        self,
        environment: Environment,
    ) -> None:

        self.environment = environment

    def test(
        self,
        organism: Organism,
        era_id: int,
    ) -> dict:

        cases = (
            self.environment
            .get_cases_for_era(
                era_id
            )
        )

        total_error = 0.0

        task_errors = defaultdict(
            list
        )

        for (
            task,
            input_value,
            target_value,
        ) in cases:

            try:

                output = (
                    organism.genome.execute(
                        input_value,
                        task.context_id,
                    )
                )

            except (
                ValueError,
                OverflowError,
                RuntimeError,
            ):

                return {
                    "era_id":
                        era_id,

                    "valid":
                        False,

                    "fitness":
                        0.0,

                    "mean_error":
                        float("inf"),

                    "task_errors":
                        {},
                }

            if (
                output != output
                or abs(output)
                > 1_000_000
            ):

                return {
                    "era_id":
                        era_id,

                    "valid":
                        False,

                    "fitness":
                        0.0,

                    "mean_error":
                        float("inf"),

                    "task_errors":
                        {},
                }

            error = abs(
                target_value
                - output
            )

            total_error += error

            task_errors[
                task.name
            ].append(
                error
            )

        task_mean_errors = {
            task_name:
                sum(errors)
                / len(errors)

            for task_name, errors
            in task_errors.items()
        }

        mean_error = (
            total_error
            / len(cases)
        )

        worst_task_error = max(
            task_mean_errors.values()
        )

        complexity_cost = (
            organism
            .genome
            .total_instruction_count()
            * 0.01
        )

        balanced_error = (
            mean_error
            + worst_task_error
            * 0.35
        )

        fitness = (
            100.0
            / (
                1.0
                + balanced_error
                + complexity_cost
            )
        )

        return {
            "era_id":
                era_id,

            "valid":
                True,

            "fitness":
                fitness,

            "mean_error":
                mean_error,

            "task_errors":
                task_mean_errors,
        }

    def compare(
        self,
        organism: Organism,
        era_ids: list[int],
    ) -> list[dict]:

        return [
            self.test(
                organism,
                era_id,
            )

            for era_id
            in era_ids
        ]