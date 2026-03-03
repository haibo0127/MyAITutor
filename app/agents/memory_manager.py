"""
用户记忆管理工具
包含：update_user_memory、get_user_memory 核心函数
适配routers/study.py的导入调用
"""
import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import UserMemory
from app.schemas import UserMemoryCreate


def update_user_memory(
        db: Session,
        user_id: int,
        memory_key: str,
        memory_value: list or dict or str,
        confidence: float = 0.8
):
    """
    更新用户记忆（存在则更新，不存在则创建）
    :param db: 数据库会话
    :param user_id: 用户ID
    :param memory_key: 记忆键（如：weak_points_junior）
    :param memory_value: 记忆值（支持列表/字典/字符串，自动转为JSON）
    :param confidence: 置信度（0-1，默认0.8）
    :return: 更新后的UserMemory对象
    """
    # 转换为JSON字符串（兼容不同类型的memory_value）
    if isinstance(memory_value, (list, dict)):
        memory_value_str = json.dumps(memory_value, ensure_ascii=False)
    else:
        memory_value_str = str(memory_value)

    # 转换置信度为整数（0-100），匹配模型定义
    confidence_int = int(confidence * 100)

    # 检查是否已存在该记忆
    memory = db.query(UserMemory).filter(
        UserMemory.user_id == user_id,
        UserMemory.memory_key == memory_key
    ).first()

    if memory:
        # 更新现有记忆
        memory.memory_value = memory_value_str
        memory.confidence = confidence_int
        memory.updated_at = datetime.now()
    else:
        # 创建新记忆
        memory = UserMemory(
            user_id=user_id,
            memory_key=memory_key,
            memory_value=memory_value_str,
            confidence=confidence_int
        )
        db.add(memory)

    # 提交事务
    db.commit()
    db.refresh(memory)

    return memory


def get_user_memory(
        db: Session,
        user_id: int,
        memory_key: str = None
) -> list:
    """
    获取用户记忆
    :param db: 数据库会话
    :param user_id: 用户ID
    :param memory_key: 可选，指定记忆键（如weak_points_junior）
    :return: 格式化的记忆列表
    """
    # 构建查询
    query = db.query(UserMemory).filter(UserMemory.user_id == user_id)
    if memory_key:
        query = query.filter(UserMemory.memory_key == memory_key)

    # 执行查询
    memories = query.all()

    # 格式化返回结果（转换JSON字符串为原类型）
    result = []
    for mem in memories:
        try:
            # 尝试解析JSON字符串
            value = json.loads(mem.memory_value)
        except json.JSONDecodeError:
            # 解析失败则返回原始字符串
            value = mem.memory_value

        result.append({
            "id": mem.id,
            "user_id": mem.user_id,
            "memory_key": mem.memory_key,
            "memory_value": value,
            "confidence": mem.confidence / 100,  # 转换回0-1的浮点数
            "updated_at": mem.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        })

    return result


def delete_user_memory(
        db: Session,
        user_id: int,
        memory_id: int = None,
        memory_key: str = None
) -> dict:
    """
    删除用户记忆
    :param db: 数据库会话
    :param user_id: 用户ID
    :param memory_id: 可选，指定记忆ID
    :param memory_key: 可选，指定记忆键
    :return: 删除结果
    """
    # 校验参数
    if not memory_id and not memory_key:
        raise ValueError("必须指定memory_id或memory_key")

    # 构建查询
    query = db.query(UserMemory).filter(UserMemory.user_id == user_id)
    if memory_id:
        query = query.filter(UserMemory.id == memory_id)
    if memory_key:
        query = query.filter(UserMemory.memory_key == memory_key)

    # 执行删除
    deleted_count = query.delete()
    db.commit()

    return {
        "status": "success",
        "deleted_count": deleted_count,
        "message": f"成功删除{deleted_count}条记忆记录"
    }