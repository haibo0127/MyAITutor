"""
文件处理工具：保存上传文件、图片OCR识别、知识点分析
"""
import os
import uuid
import cv2
import numpy as np
import pytesseract
from fastapi import HTTPException, status
from app.config import settings

# Windows适配：Tesseract-OCR路径（根据你的安装路径修改）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def save_uploaded_file(file) -> tuple[str, str]:
    """
    保存上传的文件
    返回：(唯一文件名, 文件路径)
    """
    # 生成唯一文件名
    file_ext = file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_ext}"

    # 确保上传目录存在
    os.makedirs(settings.upload_dir, exist_ok=True)

    # 拼接路径（适配Windows/Linux）
    file_path = os.path.join(settings.upload_dir, unique_filename)

    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        return unique_filename, file_path
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )


def preprocess_image(image_path: str) -> np.ndarray:
    """
    图片预处理（提高OCR识别率）
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片读取失败"
        )

    # 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 二值化（去除噪声）
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # 膨胀操作（连接断裂的字符）
    kernel = np.ones((1, 1), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=1)

    return thresh


def analyze_image_content(image_path: str, grade: str) -> dict:
    """
    分析图片内容：OCR识别 + 知识点/薄弱点分析
    """
    try:
        # 图片预处理
        processed_img = preprocess_image(image_path)

        # OCR识别（中文+数字）
        custom_config = r'--oem 3 --psm 6 -l chi_sim+eng'
        text = pytesseract.image_to_string(processed_img, config=custom_config)

        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片中未识别到文字内容"
            )

        # 模拟知识点分析（根据年级和识别文本）
        # 实际场景可对接大模型，这里简化返回
        knowledge_points = []
        weak_points = []

        if grade == "初中":
            if any(key in text for key in ["一元一次方程", "几何", "三角形"]):
                knowledge_points.append("初中数学-一元一次方程")
                weak_points.append("初中数学-几何证明")
            if any(key in text for key in ["英语", "语法", "单词"]):
                knowledge_points.append("初中英语-语法填空")
        elif grade == "高中":
            if any(key in text for key in ["导数", "函数", "解析几何"]):
                knowledge_points.append("高中数学-导数应用")
                weak_points.append("高中数学-解析几何")
            if any(key in text for key in ["物理", "力学", "电磁学"]):
                knowledge_points.append("高中物理-电磁学")
                weak_points.append("高中物理-力学综合")

        # 统计错题数（简化）
        error_count = len([line for line in text.split("\n") if "×" in line or "错" in line])

        return {
            "ocr_text": text.strip(),
            "grade": grade,
            "knowledge_points": knowledge_points,
            "weak_points": weak_points,
            "error_count": error_count,
            "suggestion": f"重点复习：{', '.join(weak_points)}" if weak_points else "知识点掌握良好，继续保持"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片分析失败: {str(e)}"
        )