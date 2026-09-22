# main.py

import random

from config import (
    GENERATIONS,
    RANDOM_SEED,
    REPORT_EVERY,
)

from evolution_engine import (
    EvolutionEngine,
)
from state_manager import (
    StateManager,
)


def print_task_performance(
    organism,
) -> None:

    task_errors = getattr(
        organism,
        "task_errors",
        {},
    )

    print()
    print("TASK PERFORMANCE")

    for (
        task_name,
        error,
    ) in sorted(
        task_errors.items()
    ):
        print(
            f"{task_name}: "
            f"mean error = "
            f"{error:.6f}"
        )


def print_generation_report(
    engine: EvolutionEngine,
) -> None:

    best = engine.population[0]

    diversity = (
        engine.diversity_report()
    )

    print()
    print("=" * 70)

    print(
        f"GENERATION "
        f"{engine.generation}"
    )

    print("-" * 70)

    print(
        f"Best fitness:       "
        f"{best.fitness:.4f}"
    )

    print(
        f"Average fitness:    "
        f"{engine.average_fitness():.4f}"
    )

    print(
        f"Best error:         "
        f"{best.error:.6f}"
    )

    print(
        f"Best organism:      "
        f"{best.id}"
    )

    print(
        f"Parent:             "
        f"{best.parent_id}"
    )

    print(
        f"Lineage depth:      "
        f"{best.lineage_depth}"
    )

    print(
        f"Genome length:      "
        f"{len(best.genome.instructions)}"
    )

    print(
        f"Archive size:       "
        f"{engine.archive_size()}"
    )

    print()
    print("DIVERSITY")

    print(
        f"Unique genomes:     "
        f"{diversity['unique_genomes']}"
        f"/{len(engine.population)}"
    )

    print(
        f"Genome diversity:   "
        f"{diversity['diversity_ratio']:.2%}"
    )

    print(
        f"Avg genome length:  "
        f"{diversity['average_genome_length']:.2f}"
    )

    print(
        f"Avg modules:        "
        f"{diversity['average_module_count']:.2f}"
    )

    usage = diversity[
        "operation_usage"
    ]

    print(
        "Operation usage:    "
        f"ADD={usage.get('ADD', 0)}, "
        f"SUBTRACT={usage.get('SUBTRACT', 0)}, "
        f"MULTIPLY={usage.get('MULTIPLY', 0)}"
    )

    module_report = (
        engine.module_report()
    )

    print()
    print("MODULE ECOLOGY")

    print(
        f"Avg module calls:   "
        f"{module_report['average_calls']:.2f}"
    )

    print(
        f"Organisms reusing:  "
        f"{module_report['organisms_with_reuse']}"
        f"/{len(engine.population)}"
    )

    lineage_report = (
        engine.module_lineage_report()
    )

    print(
        f"Module variants seen:"
        f" {lineage_report['archived_module_variants']}"
    )

    print(
        f"Variants alive now: "
        f"{lineage_report['current_module_variants']}"
    )

    family_report = (
        engine.module_family_report()
    )

    print()
    print("MODULE FAMILIES")

    print(
        f"Families ever seen: "
        f"{family_report['families_ever_seen']}"
    )

    print(
        f"Families alive:     "
        f"{family_report['families_alive']}"
    )

    print(
        f"Families extinct:   "
        f"{family_report['families_extinct']}"
    )

    dominants = (
        family_report[
            "dominant_families"
        ]
    )

    if dominants:

        names = ", ".join(
            family["family"]
            for family
            in dominants
        )

        maximum_spread = (
            dominants[0][
                "organisms"
            ]
        )

        print(
            f"Dominant families: "
            f"{names}"
        )

        print(
            f"Dominant spread:    "
            f"{maximum_spread}"
            f"/{len(engine.population)}"
        )

    family_events = (
        engine.family_event_report()
    )

    print()
    print("FAMILY EVENTS")

    print(
        f"Events total:       "
        f"{family_events['total_events']}"
    )

    print(
        f"New this generation:"
        f" {len(family_events['new_events'])}"
    )

    for event in (
        family_events[
            "new_events"
        ]
    ):

        print(
            f"  {event['event_type']} | "
            f"{event['family']} | "
            f"{event['percentage']:.1f}%"
        )

    print_task_performance(
        best
    )

    novelty = (
        engine.novelty_report()
    )

    print()
    print("NOVELTY")

    print(
        f"Known structures:    "
        f"{novelty['total_structures']}"
    )

    print(
        f"New this generation: "
        f"{novelty['new_this_generation']}"
    )

    major = (
        engine.major_event_report()
    )

    print()
    print("EVOLUTIONARY EVENTS")

    print(
        f"Major events total:  "
        f"{major['total_events']}"
    )

    print(
        f"New this generation: "
        f"{major['new_this_generation']}"
    )

    print(
        f"Best modules:       "
        f"{best.genome.module_count()}"
    )

    best_module_report = (
        engine.organism_module_report(
            best
        )
    )

    print(
        f"Best module calls:  "
        f"{best_module_report['total_module_calls']}"
    )

    print(
        f"Best unused modules:"
        f" {best_module_report['unused_modules']}"
    )

    print(
        f"Best reused modules:"
        f" {best_module_report['reused_modules']}"
    )

    print()
    print("BEST GENOME:")
    print(
        best.genome.describe()
    )


