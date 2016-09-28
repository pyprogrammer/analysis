from textx.metamodel import metamodel_from_file
from textx.export import model_export

def parse(filename):
    metamodel = metamodel_from_file("trace.tx")
    model = metamodel.model_from_file(filename)
    return model

def main():
    parse("examples/simple.log")


if __name__ == "__main__":
    main()