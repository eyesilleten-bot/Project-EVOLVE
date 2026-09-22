# module_tracker.py

from __future__ import annotations

from collections import Counter

from organism import Organism


class ModuleTracker:
    """
    Modüllerin hem MAIN hem de diğer modüller
    tarafından nasıl kullanıldığını analiz eder.

    V0.4 ile hierarchical / nested module
    çağrılarını da takip eder.
    """

    # ========================================================
    # DIRECT CALLS
    # ========================================================

    @staticmethod
    def _direct_calls(
        organism: Organism,
    ) -> tuple[
        Counter,
        Counter,
    ]:

        genome = organism.genome

        main_calls = Counter()
        nested_calls = Counter()

        # MAIN -> MODULE
        for instruction in (
            genome.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                is not None
            ):

                main_calls[
                    instruction.module_id
                ] += 1

        # MODULE -> MODULE
        for module in (
            genome.modules.values()
        ):

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    is not None
                ):

                    nested_calls[
                        instruction.module_id
                    ] += 1

        return (
            main_calls,
            nested_calls,
        )

    # ========================================================
    # DEPENDENCY GRAPH
    # ========================================================

    @staticmethod
    def dependency_graph(
        organism: Organism,
    ) -> dict[
        int,
        set[int],
    ]:

        genome = organism.genome

        graph: dict[
            int,
            set[int],
        ] = {
            module_id: set()
            for module_id
            in genome.modules
        }

        for (
            module_id,
            module,
        ) in genome.modules.items():

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    is not None
                    and instruction.module_id
                    in genome.modules
                ):

                    graph[
                        module_id
                    ].add(
                        instruction.module_id
                    )

        return graph

    # ========================================================
    # REACHABILITY
    # ========================================================

    @classmethod
    def reachable_modules(
        cls,
        organism: Organism,
    ) -> set[int]:

        genome = organism.genome

        reachable_modules: set[int] = set()
        reachable_macros: set[int] = set()

        worklist: list[
            tuple[str, int]
        ] = []

        # MAIN roots
        for instruction in (
            genome.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                in genome.modules
            ):

                worklist.append(
                    (
                        "MODULE",
                        instruction.module_id,
                    )
                )

            elif (
                instruction.operation
                == "CALL_MACRO"
                and instruction.macro_id
                in genome.macros
            ):

                worklist.append(
                    (
                        "MACRO",
                        instruction.macro_id,
                    )
                )

        while worklist:

            kind, item_id = (
                worklist.pop()
            )

            if kind == "MODULE":

                if (
                    item_id
                    in reachable_modules
                ):
                    continue

                reachable_modules.add(
                    item_id
                )

                sequence = (
                    genome.modules[
                        item_id
                    ]
                )

            else:

                if (
                    item_id
                    in reachable_macros
                ):
                    continue

                reachable_macros.add(
                    item_id
                )

                sequence = (
                    genome.macros[
                        item_id
                    ]
                )

            for instruction in sequence:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    in genome.modules
                ):

                    worklist.append(
                        (
                            "MODULE",
                            instruction.module_id,
                        )
                    )

                elif (
                    instruction.operation
                    == "CALL_MACRO"
                    and instruction.macro_id
                    in genome.macros
                ):

                    worklist.append(
                        (
                            "MACRO",
                            instruction.macro_id,
                        )
                    )

        return reachable_modules

    @classmethod
    def reachable_macros(
        cls,
        organism: Organism,
    ) -> set[int]:

        genome = organism.genome

        reachable_modules: set[int] = set()
        reachable_macros: set[int] = set()

        worklist: list[
            tuple[str, int]
        ] = []

        for instruction in (
            genome.instructions
        ):

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                in genome.modules
            ):

                worklist.append(
                    (
                        "MODULE",
                        instruction.module_id,
                    )
                )

            elif (
                instruction.operation
                == "CALL_MACRO"
                and instruction.macro_id
                in genome.macros
            ):

                worklist.append(
                    (
                        "MACRO",
                        instruction.macro_id,
                    )
                )

        while worklist:

            kind, item_id = (
                worklist.pop()
            )

            if kind == "MODULE":

                if (
                    item_id
                    in reachable_modules
                ):
                    continue

                reachable_modules.add(
                    item_id
                )

                sequence = (
                    genome.modules[
                        item_id
                    ]
                )

            else:

                if (
                    item_id
                    in reachable_macros
                ):
                    continue

                reachable_macros.add(
                    item_id
                )

                sequence = (
                    genome.macros[
                        item_id
                    ]
                )

            for instruction in sequence:

                if (
                    instruction.operation
                    == "CALL_MODULE"
                    and instruction.module_id
                    in genome.modules
                ):

                    worklist.append(
                        (
                            "MODULE",
                            instruction.module_id,
                        )
                    )

                elif (
                    instruction.operation
                    == "CALL_MACRO"
                    and instruction.macro_id
                    in genome.macros
                ):

                    worklist.append(
                        (
                            "MACRO",
                            instruction.macro_id,
                        )
                    )

        return reachable_macros

    # ========================================================
    # DEPTH
    # ========================================================

    @classmethod
    def maximum_module_depth(
        cls,
        organism: Organism,
    ) -> int:

        genome = organism.genome

        graph = (
            cls.dependency_graph(
                organism
            )
        )

        roots = {
            instruction.module_id

            for instruction
            in genome.instructions

            if (
                instruction.operation
                == "CALL_MODULE"
                and instruction.module_id
                in genome.modules
            )
        }

        if not roots:
            return 0

        def depth(
            module_id: int,
            path: set[int],
        ) -> int:

            if module_id in path:

                # Cycle guard.
                return 0

            children = (
                graph.get(
                    module_id,
                    set(),
                )
            )

            if not children:
                return 1

            new_path = set(
                path
            )

            new_path.add(
                module_id
            )

            return (
                1
                + max(
                    depth(
                        child,
                        new_path,
                    )
                    for child
                    in children
                )
            )

        return max(
            depth(
                root,
                set(),
            )
            for root
            in roots
        )

    # ========================================================
    # ORGANISM REPORT
    # ========================================================

    @classmethod
    def analyze_organism(
        cls,
        organism: Organism,
    ) -> dict:

        genome = organism.genome

        (
            main_calls,
            nested_calls,
        ) = cls._direct_calls(
            organism
        )

        all_calls = (
            main_calls
            + nested_calls
        )

        existing_modules = set(
            genome.modules.keys()
        )

        reachable = (
            cls.reachable_modules(
                organism
            )
        )

        reachable_macros = (
            cls.reachable_macros(
                organism
            )
        )

        unused_modules = (
            existing_modules
            - reachable
        )

        reused_modules = {
            module_id: count

            for module_id, count
            in all_calls.items()

            if count >= 2
        }

        nested_reused_modules = {
            module_id: count

            for module_id, count
            in nested_calls.items()

            if count >= 2
        }

        defined_composite_modules = {
            module_id

            for module_id, module
            in genome.modules.items()

            if any(
                instruction.operation
                == "CALL_MODULE"

                for instruction in module
            )
        }

        active_composite_modules = (
            defined_composite_modules
            & reachable
        )

        macro_calls = 0

        # MAIN macro calls
        for instruction in (
            genome.instructions
        ):

            if (
                instruction.operation
                == "CALL_MACRO"
            ):

                macro_calls += 1

        # MODULE -> macro
        for module in (
            genome.modules.values()
        ):

            for instruction in module:

                if (
                    instruction.operation
                    == "CALL_MACRO"
                ):

                    macro_calls += 1

        # MACRO -> macro
        for macro in (
            genome.macros.values()
        ):

            for instruction in macro:

                if (
                    instruction.operation
                    == "CALL_MACRO"
                ):

                    macro_calls += 1

        return {
            "module_count":
                len(
                    existing_modules
                ),

            "reachable_modules":
                len(
                    reachable
                ),

            "referenced_modules":
                len(
                    set(
                        all_calls.keys()
                    )
                ),

            "unused_modules":
                len(
                    unused_modules
                ),

            "reused_modules":
                reused_modules,

            "nested_reused_modules":
                nested_reused_modules,

            "total_module_calls":
                sum(
                    all_calls.values()
                ),

            "main_module_calls":
                sum(
                    main_calls.values()
                ),

            "nested_module_calls":
                sum(
                    nested_calls.values()
                ),

            "composite_modules":
                len(
                    active_composite_modules
                ),

            "defined_composite_modules":
                len(
                    defined_composite_modules
                ),

            "inactive_composite_modules":
                len(
                    defined_composite_modules
                    - active_composite_modules
                ),

            "maximum_module_depth":
                cls.maximum_module_depth(
                    organism
                ),

            "macro_count":
                len(
                    genome.macros
                ),

            "reachable_macros":
                len(
                    reachable_macros
                ),

            "inactive_macros":
                (
                    len(
                        genome.macros
                    )
                    - len(
                        reachable_macros
                    )
                ),

            "macro_calls":
                macro_calls,

            "uses_macro":
                bool(
                    reachable_macros
                ),

            "call_counts":
                dict(
                    all_calls
                ),

            "main_call_counts":
                dict(
                    main_calls
                ),

            "nested_call_counts":
                dict(
                    nested_calls
                ),
        }

    # ========================================================
    # POPULATION REPORT
    # ========================================================

    @classmethod
    def analyze_population(
        cls,
        population: list[Organism],
    ) -> dict:

        if not population:

            return {
                "average_modules": 0.0,
                "average_calls": 0.0,
                "average_nested_calls": 0.0,
                "average_composite_modules": 0.0,
                "average_defined_composite_modules": 0.0,
                "average_inactive_composite_modules": 0.0,
                "average_module_depth": 0.0,
                "organisms_with_reuse": 0,
                "organisms_with_nested_calls": 0,
                "organisms_with_composites": 0,
                "average_macros": 0.0,
                "average_active_macros": 0.0,
                "average_macro_calls": 0.0,
                "organisms_with_macros": 0,
            }

        module_total = 0
        call_total = 0
        nested_call_total = 0
        composite_total = 0
        defined_composite_total = 0
        inactive_composite_total = 0
        depth_total = 0

        macro_total = 0
        active_macro_total = 0
        macro_call_total = 0

        reuse_count = 0
        nested_count = 0
        composite_organisms = 0
        macro_organisms = 0

        for organism in population:

            report = (
                cls.analyze_organism(
                    organism
                )
            )

            module_total += (
                report[
                    "module_count"
                ]
            )

            call_total += (
                report[
                    "total_module_calls"
                ]
            )

            nested_call_total += (
                report[
                    "nested_module_calls"
                ]
            )

            composite_total += (
                report[
                    "composite_modules"
                ]
            )

            defined_composite_total += (
                report[
                    "defined_composite_modules"
                ]
            )

            inactive_composite_total += (
                report[
                    "inactive_composite_modules"
                ]
            )

            depth_total += (
                report[
                    "maximum_module_depth"
                ]
            )

            macro_total += (
                report[
                    "macro_count"
                ]
            )

            active_macro_total += (
                report[
                    "reachable_macros"
                ]
            )

            macro_call_total += (
                report[
                    "macro_calls"
                ]
            )

            if report[
                "reused_modules"
            ]:

                reuse_count += 1

            if (
                report[
                    "nested_module_calls"
                ]
                > 0
            ):

                nested_count += 1

            if (
                report[
                    "composite_modules"
                ]
                > 0
            ):

                composite_organisms += 1

            if report[
                "uses_macro"
            ]:

                macro_organisms += 1

        population_size = len(
            population
        )

        return {
            "average_modules":
                module_total
                / population_size,

            "average_calls":
                call_total
                / population_size,

            "average_nested_calls":
                nested_call_total
                / population_size,

            "average_composite_modules":
                composite_total
                / population_size,

            "average_defined_composite_modules":
                defined_composite_total
                / population_size,

            "average_inactive_composite_modules":
                inactive_composite_total
                / population_size,

            "average_module_depth":
                depth_total
                / population_size,

            "organisms_with_reuse":
                reuse_count,

            "organisms_with_nested_calls":
                nested_count,

            "organisms_with_composites":
                composite_organisms,

            "average_macros":
                macro_total
                / population_size,

            "average_active_macros":
                active_macro_total
                / population_size,

            "average_macro_calls":
                macro_call_total
                / population_size,

            "organisms_with_macros":
                macro_organisms,
        }
