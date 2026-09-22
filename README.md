# Project EVOLVE

[Türkçe README](README_TR.md)

Project EVOLVE is an experimental evolutionary programming system focused on evolving executable program structures rather than only optimizing fixed numeric parameters.

## V1 Status

Version 1.0 freezes the research system at a stable experimental milestone.

Project EVOLVE V1 currently supports:

- population-based program evolution
- AST-based executable genomes
- mutation and selection of program structure
- evolved opcodes
- evolved functions
- program architecture evolution
- lineage and diversity tracking
- generated Python execution
- dual execution validation
- EVIR standalone runtime

The project has experimentally demonstrated evolved instructions with measurable causal fitness contribution.

## What V1 Is Not

V1 does not claim to have evolved a complete general-purpose programming language.

Useful evolved functions and full language autonomy remain research goals for future versions.

## Quick Start

Run the demo:

    python evolve.py demo

Run the release test:

    python evolve.py test

## Architecture

Core components include:

- EvolutionEngine
- Genome
- ASTProgram
- ProgramArchitecture
- EvolvedLanguage
- Evaluator
- DualExecutionValidator
- EVIR standalone runtime

## Research Direction

Future work may explore:

- persistent useful evolved functions
- legacy-independent programs
- reusable evolved vocabularies
- autonomous evolved language structures
- external program generation

## V1 Philosophy

V1 is intentionally frozen as a compact, reproducible research release.

The goal is to preserve a working evolutionary programming system without indefinitely delaying release for open-ended language evolution research.

## License

Released under the MIT License. See `LICENSE`.


