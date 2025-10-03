import argparse
import os
import pandas as pd
from utils import restriction_prompt, query, get_code_with_markdown, find_context, lines_eq_start, lines_eq_end, rm_none_line
from fp_utils import build_cfp, collect_all_function_call_names, collect_all_function_def_names, anchor, tokenize_c_code


def get_new_block(part_old, code_new, name_list=[], range_anchor=[], llm='gpt-4-turbo', tmp_query_time=None, method='miggpt', m=3):
    # query LLM
    task_prompt = 'We are facing a challenge that requires your specialized knowledge and expertise. We need to locate a corresponding segment of code, indicated as `part_new`, within a C file named `new.c` that matches semantically with a provided code snippet labeled as `part_old`. Given that `part_new`, the target code segment, originates from modifications made to `part_old`, it is essential to identify this correspondence accurately.\n'
    prompt_part_old = f'The starting point for your task involves comparing the following `part_old`: \n```\n{part_old}\n```\n'
    prompt_code_new = f'And the entire context available in the `new.c`: \n```\n{code_new}\n```\n'
    if method == 'vanilla':
        prompt = task_prompt + prompt_part_old + prompt_code_new + restriction_prompt

    elif method == 'miggpt':
        if len(name_list) == 0:
            prompt_fuc_def = ''
        else:
            feature_list = []
            for name, types in name_list:
                _name = types
                _name.append(name)
                func_def_features = ' '.join(_name)
                feature_list.append(func_def_features)
                feature = ', '.join(feature_list)
            
            prompt_fuc_def = f'It appears that `part_old` encompasses the definition of the function `{feature}`. Your role is to pinpoint the matching code segment `part_new` within `new.c`. Please ensure that the identified function definitions are solely derived from `new.c`. Avoid constructing false code snippets by using the function definitions from `part_old`.\n'
        if len(range_anchor) == 0:
            prompt_align = ''
        else:
            prompt_align = f'To facilitate the search, you may need to align `part_new` using the initial line `{range_anchor[0]}` and the final line `{range_anchor[1]}` from `part_old`.\n'
        prompt = task_prompt + prompt_part_old + prompt_code_new + prompt_fuc_def + prompt_align + restriction_prompt
    else:
        raise ValueError

    response = query(user_content=prompt, query_model=llm, temperature=0.5)
    response_code = get_code_with_markdown(response)
 
    tmp_query_time += 1

    interact_list = []
    response_code_lines = response_code.splitlines()
    find_name = []
    for name, types in name_list:
        for line in response_code_lines:
            tokens = tokenize_c_code(line)
            if name in tokens:
                for t in types:
                    if t in tokens:
                        find_name.append((name, types))
                        break
    for item in name_list:
        if item not in find_name:
            interact_list.append(item)

    code_new_lines = code_new.splitlines()

    if len(interact_list) != 0:
        fp_tmp_part_new = build_cfp(response_code)
        tmp_funcdef_list = collect_all_function_def_names(fp_tmp_part_new)
        
        tmp_list = []
        for tmp_feature, _ in tmp_funcdef_list:
            tmp_list.append(tmp_feature)

        rm_context = find_context(tmp_list, code_new, out_type='idx')
        tmp_code_new_lines = []

        for idx, line in enumerate(code_new_lines):
            for tmp_s, tmp_e in rm_context:
                if not (idx>=tmp_s and idx<=tmp_e):
                    tmp_code_new_lines.append(line)
        tmp_code_new = '\n'.join(tmp_code_new_lines)
        tmp_response_code = response_code

        query_time = 0

        while len(interact_list) > 0 and query_time <= m:
            _prompt_code_new = f'Here is the code of `new.c`: \n```\n{tmp_code_new}\n```\n'
            _prompt = task_prompt + prompt_part_old + _prompt_code_new + prompt_fuc_def + prompt_align + restriction_prompt

            response = query(user_content=_prompt, query_model=llm, temperature=0.4)
            response_code = get_code_with_markdown(response)
            tmp_query_time += 1
            if response_code is None:
                response_code = tmp_response_code
                print('Back to last')
                break

            interact_list = []
            response_code_lines = response_code.splitlines()
            find_name = []
            for name, types in name_list:
                for line in response_code_lines:
                    if name in line:
                        for t in types:
                            if t in line:
                                find_name.append((name, types))
                                break
            for item in name_list:
                if item not in find_name:
                    interact_list.append(item)
            if len(interact_list) == 0:
                break
            else:
                fp_tmp_part_new = build_cfp(response_code)
                tmp_funcdef_list = collect_all_function_def_names(fp_tmp_part_new)
                
                tmp_list = []
                for tmp_feature, _ in tmp_funcdef_list:
                    tmp_list.append(tmp_feature)
                
                rm_context = find_context(tmp_list, code_new, out_type='idx')
                
                _tmp_code_new_lines = []

                for idx, line in enumerate(tmp_code_new_lines):
                    for tmp_s, tmp_e in rm_context:
                        if not (idx>=tmp_s and idx<=tmp_e):
                            _tmp_code_new_lines.append(line)
                tmp_code_new = '\n'.join(_tmp_code_new_lines)
                tmp_response_code = response_code

            query_time += 1

    response_code_lines = response_code.splitlines()
    start = -1
    end = -1
    start_add = 0
    end_add = 0
    
    if '}' in response_code_lines[-1] and '{' not in response_code_lines[-1]:
        if '}' in response_code_lines[-2]:
            end_line = response_code_lines[-3]
            end_line_up = response_code_lines[-4]
            add_lo = 2
            if end_line == ' */':
                end_add = 1
                end_line = response_code_lines[-4]
                end_line_up = response_code_lines[-3]
        else:
            end_line = response_code_lines[-2]
            end_line_up = response_code_lines[-3]
            add_lo = 1
            if end_line == ' */':
                end_add = 1
                end_line = response_code_lines[-3]
                end_line_up = response_code_lines[-4]
        end_type = 'in'
    else:
        end_line = response_code_lines[-1]
        end_line_up = response_code_lines[-2]
        end_type = 'out'
        add_lo = 0
        if end_line == ' */':
            end_add = 1
            end_line = response_code_lines[-2]
            end_line_up = response_code_lines[-3]
    
    if response_code_lines[0] == '/*':
        start_line = response_code_lines[1]
        start_add = -1
    else:
        start_line = response_code_lines[0]

    for idx, line in enumerate(code_new_lines):
        if lines_eq_start(line, start_line):
            start = idx
        else:
            if start != -1:
                if idx + add_lo < len(code_new_lines):
                    if lines_eq_end(line, end_line, code_new_lines[idx-1], end_line_up, end_type, code_new_lines[idx + add_lo]):
                        if end_type == 'in':
                            end = idx + add_lo
                            break
                        elif end_type == 'out':
                            end = idx
                            break

    if start != -1:
        if end != -1:
            response_code = '\n'.join(code_new_lines[start+start_add:end+1+end_add])
            return response_code, True, tmp_query_time
        else:
            print('Not Found 1')
            return response_code, False, tmp_query_time
    else:
        print('Not Found 2')
        return response_code, False, tmp_query_time


