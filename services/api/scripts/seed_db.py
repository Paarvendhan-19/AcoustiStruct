import asyncio
import os
import sys

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db_context
from app.models.user import Organization, User
from app.models.form import Form, FormField

async def seed_data():
    async with get_db_context() as db:
        print("Seeding database...")
        
        # 1. Organization
        org = Organization(
            name="Tamil Nadu Agriculture Dept",
            slug="tn-agri"
        )
        db.add(org)
        await db.commit()
        await db.refresh(org)
        
        # 2. User
        user = User(
            id="00000000-0000-0000-0000-000000000001",
            email="fieldworker@tnagri.gov.in",
            username="fieldworker1",
            full_name="Demo Field Worker",
            hashed_password="not-a-real-hash-demo-only",
            role="field_worker",
            organization_id=org.id
        )
        db.add(user)
        
        # 3. Form (Agriculture Assessment)
        form = Form(
            name="Agriculture Field Assessment",
            slug="agri-assessment",
            domain="agriculture",
            description="Field data capture for crop status and damage estimation.",
            version=1,
            language="ta",
            document_template="agriculture_report.html"
        )
        db.add(form)
        await db.commit()
        await db.refresh(form)
        
        # 4. Form Fields
        fields = [
            FormField(form_id=form.id, field_key="farmer_name", label="Farmer Name", label_local="விவசாயி பெயர்", field_type="string", required=True, risk_level="high", sort_order=1),
            FormField(form_id=form.id, field_key="village", label="Village", label_local="கிராமம்", field_type="string", required=True, risk_level="medium", sort_order=2),
            FormField(form_id=form.id, field_key="district", label="District", label_local="மாவட்டம்", field_type="string", required=True, risk_level="medium", sort_order=3),
            FormField(form_id=form.id, field_key="land_area", label="Land Area", label_local="நிலப்பரப்பு", field_type="float", required=True, risk_level="high", sort_order=4, min_value=0.1),
            FormField(form_id=form.id, field_key="land_area_unit", label="Land Area Unit", label_local="அலகு", field_type="enum", required=True, risk_level="low", sort_order=5, enum_values=["acre", "hectare", "cent"]),
            FormField(form_id=form.id, field_key="crop", label="Crop", label_local="பயிர்", field_type="string", required=True, risk_level="high", sort_order=6),
            FormField(form_id=form.id, field_key="irrigation_type", label="Irrigation Type", label_local="பாசன முறை", field_type="enum", required=True, risk_level="medium", sort_order=7, enum_values=["well_irrigation", "borewell", "river_irrigation", "rainfed", "canal_irrigation", "drip_irrigation"]),
            FormField(form_id=form.id, field_key="water_availability", label="Water Availability", label_local="நீர் இருப்பு", field_type="enum", required=True, risk_level="medium", sort_order=8, enum_values=["abundant", "adequate", "insufficient", "severe_shortage"]),
            FormField(form_id=form.id, field_key="rainfall_condition", label="Rainfall Condition", label_local="மழை நிலை", field_type="enum", required=False, risk_level="low", sort_order=9, enum_values=["above_normal", "normal", "below_normal", "drought"]),
            FormField(form_id=form.id, field_key="soil_condition", label="Soil Condition", label_local="மண் வளம்", field_type="enum", required=False, risk_level="low", sort_order=10, enum_values=["good", "moderate", "poor"]),
            FormField(form_id=form.id, field_key="fertilizer_usage", label="Fertilizer Usage", label_local="உரப் பயன்பாடு", field_type="string", required=False, risk_level="low", sort_order=11),
            FormField(form_id=form.id, field_key="pest_problem", label="Pest Problem", label_local="பூச்சி தாக்குதல்", field_type="string", required=False, risk_level="medium", sort_order=12),
            FormField(form_id=form.id, field_key="crop_damage", label="Crop Damage (%)", label_local="பயிர் சேதம் (%)", field_type="integer", required=False, risk_level="high", sort_order=13, min_value=0, max_value=100),
            FormField(form_id=form.id, field_key="estimated_loss", label="Estimated Loss (Rs)", label_local="மதிப்பிடப்பட்ட இழப்பு (ரூ)", field_type="integer", required=False, risk_level="high", sort_order=14, min_value=0),
            FormField(form_id=form.id, field_key="sowing_date", label="Sowing Date", label_local="விதைத்த தேதி", field_type="date", required=False, risk_level="medium", sort_order=15),
            FormField(form_id=form.id, field_key="harvest_date", label="Harvest Date", label_local="அறுவடை தேதி", field_type="date", required=False, risk_level="medium", sort_order=16),
            FormField(form_id=form.id, field_key="remarks", label="Remarks", label_local="குறிப்புகள்", field_type="long_text", required=False, risk_level="low", sort_order=17),
        ]
        
        db.add_all(fields)
        await db.commit()
        
        print("Database seeded successfully with demo Agriculture Assessment form.")

if __name__ == "__main__":
    asyncio.run(seed_data())
