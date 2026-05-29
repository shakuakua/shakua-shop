"""Update all products with appropriate placeholder images."""
import sys
sys.path.insert(0, '.')
from app import create_app
from models import db, Product

# Product name -> image URL mapping (using picsum with seeds for stable images)
IMAGE_MAP = {
    "iPhone 15 Pro": "https://picsum.photos/seed/iphone15/400/300",
    "MacBook Air M3": "https://picsum.photos/seed/macbook/400/300",
    "iPad Air": "https://picsum.photos/seed/ipad/400/300",
    "AirPods Pro 2": "https://picsum.photos/seed/airpods/400/300",
    "华为Mate 60 Pro": "https://picsum.photos/seed/mate60/400/300",
    "小米14 Ultra": "https://picsum.photos/seed/xiaomi14/400/300",
    "男士商务夹克": "https://picsum.photos/seed/jacket/400/300",
    "女士连衣裙": "https://picsum.photos/seed/dress/400/300",
    "跑步鞋": "https://picsum.photos/seed/runningshoes/400/300",
    "休闲卫衣": "https://picsum.photos/seed/hoodie/400/300",
    "Python编程从入门到实践": "https://picsum.photos/seed/pythonbook/400/300",
    "三体全集": "https://picsum.photos/seed/threebody/400/300",
    "人类简史": "https://picsum.photos/seed/sapiens/400/300",
    "有机坚果礼盒": "https://picsum.photos/seed/nuts/400/300",
    "进口咖啡豆": "https://picsum.photos/seed/coffee/400/300",
    "龙井绿茶礼盒": "https://picsum.photos/seed/greentea/400/300",
    "智能扫地机器人": "https://picsum.photos/seed/robot/400/300",
    "乳胶记忆枕": "https://picsum.photos/seed/pillow/400/300",
    "多功能料理锅": "https://picsum.photos/seed/cooker/400/300",
    "瑜伽垫加厚防滑": "https://picsum.photos/seed/yogamat/400/300",
    "户外登山背包": "https://picsum.photos/seed/backpack/400/300",
    "智能运动手表": "https://picsum.photos/seed/smartwatch/400/300",
}

app = create_app()
with app.app_context():
    count = 0
    for p in Product.query.all():
        if p.name in IMAGE_MAP:
            p.image_url = IMAGE_MAP[p.name]
            count += 1
            print(f"Updated: {p.name} -> {p.image_url}")
    db.session.commit()
    print(f"\nDone! Updated {count} products.")
