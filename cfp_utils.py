from node_types import *
import re


def tokenize_c_code(line):
    tokens = re.findall(r'#[a-zA-Z_]\w*|<[a-zA-Z0-9_./]*>|[a-zA-Z_]\w*|'
                        r'[\+\-\*/%]=|<<=?|>>=?|<=?|>=?|==?|!=|&&?|\|\|?|'
                        r'\+\+|--|!|[\+\-\*/%=\(\)\{\};,|]|\d+(?:\.\d*)?|\.\d+', line)
    return [token for token in tokens if token.strip()]


def is_function_declaration(tokens):
    for ll in ['if', 'while', 'for', 'while', 'switch']:
        if ll in tokens:
            return False
    
    if ';' == tokens[-1]:
        return False

    feature_list = ['extern', 'static', 'inline', 'void', 'long', 'int', 'float', 'double', 'char', 'enum']
    left = -1
    for ii, token in enumerate(tokens):
        if token == '(':
            left = ii
            break

    feature_tokens = tokens[:left]
    if left == -1:
        return False
    for feature in feature_list:
        if feature in feature_tokens:
            return True
    
    return False


def cnt_bracket(token):
    right = 0
    left = 0
    for t in token:
        if t == '(':
            right += 1
        elif t == ')':
            left += 1
    return left, right


def find_funccall(tokens):
    funccalls = []
    for idx, token in enumerate(tokens[:-1]):
        if tokens[idx+1] == '(':
            if token not in ['for', 'if', 'while', 'do', '(', '||', '==', '&&', '|', '&', '!', ',', '*', ')']:
                funccalls.append(FunctionCall(token))
    return funccalls


def parse_tokens(tokens, start, end, code_lines):
    if tokens[0] == '#include':
        include_value = tokens[1]
        return Include(include_value, pos=start, end=end)
    
    elif tokens[0] == '#define':
        name = tokens[1]
        return Definition(name, pos=start, end=end)
    
    elif tokens[0] == '#ifdef':
        condition = tokens[1]
        return IfDefNode(condition, pos=start, end=end)
    
    elif tokens[0] == '#else':
        return ElseDefNode(pos=start, end=end)
    
    elif tokens[0] == '#endif':
        return EndIfDefNode(pos=start, end=end)
    
    elif is_function_declaration(tokens):
        for i, token in enumerate(tokens):
            if token == '(':
                name = tokens[i-1]
                types = tokens[:i-1]
        return FuncDecNode(name, types, pos=start, end=end)
    
    elif tokens[0] == 'return':
        inside_funccall = find_funccall(tokens)
        return ReturnNode(value=tokens[1:], inside_funccall=inside_funccall, pos=start, end=end)
    
    elif tokens[0] == 'break':
        return BreakNode(pos=start, end=end)
    
    elif tokens[0] == 'continue':
        return ContinueNode(pos=start, end=end)
    
    elif tokens[0] == 'goto':
        return GotoNode(tokens[1:], pos=start, end=end)
    
    elif tokens[0] == 'if':
        inside_funccall = find_funccall(tokens)
        return IfNode(inside_funccall, pos=start, end=end)
    
    elif 'else' in tokens and '#else' not in tokens:
        return ElseNode(pos=start, end=end)
    elif tokens[0] == 'for':
        inside_funccall = find_funccall(tokens)
        return ForNode(inside_funccall, pos=start, end=end)
    
    elif tokens[0] == 'while':
        inside_funccall = find_funccall(tokens)
        return WhileNode(inside_funccall, pos=start, end=end)
    
    elif tokens[0] == 'do' in tokens:
        target_line = code_lines[end-1]
        _tokens = tokenize_c_code(target_line)
        assert 'while' in _tokens, 'error'
        inside_funccall = find_funccall(_tokens)
        return DoWhileNode(inside_funccall, pos=start, end=end)
    
    elif 'struct' in tokens[:2]:
        ii = tokens.index('struct')
        name = tokens[ii+1]
        types = tokens[:ii]
        return StructNode(name, types, pos=start, end=end)
    
    elif tokens[0] == '/':
        context = code_lines[start-1:end]
        return AnnotationNode(context=''.join(context), pos=start, end=end)
    
    elif tokens[0] == 'asm':
        context = code_lines[start-1:end]
        return ASMNode(''.join(context), pos=start, end=end)
    
    elif tokens[0] == 'switch':
        inside_funccall = find_funccall(tokens)
        return SwitchNode(inside_funccall, pos=start, end=end)

    else:
        inside_funccall = find_funccall(tokens)
        context = code_lines[start-1:end]
        return NormalNode(inside_funccall, context=''.join(context), pos=start, end=end)
    

