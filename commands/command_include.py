import os
from enum import Enum
from .a_command import ACommand
from typing import Callable

class Config(Enum):
  SKIP_LEADING_COMMENTS = 1
  SKIP_LEADING_EMPTY = 2
  SKIP_LEADING_PACKAGE = 3
  SKIP_LEADING_IMPORTS = 4
  WRAP_IN_COLLAPSIBLE = 5

class Include(ACommand):

  @staticmethod
  def generate_config() -> dict:
    return {
      Config.SKIP_LEADING_COMMENTS.name: 'false',
      Config.SKIP_LEADING_EMPTY.name: 'false',
      Config.SKIP_LEADING_PACKAGE.name: 'false',
      Config.SKIP_LEADING_IMPORTS.name: 'false',
      Config.WRAP_IN_COLLAPSIBLE.name: 'false'
    }

  @staticmethod
  def invoke(readme_lines: list[str], base_path: str, index: int, args: list[str], logger: Callable[[str], None], config: dict):

    if len(args) == 0:
      logger('please specify a target file path')
      return

    target_path = ''.join(args)

    if not target_path.startswith('/'):
      target_path = os.path.join(base_path, target_path)

    if not '.' in target_path or not os.path.isfile(target_path):
      logger(f'The provided path does not point at a valid file ({target_path})')
      return

    lines = []
    with open(target_path, 'r') as f:
      lines = f.readlines()

    # Get the target file's extension
    file_ext = os.path.splitext(target_path)[1]

    # Configuration
    skip_leading_comments = ACommand.is_option_enabled(config[Config.SKIP_LEADING_COMMENTS.name])
    skip_leading_empty    = ACommand.is_option_enabled(config[Config.SKIP_LEADING_EMPTY.name])
    skip_leading_package  = ACommand.is_option_enabled(config[Config.SKIP_LEADING_PACKAGE.name])
    skip_leading_imports  = ACommand.is_option_enabled(config[Config.SKIP_LEADING_IMPORTS.name])

    in_comment = False

    filtered_lines = []
    for i in range(0, len(lines)):
      line_content = lines[i].strip()
      is_package = line_content.startswith('package')
      is_import = line_content.startswith('import')

      if is_import and skip_leading_imports:
        continue

      if is_package and skip_leading_package:
        continue

      if line_content.startswith('/*'):
        in_comment = True

      if skip_leading_comments and in_comment:
        if line_content.endswith('*/'):
          in_comment = False
        continue

      if skip_leading_empty and line_content == '':
        continue

      # Begin of file encountered, no more stripping from here on out,
      # just copy the remaining lines over and stop the iteration
      if not is_package and not is_import and not in_comment and line_content != '':

        # The file begin shouldn't be directly glued onto any of the previous non-skipped lines
        len_filtered_lines = len(filtered_lines)
        if len_filtered_lines > 0 and filtered_lines[len_filtered_lines - 1].strip() != '':
          filtered_lines.append('\n')

        filtered_lines.extend(lines[i:])
        break

      filtered_lines.append(lines[i])

    # Wrap the remaining lines by a code block of type file_ext
    filtered_lines.insert(0, f'```{file_ext[1:]}\n')
    filtered_lines.append('```\n')

    # Wrap the whole block into a details tag where the summary is going to display the file name of the target path
    if ACommand.is_option_enabled(config[Config.WRAP_IN_COLLAPSIBLE.name]):
      # Wrap in details tag
      filtered_lines.insert(0, f'<summary>{target_path[target_path.rindex("/") + 1:]}</summary>\n\n')
      filtered_lines.insert(0, '<details>\n')
      filtered_lines.append('</details>\n\n')

    # Remove instruction comment
    readme_lines.pop(index)

    # Insert result lines
    for line in reversed(filtered_lines):
      readme_lines.insert(index, line)

    logger(f'Inserted transformed contents of {target_path}')

  @staticmethod
  def get_name() -> str:
    return 'include'