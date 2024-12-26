# declopy/cli.py

import sys
import os
import fire

from declo.compiler import compile_declo_to_python

def _check_declo_file_extension(filepath: str):
    """
    Ensure the input file ends with .declo, otherwise raise an error.
    """
    if not filepath.endswith(".declo"):
        raise ValueError(f"Error: Only '.declo' files are supported. Got '{filepath}'")

def compile_file(input_file: str, output_file: str = None):
    """
    Read a Declo file, compile it to Python, and optionally write to an output file.

    Usage:
      declopy compile_file path/to/input.declo --output_file=path/to/output.py
    """
    _check_declo_file_extension(input_file)

    if not os.path.isfile(input_file):
        print(f"Error: file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    compiled_code = compile_declo_to_python(code)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as fw:
            fw.write(compiled_code)
        print(f"Compiled output saved to '{output_file}'.")
    else:
        # If no output file is specified, just print to stdout
        print(compiled_code)

def run_file(input_file: str):
    """
    Compile the input Declo file to Python code in-memory, then execute it.

    Usage:
      declopy run_file path/to/input.declo
    """
    _check_declo_file_extension(input_file)

    if not os.path.isfile(input_file):
        print(f"Error: file '{input_file}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    compiled_code = compile_declo_to_python(code)
    
    local_namespace = {}
    exec(compiled_code, {}, local_namespace)

def main():
    """
    Entrypoint for the declopy command line interface.
    """
    fire.Fire({
        'compile': compile_file,
        'run': run_file,
    })
