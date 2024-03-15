from typing import Any
# 导入 CallbackManagerForLLMRun 类，用于管理回调函数
from langchain.callbacks.manager import CallbackManagerForLLMRun
# 导入 BaseChatModel 类，用于定义聊天模型
from langchain.chat_models.base import BaseChatModel
# 导入 root_validator 装饰器，用于验证环境变量
from langchain.pydantic_v1 import root_validator
from langchain.schema import (
    BaseMessage,  # 基础消息类
    ChatMessage,  # 聊天消息类
    SystemMessage,  # 系统消息类
    HumanMessage,  # 人类消息类
    AIMessage,  # AI 消息类
    ChatResult,  # 聊天结果类
    ChatGeneration,  # 聊天生成类
)
from transformers import AutoTokenizer, AutoModel


class ChatGLM2(BaseChatModel):
    tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True)
    model = AutoModel.from_pretrained("THUDM/chatglm2-6b-int4", trust_remote_code=True).float()
    model.eval()

    @root_validator()
    def validate_environment(cls, values):
        return values

    def _generate(
        self,
        messages: [BaseMessage],
        stop: [[str]] = None,
        run_manager: [CallbackManagerForLLMRun] = None,
        **kwargs: dict,
    ) -> ChatResult:
        message = self._convert_messages(messages)
        print(message)

        response = self._chat(message)
        print(response)

        generations = self._get_generations(response)
        return ChatResult(generations=generations)

    def _chat(self, message: str) -> str:
        response, history = self.model.chat(self.tokenizer, message, history=[])
        return response

    # 转换 BaseMessage
    def _convert_messages(self, messages: [BaseMessage]) -> str:
        # 将多个 message.content 拼接到一起
        return " ".join([m.content for m in messages])

    # 通过 response 获取聊天结果
    def _get_generations(self, response: str) -> [ChatGeneration]:
        return [ChatGeneration(message=AIMessage(content=response))]

    @property
    def _llm_type(self) -> str:
        return "chatGLM2-6b"
    
