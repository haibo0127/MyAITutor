"""
学习模块路由
包含：图片上传、内容分析、记忆管理
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Any, Dict

# 本地模块导入
from app.database import get_db
from app.auth import get_current_user
from app.models import User
from app.config import settings
from app.utils.file_handler import save_uploaded_file, analyze_image_content
from app.agents.memory_manager import update_user_memory

# 路由实例
router = APIRouter()


# ------------------- 图片上传 -------------------
@router.post("/upload/image", summary="上传学习图片（作业/试卷）")
async def upload_study_image(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    上传图片文件（支持jpg/jpeg/png格式）
    """
    # 验证文件类型
    allowed_extensions = {"jpg", "jpeg", "png"}
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持jpg/jpeg/png格式的图片文件"
        )

    # 保存文件
    try:
        file_id, file_path = save_uploaded_file(file)
        return {
            "status": "success",
            "detail": "文件上传成功",
            "file_id": file_id,
            "file_path": file_path,
            "user_id": current_user.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )


# ------------------- 图片内容分析 -------------------
@router.post("/analyze/{file_id}", summary="分析图片中的学习内容")
async def analyze_study_content(
        file_id: str,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    分析图片中的题目、错题、知识点，并更新用户记忆
    """
    # 验证文件存在
    file_path = os.path.join(settings.upload_dir, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文件不存在: {file_id}"
        )

    # 分析图片内容
    try:
        # 调用OCR+知识点分析
        analysis_result = analyze_image_content(file_path, current_user.grade)

        # 更新用户记忆（薄弱点）
        if analysis_result.get("weak_points"):
            update_user_memory(
                db=db,
                user_id=current_user.id,
                memory_key=f"weak_points_{current_user.grade}",
                memory_value=analysis_result["weak_points"],
                confidence=0.8
            )

        return {
            "status": "success",
            "user_info": {
                "username": current_user.username,
                "grade": current_user.grade
            },
            "analysis": analysis_result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内容分析失败: {str(e)}"
        )


# ------------------- 获取用户学习记忆 -------------------
@router.get("/memory", summary="获取当前用户的学习记忆")
async def get_study_memory(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取用户的个性化学习记忆（薄弱点、错题等）
    """
    from app.agents.memory_manager import get_user_memory

    memories = get_user_memory(db, current_user.id)

    return {
        "status": "success",
        "username": current_user.username,
        "memories": memories
    }