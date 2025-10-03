

class Definition:
    def __init__(self, name: str, pos: int, end: int):
        self.name = name
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"Definition(name={self.name}, pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, Definition):
            if self.name != other.name:
                return False
        else:
            return False

        return True


class Include:
    def __init__(self, value: str, pos: int, end: int):
        self.value = value
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"Include(value={self.value}, pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, Include):
            if self.value != other.value:
                return False
        else:
            return False

        return True


class IfDefNode:
    def __init__(self, condition: str, pos: int, end: int):
        self.condition = condition
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"IfDefNode(condition={self.condition}, pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, IfDefNode):
            if self.condition != other.condition:
                return False
        else:
            return False

        return True


class ElseDefNode:
    def __init__(self, pos: int, end: int):
        self.pos = pos
        self.end = end
    def __repr__(self):
        return f"ElseDefNode(pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, ElseDefNode):
            return True
        else:
            return False


class EndIfDefNode:
    def __init__(self, pos: int, end: int):
        self.pos = pos
        self.end = end
    def __repr__(self):
        return f"EndIfDefNode(pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, EndIfDefNode):
            return True
        else:
            return False


class FuncDecNode():
    def __init__(self, name: str, types: list, pos: int, end: int):
        self.name = name
        self.types = types
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"FuncDecNode(name={self.name}, types={self.types}, pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, FuncDecNode):
            if self.name == other.name:
                for t, _t in zip(self.types, other.types):
                    if t != _t:
                        return False
                return True
            else:
                return False
        else:
            return False


class ReturnNode:
    def __init__(self, value: str, inside_funccall, pos: int, end: int):
        self.value = value
        self.inside_funccall = inside_funccall
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"ReturnNode(value={self.value}, inside_funccall={self.inside_funccall}, pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, ReturnNode):
            if self.value != other.value:
                return False
        else:
            return False

        return True


class BreakNode:
    def __init__(self, pos: int, end: int):
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"Break(pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, BreakNode):
            return True
        else:
            return False


class ContinueNode:
    def __init__(self, pos: int, end: int):
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"Continue(pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, ContinueNode):
            return True
        else:
            return False


class GotoNode:
    def __init__(self, label: str, pos: int, end: int):
        self.label = label
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"Goto(label={self.label}, pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, GotoNode):
            if self.label == other.label:
                return True
            else:
                return False
        else:
            return False


class IfNode():
    def __init__(self, inside_funccall, pos: int, end: int) -> None:
        self.inside_funccall = inside_funccall
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"IfNode(inside_funccall={self.inside_funccall}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, IfNode):
            if self.inside_funccall == other.inside_funccall:
                return True
            else:
                return False
        else:
            return False


class ElseNode:
    def __init__(self, pos: int, end: int):
        self.pos = pos
        self.end = end
    def __repr__(self):
        return f"ElseNode(pos={self.pos}, end={self.end})"
    
    def __eq__(self, other):
        if isinstance(other, ElseNode):
            return True
        else:
            return False


class ForNode():
    def __init__(self, inside_funccall, pos: int, end: int):
        self.inside_funccall = inside_funccall
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"ForNode(inside_funccall={self.inside_funccall}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, IfNode):
            if self.inside_funccall == other.inside_funccall:
                return True
            else:
                return False
        else:
            return False


class WhileNode():
    def __init__(self, inside_funccall, pos: int, end: int):
        self.inside_funccall = inside_funccall
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"WhileNode(inside_funccall={self.inside_funccall}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, IfNode):
            if self.inside_funccall == other.inside_funccall:
                return True
            else:
                return False
        else:
            return False


class DoWhileNode():
    def __init__(self, inside_funccall, pos: int, end: int):
        self.inside_funccall = inside_funccall
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"DoWhileNode(inside_funccall={self.inside_funccall}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, DoWhileNode):
            if self.inside_funccall == other.inside_funccall:
                return True
            else:
                return False
        else:
            return False


class NormalNode():
    def __init__(self, inside_funccall, context: str, pos: int, end: int):
        self.inside_funccall = inside_funccall
        self.context = context
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"NormalNode(inside_funccall={self.inside_funccall}, context={self.context}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, NormalNode):
            if self.inside_funccall == other.inside_funccall:
                return True
            else:
                return False
        else:
            return False

    
class FunctionCall():
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"FunctionCall(name={self.name})"
    
    def __eq__(self, other):
        if isinstance(other, FunctionCall):
            if self.name != other.name:
                return False
            else:
                return True
        else:
            return False


class StructNode():
    def __init__(self, name: str, types: list, pos: int, end: int):
        self.name = name
        self.types = types
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"StructNode(name={self.name}, types={self.types}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, StructNode):
            if self.name != other.name:
                return False
            else:
                return False
        else:
            return False


class AnnotationNode():
    def __init__(self, context: str, pos: int, end: int):
        self.context = context
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"AnnotationNode(context={self.context}, pos={self.pos}, end={self.end})"


class ASMNode():
    def __init__(self, context: str, pos: int, end: int):
        self.context = context
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"ASMNode(context={self.context}, pos={self.pos}, end={self.end})"


class SwitchNode():
    def __init__(self, inside_funccall, pos: int, end: int):
        self.inside_funccall = inside_funccall
        self.pos = pos
        self.end = end

    def __repr__(self):
        return f"SwitchNode(inside_funccall={self.inside_funccall}, pos={self.pos}, end={self.end})"

    def __eq__(self, other):
        if isinstance(other, SwitchNode):
            if self.inside_funccall == other.inside_funccall:
                return True
            else:
                return False
        else:
            return False


class FieldDeclaration():
    def __init__(self, name: str, type):
        self.name = name
        self.type = type

    def __repr__(self):
        return f"FieldDeclaration(name={self.name}, type={self.type})"
    
    def __eq__(self, other):
        if isinstance(other, FieldDeclaration):
            if self.name != other.name:
                return False
            else:
                if other.type != self.type:
                    return False
        else:
            return False

        return True


class LabelNode:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"LabelNode(name={self.name})"