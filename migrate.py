import argparse
import pandas as pd
from utils import restriction_prompt, query, get_code_with_markdown
from cfp_utils import build_cfp, get_diff_part


def migration(part_old, part_old_patched, part_new, context, llm='gpt-4-turbo', method='miggpt'):
    task_prompt = 'I am reaching out to you with a specialized code migration task where your expertise in Linux kernel development would be invaluable. Your assistance will help ensure the successful adaptation of existing code to the latest version of the Linux kernel. For this task, I will provide three code snippets for your consideration:\n'
    code_old_prompt = f'Code Snippet 1: The old version of the Linux kernel code snippet, which we will refer to as `part_old`.\n```\n{part_old}\n```\n'
    code_old_patched_prompt = f'Code Snippet 2: The corresponding code developed based on the old version of the Linux kernel code snippet `part_old`, referred to as `part_old_patched`.\n```\n{part_old_patched}\n```\n'
    code_new_prompt = f'Code Snippet 3: The new version of the Linux kernel code snippet, denoted as `part_new`.\n```\n{part_new}\n```\n'
    query_prompt = 'It\'s likely that similar adjustments will need to be made within `part_new` to maintain functionality and compatibility. Given your extensive knowledge and experience in this field, could you kindly assist by generating the corresponding code snippet `part_new_patched` developed on `part_new`?'
    
    if method == 'vanilla':
        prompt = task_prompt + code_old_prompt + code_old_patched_prompt + code_new_prompt + query_prompt + restriction_prompt
    elif method == 'miggpt':
        analysis_prompt = f'Upon preliminary analysis, it appears that there is {len(context)} specific area within `part_old_patched` that requires modification:\n'
        for idx, (diff_string, top_string, bottom_string) in enumerate(context):
            if top_string != '':
                top_mod = f'situated after the line containing \n```\n{top_string}\n```\n'
            else:
                top_mod = ''

            if bottom_string != '':
                if top_mod != '':
                    bottom_mod = f', and before the line containing \n```\n{bottom_string}\n```\n'
                else:
                    bottom_mod = f'before the line containing \n```\n{bottom_string}\n```\n'
            else:
                bottom_mod = ''
            
            analysis_prompt = analysis_prompt + f'The modification {idx+1} should be made {top_mod}{bottom_mod} with the change being \n```\n{diff_string}\n```\n'  
        prompt = task_prompt + code_old_prompt + code_old_patched_prompt + code_new_prompt + analysis_prompt + query_prompt + restriction_prompt
    else:
        raise ValueError

    response = query(user_content=prompt, query_model=llm, temperature=0.4)
    response_code = get_code_with_markdown(response)

    return response_code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is migration task.')
    parser.add_argument('--llm', type=str, default='gpt-4-turbo', help='The LLM chosen for use.')
    parser.add_argument('--data_path', type=str, default='data/data.csv', help='Data location.')
    parser.add_argument('--save_path', type=str, default='results', help='Select the storage location for the results.')
    parser.add_argument('--method', type=str, default='miggpt', choices=['miggpt', 'vanilla'], help='miggpt and vanilla method.')

    args = parser.parse_args()

    model = args.llm
    data_path = args.data_path
    method = args.method
    retrieval_results_path = f'{args.save_path}/retrieval_{method}.csv'
    save_path = f'{args.save_path}/migration_{method}.csv'

    results_list = []
    df = pd.read_csv(data_path)
    df2 = pd.read_csv(retrieval_results_path)

    for index, row in df.iterrows():
        name_type = row['type']
        s_old = row['s_old']
        file_new = row['file_new']
        s_old_p = row['s_old_p']

        _, name_type2, s_old2, file_new2, s_new_res = df2.iloc[index].values

        assert name_type == name_type2, 'error'
        assert s_old == s_old2, 'error'
        assert file_new == file_new2, 'error'

        if s_new_res == 'none':
            s_new_p_res = 'none'
        else:
            cfp_s_old = build_cfp(s_old)
            cfp_s_old_p = build_cfp(s_old_p)
            mod_context = get_diff_part(cfp_s_old, cfp_s_old_p, s_old_p)
            s_new_p_res = migration(s_old, s_old_p, s_new_res, mod_context, llm=model, method=method)

        results_list.append((name_type, s_old, s_old_p, file_new, s_new_res, s_new_p_res))
        break

    df = pd.DataFrame(results_list, columns=['type', 's_old', 's_old_p', 'file_new', 's_new_res', 's_new_p_res'])
    df.to_csv(save_path, index=True)