def find_end_idx(end_idx, tokens, code_lines):
    if tokens[0] == '#ifdef':
        for idx in range(end_idx, len(code_lines)):
            if '#endif' in tokenize_c_code(code_lines[idx]):
                _end_idx = idx
                break
            else:
                _end_idx = idx
    
    elif tokens[0] == '#else':
        for idx in range(end_idx, len(code_lines)):
            if '#endif' in tokenize_c_code(code_lines[idx]):
                _end_idx = idx
                break
            else:
                _end_idx = idx
    
    elif is_function_declaration(tokens[0]):
        for idx in range(end_idx, len(code_lines)):
            _tokens = tokenize_c_code(code_lines[idx])
            if len(_tokens) == 0 and _tokens[0] == '}':
                _end_idx = idx
                break
    
    elif tokens[0] in ['if', 'else', 'for', 'while', 'switch']:
        if '{' in tokens:
            for idx in range(end_idx, len(code_lines)):
                _tokens = tokenize_c_code(code_lines[idx])
                if len(_tokens) == 0:
                        continue
                if '}' in _tokens[0]:
                    _end_idx = idx
                    break
        else:
            _end_idx = end_idx + 1
    
    elif tokens[0] in ['do']:
        if '{' in tokens:
            for idx in range(end_idx, len(code_lines)):
                _tokens = tokenize_c_code(code_lines[idx])
                if len(_tokens) == 0:
                        continue
                if '}' in _tokens[0] and 'while' in _tokens:
                    _end_idx = idx
                    break
        else:
            _end_idx = end_idx + 1
    
    elif tokens[0] == '/':
        if tokens[1] == '*':
            if tokens[-1] == '/' and tokens[-2] == '*':
                _end_idx = end_idx
            else:
                for idx in range(end_idx, len(code_lines)):
                    _tokens = tokenize_c_code(code_lines[idx])
                    if len(_tokens) < 2:
                        continue
                    elif _tokens[-1] == '/' and _tokens[-2] == '*':
                        _end_idx = idx
                        break
                    else:
                        if _tokens[0] == '*' and _tokens[1] == '/':
                            _end_idx = idx
                            break
        else:
            _end_idx = end_idx
            for idx in range(end_idx, len(code_lines)):
                _tokens = tokenize_c_code(code_lines[idx])
                if len(_tokens) < 3:
                    break
                else:
                    if _tokens[0] == '/' and _tokens[1] == '/':
                        _end_idx = idx
                    else:
                        break

    else:
        _end_idx = end_idx
    
    return _end_idx


