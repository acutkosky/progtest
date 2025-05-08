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
            os.makedirs(command.args[0], exist_ok=True)
        elif command.cmd == 'rm':
            if '-r' in command.args or '-rf' in command.args:
                args = [arg for arg in command.args if not arg.startswith('-')]
                shutil.rmtree(args[0])
            else:
                os.remove(command.args[0])
        elif command.cmd == 'rmdir':
            os.rmdir(command.args[0])
        elif command.cmd == 'touch':
            pathlib.Path(command.args[0]).touch()
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
            pattern = command.args[0]
            files = command.args[1:] if len(command.args) > 1 else ['-']
            
            if files == ['-']:
                # Read from stdin
                for line in sys.stdin:
                    if pattern in line:
                        sys.stdout.write(line)
            else:
                for file in files:
                    with open(file, 'r') as f:
                        for i, line in enumerate(f, 1):
                            if pattern in line:
                                if len(files) > 1:
                                    print(f"{file}:{i}:{line}", end='')
                                else:
                                    print(line, end='')
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
        
    # Create a StringIO to capture terminal output
    terminal_output = StringIO()
    
    # If the last command outputs to stdout, redirect it to our terminal_output
    if commands[-1].output_file == sys.stdout:
        commands[-1] = commands[-1]._replace(output_file=terminal_output)
    
    # Execute the command sequence
    execute_command_sequence(commands)
    
    # Get the output
    if isinstance(commands[-1].output_file, StringIO):
        commands[-1].output_file.seek(0)
        output = commands[-1].output_file.read()
    else:
        output = ""
        
    return output 