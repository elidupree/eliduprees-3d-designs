"""
Slightly hacky tool to help with writing the pyOCCT API wrappers.

Lots of boilerplate is needed, and I don't want to write it manually. My previous approach used internal Python meta-programming, but that made IDEs not understand what functions were available. So, now I use code generation.

This is only for top-level library code, so the design is as follows:

* When you want to inject code, you write `inject_code` as its own line in a module, and pass a string (which you generated however you want).
* The goal is to make it so that every such line also has the generated code under it, wrapped in comments that clearly label it as generated code.
* When the interpreter reaches this call, it automatically checks the current state of the file. If the generated code is already present, it does nothing more. If not present, it throws a GeneratedCodeNeedsUpdate exception.
* When you run this file (`code_generation.py`) as __main__, it walks the current directory, catches those exceptions, and performs the actual code updates. Also, it deletes any code that's labeled as generated and isn't induced by an existing inject_code call.
"""

import inspect
import os.path
import sys
from typing import List, Tuple, Optional

from atomicwrites import atomic_write

# These are magic strings; if you edit them, you'll have to update any existing generated-code files too, or the lines will cease to be acknowledged as machine-generated
generated_code_line_label = " #gen#"
generated_code_start_label = "# == Generated code (don't edit this) =="
generated_code_end_label = "# == End of generated code (don't edit this) =="


def _line_is_generated(line):
    return line.endswith(generated_code_line_label)


def _labeled_line(raw_line):
    target_length = 80
    forced_length = len(raw_line) + len(generated_code_line_label)
    return raw_line + " " * (target_length - forced_length) + generated_code_line_label


def _unlabeled_line(labeled_line):
    assert (_line_is_generated(labeled_line))
    return labeled_line[:-len(generated_code_line_label)].rstrip()


def _full_generated_lines(raw_lines):
    return [
        _labeled_line(line) for line in
        [generated_code_start_label] + raw_lines + [generated_code_end_label]
    ]


def inject_code(raw_generated_code):
    caller = inspect.currentframe().f_back
    file_path = caller.f_globals["__file__"]
    with open(file_path, "r") as file:
        old_code = file.read()
    existing_lines = old_code.splitlines()
    generated_lines = _full_generated_lines(raw_generated_code.split("\n"))
    # f_lineno is 1-indexed, so this is the next line after the call
    generated_code_start_lineidx = caller.f_lineno
    calling_line = existing_lines[caller.f_lineno - 1]
    assert (calling_line.startswith("inject_code(")), "inject_code() should only be called at the top level"

    updated_lines = _lines_with_replacing_generated_code_at(generated_code_start_lineidx, existing_lines, generated_lines)

    if updated_lines != existing_lines:
        new_code = "\n".join(updated_lines)
        raise GeneratedCodeNeedsUpdate(file_path, old_code, new_code, f"{os.path.basename(file_path)}:{caller.f_lineno}")


def _lines_with_removing_generated_code_before_first_generator(original_lines: List[str]) -> List[str]:
    result = []
    for i, line in enumerate(original_lines):
        if line.startswith("inject_code"):
            result.extend(original_lines[i:])
            break

        if not _line_is_generated(line):
            result.append(line)

    return result


def _closest_generated_code_chunk_starting_above(lines: List[str], line_index: int) -> Optional[Tuple[int, int]]:
    end_index = line_index
    try:
        while _line_is_generated(lines[end_index]):
            end_index += 1
        while not _line_is_generated(lines[end_index - 1]):
            end_index -= 1
    except IndexError:
        pass
    start_index = end_index - 1
    try:
        while _line_is_generated(lines[start_index - 1]):
            start_index -= 1
    except IndexError:
        pass

    if start_index > 0:
        return start_index, end_index


def _lines_with_replacing_generated_code_at_start(original_lines: List[str], generated_lines: List[str]) -> List[str]:
    cleaned = _lines_with_removing_generated_code_before_first_generator(original_lines)
    return generated_lines + cleaned


def _lines_with_replacing_generated_code_at(generated_code_start_lineidx: int, original_lines: List[str],
                                            generated_lines: List[str]) -> List[str]:
    return original_lines[:generated_code_start_lineidx] + _lines_with_replacing_generated_code_at_start(
        original_lines[generated_code_start_lineidx:], generated_lines)


