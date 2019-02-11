import curses
import operator
import re
from functools import lru_cache

class Terminfo:
    def __init__(self):
        curses.setupterm()
    
    @lru_cache(128)
    def getflag(self, name):
        return curses.tigetflag(name).decode("ascii")
    
    @lru_cache(128)
    def getnum(self, name):
        return curses.tigetnum(name).decode("ascii")

    @lru_cache(128)
    def getstr(self, name):
        return curses.tigetstr(name).decode("ascii")

    def __getitem__(self, name):
        return self.getstr(name)
    
def termcap_format(format_str, *args):
    """Evaluate a parameterized termcap string. (it's a full language)
    See `man 5 terminfo` in section "Parameterized Strings"
    """
    arguments = list(args)
    stack = []
    regs = {}
    output = []

    def parse_output(match):
        nonlocal output
        output += match[1] % (stack.pop(),)
    def parse_push(match):
        stack.append(arguments[int(match[1]) - 1])
    def parse_set(match):
        regs[match[1]] = stack.pop()
    def parse_get(match):
        stack.append(regs[match[1]])
    def parse_const_char(match):
        stack.append(match[1])
    def parse_const_int(match):
        stack.append(int(match[1]))
    def parse_binop(match):
        lhs = stack.pop()
        rhs = stack.pop()
        stack.append({
            "+": operator.add,
            "-": operator.sub,
            "*": operator.mul,
            "/": operator.floordiv,
            "m": operator.mod,
            "&": operator.and_,
            "|": operator.or_,
            "^": operator.xor,
            "=": operator.eq,
            "<": operator.lt,
            ">": operator.gt,
            "A": lambda l, r: l and r,
            "O": lambda l, r: l or r
        }[match[1]](lhs, rhs))
    def parse_unop(match):
        operand = stack.pop()
        stack.append({
            "!": operator.not_,
            "~": operator.invert
        }[match[1]](operand))
    def parse_inc(match):
        arguments[0] += 1
        arguments[1] += 1
    def parse_percent(match):
        output.append("%")
    def parse_char(match):
        output.append(match[0])
    def parse_conditional(match):
        if_part = match[1]
        then_part = match[2]
        else_part = match[3]
        parse(if_part)
        if stack.pop():
            parse(then_part)
        elif else_part:
            parse(else_part)
    
    patterns = {
        re.compile(r"(%(?:0?\d)?[dx]|c|s)"): parse_output,
        re.compile(r"%p([1-9])"): parse_push,
        re.compile(r"%P([a-z])"): parse_set,
        re.compile(r"%g([a-z])"): parse_get,
        re.compile(r"%'(.)'"): parse_const_char,
        re.compile(r"%{(\d+)}"): parse_const_int,
        re.compile(r"%([+\-*/m&|\^=<>AO])"): parse_binop,
        re.compile(r"%([!~])"): parse_unop,
        re.compile(r"%\?(.+)%t(.+)(?:%e(.+))?%;"): parse_conditional,
        re.compile(r"%i"): parse_inc,
        re.compile(r"%%"): parse_percent,
        re.compile(r"."): parse_char
    }
    
    def parse(string):
        while len(string) > 0:
            for p, parser in patterns.items():
                match = p.match(string)
                if match:
                    parser(match)
                    string = string[len(match[0]):]
                    break
    parse(format_str)
    
    return "".join(output)
