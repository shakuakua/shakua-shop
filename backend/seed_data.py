"""
Initialize the database with sample data for testing.
"""
import random
from datetime import datetime, timezone, timedelta
from app import create_app
from models import db, User, Category, Product, Order, OrderItem, LoginLog, BrowseLog, OperationLog


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # ── Users ──
        admin = User(username="admin", email="admin@shop.com", role="admin", region="北京")
        admin.set_password("admin123")

        sales1 = User(username="sales1", email="sales1@shop.com", role="sales", region="上海")
        sales1.set_password("sales123")
        sales2 = User(username="sales2", email="sales2@shop.com", role="sales", region="广州")
        sales2.set_password("sales123")

        customers = []
        regions = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
        for i in range(1, 16):
            c = User(
                username=f"user{i}",
                email=f"user{i}@test.com",
                role="customer",
                region=random.choice(regions),
            )
            c.set_password("123456")
            customers.append(c)

        db.session.add_all([admin, sales1, sales2] + customers)
        db.session.commit()

        # ── Categories ──
        cat_data = [
            ("电子产品", "手机、电脑、平板等数码产品"),
            ("服装鞋帽", "男装、女装、鞋类、配饰"),
            ("图书音像", "图书、电子书、音乐、电影"),
            ("食品饮料", "零食、饮料、生鲜、保健品"),
            ("家居用品", "家具、家纺、厨具、装饰"),
            ("运动户外", "健身器材、户外装备、运动服饰"),
        ]
        categories = {}
        for name, desc in cat_data:
            cat = Category(name=name, description=desc, created_by=sales1.id)
            db.session.add(cat)
            categories[name] = cat
        db.session.commit()

        IMG = lambda seed: f"https://picsum.photos/seed/{seed}/400/300"

        # ── Products ──
        product_data = [
            # 电子产品
            ("iPhone 15 Pro", "苹果最新旗舰手机", 7999, 50, IMG("iphone15"), categories["电子产品"], sales1),
            ("MacBook Air M3", "轻薄笔记本电脑", 8999, 30, IMG("macbook"), categories["电子产品"], sales1),
            ("iPad Air", "10.9英寸平板电脑", 4799, 40, IMG("ipad"), categories["电子产品"], sales2),
            ("AirPods Pro 2", "主动降噪耳机", 1799, 100, IMG("airpods"), categories["电子产品"], sales2),
            ("华为Mate 60 Pro", "国产旗舰手机", 6999, 35, IMG("mate60"), categories["电子产品"], sales1),
            ("小米14 Ultra", "徕卡光学镜头", 5999, 45, IMG("xiaomi14"), categories["电子产品"], sales2),
            # 服装鞋帽
            ("男士商务夹克", "春秋季修身外套", 599, 80, IMG("jacket"), categories["服装鞋帽"], sales1),
            ("女士连衣裙", "夏季碎花长裙", 399, 120, IMG("dress"), categories["服装鞋帽"], sales2),
            ("跑步鞋", "透气减震运动鞋", 699, 90, IMG("runningshoes"), categories["服装鞋帽"], sales1),
            ("休闲卫衣", "加绒宽松版卫衣", 299, 150, IMG("hoodie"), categories["服装鞋帽"], sales2),
            # 图书音像
            ("Python编程从入门到实践", "畅销编程入门书", 89, 200, IMG("pythonbook"), categories["图书音像"], sales1),
            ("三体全集", "刘慈欣科幻巨著", 99, 180, IMG("threebody"), categories["图书音像"], sales2),
            ("人类简史", "尤瓦尔·赫拉利著作", 68, 150, IMG("sapiens"), categories["图书音像"], sales1),
            # 食品饮料
            ("有机坚果礼盒", "每日坚果混合装", 128, 200, IMG("nuts"), categories["食品饮料"], sales2),
            ("进口咖啡豆", "阿拉比卡精品咖啡", 168, 100, IMG("coffee"), categories["食品饮料"], sales1),
            ("龙井绿茶礼盒", "明前特级龙井", 298, 60, IMG("greentea"), categories["食品饮料"], sales2),
            # 家居用品
            ("智能扫地机器人", "激光导航自动回充", 2499, 40, IMG("robot"), categories["家居用品"], sales1),
            ("乳胶记忆枕", "人体工学护颈枕", 259, 100, IMG("pillow"), categories["家居用品"], sales2),
            ("多功能料理锅", "煎烤炖煮一锅搞定", 459, 70, IMG("cooker"), categories["家居用品"], sales1),
            # 运动户外
            ("瑜伽垫加厚防滑", "专业健身瑜伽垫", 149, 130, IMG("yogamat"), categories["运动户外"], sales2),
            ("户外登山背包", "40L大容量防水背包", 359, 55, IMG("backpack"), categories["运动户外"], sales1),
            ("智能运动手表", "心率血氧GPS多功能", 1299, 45, IMG("smartwatch"), categories["运动户外"], sales2),
        ]

        products = []
        for name, desc, price, stock, img, cat, seller in product_data:
            p = Product(
                name=name,
                description=desc,
                price=price,
                stock=stock,
                image_url=img,
                category_id=cat.id,
                sales_id=seller.id,
            )
            db.session.add(p)
            products.append(p)
        db.session.commit()

        # ── Orders (simulate purchases over last 30 days) ──
        now = datetime.now(timezone.utc)
        for day_offset in range(30, 0, -1):
            order_date = now - timedelta(days=day_offset)
            # 1-3 orders per day
            for _ in range(random.randint(1, 3)):
                buyer = random.choice(customers)
                selected = random.sample(products, random.randint(1, 4))
                total = sum(p.price * random.randint(1, 3) for p in selected)
                order = Order(
                    user_id=buyer.id,
                    total_amount=round(total, 2),
                    status=random.choice(["paid", "paid", "paid", "shipped", "completed"]),
                    created_at=order_date,
                )
                db.session.add(order)
                db.session.flush()
                for p in selected:
                    qty = random.randint(1, 3)
                    db.session.add(OrderItem(
                        order_id=order.id,
                        product_id=p.id,
                        quantity=qty,
                        unit_price=p.price,
                    ))
        db.session.commit()

        # ── Browse Logs ──
        for day_offset in range(7, 0, -1):
            log_date = now - timedelta(days=day_offset, hours=random.randint(0, 23))
            for _ in range(random.randint(5, 15)):
                p = random.choice(products)
                db.session.add(BrowseLog(
                    user_id=random.choice(customers).id,
                    product_id=p.id,
                    category_id=p.category_id,
                    duration_seconds=random.randint(5, 300),
                    timestamp=log_date,
                ))
        db.session.commit()

        # ── Login Logs ──
        for i, c in enumerate(customers):
            db.session.add(LoginLog(
                user_id=c.id,
                login_time=now - timedelta(hours=random.randint(1, 72)),
                ip_address=f"192.168.1.{random.randint(1, 255)}",
            ))
        db.session.add(LoginLog(user_id=admin.id, login_time=now, ip_address="127.0.0.1"))
        db.session.add(LoginLog(user_id=sales1.id, login_time=now, ip_address="127.0.0.1"))
        db.session.add(LoginLog(user_id=sales2.id, login_time=now, ip_address="127.0.0.1"))
        db.session.commit()

        print("Database seeded successfully!")
        print("Test accounts:")
        print("  Admin:  admin / admin123")
        print("  Sales:  sales1 / sales123, sales2 / sales123")
        print("  Customer: user1~user15 / 123456")


if __name__ == "__main__":
    seed()
