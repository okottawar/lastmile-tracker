import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal,init_db
from app.core.security import hash_password
from app.models.user import User
from app.models.zone import Zone,ZoneArea
from app.models.rate_card import RateCard,CODSurchargeRule
from app.models.agent import Agent
from app.models.enums import UserRole,OrderType,ZoneRelation,AgentAvailability
async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        if (await db.execute(select(User.id).where(User.email=="admin@lastmile.com"))).scalar_one_or_none(): print("Seed data already exists; nothing to do.");return
        admin=User(name="Admin User",email="admin@lastmile.com",phone="+919999999999",hashed_password=hash_password("admin123"),role=UserRole.ADMIN);db.add(admin)
        mumbai=Zone(name="Mumbai",description="Mumbai metro area");pune=Zone(name="Pune",description="Pune metro area");db.add_all([mumbai,pune]);await db.flush()
        db.add_all([ZoneArea(zone_id=mumbai.id,pincode="400001",area_name="Fort",city="Mumbai"),ZoneArea(zone_id=mumbai.id,pincode="400059",area_name="Andheri",city="Mumbai"),ZoneArea(zone_id=pune.id,pincode="411001",area_name="Pune Camp",city="Pune"),ZoneArea(zone_id=pune.id,pincode="411045",area_name="Hinjewadi",city="Pune")])
        lanes=[(mumbai.id,mumbai.id,OrderType.B2C,40,15,.5),(mumbai.id,mumbai.id,OrderType.B2B,60,12,1),(pune.id,pune.id,OrderType.B2C,40,15,.5),(pune.id,pune.id,OrderType.B2B,60,12,1),(mumbai.id,pune.id,OrderType.B2C,80,20,.5),(pune.id,mumbai.id,OrderType.B2C,80,20,.5),(mumbai.id,pune.id,OrderType.B2B,100,18,1),(pune.id,mumbai.id,OrderType.B2B,100,18,1)]
        for o,d,t,b,w,m in lanes: db.add(RateCard(origin_zone_id=o,dest_zone_id=d,order_type=t,relation=ZoneRelation.INTRA if o==d else ZoneRelation.INTER,base_price=b,price_per_kg=w,min_chargeable_weight_kg=m))
        db.add_all([CODSurchargeRule(order_type=OrderType.B2C,flat_fee=20,percent_of_order=2),CODSurchargeRule(order_type=OrderType.B2B,flat_fee=50,percent_of_order=1.5)])
        u1=User(name="Ravi Kumar",email="agent1@lastmile.com",phone="+919111111111",hashed_password=hash_password("agent123"),role=UserRole.AGENT);u2=User(name="Sneha Patil",email="agent2@lastmile.com",phone="+919222222222",hashed_password=hash_password("agent123"),role=UserRole.AGENT);db.add_all([u1,u2]);await db.flush();db.add_all([Agent(user_id=u1.id,home_zone_id=mumbai.id,availability=AgentAvailability.AVAILABLE,current_lat=19.076,current_lng=72.877,max_active_orders=5),Agent(user_id=u2.id,home_zone_id=pune.id,availability=AgentAvailability.AVAILABLE,current_lat=18.520,current_lng=73.856,max_active_orders=5)])
        db.add(User(name="Demo Customer",email="customer@lastmile.com",phone="+919333333333",hashed_password=hash_password("customer123"),role=UserRole.CUSTOMER));await db.commit();print("Seed complete.")
if __name__=="__main__": asyncio.run(seed())
