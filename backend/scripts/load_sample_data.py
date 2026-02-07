"""
Script to load sample data into the Emergency Triage System
Run this after setting up MongoDB to populate with test resources
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import db_manager
from app.models.schemas import Resource, ResourceType, ResourceLocation, NeedType
from datetime import datetime


async def load_sample_resources():
    """Load sample emergency resources into the database"""
    
    print("Connecting to database...")
    await db_manager.connect()
    
    print("Clearing existing resources...")
    await Resource.delete_all()
    
    print("Loading sample resources...")
    
    sample_resources = [
        Resource(
            resource_id="ambulance-001",
            resource_type=ResourceType.AMBULANCE,
            name="City Hospital Ambulance Unit A",
            description="Advanced life support ambulance with paramedic team",
            location=ResourceLocation(
                address="123 Hospital Drive, Downtown",
                latitude=40.7128,
                longitude=-74.0060,
                region="Downtown"
            ),
            capacity=4,
            current_availability=4,
            capabilities=[NeedType.MEDICAL_AID, NeedType.RESCUE],
            status="active",
            contact_info={
                "phone": "+1-555-0101",
                "radio": "Channel 5"
            },
            estimated_response_time_minutes=15,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="ambulance-002",
            resource_type=ResourceType.AMBULANCE,
            name="Mercy Hospital Ambulance Unit B",
            description="Basic life support ambulance",
            location=ResourceLocation(
                address="456 Medical Plaza, Uptown",
                latitude=40.7580,
                longitude=-73.9855,
                region="Uptown"
            ),
            capacity=2,
            current_availability=2,
            capabilities=[NeedType.MEDICAL_AID],
            status="active",
            contact_info={
                "phone": "+1-555-0102",
                "radio": "Channel 7"
            },
            estimated_response_time_minutes=20,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="rescue-001",
            resource_type=ResourceType.RESCUE_TEAM,
            name="Fire Department Rescue Squad Alpha",
            description="Heavy rescue team with specialized equipment",
            location=ResourceLocation(
                address="789 Fire Station Road, Central",
                latitude=40.7489,
                longitude=-73.9680,
                region="Central"
            ),
            capacity=10,
            current_availability=10,
            capabilities=[NeedType.RESCUE, NeedType.EVACUATION, NeedType.MEDICAL_AID],
            status="active",
            contact_info={
                "phone": "+1-555-0201",
                "radio": "Channel 3"
            },
            estimated_response_time_minutes=12,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="rescue-002",
            resource_type=ResourceType.RESCUE_TEAM,
            name="Search and Rescue Team Bravo",
            description="Specialized urban search and rescue team",
            location=ResourceLocation(
                address="321 Emergency Services Blvd, Westside",
                latitude=40.7589,
                longitude=-73.9851,
                region="Westside"
            ),
            capacity=8,
            current_availability=6,
            capabilities=[NeedType.RESCUE, NeedType.EVACUATION],
            status="active",
            contact_info={
                "phone": "+1-555-0202",
                "radio": "Channel 4"
            },
            estimated_response_time_minutes=18,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="food-supplies-001",
            resource_type=ResourceType.FOOD_SUPPLIES,
            name="Red Cross Food Distribution Unit",
            description="Mobile food distribution with emergency supplies",
            location=ResourceLocation(
                address="555 Charity Lane, Eastside",
                latitude=40.7282,
                longitude=-73.9942,
                region="Eastside"
            ),
            capacity=200,
            current_availability=200,
            capabilities=[NeedType.FOOD, NeedType.WATER],
            status="active",
            contact_info={
                "phone": "+1-555-0301",
                "email": "food@redcross.org"
            },
            estimated_response_time_minutes=45,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="water-supplies-001",
            resource_type=ResourceType.WATER_SUPPLIES,
            name="Emergency Water Distribution Truck",
            description="Clean water supply and purification unit",
            location=ResourceLocation(
                address="888 Relief Center St, Northend",
                latitude=40.7831,
                longitude=-73.9712,
                region="Northend"
            ),
            capacity=500,
            current_availability=500,
            capabilities=[NeedType.WATER, NeedType.SANITATION],
            status="active",
            contact_info={
                "phone": "+1-555-0302"
            },
            estimated_response_time_minutes=40,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="shelter-001",
            resource_type=ResourceType.SHELTER_TEAM,
            name="Community Shelter Team",
            description="Mobile shelter setup with supplies",
            location=ResourceLocation(
                address="999 Community Center Ave, Southside",
                latitude=40.7069,
                longitude=-74.0113,
                region="Southside"
            ),
            capacity=150,
            current_availability=150,
            capabilities=[NeedType.SHELTER, NeedType.BLANKETS, NeedType.CLOTHING],
            status="active",
            contact_info={
                "phone": "+1-555-0401",
                "email": "shelter@community.org"
            },
            estimated_response_time_minutes=60,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="medical-team-001",
            resource_type=ResourceType.MEDICAL_TEAM,
            name="Emergency Mobile Clinic",
            description="Full medical team with portable clinic equipment",
            location=ResourceLocation(
                address="222 Healthcare Plaza, Medical District",
                latitude=40.7423,
                longitude=-73.9892,
                region="Medical District"
            ),
            capacity=50,
            current_availability=50,
            capabilities=[NeedType.MEDICAL_AID, NeedType.PSYCHOLOGICAL_SUPPORT],
            status="active",
            contact_info={
                "phone": "+1-555-0501",
                "email": "mobile@healthclinic.org"
            },
            estimated_response_time_minutes=30,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="transport-001",
            resource_type=ResourceType.TRANSPORT,
            name="Emergency Evacuation Bus Fleet",
            description="3 buses for mass evacuation",
            location=ResourceLocation(
                address="777 Transit Hub, Transport Center",
                latitude=40.7614,
                longitude=-73.9776,
                region="Transport Center"
            ),
            capacity=120,
            current_availability=120,
            capabilities=[NeedType.EVACUATION],
            status="active",
            contact_info={
                "phone": "+1-555-0601",
                "radio": "Channel 9"
            },
            estimated_response_time_minutes=25,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        
        Resource(
            resource_id="supplies-001",
            resource_type=ResourceType.SUPPLIES,
            name="General Emergency Supplies Warehouse",
            description="Warehouse with various emergency supplies",
            location=ResourceLocation(
                address="444 Warehouse District, Industrial Area",
                latitude=40.7178,
                longitude=-74.0132,
                region="Industrial Area"
            ),
            capacity=1000,
            current_availability=1000,
            capabilities=[
                NeedType.BLANKETS,
                NeedType.CLOTHING,
                NeedType.SANITATION,
                NeedType.FOOD,
                NeedType.WATER
            ],
            status="active",
            contact_info={
                "phone": "+1-555-0701",
                "email": "supplies@emergency.org"
            },
            estimated_response_time_minutes=90,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
    ]
    
    # Insert all resources
    for resource in sample_resources:
        await resource.insert()
        print(f"✓ Added: {resource.name}")
    
    print(f"\n✅ Successfully loaded {len(sample_resources)} sample resources!")
    
    await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(load_sample_resources())
