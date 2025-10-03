import distance
import argparse
import pandas as pd
from codebleu import calc_codebleu


def codebleu_match(reference, prediction, th=0.9, lang='c'):
    result = calc_codebleu([reference], [prediction], lang=lang, weights=(0.25, 0.25, 0.25, 0.25), tokenizer=None)
    code_bleu = result['codebleu']
    if code_bleu > th:
        return True  # clone
    else:
        return False # not clone


def best_match(code1, code2):
    clean_code1 = ''.join(code1.split())
    clean_code2 = ''.join(code2.split())
    edit_distance = distance.levenshtein(clean_code1, clean_code2)

    return edit_distance


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is migration task.')
    parser.add_argument('--metric', type=str, default='best', choices=['best', 'semantic'], help='The LLM chosen for use.')
    parser.add_argument('--data_path', type=str, default='data/data.csv', help='Data location.')
    parser.add_argument('--save_path', type=str, default='results', help='Select the storage location for the results.')
    parser.add_argument('--method', type=str, default='miggpt', choices=['miggpt', 'vanilla'], help='miggpt and vanilla method.')

    args = parser.parse_args()

    metric = args.metric
    data_path = args.data_path
    results_path = f'{args.save_path}/migration_{args.method}.csv'

    df = pd.read_csv(data_path)
    df2 = pd.read_csv(results_path)

    cnt = 0
    type1_match = 0
    type2_match = 0

    for index, row in df.iterrows():
        name_type = row['type']
        s_old = row['s_old']
        s_old_p = row['s_old_p']
        file_new = row['file_new']
        s_new_gt1 = row['s_new_gt1']
        s_new_gt2 = row['s_new_gt2']

        _, name_type2, s_old2, s_old_p2, file_new2, s_new_res, s_new_p_res = df2.iloc[index].values

        assert name_type == name_type2, 'error'
        assert s_old == s_old2, 'error'
        assert s_old_p == s_old_p2, 'error'
        assert file_new == file_new2, 'error'

        if s_new_res == 'none':
            assert s_new_p_res == 'none', 'error'
            cnt += 1
            continue
        else:
            if metric == 'best':
                distance_new = best_match(s_new_res, s_new_gt1)
                if distance_new == 0:
                    if name_type == 'type1':
                        type1_match += 1
                    elif name_type == 'type2':
                        type2_match += 1
                    else:
                        raise ValueError
                    cnt += 1
                    continue
                else:
                    distance_new2 = best_match(s_new_res, s_new_gt2)
                    if distance_new2 == 0:
                        if name_type == 'type1':
                            type1_match += 1
                        elif name_type == 'type2':
                            type2_match += 1
                        else:
                            raise ValueError
                    cnt += 1
                    continue
            elif metric == 'semantic':
                distance_new = codebleu_match(s_new_gt1, s_new_res)
                if distance_new:
                    if name_type == 'type1':
                        type1_match += 1
                    elif name_type == 'type2':
                        type2_match += 1
                    else:
                        raise ValueError
                    cnt += 1
                    continue
                else:
                    distance_new2 = codebleu_match(s_new_gt2, s_new_res)
                    if distance_new2:
                        if name_type == 'type1':
                            type1_match += 1
                        elif name_type == 'type2':
                            type2_match += 1
                        else:
                            raise ValueError
                    cnt += 1
                    continue
            else:
                raise ValueError

    assert cnt == 135, 'error'

    cnt_p = 0
    type1_match_p = 0
    type2_match_p = 0

    for index, row in df.iterrows():
        name_type = row['type']
        s_old = row['s_old']
        s_old_p = row['s_old_p']
        file_new = row['file_new']
        s_new_p_gt1 = row['s_new_p_gt1']
        s_new_p_gt2 = row['s_new_p_gt2']

        _, name_type2, s_old2, s_old_p2, file_new2, s_new_res, s_new_p_res = df2.iloc[index].values

        assert name_type == name_type2, 'error'
        assert s_old == s_old2, 'error'
        assert s_old_p == s_old_p2, 'error'
        assert file_new == file_new2, 'error'

        if s_new_res == 'none':
            assert s_new_p_res == 'none', 'error'
            cnt_p += 1
            continue
        else:
            if metric == 'best':
                distance_new_p = best_match(s_new_p_res, s_new_p_gt1)
                if distance_new_p == 0:
                    if name_type == 'type1':
                        type1_match_p += 1
                    elif name_type == 'type2':
                        type2_match_p += 1
                    else:
                        raise ValueError
                    cnt_p += 1
                    continue
                else:
                    distance_new_p2 = best_match(s_new_p_res, s_new_p_gt2)
                    if distance_new_p2 == 0:
                        if name_type == 'type1':
                            type1_match_p += 1
                        elif name_type == 'type2':
                            type2_match_p += 1
                        else:
                            raise ValueError
                    cnt_p += 1
                    continue
            elif metric == 'semantic':
                distance_new_p = codebleu_match(s_new_p_gt1, s_new_p_res)
                if distance_new_p:
                    if name_type == 'type1':
                        type1_match_p += 1
                    elif name_type == 'type2':
                        type2_match_p += 1
                    else:
                        raise ValueError
                    cnt_p += 1
                    continue
                else:
                    distance_new2 = codebleu_match(s_new_p_gt2, s_new_p_res)
                    if distance_new2:
                        if name_type == 'type1':
                            type1_match_p += 1
                        elif name_type == 'type2':
                            type2_match_p += 1
                        else:
                            raise ValueError
                    cnt_p += 1
                    continue
            else:
                raise ValueError

    assert cnt_p == 135, 'error'

    all_match = type1_match + type2_match
    all_match_p = type1_match_p + type2_match_p

    print('============================================================================')
    print(f'{metric} match of s_new code: {all_match}/135={all_match/135.}')
    print(f'type1: {type1_match}/80={type1_match/80.}')
    print(f'type2: {type2_match}/55={type2_match/55.}')
    print('============================================================================')
    print(f'{metric} match of s_new_p code: {all_match_p}/135={all_match_p/135.}')
    print(f'type1: {type1_match_p}/80={type1_match_p/80.}')
    print(f'type2: {type2_match_p}/55={type2_match_p/55.}')

