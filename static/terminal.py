import sys
from io import StringIO
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

def parse_command(command):
    """Parse a command string into command, args, and redirection."""
    try:
        # First handle redirection
        output_file = None
        append_mode = False
        
        # Handle >> before > to avoid partial matches
        if '>>' in command:
            parts = command.split('>>', 1)
            command = parts[0]
            output_file = parts[1].strip()
            append_mode = True
        elif '>' in command:
            parts = command.split('>', 1)
            command = parts[0]
            output_file = parts[1].strip()
        
        # Use shlex to properly handle quotes and escapes
        args = shlex.split(command)
        if not args:
            return None, [], None, False
            
        cmd = args[0]
        # Process each argument to handle escape sequences
        processed_args = [process_arg(arg) for arg in args[1:]]
        
        # If output_file was quoted, remove the quotes
        if output_file:
            output_file = shlex.split(output_file)[0]
            
        return cmd, processed_args, output_file, append_mode
    except Exception as e:
        print(f"Error parsing command: {str(e)}")
        return None, [], None, False

def execute_command(command):
    """Execute a command string and return the output."""
    # Parse the command
    cmd, args, output_file, append_mode = parse_command(command)
    if cmd is None:
        return ""
    
    # Capture the output for potential redirection
    output_buffer = StringIO()
    original_stdout = sys.stdout
    sys.stdout = output_buffer
    
    try:
        if cmd == 'cd':
            if not args:
                print(os.getcwd())
            else:
                os.chdir(args[0])
        elif cmd == 'ls':
            # Parse options
            show_hidden = '-a' in args
            long_format = '-l' in args
            recursive = '-R' in args
            
            # Remove options from args
            args = [arg for arg in args if not arg.startswith('-')]
            
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
        elif cmd == 'pwd':
            print(os.getcwd())
        elif cmd == 'mkdir':
            os.makedirs(args[0], exist_ok=True)
        elif cmd == 'rm':
            if '-r' in args or '-rf' in args:
                args = [arg for arg in args if not arg.startswith('-')]
                shutil.rmtree(args[0])
            else:
                os.remove(args[0])
        elif cmd == 'rmdir':
            os.rmdir(args[0])
        elif cmd == 'touch':
            pathlib.Path(args[0]).touch()
        elif cmd == 'cat':
            if output_file:
                content = []
                for file in args:
                    with open(file, 'r') as f:
                        content.append(f.read())
                write_output(''.join(content), output_file, append_mode)
            else:
                for file in args:
                    with open(file, 'r') as f:
                        print(f.read(), end='')
        elif cmd == 'echo':
            # Join arguments with a single space, no additional processing needed
            # since arguments are already processed by process_arg
            content = ' '.join(args)
            
            # For echo, we want to print exactly what's in content, without adding
            # an extra newline if the content already ends with one
            if output_file:
                # For files, we still want to ensure there's exactly one trailing newline
                write_output(content.rstrip('\n'), output_file, append_mode)
            else:
                # For terminal output, print exactly what's in content
                # If it ends with \n, that will be preserved
                # If it doesn't, no extra newline will be added
                print(content, end='')
                # Only add a newline if the content doesn't end with one
                if not content.endswith('\n'):
                    print()
        elif cmd == 'find':
            start_dir = '.' if not args else args[0]
            pattern = '*' if len(args) <= 1 else args[1]
            
            for root, dirs, files in os.walk(start_dir):
                for name in files:
                    if fnmatch.fnmatch(name, pattern):
                        print(os.path.join(root, name))
        elif cmd == 'grep':
            pattern = args[0]
            files = args[1:] if len(args) > 1 else ['.']
            
            for file in files:
                if os.path.isfile(file):
                    with open(file, 'r') as f:
                        for i, line in enumerate(f, 1):
                            if pattern in line:
                                print(f"{file}:{i}:{line.rstrip()}")
        elif cmd == 'cp':
            if '-r' in args:
                args = [arg for arg in args if not arg.startswith('-')]
                shutil.copytree(args[0], args[1])
            else:
                shutil.copy2(args[0], args[1])
        elif cmd == 'mv':
            shutil.move(args[0], args[1])
        elif cmd == 'head':
            n = 10
            if args[0].startswith('-'):
                n = int(args[0][1:])
                args = args[1:]
            
            with open(args[0], 'r') as f:
                for _ in range(n):
                    line = f.readline()
                    if not line:
                        break
                    print(line.rstrip())
        elif cmd == 'tail':
            n = 10
            if args[0].startswith('-'):
                n = int(args[0][1:])
                args = args[1:]
            
            with open(args[0], 'r') as f:
                lines = f.readlines()
                for line in lines[-n:]:
                    print(line.rstrip())
        else:
            print(f"{cmd}: command not found")
    
    finally:
        # Reset stdout and get the captured output
        sys.stdout = original_stdout
        content = output_buffer.getvalue()
        
        # Handle the output
        if output_file:
            write_output(content, output_file, append_mode)
        
        # Return the content instead of printing it
        return content 