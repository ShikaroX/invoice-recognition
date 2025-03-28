import re
from ollama import chat, ChatResponse

def ask_deepseek(input_content, system_prompt, print_log = False):
    response: ChatResponse = chat(model="deepseek-r1:14b", messages=[
        {'role' : 'system', 'content': system_prompt},
        {'role' : 'user', 'content': input_content}
    ])
    response_text = response['message']['content']
    if print_log: print(response_text)
    clean_response = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()

    return clean_response
