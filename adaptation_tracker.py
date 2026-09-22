# adaptation_tracker.py

from __future__ import annotations


RECOVERY_THRESHOLDS = (
    50,
    75,
    90,
    100,
)


class AdaptationTracker:

    def __init__(self) -> None:

        self.current_era_id: int | None = None
        self.era_name = ""

        self.era_start_generation = 0

        self.pre_shift_reference = 0.0
        self.start_fitness = 0.0

        self.best_fitness = 0.0
        self.lowest_fitness = float("inf")

        self.recovery_generation: int | None = None

        self.milestones: dict[
            int,
            int | None,
        ] = {
            threshold: None
            for threshold
            in RECOVERY_THRESHOLDS
        }

        self.history: list[dict] = []

    # ========================================================
    # UPDATE
    # ========================================================

    def update(
        self,
        *,
        era_id: int,
        era_name: str,
        generation: int,
        current_best_fitness: float,
        previous_reference: float,
    ) -> None:

        if (
            self.current_era_id is None
            or era_id != self.current_era_id
        ):

            if self.current_era_id is not None:

                self._archive_current_era(
                    end_generation=(
                        generation - 1
                    )
                )

            self._start_new_era(
                era_id=era_id,
                era_name=era_name,
                generation=generation,
                current_best_fitness=(
                    current_best_fitness
                ),
                previous_reference=(
                    previous_reference
                ),
            )

            return

        self.best_fitness = max(
            self.best_fitness,
            current_best_fitness,
        )

        self.lowest_fitness = min(
            self.lowest_fitness,
            current_best_fitness,
        )

        self._update_milestones(
            generation
        )

    # ========================================================
    # NEW ERA
    # ========================================================

    def _start_new_era(
        self,
        *,
        era_id: int,
        era_name: str,
        generation: int,
        current_best_fitness: float,
        previous_reference: float,
    ) -> None:

        self.current_era_id = era_id
        self.era_name = era_name

        if era_id == 1:

            self.era_start_generation = 0

        else:

            self.era_start_generation = (
                1001
                + (
                    era_id - 2
                ) * 500
            )

        self.pre_shift_reference = (
            previous_reference
        )

        # ERA 2'ye adaptation tracker sonradan
        # eklendiği için gerçek Gen 1001
        # ölçümünü koruyoruz.
        if (
            era_id == 2
            and generation > 1001
            and not self.history
        ):

            self.start_fitness = 34.4110

            self.lowest_fitness = min(
                34.4110,
                current_best_fitness,
            )

        else:

            self.start_fitness = (
                current_best_fitness
            )

            self.lowest_fitness = (
                current_best_fitness
            )

        self.best_fitness = max(
            self.start_fitness,
            current_best_fitness,
        )

        self.recovery_generation = None

        self.milestones = {
            threshold: None
            for threshold
            in RECOVERY_THRESHOLDS
        }

        self._update_milestones(
            generation
        )

    # ========================================================
    # RECOVERY
    # ========================================================

    def _current_recovery_percent(
        self,
    ) -> float:

        if (
            self.pre_shift_reference
            <= 0
        ):
            return 100.0

        return (
            self.best_fitness
            / self.pre_shift_reference
            * 100.0
        )

    def _update_milestones(
        self,
        generation: int,
    ) -> None:

        recovery_percent = (
            self._current_recovery_percent()
        )

        for threshold in (
            RECOVERY_THRESHOLDS
        ):

            if (
                self.milestones[
                    threshold
                ]
                is None
                and recovery_percent
                >= threshold
            ):

                self.milestones[
                    threshold
                ] = generation

        if (
            self.milestones[100]
            is not None
            and self.recovery_generation
            is None
        ):

            self.recovery_generation = (
                self.milestones[100]
            )

    # ========================================================
    # REFERENCE REBASE
    # ========================================================

    def rebase_reference(
        self,
        *,
        new_reference: float,
        generation: int,
    ) -> None:
        """
        Eski bir evaluation protokolünden gelen referansı
        mevcut standart protokole çevirir.

        Geçmiş milestone'ları mümkün olduğunca korur.

        Eğer yeni referansa göre %100 recovery zaten
        gerçekleşmiş görünüyorsa fakat tam crossing generation
        geçmiş loglardan bilinmiyorsa, mevcut generation
        'first confirmed generation' olarak kaydedilir.
        """

        if new_reference <= 0:
            return

        old_reference = (
            self.pre_shift_reference
        )

        # Zaten aynı referanstaysak hiçbir şey yapma.
        if (
            old_reference > 0
            and abs(
                old_reference
                - new_reference
            )
            < 1e-9
        ):
            return

        self.pre_shift_reference = (
            float(
                new_reference
            )
        )

        recovery_percent = (
            self._current_recovery_percent()
        )

        # Eski 50/75/90 milestone kayıtlarımız
        # gerçek gözlemlerden geldiği için koruyoruz.
        #
        # Fakat yeni referansa göre artık %100 aşılmışsa
        # ve %100 milestone bilinmiyorsa, exact historical
        # crossing generation elimizde olmadığı için
        # mevcut generation'ı first confirmed olarak yazıyoruz.

        if (
            recovery_percent >= 100.0
            and self.milestones[
                100
            ] is None
        ):

            self.milestones[
                100
            ] = generation

            self.recovery_generation = (
                generation
            )

        elif (
            recovery_percent < 100.0
        ):

            # Yanlış legacy reference yüzünden daha önce
            # full recovery işaretlendiyse temizle.
            self.milestones[
                100
            ] = None

            self.recovery_generation = None

        self._update_milestones(
            generation
        )

    # ========================================================
    # REPORT
    # ========================================================

    def report(
        self,
        generation: int,
    ) -> dict:

        if self.current_era_id is None:

            return {
                "active": False,
            }

        reference = (
            self.pre_shift_reference
        )

        recovery_percent = (
            self._current_recovery_percent()
        )

        if reference > 0:

            shock_loss_percent = (
                (
                    reference
                    - self.start_fitness
                )
                / reference
                * 100.0
            )

        else:

            shock_loss_percent = 0.0

        milestone_ages = {}

        for (
            threshold,
            milestone_generation,
        ) in self.milestones.items():

            if milestone_generation is None:

                milestone_ages[
                    threshold
                ] = None

            else:

                milestone_ages[
                    threshold
                ] = (
                    milestone_generation
                    - self.era_start_generation
                )

        return {
            "active":
                True,

            "era_id":
                self.current_era_id,

            "era_name":
                self.era_name,

            "start_generation":
                self.era_start_generation,

            "generations_in_era":
                (
                    generation
                    - self.era_start_generation
                ),

            "pre_shift_reference":
                reference,

            "start_fitness":
                self.start_fitness,

            "lowest_fitness":
                self.lowest_fitness,

            "era_best_fitness":
                self.best_fitness,

            "shock_loss_percent":
                shock_loss_percent,

            "recovery_percent":
                recovery_percent,

            "recovery_generation":
                self.recovery_generation,

            "fully_recovered":
                (
                    self.recovery_generation
                    is not None
                ),

            "milestones":
                dict(
                    self.milestones
                ),

            "milestone_ages":
                milestone_ages,
        }

    # ========================================================
    # ARCHIVE
    # ========================================================

    def _archive_current_era(
        self,
        end_generation: int,
    ) -> None:

        if self.current_era_id is None:
            return

        self.history.append(
            {
                "era_id":
                    self.current_era_id,

                "era_name":
                    self.era_name,

                "start_generation":
                    self.era_start_generation,

                "end_generation":
                    end_generation,

                "pre_shift_reference":
                    self.pre_shift_reference,

                "start_fitness":
                    self.start_fitness,

                "lowest_fitness":
                    self.lowest_fitness,

                "best_fitness":
                    self.best_fitness,

                "recovery_generation":
                    self.recovery_generation,

                "milestones":
                    dict(
                        self.milestones
                    ),
            }
        )