import sys
from io import StringIO, TextIOBase
from typing import NamedTuple
import os
import shutil
import stat
import datetime
import glob
import fnmatch
import pathlib
import json
import shlex  # For proper shell-like argument parsing
import re


def process_arg(arg):
    """Process a command argument, handling quotes and escape sequences properly."""
    try:
        # If the argument is already processed by shlex, we just need to handle escape sequences
        if not arg:
            return arg
            
        # Handle escape sequences
        result = ""
        i = 0
        while i < len(arg):
            if arg[i] == '\\' and i + 1 < len(arg):
                if arg[i + 1] == 'n':
                    result += '\n'
                    i += 2
                elif arg[i + 1] == 't':
                    result += '\t'
                    i += 2
                elif arg[i + 1] in ['"', "'", '\\']:
                    result += arg[i + 1]
                    i += 2
                else:
                    # Keep unrecognized escape sequences as-is
                    result += '\\' + arg[i + 1]
                    i += 2
            else:
                result += arg[i]
                i += 1
                
        return result
    except Exception as e:
        print(f"Error processing argument: {str(e)}")
        return arg

def write_output(content, file_path, append=False):
    mode = 'a' if append else 'w'
    with open(file_path, mode) as f:
        # Ensure content ends with a newline if it doesn't already
        if not content.endswith('\n'):
            content += '\n'
        f.write(content)

class Command(NamedTuple):
    cmd: str
    args: list[str]
    output_file: StringIO | TextIOBase
    input_file: StringIO | TextIOBase
    append_mode: bool

def parse_command(command):
    """Parse a command string into a list of Command objects with proper I/O handling."""
    try:
        terms = shlex.split(command)
        if not terms:
            return []

        # First split into pipe segments
        pipe_segments = []
        current_segment = []
        
        for term in terms:
            if term == '|':
                if current_segment:
                    pipe_segments.append(current_segment)
                    current_segment = []
            else:
                current_segment.append(term)
        if current_segment:
            pipe_segments.append(current_segment)
            
        if not pipe_segments:
            return []
            
        # Process each segment for redirections and create Command objects
        commands = []
        for i, segment in enumerate(pipe_segments):
            cmd_terms = []
            input_file = StringIO()  # Default to empty input
            output_file = sys.stdout  # Default to stdout
            append_mode = False
            
            # Process terms for redirections
            j = 0
            while j < len(segment):
                term = segment[j]
                if term in ['<', '>', '>>']: 
                    if j + 1 >= len(segment):
                        raise ValueError(f"Missing file argument for {term}")
                    file_path = segment[j + 1]
                    
                    if term == '<':
                        input_file = open(file_path, 'r')
                    elif term == '>':
                        output_file = open(file_path, 'w')
                    elif term == '>>':
                        output_file = open(file_path, 'a')
                        append_mode = True
                    j += 2
                else:
                    cmd_terms.append(term)
                    j += 1
            
            if not cmd_terms:
                raise ValueError("Empty command")
                
            # Create Command object
            cmd = Command(
                cmd=cmd_terms[0],
                args=[process_arg(arg) for arg in cmd_terms[1:]],
                input_file=input_file,
                output_file=output_file,
                append_mode=append_mode
            )
            commands.append(cmd)
            
        # Connect pipes - this is where we properly connect input/output
        for i in range(len(commands) - 1):
            # Create a shared StringIO buffer for the pipe
            shared_buffer = StringIO()
            
            # The current command writes to the buffer
            commands[i] = commands[i]._replace(output_file=shared_buffer)
            
            # The next command reads from the same buffer
            # Only replace its input if it wasn't set by < redirection
            if isinstance(commands[i + 1].input_file, StringIO) and not commands[i + 1].input_file.getvalue():
                commands[i + 1] = commands[i + 1]._replace(input_file=shared_buffer)
            
        return commands

    except Exception as e:
        print(f"Error parsing command: {str(e)}")
        return []

