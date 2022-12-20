import sys
import os

from commands.command_include import Include
from commands.command_toc import Toc
from commands.a_command import ACommand

if len(sys.argv) < 3:
  print(f'Usage: {sys.argv[0]} <input_path> <output_path>')
  sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

base_path = os.path.dirname(input_path)

if not os.path.isfile(input_path) or not input_path.endswith('.md'):
  print('Invalid input path, not a markdown file')
  sys.exit(1)

if not output_path.endswith('.md'):
  print('Invalid output path, not a markdown file')
  sys.exit(1)

readme_lines = []
with open(input_path, 'r') as f:
  readme_lines = f.readlines()

commands: list[ACommand] = [Include, Toc]
configs = {}
invokes = {}

for command in commands:
  name = command.get_name()
  configs[name] = command.generate_config()
  invokes[name] = command.invoke

i = len(readme_lines) - 1
in_code_block = False

# Loop file bottom up as the lines grow downwards when substituting
while i > 0:
  line = readme_lines[i]
  line_index = i
  line_number = i + 1
  i -= 1

  if line.strip().startswith("```"):
    in_code_block = not in_code_block

  if in_code_block:
    continue

  # Not a single line comment
  if not (line.strip().startswith("<!--") and line.strip().endswith("-->")):
    continue

  # Parse comment text
  comment_content = line[line.index("<!--") + 4 : line.index("-->")].strip()

  # Not ment as an instruction
  if not comment_content.startswith('#'):
    continue
  
  # Split on space, <command> <args>
  command_info = comment_content[1:].split(" ")
  command = command_info[0].lower()
  command_args = command_info[1:]

  command_logger = lambda x: print(f'{command}@{line_number}: {x}')

  if command == "configure":

    if len(command_args) < 3:
      command_logger('Missing arguments, syntax is: #configure <command> <key> <value>')
      continue

    target_command = command_args[0]

    if target_command not in configs:
      command_logger(f'Unknown target command {target_command}, available: {", ".join(configs.keys())}')
      continue

    target_config = configs[target_command]
    target_key = command_args[1]

    if target_key not in target_config:
      command_logger(f'Unknown target key {target_key}, available: {", ".join(target_config.keys())}')
      continue

    target_value = ''.join(command_args[2:])
    target_config[target_key] = target_value

    readme_lines.pop(line_index)

    command_logger(f'Set {target_key}={target_value} for command {target_command}')
    continue

  # Unregistered command
  if command not in invokes:
    print(f'Unknown command invocation "{command}" at line {line_number}')
    continue

  # Invoke
  invokes[command](readme_lines, base_path, line_index, command_args, command_logger, configs[command])

with open(output_path, 'w') as f:
  f.writelines(readme_lines)