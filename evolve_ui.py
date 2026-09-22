# evolve_ui.py

from __future__ import annotations

import tkinter as tk
import customtkinter as ctk

from evolution_engine import EvolutionEngine
from module_tracker import (
    ModuleTracker,
)
from state_manager import StateManager


# ============================================================
# APPEARANCE
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

BG = "#0B1020"
SURFACE = "#11182B"
SURFACE_2 = "#151E34"
SURFACE_3 = "#1A2540"

BORDER = "#263453"

TEXT = "#F4F7FF"
TEXT_SOFT = "#AAB6D3"
TEXT_MUTED = "#71809F"

BLUE = "#4D7CFE"
BLUE_HOVER = "#638DFF"

CYAN = "#22D3EE"
PURPLE = "#A855F7"
GREEN = "#22C55E"
ORANGE = "#F59E0B"
RED = "#EF4444"

FONT = "Segoe UI"
MONO = "Consolas"


class EvolveControlCenter(
    ctk.CTk
):

    def __init__(
        self,
    ) -> None:

        super().__init__()

        self.title(
            "PROJECT EVOLVE — Control Center"
        )

        self.geometry(
            "1500x900"
        )

        self.minsize(
            1180,
            720,
        )

        self.configure(
            fg_color=BG
        )

        # -----------------------------
        # ENGINE
        # -----------------------------

        self.engine = (
            EvolutionEngine()
        )

        self.running = False
        self.continuous = False

        self.generations_remaining = 0

        self.loaded_existing = (
            StateManager.load(
                self.engine
            )
        )

        if not self.loaded_existing:

            self.engine.create_generation_zero()

            self.engine.evaluate_population()

            StateManager.save(
                self.engine
            )

        # -----------------------------
        # ROOT GRID
        # -----------------------------

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self._build_header()
        self._build_content()
        self._build_controls()

        self.refresh()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close,
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def create_card(
        self,
        parent,
        *,
        corner_radius: int = 18,
    ) -> ctk.CTkFrame:

        return ctk.CTkFrame(
            parent,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            corner_radius=corner_radius,
        )

    def section_title(
        self,
        parent,
        text: str,
        color: str = TEXT,
    ) -> ctk.CTkLabel:

        return ctk.CTkLabel(
            parent,
            text=text,
            text_color=color,
            font=(
                FONT,
                15,
                "bold",
            ),
        )

    # ========================================================
    # HEADER
    # ========================================================

    def _build_header(
        self,
    ) -> None:

        header = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            height=110,
            corner_radius=0,
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        header.grid_propagate(
            False
        )

        header.grid_columnconfigure(
            1,
            weight=1,
        )

        # -----------------------------
        # LOGO
        # -----------------------------

        logo = ctk.CTkFrame(
            header,
            width=58,
            height=58,
            corner_radius=18,
            fg_color="#172A59",
        )

        logo.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(
                28,
                18,
            ),
            pady=24,
        )

        logo.grid_propagate(
            False
        )

        ctk.CTkLabel(
            logo,
            text="E",
            text_color=CYAN,
            font=(
                FONT,
                30,
                "bold",
            ),
        ).place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        # -----------------------------
        # TITLE
        # -----------------------------

        ctk.CTkLabel(
            header,
            text="PROJECT EVOLVE",
            text_color=TEXT,
            font=(
                FONT,
                28,
                "bold",
            ),
        ).grid(
            row=0,
            column=1,
            sticky="sw",
            pady=(
                21,
                0,
            ),
        )

        ctk.CTkLabel(
            header,
            text=(
                "Persistent Evolution Laboratory"
            ),
            text_color=TEXT_SOFT,
            font=(
                FONT,
                13,
            ),
        ).grid(
            row=1,
            column=1,
            sticky="nw",
            pady=(
                2,
                18,
            ),
        )

        # -----------------------------
        # ENVIRONMENT + GENERATION
        # -----------------------------

        environment_box = (
            ctk.CTkFrame(
                header,
                fg_color="#151E34",
                corner_radius=14,
                border_width=1,
                border_color=BORDER,
            )
        )

        environment_box.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(
                10,
                8,
            ),
            pady=22,
        )

        ctk.CTkLabel(
            environment_box,
            text="ENVIRONMENT",
            text_color=TEXT_MUTED,
            font=(
                FONT,
                10,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=16,
            pady=(
                10,
                1,
            ),
        )

        self.environment_label = (
            ctk.CTkLabel(
                environment_box,
                text="ERA 1",
                text_color=CYAN,
                font=(
                    FONT,
                    17,
                    "bold",
                ),
            )
        )

        self.environment_label.pack(
            anchor="w",
            padx=16,
        )

        self.environment_name_label = (
            ctk.CTkLabel(
                environment_box,
                text="ORIGINAL WORLD",
                text_color=TEXT_SOFT,
                font=(
                    FONT,
                    10,
                ),
            )
        )

        self.environment_name_label.pack(
            anchor="w",
            padx=16,
            pady=(
                0,
                10,
            ),
        )

        generation_box = (
            ctk.CTkFrame(
                header,
                fg_color="transparent",
            )
        )

        generation_box.grid(
            row=0,
            column=3,
            rowspan=2,
            padx=32,
        )

        ctk.CTkLabel(
            generation_box,
            text="GENERATION",
            text_color=TEXT_MUTED,
            font=(
                FONT,
                11,
                "bold",
            ),
        ).pack(
            anchor="e"
        )

        self.generation_label = (
            ctk.CTkLabel(
                generation_box,
                text="0",
                text_color=TEXT,
                font=(
                    FONT,
                    31,
                    "bold",
                ),
            )
        )

        self.generation_label.pack(
            anchor="e"
        )

        self.status_badge = (
            ctk.CTkLabel(
                generation_box,
                text="● LOADED",
                text_color=GREEN,
                fg_color="#102A20",
                corner_radius=10,
                padx=10,
                pady=4,
                font=(
                    FONT,
                    11,
                    "bold",
                ),
            )
        )

        self.status_badge.pack(
            anchor="e",
            pady=(
                5,
                0,
            ),
        )

    # ========================================================
    # MAIN CONTENT
    # ========================================================

    def _build_content(
        self,
    ) -> None:

        content = ctk.CTkFrame(
            self,
            fg_color=BG,
        )

        content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=22,
            pady=18,
        )

        content.grid_columnconfigure(
            0,
            weight=0,
            minsize=330,
        )

        content.grid_columnconfigure(
            1,
            weight=1,
        )

        content.grid_rowconfigure(
            0,
            weight=1,
        )

        self._build_metrics_panel(
            content
        )

        self._build_right_panel(
            content
        )

    # ========================================================
    # METRICS
    # ========================================================

    def _build_metrics_panel(
        self,
        parent,
    ) -> None:

        outer = self.create_card(
            parent
        )

        outer.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(
                0,
                14,
            ),
        )

        outer.grid_columnconfigure(
            0,
            weight=1,
        )

        outer.grid_rowconfigure(
            1,
            weight=1,
        )

        self.section_title(
            outer,
            "EVOLUTION STATE",
            BLUE,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(
                20,
                12,
            ),
        )

        # Scrollable içerik alanı
        card = ctk.CTkScrollableFrame(
            outer,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#263453",
            scrollbar_button_hover_color=BLUE,
        )

        card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(
                8,
                8,
            ),
            pady=(
                0,
                12,
            ),
        )

        card.grid_columnconfigure(
            0,
            weight=1,
        )

        self.metric_labels = {}

        metrics = [
            (
                "Best fitness",
                "BEST FITNESS",
                BLUE,
            ),
            (
                "All-time fitness",
                "ALL-TIME FITNESS",
                GREEN,
            ),
            (
                "Era best",
                "ERA BEST",
                BLUE,
            ),
            (
                "Recovery",
                "RECOVERY",
                GREEN,
            ),
            (
                "Recovery 75",
                "75% RECOVERY",
                GREEN,
            ),
            (
                "Recovery 90",
                "90% RECOVERY",
                GREEN,
            ),
            (
                "Recovery 100",
                "FULL RECOVERY",
                GREEN,
            ),
            (
                "Generations in era",
                "ERA AGE",
                CYAN,
            ),
            (
                "Average fitness",
                "AVERAGE FITNESS",
                CYAN,
            ),
            (
                "Best error",
                "BEST ERROR",
                ORANGE,
            ),
            (
                "Population",
                "POPULATION",
                PURPLE,
            ),
            (
                "Diversity",
                "DIVERSITY",
                GREEN,
            ),
            (
                "Avg code size",
                "AVG CODE SIZE",
                CYAN,
            ),
            (
                "Avg modules",
                "AVG MODULES",
                PURPLE,
            ),
            (
                "Families alive",
                "FAMILIES ALIVE",
                GREEN,
            ),
            (
                "Families extinct",
                "FAMILIES EXTINCT",
                RED,
            ),
            (
                "Major events",
                "MAJOR EVENTS",
                ORANGE,
            ),
            (
                "Novel structures",
                "NOVEL STRUCTURES",
                BLUE,
            ),
            (
                "Module variants",
                "MODULE VARIANTS",
                PURPLE,
            ),
            (
                "Nested calls",
                "AVG NESTED CALLS",
                PURPLE,
            ),
            (
                "Composite modules",
                "AVG COMPOSITES",
                CYAN,
            ),
            (
                "Defined composites",
                "DEFINED COMPOSITES",
                TEXT_SOFT,
            ),
            (
                "Module depth",
                "AVG MODULE DEPTH",
                GREEN,
            ),
            (
                "Composite organisms",
                "COMPOSITE ORGANISMS",
                BLUE,
            ),
            (
                "Avg macros",
                "AVG MACROS",
                PURPLE,
            ),
            (
                "Active macros",
                "AVG ACTIVE MACROS",
                CYAN,
            ),
            (
                "Macro calls",
                "AVG MACRO CALLS",
                GREEN,
            ),
            (
                "Macro organisms",
                "MACRO ORGANISMS",
                BLUE,
            ),
        ]

        for index, (
            metric_key,
            display_name,
            accent,
        ) in enumerate(
            metrics
        ):

            metric = ctk.CTkFrame(
                card,
                fg_color=SURFACE_2,
                corner_radius=12,
                border_width=1,
                border_color="#1D2944",
            )

            metric.grid(
                row=index,
                column=0,
                sticky="ew",
                padx=6,
                pady=4,
                ipady=7,
            )

            metric.grid_columnconfigure(
                1,
                weight=1,
            )

            accent_bar = ctk.CTkFrame(
                metric,
                width=4,
                height=32,
                fg_color=accent,
                corner_radius=4,
            )

            accent_bar.grid(
                row=0,
                column=0,
                padx=(
                    0,
                    12,
                ),
                pady=3,
            )

            ctk.CTkLabel(
                metric,
                text=display_name,
                text_color="#B8C4DF",
                font=(
                    FONT,
                    11,
                    "bold",
                ),
                anchor="w",
            ).grid(
                row=0,
                column=1,
                sticky="w",
            )

            value = ctk.CTkLabel(
                metric,
                text="—",
                text_color=accent,
                font=(
                    FONT,
                    15,
                    "bold",
                ),
                anchor="e",
            )

            value.grid(
                row=0,
                column=2,
                sticky="e",
                padx=(
                    14,
                    16,
                ),
            )

            self.metric_labels[
                metric_key
            ] = value

    # ========================================================
    # RIGHT SIDE
    # ========================================================

    def _build_right_panel(
        self,
        parent,
    ) -> None:

        right = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        right.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        right.grid_columnconfigure(
            0,
            weight=1,
        )

        right.grid_rowconfigure(
            0,
            weight=3,
        )

        right.grid_rowconfigure(
            1,
            weight=2,
        )

        self._build_best_organism(
            right
        )

        self._build_events(
            right
        )

    # ========================================================
    # BEST ORGANISM
    # ========================================================

    def _build_best_organism(
        self,
        parent,
    ) -> None:

        card = self.create_card(
            parent
        )

        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            pady=(
                0,
                14,
            ),
        )

        card.grid_columnconfigure(
            0,
            weight=1,
        )

        card.grid_rowconfigure(
            4,
            weight=1,
        )

        header = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=(
                18,
                6,
            ),
        )

        header.grid_columnconfigure(
            1,
            weight=1,
        )

        self.section_title(
            header,
            "CURRENT GENERATION BEST",
            BLUE,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        self.best_id_label = (
            ctk.CTkLabel(
                header,
                text="EV-000000",
                text_color=TEXT_MUTED,
                font=(
                    MONO,
                    12,
                ),
            )
        )

        self.best_id_label.grid(
            row=0,
            column=1,
            sticky="e",
        )

        # -----------------------------
        # TOP STATS
        # -----------------------------

        stats = ctk.CTkFrame(
            card,
            fg_color=SURFACE_2,
            corner_radius=14,
        )

        stats.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=18,
            pady=8,
        )

        for col in range(4):
            stats.grid_columnconfigure(
                col,
                weight=1,
            )

        self.best_stat_labels = {}

        best_stats = [
            (
                "FITNESS",
                BLUE,
            ),
            (
                "ERROR",
                ORANGE,
            ),
            (
                "MODULES",
                PURPLE,
            ),
            (
                "BORN",
                CYAN,
            ),
        ]

        for col, (
            name,
            color,
        ) in enumerate(
            best_stats
        ):

            frame = ctk.CTkFrame(
                stats,
                fg_color="transparent",
            )

            frame.grid(
                row=0,
                column=col,
                sticky="ew",
                padx=16,
                pady=13,
            )

            ctk.CTkLabel(
                frame,
                text=name,
                text_color=TEXT_MUTED,
                font=(
                    FONT,
                    10,
                    "bold",
                ),
            ).pack(
                anchor="w"
            )

            value = ctk.CTkLabel(
                frame,
                text="-",
                text_color=color,
                font=(
                    FONT,
                    19,
                    "bold",
                ),
            )

            value.pack(
                anchor="w",
                pady=(
                    2,
                    0,
                ),
            )

            self.best_stat_labels[
                name
            ] = value

        # -----------------------------
        # GENOME TITLE
        # -----------------------------

        self.transfer_frame = ctk.CTkFrame(
            card,
            fg_color="#0E172A",
            border_width=1,
            border_color=BORDER,
            corner_radius=12,
        )

        self.transfer_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=18,
            pady=(
                8,
                4,
            ),
        )

        self.transfer_frame.grid_columnconfigure(
            1,
            weight=1,
        )

        self.transfer_frame.grid_columnconfigure(
            2,
            weight=1,
        )

        ctk.CTkLabel(
            self.transfer_frame,
            text="CROSS-ERA TRANSFER",
            text_color=CYAN,
            font=(
                FONT,
                11,
                "bold",
            ),
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=14,
            pady=(
                10,
                7,
            ),
        )

        ctk.CTkLabel(
            self.transfer_frame,
            text="CHAMPION",
            text_color=TEXT_MUTED,
            font=(
                FONT,
                9,
                "bold",
            ),
        ).grid(
            row=1,
            column=0,
            padx=14,
            pady=4,
            sticky="w",
        )

        self.transfer_header_era1 = ctk.CTkLabel(
            self.transfer_frame,
            text="ERA 1",
            text_color=TEXT_MUTED,
            font=(
                FONT,
                9,
                "bold",
            ),
        )

        self.transfer_header_era1.grid(
            row=1,
            column=1,
            pady=4,
        )

        self.transfer_header_era2 = ctk.CTkLabel(
            self.transfer_frame,
            text="ERA 2",
            text_color=TEXT_MUTED,
            font=(
                FONT,
                9,
                "bold",
            ),
        )

        self.transfer_header_era2.grid(
            row=1,
            column=2,
            pady=4,
        )

        self.transfer_matrix_labels = {}

        for row, era_id in enumerate(
            (1, 2),
            start=2,
        ):

            ctk.CTkLabel(
                self.transfer_frame,
                text=f"ERA {era_id}",
                text_color=TEXT_SOFT,
                font=(
                    FONT,
                    10,
                    "bold",
                ),
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=14,
                pady=5,
            )

            for test_era in (
                1,
                2,
            ):

                value = ctk.CTkLabel(
                    self.transfer_frame,
                    text="—",
                    text_color=TEXT,
                    font=(
                        FONT,
                        12,
                        "bold",
                    ),
                )

                value.grid(
                    row=row,
                    column=test_era,
                    pady=5,
                )

                self.transfer_matrix_labels[
                    (
                        era_id,
                        test_era,
                    )
                ] = value

        ctk.CTkLabel(
            card,
            text="GENOME STRUCTURE",
            text_color=TEXT_SOFT,
            font=(
                FONT,
                11,
                "bold",
            ),
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(
                8,
                4,
            ),
        )

        # -----------------------------
        # GENOME TEXT
        # -----------------------------

        self.genome_text = (
            ctk.CTkTextbox(
                card,
                fg_color="#0C1324",
                border_width=1,
                border_color=BORDER,
                corner_radius=13,
                text_color="#DCE7FF",
                font=(
                    MONO,
                    12,
                ),
                wrap="word",
            )
        )

        self.genome_text.grid(
            row=4,
            column=0,
            sticky="nsew",
            padx=18,
            pady=(
                2,
                18,
            ),
        )

    # ========================================================
    # EVENTS
    # ========================================================

    def _build_events(
        self,
        parent,
    ) -> None:

        outer = self.create_card(
            parent
        )

        outer.grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        outer.grid_columnconfigure(
            0,
            weight=1,
        )

        outer.grid_rowconfigure(
            1,
            weight=1,
        )

        self.section_title(
            outer,
            "RECENT EVOLUTIONARY ACTIVITY",
            TEXT,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(
                18,
                10,
            ),
        )

        events = ctk.CTkFrame(
            outer,
            fg_color="transparent",
        )

        events.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=16,
            pady=(
                0,
                16,
            ),
        )

        events.grid_columnconfigure(
            0,
            weight=1,
        )

        events.grid_columnconfigure(
            1,
            weight=1,
        )

        events.grid_rowconfigure(
            0,
            weight=1,
        )

        # FAMILY EVENTS

        family_card = ctk.CTkFrame(
            events,
            fg_color="#101D35",
            corner_radius=14,
            border_width=1,
            border_color="#234577",
        )

        family_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(
                0,
                7,
            ),
        )

        family_card.grid_columnconfigure(
            0,
            weight=1,
        )

        family_card.grid_rowconfigure(
            1,
            weight=1,
        )

        ctk.CTkLabel(
            family_card,
            text="FAMILY EVENTS",
            text_color=CYAN,
            font=(
                FONT,
                12,
                "bold",
            ),
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=14,
            pady=(
                13,
                7,
            ),
        )

        self.family_events_text = (
            ctk.CTkTextbox(
                family_card,
                fg_color="transparent",
                text_color="#D4E9FF",
                font=(
                    MONO,
                    10,
                ),
                wrap="none",
            )
        )

        self.family_events_text.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(
                0,
                8,
            ),
        )

        # MAJOR EVENTS

        major_card = ctk.CTkFrame(
            events,
            fg_color="#10251F",
            corner_radius=14,
            border_width=1,
            border_color="#225B47",
        )

        major_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(
                7,
                0,
            ),
        )

        major_card.grid_columnconfigure(
            0,
            weight=1,
        )

        major_card.grid_rowconfigure(
            1,
            weight=1,
        )

        self.major_events_title = (
            ctk.CTkLabel(
                major_card,
                text=(
                    "MAJOR EVOLUTIONARY EVENTS"
                ),
                text_color=GREEN,
                font=(
                    FONT,
                    12,
                    "bold",
                ),
            )
        )

        self.major_events_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=14,
            pady=(
                13,
                7,
            ),
        )

        self.major_events_text = (
            ctk.CTkTextbox(
                major_card,
                fg_color="transparent",
                text_color="#DDFBEB",
                font=(
                    MONO,
                    10,
                ),
                wrap="none",
            )
        )

        self.major_events_text.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(
                0,
                8,
            ),
        )

    # ========================================================
    # CONTROLS
    # ========================================================

    def _build_controls(
        self,
    ) -> None:

        bar = ctk.CTkFrame(
            self,
            fg_color=SURFACE,
            height=84,
            corner_radius=0,
        )

        bar.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        bar.grid_propagate(
            False
        )

        bar.grid_columnconfigure(
            8,
            weight=1,
        )

        buttons = [
            (
                "▶  Run 1",
                lambda:
                    self.start_generations(
                        1
                    ),
                BLUE,
            ),
            (
                "▶▶  Run 10",
                lambda:
                    self.start_generations(
                        10
                    ),
                BLUE,
            ),
            (
                "▶▶  Run 100",
                lambda:
                    self.start_generations(
                        100
                    ),
                BLUE,
            ),
            (
                "⏩  Run 500",
                lambda:
                    self.start_generations(
                        500
                    ),
                PURPLE,
            ),
        ]

        for column, (
            text,
            command,
            color,
        ) in enumerate(
            buttons
        ):

            ctk.CTkButton(
                bar,
                text=text,
                command=command,
                width=125,
                height=42,
                corner_radius=12,
                fg_color=color,
                hover_color=BLUE_HOVER,
                font=(
                    FONT,
                    12,
                    "bold",
                ),
            ).grid(
                row=0,
                column=column,
                padx=(
                    8
                    if column
                    else 22,
                    4,
                ),
                pady=20,
            )

        ctk.CTkButton(
            bar,
            text="⟳  Continuous",
            command=(
                self.start_continuous
            ),
            width=145,
            height=42,
            corner_radius=12,
            fg_color="#0E9F6E",
            hover_color="#13B981",
            font=(
                FONT,
                12,
                "bold",
            ),
        ).grid(
            row=0,
            column=4,
            padx=8,
        )

        ctk.CTkButton(
            bar,
            text="Ⅱ  Pause",
            command=self.pause,
            width=110,
            height=42,
            corner_radius=12,
            fg_color=ORANGE,
            hover_color="#F7B32B",
            text_color="#161616",
            font=(
                FONT,
                12,
                "bold",
            ),
        ).grid(
            row=0,
            column=5,
            padx=4,
        )

        ctk.CTkButton(
            bar,
            text="▣  Save",
            command=self.manual_save,
            width=105,
            height=42,
            corner_radius=12,
            fg_color=PURPLE,
            hover_color="#B66BFB",
            font=(
                FONT,
                12,
                "bold",
            ),
        ).grid(
            row=0,
            column=6,
            padx=4,
        )

        self.bottom_status = (
            ctk.CTkLabel(
                bar,
                text="READY",
                text_color=BLUE,
                fg_color="#122249",
                corner_radius=12,
                padx=16,
                pady=9,
                font=(
                    FONT,
                    11,
                    "bold",
                ),
            )
        )

        self.bottom_status.grid(
            row=0,
            column=9,
            sticky="e",
            padx=22,
        )

    # ========================================================
    # EVOLUTION
    # ========================================================

    def start_generations(
        self,
        count: int,
    ) -> None:

        if self.running:
            return

        self.generations_remaining = (
            count
        )

        self.continuous = False
        self.running = True

        self._set_running_status(
            f"RUNNING +{count}"
        )

        self.after(
            1,
            self._evolution_tick,
        )

    def start_continuous(
        self,
    ) -> None:

        if self.running:
            return

        self.continuous = True
        self.running = True

        self._set_running_status(
            "CONTINUOUS"
        )

        self.after(
            1,
            self._evolution_tick,
        )

    def pause(
        self,
    ) -> None:

        self.running = False
        self.continuous = False
        self.generations_remaining = 0

        StateManager.save(
            self.engine
        )

        self.status_badge.configure(
            text="● PAUSED",
            text_color=ORANGE,
            fg_color="#33260B",
        )

        self.bottom_status.configure(
            text=(
                f"SAVED — GEN "
                f"{self.engine.generation}"
            ),
            text_color=ORANGE,
            fg_color="#33260B",
        )

        self.refresh()

    def _set_running_status(
        self,
        text: str,
    ) -> None:

        self.status_badge.configure(
            text=f"● {text}",
            text_color=GREEN,
            fg_color="#102A20",
        )

        self.bottom_status.configure(
            text=text,
            text_color=GREEN,
            fg_color="#102A20",
        )

    def _evolution_tick(
        self,
    ) -> None:

        if not self.running:
            return

        self.engine.create_next_generation()

        self.engine.evaluate_population()

        generation = (
            self.engine.generation
        )

        if (
            generation > 0
            and generation % 50 == 0
        ):

            StateManager.save(
                self.engine
            )

            self.bottom_status.configure(
                text=(
                    f"AUTOSAVED — GEN "
                    f"{generation}"
                )
            )

        if (
            generation % 5 == 0
            or not self.continuous
        ):
            self.refresh()

        if self.continuous:

            self.after(
                1,
                self._evolution_tick,
            )

            return

        self.generations_remaining -= 1

        if (
            self.generations_remaining
            <= 0
        ):

            self.running = False

            StateManager.save(
                self.engine
            )

            self.status_badge.configure(
                text="● READY",
                text_color=BLUE,
                fg_color="#122249",
            )

            self.bottom_status.configure(
                text=(
                    f"COMPLETE — GEN "
                    f"{generation}"
                ),
                text_color=BLUE,
                fg_color="#122249",
            )

            self.refresh()

            return

        self.after(
            1,
            self._evolution_tick,
        )

    # ========================================================
    # SAVE
    # ========================================================

    def manual_save(
        self,
    ) -> None:

        StateManager.save(
            self.engine
        )

        self.bottom_status.configure(
            text=(
                f"SAVED — GEN "
                f"{self.engine.generation}"
            ),
            text_color=PURPLE,
            fg_color="#29163E",
        )

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(
        self,
    ) -> None:

        if not self.engine.population:
            return

        best = (
            self.engine.population[0]
        )

        diversity = (
            self.engine
            .diversity_report()
        )

        family_report = (
            self.engine
            .module_family_report()
        )

        novelty = (
            self.engine
            .novelty_report()
        )

        lineage_report = (
            self.engine
            .module_lineage_report()
        )

        major = (
            self.engine
            .major_event_report()
        )

        self.major_events_title.configure(
            text=(
                f"ERA {major['era_id']} "
                f"MAJOR EVOLUTIONARY EVENTS"
            )
        )

        environment = (
            self.engine
            .environment_report()
        )

        adaptation = (
            self.engine
            .adaptation_report()
        )

        module_ecology = (
            ModuleTracker
            .analyze_population(
                self.engine.population
            )
        )

        transfer_matrix = (
            self.engine
            .era_transfer_matrix()
        )

        # -----------------------------
        # HEADER
        # -----------------------------

        self.generation_label.configure(
            text=str(
                self.engine.generation
            )
        )

        self.environment_label.configure(
            text=(
                f"ERA "
                f"{environment['era_id']}"
            )
        )

        self.environment_name_label.configure(
            text=environment[
                "name"
            ]
        )

        # -----------------------------
        # METRICS
        # -----------------------------

        values = {
            "Best fitness":
                f"{best.fitness:.4f}",

            "All-time fitness":
                (
                    f"{self.engine.best_ever.fitness:.4f}"
                    if self.engine.best_ever
                    is not None
                    else "—"
                ),

            "Era best":
                (
                    f"{adaptation['era_best_fitness']:.4f}"
                    if adaptation.get(
                        "active"
                    )
                    else "—"
                ),

            "Recovery":
                (
                    f"{adaptation['recovery_percent']:.1f}%"
                    if adaptation.get(
                        "active"
                    )
                    else "—"
                ),

            "Recovery 75":
                (
                    str(
                        adaptation[
                            "milestone_ages"
                        ][75]
                    )
                    + " gen"
                    if (
                        adaptation.get(
                            "active"
                        )
                        and adaptation[
                            "milestone_ages"
                        ][75]
                        is not None
                    )
                    else "PENDING"
                ),

            "Recovery 90":
                (
                    str(
                        adaptation[
                            "milestone_ages"
                        ][90]
                    )
                    + " gen"
                    if (
                        adaptation.get(
                            "active"
                        )
                        and adaptation[
                            "milestone_ages"
                        ][90]
                        is not None
                    )
                    else "PENDING"
                ),

            "Recovery 100":
                (
                    str(
                        adaptation[
                            "milestone_ages"
                        ][100]
                    )
                    + " gen"
                    if (
                        adaptation.get(
                            "active"
                        )
                        and adaptation[
                            "milestone_ages"
                        ][100]
                        is not None
                    )
                    else "PENDING"
                ),

            "Generations in era":
                (
                    str(
                        adaptation[
                            "generations_in_era"
                        ]
                    )
                    if adaptation.get(
                        "active"
                    )
                    else "—"
                ),

            "Average fitness":
                (
                    f"{self.engine.average_fitness():.4f}"
                ),

            "Best error":
                f"{best.error:.6f}",

            "Population":
                str(
                    len(
                        self.engine.population
                    )
                ),

            "Diversity":
                (
                    f"{diversity['diversity_ratio'] * 100:.2f}%"
                ),

            "Avg code size":
                (
                    f"{diversity['average_genome_length']:.2f}"
                ),

            "Avg modules":
                (
                    f"{diversity['average_module_count']:.2f}"
                ),

            "Families alive":
                str(
                    family_report.get(
                        "families_alive",
                        0,
                    )
                ),

            "Families extinct":
                str(
                    family_report.get(
                        "families_extinct",
                        0,
                    )
                ),

            "Major events":
                str(
                    major[
                        "total_events"
                    ]
                ),

            "Novel structures":
                str(
                    novelty[
                        "total_structures"
                    ]
                ),

            "Module variants":
                str(
                    lineage_report[
                        "archived_module_variants"
                    ]
                ),

            "Nested calls":
                (
                    f"{module_ecology['average_nested_calls']:.2f}"
                ),

            "Composite modules":
                (
                    f"{module_ecology['average_composite_modules']:.2f}"
                ),

            "Defined composites":
                (
                    f"{module_ecology['average_defined_composite_modules']:.2f}"
                ),

            "Module depth":
                (
                    f"{module_ecology['average_module_depth']:.2f}"
                ),

            "Composite organisms":
                str(
                    module_ecology[
                        "organisms_with_composites"
                    ]
                ),

            "Avg macros":
                (
                    f"{module_ecology['average_macros']:.2f}"
                ),

            "Active macros":
                (
                    f"{module_ecology['average_active_macros']:.2f}"
                ),

            "Macro calls":
                (
                    f"{module_ecology['average_macro_calls']:.2f}"
                ),

            "Macro organisms":
                str(
                    module_ecology[
                        "organisms_with_macros"
                    ]
                ),
        }

        for name, value in (
            values.items()
        ):

            self.metric_labels[
                name
            ].configure(
                text=value
            )

        # -----------------------------
        # BEST ORGANISM
        # -----------------------------

        self.best_id_label.configure(
            text=best.id
        )

        self.best_stat_labels[
            "FITNESS"
        ].configure(
            text=f"{best.fitness:.4f}"
        )

        self.best_stat_labels[
            "ERROR"
        ].configure(
            text=f"{best.error:.5f}"
        )

        self.best_stat_labels[
            "MODULES"
        ].configure(
            text=str(
                best.genome.module_count()
            )
        )

        self.best_stat_labels[
            "BORN"
        ].configure(
            text=str(
                best.generation
            )
        )

        for label in (
            self.transfer_matrix_labels.values()
        ):

            label.configure(
                text="—",
                text_color=TEXT_MUTED,
            )

        for row in transfer_matrix:

            champion_era = (
                row[
                    "champion_era"
                ]
            )

            for result in (
                row["results"]
            ):

                test_era = (
                    result["era_id"]
                )

                key = (
                    champion_era,
                    test_era,
                )

                label = (
                    self
                    .transfer_matrix_labels
                    .get(
                        key
                    )
                )

                if label is None:
                    continue

                if not result["valid"]:

                    label.configure(
                        text="INVALID",
                        text_color=RED,
                    )

                    continue

                fitness = (
                    result["fitness"]
                )

                # Kendi environment'ındaki
                # performansı yeşil göster.
                if (
                    champion_era
                    == test_era
                ):
                    color = GREEN

                else:
                    color = ORANGE

                label.configure(
                    text=(
                        f"{fitness:.2f}"
                    ),
                    text_color=color,
                )

        self.genome_text.configure(
            state="normal"
        )

        self.genome_text.delete(
            "1.0",
            "end",
        )

        genome_display = (
            best
            .genome
            .describe()
            .replace(
                "] MODULES[",
                "]\n\nMODULES[\n",
            )
            .replace(
                " ; ",
                "\n\n",
            )
        )

        self.genome_text.insert(
            "1.0",
            genome_display,
        )

        self.genome_text.configure(
            state="disabled"
        )

        # -----------------------------
        # FAMILY EVENTS
        # -----------------------------

        family_events = (
            self.engine
            .family_event_report()
        )

        self.family_events_text.configure(
            state="normal"
        )

        self.family_events_text.delete(
            "1.0",
            "end",
        )

        events = (
            family_events.get(
                "recent_events",
                [],
            )[-10:]
        )

        if not events:

            self.family_events_text.insert(
                "1.0",
                "No family events yet."
            )

        else:

            lines = []

            for event in events:

                lines.append(
                    (
                        f"GEN "
                        f"{event['generation']:<5} "
                        f"{event['event_type']:<18} "
                        f"{event['family']} "
                        f"{event['percentage']:>5.1f}%"
                    )
                )

            self.family_events_text.insert(
                "1.0",
                "\n".join(
                    lines
                ),
            )

        self.family_events_text.configure(
            state="disabled"
        )

        # -----------------------------
        # MAJOR EVENTS
        # -----------------------------

        self.major_events_text.configure(
            state="normal"
        )

        self.major_events_text.delete(
            "1.0",
            "end",
        )

        major_events = (
            major[
                "recent_events"
            ][-10:]
        )

        if not major_events:

            self.major_events_text.insert(
                "1.0",
                (
                    f"No major ERA "
                    f"{major['era_id']} "
                    f"events recorded yet.\n\n"
                    f"Current ERA record: "
                    f"{major['era_best_reference']:.4f}"
                ),
            )

        else:

            lines = []

            for event in major_events:

                lines.append(
                    (
                        f"GEN "
                        f"{event['generation']:<5} "
                        f"{event['organism_id']}   "
                        f"FIT "
                        f"{event['fitness']:>7.3f}   "
                        f"Δ +"
                        f"{event['fitness_gain']:.3f}"
                    )
                )

            self.major_events_text.insert(
                "1.0",
                "\n".join(
                    lines
                ),
            )

        self.major_events_text.configure(
            state="disabled"
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def on_close(
        self,
    ) -> None:

        self.running = False

        StateManager.save(
            self.engine
        )

        self.destroy()


def main() -> None:

    app = (
        EvolveControlCenter()
    )

    app.mainloop()


if __name__ == "__main__":
    main()