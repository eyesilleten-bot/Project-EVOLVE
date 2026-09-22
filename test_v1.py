from pathlib import Path
import importlib

MODULES = [
    "config",
    "ast_program",
    "program_architecture",
    "evolved_language",
    "organism",
    "environment",
    "evaluator",
    "genome",
    "generated_runtime",
    "generated_python_runner",
    "python_emitter",
    "dual_execution_validator",
    "state_manager",
    "evolution_engine",
    "evir",
    "evolve_ir_standalone_runtime",
]


def test_imports():
    errors = []

    for module_name in MODULES:
        try:
            importlib.import_module(
                module_name
            )
        except Exception as exc:
            errors.append(
                (
                    module_name,
                    repr(exc),
                )
            )

    return errors


def test_engine_creation():
    from evolution_engine import EvolutionEngine

    engine = EvolutionEngine()

    return engine


def main():

    print("=" * 78)
    print("PROJECT EVOLVE V1 — RELEASE TEST")
    print("=" * 78)

    print()
    print("[1/3] Core imports")

    import_errors = test_imports()

    if import_errors:

        print(
            "FAIL"
        )

        for module_name, error in import_errors:
            print(
                module_name,
                "=>",
                error,
            )

        return 1

    print(
        "PASS"
    )


    print()
    print("[2/3] EvolutionEngine creation")

    try:

        engine = test_engine_creation()

        print(
            "PASS",
            type(engine).__name__,
        )

    except Exception as exc:

        print(
            "FAIL",
            repr(exc),
        )

        return 1


    print()
    print("[3/3] EVIR standalone runtime")

    try:

        runtime = importlib.import_module(
            "evolve_ir_standalone_runtime"
        )

        print(
            "PASS",
            runtime.__name__,
        )

    except Exception as exc:

        print(
            "FAIL",
            repr(exc),
        )

        return 1


    print()
    print("=" * 78)
    print("V1 RELEASE STATUS")
    print("=" * 78)
    print("PASS: True")

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
