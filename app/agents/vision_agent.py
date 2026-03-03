import json
from typing import Dict, Any, List
import dashscope
from dashscope import MultiModalConversation

from app.config import settings
from app.utils.file_handler import extract_text_from_image


class VisionAgent:
    """视觉处理Agent - 负责图片识别、内容分析"""

    def __init__(self):
        # 配置通义千问API
        dashscope.api_key = settings.dashscope_api_key

    def analyze_image_content(self, image_path: str, user_grade: str) -> Dict[str, Any]:
        """
        分析图片内容（作业/试卷）
        返回：包含文本、知识点、错题、薄弱点的分析结果
        """
        # 1. 提取图片文本
        ocr_text = extract_text_from_image(image_path)

        if not ocr_text:
            return {
                "content": "",
                "knowledge_points": [],
                "wrong_questions": [],
                "weak_points": [],
                "score": None,
                "suggestions": []
            }

        # 2. 使用通义千问多模态模型分析内容
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "image": f"{image_path}",  # 本地图片路径
                    },
                    {
                        "text": f"""
                        你是一个专业的{user_grade}学习辅导老师，请分析这张作业/试卷图片的内容：
                        1. 识别所有题目和答案
                        2. 批改对错，指出错误的地方
                        3. 提取涉及的知识点（以列表形式返回）
                        4. 识别错题（以列表形式返回，包含题目、错误答案、正确答案、错误原因）
                        5. 分析薄弱知识点（以列表形式返回）
                        6. 给出分数（如果适用）
                        7. 给出针对性的学习建议（以列表形式返回）

                        请严格按照以下JSON格式返回，不要添加任何额外内容：
                        {{
                            "content": "识别的完整文本",
                            "knowledge_points": ["知识点1", "知识点2"],
                            "wrong_questions": [{{"question": "题目", "wrong_answer": "错误答案", "correct_answer": "正确答案", "reason": "错误原因"}}],
                            "weak_points": ["薄弱点1", "薄弱点2"],
                            "score": 90.0,
                            "suggestions": ["建议1", "建议2"]
                        }}
                        """
                    }
                ]
            }
        ]

        try:
            # 调用通义千问多模态API
            response = MultiModalConversation.call(
                model='qwen-vl-plus',
                messages=messages,
                result_format='message',
                stream=False,
                temperature=0.1
            )

            # 解析响应
            content = response.output.choices[0].message.content
            analysis_result = json.loads(content)

            # 补充OCR文本（如果模型返回的content为空）
            if not analysis_result.get("content"):
                analysis_result["content"] = ocr_text

            return analysis_result

        except Exception as e:
            # 降级处理：仅使用OCR文本 + 基础分析
            return {
                "content": ocr_text,
                "knowledge_points": ["无法识别知识点"],
                "wrong_questions": [],
                "weak_points": [],
                "score": None,
                "suggestions": ["图片分析失败，请检查图片质量或重试"]
            }