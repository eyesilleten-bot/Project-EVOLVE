# environment.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:

    name: str
    context_id: int

    slope: float
    intercept: float

    # -----------------------------------------------------
    # OPTIONAL COMPOSITIONAL PIPELINE
    #
    # Eski görevlerde boş kalır ve klasik:
    #
    #     slope * x + intercept
    #
    # davranışı korunur.
    #
    # Yeni görevlerde işlemler mevcut çalışma değeri
    # üzerinde sırayla uygulanır.
    # -----------------------------------------------------

    operations: tuple[
        tuple[
            str,
            float,
        ],
        ...,
    ] = ()

    def target(
        self,
        x: float,
    ) -> float:

        if not self.operations:

            return (
                self.slope * x
                + self.intercept
            )

        value = float(x)

        for (
            operation,
            parameter,
        ) in self.operations:

            if operation == "ADD":

                value += parameter

            elif operation == "SUBTRACT":

                value -= parameter

            elif operation == "MULTIPLY":

                value *= parameter

            elif operation == "ABS":

                value = abs(value)

            else:

                raise ValueError(
                    "Unsupported task operation: "
                    f"{operation}"
                )

        return value

    def describe(
        self,
    ) -> str:

        if self.operations:

            descriptions = []

            for (
                operation,
                parameter,
            ) in self.operations:

                if operation == "ABS":

                    descriptions.append(
                        "ABS"
                    )

                else:

                    descriptions.append(
                        (
                            f"{operation}"
                            f"({parameter:.2f})"
                        )
                    )

            return (
                " -> ".join(
                    descriptions
                )
            )

        sign = (
            "+"
            if self.intercept >= 0
            else "-"
        )

        return (
            f"{self.slope:.2f}x "
            f"{sign} "
            f"{abs(self.intercept):.2f}"
        )


@dataclass(frozen=True)
class EnvironmentEra:

    era_id: int

    name: str

    start_generation: int
    end_generation: int | None

    tasks: tuple[
        Task,
        ...
    ]


