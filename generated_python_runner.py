from __future__ import annotations

import hashlib
import importlib.util

from pathlib import Path
from types import ModuleType

from generated_runtime import (
    GeneratedRuntime,
)

from python_emitter import (
    PythonEmitter,
)


class GeneratedPythonRunner:

    def __init__(
        self,
        output_directory: str = "generated",
    ) -> None:

        self.emitter = PythonEmitter(
            output_directory=output_directory
        )

        self.loaded_modules: dict[
            str,
            ModuleType,
        ] = {}

    # =====================================================
    # SOURCE
    # =====================================================

    def source_for(
        self,
        organism,
    ) -> str:

        program = (
            organism.genome.ast_program
        )

        if program is None:

            raise ValueError(
                "Organism has no AST program."
            )

        return self.emitter.render_program(
            program
        )

    # =====================================================
    # SOURCE FINGERPRINT
    # =====================================================

    def source_fingerprint_for(
        self,
        organism,
    ) -> str:

        source = self.source_for(
            organism
        )

        digest = hashlib.sha256(
            source.encode(
                "utf-8"
            )
        ).hexdigest()

        # 16 hex karakter şimdilik yeterli.
        return digest[:16]

    # =====================================================
    # MODULE NAME
    # =====================================================

    def module_name_for(
        self,
        organism,
    ) -> str:

        fingerprint = (
            self.source_fingerprint_for(
                organism
            )
        )

        return (
            f"evo_module_"
            f"{fingerprint}"
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def export(
        self,
        organism,
    ) -> Path:

        program = (
            organism.genome.ast_program
        )

        if program is None:

            raise ValueError(
                "Organism has no AST program."
            )

        module_name = (
            self.module_name_for(
                organism
            )
        )

        return self.emitter.emit_program(
            program,
            module_name,
        )

    # =====================================================
    # LOAD
    # =====================================================

    def load(
        self,
        organism,
        force_reload: bool = False,
    ) -> ModuleType:

        module_name = (
            self.module_name_for(
                organism
            )
        )

        if (
            not force_reload
            and module_name
            in self.loaded_modules
        ):

            return self.loaded_modules[
                module_name
            ]

        path = self.export(
            organism
        )

        spec = (
            importlib.util
            .spec_from_file_location(
                module_name,
                path,
            )
        )

        if (
            spec is None
            or spec.loader is None
        ):

            raise RuntimeError(
                "Could not load generated "
                f"Python module: {path}"
            )

        module = (
            importlib.util
            .module_from_spec(
                spec
            )
        )

        spec.loader.exec_module(
            module
        )

        if not hasattr(
            module,
            "evolved_program",
        ):

            raise RuntimeError(
                "Generated module does not "
                "contain evolved_program()."
            )

        self.loaded_modules[
            module_name
        ] = module

        return module

    # =====================================================
    # EXECUTE
    # =====================================================

    def run(
        self,
        organism,
        input_value: float,
        context_id: int,
    ) -> float:

        module = self.load(
            organism
        )

        runtime = GeneratedRuntime(
            organism.genome
        )

        result = module.evolved_program(
            input_value,
            context_id,
            runtime,
        )

        return float(
            result
        )

    # =====================================================
    # ARCHITECTURE SOURCE
    # =====================================================

    def architecture_source_for(
        self,
        organism,
    ) -> str:

        architecture = (
            organism.genome
            .program_architecture
        )

        if architecture is None:

            raise ValueError(
                "Organism has no program architecture."
            )

        return (
            self.emitter
            .render_architecture(
                architecture,
                organism.genome
                .evolved_language,
            )
        )

    def architecture_source_fingerprint_for(
        self,
        organism,
    ) -> str:

        source = (
            self.architecture_source_for(
                organism
            )
        )

        digest = hashlib.sha256(
            source.encode(
                "utf-8"
            )
        ).hexdigest()

        return digest[:16]

    def architecture_module_name_for(
        self,
        organism,
    ) -> str:

        fingerprint = (
            self
            .architecture_source_fingerprint_for(
                organism
            )
        )

        return (
            f"evo_arch_"
            f"{fingerprint}"
        )

    # =====================================================
    # ARCHITECTURE EXPORT
    # =====================================================

    def export_architecture(
        self,
        organism,
    ) -> Path:

        architecture = (
            organism.genome
            .program_architecture
        )

        if architecture is None:

            raise ValueError(
                "Organism has no program architecture."
            )

        module_name = (
            self
            .architecture_module_name_for(
                organism
            )
        )

        return (
            self.emitter.emit_architecture(
                architecture,
                module_name,
                organism.genome
                .evolved_language,
            )
        )

    # =====================================================
    # ARCHITECTURE LOAD
    # =====================================================

    def load_architecture(
        self,
        organism,
        force_reload: bool = False,
    ) -> ModuleType:

        module_name = (
            self
            .architecture_module_name_for(
                organism
            )
        )

        if (
            not force_reload
            and module_name
            in self.loaded_modules
        ):

            return self.loaded_modules[
                module_name
            ]

        path = (
            self.export_architecture(
                organism
            )
        )

        spec = (
            importlib.util
            .spec_from_file_location(
                module_name,
                path,
            )
        )

        if (
            spec is None
            or spec.loader is None
        ):

            raise RuntimeError(
                "Could not load generated "
                f"architecture module: {path}"
            )

        module = (
            importlib.util
            .module_from_spec(
                spec
            )
        )

        spec.loader.exec_module(
            module
        )

        if not hasattr(
            module,
            "evolved_program",
        ):

            raise RuntimeError(
                "Generated architecture module "
                "does not contain "
                "evolved_program()."
            )

        self.loaded_modules[
            module_name
        ] = module

        return module

    # =====================================================
    # ARCHITECTURE EXECUTE
    # =====================================================

    def run_architecture(
        self,
        organism,
        input_value: float,
        context_id: int,
    ) -> float:

        module = (
            self.load_architecture(
                organism
            )
        )

        runtime = GeneratedRuntime(
            organism.genome,
            architecture_mode=True,
        )

        result = (
            module.evolved_program(
                input_value,
                context_id,
                runtime,
            )
        )

        return float(result)
