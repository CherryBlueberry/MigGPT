import openai
import re

restriction_prompt = 'You are an expert in Linux Kernel development and coding. We kindly ask you to respond with a Markdown-formatted string within a code block that starts and ends with triple backticks (```). The response should strictly contain the identified `part_new` without providing additional analysis or using a list to store lines of code.'


def get_chat_messages(prompt_text, model="gpt-3.5-turbo", temperature=0.4):
    openai.api_key = 'your key'
    
    response = openai.chat.completions.create(
        model=model,
        messages=prompt_text,
        max_tokens=2000,
        n=1,
        stop=None,
        temperature=temperature,
    )

    return response.choices[0].message.content


def query(user_content, query_model='gpt-4', temperature=0.4):
    sys_content = "You are an expert in coding and linux kernel."
    prompt_text = [{"role": "system", "content": sys_content},
            {"role": "user", "content": "Please return the code block using Markdown format. Ensure the code block starts and ends with ```."},
            {"role": "user", "content": user_content}
        ]
    
    response_content = get_chat_messages(prompt_text, model=query_model, temperature=temperature)
    # print('response start ------------------------------------')
    # print(response_content)
    # print('response end ------------------------------------')

    return response_content


def get_code_with_markdown(response_content):
    code_block_pattern = r'```\s*(\w*)\n(.*?)\n```'
    match = re.search(code_block_pattern, response_content, re.DOTALL)
    
    if match:
        code_string = match.group(2)
        return code_string
    else:
        return None


def find_context(name_list, code, out_type='code'):
    context = []
    indexes = []
    code_lines = code.splitlines()
    features = ['extern', 'static', 'inline', 'void', 'long', 'int', 'float', 'double', 'char', 'enum']
    for name in name_list:
        start = -1
        end = -1
        for idx, line in enumerate(code_lines[:-1]):
            if (f'{name}(' in line) or (f'{name} (' in line):
                if ('{' in line) or (code_lines[idx+1]=='{'):
                    if ('if' not in line) and ('while' not in line) and ('for' not in line):
                        for feature in features:
                            if feature in line:
                                start = idx
                else:
                    l_cnt = 0
                    for char in code_lines[idx+1]:
                        if char == ')':
                            l_cnt += 1
                    if l_cnt%2==1:
                        if ('{' in code_lines[idx+1]) or (code_lines[idx+2]=='{'):
                            if ('if' not in line) and ('while' not in line) and ('for' not in line):
                                for feature in features:
                                    if feature in line:
                                        start = idx

            if start != -1 and line == '}':
                end = idx
                break

        if start != -1:
            assert end != -1, 'error'
            context.append('\n'.join(code_lines[start:end+1]))
            indexes.append((start, end))
    
    if out_type == 'code':
        return context
    elif out_type == 'idx':
        return indexes


def tokenize_c_code(line):
    tokens = re.findall(r'#[a-zA-Z_]\w*|<[a-zA-Z0-9_./]*>|[a-zA-Z_]\w*|'
                        r'[\+\-\*/%]=|<<=?|>>=?|<=?|>=?|==?|!=|&&?|\|\|?|'
                        r'\+\+|--|!|[\+\-\*/%=\(\)\{\};,|]|\d+(?:\.\d*)?|\.\d+', line)
    return [token for token in tokens if token.strip()]


def remove_code(source, target):
    if target == '':
        return source
    else:
        _source = source.replace(target, '\n')
        return _source


def lines_eq_start(line1, line2):
    tokens1 = tokenize_c_code(line1)
    tokens2 = tokenize_c_code(line2)
    if tokens1 == tokens2:
        return True
    else:
        return False


def tokens_eq(tokens1, tokens2):
    if tokens1 == [] and tokens2 != []:
        return False
    elif tokens1 != [] and tokens2 == []:
        return False

    if tokens1 == tokens2:
        return True
    else:
        token_set1 = set(tokens1)
        token_set2 = set(tokens2)
        if (len(list(token_set1-token_set2)) + len(list(token_set2-token_set1)))/2 < 2:
            if len(tokens1) > 8 and len(tokens2) > 8:
                return True
            else:
                return False
        else:
            return False


def lines_eq_end(line1, line2, line3, line4, end_type, true_end_line):
    tokens1 = tokenize_c_code(line1)
    tokens2 = tokenize_c_code(line2)
    tokens3 = tokenize_c_code(line3)
    tokens4 = tokenize_c_code(line4)

    if tokens_eq(tokens1, tokens2) and tokens_eq(tokens3, tokens4):
        if end_type == 'out':
            return True
        elif end_type == 'in':
            if '}' in true_end_line:
                return True
    else:
        return False


def rm_none_line(line_list):
    _line_list = []
    for i, line in enumerate(line_list):
        if line != '':
            _line_list.append(line)
    
    return _line_list
