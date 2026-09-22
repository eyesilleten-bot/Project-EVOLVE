from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class Instruction:

    operation: str
    value: float = 0.0
    context: int = 0
    offset: int = 1
    module_id: int | None = None
    macro_id: int | None = None


@dataclass
class Node:

    node_type: str

    value: float | None = None
    context: int | None = None

    target: str | int | None = None

    children: list["Node"] | None = None


class ExpressionParser:

    TOKEN_PATTERN = re.compile(
        r"""
        \s*
        (
            [A-Za-z_][A-Za-z0-9_]*
            |
            [+-]?(?:\d+(?:\.\d*)?|\.\d+)
            |
            \(
            |
            \)
            |
            ,
        )
        """,
        re.VERBOSE,
    )

    def __init__(
        self,
        text: str,
    ):

        self.tokens = [
            match.group(1)

            for match in (
                self.TOKEN_PATTERN
                .finditer(text)
            )
        ]

        self.index = 0

    def peek(self):

        if self.index >= len(
            self.tokens
        ):

            return None

        return self.tokens[
            self.index
        ]

    def take(self):

        token = self.peek()

        if token is None:

            raise ValueError(
                "Unexpected end of expression."
            )

        self.index += 1

        return token

    def expect(
        self,
        expected,
    ):

        token = self.take()

        if token != expected:

            raise ValueError(
                f"Expected {expected!r}, "
                f"received {token!r}."
            )

    def parse(self):

        result = (
            self.parse_expression()
        )

        if self.peek() is not None:

            raise ValueError(
                "Unexpected trailing token: "
                f"{self.peek()}"
            )

        return result

    def parse_expression(self):

        operation = self.take()

        if operation in {
            "ABS",
            "CALL_LEGACY_MAIN",
        }:

            return Node(
                node_type=operation,
                children=[],
            )

        self.expect("(")

        if operation == "SEQ":

            children = []

            if self.peek() != ")":

                while True:

                    children.append(
                        self.parse_expression()
                    )

                    if self.peek() == ",":

                        self.take()
                        continue

                    break

            self.expect(")")

            return Node(
                node_type="SEQUENCE",
                children=children,
            )

        if operation in {
            "ADD",
            "SUBTRACT",
            "MULTIPLY",
            "DIVIDE",
        }:

            value = float(
                self.take()
            )

            self.expect(")")

            return Node(
                node_type=operation,
                value=value,
                children=[],
            )

        if operation == "IF_CONTEXT":

            context = int(
                float(
                    self.take()
                )
            )

            self.expect(",")

            child = (
                self.parse_expression()
            )

            self.expect(")")

            return Node(
                node_type="IF_CONTEXT",
                context=context,
                children=[
                    child
                ],
            )

        if operation in {
            "CALL_OPCODE",
            "CALL_MACRO",
            "CALL_MODULE",
            "CALL_FUNCTION",
        }:

            target = self.take()

            self.expect(")")

            if operation in {
                "CALL_MACRO",
                "CALL_MODULE",
                "CALL_FUNCTION",
            }:

                target = int(
                    target[1:]
                )

            return Node(
                node_type=operation,
                target=target,
                children=[],
            )

        raise ValueError(
            "Unsupported AST operation: "
            f"{operation}"
        )


class EVIRBundle:

    def __init__(
        self,
    ):

        self.version = None
        self.metadata = {}

        self.main = None

        self.legacy_main = []

        self.macros = {}
        self.modules = {}

        self.functions = {}
        self.opcodes = {}

        self.manifest = {}


