import click
import sys
import subprocess

from lexing import Tokenizer
from parsing import Parser
from semantic_analysis import SemanticAnalyzer
from compilation import Compiler
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
        ast = Parser().parse(tokens)
        SemanticAnalyzer().analyze(ast)
        instructions = Compiler().compile(ast)
    except CompilationError as e:
        print(f"{path}:{e}", file=sys.stderr)
        return
    with open(asm_out ,'w') as output:
        output.write('\n'.join(instructions))
    subprocess.run(['gcc', asm_out, '-o', bin_out])


if __name__ == "__main__":
    main()