def execute_single_command(command: Command) -> None:
    """Execute a single Command object with proper I/O handling."""
    # Save original stdin/stdout
    original_stdin = sys.stdin
    original_stdout = sys.stdout
    
    try:
        # Set up I/O redirection
        sys.stdin = command.input_file
        sys.stdout = command.output_file
        
        if command.cmd == 'cd':
            if not command.args:
                print(os.getcwd())
            else:
                os.chdir(command.args[0])
        elif command.cmd == 'ls':
            # Parse options
            show_hidden = '-a' in command.args
            long_format = '-l' in command.args
            recursive = '-R' in command.args
            
            # Remove options from args
            args = [arg for arg in command.args if not arg.startswith('-')]
            
            # Get target directory
            target = '.' if not args else args[0]
            
            if os.path.isdir(target):
                def list_dir(dir_path, indent=''):
                    files = os.listdir(dir_path)
                    if not show_hidden:
                        files = [f for f in files if not f.startswith('.')]
                    
                    if long_format:
                        for f in files:
                            path = os.path.join(dir_path, f)
                            st = os.stat(path)
                            mode = stat.filemode(st.st_mode)
                            size = st.st_size
                            mtime = datetime.datetime.fromtimestamp(st.st_mtime).strftime('%b %d %H:%M')
                            print(f"{indent}{mode} {size:8d} {mtime} {f}")
                    else:
                        print(indent + '\n'.join(files))
                    
                    if recursive:
                        for f in files:
                            path = os.path.join(dir_path, f)
                            if os.path.isdir(path):
                                print(f"\n{indent}{path}:")
                                list_dir(path, indent + '  ')
                
                list_dir(target)
            else:
                print(f"ls: cannot access '{target}': No such file or directory")
        elif command.cmd == 'pwd':
            print(os.getcwd())
        elif command.cmd == 'mkdir':
            # Parse options
            make_parents = '-p' in command.args
            # Get non-option arguments
            dirs = [arg for arg in command.args if not arg.startswith('-')]
            
            try:
                for dir_path in dirs:
                    if make_parents:
                        os.makedirs(dir_path, exist_ok=True)
                    else:
                        os.mkdir(dir_path)
            except FileExistsError:
                if not make_parents:
                    print(f"mkdir: cannot create directory '{dir_path}': File exists")
            except FileNotFoundError:
                if not make_parents:
                    print(f"mkdir: cannot create directory '{dir_path}': No such file or directory")
        elif command.cmd == 'chmod':
            if not command.args:
                print("chmod: missing operand")
                return
                
            mode_str = command.args[0]
            target = command.args[1] if len(command.args) > 1 else None
            
            if not target:
                print("chmod: missing operand after", mode_str)
                return
                
            try:
                # Handle symbolic mode (e.g., a+x)
                if '+' in mode_str or '-' in mode_str or '=' in mode_str:
                    current_mode = stat.S_IMODE(os.stat(target).st_mode)
                    
                    # Parse the symbolic mode
                    # Handle both 'a+x' and '+x' formats
                    if mode_str[0] in 'ugo':
                        who = mode_str[0]
                        op = mode_str[1]
                        what = mode_str[2:]
                    else:
                        who = 'a'  # Default to 'all' if no who specified
                        if mode_str[0] in '+-=':
                            op = mode_str[0]
                            what = mode_str[1:]
                        else:
                            who = mode_str[0]  # Explicit 'a' specified
                            op = mode_str[1]
                            what = mode_str[2:]
                    
                    # Initialize permission masks
                    if what == 'x':
                        if who == 'a':
                            mask = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                        elif who == 'u':
                            mask = stat.S_IXUSR
                        elif who == 'g':
                            mask = stat.S_IXGRP
                        else:  # who == 'o'
                            mask = stat.S_IXOTH
                            
                        # Apply the operation
                        if op == '+':
                            new_mode = current_mode | mask
                        elif op == '-':
                            new_mode = current_mode & ~mask
                        else:  # op == '='
                            new_mode = (current_mode & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)) | mask
                    
                    # Apply the mode change
                    os.chmod(target, new_mode)
                # Handle octal mode
                else:
                    os.chmod(target, int(mode_str, 8))
                    
            except ValueError:
                print(f"chmod: invalid mode: '{mode_str}'")
            except FileNotFoundError:
                print(f"chmod: cannot access '{target}': No such file or directory")
            except Exception as e:
                print(f"chmod: error: {str(e)}")
                
        elif command.cmd == 'rm':
            if '-r' in command.args or '-rf' in command.args:
                args = [arg for arg in command.args if not arg.startswith('-')]
                shutil.rmtree(args[0])
            else:
                os.remove(command.args[0])
        elif command.cmd == 'rmdir':
            os.rmdir(command.args[0])
        elif command.cmd == 'touch':
            if not command.args:
                print("touch: missing file operand")
                return
            
            for file in command.args:
                try:
                    pathlib.Path(file).touch()
                except OSError as e:
                    print(f"touch: cannot touch '{file}': {str(e)}", file=sys.stderr)
        elif command.cmd == 'cat':
            if not command.args:
                # If no args, cat reads from stdin
                while True:
                    try:
                        line = sys.stdin.readline()
                        if not line:
                            break
                        sys.stdout.write(line)
                    except KeyboardInterrupt:
                        break
            else:
                for file in command.args:
                    with open(file, 'r') as f:
                        print(f.read(), end='')
        elif command.cmd == 'echo':
            # Join arguments with a single space
            content = ' '.join(command.args)
            print(content)
        elif command.cmd == 'grep':
            # Parse options and get pattern
            invert_match = '-v' in command.args
            args = [arg for arg in command.args if not arg.startswith('-')]
            pattern = args[0] if args else ''
            files = args[1:] if len(args) > 1 else ['-']
            
            try:
                regex = re.compile(pattern)
            except re.error:
                print(f"grep: invalid pattern: {pattern}", file=sys.stderr)
                return
            
            if files == ['-']:
                # Read from stdin
                for line in sys.stdin:
                    matches = bool(regex.search(line))
                    if matches != invert_match:  # XOR with invert_match
                        sys.stdout.write(line)
            else:
                for file in files:
                    with open(file, 'r') as f:
                        for i, line in enumerate(f, 1):
                            matches = bool(regex.search(line))
                            if matches != invert_match:  # XOR with invert_match
                                if len(files) > 1:
                                    print(f"{file}:{i}:{line}", end='')
                                else:
                                    print(line, end='')
        elif command.cmd == 'sort':
            # Parse options
            numeric = '-n' in command.args
            reverse = '-r' in command.args
            
            # Get input source (file or stdin)
            files = [arg for arg in command.args if not arg.startswith('-')]
            lines = []
            
            if not files:  # Read from stdin
                lines = sys.stdin.readlines()
            else:
                for file in files:
                    with open(file, 'r') as f:
                        lines.extend(f.readlines())
            
            # Sort the lines
            if numeric:
                # Extract leading numbers for numeric sort
                def get_num(line):
                    parts = line.strip().split()
                    try:
                        return float(parts[0]) if parts else 0
                    except ValueError:
                        return 0
                lines.sort(key=get_num, reverse=reverse)
            else:
                lines.sort(reverse=reverse)
            
            # Output sorted lines
            for line in lines:
                print(line, end='')
                
        elif command.cmd == 'uniq':
            # Parse options
            count = '-c' in command.args
            
            # Get input source (file or stdin)
            files = [arg for arg in command.args if not arg.startswith('-')]
            lines = []
            
            if not files:  # Read from stdin
                lines = sys.stdin.readlines()
            else:
                with open(files[0], 'r') as f:
                    lines = f.readlines()
            
            # Process lines
            if not lines:
                return
                
            current_line = lines[0]
            current_count = 1
            
            for line in lines[1:]:
                if line == current_line:
                    current_count += 1
                else:
                    if count:
                        print(f"{current_count:>7} {current_line}", end='')
                    else:
                        print(current_line, end='')
                    current_line = line
                    current_count = 1
            
            # Print last group
            if count:
                print(f"{current_count:>7} {current_line}", end='')
            else:
                print(current_line, end='')
                
        elif command.cmd == 'wc':
            # Parse options
            count_lines = '-l' in command.args
            count_words = '-w' in command.args
            count_chars = '-c' in command.args
            # Default to all if no options specified
            if not (count_lines or count_words or count_chars):
                count_lines = count_words = count_chars = True
            
            # Get input source (file or stdin)
            files = [arg for arg in command.args if not arg.startswith('-')]
            if not files:  # Read from stdin
                content = sys.stdin.read()
                lines = content.splitlines()
                words = content.split()
                chars = len(content)
                
                if count_lines:
                    print(f"{len(lines):>7}", end='')
                if count_words:
                    print(f"{len(words):>7}", end='')
                if count_chars:
                    print(f"{chars:>7}", end='')
                print()
            else:
                total_lines = total_words = total_chars = 0
                for file in files:
                    with open(file, 'r') as f:
                        content = f.read()
                        lines = content.splitlines()
                        words = content.split()
                        chars = len(content)
                        
                        if count_lines:
                            print(f"{len(lines):>7}", end='')
                            total_lines += len(lines)
                        if count_words:
                            print(f"{len(words):>7}", end='')
                            total_words += len(words)
                        if count_chars:
                            print(f"{chars:>7}", end='')
                            total_chars += chars
                        print(f" {file}")
                
                if len(files) > 1:
                    if count_lines:
                        print(f"{total_lines:>7}", end='')
                    if count_words:
                        print(f"{total_words:>7}", end='')
                    if count_chars:
                        print(f"{total_chars:>7}", end='')
                    print(" total")
        elif command.cmd == 'find':
            # Parse options
            if len(command.args) < 1:
                print("find: missing path operand")
                return
                
            start_path = '.'  # Default to current directory
            name_pattern = None
            file_type = None  # 'f' for regular files, 'd' for directories
            
            # Parse arguments
            i = 0
            while i < len(command.args):
                if command.args[i] == '-name':
                    if i + 1 >= len(command.args):
                        print("find: missing argument to '-name'")
                        return
                    name_pattern = command.args[i + 1]
                    # Remove quotes if present
                    if (name_pattern.startswith("'") and name_pattern.endswith("'")) or \
                       (name_pattern.startswith('"') and name_pattern.endswith('"')):
                        name_pattern = name_pattern[1:-1]
                    i += 2
                elif command.args[i] == '-type':
                    if i + 1 >= len(command.args):
                        print("find: missing argument to '-type'")
                        return
                    file_type = command.args[i + 1]
                    if file_type not in ['f', 'd']:
                        print(f"find: Unknown argument to -type: {file_type}")
                        return
                    i += 2
                else:
                    start_path = command.args[i]
                    i += 1
            
            # Walk directory tree
            try:
                found_files = []
                for root, dirs, files in os.walk(start_path):
                    if file_type == 'd':
                        # Handle directory matches
                        if name_pattern:
                            matching_dirs = fnmatch.filter(dirs, name_pattern)
                            for dir in matching_dirs:
                                found_path = os.path.join(root, dir)
                                found_files.append(found_path)
                                print(found_path)
                        else:
                            print(root)
                            for dir in dirs:
                                found_path = os.path.join(root, dir)
                                found_files.append(found_path)
                                print(found_path)
                    else:  # file_type == 'f' or None
                        # Handle file matches (default behavior is to match files)
                        if name_pattern:
                            matching_files = fnmatch.filter(files, name_pattern)
                            for file in matching_files:
                                found_path = os.path.join(root, file)
                                found_files.append(found_path)
                                print(found_path)
                        else:
                            for file in files:
                                found_path = os.path.join(root, file)
                                found_files.append(found_path)
                                print(found_path)
                return found_files  # Return list for piping
            except OSError as e:
                print(f"find: '{start_path}': {str(e)}", file=sys.stderr)
                return []
        else:
            print(f"{command.cmd}: command not found", file=sys.stderr)
            
    finally:
        # Always restore original stdin/stdout
        sys.stdin = original_stdin
        sys.stdout = original_stdout
        
        # If we used StringIO buffers, seek to start for reading
        if isinstance(command.output_file, StringIO):
            command.output_file.seek(0)
        if isinstance(command.input_file, StringIO):
            command.input_file.seek(0)

