from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain

from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from utils import LOG

from .chatglm2 import ChatGLM2

# 创建一个 TranslationChain 类，用于构造翻译任务的聊天模型
class TranslationChain:
    # model_name: 聊天模型的名称，默认为 chatglm2
    # verbose: 是否打印日志，默认为 True
    def __init__(self, model_name: str = "chatglm2", verbose: bool = True):
        
        # 翻译任务指令始终由 System 角色承担
        template = (
            """You are a translation expert, proficient in various languages. \n
            Translates {source_language} to {target_language}."""
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)

        # 待翻译文本由 Human 角色输入
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        # 使用 System 和 Human 角色的提示模板构造 ChatPromptTemplate
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        print(f"Loading chat model {model_name}")
        if model_name == "chatglm2":
            chat = ChatGLM2()
        elif model_name == "gpt-3.5-turbo":
            chat = ChatOpenAI(model_name=model_name, temperature=0, verbose=verbose)
        else:
            chat = ChatOpenAI(verbose=verbose)

        self.chain = LLMChain(llm=chat, prompt=chat_prompt_template, verbose=verbose)

    def run(self, text: str, source_language: str, target_language: str) -> (str, bool):
        result = ""
        try:
            result = self.chain.run({
                "text": text,
                "source_language": source_language,
                "target_language": target_language,
            })
        except Exception as e:
            LOG.error(f"An error occurred during translation: {e}")
            return result, False

        return result, True