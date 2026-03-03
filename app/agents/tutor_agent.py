import json
from typing import Dict, Any, List
import dashscope
from dashscope import Generation

from app.config import settings
from app.agents.memory_manager import MemoryManager


class TutorAgent:
    """学习辅导Agent - 结合大模型和用户记忆提供个性化辅导"""

    def __init__(self, db):
        self.db = db
        # 配置通义千问API
        dashscope.api_key = settings.dashscope_api_key
        # 初始化记忆管理器
        self.memory_manager = MemoryManager(db)

    def generate_personalized_content(self, user_id: int, user_grade: str, topic: str = None) -> Dict[str, Any]:
        """
        生成个性化学习内容
        """
        # 获取用户记忆（薄弱点等）
        user_memory = self.memory_manager.get_user_memory(user_id)
        weak_points = self.memory_manager.get_user_weak_points(user_id)

        # 构建提示词
        prompt = f"""
        你是一位专业的{user_grade}全科辅导老师，根据学生的学习情况生成个性化学习内容。

        学生信息：
        - 年级：{user_grade}
        - 薄弱知识点：{weak_points['memory_value']['top_weak'] if weak_points else '暂无'}

        {"- 学习主题：" + topic if topic else ""}

        请生成：
        1. 针对性的练习题（5-10道），重点覆盖薄弱知识点
        2. 知识点讲解（简明易懂）
        3. 学习建议
        4. 相关学习资源推荐

        要求：
        - 内容难度适配{user_grade}水平
        - 重点针对薄弱知识点
        - 语言通俗易懂，适合学生自主学习
        - 练习题要有答案和解析

        请严格按照以下JSON格式返回：
        {{
            "exercises": [{{
                "question": "题目内容",
                "options": ["选项A", "选项B", "选项C", "选项D"],
                "correct_answer": "正确答案",
                "analysis": "答案解析"
            }}],
            "knowledge_explanation": "知识点讲解内容",
            "learning_suggestions": ["建议1", "建议2"],
            "resource_recommendations": ["资源1", "资源2"]
        }}
        """

        try:
            # 调用通义千问API
            response = Generation.call(
                model='qwen-plus',
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                result_format='message',
                temperature=0.7,
                top_p=0.8
            )

            content = json.loads(response.output.choices[0].message.content)
            return content

        except Exception as e:
            return {
                "error": str(e),
                "exercises": [],
                "knowledge_explanation": "",
                "learning_suggestions": [],
                "resource_recommendations": []
            }

    def analyze_study_progress(self, user_id: int, user_grade: str) -> Dict[str, Any]:
        """
        分析学生学习进度和效果
        """
        # 获取用户所有记忆和学习记录
        user_memory = self.memory_manager.get_user_memory(user_id)
        weak_points = self.memory_manager.get_user_weak_points(user_id)

        prompt = f"""
        请分析这位{user_grade}学生的学习进度：

        薄弱知识点：{weak_points['memory_value'] if weak_points else '暂无'}
        学习记录：{user_memory}

        请生成：
        1. 学习进度总结
        2. 进步点和不足点
        3. 下一步学习计划
        4. 家长辅导建议

        请严格按照以下JSON格式返回：
        {{
            "progress_summary": "学习进度总结",
            "strengths": ["进步点1", "进步点2"],
            "weaknesses": ["不足点1", "不足点2"],
            "study_plan": ["计划1", "计划2"],
            "parent_suggestions": ["建议1", "建议2"]
        }}
        """

        try:
            response = Generation.call(
                model='qwen-plus',
                messages=[
                    {'role': 'user', 'content': prompt}
                ],
                result_format='message',
                temperature=0.5
            )

            return json.loads(response.output.choices[0].message.content)

        except Exception as e:
            return {
                "error": str(e),
                "progress_summary": "",
                "strengths": [],
                "weaknesses": [],
                "study_plan": [],
                "parent_suggestions": []
            }