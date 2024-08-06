import subprocess
import argparse
import os
import sys

def update_readme(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    new_lines = []
    in_code_block = False
    code_block_lines = []

    for line in lines:
        if line.strip() == '```bash':
            in_code_block = True
            code_block_lines.append(line)
        elif line.strip() == '```' and in_code_block:
            in_code_block = False

            # Check if the command line starts with $
            if code_block_lines and len(code_block_lines) > 1:
                command_line = code_block_lines[1].strip()
                if command_line.startswith('$ '):
                    command = command_line[2:]
                    print(f"Executing: {command}")

                    try:
                        # Use bash to execute the command
                        process = subprocess.Popen(f"bash -c \"{command}\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                        stdout_lines = []
                        stderr_lines = []
                        for stdout_line in iter(process.stdout.readline, ''):
                            sys.stdout.write(stdout_line)
                            stdout_lines.append(stdout_line)
                        for stderr_line in iter(process.stderr.readline, ''):
                            sys.stderr.write(stderr_line)
                            stderr_lines.append(stderr_line)

                        process.stdout.close()
                        process.stderr.close()
                        process.wait()

                        stdout = ''.join(stdout_lines)
                        stderr = ''.join(stderr_lines)

                        if process.returncode == 0:
                            result = f'$ {command}\n{stdout}'
                        else:
                            result = f'$ {command}\nError: {stderr}\n'
                    except Exception as e:
                        result = f'$ {command}\nError: {e}\n'

                    # Replace the original block with the result
                    new_lines.append('```bash\n')
                    new_lines.append(result)
                    new_lines.append('```\n')
                else:
                    # If the next line doesn't start with $, retain original block
                    new_lines.extend(code_block_lines)
                    new_lines.append('```\n')
            else:
                new_lines.extend(code_block_lines)
                new_lines.append('```\n')

            code_block_lines = []
        elif in_code_block:
            code_block_lines.append(line)
        else:
            new_lines.append(line)

    with open(readme_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Update README.md with the output of bash commands.')
    parser.add_argument('path', nargs='?', default=os.path.join(os.getcwd(), 'README.md'),
                        help='Path to the README.md file (default: ./README.md)')
    
    args = parser.parse_args()
    update_readme(args.path)