class EVIRBundleParser:

    @staticmethod
    def parse_instruction(
        line: str,
    ) -> Instruction:

        parts = [
            part.strip()

            for part in line.split("|")
        ]

        if len(parts) != 7:

            raise ValueError(
                "Invalid instruction line: "
                f"{line}"
            )

        operation = parts[1]

        fields = {}

        for part in parts[2:]:

            key, value = (
                part.split(
                    "=",
                    1,
                )
            )

            fields[
                key.strip()
            ] = value.strip()

        module_text = (
            fields["module"]
        )

        macro_text = (
            fields["macro"]
        )

        module_id = (
            None

            if module_text == "none"

            else int(
                module_text[1:]
            )
        )

        macro_id = (
            None

            if macro_text == "none"

            else int(
                macro_text[1:]
            )
        )

        return Instruction(
            operation=operation,

            value=float(
                fields["value"]
            ),

            context=int(
                fields["context"]
            ),

            offset=int(
                fields["offset"]
            ),

            module_id=module_id,
            macro_id=macro_id,
        )

    @classmethod
    def parse(
        cls,
        path: Path,
    ) -> EVIRBundle:

        lines = path.read_text(
            encoding="utf-8"
        ).splitlines()

        if not lines:

            raise ValueError(
                "Empty EVIR bundle."
            )

        header = (
            lines[0].strip()
        )

        if not header.startswith(
            "EVOLVE_IR "
        ):

            raise ValueError(
                "Invalid EVIR header."
            )

        bundle = EVIRBundle()

        bundle.version = (
            header.split(
                None,
                1,
            )[1]
        )

        sections = {}
        current = None

        for raw_line in lines[1:]:

            stripped = (
                raw_line.strip()
            )

            if (
                stripped.startswith("[")
                and
                stripped.endswith("]")
            ):

                current = (
                    stripped[1:-1]
                )

                sections[
                    current
                ] = []

                continue

            if current is not None:

                sections[
                    current
                ].append(
                    raw_line
                )

        for line in sections.get(
            "metadata",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or "=" not in stripped
            ):

                continue

            key, value = (
                stripped.split(
                    "=",
                    1,
                )
            )

            bundle.metadata[
                key.strip()
            ] = value.strip().strip(
                '"'
            )

        main_lines = [
            line.strip()

            for line in sections.get(
                "main",
                []
            )

            if line.strip()
        ]

        if len(main_lines) != 1:

            raise ValueError(
                "Invalid [main] section."
            )

        bundle.main = (
            ExpressionParser(
                main_lines[0]
            ).parse()
        )

        for line in sections.get(
            "legacy_main",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or stripped == "none"
            ):

                continue

            bundle.legacy_main.append(
                cls.parse_instruction(
                    stripped
                )
            )

        current_macro = None

        for line in sections.get(
            "macros",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or stripped == "none"
            ):

                continue

            if stripped.startswith(
                "macro K"
            ):

                current_macro = int(
                    stripped.split(
                        "K",
                        1,
                    )[1]
                )

                bundle.macros[
                    current_macro
                ] = []

                continue

            if current_macro is None:

                raise ValueError(
                    "Macro instruction before "
                    "macro declaration."
                )

            bundle.macros[
                current_macro
            ].append(
                cls.parse_instruction(
                    stripped
                )
            )

        current_module = None

        for line in sections.get(
            "modules",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or stripped == "none"
            ):

                continue

            if stripped.startswith(
                "module M"
            ):

                current_module = int(
                    stripped.split(
                        "M",
                        1,
                    )[1]
                )

                bundle.modules[
                    current_module
                ] = []

                continue

            if current_module is None:

                raise ValueError(
                    "Module instruction before "
                    "module declaration."
                )

            bundle.modules[
                current_module
            ].append(
                cls.parse_instruction(
                    stripped
                )
            )

        for line in sections.get(
            "reachable_functions",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or stripped == "none"
            ):

                continue

            function_name, body = (
                stripped.split(
                    "=",
                    1,
                )
            )

            function_id = int(
                function_name
                .strip()[1:]
            )

            bundle.functions[
                function_id
            ] = ExpressionParser(
                body.strip()
            ).parse()

        current_opcode = None

        for line in sections.get(
            "reachable_opcodes",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or stripped == "none"
            ):

                continue

            if stripped.startswith(
                "opcode "
            ):

                current_opcode = (
                    stripped.split(
                        None,
                        1,
                    )[1]
                )

                continue

            if stripped.startswith(
                "body ="
            ):

                if current_opcode is None:

                    raise ValueError(
                        "Opcode body before "
                        "opcode declaration."
                    )

                body = (
                    stripped.split(
                        "=",
                        1,
                    )[1]
                    .strip()
                )

                bundle.opcodes[
                    current_opcode
                ] = ExpressionParser(
                    body
                ).parse()

        for line in sections.get(
            "dependency_manifest",
            [],
        ):

            stripped = line.strip()

            if (
                not stripped
                or "=" not in stripped
            ):

                continue

            key, value = (
                stripped.split(
                    "=",
                    1,
                )
            )

            bundle.manifest[
                key.strip()
            ] = value.strip()

        return bundle


