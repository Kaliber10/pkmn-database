import sys

class Element():
    tag = ""
    def __init__(self, **kwargs):
        self.children = []
        self.text_content = ""
        self.attributes = kwargs

    @classmethod
    def tags(cls):
        return f"<{cls.tag}>", f"</{cls.tag}>"

    def full_tags(self):
        tags = self.tags()
        open_tag = tags[0]
        attrs = self.list_attributes()
        if attrs:
            open_tag = open_tag.replace(">", f" {attrs}>")
        return open_tag, tags[1]

    def list_attributes(self):
        return " ".join([f'{key}="{value}"' for key, value in self.attributes.items()])

    def __str__(self):
        e_tags = self.full_tags()
        return f"{e_tags[0]}{self.text_content}{e_tags[1]}"

class HTML(Element):
    tag = "html"

class Head(Element):
    tag = "head"

class Body(Element):
    tag = "body"

class Anchor(Element):
    tag = "a"

class Div(Element):
    tag = "div"

class Heading1(Element):
    tag = "h1"

class Heading2(Element):
    tag = "h2"

class Table(Element):
    tag = "table"

class TableBody(Element):
    tag= "tbody"

class TableRow(Element):
    tag = "tr"

class TableHeader(Element):
    tag = "th"

class TableDataCell(Element):
    tag = "td"

class DOM():

    def __init__(self, html_element=None):
        if not html_element:
            html_element = HTML()
        self.top = html_element
        self.top.children.append(Head())
        self.top.children.append(Body())

    def _print_element(self, element: Element, indent_value=0, indent=4, stream=sys.stdout):
        tags = element.full_tags()
        indent_string = " " * indent * indent_value
        if element.children:
            stream.write(indent_string + tags[0] + "\n")
            if element.text_content:
                stream.write(indent_string + element.text_content + "\n")
            for c in element.children:
                self._print_element(c, indent_value=indent_value+1,indent=indent, stream=stream)
            stream.write(indent_string + tags[1] + "\n")
        else:
            stream.write(indent_string + tags[0])
            if element.text_content:
                stream.write(element.text_content)
            stream.write(tags[1] + "\n")

    def print(self, stream=sys.stdout, indent=4):
        stream.write("<!DOCTYPE html>\n")
        html_tags = self.top.tags()
        stream.write(html_tags[0] + "\n")
        head_tags = self.top.children[0].tags()
        stream.write(head_tags[0] + head_tags[1] + "\n")
        self._print_element(self.top.children[1], indent=indent, stream=stream)
        stream.write(html_tags[1])