def print_lineage(
    engine: EvolutionEngine,
    organism_id: str,
) -> None:

    lineage = (
        engine.trace_lineage(
            organism_id,
            max_depth=15,
        )
    )

    print()
    print("=" * 70)
    print("CHAMPION LINEAGE")
    print("=" * 70)

    for index, record in enumerate(
        lineage
    ):
        prefix = (
            "CURRENT"
            if index == 0
            else f"ANCESTOR {index}"
        )

        print()
        print(
            f"{prefix}: "
            f"{record['id']}"
        )

        print(
            f"Generation: "
            f"{record['generation']}"
        )

        print(
            f"Genome: "
            f"{record['genome']}"
        )

        print(
            "Birth mutations:"
        )

        for mutation in (
            record[
                "birth_mutations"
            ]
        ):
            print(
                f"  - {mutation}"
            )


def hidden_generalization_test(
    engine: EvolutionEngine,
    organism,
) -> None:

    print()
    print("=" * 70)

    print(
        "HIDDEN TASK TEST"
    )

    print("=" * 70)

    task = (
        engine
        .environment
        .hidden_task
    )

    print(
        f"Hidden rule: "
        f"{task.multiplier}x "
        f"+ {task.bias}"
    )

    print()

    total_error = 0.0
    cases = (
        engine
        .environment
        .hidden_generalization_cases()
    )

    for (
        _task,
        input_value,
        expected,
    ) in cases:

        output = organism.run(
            input_value,
            task.context_id,
        )

        error = abs(
            expected - output
        )

        total_error += error

        print(
            f"x={input_value:6.2f} | "
            f"EVOLVE={output:10.4f} | "
            f"expected={expected:10.4f} | "
            f"error={error:.4f}"
        )

    mean_error = (
        total_error
        / len(cases)
    )

    print()
    print(
        f"Hidden task mean error: "
        f"{mean_error:.6f}"
    )


