from __future__ import annotations

import argparse
import sys

from pathlib import Path

from evolve_ir_standalone_runtime import (
    EVIRBundleParser,
    EVIRRuntime,
)


def build_parser():

    parser = argparse.ArgumentParser(
        description=(
            "Execute an EVOLVE IR "
            "0.2 bundle."
        )
    )

    parser.add_argument(
        "file",
        type=Path,
        help="Path to .evir bundle.",
    )

    parser.add_argument(
        "input",
        type=float,
        help="Input value.",
    )

    parser.add_argument(
        "context",
        type=int,
        help="Execution context.",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help=(
            "Show bundle metadata "
            "before execution."
        ),
    )

    return parser


def main():

    args = (
        build_parser()
        .parse_args()
    )

    if not args.file.exists():

        print(
            "ERROR: EVIR file "
            "does not exist:",
            args.file,
            file=sys.stderr,
        )

        raise SystemExit(1)

    bundle = (
        EVIRBundleParser.parse(
            args.file
        )
    )

    if bundle.version != "0.2":

        print(
            "ERROR: unsupported "
            "EVIR version:",
            bundle.version,
            file=sys.stderr,
        )

        raise SystemExit(1)

    runtime = EVIRRuntime(
        bundle
    )

    result = runtime.run(
        args.input,
        args.context,
    )

    if args.info:

        print(
            "EVIR VERSION:",
            bundle.version,
        )

        print(
            "GENERATION:",
            bundle.metadata.get(
                "generation"
            ),
        )

        print(
            "ORGANISM:",
            bundle.metadata.get(
                "organism_id"
            ),
        )

        print(
            "MACROS:",
            sorted(
                bundle.macros
            ),
        )

        print(
            "MODULES:",
            sorted(
                bundle.modules
            ),
        )

        print(
            "OPCODES:",
            sorted(
                bundle.opcodes
            ),
        )

        print()

    print(
        "INPUT:",
        float(args.input),
    )

    print(
        "CONTEXT:",
        int(args.context),
    )

    print(
        "OUTPUT:",
        result,
    )


if __name__ == "__main__":
    main()