def build_cfp(code):
    code_lines = code.splitlines()
    parsed_lines = []
    half_line = -1
    for idx, line in enumerate(code_lines):
        # print(f'================================== line {idx+1}  ==================================')
        # print(line)
        tokens = tokenize_c_code(line)
        # print(tokens)
        if len(tokens) == 0:
            continue
        elif tokens == ['{'] or tokens == ['}']:
            continue
        elif half_line >= idx+1:
            if half_line == idx+1:
                half_line = -1
            continue
        elif '}' in tokens and 'while' in tokens and tokens.index('}') < tokens.index('while'):
            continue
        elif tokens[0] == '*':
            if len(tokens) == 1:
                continue
            if line[line.find('*')-1] == ' ':
                continue
        
        left_bracket_num, right_bracket_num = cnt_bracket(tokens)
        if left_bracket_num == right_bracket_num:
            end_idx = find_end_idx(idx, tokens, code_lines)
            parsed_line = parse_tokens(tokens, idx+1, end_idx+1, code_lines)
        else:
            all_left_bracket_num = left_bracket_num
            all_right_bracket_num = right_bracket_num
            all_tokens = tokens
            end_idx = -1
            for s_idx in range(idx+1, len(code_lines)):
                sub_tokens = tokenize_c_code(code_lines[s_idx])
                sub_left_bracket_num, sub_right_bracket_num = cnt_bracket(sub_tokens)
                all_left_bracket_num += sub_left_bracket_num
                all_right_bracket_num += sub_right_bracket_num
                for el in sub_tokens:
                    all_tokens.append(el)
                if all_left_bracket_num == all_right_bracket_num:
                    end_idx = s_idx
                    half_line = end_idx+1
                    break
            assert end_idx != -1, 'error'
            end_idx = find_end_idx(end_idx, all_tokens, code_lines)
            parsed_line = parse_tokens(all_tokens, idx+1, end_idx+1, code_lines)
        # print(parsed_line)
        parsed_lines.append(parsed_line)

    return parsed_lines


def collect_all_function_call_names(fp):
    result = []
    for node in fp:
        if hasattr(node, 'inside_funccall'):
            for fuccall in node.inside_funccall:
                result.append(fuccall.name)

    return result


def collect_all_function_def_names(fp):
    result = []
    for node in fp:
        if isinstance(node, FuncDecNode):
            result.append((node.name, node.types))

    return result


def get_string(node):
    if isinstance(node, Include):
        string = f'#include {node.value}'

    elif isinstance(node, Definition):
        string = f'#define {node.name}'

    elif isinstance(node, IfDefNode):
        string = f'#ifndef {node.condition}'

    elif isinstance(node, EndIfDefNode):
        string = f'#endif'

    elif isinstance(node, AnnotationNode):
        string = f'{node.context}'
    
    elif isinstance(node, NormalNode):
        string = f'{node.context}'
    
    elif isinstance(node, FuncDecNode):
        per = ' '.join(node.types)
        string = f'{per} {node.name}'
    
    elif isinstance(node, StructNode):
        per = ' '.join(node.types)
        string = f'{per} struct {node.name}'
        
    else:
        string = ''

    return string


def anchor(fp):
    start_string = get_string(fp[0])
    end_string = get_string(fp[-1])
        
    return [start_string, end_string]
    


def get_diff_part(fp_part_old, fp_part_old_patched, code_old_patched):
    code_lines = code_old_patched.splitlines()
    target_node = []
    target_node_patched = []
    for idx, node in enumerate(fp_part_old):
        if isinstance(node, IfDefNode):
            target_node.append((idx, node, node.condition))

    for idx, node in enumerate(fp_part_old_patched):
        if isinstance(node, IfDefNode):
            target_node_patched.append((idx, node, node.condition))

    third_elements_old = set([item[2] for item in target_node])
    third_elements_old_patched = set([item[2] for item in target_node_patched])
    difference = third_elements_old_patched - third_elements_old
    result = [item for item in target_node_patched if item[2] in difference]
    diff = []
    for ii, res, _ in result:
        if ii > 0:
            top = code_lines[fp_part_old_patched[ii-1].pos-1:fp_part_old_patched[ii-1].end]
        else:
            top = ''
        
        if ii+1 < len(fp_part_old_patched):
            for jj in range(ii+1, len(fp_part_old_patched)):
                if isinstance(fp_part_old_patched[jj], EndIfDefNode):
                    if jj+1 < len(fp_part_old_patched):
                        bottom_node = fp_part_old_patched[jj+1]
                        bottom = code_lines[bottom_node.pos-1:bottom_node.end]
                    else:
                        bottom = ''
                    break
        else:
            bottom = ''

        target_code = code_lines[res.pos-1:res.end]
        diff.append(('\n'.join(target_code), '\n'.join(top), '\n'.join(bottom)))

    return diff
