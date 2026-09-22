from __future__ import annotations

from dataclasses import dataclass, field

from ast_program import ASTProgram


MAX_SEMANTIC_HISTORY = 32
MAX_EXTINCT_OPCODE_ARCHIVE = 128


@dataclass
class EvolvedOpcode:
    opcode_id: str
    program: ASTProgram

    created_generation: int = 0
    origin: str = "UNKNOWN"

    parent_opcode_id: str | None = None
    lineage_root_id: str | None = None

    revision: int = 0
    last_mutated_generation: int | None = None

    semantic_history: list[dict] = field(
        default_factory=list
    )

    def ensure_lineage_metadata(
        self,
    ) -> None:

        if self.lineage_root_id is None:

            self.lineage_root_id = (
                self.parent_opcode_id
                or self.opcode_id
            )

        if not self.semantic_history:

            self.semantic_history.append(
                {
                    "revision": self.revision,
                    "generation": (
                        self.created_generation
                    ),
                    "event": "CREATED",
                    "description": (
                        self.program.describe()
                    ),
                    "program": (
                        self.program.to_dict()
                    ),
                }
            )

    def record_semantic_revision(
        self,
        generation: int,
        event: str,
        description: str,
        previous_program: dict,
    ) -> None:

        self.ensure_lineage_metadata()

        self.revision += 1

        self.last_mutated_generation = (
            generation
        )

        previous_description = (
            ASTProgram.from_dict(
                previous_program
            )
            .describe()
        )

        self.semantic_history.append(
            {
                "revision": self.revision,
                "generation": generation,
                "event": event,
                "description": description,
                "previous_description": (
                    previous_description
                ),
                "program_description": (
                    self.program.describe()
                ),
            }
        )

        if (
            len(self.semantic_history)
            > MAX_SEMANTIC_HISTORY
        ):

            first_entry = (
                self.semantic_history[0]
            )

            recent_entries = (
                self.semantic_history[
                    -(
                        MAX_SEMANTIC_HISTORY
                        - 1
                    ):
                ]
            )

            self.semantic_history = [
                first_entry,
                *recent_entries,
            ]

    def clone(
        self,
    ) -> "EvolvedOpcode":

        return EvolvedOpcode.from_dict(
            self.to_dict()
        )

    def to_dict(
        self,
    ) -> dict:

        return {
            "opcode_id": self.opcode_id,
            "program": self.program.to_dict(),
            "created_generation": (
                self.created_generation
            ),
            "origin": self.origin,
            "parent_opcode_id": (
                self.parent_opcode_id
            ),
            "lineage_root_id": (
                self.lineage_root_id
            ),
            "revision": self.revision,
            "last_mutated_generation": (
                self.last_mutated_generation
            ),
            "semantic_history": [
                dict(entry)

                for entry
                in self.semantic_history
            ],
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "EvolvedOpcode":

        opcode = cls(
            opcode_id=data["opcode_id"],
            program=ASTProgram.from_dict(
                data["program"]
            ),
            created_generation=data.get(
                "created_generation",
                0,
            ),
            origin=data.get(
                "origin",
                "UNKNOWN",
            ),
            parent_opcode_id=data.get(
                "parent_opcode_id"
            ),
            lineage_root_id=data.get(
                "lineage_root_id"
            ),
            revision=data.get(
                "revision",
                0,
            ),
            last_mutated_generation=(
                data.get(
                    "last_mutated_generation"
                )
            ),
            semantic_history=[
                dict(entry)

                for entry
                in data.get(
                    "semantic_history",
                    []
                )
            ],
        )

        opcode.ensure_lineage_metadata()

        if (
            len(opcode.semantic_history)
            > MAX_SEMANTIC_HISTORY
        ):

            opcode.semantic_history = [
                opcode.semantic_history[0],
                *opcode.semantic_history[
                    -(
                        MAX_SEMANTIC_HISTORY
                        - 1
                    ):
                ],
            ]

        return opcode

    def describe(
        self,
    ) -> str:

        return (
            f"{self.opcode_id}: "
            f"{self.program.describe()} "
            f"[root={self.lineage_root_id}, "
            f"revision={self.revision}]"
        )


@dataclass
class EvolvedLanguage:
    opcodes: dict[
        str,
        EvolvedOpcode,
    ] = field(
        default_factory=dict
    )

    extinct_opcodes: list[dict] = field(
        default_factory=list
    )

    next_opcode_id: int = 1

    birth_generation: int = 0
    origin: str = "UNKNOWN"

    def allocate_opcode_id(
        self,
    ) -> str:

        opcode_id = (
            f"O{self.next_opcode_id:03d}"
        )

        self.next_opcode_id += 1

        return opcode_id

    def add_opcode(
        self,
        program: ASTProgram,
        generation: int = 0,
        origin: str = "EVOLVED",
        parent_opcode_id: str | None = None,
        lineage_root_id: str | None = None,
    ) -> str:

        opcode_id = (
            self.allocate_opcode_id()
        )

        opcode = EvolvedOpcode(
            opcode_id=opcode_id,
            program=program,
            created_generation=generation,
            origin=origin,
            parent_opcode_id=(
                parent_opcode_id
            ),
            lineage_root_id=(
                lineage_root_id
                or parent_opcode_id
                or opcode_id
            ),
            revision=0,
            last_mutated_generation=None,
        )

        opcode.ensure_lineage_metadata()

        self.opcodes[
            opcode_id
        ] = opcode

        return opcode_id

    def remove_opcode(
        self,
        opcode_id: str,
    ) -> None:

        self.opcodes.pop(
            opcode_id,
            None,
        )

    def archive_and_remove_opcode(
        self,
        opcode_id: str,
        generation: int,
        reason: str,
    ) -> dict | None:

        opcode = self.opcodes.get(
            opcode_id
        )

        if opcode is None:
            return None

        archive_entry = {
            "opcode_id": opcode_id,
            "lineage_root_id": (
                opcode.lineage_root_id
            ),
            "parent_opcode_id": (
                opcode.parent_opcode_id
            ),
            "created_generation": (
                opcode.created_generation
            ),
            "deleted_generation": (
                generation
            ),
            "origin": opcode.origin,
            "revision": opcode.revision,
            "last_mutated_generation": (
                opcode.last_mutated_generation
            ),
            "reason": reason,
            "final_program": (
                opcode.program.to_dict()
            ),
            "final_description": (
                opcode.program.describe()
            ),
            "semantic_history": [
                dict(entry)

                for entry
                in opcode.semantic_history
            ],
        }

        self.extinct_opcodes.append(
            archive_entry
        )

        if (
            len(self.extinct_opcodes)
            > MAX_EXTINCT_OPCODE_ARCHIVE
        ):

            self.extinct_opcodes = (
                self.extinct_opcodes[
                    -MAX_EXTINCT_OPCODE_ARCHIVE:
                ]
            )

        self.remove_opcode(
            opcode_id
        )

        return archive_entry

    def get_opcode(
        self,
        opcode_id: str,
    ) -> EvolvedOpcode | None:

        return self.opcodes.get(
            opcode_id
        )

    def opcode_count(
        self,
    ) -> int:

        return len(
            self.opcodes
        )

    def total_node_count(
        self,
    ) -> int:

        return sum(
            opcode.program.node_count()

            for opcode
            in self.opcodes.values()
        )

    def maximum_depth(
        self,
    ) -> int:

        if not self.opcodes:
            return 0

        return max(
            opcode.program.depth()

            for opcode
            in self.opcodes.values()
        )

    def clone(
        self,
    ) -> "EvolvedLanguage":

        return (
            EvolvedLanguage.from_dict(
                self.to_dict()
            )
        )

    def to_dict(
        self,
    ) -> dict:

        return {
            "opcodes": {
                opcode_id:
                    opcode.to_dict()

                for (
                    opcode_id,
                    opcode,
                )
                in self.opcodes.items()
            },
            "extinct_opcodes": [
                dict(entry)

                for entry
                in self.extinct_opcodes
            ],
            "next_opcode_id": (
                self.next_opcode_id
            ),
            "birth_generation": (
                self.birth_generation
            ),
            "origin": self.origin,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "EvolvedLanguage":

        language = cls(
            extinct_opcodes=[
                dict(entry)

                for entry
                in data.get(
                    "extinct_opcodes",
                    []
                )[
                    -MAX_EXTINCT_OPCODE_ARCHIVE:
                ]
            ],
            next_opcode_id=data.get(
                "next_opcode_id",
                1,
            ),
            birth_generation=data.get(
                "birth_generation",
                0,
            ),
            origin=data.get(
                "origin",
                "UNKNOWN",
            ),
        )

        language.opcodes = {
            opcode_id:
                EvolvedOpcode.from_dict(
                    opcode_data
                )

            for (
                opcode_id,
                opcode_data,
            )
            in data.get(
                "opcodes",
                {}
            ).items()
        }

        return language

    def describe(
        self,
    ) -> str:

        if not self.opcodes:

            return (
                "EVOLVED LANGUAGE: EMPTY"
            )

        lines = [
            "EVOLVED LANGUAGE:"
        ]

        for opcode_id in sorted(
            self.opcodes
        ):

            lines.append(
                self.opcodes[
                    opcode_id
                ].describe()
            )

        return "\n".join(
            lines
        )