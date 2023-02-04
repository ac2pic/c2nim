from pycparser import c_ast

def raise_(ex):
    raise ex

class C2NimGenerator(object):
    def __init__(self, filepath):
        self.filepath = filepath
        pass

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        generic_visit = lambda node: '' if node is None else raise_(Exception(method + ' is not implemented'))
        return getattr(self, method, generic_visit)(node) 

    def visit_FileAST(self, node):
        s = ''
        for ext in node.ext:
            if ext.coord.file != self.filepath:
                continue
            result = self.visit(ext)
            s += result + '\n'
        return s

    def visit_Typedef(self, node):
        print(node)
        return ''


    def visit_IdentifierType(self, node):
        translated_names = []
        for name in node.names:
            if name == "int":
                translated_names.append("cint")
            elif name == "char":
                translated_names.append("cchar")
            else:
                translated_names.append(name)
        return ' '.join(translated_names)

    def visit_Struct(self, _):
        return ""

    def visit_ParamList(self, node):
        params = []
        i = 0
        for param in node.params:
            typ = self._generate_type(param, [node])
            typ = typ.format("param" + str(i))
            i += 1
            params.append(typ)
        return ', '.join(params)

    def visit_Decl(self, node):
        return self._generate_type(node.type, [node])

    def visit_Typename(self, node):
        return self._generate_type(node.type)

    def visit_TypeDecl(self, node):
        return self._generate_type(node, emit_declname=False)

    def visit_PtrDecl(self, node):
        return self._generate_type(node, emit_declname=False)
    
    def visit_FuncDecl(self, node):
        return self._generate_type(node)

    def _generate_type(self, node, parents=[], emit_declname=True):
        node_type = type(node)
        if node_type == c_ast.TypeDecl:
            parents.append(node)
            return self._generate_decl(parents)
        elif node_type == c_ast.Decl:
            return self._generate_type(node.type, parents + [node], emit_declname)
        elif node_type == c_ast.Typename:
            return self._generate_type(node.type, parents + [node], emit_declname)
        elif node_type in (c_ast.PtrDecl, c_ast.FuncDecl):
            return self._generate_type(node.type, parents + [node], emit_declname)
        return ''

    def _generate_decl(self, parents):
        if len(parents) == 0:
            return ""
        typ = self._detect_decltype(parents)
        if typ == "proc":
            return self._generate_procdecl(parents)
        elif typ == "let":
            return self._generate_letdecl(parents)
        elif typ == "var":
            return self._generate_vardecl(parents)
        elif typ == "param":
            return self._generate_paramdecl(parents)
        return ""

    def _generate_paramdecl(self, parents):
        param_name = parents[1].name or "{}"
        param_type = self._generate_ret_type((parents[2:]))
        return "{}: {}".format(param_name, param_type)

    def _generate_procdecl(self, parents):
        proc_name = parents[0].name
        proc_args = self.visit(parents[1].args)
        proc_ret = self._generate_ret_type(parents[2:])
        if proc_ret == "void":
            proc_ret = ""

        if len(proc_ret):
            proc_ret = " : " + proc_ret

        return "proc {}({}){}".format(proc_name, proc_args, proc_ret)

    
    def _generate_ret_type(self, rets):
        # C constants are not directly translatable
        rettype_code = []
        for i, ret in enumerate(rets):
            if isinstance(ret, c_ast.PtrDecl):
                rettype_code.append("ptr")
            elif isinstance(ret, c_ast.TypeDecl):
                type_val = self.visit(ret.type)
                if len(rettype_code) > 0 and rettype_code[-1] == "ptr":
                    if type_val == "void":
                        rettype_code.pop()
                        rettype_code.append("pointer")
                    elif type_val == "cchar":
                        rettype_code.append("cstring")
                    else:
                        rettype_code.append(type_val)
                else:
                    rettype_code.append(type_val)
            elif isinstance(ret, c_ast.FuncDecl):
                proc_args = self.visit(ret.args)
                proc_ret = self._generate_ret_type(rets[i+1:])
                if i != 0 and isinstance(rets[i - 1], c_ast.PtrDecl):
                    rettype_code.pop()
                include_paren = i > 1
                code = "proc ({}): {}".format(proc_args, proc_ret)

                if include_paren:
                    code = "(" + code + ")"
                rettype_code.append(code)
                break
        return ' '.join(rettype_code)

    def _generate_vardecl(self, parents):
        var_name = parents[0].name
        var_type = self._generate_ret_type((parents[1:]))
        return "var {}: {}".format(var_name, var_type)

    def _generate_letdecl(self, _):
        return ""

    def _detect_decltype(self, parents):
        if len(parents) == 0:
            return ""
        if isinstance(parents[0], c_ast.ParamList):
            return "param"

        if isinstance(parents[0], c_ast.Decl):
            if isinstance(parents[1], c_ast.FuncDecl):
                return "proc"
            if 'const' in parents[0].quals:
                return "let"
            return "var"
        return ""
