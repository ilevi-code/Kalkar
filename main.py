import click
import sys

from compilation import Compiler
from tokenization import Tokenizer
from errors import CompilationError


@click.command()
@click.argument("path")
@click.option("-o", "--output", default="a.out")
def main(path: str, output: str):
    with open(path) as file:
        content = file.read()
    try:
        tokens = Tokenizer().tokenize(content)
        with open(output,'w') as output:
            compiler = Compiler(output)
            compiler.compile()
    except CompilationError as e:
        print(f"{path}:{e}", file=sys.stderr)


if __name__ == "__main__":
    main()
