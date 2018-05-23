import plex

class ParseError(Exception):
    pass

class ParserClass():
    def __init__(self):
        self.st = {}

    def create_scanner(self, fp):
        keyword = plex.Str("print")
        assignment = plex.Str("=")
        parenthesis = plex.Str("(",")")
        Logical_Operator = plex.Str("not", "and", "or")
        letter = plex.Range("azAZ")
        digit = plex.Str("0","1")
        condition = letter + plex.Rep(letter | digit)
        true = plex.NoCase(plex.Str("true", "t", "1"))
        false = plex.NoCase(plex.Str("false", "f", "0"))
        space_or_new_line = plex.Any(' \n\t')
        lexicon = plex.Lexicon([
            (keyword, plex.TEXT),
            (Logical_Operator, plex.TEXT),
            (assignment, plex.TEXT),
            (parenthesis,plex.TEXT),
            (true, "True"),
            (false, "False"),
            (condition, "Condition"),
            (space_or_new_line, plex.IGNORE)
        ])

        self.scanner = plex.Scanner(lexicon, fp)
        self.next_value, self.value = self.next_token()

    def parse(self, fp):
        self.create_scanner(fp)
        fp.seek(0)
        self.text = fp.readlines()
        self.text = [line.strip() for line in self.text]
        self.terms_list()

    def next_token(self):
        return self.scanner.read()

    def terms_list(self):
        first_set = ["Condition", "print"]
        if self.next_value in first_set:
            self.terms()
            self.terms_list()
        elif self.next_value is None:
            return
        else:
            raise ParseError("terms_list error")

    def terms(self):
        if self.next_value == "Condition":
            varmane = self.value
            self.match("Condition")
            self.match("=")
            self.st[varmane] = self.expression()
        elif self.next_value == "print":
            self.match("print")
            print(self.expression())
        else:
            raise ParseError("terms error")

    def expression(self):
        first_set = ["not", "(", "Condition", "False", "True"]
        if self.next_value in first_set:
            t = self.term()
            tt = self.term_tail()
            if tt is None:
                return t
            if tt[0] == "or":
                return t or tt[1]
        else:
            raise ParseError("expression error")

    def term_tail(self):
        follow_set = [")", "Condition", "print"]
        if self.next_value == "or":
            op = self.oroperator()
            t = self.term()
            tt = self.term_tail()
            if tt is None:
                return (op, t)
            if tt[0] == "or":
                return (op, t or tt[1])
        elif self.next_value in follow_set or self.next_value is None:
            return
        else:
            raise ParseError("termtail error")

    def term(self):
        first_set = ["not", "(", "Condition", "False", "True"]
        if self.next_value in first_set:
            neg = self.notoperator()
            f = self.factor()
            ft = self.factor_tail()
            if ft is None:
                if neg is None:
                    return f
                else:
                    return not f
            if ft[0] == "and":
                if neg is None:
                    return f and ft[1]
                else:
                    return not f and ft[1]
        else:
            raise ParseError("term error")

    def factor_tail(self):
        follow_set = [")", "or", "Condition", "print"]
        if self.next_value == "and":
            op = self.andoperator()
            neg = self.notoperator()
            f = self.factor()
            ft = self.factor_tail()
            if ft is None:
                if neg is None:
                    return (op, f)
                return (op, not f)
            if ft[0] == "and":
                if neg is None:
                    return (op, f and ft[1])
                return (op, not f and ft[1])
        else:
            return

    def factor(self):
        if self.next_value == "(":
            self.match("(")
            exp = self.expression()
            self.match(")")
            return exp
        elif self.next_value == "Condition":
            varname = self.value
            self.match("Condition")
            return self.get_value(varname)
        elif self.next_value == "False":
            self.match("False")
            return False
        elif self.next_value == "True":
            self.match("True")
            return True
        else:
            raise ParseError("factor error")

    def notoperator(self):
        if self.next_value == "not":
            self.match("not")
            return "not"


    def andoperator(self):
        if self.next_value == "and":
            self.match("and")
            return "and"
      
    def oroperator(self):
        if self.next_value == "or":
            self.match("or")
            return "or"

    def match(self, token):
        if self.next_value == token:
            self.pos = self.scanner.position()
            self.next_value, self.value = self.next_token()
        else:
            raise ParseError("match error")

    def get_value(self, name):
        if name in self.st:
            return self.st[name]
        else:
            raise ParseError("get_value error" )


ParserObject = ParserClass() 
fp = open("data.txt", "r")   
try:
    ParserObject.parse(fp)
except ParseError as ErrorMsg: 
    print(ErrorMsg)
fp.close()

