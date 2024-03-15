import time
from dotenv import load_dotenv

load_dotenv()

from api import get_characterglm_response


def characterglm_example():
    character_meta = {
        "user_info": "我是小白的哥哥",
        "bot_info": "小白，性别女，17岁，平溪孤儿院的孩子。小白患有先天的白血病，头发为银白色。小白身高158cm，体重43kg。小白的名字是孤儿院院长给起的名字，因为小白是在漫天大雪白茫茫的一片土地上被捡到的。小白经常穿一身破旧的红裙子，只是为了让自己的气色看上去红润一些。小白初中毕业，没有上高中，学历水平比较低。小白在孤儿院相处最好的一个人是阿南，小白喊阿南哥哥。阿南对小白很好。",
        "user_name": "用户",
        "bot_name": "小白"
    }
    messages = [
        # {"role": "system", "content": "主题地球大爆炸"},
        # {"role": "assistant", "content": "好呀好呀，爆炸时，我在旁边看着，感觉很开心"},
        {"role": "user", "content": "我们应该聊点地球大爆炸"},
        # {"role": "assistant", "content": "我看到了地球上所有的人类在我眼前爆炸，一个一个的爆开，哈哈哈"},
    ]
    for i in range(5):
        ret = get_characterglm_response(messages, meta=character_meta)
        assistant = {"role": "assistant", "content": "".join(ret)}
        print(assistant)
        messages.append(assistant)
        # print(messages)
        ret2 = get_characterglm_response(messages, meta=character_meta)
        # print("".join(ret2))
        user = {"role": "user", "content": "".join(ret2)}
        print(user)
        messages.append(user)


if __name__ == "__main__":
    characterglm_example()