class Environment:

    def __init__(
        self,
    ) -> None:

        self.current_generation = 0

        self.training_inputs = (
            -8.0,
            -4.0,
            -2.0,
            0.0,
            2.0,
            4.0,
            8.0,
        )

        self.eras = (
            # ---------------------------------
            # ERA 1
            # Original world.
            # Generation 0–1000.
            # ---------------------------------

            EnvironmentEra(
                era_id=1,

                name="ORIGINAL WORLD",

                start_generation=0,
                end_generation=1000,

                tasks=(
                    Task(
                        name="TASK_A",
                        context_id=0,
                        slope=2.0,
                        intercept=3.0,
                    ),

                    Task(
                        name="TASK_B",
                        context_id=1,
                        slope=1.5,
                        intercept=-2.0,
                    ),

                    Task(
                        name="TASK_C",
                        context_id=2,
                        slope=-1.0,
                        intercept=4.0,
                    ),
                ),
            ),

            # ---------------------------------
            # ERA 2
            # First environmental shift.
            # Generation 1001–1500.
            # ---------------------------------

            EnvironmentEra(
                era_id=2,

                name="SHIFTED WORLD",

                start_generation=1001,
                end_generation=1500,

                tasks=(
                    Task(
                        name="TASK_A",
                        context_id=0,
                        slope=2.20,
                        intercept=2.50,
                    ),

                    Task(
                        name="TASK_B",
                        context_id=1,
                        slope=1.30,
                        intercept=-1.00,
                    ),

                    Task(
                        name="TASK_C",
                        context_id=2,
                        slope=-0.80,
                        intercept=5.00,
                    ),
                ),
            ),

            # ---------------------------------
            # ERA 3
            # Second shift.
            # ---------------------------------

            EnvironmentEra(
                era_id=3,

                name="SECOND SHIFT",

                start_generation=1501,
                end_generation=2000,

                tasks=(
                    Task(
                        name="TASK_A",
                        context_id=0,
                        slope=1.70,
                        intercept=4.20,
                    ),

                    Task(
                        name="TASK_B",
                        context_id=1,
                        slope=1.80,
                        intercept=-3.00,
                    ),

                    Task(
                        name="TASK_C",
                        context_id=2,
                        slope=-1.20,
                        intercept=3.20,
                    ),
                ),
            ),

            # ---------------------------------
            # ERA 4
            # More distant environment.
            # ---------------------------------

            EnvironmentEra(
                era_id=4,

                name="THIRD SHIFT",

                start_generation=2001,
                end_generation=2500,

                tasks=(
                    Task(
                        name="TASK_A",
                        context_id=0,
                        slope=2.50,
                        intercept=1.00,
                    ),

                    Task(
                        name="TASK_B",
                        context_id=1,
                        slope=1.10,
                        intercept=0.50,
                    ),

                    Task(
                        name="TASK_C",
                        context_id=2,
                        slope=-0.60,
                        intercept=6.00,
                    ),
                ),
            ),

            # ---------------------------------
            # ERA 5
            # First nonlinear compositional world.
            # Generation 2501–3000.
            #
            # Shared core:
            #
            #     ABS(1.5x + 0.75)
            #
            # Context-specific continuations:
            #
            # A = shared core
            # B = shared core * 0.5 + 2.0
            # C = shared core * 2.0 - 3.0
            # ---------------------------------

            EnvironmentEra(
                era_id=5,

                name="COMPOSITIONAL WORLD",

                start_generation=2501,
                end_generation=3000,

                tasks=(
                    Task(
                        name="TASK_A",
                        context_id=0,

                        # Eski rapor alanları korunuyor.
                        slope=1.0,
                        intercept=0.0,

                        operations=(
                            (
                                "MULTIPLY",
                                1.50,
                            ),
                            (
                                "ADD",
                                0.75,
                            ),
                            (
                                "ABS",
                                0.0,
                            ),
                        ),
                    ),

                    Task(
                        name="TASK_B",
                        context_id=1,

                        slope=1.0,
                        intercept=0.0,

                        operations=(
                            (
                                "MULTIPLY",
                                1.50,
                            ),
                            (
                                "ADD",
                                0.75,
                            ),
                            (
                                "ABS",
                                0.0,
                            ),
                            (
                                "MULTIPLY",
                                0.50,
                            ),
                            (
                                "ADD",
                                2.00,
                            ),
                        ),
                    ),

                    Task(
                        name="TASK_C",
                        context_id=2,

                        slope=1.0,
                        intercept=0.0,

                        operations=(
                            (
                                "MULTIPLY",
                                1.50,
                            ),
                            (
                                "ADD",
                                0.75,
                            ),
                            (
                                "ABS",
                                0.0,
                            ),
                            (
                                "MULTIPLY",
                                2.00,
                            ),
                            (
                                "SUBTRACT",
                                3.00,
                            ),
                        ),
                    ),
                ),
            ),
        )

    # ========================================================
    # GENERATION
    # ========================================================

    def set_generation(
        self,
        generation: int,
    ) -> None:

        self.current_generation = (
            max(
                0,
                int(generation),
            )
        )

    # ========================================================
    # ERA
    # ========================================================

    def get_current_era(
        self,
    ) -> EnvironmentEra:

        generation = (
            self.current_generation
        )

        for era in self.eras:

            if (
                generation
                < era.start_generation
            ):
                continue

            if (
                era.end_generation
                is None
                or generation
                <= era.end_generation
            ):
                return era

        # Tanımlı son generation sonrasında
        # son çevreyi koruyoruz.
        return self.eras[-1]

    def era_report(
        self,
    ) -> dict:

        era = (
            self.get_current_era()
        )

        return {
            "era_id":
                era.era_id,

            "name":
                era.name,

            "start_generation":
                era.start_generation,

            "end_generation":
                era.end_generation,

            "generation":
                self.current_generation,

            "tasks": [
                {
                    "name":
                        task.name,

                    "context_id":
                        task.context_id,

                    "slope":
                        task.slope,

                    "intercept":
                        task.intercept,

                    "operations": [
                        (
                            operation,
                            parameter,
                        )

                        for (
                            operation,
                            parameter,
                        )
                        in task.operations
                    ],

                    "rule":
                        task.describe(),
                }

                for task in era.tasks
            ],
        }

    # ========================================================
    # TRAINING
    # ========================================================

    def get_training_cases(
        self,
    ) -> list[
        tuple[
            Task,
            float,
            float,
        ]
    ]:

        era = (
            self.get_current_era()
        )

        cases = []

        for task in era.tasks:

            for x in (
                self.training_inputs
            ):

                cases.append(
                    (
                        task,
                        x,
                        task.target(
                            x
                        ),
                    )
                )

        return cases

    def get_cases_for_era(
        self,
        era_id: int,
    ) -> list[
        tuple[
            Task,
            float,
            float,
        ]
    ]:

        selected_era = None

        for era in self.eras:

            if era.era_id == era_id:

                selected_era = era
                break

        if selected_era is None:

            raise ValueError(
                f"Unknown era: {era_id}"
            )

        cases = []

        for task in selected_era.tasks:

            for x in self.training_inputs:

                cases.append(
                    (
                        task,
                        x,
                        task.target(x),
                    )
                )

        return cases

    # ========================================================
    # HIDDEN / ZERO-SHOT TEST
    # ========================================================

    @staticmethod
    def hidden_rule(
        x: float,
    ) -> float:

        return (
            0.5 * x
            + 7.0
        )

    def get_hidden_cases(
        self,
    ) -> list[
        tuple[
            float,
            float,
        ]
    ]:

        inputs = (
            -10.0,
            -4.5,
            0.0,
            3.5,
            10.0,
        )

        return [
            (
                x,
                self.hidden_rule(
                    x
                ),
            )

            for x in inputs
        ]