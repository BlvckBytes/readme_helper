import os
from enum import Enum
from .a_command import ACommand
from typing import Callable

class Config(Enum):
  SKIP_LEADING_COMMENTS = 1
  SKIP_LEADING_EMPTY = 2
  SKIP_LEADING_PACKAGE = 3
  SKIP_LEADING_IMPORTS = 4
  CODE_LANGUAGE = 5

class Include(ACommand):

  @staticmethod
  def generate_config() -> dict:
    return {
      Config.SKIP_LEADING_COMMENTS.name: 'false',
      Config.SKIP_LEADING_EMPTY.name: 'false',
      Config.SKIP_LEADING_PACKAGE.name: 'false',
      Config.SKIP_LEADING_IMPORTS.name: 'false'
    }

  @staticmethod
  def invoke(readme_lines: list[str], index: int, args: list[str], logger: Callable[[str], None], config: dict):

    if len(args) == 0:
      logger('please specify a target file path')
      return

    target_path = ''.join(args)

    if not '.' in target_path or not os.path.isfile(target_path):
      logger('The provided path does not point at a valid file')
      return

    lines = []
    with open(target_path, 'r') as f:
      lines = f.readlines()

    # Get the target file's extension
    file_ext = os.path.splitext(target_path)[1]

    in_comment = False

    while len(lines) > 0:
      first_line = lines.pop(0)
      line_content = first_line.strip()

      # On a commented out line
      if line_content.startswith('/*') or line_content.startswith('//'):
        in_comment = True

      # Do not add comments when in skip mode
      if ACommand.is_option_enabled(config[Config.SKIP_LEADING_COMMENTS.name]) and in_comment:

        # End single line comment on same line
        if line_content.startswith('//'):
          in_comment = False

        # Multi line comment just ended
        if line_content.endswith('*/'):
          in_comment = False

        continue
      
      # Do not add empty lines when in skip mode
      if ACommand.is_option_enabled(config[Config.SKIP_LEADING_EMPTY.name]) and line_content == '':
        continue

      # Do not add package declarations when in skip mode
      if ACommand.is_option_enabled(config[Config.SKIP_LEADING_PACKAGE.name]) and line_content.startswith('package'):
        continue

      # Do not add import statements when in skip mode
      if ACommand.is_option_enabled(config[Config.SKIP_LEADING_IMPORTS.name]) and line_content.startswith('import'):
        continue
      
      # First line which passed all checks, put the popped line back and stop stripping
      lines.insert(0, first_line)
      break

    # Wrap the remaining lines by a code block of type file_ext
    lines.insert(0, f'```{file_ext[1:]}\n')
    lines.append('```\n')

    # Remove instruction comment
    readme_lines.pop(index)

    # Insert result lines
    for line in reversed(lines):
      readme_lines.insert(index, line)

    logger(f'Inserted transformed contents of {target_path}')

  @staticmethod
  def get_name() -> str:
    return 'include'