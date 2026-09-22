# evaluator.py

from __future__ import annotations

from collections import defaultdict

from environment import Environment
from organism import Organism


class Evaluator:

    def __init__(
        self,
        environment: Environment,
    ):
        self.environment = environment

    def evaluate(
        self,
        organism: Organism,
    ) -> float:

        cases = (
            self.environment
            .get_training_cases()
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
                output = organism.run(
                    input_value,
                    task.context_id,
                )

            except (
                ValueError,
                OverflowError,
                RuntimeError,
            ):
                organism.fitness = 0.0
                organism.error = float("inf")
                organism.task_errors = {}

                return 0.0

            if (
                output != output
                or abs(output) > 1_000_000
            ):
                organism.fitness = 0.0
                organism.error = float("inf")
                organism.task_errors = {}

                return 0.0

            error = abs(
                target_value - output
            )

            total_error += error

            task_errors[
                task.name
            ].append(
                error
            )

        task_mean_errors = {
            task_name:
                sum(errors) / len(errors)

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

        total_code_size = (
            organism
            .genome
            .active_code_size()
        )

        complexity_cost = (
            total_code_size
            * 0.01
        )

        balanced_error = (
            mean_error
            + worst_task_error * 0.35
        )

        organism.error = (
            mean_error
        )

        organism.task_errors = (
            task_mean_errors
        )

        organism.fitness = (
            100.0
            / (
                1.0
                + balanced_error
                + complexity_cost
            )
        )

        return organism.fitness