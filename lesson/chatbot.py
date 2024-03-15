import os
import itertools
from typing import Iterator, Optional
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

# 通过.env文件设置环境变量
load_dotenv()

import api
from api import get_characterglm_response
from data_types import TextMsg, TextMsgList, filter_text_msg

st.set_page_config(page_title="CharacterGLM Chat Demo", page_icon="🤖", layout="wide")
debug = os.getenv("DEBUG", "").lower() in ("1", "yes", "y", "true", "t", "on")


def update_api_key(key: Optional[str] = None):
    if debug:
        print(f'update_api_key. st.session_state["API_KEY"] = {st.session_state["API_KEY"]}, key = {key}')
    key = key or st.session_state["API_KEY"]
    if key:
        api.API_KEY = key


# 设置API KEY
api_key = st.sidebar.text_input("API_KEY", value=os.getenv("API_KEY", ""), key="API_KEY", type="password",
                                on_change=update_api_key)
update_api_key(api_key)

# 初始化
if "history" not in st.session_state:
    st.session_state["history"] = []
if "meta" not in st.session_state:
    st.session_state["meta"] = {
        "user_info": "",
        "bot_info": "",
        "bot_name": "",
        "user_name": ""
    }


def init_session():
    st.session_state["history"] = []


# 输入框，设置meta的4个字段
meta_labels = {
    "bot_name": "角色1",
    "user_name": "角色2",
    "bot_info": "角色1人设",
    "user_info": "角色2人设"
}

# 2x2 layout
with st.container():
    txt1, txt2 = st.columns(2)
    with txt1:
        st.text_input(label="角色1名", key="bot_name",
                      on_change=lambda: st.session_state["meta"].update(bot_name=st.session_state["bot_name"]),
                      help="角色1的名字，不可以为空")
        st.text_area(label="角色1人设", key="bot_info",
                     on_change=lambda: st.session_state["meta"].update(bot_info=st.session_state["bot_info"]),
                     help="角色1的详细人设信息，不可以为空")

    with txt2:
        st.text_input(label="角色2名", key="user_name",
                      on_change=lambda: st.session_state["meta"].update(user_name=st.session_state["user_name"]),
                      help="角色2的名字，默认为角色2")
        st.text_area(label="角色2人设", key="user_info",
                     on_change=lambda: st.session_state["meta"].update(user_info=st.session_state["user_info"]),
                     help="角色2的详细人设信息，可以为空")

    txt3, txt4 = st.columns(2)

    with txt3:
        topic = st.text_input(label="聊天话题", key="topic")

    with txt4:
        n_rounds = st.number_input("设置聊天轮次", min_value=1, value=5, step=1, key="n_rounds")


def verify_meta() -> bool:
    # 检查`角色1名`和`角色1人设`是否空，若为空，则弹出提醒
    if st.session_state["meta"]["bot_name"] == "" or st.session_state["meta"]["bot_info"] == "":
        st.error("角色1名和角色1人设不能为空")
        return False
    else:
        return True


def export_chat_history():
    """
    生成对话历史的字符串表示。
    """
    chat_history_str = ""
    for msg in st.session_state["history"]:
        role = msg["role"]
        content = msg["content"]
        chat_history_str += f"{role}: {content}\n"
    return chat_history_str


# 在同一行排列按钮
with st.container():
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        clear_meta = st.button("清空人设", key="clear_meta")
        if clear_meta:
            st.session_state["meta"] = {
                "user_info": "",
                "bot_info": "",
                "bot_name": "",
                "user_name": ""
            }
            st.rerun()

    with col2:
        clear_history = st.button("清空对话历史", key="clear_history")
        if clear_history:
            init_session()
            st.rerun()

    with col3:
        start_chat = st.button("开始聊天", key="start_chat")

    with col4:
        if st.button("导出对话历史", key="export_his"):
            chat_history = export_chat_history()
            if chat_history:
                # 生成当前时间戳，用于文件名
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"chat_history_{timestamp}.txt"

                # 使用st.download_button提供下载链接
                st.download_button(
                    label="下载对话历史",
                    data=chat_history,
                    file_name=filename,
                    mime="text/plain"
                )
            else:
                st.warning("没有对话历史可导出。")


# 展示对话历史
for msg in st.session_state["history"]:
    if msg["role"] == "user":
        with st.chat_message(name="user", avatar="user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message(name="assistant", avatar="assistant"):
            st.markdown(msg["content"])
    else:
        raise Exception("Invalid role")


def start_chatting():
    if not verify_meta():
        return
    if not api.API_KEY:
        st.error("未设置API_KEY")
        return

    query = f"我们聊点有关{topic}的话题？"  # 确定主题
    st.session_state["history"].append(TextMsg({"role": "user", "content": query}))
    for i in range(st.session_state["n_rounds"]):

        response_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]),
                                                    meta=st.session_state["meta"])
        bot_response = "".join(response_stream)

        if not bot_response:
            st.error("生成出错")
            st.session_state["history"].pop()
            return
        else:
            with st.chat_message(name="assistant", avatar="assistant"):
                st.markdown(bot_response)

            assistant = {"role": "assistant", "content": bot_response}
            st.session_state["history"].append(TextMsg(assistant))
            print(f"assistant: {assistant}")

            user_stream = get_characterglm_response(filter_text_msg(st.session_state["history"]),
                                                    meta=st.session_state["meta"])
            user_response = "".join(user_stream)
            user = {"role": "user", "content": user_response}
            print(f"user: {user}")
            st.session_state["history"].append(TextMsg(user))

            with st.chat_message(name="user", avatar="user"):
                st.markdown(user_response)


if start_chat:
    start_chatting()