def execute_command_sequence(commands: list[Command]) -> None:
    """Execute a sequence of commands connected by pipes."""
    if not commands:
        return
        
    try:
        # Execute each command in sequence
        for cmd in commands:
            execute_single_command(cmd)
            
            # If this command writes to a StringIO that's used as input for the next command,
            # we need to seek to the start of the buffer for reading
            if isinstance(cmd.output_file, StringIO):
                cmd.output_file.seek(0)
                
    finally:
        # Clean up any file handles
        for cmd in commands:
            if isinstance(cmd.input_file, TextIOBase) and not isinstance(cmd.input_file, StringIO):
                cmd.input_file.close()
            if isinstance(cmd.output_file, TextIOBase) and not isinstance(cmd.output_file, StringIO):
                cmd.output_file.close()

def execute_command(command_str: str) -> str:
    """Parse and execute a command string, returning the output for the terminal."""
    # Parse the command string into a sequence of Command objects
    commands = parse_command(command_str)
    if not commands:
        return ""
        
    # Create StringIO buffers to capture both stdout and stderr
    terminal_output = StringIO()
    error_output = StringIO()
    
    # Save original stderr
    original_stderr = sys.stderr
    sys.stderr = error_output
    
    try:
        # If the last command outputs to stdout, redirect it to our terminal_output
        if commands[-1].output_file == sys.stdout:
            commands[-1] = commands[-1]._replace(output_file=terminal_output)
        
        # Execute the command sequence
        execute_command_sequence(commands)
        
        # Get the output and errors
        error_output.seek(0)
        errors = error_output.read()
        
        if isinstance(commands[-1].output_file, StringIO):
            commands[-1].output_file.seek(0)
            output = commands[-1].output_file.read()
        else:
            output = ""
            
        # Combine output and errors in the right order
        return output + errors
        
    finally:
        # Restore stderr
        sys.stderr = original_stderr
        
        # Clean up any file handles
        for cmd in commands:
            if isinstance(cmd.input_file, TextIOBase) and not isinstance(cmd.input_file, StringIO):
                cmd.input_file.close()
            if isinstance(cmd.output_file, TextIOBase) and not isinstance(cmd.output_file, StringIO):
                cmd.output_file.close() 