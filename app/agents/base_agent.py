import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from app.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    OpenCLAW Agent 基类
    所有具体的 Agent (如视觉分析、辅导老师) 都应继承此类。
    提供统一的日志记录、重试机制和配置加载。
    """

    def __init__(self, model_name: str = "qwen-max"):
        self.model_name = model_name
        self.api_key = settings.DASHSCOPE_API_KEY

        if not self.api_key:
            logger.error("DashScope API Key is not configured in environment variables.")
            raise ValueError("Missing DASHSCOPE_API_KEY")

    def _log_request(self, prompt_summary: str):
        """记录请求日志"""
        logger.info(f"[{self.__class__.__name__}] 正在调用模型: {self.model_name}")
        logger.debug(f"Prompt 摘要: {prompt_summary[:100]}...")

    def _log_response(self, response_summary: str):
        """记录响应日志"""
        logger.info(f"[{self.__class__.__name__}] 模型响应接收成功")
        logger.debug(f"Response 摘要: {response_summary[:100]}...")

    def _handle_error(self, error: Exception, context: str = ""):
        """统一错误处理"""
        logger.error(f"[{self.__class__.__name__}] 发生错误: {str(error)} | 上下文: {context}")
        # 这里可以添加重试逻辑或 fallback 逻辑
        raise error

    @abstractmethod
    def run(self, input_data: Any, **kwargs) -> Any:
        """
        执行 Agent 的核心逻辑
        子类必须实现此方法
        """
        pass

    def generate_system_prompt(self, role: str, context: str = "") -> str:
        """
        生成标准的 System Prompt
        """
        base_prompt = f"你是一位专业的{role}。"
        if context:
            base_prompt += f"\n背景信息：{context}"
        base_prompt += "\n请确保回答准确、逻辑清晰，并严格遵守输出格式要求。"
        return base_prompt