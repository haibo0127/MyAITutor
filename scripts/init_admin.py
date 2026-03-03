"""
初始化管理员账号脚本
首次启动时执行
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, SessionLocal
from app.models import Base, User
from app.auth import get_password_hash


def init_admin_user():
    """创建默认管理员账号"""
    # 1. 创建数据库表
    Base.metadata.create_all(bind=engine)

    # 2. 创建数据库会话
    db = SessionLocal()

    try:
        # 3. 检查管理员是否已存在
        admin_user = db.query(User).filter(User.username == "admin").first()
        if admin_user:
            print("✅ 管理员账号已存在，无需重复创建")
            return

        # 4. 创建管理员账号（密码自动截断72字节）
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123456")
        hashed_password = get_password_hash(admin_password)

        admin_user = User(
            username="admin",
            full_name="Super Administrator",
            email="admin@example.com",
            grade="admin",
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True
        )

        # 5. 保存到数据库
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("🎉 管理员账号创建成功！")
        print(f"🔑 用户名: admin")
        print(f"🔐 初始密码: {admin_password}")
        print("⚠️  请尽快修改初始密码！")

    except Exception as e:
        print(f"❌ 创建管理员失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_admin_user()