def main() -> None:

    random.seed(
        RANDOM_SEED
    )

    print()
    print("PROJECT EVOLVE")

    print(
        "V0.2.3 — PERSISTENT EVOLUTION"
    )

    print()

    print(
        "WE WROTE GENERATION ZERO."
    )

    print(
        "Everything after that "
        "is an experiment."
    )

    print()

    engine = EvolutionEngine()

    loaded = (
        StateManager.load(
            engine
        )
    )

    if loaded:

        print()
        print(
            "PERSISTENT STATE FOUND."
        )

        print(
            f"Resuming from "
            f"generation "
            f"{engine.generation}."
        )

    else:

        print()
        print(
            "NO SAVE FOUND."
        )

        print(
            "Creating Generation Zero."
        )

        engine.create_generation_zero()

    engine.evaluate_population()

    print_generation_report(
        engine
    )

    for _ in range(
        GENERATIONS
    ):

        engine.create_next_generation()

        engine.evaluate_population()

        if (
            engine.generation
            % REPORT_EVERY
            == 0
        ):
            print_generation_report(
                engine
            )

        if (
            engine.generation > 0
            and engine.generation % 50 == 0
        ):
            StateManager.save(
                engine
            )

            print(
                f"[AUTOSAVE] "
                f"Generation "
                f"{engine.generation}"
            )

    StateManager.save(
        engine
    )

    print()
    print(
        f"STATE SAVED AT "
        f"GENERATION "
        f"{engine.generation}"
    )

    print()
    print("=" * 70)
    print(
        "EVOLUTION RUN COMPLETE"
    )
    print("=" * 70)

    best = engine.best_ever

    if best is None:
        return

    print()

    print(
        f"Best organism ever: "
        f"{best.id}"
    )

    print(
        f"Born generation:    "
        f"{best.generation}"
    )

    print(
        f"Best fitness ever:  "
        f"{best.fitness:.4f}"
    )

    print(
        f"Best error ever:    "
        f"{best.error:.6f}"
    )

    print()
    print(
        "BEST EVOLVED GENOME:"
    )

    print(
        best.genome.describe()
    )

    print()
    print("=" * 70)
    print("MODULE ABLATION TEST")
    print("=" * 70)

    ablation_results = (
        engine.ablation_report(
            best
        )
    )

    for result in (
        ablation_results
    ):

        print()

        module_id = (
            result["module_id"]
        )

        print(
            f"M{module_id:03d}"
        )

        if not result["valid"]:

            print(
                "Ablation invalid."
            )

            continue

        print(
            f"Baseline fitness: "
            f"{result['baseline_fitness']:.4f}"
        )

        print(
            f"Without module:   "
            f"{result['ablated_fitness']:.4f}"
        )

        print(
            f"Fitness loss:     "
            f"{result['fitness_loss']:.4f}"
        )

        print(
            f"Baseline error:   "
            f"{result['baseline_error']:.6f}"
        )

        print(
            f"Ablated error:    "
            f"{result['ablated_error']:.6f}"
        )

        print(
            "Task errors without module:"
        )

        for (
            task_name,
            error,
        ) in result[
            "task_errors"
        ].items():

            print(
                f"  {task_name}: "
                f"{error:.6f}"
            )

    best_module_report = (
        engine.organism_module_report(
            best
        )
    )

    print()
    print("MODULE REUSE REPORT")

    print(
        f"Modules: "
        f"{best_module_report['module_count']}"
    )

    print(
        f"Referenced modules: "
        f"{best_module_report['referenced_modules']}"
    )

    print(
        f"Total module calls: "
        f"{best_module_report['total_module_calls']}"
    )

    print(
        f"Unused modules: "
        f"{best_module_report['unused_modules']}"
    )

    print(
        "Call counts:"
    )

    for (
        module_id,
        count,
    ) in sorted(
        best_module_report[
            "call_counts"
        ].items()
    ):

        print(
            f"  M{module_id:03d}: "
            f"{count} call(s)"
        )

    print(
        "Reused modules:"
    )

    if (
        best_module_report[
            "reused_modules"
        ]
    ):

        for (
            module_id,
            count,
        ) in sorted(
            best_module_report[
                "reused_modules"
            ].items()
        ):

            print(
                f"  M{module_id:03d}: "
                f"{count} calls"
            )

    else:

        print(
            "  none"
        )

    print()
    print("CHAMPION MODULE IDENTITIES")

    for (
        module_id,
        metadata,
    ) in sorted(
        best.genome.module_meta.items()
    ):

        print(
            f"M{module_id:03d}: "
            f"{metadata['uid']} | "
            f"origin="
            f"{metadata['origin']} | "
            f"born="
            f"{metadata['birth_generation']} | "
            f"parent="
            f"{metadata['parent_uid']}"
        )

    for (
        module_id,
        metadata,
    ) in sorted(
        best.genome.module_meta.items()
    ):

        print()
        print(
            f"MODULE LINEAGE "
            f"M{module_id:03d}"
        )

        lineage = (
            engine.trace_module_lineage(
                metadata["uid"],
                max_depth=10,
            )
        )

        for index, record in enumerate(
            lineage
        ):

            label = (
                "CURRENT"
                if index == 0
                else f"ANCESTOR {index}"
            )

            print(
                f"{label}: "
                f"{record['uid']} | "
                f"Gen "
                f"{record['birth_generation']} | "
                f"{record['origin']}"
            )

    family_report = (
        engine.module_family_report()
    )

    print()
    print("=" * 70)
    print("MODULE FAMILY ECOLOGY")
    print("=" * 70)

    print(
        f"Families ever seen: "
        f"{family_report['families_ever_seen']}"
    )

    print(
        f"Families alive: "
        f"{family_report['families_alive']}"
    )

    print(
        f"Families extinct: "
        f"{family_report['families_extinct']}"
    )

    print()
    print("TOP LIVING FAMILIES")

    for family in (
        family_report["families"][:10]
    ):

        print()

        print(
            f"Family: "
            f"{family['family']}"
        )

        print(
            f"Present in organisms: "
            f"{family['organisms']}"
            f"/{len(engine.population)}"
        )

        print(
            f"Module instances: "
            f"{family['module_instances']}"
        )

        print(
            f"Living variants: "
            f"{family['living_variants']}"
        )

        print(
            f"First seen generation: "
            f"{family['first_seen']}"
        )

        print(
            f"Historical peak: "
            f"{family['peak_organisms']}"
            f"/{len(engine.population)}"
        )

    family_events = (
        engine.family_event_report()
    )

    print()
    print("=" * 70)
    print("RECENT FAMILY EVENTS")
    print("=" * 70)

    print(
        f"Total family events: "
        f"{family_events['total_events']}"
    )

    for event in (
        family_events[
            "recent_events"
        ]
    ):

        print()

        print(
            f"Generation "
            f"{event['generation']}"
        )

        print(
            f"{event['event_type']} | "
            f"{event['family']}"
        )

        print(
            f"Spread: "
            f"{event['organisms']}/"
            f"{event['population_size']} "
            f"({event['percentage']:.1f}%)"
        )

    novelty = (
        engine.novelty_report()
    )

    print()
    print(
        "NOVELTY SUMMARY"
    )

    print(
        f"Total unique program structures: "
        f"{novelty['total_structures']}"
    )

    print()
    print(
        "RECENT NOVEL STRUCTURES"
    )

    for event in (
        novelty["recent_events"]
    ):

        print()

        print(
            f"Generation "
            f"{event['generation']} | "
            f"{event['organism_id']}"
        )

        print(
            f"Length: "
            f"{event['genome_length']}"
        )

        print(
            event["genome"]
        )

    major = (
        engine.major_event_report()
    )

    print()
    print("=" * 70)
    print(
        "MAJOR EVOLUTIONARY EVENTS"
    )
    print("=" * 70)

    print(
        f"Total major events: "
        f"{major['total_events']}"
    )

    for event in (
        major["recent_events"]
    ):

        print()
        print(
            f"Generation "
            f"{event['generation']} | "
            f"{event['organism_id']}"
        )

        print(
            f"Fitness: "
            f"{event['fitness']:.4f}"
        )

        print(
            f"Fitness gain: "
            f"+{event['fitness_gain']:.4f}"
        )

        print(
            f"Mean error: "
            f"{event['error']:.6f}"
        )

        print(
            f"Genome length: "
            f"{event['genome_length']}"
        )

        print(
            "Genome:"
        )

        print(
            event["genome"]
        )

        print(
            "Task errors:"
        )

        for (
            task_name,
            error,
        ) in event[
            "task_errors"
        ].items():

            print(
                f"  {task_name}: "
                f"{error:.6f}"
            )

        print(
            "Birth mutations:"
        )

        for mutation in (
            event[
                "birth_mutations"
            ]
        ):

            print(
                f"  - {mutation}"
            )

    print_task_performance(
        best
    )

    hidden_generalization_test(
        engine,
        best,
    )

    print_lineage(
        engine,
        best.id,
    )


if __name__ == "__main__":
    main()