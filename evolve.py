import argparse
import importlib

from evolution_engine import EvolutionEngine


def run_demo():
    print("=" * 78)
    print("PROJECT EVOLVE V1")
    print("=" * 78)
    print()
    print("Experimental evolutionary programming system")
    print()

    print("[1/4] Creating evolution engine...")
    engine = EvolutionEngine()
    print("PASS:", type(engine).__name__)

    print()
    print("[2/4] Loading core architecture modules...")
    modules = [
        "ast_program",
        "program_architecture",
        "evolved_language",
        "genome",
        "dual_execution_validator",
    ]

    for module_name in modules:
        importlib.import_module(module_name)
        print("PASS:", module_name)

    print()
    print("[3/4] Loading EVIR standalone runtime...")
    runtime = importlib.import_module(
        "evolve_ir_standalone_runtime"
    )
    print("PASS:", runtime.__name__)

    print()
    print("[4/4] V1 capabilities")
    print("- evolutionary program architecture")
    print("- AST-based executable genomes")
    print("- evolved opcodes and functions")
    print("- lineage / diversity tracking")
    print("- generated Python execution")
    print("- dual execution validation")
    print("- EVIR standalone runtime")

    print()
    print("=" * 78)
    print("DEMO COMPLETE")
    print("=" * 78)


def run_test():
    import test_v1

    raise SystemExit(
        test_v1.main()
    )


def main():
    parser = argparse.ArgumentParser(
        prog="Project EVOLVE",
        description=(
            "Project EVOLVE V1 - "
            "Experimental evolutionary programming system"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command"
    )

    subparsers.add_parser(
        "demo",
        help="Run the V1 demonstration",
    )

    subparsers.add_parser(
        "test",
        help="Run the V1 release test",
    )

    args = parser.parse_args()

    if args.command == "demo":
        run_demo()

    elif args.command == "test":
        run_test()

    else:
        run_demo()
        print()
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
