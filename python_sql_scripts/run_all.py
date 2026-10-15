"""Run steps 01-07 strictly one after another, in plan order.

Guarantees:
- only one runner at a time: a MySQL named lock (GET_LOCK) is held for the
  whole run and is released automatically if this process dies;
- a step starts only after the previous step's process has exited with code 0
  AND MySQL has no other active statement on the schema (for example an
  ALTER TABLE that kept running server-side after a dropped connection);
- the first failing step stops the run; later steps never start;
- steps 6 and 7 start only after KNIME has finished writing its tables
  (row count non-zero and unchanged across consecutive checks).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from mysql.connector import Error

from common import connect, database_name, ident, scalar


HERE = Path(__file__).resolve().parent
STEPS = {
    1: "01_create_schema.py",
    2: "02_load_data.py",
    3: "03_quality_checks.py",
    4: "04_create_splits.py",
    5: "05_feature_tables.py",
    6: "06_logistic_features.py",
    7: "07_dashboard_views.py",
}
# Tables KNIME must write back to MySQL before a step may start.
KNIME_INPUTS = {
    6: ("user_segments",),
    7: ("user_segments", "rating_predictions", "model_metrics"),
}
LOCK_NAME = "movielens_strategy_pipeline"
POLL_SECONDS = 15
STABLE_CHECKS = 3


class PipelineLock:
    """Hold one dedicated connection that owns the pipeline lock."""

    def __init__(self) -> None:
        self.connection = None

    def acquire(self) -> None:
        self.connection = connect(with_database=False)
        # Keep the lock connection alive through long steps and KNIME waits.
        cursor = self.connection.cursor()
        try:
            cursor.execute("SET SESSION wait_timeout = 31536000")
        finally:
            cursor.close()
        if scalar(self.connection, "SELECT GET_LOCK(%s, 0)", (LOCK_NAME,)) != 1:
            holder = scalar(self.connection, "SELECT IS_USED_LOCK(%s)", (LOCK_NAME,))
            self.connection.close()
            raise SystemExit(
                f"Another pipeline run holds the lock (MySQL connection {holder}). "
                "Wait for it to finish; do not start a second run."
            )

    def verify(self) -> None:
        """Fail closed if the lock connection was lost."""
        try:
            owner = scalar(self.connection, "SELECT IS_USED_LOCK(%s) = CONNECTION_ID()", (LOCK_NAME,))
        except Error as exc:
            raise SystemExit(f"Lost the pipeline lock connection ({exc}); stopping for safety.")
        if owner != 1:
            raise SystemExit("Pipeline lock is no longer held by this run; stopping for safety.")

    def release(self) -> None:
        if self.connection is not None and self.connection.is_connected():
            try:
                scalar(self.connection, "SELECT RELEASE_LOCK(%s)", (LOCK_NAME,))
            finally:
                self.connection.close()


def active_statements(connection) -> list[tuple]:
    """Other non-idle sessions working on the project schema."""
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT ID, COMMAND, TIME, LEFT(COALESCE(INFO, ''), 80)
            FROM information_schema.processlist
            WHERE DB = %s AND ID <> CONNECTION_ID()
              AND COMMAND NOT IN ('Sleep', 'Daemon', 'Binlog Dump')
            """,
            (database_name(),),
        )
        return list(cursor.fetchall())
    finally:
        cursor.close()


def wait_for_idle_server(lock: PipelineLock, before: str) -> None:
    waited = 0
    while True:
        lock.verify()
        busy = active_statements(lock.connection)
        if not busy:
            return
        if waited % 60 == 0:
            print(f"[wait] {len(busy)} statement(s) still running on MySQL before {before}:")
            for process_id, command, seconds, info in busy:
                print(f"       id={process_id} {command} {seconds}s {info}")
        time.sleep(POLL_SECONDS)
        waited += POLL_SECONDS


def table_rows(connection, table: str) -> int:
    exists = scalar(
        connection,
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s AND table_name=%s",
        (database_name(), table),
    )
    if not exists:
        return 0
    return int(scalar(connection, f"SELECT COUNT(*) FROM {ident(database_name())}.{ident(table)}"))


def wait_for_knime(lock: PipelineLock, step: int, wait: bool) -> None:
    tables = KNIME_INPUTS.get(step)
    if not tables:
        return
    previous: dict[str, int] | None = None
    stable = 0
    announced = False
    while True:
        lock.verify()
        counts = {table: table_rows(lock.connection, table) for table in tables}
        ready = all(counts.values())
        if ready and counts == previous and not active_statements(lock.connection):
            stable += 1
            if stable >= STABLE_CHECKS:
                summary = ", ".join(f"{t}={n:,}" for t, n in counts.items())
                print(f"[ok  ] KNIME output is complete and stable: {summary}")
                return
        else:
            stable = 0
        previous = counts
        if not ready:
            missing = ", ".join(t for t, n in counts.items() if n == 0)
            if not wait:
                raise SystemExit(
                    f"Step {step} needs KNIME output in: {missing}. Run the KNIME "
                    f"write-back, then resume with --from-step {step}."
                )
            if not announced:
                print(
                    f"\n[wait] Step {step} needs KNIME write-back to: {missing}.\n"
                    "       Run the KNIME workflow now; this runner continues "
                    "automatically once the tables are filled and stop changing.\n"
                    "       Press Ctrl+C to stop and resume later with "
                    f"--from-step {step}."
                )
                announced = True
        time.sleep(POLL_SECONDS)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-step", type=int, choices=STEPS, default=1)
    parser.add_argument("--through", type=int, choices=STEPS, default=7)
    parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Stop instead of waiting when KNIME output for step 6/7 is missing",
    )
    args = parser.parse_args()
    if args.from_step > args.through:
        parser.error("--from-step must be <= --through")

    lock = PipelineLock()
    lock.acquire()
    started = time.monotonic()
    try:
        for number in range(args.from_step, args.through + 1):
            script = HERE / STEPS[number]
            wait_for_knime(lock, number, wait=not args.no_wait)
            wait_for_idle_server(lock, script.name)
            print(f"\n{'=' * 72}\nStep {number}: {script.name}\n{'=' * 72}", flush=True)
            step_started = time.monotonic()
            # run() blocks until the child process has fully exited.
            result = subprocess.run([sys.executable, str(script)], cwd=HERE)
            elapsed = time.monotonic() - step_started
            if result.returncode != 0:
                print(
                    f"\n[fail] Step {number} exited with code {result.returncode} "
                    f"after {elapsed:,.0f}s. Later steps were not started.\n"
                    f"       Fix the error, then resume with --from-step {number}."
                )
                sys.exit(result.returncode)
            print(f"[done] Step {number} finished in {elapsed:,.0f}s")
            # Do not hand over while a server-side statement from this step lingers.
            wait_for_idle_server(lock, "the next step")
    except KeyboardInterrupt:
        print("\n[stop] Interrupted; the current step's MySQL work may still finish server-side.")
        sys.exit(130)
    finally:
        lock.release()
    print(f"\nSteps {args.from_step}-{args.through} complete in {time.monotonic() - started:,.0f}s.")


if __name__ == "__main__":
    main()