class EVIRRuntime:

    def __init__(
        self,
        bundle: EVIRBundle,
    ):

        self.bundle = bundle

        self.call_depth = 0
        self.max_call_depth = 128

    def guarded_call(
        self,
        function,
        *args,
    ):

        self.call_depth += 1

        try:

            if (
                self.call_depth
                > self.max_call_depth
            ):

                raise RuntimeError(
                    "EVIR maximum call depth "
                    "exceeded."
                )

            return function(
                *args
            )

        finally:

            self.call_depth -= 1

    def execute_instruction_sequence(
        self,
        instructions,
        value,
        context,
    ):

        index = 0

        while index < len(
            instructions
        ):

            instruction = (
                instructions[index]
            )

            operation = (
                instruction.operation
            )

            if operation == "ADD":

                value += (
                    instruction.value
                )

            elif (
                operation
                == "SUBTRACT"
            ):

                value -= (
                    instruction.value
                )

            elif (
                operation
                == "MULTIPLY"
            ):

                value *= (
                    instruction.value
                )

            elif (
                operation
                == "DIVIDE"
            ):

                if (
                    abs(
                        instruction.value
                    )
                    > 1e-12
                ):

                    value /= (
                        instruction.value
                    )

            elif (
                operation
                == "CALL_MACRO"
            ):

                macro_id = (
                    instruction.macro_id
                )

                if macro_id not in (
                    self.bundle.macros
                ):

                    raise RuntimeError(
                        "Missing macro "
                        f"K{macro_id:03d}"
                    )

                value = (
                    self.guarded_call(
                        self.execute_instruction_sequence,
                        self.bundle.macros[
                            macro_id
                        ],
                        value,
                        context,
                    )
                )

            elif (
                operation
                == "CALL_MODULE"
            ):

                module_id = (
                    instruction.module_id
                )

                if module_id not in (
                    self.bundle.modules
                ):

                    raise RuntimeError(
                        "Missing module "
                        f"M{module_id:03d}"
                    )

                value = (
                    self.guarded_call(
                        self.execute_instruction_sequence,
                        self.bundle.modules[
                            module_id
                        ],
                        value,
                        context,
                    )
                )

            elif (
                operation
                == "JUMP_IF_CONTEXT_NE"
            ):

                if (
                    context
                    != instruction.context
                ):

                    index += (
                        instruction.offset
                    )

                    continue

            else:

                raise RuntimeError(
                    "Unsupported legacy "
                    "instruction: "
                    f"{operation}"
                )

            index += 1

        return value

    def execute_ast(
        self,
        node,
        value,
        context,
    ):

        node_type = (
            node.node_type
        )

        if node_type == "SEQUENCE":

            for child in (
                node.children
            ):

                value = self.execute_ast(
                    child,
                    value,
                    context,
                )

            return value

        if node_type == "ADD":

            return value + node.value

        if node_type == "SUBTRACT":

            return value - node.value

        if node_type == "MULTIPLY":

            return value * node.value

        if node_type == "DIVIDE":

            if abs(
                node.value
            ) <= 1e-12:

                return value

            return value / node.value

        if node_type == "ABS":

            return abs(value)

        if node_type == "IF_CONTEXT":

            if context == node.context:

                return self.execute_ast(
                    node.children[0],
                    value,
                    context,
                )

            return value

        if (
            node_type
            == "CALL_LEGACY_MAIN"
        ):

            return self.guarded_call(
                self.execute_instruction_sequence,
                self.bundle.legacy_main,
                value,
                context,
            )

        if node_type == "CALL_MACRO":

            macro_id = int(
                node.target
            )

            return self.guarded_call(
                self.execute_instruction_sequence,
                self.bundle.macros[
                    macro_id
                ],
                value,
                context,
            )

        if node_type == "CALL_MODULE":

            module_id = int(
                node.target
            )

            return self.guarded_call(
                self.execute_instruction_sequence,
                self.bundle.modules[
                    module_id
                ],
                value,
                context,
            )

        if (
            node_type
            == "CALL_OPCODE"
        ):

            opcode_id = str(
                node.target
            )

            return self.guarded_call(
                self.execute_ast,
                self.bundle.opcodes[
                    opcode_id
                ],
                value,
                context,
            )

        if (
            node_type
            == "CALL_FUNCTION"
        ):

            function_id = int(
                node.target
            )

            return self.guarded_call(
                self.execute_ast,
                self.bundle.functions[
                    function_id
                ],
                value,
                context,
            )

        raise RuntimeError(
            "Unsupported AST node: "
            f"{node_type}"
        )

    def run(
        self,
        input_value,
        context,
    ):

        self.call_depth = 0

        return self.execute_ast(
            self.bundle.main,
            float(input_value),
            int(context),
        )


