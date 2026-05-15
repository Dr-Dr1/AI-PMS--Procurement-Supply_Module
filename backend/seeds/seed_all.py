"""
Master seed runner — identity + schedule + procurement module in dependency order.

Usage (from backend/ directory):
    python -m seeds.seed_all

All seeds are idempotent; re-running is safe.
"""
from __future__ import annotations

import asyncio

from seeds.identity_seed import seed as seed_identity
from seeds.schedule_seed import seed as seed_schedule
from seeds.procurement_seed import seed as seed_procurement


async def main() -> None:
    print("=== Step 1/3: Identity ===")
    await seed_identity()

    print("=== Step 2/3: Schedule Module ===")
    await seed_schedule()

    print("=== Step 3/3: Procurement Module ===")
    await seed_procurement()

    print("=== All done ===")


if __name__ == "__main__":
    asyncio.run(main())
