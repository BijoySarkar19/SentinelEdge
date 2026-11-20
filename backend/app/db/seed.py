"""Database seed script for SentinelEdge demo and production testing."""
import asyncio
import uuid
import structlog
from datetime import datetime, timezone, timedelta
from app.db.session import AsyncSessionLocal
from app.models.camera import Camera
from app.models.zone import Zone
from app.models.rule import Rule
from app.models.incident import Incident
from app.models.incident_audit import IncidentAudit
from app.models.detection_event import DetectionEvent
from app.search.embedder import index_incident
from app.models.user import User
from sqlalchemy import select

logger = structlog.get_logger()

async def run_seed():
    print("Starting SentinelEdge database seeding...")
    async with AsyncSessionLocal() as db:
        # Clean existing records to ensure fresh rich seed
        for model in [IncidentAudit, Incident, Rule, Zone, Camera]:
            records = await db.execute(select(model))
            for r in records.scalars().all():
                await db.delete(r)
        await db.commit()

        # 1. Cameras
        c1 = Camera(
            id=uuid.UUID("11111111-1111-1111-1111-111111111101"),
            name="Main Entrance North",
            description="High-definition perimeter camera monitoring Gate 1 pedestrian and vehicle access",
            source_type="rtsp",
            location="Gate 1 Plaza",
            latitude=37.7749,
            longitude=-122.4194,
            status="online",
            processing_enabled=True,
        )
        c2 = Camera(
            id=uuid.UUID("22222222-2222-2222-2222-222222222202"),
            name="Industrial Logistics Bay",
            description="Automated warehouse bay and heavy loading dock apron",
            source_type="rtsp",
            location="Warehouse Dock 4",
            latitude=37.7758,
            longitude=-122.4180,
            status="online",
            processing_enabled=True,
        )
        c3 = Camera(
            id=uuid.UUID("33333333-3333-3333-3333-333333333303"),
            name="Employee Lobby Concourse",
            description="Indoor concourse monitoring main employee turnstiles and security checkpoints",
            source_type="webcam",
            location="Building A Central",
            latitude=37.7742,
            longitude=-122.4205,
            status="online",
            processing_enabled=True,
        )
        c4 = Camera(
            id=uuid.UUID("44444444-4444-4444-4444-444444444404"),
            name="Perimeter Gate South",
            description="South perimeter fence boundary and emergency egress access lane",
            source_type="file",
            location="South Fence Line",
            latitude=37.7735,
            longitude=-122.4172,
            status="online",
            processing_enabled=True,
        )
        c5 = Camera(
            id=uuid.UUID("55555555-5555-5555-5555-555555555505"),
            name="Chemical Storage Sector",
            description="High-security hazmat chemical containment area and storage perimeter",
            source_type="rtsp",
            location="Hazardous Sector 3",
            latitude=37.7765,
            longitude=-122.4215,
            status="online",
            processing_enabled=True,
        )
        c6 = Camera(
            id=uuid.UUID("66666666-6666-6666-6666-666666666606"),
            name="North Inbound Arterial Lane",
            description="Main vehicle approach road and delivery traffic staging lane",
            source_type="rtsp",
            location="East Highway Ramp",
            latitude=37.7770,
            longitude=-122.4160,
            status="online",
            processing_enabled=True,
        )
        db.add_all([c1, c2, c3, c4, c5, c6])
        await db.commit()
        print("Cameras seeded (6 nodes).")

        # 2. Zones
        z1 = Zone(
            id=uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"),
            camera_id=c1.id,
            name="Zone A - Access Corridor",
            zone_type="access_lane",
            polygon_coordinates=[[120, 80], [340, 110], [380, 260], [160, 240]],
        )
        z2 = Zone(
            id=uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2"),
            camera_id=c2.id,
            name="Zone B - Restricted Dock Perimeter",
            zone_type="restricted",
            polygon_coordinates=[[450, 180], [720, 200], [680, 440], [430, 410]],
        )
        z3 = Zone(
            id=uuid.UUID("cccccccc-cccc-cccc-cccc-ccccccccccc3"),
            camera_id=c3.id,
            name="Zone C - High Density Concourse",
            zone_type="crowd",
            polygon_coordinates=[[100, 100], [500, 100], [500, 400], [100, 400]],
        )
        z4 = Zone(
            id=uuid.UUID("dddddddd-dddd-dddd-dddd-ddddddddddd4"),
            camera_id=c4.id,
            name="Zone D - Emergency Fire Lane",
            zone_type="access_lane",
            polygon_coordinates=[[50, 300], [400, 300], [400, 500], [50, 500]],
        )
        z5 = Zone(
            id=uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee5"),
            camera_id=c5.id,
            name="Zone E - Chemical Hazmat Boundary",
            zone_type="restricted",
            polygon_coordinates=[[200, 200], [600, 200], [600, 450], [200, 450]],
        )
        db.add_all([z1, z2, z3, z4, z5])
        await db.commit()
        print("Zones seeded (5 detection sectors).")

        # 3. Rules
        r1 = Rule(
            id=uuid.UUID("10000000-0000-0000-0000-000000000001"),
            camera_id=c1.id,
            zone_id=z1.id,
            name="Crowd Density Warning",
            rule_type="crowd_density",
            severity="high",
            is_enabled=True,
            configuration={"threshold_persons": 6, "min_dwell_seconds": 3.0},
        )
        r2 = Rule(
            id=uuid.UUID("20000000-0000-0000-0000-000000000002"),
            camera_id=c2.id,
            zone_id=z2.id,
            name="Restricted Logistics Breach",
            rule_type="restricted_zone",
            severity="critical",
            is_enabled=True,
            configuration={"threshold_objects": 1, "min_dwell_seconds": 2.0},
        )
        r3 = Rule(
            id=uuid.UUID("30000000-0000-0000-0000-000000000003"),
            camera_id=c6.id,
            zone_id=None,
            name="Vehicle Arterial Congestion",
            rule_type="vehicle_congestion",
            severity="medium",
            is_enabled=True,
            configuration={"threshold_vehicles": 4, "min_dwell_seconds": 5.0},
        )
        r4 = Rule(
            id=uuid.UUID("40000000-0000-0000-0000-000000000004"),
            camera_id=c4.id,
            zone_id=z4.id,
            name="Emergency Fire Lane Blockage",
            rule_type="access_lane",
            severity="critical",
            is_enabled=True,
            configuration={"threshold_vehicles": 1, "min_dwell_seconds": 10.0},
        )
        r5 = Rule(
            id=uuid.UUID("50000000-0000-0000-0000-000000000005"),
            camera_id=c5.id,
            zone_id=z5.id,
            name="Chemical Facility Night Intrusion",
            rule_type="restricted_zone",
            severity="critical",
            is_enabled=True,
            configuration={"threshold_objects": 1, "min_dwell_seconds": 1.5},
        )
        db.add_all([r1, r2, r3, r4, r5])
        await db.commit()
        print("Rules seeded (5 active detection rules).")

        # 4. Get Admin User for audits
        user_res = await db.execute(select(User).limit(1))
        admin_user = user_res.scalar_one_or_none()
        admin_id = admin_user.id if admin_user else None

        # 5. Incidents
        now = datetime.now(timezone.utc)
        demo_incidents_data = [
            {
                "camera_id": c1.id,
                "zone_id": z1.id,
                "rule_id": r1.id,
                "title": "Unusual Crowd Density Warning in Gate 1 Plaza",
                "description": "Crowd density threshold exceeded: 9 persons stationary in Gate 1 access corridor for over 15.2 seconds.",
                "severity": "high",
                "status": "open",
                "confidence": 0.93,
                "lat": 37.7749,
                "lng": -122.4194,
                "counts": {"person": 9},
                "classes": ["person"],
                "created_at": now - timedelta(minutes=14),
            },
            {
                "camera_id": c2.id,
                "zone_id": z2.id,
                "rule_id": r2.id,
                "title": "Restricted Logistics Bay Intrusion Detected",
                "description": "Unauthorized personnel detected inside hazardous loading dock zone during automated machinery operation.",
                "severity": "critical",
                "status": "acknowledged",
                "confidence": 0.96,
                "lat": 37.7758,
                "lng": -122.4180,
                "counts": {"person": 2},
                "classes": ["person"],
                "created_at": now - timedelta(minutes=45),
            },
            {
                "camera_id": c4.id,
                "zone_id": z4.id,
                "rule_id": r4.id,
                "title": "Emergency Access Fire Lane Blocked by Commercial Vehicle",
                "description": "Delivery truck stationary in designated emergency response fire corridor for over 4 minutes.",
                "severity": "critical",
                "status": "investigating",
                "confidence": 0.98,
                "lat": 37.7735,
                "lng": -122.4172,
                "counts": {"truck": 1},
                "classes": ["truck"],
                "created_at": now - timedelta(hours=2, minutes=10),
            },
            {
                "camera_id": c6.id,
                "zone_id": None,
                "rule_id": r3.id,
                "title": "Arterial Highway Inbound Vehicle Congestion Alert",
                "description": "Traffic flow reduced to stationary queue: 7 vehicles stopped across inbound lanes.",
                "severity": "medium",
                "status": "resolved",
                "confidence": 0.89,
                "lat": 37.7770,
                "lng": -122.4160,
                "counts": {"car": 5, "truck": 2},
                "classes": ["car", "truck"],
                "created_at": now - timedelta(hours=4, minutes=30),
            },
            {
                "camera_id": c5.id,
                "zone_id": z5.id,
                "rule_id": r5.id,
                "title": "Restricted Hazmat Chemical Storage Perimeter Breach",
                "description": "Perimeter optical beam triggered: single human target traversing hazardous containment buffer zone.",
                "severity": "critical",
                "status": "open",
                "confidence": 0.95,
                "lat": 37.7765,
                "lng": -122.4215,
                "counts": {"person": 1},
                "classes": ["person"],
                "created_at": now - timedelta(hours=6),
            },
            {
                "camera_id": c3.id,
                "zone_id": z3.id,
                "rule_id": None,
                "title": "Elevated Dwell Time at Security Turnstiles",
                "description": "Cluster of 14 people gathered at Building A turnstiles causing hallway congestion.",
                "severity": "medium",
                "status": "resolved",
                "confidence": 0.87,
                "lat": 37.7742,
                "lng": -122.4205,
                "counts": {"person": 14},
                "classes": ["person"],
                "created_at": now - timedelta(days=1, hours=2),
            },
            {
                "camera_id": c1.id,
                "zone_id": z1.id,
                "rule_id": r1.id,
                "title": "Overnight Loitering Alert at Gate 1",
                "description": "Individual loitering stationary in North Gate access corridor after operational hours.",
                "severity": "low",
                "status": "resolved",
                "confidence": 0.84,
                "lat": 37.7749,
                "lng": -122.4194,
                "counts": {"person": 1},
                "classes": ["person"],
                "created_at": now - timedelta(days=2, hours=5),
            },
            {
                "camera_id": c2.id,
                "zone_id": z2.id,
                "rule_id": r2.id,
                "title": "Forklift Speed Anomaly in Logistics Apron",
                "description": "Industrial forklift exceeding 15 km/h safety speed threshold in loading bay zone.",
                "severity": "medium",
                "status": "resolved",
                "confidence": 0.91,
                "lat": 37.7758,
                "lng": -122.4180,
                "counts": {"truck": 1},
                "classes": ["truck"],
                "created_at": now - timedelta(days=3),
            },
        ]

        created_incidents = []
        for item in demo_incidents_data:
            inc = Incident(
                event_id=f"EVT-{uuid.uuid4().hex[:12].upper()}",
                camera_id=item["camera_id"],
                zone_id=item["zone_id"],
                rule_id=item["rule_id"],
                title=item["title"],
                description=item["description"],
                severity=item["severity"],
                status=item["status"],
                confidence=item["confidence"],
                latitude=item["lat"],
                longitude=item["lng"],
                object_counts=item["counts"],
                detected_classes=item["classes"],
                inference_latency_ms=41.2,
                simulated=True,
            )
            inc.created_at = item["created_at"]
            inc.updated_at = item["created_at"]
            db.add(inc)
            created_incidents.append(inc)

        await db.commit()

        # Add Audits and Vector Embeddings
        for inc in created_incidents:
            audit = IncidentAudit(
                incident_id=inc.id,
                user_id=admin_id,
                previous_status="open",
                new_status=inc.status,
                comment=f"Automated ingestion & triage: marked as {inc.status}",
                timestamp=inc.created_at + timedelta(minutes=2),
            )
            db.add(audit)

            # Index embedding for semantic search
            try:
                await index_incident(db, inc)
            except Exception as e:
                logger.warning("Embedding index failed for incident", error=str(e))

        await db.commit()
        print(f"Incidents seeded ({len(created_incidents)} records with embeddings and audit trail).")

        # 6. Detection Events for analytics graphs
        for i in range(25):
            evt = DetectionEvent(
                event_id=f"EVT-DET-{uuid.uuid4().hex[:12].upper()}",
                camera_id=c1.id if i % 2 == 0 else c2.id,
                event_type="crowd_density" if i % 2 == 0 else "restricted_zone",
                object_counts={"person": 1 + (i % 5)},
                confidence=0.92,
                event_timestamp=now - timedelta(hours=i),
                simulated=True,
            )
            db.add(evt)

        await db.commit()
        print("Detection events seeded (25 real-time samples).")

    print("SentinelEdge database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_seed())
