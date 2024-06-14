import click
from compilation import Compiler
from preprocessing import Preprocessor
from tokening import Tokenizer


@click.command()
@click.argument("path")
@click.option("-o", "--output", default="a.out")
def main(path: str, output: str):
    with open(path) as file:
        content = file.read()
    content = Preprocessor().preprocess(content)
    tokens = Tokenizer().tokenize(content)
    with open(output,'w') as output:
        compiler = Compiler(output)
        compiler.compile()

if __name__ == "__main__":
    main()
