import os
import shutil
import datetime
import platform
import getpass
import subprocess
import time
import random
import ast
import operator
import re

RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
WHITE = "\033[97m"

class Therapist:
    def __init__(self):
        self.topics = {
            "mood": {
                "question": "How are you feeling today?",
                "followups": [
                    "Can you tell me why you feel that way?",
                    "What could make your day better?",
                    "How does that affect your usual routine?"
                ]
            },
            "support": {
                "question": "Do you feel supported by those around you?",
                "followups": [
                    "Who do you usually rely on?",
                    "How does it feel when support is missing?",
                    "Have you tried talking to them about it?"
                ]
            },
            "stress": {
                "question": "How do you usually relax after a stressful day?",
                "followups": [
                    "What helps you the most when you're stressed?",
                    "Do you feel your relaxation methods work well?",
                    "Have you tried anything new recently to unwind?"
                ]
            },
            "happy_moment": {
                "question": "Can you describe a moment that made you happy recently?",
                "followups": [
                    "What made that moment special?",
                    "Who were you with?",
                    "Would you like to have more moments like that?"
                ]
            }
        }

        self.positive_keywords = ["happy", "good", "great", "excited", "fun", "awesome", "amazing", "joy"]
        self.negative_keywords = ["sad", "bad", "tired", "angry", "stressed", "upset", "frustrated", "unhappy"]

        self.generic_positive_responses = [
            "That's wonderful to hear!",
            "Wow, that sounds really uplifting!",
            "I'm glad you experienced that!"
        ]
        self.generic_negative_responses = [
            "I hear you, that sounds tough.",
            "That must be difficult to handle.",
            "I'm sorry you're going through that."
        ]
        self.generic_neutral_responses = [
            "I see. Can you tell me more?",
            "Hmm, I understand. Go on.",
            "Thanks for sharing. How does that make you feel?"
        ]

    def start(self):
        print("Therapist session started. Type ':wd' to exit anytime.\n")
        topic_keys = list(self.topics.keys())
        random.shuffle(topic_keys)

        for topic in topic_keys:
            question = self.topics[topic]["question"]
            quit_flag = self.ask_question_loop(question, list(self.topics[topic]["followups"]))
            if quit_flag:
                print("Therapist: Session ended. Take care!")
                return
        print("Therapist: Session ended. Take care!")

    def ask_question_loop(self, question, followups):
        while True:
            print(f"Therapist: {question}")
            response = input("You: ").strip()
            if response.lower() == ":wd":
                return True
            if not response:
                print("Therapist: It's okay, take your time to answer.")
                continue
            self.react(response)
            if followups:
                question = random.choice(followups)
                followups.remove(question)
            else:
                break
            print()
        return False

    def react(self, user_input):
        user_input_lower = user_input.lower()
        if any(word in user_input_lower for word in self.positive_keywords):
            print(f"Therapist: {random.choice(self.generic_positive_responses)}")
        elif any(word in user_input_lower for word in self.negative_keywords):
            print(f"Therapist: {random.choice(self.generic_negative_responses)}")
        else:
            print(f"Therapist: {random.choice(self.generic_neutral_responses)}")
class _SafeEval(ast.NodeVisitor):
    def __init__(self):
        # Standard operators
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,

            ast.Eq: operator.eq,
            ast.NotEq: operator.ne,
            ast.Lt: operator.lt,
            ast.LtE: operator.le,
            ast.Gt: operator.gt,
            ast.GtE: operator.ge,

            ast.And: lambda a, b: a and b,
            ast.Or: lambda a, b: a or b,
            ast.Not: operator.not_,

            ast.BitOr: operator.or_,
            ast.BitAnd: operator.and_,
            ast.BitXor: operator.xor,
            ast.Invert: operator.invert,
            ast.LShift: operator.lshift,
            ast.RShift: operator.rshift,
        }

        # Lumen custom operators
        self.lumen_ops = {
            '!|': lambda a, b: not (a or b),  # NOR
            '!&': lambda a, b: not (a and b),  # NAND
            '>|<': lambda a, b: (a and not b) or (not a and b),  # XOR
            '<&>': lambda a, b: (a and b) or (not a and not b)  # XAND
        }

    def visit(self, node):
        if isinstance(node, ast.Expression):
            return self.visit(node.body)
        elif isinstance(node, ast.BinOp):
            left = self.visit(node.left)
            right = self.visit(node.right)
            op_type = type(node.op)
            if op_type in self.operators:
                return self.operators[op_type](left, right)
            raise ValueError(f"Unsupported binary operator: {op_type}")
        elif isinstance(node, ast.BoolOp):
            values = [self.visit(v) for v in node.values]
            op_type = type(node.op)
            if op_type == ast.And:
                return all(values)
            elif op_type == ast.Or:
                return any(values)
            raise ValueError(f"Unsupported boolean operator: {op_type}")
        elif isinstance(node, ast.UnaryOp):
            operand = self.visit(node.operand)
            op_type = type(node.op)
            if op_type in self.operators:
                return self.operators[op_type](operand)
            raise ValueError(f"Unsupported unary operator: {op_type}")
        elif isinstance(node, ast.Compare):
            left = self.visit(node.left)
            for op, right_node in zip(node.ops, node.comparators):
                right = self.visit(right_node)
                op_type = type(op)
                if op_type in self.operators:
                    if not self.operators[op_type](left, right):
                        return False
                    left = right
                else:
                    raise ValueError(f"Unsupported comparison operator: {op_type}")
            return True
        elif isinstance(node, ast.Call):
            # Handle lumen_op calls
            func_name = node.func.id
            if func_name == "lumen_op":
                a = self.visit(node.args[0])
                b = self.visit(node.args[1])
                op = node.args[2].s
                return self.lumen_ops[op](a, b)
            raise ValueError(f"Unsupported function call: {func_name}")
        elif isinstance(node, ast.Constant):
            return node.value
        else:
            raise ValueError(f"Unsupported expression: {type(node)}")

    def eval(self, expr):
        # Convert Lumen operators to function calls: a !& b -> lumen_op(a,b,'!&')
        for op in sorted(self.lumen_ops, key=len, reverse=True):
            expr = re.sub(
                rf'(\S+)\s*{re.escape(op)}\s*(\S+)',
                r'lumen_op(\1,\2,"' + op + '")',
                expr
            )

        # Define safe lumen_op
        def lumen_op(a, b, op):
            return self.lumen_ops[op](a, b)

        # Parse and evaluate
        tree = ast.parse(expr, mode='eval')
        return self.visit(tree)