def _remove_generated_code_before_first_generator(file_path):
    with open(file_path, "r") as file:
        existing_lines = list(file.read().splitlines())
    cleaned = _lines_with_removing_generated_code_before_first_generator(existing_lines)
    if cleaned != existing_lines:
        with atomic_write(file_path, overwrite=True) as file:
            file.write("\n".join(cleaned))


class GeneratedCodeNeedsUpdate(Exception):
    def __init__(self, file_path, old_code, new_code, caller):
        self.file_path = file_path
        self.old_code = old_code
        self.new_code = new_code
        self.caller = caller
        assert (new_code != old_code), "Constructed GeneratedCodeNeedsUpdate when the code didn't change!"

    def __str__(self):
        return f"Generated code for {self.caller} isn't up-to-date"

    def execute(self):
        print(f"Rewriting generated code for {self.caller}")
        with open(self.file_path, "r") as file:
            if file.read() != self.old_code:
                raise RuntimeError(
                    "Threw GeneratedCodeNeedsUpdate but the file on disk changed before we handled the exception? (Theoretically this should happen almost instantly, AND this doesn't protect from overwrites if the timing is slightly different, but this exception is here to protect from me theoretically-potentially making mistakes in the code where GeneratedCodeNeedsUpdate is handled a macroscopic amount of time later)")
        with atomic_write(self.file_path, overwrite=True) as file:
            file.write(self.new_code)


def _update_all_generated_code(file_path):
    print(f"Checking {file_path}...")
    _remove_generated_code_before_first_generator(file_path)
    attempts = 100
    for attempt in range(attempts):
        with open(file_path) as f:
            source_text = f.read()
        try:
            code = compile(source_text, file_path, "exec")
        except SyntaxError as e:
            # We need special handling for syntax errors, because if you leave a syntax error in the generated code, you can't even rerun the generation.
            lines = source_text.splitlines()
            line_index = (e.end_lineno if hasattr(e, "end_lineno") else e.lineno) - 1

            chunk = _closest_generated_code_chunk_starting_above(lines, line_index)
            if chunk is None:
                print("Warning: Syntax error existed in file with no generated code up to that point")
                break

            start, end = chunk

            def commented_line(line):
                if line.startswith("#"):
                    return line
                return _labeled_line("# " + _unlabeled_line(line))

            # thought of putting this at the start, but don't want to affect line numbers
            # ['"Code disabled due to syntax error (see below)"']+
            lines[start:end] = [commented_line(line) for line in lines[start:end]]
            lines.insert(min(line_index + 1, end), _labeled_line(f'"{" " * e.offset}^ {e} "'))
            with atomic_write(file_path, overwrite=True) as file:
                file.write("\n".join(lines))

            import traceback
            traceback.print_exception(SyntaxError, e, None)
            break

        try:
            module_globals = {"__name__": os.path.splitext(os.path.basename(file_path))[0], "__file__": file_path}
            exec(code, module_globals, module_globals)
            break
        except GeneratedCodeNeedsUpdate as e:
            # In case we generate a syntax error, we want to be able to reload 1 more time (hopefully this will never matter because we won't run out of attempts, but just in case)
            if attempt + 1 < attempts:
                e.execute()
        except:
            import traceback
            ty, exc, tb = sys.exc_info()
            while inspect.getframeinfo(tb.tb_frame).filename != file_path:
                tb = tb.tb_next
            traceback.print_exception(ty, exc, tb)
            break


def this_file_uses_code_generation():
    caller = inspect.currentframe().f_back
    if caller.f_globals["__name__"] == "__main__":
        _update_all_generated_code(caller.f_globals["__file__"])
        sys.exit(0)


def _main():
    from code_generation import _update_all_generated_code
    updates_needed = []
    for root, dirs, files in os.walk(os.path.dirname(__file__)):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                imported = False
                with open(file_path) as f:
                    for line in f:
                        if line == "from code_generation import inject_code\n":
                            imported = True
                        if imported and line.startswith("inject_code("):
                            updates_needed.append(file_path)
                            break
    for file_path in updates_needed:
        _update_all_generated_code(file_path)


if __name__ == "__main__":
    _main()
