from openai import OpenAI


# 初始化OpenAI客户端
def get_llm_client(base_url: str, api_key:  str) -> OpenAI:
    """
    初始化OpenAI客户端
    :param base_url:OpenAI API的Base URL
    :param api_key:OpenAI API的API Key
    :return:OpenAI客户端
    """
    return OpenAI(
        base_url=base_url,
        api_key=api_key
    )    