def add_extra_code(part_new, fp_part_old, code_new):
    fp_part_new = build_cfp(part_new)

    part_old_funccall = set(collect_all_function_call_names(fp_part_old))
    part_new_funccall = set(collect_all_function_call_names(fp_part_new))
    new_funccall_list = list(part_new_funccall - part_old_funccall)
    
    add_context = find_context(new_funccall_list, code_new)

    if len(add_context) != 0:
        print('add extra code...')
        add_context_string = '\n'.join(add_context) 
        part_new = f'{add_context_string}\n\n{part_new}'
    
    return part_new


def more_align(part_new, part_old):
    part_new_lines = part_new.splitlines()
    part_old_lines = rm_none_line(part_old.splitlines())
    start = -1
    end = -1

    for idx, line in enumerate(part_new_lines):
        if lines_eq_start(line, part_old_lines[0]):
            start = idx
            break
    if start == -1:
        return part_new

    if part_old_lines[-1] == '}':
        for idx, line in enumerate(reversed(part_new_lines)):
            if line == '}':
                end = len(part_new_lines) - idx - 1
                break
    else:
        for idx, line in enumerate(reversed(part_new_lines)):
            if lines_eq_start(line, part_old_lines[-1]):
                end = len(part_new_lines) - idx - 1
                break
    if end == -1:
        return part_new
    
    _part_new = '\n'.join(part_new_lines[start:end+1])

    return _part_new


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is retrieval task.')
    parser.add_argument('--m', type=int, default=3, help='Hyperparameter m')
    parser.add_argument('--llm', type=str, default='gpt-4-turbo', help='The LLM chosen for use.')
    parser.add_argument('--data_path', type=str, default='data/data.csv', help='Data location.')
    parser.add_argument('--save_path', type=str, default='results', help='Select the storage location for the results.')
    parser.add_argument('--method', type=str, default='miggpt', choices=['miggpt', 'vanilla'], help='miggpt and vanilla method.')

    args = parser.parse_args()

    m = args.m
    model = args.llm
    data_path = args.data_path
    method = args.method
    os.makedirs(args.save_path, exist_ok=True)
    save_path = f'{args.save_path}/retrieval_{method}.csv'

    results_list = []
    df = pd.read_csv(data_path)

    for index, row in df.iterrows():
        name_type = row['type']
        s_old = row['s_old']
        file_new = row['file_new']

        cfp_s_old = build_cfp(s_old)
        funcdef_list = collect_all_function_def_names(cfp_s_old)
        part_anchor = anchor(cfp_s_old)

        s_new_res, found, all_query_time = get_new_block(part_old=s_old, code_new=file_new, name_list=funcdef_list, 
                                    range_anchor=part_anchor, llm=model, tmp_query_time=0, method=method, m=m)
        
        if found:
            s_new_res = more_align(s_new_res, s_old)
            s_new_res = add_extra_code(s_new_res, cfp_s_old, file_new)

            results_list.append((name_type, s_old, file_new, s_new_res))
        else:
            print('Not found! You can try agian.')
            results_list.append((name_type, s_old, file_new, 'none'))
        
        break
    
    df = pd.DataFrame(results_list, columns=['type', 's_old', 'file_new', 's_new_res'])
    df.to_csv(save_path, index=True)
                
