# config.py

RANDOM_SEED = 42

POPULATION_SIZE = 80
GENERATIONS = 500

ELITE_COUNT = 16

MUTATION_RATE = 0.35
PARAMETER_MUTATION_SCALE = 1.0

MIN_GENOME_LENGTH = 1
MAX_GENOME_LENGTH = 20

REPORT_EVERY = 50


# ---------------------------------------------------------
# HIERARCHICAL ABSTRACTIONS
# ---------------------------------------------------------

MAX_MODULES = 12

MAX_MODULE_LENGTH = 10

MAX_MODULE_CALL_DEPTH = 8

COMPOSITE_MODULE_RATE = 0.035

COMPOSITE_REPLACEMENT_CHANCE = 0.70

MODULE_CALL_MUTATION_RATE = 0.20


# ---------------------------------------------------------
# EVOLVED VOCABULARY
# ---------------------------------------------------------

MAX_MACROS = 10

MAX_MACRO_LENGTH = 8

MACRO_CREATION_RATE = 0.025

MACRO_REPLACEMENT_CHANCE = 0.80

MACRO_INSTRUCTION_RATE = 0.12


# ---------------------------------------------------------
# V0.7 AST EVOLUTION
# ---------------------------------------------------------

MAX_AST_NODES = 30

MAX_AST_DEPTH = 8

AST_EXECUTION_BUDGET = 120

AST_CREATION_RATE = 0.02

AST_BRIDGE_CREATION_CHANCE = 0.80

AST_PARAMETER_MUTATION_RATE = 0.25

AST_PARAMETER_MUTATION_SCALE = 0.75

AST_NODE_REPLACEMENT_RATE = 0.12

AST_SUBTREE_INSERT_RATE = 0.10

AST_SUBTREE_DELETE_RATE = 0.08

AST_SUBTREE_DUPLICATION_RATE = 0.06

AST_STRUCTURE_MUTATION_SHARE = 0.70


# =========================================================
# V0.9 — PROGRAM ARCHITECTURE EVOLUTION
# =========================================================

ARCH_CREATION_RATE = 0.015

MAX_ARCH_FUNCTIONS = 8

# Bir ARCH child doğduktan sonra tek mutation domain seçilir.
# Aşağıdaki ağırlıkların toplamı 1.0'dır.

ARCH_CREATE_FUNCTION_WEIGHT = 0.18
ARCH_DUPLICATE_FUNCTION_WEIGHT = 0.10
ARCH_DELETE_FUNCTION_WEIGHT = 0.08

ARCH_BODY_MUTATION_WEIGHT = 0.40

ARCH_INSERT_CALL_WEIGHT = 0.14
ARCH_RETARGET_CALL_WEIGHT = 0.10

ARCH_PARAMETER_MUTATION_SCALE = 0.75


# =========================================================
# V1.0.6 — EVOLVED OPCODE VOCABULARY
# =========================================================

MAX_EVOLVED_OPCODES = 10

# ARCH child doğduğunda mutation domain:
#
# language domain vs architecture domain.
LANGUAGE_MUTATION_SHARE = 0.20

# Language domain içindeki mutation ağırlıkları.
# Toplam = 1.0
OPCODE_CREATE_WEIGHT = 0.12
OPCODE_DERIVE_WEIGHT = 0.10
OPCODE_MUTATE_WEIGHT = 0.38
OPCODE_DELETE_WEIGHT = 0.10

OPCODE_INSERT_CALL_WEIGHT = 0.10
OPCODE_LOCAL_INSERT_CALL_WEIGHT = 0.10
OPCODE_RETARGET_CALL_WEIGHT = 0.10

OPCODE_PARAMETER_MUTATION_SCALE = 0.75

DERIVED_OPCODE_PARAMETER_MUTATION_SCALE = 0.20

DERIVED_OPCODE_GENTLE_PROBABILITY = 0.80
