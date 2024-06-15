import click
import sys
import subprocess

from compilation import Compiler
from tokenization import Tokenizer
from errors import CompilationError


@click.command()
@click.argument("path")
@click.option("-o", "--output", "bin_out", default="a.out")
def main(path: str, bin_out: str):
    asm_out = bin_out + '.S'
    with open(path) as file:
        content = file.read()
    try:
        tokens = Tokenizer().tokenize(content)
        with open(asm_out ,'w') as output:
            compiler = Compiler(output)
            compiler.compile(tokens)
    except CompilationError as e:
        print(f"{path}:{e}", file=sys.stderr)
    subprocess.run(['gcc', asm_out, '-o', bin_out])


if __name__ == "__main__":
    main()