REFERENCE_CASES = [

    (0, -8.0, 9.78919310774093),
    (0, -4.0, 2.819535196257677),
    (0, -2.0, -0.6652937594839481),
    (0, 0.0, 0.6123948500640115),
    (0, 2.0, 4.097223805805635),
    (0, 4.0, 7.582052761547258),
    (0, 8.0, 14.551710673030511),

    (1, -8.0, 14.847691851404871),
    (1, -4.0, 7.878033939921621),
    (1, -2.0, 4.393204984179997),
    (1, 0.0, 0.9083760284383717),
    (1, 2.0, 2.576452927303253),
    (1, 4.0, 6.061281883044876),
    (1, 8.0, 13.030939794528123),

    (2, -8.0, 12.840398385832842),
    (2, -4.0, 5.835527663601811),
    (2, -2.0, 2.333092302486293),
    (2, 0.0, -0.9317281369897417),
    (2, 2.0, 2.5707072241257767),
    (2, 4.0, 6.073142585241292),
    (2, 8.0, 13.078013307472336),
]


def main():

    path = Path(
        "exports"
    ) / (
        "gen2536_"
        "EV-202889_"
        "bundle.evir"
    )

    bundle = (
        EVIRBundleParser.parse(
            path
        )
    )

    runtime = EVIRRuntime(
        bundle
    )

    results = []

    for (
        context,
        input_value,
        expected,
    ) in REFERENCE_CASES:

        actual = runtime.run(
            input_value,
            context,
        )

        difference = abs(
            actual
            - expected
        )

        results.append(
            {
                "context":
                    context,

                "input":
                    input_value,

                "expected":
                    expected,

                "actual":
                    actual,

                "difference":
                    difference,

                "match":
                    difference
                    <= 1e-12,
            }
        )

    mismatches = [
        record

        for record in results

        if not record[
            "match"
        ]
    ]

    max_difference = max(
        (
            record["difference"]

            for record in results
        ),
        default=0.0,
    )

    print("=" * 78)
    print(
        "V1.1.0K — "
        "STANDALONE EVIR RUNTIME"
    )
    print("=" * 78)

    print(
        "FILE:",
        path,
    )

    print(
        "VERSION:",
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

    print()
    print("-" * 78)
    print("BUNDLE CONTENT")
    print("-" * 78)

    print(
        "LEGACY INSTRUCTIONS:",
        len(
            bundle.legacy_main
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
        "FUNCTIONS:",
        sorted(
            bundle.functions
        ),
    )

    print(
        "OPCODES:",
        sorted(
            bundle.opcodes
        ),
    )

    print()
    print("-" * 78)
    print("STANDALONE PARITY")
    print("-" * 78)

    print(
        "TOTAL CASES:",
        len(results),
    )

    print(
        "MATCHING CASES:",
        len(results)
        - len(mismatches),
    )

    print(
        "MISMATCHES:",
        len(mismatches),
    )

    print(
        "MAX DIFFERENCE:",
        max_difference,
    )

    for result in results:

        print(result)

    print()
    print("-" * 78)
    print("INDEPENDENCE")
    print("-" * 78)

    print(
        "EVOLUTION ENGINE IMPORTED:",
        False,
    )

    print(
        "STATE MANAGER IMPORTED:",
        False,
    )

    print(
        "GENOME REQUIRED:",
        False,
    )

    print(
        "SAVE FILE REQUIRED:",
        False,
    )

    print()
    print(
        "PASS:",
        (
            bundle.version == "0.2"

            and

            bundle.metadata.get(
                "generation"
            )
            == "2536"

            and

            bundle.metadata.get(
                "organism_id"
            )
            == "EV-202889"

            and

            sorted(
                bundle.macros
            )
            == [
                2,
                3,
                4,
                5,
            ]

            and

            sorted(
                bundle.modules
            )
            == [
                2,
                6,
                8,
            ]

            and

            sorted(
                bundle.opcodes
            )
            == [
                "O009",
            ]

            and

            len(results)
            == 21

            and

            not mismatches
        ),
    )


if __name__ == "__main__":

    main()
