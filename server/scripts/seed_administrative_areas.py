import asyncio
import uuid
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.administrative_area import AdministrativeArea
from app.models.enums import AdministrativeLevel


async def seed_administrative_areas():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(AdministrativeArea).limit(1))
        if result.scalar_one_or_none() is not None:
            print("Administrative areas already seeded. Skipping.")
            return

        print("Seeding administrative areas...")

        # 1. States
        karnataka = AdministrativeArea(name="Karnataka", level=AdministrativeLevel.STATE)
        maharashtra = AdministrativeArea(name="Maharashtra", level=AdministrativeLevel.STATE)
        delhi = AdministrativeArea(name="Delhi", level=AdministrativeLevel.STATE)
        tamil_nadu = AdministrativeArea(name="Tamil Nadu", level=AdministrativeLevel.STATE)
        kerala = AdministrativeArea(name="Kerala", level=AdministrativeLevel.STATE)

        session.add_all([karnataka, maharashtra, delhi, tamil_nadu, kerala])
        await session.flush()

        # 2. Districts
        bengaluru_urban = AdministrativeArea(name="Bengaluru Urban", level=AdministrativeLevel.DISTRICT, parent_id=karnataka.id)
        mumbai_suburban = AdministrativeArea(name="Mumbai Suburban", level=AdministrativeLevel.DISTRICT, parent_id=maharashtra.id)
        central_delhi = AdministrativeArea(name="Central Delhi", level=AdministrativeLevel.DISTRICT, parent_id=delhi.id)
        chennai = AdministrativeArea(name="Chennai", level=AdministrativeLevel.DISTRICT, parent_id=tamil_nadu.id)
        ernakulam = AdministrativeArea(name="Ernakulam", level=AdministrativeLevel.DISTRICT, parent_id=kerala.id)

        session.add_all([bengaluru_urban, mumbai_suburban, central_delhi, chennai, ernakulam])
        await session.flush()

        # 3. Blocks / Zones
        bengaluru_east = AdministrativeArea(name="Bengaluru East Zone", level=AdministrativeLevel.BLOCK, parent_id=bengaluru_urban.id)
        bengaluru_south = AdministrativeArea(name="Bengaluru South Zone", level=AdministrativeLevel.BLOCK, parent_id=bengaluru_urban.id)
        andheri_zone = AdministrativeArea(name="Andheri Zone", level=AdministrativeLevel.BLOCK, parent_id=mumbai_suburban.id)
        delhi_central_zone = AdministrativeArea(name="Delhi Central Zone", level=AdministrativeLevel.BLOCK, parent_id=central_delhi.id)

        session.add_all([bengaluru_east, bengaluru_south, andheri_zone, delhi_central_zone])
        await session.flush()

        # 4. Wards / Villages
        wards = [
            AdministrativeArea(name="Ward 150 - Bellandur", level=AdministrativeLevel.VILLAGE, parent_id=bengaluru_east.id),
            AdministrativeArea(name="Ward 80 - Indiranagar", level=AdministrativeLevel.VILLAGE, parent_id=bengaluru_east.id),
            AdministrativeArea(name="Ward 112 - Whitefield", level=AdministrativeLevel.VILLAGE, parent_id=bengaluru_east.id),
            AdministrativeArea(name="Ward 174 - HSR Layout", level=AdministrativeLevel.VILLAGE, parent_id=bengaluru_south.id),
            AdministrativeArea(name="Ward 85 - Koramangala", level=AdministrativeLevel.VILLAGE, parent_id=bengaluru_south.id),
            AdministrativeArea(name="Ward 149 - Varthur", level=AdministrativeLevel.VILLAGE, parent_id=bengaluru_east.id),
            AdministrativeArea(name="Bandra West Ward", level=AdministrativeLevel.VILLAGE, parent_id=andheri_zone.id),
            AdministrativeArea(name="Connaught Place Ward", level=AdministrativeLevel.VILLAGE, parent_id=delhi_central_zone.id),
            AdministrativeArea(name="Anna Nagar Ward", level=AdministrativeLevel.VILLAGE, parent_id=chennai.id),
            AdministrativeArea(name="Fort Kochi Ward", level=AdministrativeLevel.VILLAGE, parent_id=ernakulam.id),
        ]

        session.add_all(wards)
        await session.commit()
        print(f"Successfully seeded administrative areas!")


if __name__ == "__main__":
    asyncio.run(seed_administrative_areas())