def calculator(expr: str):
    try:
        return _SafeEval.eval(expr)
    except Exception as e:
        return f"Error: {e}"
def eval_condition(expr: str) -> bool:
    try:
        return bool(_SafeEval.eval(expr))
    except Exception:
        return False
class LumenInterpreter:
    """A compact, careful rewrite of the Lumen interpreter.

    - Proper block collection (run_file handles multi-line blocks for func/class/if/cycle)
    - Scope stack for functions (locals) with globals available for evaluation
    - eval_expr merges globals + top locals and provides safe builtin helpers
    - Functions bodies are stored as lists of lines and executed inside a pushed local scope
    - cycle (while) supports multi-line bodies and inline single-line bodies
    - print handles parentheses, plain expressions, and manual '+' concatenation without inserting extra spaces
    - typed declarations (int/str/float/bool) and `scan` supported
    - increment/decrement supports x++, x ++ 5, x++5, x++(expr), x ++ y
    """

    def __init__(self):
        self.globals = {}
        self.functions = {}
        #self.classes = {} Scrapped, no OOPLs :(
        self.scope_stack = []

    #utils
    def current_locals(self):
        return self.scope_stack[-1] if self.scope_stack else {}

    def split_top_level(self, s: str, sep: str):
        """Split s on sep but only at top-level (not inside quotes or parentheses).
        Returns list of parts (may include whitespace that caller should strip).
        """
        parts = []
        buf = []
        depth = 0
        in_s = False
        in_d = False
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == "'" and not in_d:
                in_s = not in_s
                buf.append(ch)
            elif ch == '"' and not in_s:
                in_d = not in_d
                buf.append(ch)
            elif not in_s and not in_d:
                if ch in "([{":
                    depth += 1
                    buf.append(ch)
                elif ch in ")]}":
                    depth -= 1
                    buf.append(ch)
                elif ch == sep and depth == 0:
                    parts.append(''.join(buf))
                    buf = []
                else:
                    buf.append(ch)
            else:
                buf.append(ch)
            i += 1
        if buf:
            parts.append(''.join(buf))
        return parts

    def eval_expr(self, expr: str):
        """Evaluate an expression using globals + current locals.

        Raises:
            Exception on syntax/runtime errors
            NameError if a name is missing (caller may choose to handle it)
        """
        expr = expr.strip()
        if expr == "":
            raise Exception("Lumen Error: Empty expression")

        # Build evaluation environment: start with globals, then local overrides
        env = dict(self.globals)
        if self.scope_stack:
            # locals should override globals
            env.update(self.scope_stack[-1])

        # Provide small safe builtins for convenience (only if not shadowed)
        for k, v in (("str", str), ("int", int), ("float", float), ("bool", bool), ("len", len)):
            if k not in env:
                env[k] = v

        try:
            return eval(expr, {}, env)
        except NameError:
            # bubble up NameError so callers can decide fallback behavior
            raise
        except SyntaxError as e:
            raise Exception(f"Lumen Error: invalid syntax in expression '{expr}': {e}")
        except Exception as e:
            raise Exception(f"Lumen Error: Error evaluating '{expr}': {e}")

    def resolve_var(self, name: str):
        if self.scope_stack and name in self.scope_stack[-1]:
            return self.scope_stack[-1][name]
        if name in self.globals:
            return self.globals[name]
        raise Exception(f"Lumen Error: Variable '{name}' not defined")

    def assign_var(self, name: str, value):
        if self.scope_stack:
            self.scope_stack[-1][name] = value
        else:
            self.globals[name] = value

    # exececutiuon
    def exec_line(self, line: str):
        if line is None:
            return
        # strip only trailing newline; preserve leading/trailing spaces for top-level splitting
        line = line.rstrip()
        if not line:
            return

        # If the line is not a block text (with braces), split top-level semicolons
        if not ("{" in line and "}" in line and (line.strip().startswith("func ") or line.strip().startswith("class ") or line.strip().startswith("if ") or line.strip().startswith("cycle "))):
            parts = self.split_top_level(line, ";")
            if len(parts) > 1:
                for p in parts:
                    self.exec_line(p.strip())
                return

        stripped = line.strip()

        # funcs
        if stripped.startswith("func ") and "{" in line:
            header, rest = line.split("{", 1)
            body_text = rest.rsplit("}", 1)[0]
            body_lines = [ln.rstrip() for ln in body_text.splitlines() if ln.strip()]
            m = re.match(r'func\s+([A-Za-z_]\w*)\s*\((.*)\)\s*$', header.strip())
            if not m:
                raise Exception(f"Lumen Error: Invalid function header '{header.strip()}'")
            fname = m.group(1)
            params_raw = m.group(2).strip()
            params = []
            if params_raw:
                for p in self.split_top_level(params_raw, ","):
                    p = p.strip()
                    if not p:
                        continue
                    parts = p.split()
                    if len(parts) != 2:
                        raise Exception(f"Lumen Error: Invalid parameter '{p}'")
                    params.append((parts[0], parts[1]))
            self.functions[fname] = {"params": params, "body": body_lines}
            return

        # # ---------- class block (minimal) ----------
        # if stripped.startswith("class ") and "{" in line:
        #     header, rest = line.split("{", 1)
        #     body_text = rest.rsplit("}", 1)[0]
        #     body_lines = [ln.rstrip() for ln in body_text.splitlines() if ln.strip()]
        #     cname = header.split()[1]
        #     fields = []
        #     methods = {}
        #     for stmt in body_lines:
        #         if stmt.startswith(("int ", "str ", "float ", "bool ")):
        #             fields.append(stmt)
        #         elif stmt.startswith("func "):
        #             # try simple inline parse for method; handle more complex later if desired
        #             h, r = stmt.split("{", 1)
        #             b = r.rsplit("}", 1)[0]
        #             hm = re.match(r'func\s+([A-Za-z_]\w*)\s*\((.*)\)\s*$', h.strip())
        #             if hm:
        #                 mname = hm.group(1)
        #                 params_raw = hm.group(2)
        #                 mparams = []
        #                 if params_raw:
        #                     for pr in self.split_top_level(params_raw, ","):
        #                         pr = pr.strip()
        #                         if not pr:
        #                             continue
        #                         parts = pr.split()
        #                         if len(parts) != 2:
        #                             raise Exception(f"Lumen Error: Invalid parameter '{pr}' in method")
        #                         mparams.append((parts[0], parts[1]))
        #                 methods[mname] = {"params": mparams, "body": [ln.rstrip() for ln in b.splitlines() if ln.strip()]}
        #     self.classes[cname] = {"fields": fields, "methods": methods}
        #     return

        # typed declarations, just how god intended
        for decl in ("int", "str", "float", "bool"):
            if stripped.startswith(decl + " "):
                rest = stripped[len(decl):].strip()
                if "=" in rest:
                    varname, rhs = rest.split("=", 1)
                    varname = varname.strip()
                    rhs = rhs.strip()
                    if rhs.startswith("scan"):
                        prompt_expr = rhs[len("scan"):].strip()
                        if prompt_expr.startswith("(") and prompt_expr.endswith(")"):
                            prompt_expr = prompt_expr[1:-1].strip()
                        prompt = ""
                        if prompt_expr:
                            try:
                                prompt = str(self.eval_expr(prompt_expr))
                            except Exception as e:
                                raise Exception(f"Lumen Error: Invalid scan prompt '{prompt_expr}': {e}")
                        user_in = input(f"{prompt}: " if prompt else "")
                        try:
                            if decl == "int":
                                val = int(user_in)
                            elif decl == "float":
                                val = float(user_in)
                            elif decl == "bool":
                                val = user_in.lower() in ("true", "1", "yes")
                            else:
                                val = user_in
                        except ValueError:
                            raise Exception(f"Lumen Error: Cannot convert input '{user_in}' to {decl}")
                        self.assign_var(varname, val)
                    else:
                        val = self.eval_expr(rhs)
                        self.assign_var(varname, val)
                else:
                    varname = rest.strip()
                    defaults = {"int": 0, "float": 0.0, "bool": False, "str": ""}
                    self.assign_var(varname, defaults[decl])
                return

        # increment/decrement
        m_inc = re.match(r"^([A-Za-z_]\w*)\s*(\+\+|--)\s*(.*)$", stripped)
        if m_inc:
            varname, op, amt_expr = m_inc.groups()
            amt_expr = (amt_expr or "").strip()
            try:
                current = self.resolve_var(varname)
            except Exception:
                raise Exception(f"Lumen Error: Variable '{varname}' not defined")
            if amt_expr == "":
                amt = 1
            else:
                amt = self.eval_expr(amt_expr)
            if op == "++":
                self.assign_var(varname, current + amt)
            else:
                self.assign_var(varname, current - amt)
            return

        # print
        if stripped.startswith("print"):
            expr = stripped[5:].strip()
            if expr.startswith("(") and expr.endswith(")"):
                expr = expr[1:-1].strip()

            # try to eval whole expression first (works for arithmetic / clean expressions)
            try:
                val = self.eval_expr(expr)
                print(val)
                return
            except NameError:
                pass
            except Exception:
                pass

            if "+" in expr:
                parts = [p.strip() for p in self.split_top_level(expr, "+")]
                out_parts = []
                for p in parts:
                    if (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
                        out_parts.append(p[1:-1])
                    else:
                        try:
                            v = self.eval_expr(p)
                            out_parts.append(str(v))
                        except NameError:
                            # check local/global variables explicitly
                            if self.scope_stack and p in self.scope_stack[-1]:
                                out_parts.append(str(self.scope_stack[-1][p]))
                                continue
                            if p in self.globals:
                                out_parts.append(str(self.globals[p]))
                                continue
                            raise Exception(f"Lumen Error: Variable '{p}' not defined")
                        except Exception as e:
                            raise Exception(f"Lumen Error: Cannot evaluate '{p}' in print: {e}")
                # do literal concatenation (no automatic spaces)
                print("".join(out_parts))
                return

            # no plus, try string literal or eval
            if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
                print(expr[1:-1])
                return
            try:
                val = self.eval_expr(expr)
                print(val)
                return
            except NameError as e:
                raise Exception(str(e))
            except Exception as e:
                raise Exception(str(e))

        # if/else inline
        if stripped.startswith("if ") and "{" in line:
            header_body = line
            cm = re.search(r"\((.*)\)", header_body)
            if not cm:
                raise Exception("Lumen Error: Invalid if condition")
            cond_expr = cm.group(1).strip()
            cond_val = self.eval_expr(cond_expr)

            # extract first {...} as then, optional second {...} as else
            first_start = header_body.find("{")
            first_end = header_body.find("}", first_start)
            then_part = header_body[first_start+1:first_end].strip()
            else_part = None
            after = header_body[first_end+1:]
            if "else" in after and "{" in after and "}" in after:
                s = after.find("{")
                e = after.find("}", s)
                else_part = after[s+1:e].strip()

            if cond_val:
                for stmt in [s.strip() for s in self.split_top_level(then_part, ";") if s.strip()]:
                    self.exec_line(stmt)
            else:
                if else_part:
                    for stmt in [s.strip() for s in self.split_top_level(else_part, ";") if s.strip()]:
                        self.exec_line(stmt)
            return

        # cycle loops
        if stripped.startswith("cycle ") and "{" in line:
            cm = re.search(r"\((.*)\)", stripped)
            if not cm:
                raise Exception("Lumen Error: Invalid cycle condition")
            cond_expr = cm.group(1).strip()
            body_text = line[line.find("{")+1:line.rfind("}")].strip()
            body_lines = [ln.rstrip() for ln in body_text.splitlines() if ln.strip()]
            # while loop
            while True:
                cond_val = self.eval_expr(cond_expr)
                if not cond_val:
                    break
                for stmt in body_lines:
                    for s in [ss.strip() for ss in self.split_top_level(stmt, ";") if ss.strip()]:
                        self.exec_line(s)
            return

        # calling fns
        call_m = re.match(r"^([A-Za-z_]\w*)\s*\((.*)\)\s*$", stripped)
        if call_m:
            fname = call_m.group(1)
            args_raw = call_m.group(2).strip()
            if fname not in self.functions:
                raise Exception(f"Lumen Error: Function '{fname}' not defined")
            func = self.functions[fname]
            args = []
            if args_raw:
                for part in self.split_top_level(args_raw, ","):
                    if part.strip():
                        args.append(part.strip())

            arg_values = []
            for a in args:
                # attempt to eval argument using current evaluation environment
                try:
                    val = self.eval_expr(a)
                except NameError:
                    # if it's a global var name, use that
                    if a in self.globals:
                        val = self.globals[a]
                    else:
                        # maybe it's a literal like "hello"
                        if (a.startswith('"') and a.endswith('"')) or (a.startswith("'") and a.endswith("'")):
                            val = a[1:-1]
                        else:
                            raise Exception(f"Lumen Error: Cannot resolve function argument '{a}'")
                arg_values.append(val)

            # create local scope only containing parameters (locals override globals via eval_expr)
            local_scope = {}
            for (typ, pname), aval in zip(func['params'], arg_values):
                local_scope[pname] = aval

            # push local scope
            self.scope_stack.append(local_scope)
            try:
                for stmt in func['body']:
                    for s in [ss.strip() for ss in self.split_top_level(stmt, ";") if ss.strip()]:
                        self.exec_line(s)
            finally:
                self.scope_stack.pop()
            return

        if "=" in stripped:
            varname, rhs = stripped.split("=", 1)
            varname = varname.strip()
            rhs = rhs.strip()
            val = self.eval_expr(rhs)
            self.assign_var(varname, val)
            return

        raise Exception(f"Lumen Error: Unknown statement '{line}'")

    def run_file(self, path: str, type_check=False):
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
        i = 0
        n = len(lines)
        while i < n:
            raw = lines[i]
            stripped = raw.strip()
            if not stripped:
                i += 1
                continue

            # detect block starting lines (func/class/if/cycle/else) with '{'
            if (stripped.startswith('func ') or stripped.startswith('class ') or stripped.startswith('if ') or stripped.startswith('cycle ') or stripped.startswith('else')) and '{' in stripped:
                block_lines = [raw]
                brace_count = raw.count('{') - raw.count('}')
                i += 1
                while brace_count > 0 and i < n:
                    ln = lines[i]
                    block_lines.append(ln)
                    brace_count += ln.count('{') - ln.count('}')
                    i += 1
                block_text = "\n".join(block_lines)
                self.exec_line(block_text)
                continue

            # non-block line: may contain several top-level semicolon-separated statements
            parts = self.split_top_level(raw, ';')
            for p in parts:
                if p.strip():
                    self.exec_line(p.strip())
            i += 1
class Shell:
    def __init__(self):
        self.current_dir = os.getcwd()
        self.previous_dir = self.current_dir
        self.command_history = []
        self.env_vars = {}
        self.jobs = {}
        self.job_counter = 1
        self.DEFAULT_EXT = ".txt"
        self.aliases ={
            "del": "delete",
            "co": "copy",
            "mv": "move",
            "mk": "make",
            "ren": "rename",
            "vi": "view",
            "hi": "history",
            "os": "osinfo",
            #"ec": "echo", #planned on doing stuff like in CMD, but thought it was dumb and made a programming language instead
            "fi": "file",
            "f": "file",
            "d": "dir",
            "lum": "lumen"
        }

        self.help_text = {
            "File Commands": {
                "calc": "Calculator (interactive or single expression)",
                "copy file": "Copy a file to another directory",
                "delete file": "Delete a file",
                "make file": "Create a new file",
                "move file": "Move a file to another directory",
                "open file": "Open an existing file",
                "rename file": "Rename a file",
                "search": "Search for files/directories containing a name",
                "view file": "View a file's contents",
                "info": "Show info about a file or directory"
            },
            "Directory Commands": {
                "delete dir": "Delete a directory",
                "goto": "Change directory",
                "here": "Show current directory",
                "list": "List contents of current directory",
                "make dir": "Create a new directory",
                "move dir": "Move a directory"
            },
            "System & Environment": {
                #"get": "Get environment variable", #1) Dumb, just make a programming language
                "osinfo": "Show system info",
                #"set": "Set environment variable", #2) Same story, I just made a programming language
                "setext": "Set default file extension"
            },
            "Jobs": {
                "jobs": "List running jobs",
                "kill": "Terminate a job",
                "run": "Run an external command"
            },
            "Miscellaneous": {
                "lumen": "Start Lumen REPL or run a Lumen script (lumen run <file>)",
                #"echo": "Print text",#Why did I ever think that i should've made lumen in python???
                "history": "Show command history",
                "quit": "Exit the shell",
                "help": "Show this help menu",
                "sleep": "Pause execution",
                "why": "Shows you why I made this",
            }
        }

    def get_prompt(self):
        home = os.path.expanduser("~")
        display_path = self.current_dir
        if self.current_dir.startswith(home):
            display_path = "~" + self.current_dir[len(home):]
        user = getpass.getuser()
        return f"{BOLD}{YELLOW}{user}{RESET}:{GREEN}{display_path}{RESET} >> "
    def check_args(self, parts, required):
        if len(parts) < required:
            print(f"{RED}Missing arguments. Expected {required - 1}.{RESET}")
            return False
        return True
    def file_path(self, name):
        return os.path.join(self.current_dir, f"{name}{self.DEFAULT_EXT}")

    def makeDir(self, name):
        path = os.path.join(self.current_dir, name)
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"{GREEN}Created directory: {path}{RESET}")
        else:
            print(f"{RED}Directory '{name}' already exists.{RESET}")

    def makeFile(self, *names):
        for name in names:
            filename = self.file_path(name)
            if os.path.exists(filename):
                print(f"{RED}File '{filename}' already exists.{RESET}")
                continue
            print(f"{GREEN}Creating file: {filename}{RESET}")
            print(f"{CYAN}Enter text (type ':wq' to save):{RESET}")
            lines = []
            while True:
                line = input()
                if line == ":wq":
                    break
                lines.append(line)
            with open(filename, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"{GREEN}Saved {filename}{RESET}")

    def openLumen(self, name):
        if not name.endswith(".lum"):
            name += ".lum"
        path = os.path.join(self.current_dir, name)
        if not os.path.exists(path):
            print(f"{RED}File '{name}' does not exist.{RESET}")
            return

        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        print(f"{CYAN}Current content of {name}:{RESET}")
        for line in lines:
            print(line)

        print(f"{CYAN}Enter new Lumen code (type ':wq' to save):{RESET}")
        new_lines = lines[:]
        while True:
            line = input()
            if line.strip() == ":wq":
                break
            new_lines.append(line)

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))

        print(f"{GREEN}Saved {name}{RESET}")
    def openFile(self, name):
        filename = self.file_path(name)
        if not os.path.exists(filename):
            print(f"{RED}File '{filename}' does not exist.{RESET}")
            return
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
        print(f"{CYAN}Current content of {filename}:{RESET}")
        for line in lines:
            print(line)
        print(f"{CYAN}Enter new text (type ':wq' to save):{RESET}")
        new_lines = lines[:]
        while True:
            line = input()
            if line == ":wq":
                break
            new_lines.append(line)
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines))
        print(f"{GREEN}Saved {filename}{RESET}")

    def move(self, item_type, name, dest_dir_name):
        """Move a file, Lumen file, or directory to another directory.
           Special keyword ':back' moves it to the parent directory."""

        # Handle Lumen extension
        if item_type == "lum" and not name.endswith(".lum"):
            name += ".lum"

        src = os.path.join(self.current_dir, name)

        # Handle special destination keywords
        if dest_dir_name == ":back":
            dest_dir = os.path.dirname(self.current_dir)  # parent directory
        elif dest_dir_name == ":home":
            dest_dir = os.path.expanduser("~")
        else:
            dest_dir = os.path.join(self.current_dir, dest_dir_name)

        dest = os.path.join(dest_dir, name)

        # Validate source
        if not os.path.exists(src):
            print(f"{RED}{item_type.capitalize()} '{name}' does not exist.{RESET}")
            return

        # Validate destination directory
        if not os.path.exists(dest_dir):
            print(f"{RED}Destination directory '{dest_dir_name}' does not exist.{RESET}")
            return

        # Move the item
        shutil.move(src, dest)
        print(f"{GREEN}Moved {item_type} '{name}' to '{dest_dir}'{RESET}")

    def copy(self, item_type, name, dest_dir_name):
        """Copy a file, Lumen file, or directory to another directory.
           Special keywords ':back' and ':home' are supported."""

        # Handle Lumen extension
        if item_type == "lum" and not name.endswith(".lum"):
            name += ".lum"

        src = os.path.join(self.current_dir, name)

        # Handle special destination keywords
        if dest_dir_name == ":back":
            dest_dir = os.path.dirname(self.current_dir)  # parent directory
        elif dest_dir_name == ":home":
            dest_dir = os.path.expanduser("~")
        else:
            dest_dir = os.path.join(self.current_dir, dest_dir_name)

        dest = os.path.join(dest_dir, name)

        # Validate source
        if not os.path.exists(src):
            print(f"{RED}{item_type.capitalize()} '{name}' does not exist.{RESET}")
            return

        # Validate destination directory
        if not os.path.exists(dest_dir):
            print(f"{RED}Destination directory '{dest_dir_name}' does not exist.{RESET}")
            return

        # Copy the item
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)

        print(f"{GREEN}Copied {item_type} '{name}' to '{dest_dir}'{RESET}")

        src = os.path.join(self.current_dir, name)
        dest_dir = os.path.join(self.current_dir, dest_dir_name)
        dest = os.path.join(dest_dir, name)

        # Validate source
        if not os.path.exists(src):
            print(f"{RED}{item_type.capitalize()} '{name}' does not exist.{RESET}")
            return

        # Validate destination directory
        if not os.path.exists(dest_dir):
            print(f"{RED}Destination directory '{dest_dir_name}' does not exist.{RESET}")
            return

        # Copy the item
        if os.path.isdir(src):
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)

        print(f"{GREEN}Copied {item_type} '{name}' to '{dest_dir_name}'{RESET}")

    def delete(self, item_type, *names):
        """Delete files, Lumen files, or directories."""
        for name in names:
            # Determine path based on type
            if item_type == "dir":
                path = os.path.join(self.current_dir, name)
            elif item_type == "lum":
                if not name.endswith(".lum"):
                    name += ".lum"
                path = os.path.join(self.current_dir, name)
            else:  # regular file
                path = os.path.join(self.current_dir, f"{name}{self.DEFAULT_EXT}")

            # Check if safe to delete
            if not self.safe_delete_path(path):
                continue

            # Confirm deletion
            confirm = input(
                f"{YELLOW}Are you sure you want to delete '{os.path.basename(path)}'? (yes/no): {RESET}").lower()
            if confirm != "yes":
                print(f"{CYAN}Delete cancelled for {os.path.basename(path)}{RESET}")
                continue

            # Perform deletion
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"{GREEN}Deleted {item_type} '{os.path.basename(path)}'{RESET}")
            except Exception as e:
                print(f"{RED}Error deleting '{os.path.basename(path)}': {e}{RESET}")

    def listDir(self):
        print(f"{CYAN}Contents of {self.current_dir}:{RESET}")
        for item in os.listdir(self.current_dir):
            path = os.path.join(self.current_dir, item)
            if os.path.isdir(path):
                print(f"{BLUE}[DIR]{RESET} {item}")
            else:
                print(f"{WHITE}      {item}{RESET}")
    def changeDir(self, name):
        if name == "..":
            parent = os.path.dirname(self.current_dir)
            if parent and os.path.exists(parent):
                self.previous_dir = self.current_dir
                self.current_dir = parent
                print(f"{GREEN}Changed directory to {self.current_dir}{RESET}")
            else:
                print(f"{RED}Already at the root directory.{RESET}")
        elif name == "-":
            self.current_dir, self.previous_dir = self.previous_dir, self.current_dir
            print(f"{GREEN}Changed directory to {self.current_dir}{RESET}")
        elif name == "~":
            self.previous_dir = self.current_dir
            self.current_dir = os.path.expanduser("~")
            print(f"{GREEN}Changed directory to {self.current_dir}{RESET}")
        else:
            path = os.path.join(self.current_dir, name)
            if os.path.exists(path) and os.path.isdir(path):
                self.previous_dir = self.current_dir
                self.current_dir = path
                print(f"{GREEN}Changed directory to {self.current_dir}{RESET}")
            else:
                print(f"{RED}Directory '{name}' does not exist.{RESET}")
    def viewFile(self, name):
        filename = self.file_path(name)
        if not os.path.exists(filename):
            print(f"{RED}File '{filename}' does not exist.{RESET}")
            return
        with open(filename, "r", encoding="utf-8") as f:
            print(f.read())
    def renameFile(self, old, new):
        old_path = os.path.join(self.current_dir, old)
        new_path = os.path.join(self.current_dir, new)
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            print(f"{GREEN}Renamed '{old}' to '{new}'{RESET}")
        else:
            print(f"{RED}File/Directory '{old}' does not exist.{RESET}")
    def fileInfo(self, name):
        path_file = os.path.join(self.current_dir, name)
        if not os.path.exists(path_file):
            print(f"{RED}'{name}' does not exist.{RESET}")
            return
        stats = os.stat(path_file)
        size = stats.st_size
        created = datetime.datetime.fromtimestamp(stats.st_ctime)
        modified = datetime.datetime.fromtimestamp(stats.st_mtime)
        type_file = "Directory" if os.path.isdir(path_file) else "File"
        print(f"{CYAN}Name: {name}\nType: {type_file}\nSize: {size} bytes\nCreated: {created}\nModified: {modified}{RESET}")
    def searchFiles(self, name):
        matches = []
        for root, dirs, files in os.walk(self.current_dir):
            for file in files:
                if name in file:
                    matches.append(os.path.join(root, file))
            for d in dirs:
                if name in d:
                    matches.append(os.path.join(root, d))
        if matches:
            for m in matches:
                print(f"{GREEN}{m}{RESET}")
        else:
            print(f"{YELLOW}No matches found.{RESET}")

    def setEnv(self, var, value):
        self.env_vars[var] = value
        print(f"{GREEN}Set {var}={value}{RESET}")
    def getEnv(self, var):
        value = self.env_vars.get(var)
        if value is not None:
            print(f"{CYAN}{var}={value}{RESET}")
        else:
            print(f"{YELLOW}Environment variable '{var}' not set.{RESET}")

    def osInfo(self):
        print(f"{CYAN}OS: {platform.system()}, Release: {platform.release()}, Version: {platform.version()}{RESET}")
        print(f"{CYAN}Architecture: {platform.architecture()[0]}, Python: {platform.python_version()}{RESET}")
    def runCommand(self, cmd):
        import shlex
        try:
            # Split command into arguments safely
            args = shlex.split(cmd)
            if not args:
                print(f"{RED}No command provided.{RESET}")
                return
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.jobs[str(self.job_counter)] = proc
            print(f"{CYAN}Started job [{self.job_counter}] PID {proc.pid}{RESET}")
            self.job_counter += 1
        except Exception as e:
            print(f"{RED}Error: {e}{RESET}")
    def safe_delete_path(self, path):
        forbidden = [os.path.abspath("/"), os.path.expanduser("~"), os.path.abspath("C:\\Windows")]
        if os.path.abspath(path) in forbidden or not os.path.exists(path):
            print(f"{RED}Deletion forbidden or path does not exist: {path}{RESET}")
            return False
        return True
    def sleepSeconds(self, seconds):
        try:
            seconds = float(seconds)
            time.sleep(seconds)
        except ValueError:
            print(f"{RED}Invalid number: {seconds}{RESET}")
    def listJobs(self):
        for job_id, proc in self.jobs.items():
            status = "Running" if proc.poll() is None else "Completed"
            print(f"{GREEN}[{job_id}] PID {proc.pid}: {status}{RESET}")
    def killJob(self, job_id):
        proc = self.jobs.get(job_id)
        if not proc:
            print(f"{RED}Job ID {job_id} not found.{RESET}")
            return
        proc.terminate()
        print(f"{GREEN}Terminated job {job_id} (PID {proc.pid}){RESET}")
    def calculator(self):
        print(f"{CYAN}Simple Calculator. Type ':wq' to quit.{RESET}")
        while True:
            expr = input(f"{BOLD}{GREEN}calc> {RESET}")
            if expr.lower() == ":wq":
                break
            try:
                print(f"{YELLOW}{eval(expr, {'__builtins__': {}}, {})}{RESET}")
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")
    def setExt(self, ext):
        if not ext.startswith("."):
            ext = "." + ext
        self.DEFAULT_EXT = ext
        print(f"{GREEN}Default file extension set to '{self.DEFAULT_EXT}'{RESET}")

    def lumen_run(self, filename):
        if not filename.endswith(".lum"):
            filename += ".lum"
        path = os.path.join(self.current_dir, filename)
        if not os.path.exists(path):
            print(f"{RED}File '{filename}' does not exist.{RESET}")
            return
        interpreter = LumenInterpreter()
        try:
            interpreter.run_file(path, type_check=True)  # <- type_check flag added
        except Exception as e:
            print(f"{RED}Lumen Error: {e}{RESET}")

    def makeLumen(self, *names):
        for filename in names:
            if not filename.endswith(".lum"):
                filename += ".lum"
            path = os.path.join(self.current_dir, filename)
            if os.path.exists(path):
                print(f"{RED}File '{filename}' already exists.{RESET}")
                continue
            print(f"{GREEN}Creating Lumen file: {filename}{RESET}")
            print(f"{CYAN}Enter Lumen code (type ':wq' to save):{RESET}")
            lines = []
            while True:
                line = input()
                if line.strip() == ":wq":
                    break
                lines.append(line)
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"{GREEN}Saved {filename}{RESET}")

    def lumen_repl(self):
        interpreter = LumenInterpreter()
        lum_files = [f for f in os.listdir(self.current_dir) if f.endswith(".lum")]
        if lum_files:
            print(f"{CYAN}Available Lumen files:{RESET}")
            for idx, f in enumerate(lum_files, 1):
                print(f"  {idx}. {f}")
            choice = input(f"{BOLD}Select a file to open (1-{len(lum_files)}) or 'new': {RESET}").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(lum_files):
                filename = lum_files[int(choice) - 1]
                path = os.path.join(self.current_dir, filename)
                try:
                    interpreter.run_file(path)
                except Exception as e:
                    print(f"{RED}Lumen Error: {e}{RESET}")

        buffer = []
        while True:
            line = input(f"{BOLD}{BLUE}lumen>{RESET} ").strip()
            if not line or line in (":wq", ":quit", "exit"):
                break

            if line.startswith(":save "):
                fname = line.split(maxsplit=1)[1].strip()
                if not fname.endswith(".lum"):
                    fname += ".lum"
                with open(os.path.join(self.current_dir, fname), "w", encoding="utf-8") as f:
                    f.write("\n".join(buffer))
                print(f"{GREEN}Saved session to {fname}{RESET}")
                continue

            if line.startswith(":run "):
                fname = line.split(maxsplit=1)[1].strip()
                if not fname.endswith(".lum"):
                    fname += ".lum"
                path = os.path.join(self.current_dir, fname)
                try:
                    interpreter.run_file(path)
                except Exception as e:
                    print(f"{RED}Lumen Error: {e}{RESET}")
                continue

            # store input in session buffer
            buffer.append(line)
            # statements = [stmt.strip() for stmt in line.split(";") if stmt.strip()]
            # for stmt in statements:
            #     try:
            #         interpreter.exec_line(stmt)
            #     except Exception as e:
            #         print(f"{RED}Lumen Error: {e}{RESET}") C++ or hell, even Holy C would've been better suited for this

    def showHelp(self, cmd_name=None):
        if cmd_name:
            search_terms = cmd_name.lower().split()
            matches = []
            for category, commands in self.help_text.items():
                for cmd, desc in commands.items():
                    cmd_words = cmd.lower().split()
                    if all(any(term in word for word in cmd_words) for term in search_terms):
                        matches.append((cmd, desc))
            if matches:
                print(f"{CYAN}Matching commands:{RESET}")
                for cmd, desc in matches:
                    print(f"  {GREEN}{cmd:<15}{RESET} - {desc}")
            else:
                print(f"{YELLOW}No commands matching '{cmd_name}' found.{RESET}")
        else:
            print(f"{CYAN}Available commands:{RESET}")
            for category, commands in self.help_text.items():
                print(f"{BOLD}{YELLOW}{category}:{RESET}")
                for cmd, desc in sorted(commands.items()):
                    print(f"  {GREEN}{cmd:<15}{RESET} - {desc}")
                print()

    def run_shell(self):
        while True:
            try:
                cmd = input(self.get_prompt()).strip()
            except KeyboardInterrupt:
                print()
                continue
            if not cmd:
                continue
            if cmd == "!!":
                if self.command_history:
                    cmd = self.command_history[-1]
                    print(f"{CYAN}{cmd}{RESET}")
                else:
                    print(f"{YELLOW}No commands in history.{RESET}")
                    continue

            self.command_history.append(cmd)
            parts = cmd.split()
            if parts[0] in self.aliases:
                parts[0] = self.aliases[parts[0]]

            match parts[0]:
                case "quit":
                    break
                case "list":
                    self.listDir()
                case "here":
                    print(f"{CYAN}{self.current_dir}{RESET}")
                case "goto":
                    if self.check_args(parts, 2):
                        self.changeDir(parts[1])
                case "make":
                    if self.check_args(parts, 3):
                        target_type = parts[1]
                        names = parts[2:]  # allow multiple names
                        if target_type in ("dir", "d"):
                            for name in names:
                                self.makeDir(name)
                        elif target_type in ("file", "f", "fi"):
                            self.makeFile(*names)
                        elif target_type in ("lumen", "lum"):
                            self.makeLumen(*names)
                        else:
                            print(f"{RED}Usage: make dir/d <name>, make file/f/fi <name>, make lumen/lum <name>{RESET}")

                case "lumen":
                    if len(parts) == 1:
                        self.lumen_repl()
                    elif len(parts) >= 3 and parts[1] == "run":
                        self.lumen_run(parts[2])
                    else:
                        print(f"{YELLOW}Usage: lumen [run <file>]{RESET}")
                case "open":
                    if len(parts) >= 3 and parts[1] == "file":
                        self.openFile(parts[2])
                    elif len(parts) >= 3 and parts[1] == "lumen":
                        self.openLumen(parts[2])
                case "view":
                    if self.check_args(parts, 2):
                        self.viewFile(parts[1])
                case "rename":
                    if self.check_args(parts, 3):
                        self.renameFile(parts[1], parts[2])
                case "info":
                    if self.check_args(parts, 2):
                        self.fileInfo(parts[1])
                case "search":
                    if self.check_args(parts, 2):
                        self.searchFiles(parts[1])
                # case "set":
                #     if self.check_args(parts, 3):
                #         self.setEnv(parts[1], parts[2])
                # case "get":
                #     if self.check_args(parts, 2):
                #         self.getEnv(parts[1])
                case "osinfo":
                    self.osInfo()
                #case "echo":
                    #print(f"{CYAN}{' '.join(parts[1:])}{RESET}")
                case "run":
                    if self.check_args(parts, 2):
                        self.runCommand(" ".join(parts[1:]))
                case "sleep":
                    if self.check_args(parts, 2):
                        self.sleepSeconds(parts[1])
                case "jobs":
                    self.listJobs()
                case "kill":
                    if self.check_args(parts, 2):
                        self.killJob(parts[1])
                case "calc":
                    self.calculator()
                case "history":
                    for i, h in enumerate(self.command_history, 1):
                        print(f"{WHITE}{i}: {h}{RESET}")
                case "move":
                    if self.check_args(parts, 4):
                        self.move(parts[1], parts[2], parts[3])

                case "copy":
                    if self.check_args(parts, 3):
                        self.copy(parts[1], parts[2], parts[3])
                case "delete":
                    if self.check_args(parts, 2):
                        item_type = parts[1]
                        items = parts[2:]  # everything after type
                        if not items:
                            print(f"{RED}No items specified to delete.{RESET}")
                        else:
                            self.delete(item_type, *items)

                case "setext":
                    if self.check_args(parts, 2):
                        self.setExt(parts[1])
                case "help":
                    if len(parts) == 1:
                        self.showHelp()
                    else:
                        self.showHelp(" ".join(parts[1:]))
                case "lumen":
                    # Options:
                    #   lumen               -> REPL
                    #   lumen run <file>    -> run file
                    if len(parts) == 1:
                        self.lumen_repl()
                    elif len(parts) >= 3 and parts[1] == "run":
                        self.lumen_run(parts[2])
                    else:
                        print(f"{YELLOW}Usage: lumen [run <file>]{RESET}")
                case "call":
                    if len(parts) >= 2 and parts[1] == "therapist":
                        therapist = Therapist()
                        therapist.start()
                case "why":
                    print("""
This is a tribute to God's loneliest programmer: Terry A. Davis.

Terrence Andrew Davis (December 15, 1969 – August 11, 2018) was an American electrical engineer, computer programmer, 
and outsider artist best known for creating and designing TempleOS, a public domain operating system. In 1996, 
Davis began experiencing regular manic episodes, one of which led him to hospitalization. 
Initially diagnosed with bipolar disorder, he was later declared to have schizophrenia. 
After 2017, he struggled with periods of homelessness and incarceration. 
His fans brought him supplies, but Davis refused their offers of housing.
On August 11, 2018, he was struck by a train and died at the age of 48.
(https://en.wikipedia.org/wiki/Terry_A._Davis)

He created one of the most ambitious programming feats one man could do. He created TempleOS, written in his own offshoot
of the C programming language called Holy C or C✝.
C✝ is a just-in-time compiled programming language created by Terry A. Davis for the TempleOS operating system, 
functioning as both a general-purpose and scripting language.
C✝ unique features and syntax, such as automatic printing of literal strings and the ability to call functions without parentheses for simple cases.
HolyC was designed for direct use within TempleOS, allowing for system-level programming and scripting from within the operating system's terminal.
(https://en.wikipedia.org/wiki/TempleOS#:~:text=HolyC%20(formerly%20C+)%2C%20named,some%20object%2Doriented%20programming%20paradigms.)

RIP Terry A. Davis""")
                case _:
                    print(f"{RED}Unknown command.{RESET}")

if __name__ == "__main__":
    shell = Shell()
    shell.run_shell()
