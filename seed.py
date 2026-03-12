from database import SessionLocal
from models import Service, Designer

def seed_data():
    db = SessionLocal()
    
    # 1. 新增服務項目
    if db.query(Service).count() == 0:
        services = [
            Service(name="洗頭", duration=15),
            Service(name="剪髮", duration=40),
            Service(name="染髮", duration=90),
            Service(name="燙髮", duration=120),
            Service(name="修臉", duration=30),
        ]
        db.add_all(services)
        db.commit()
        print("✅ 服務項目已成功新增至資料庫！")
    else:
        print("💡 資料庫中已經有服務項目囉！")

    # 2. 新增老闆（設計師）資料
    if db.query(Designer).count() == 0:
        boss = Designer(name="老闆")
        db.add(boss)
        db.commit()
        print("✅ 老闆資料已建立！")

    db.close()

if __name__ == "__main__":
    seed_data()