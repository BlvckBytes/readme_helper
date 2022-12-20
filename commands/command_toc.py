import os
from enum import Enum
from .a_command import ACommand
from typing import Callable

class Config(Enum):
  HEADLINE = 1

class Toc(ACommand):

  @staticmethod
  def generate_config() -> dict:
    return {
      Config.HEADLINE.name: 'Table of Contents'
    }

  @staticmethod
  def invoke(readme_lines: list[str], base_path: str, index: int, args: list[str], logger: Callable[[str], None], config: dict):

    toc_headline = config[Config.HEADLINE.name]
    headlines = find_headlines(readme_lines)
    lines = generate_toc(toc_headline, headlines)

    # Remove instruction comment
    readme_lines.pop(index)

    # Insert result lines
    for line in reversed(lines):
      readme_lines.insert(index, line)

    logger(f'Inserted TOC')

  @staticmethod
  def get_name() -> str:
    return 'toc'

def find_headlines(readme_lines: list[str]) -> list[tuple[str, int, int]]:
  headlines = []

  # [key level]: { [key line]: number_of_occurrences }
  headline_counter = {}

  for line in map(lambda x: x.strip(), readme_lines):

    # Not a headline
    if not line.startswith('#'):
      continue

    # Strip off leading #s and thus count the headline level
    level = 0
    while line.startswith('#'):
      line = line[1:]
      level += 1

    # Strip any leading whitespace
    line = line.lstrip()

    # Don't yield the main headline
    if level == 1:
      continue

    # Create a new tracker object for this level
    if level not in headline_counter:
      headline_counter[level] = {}

    level_tracker = headline_counter[level]

    # First occurrence of this headline, add with suffix zero (don't append)
    if line not in level_tracker:
      level_tracker[line] = 1
      headlines.append([line, level, 0])

    else:

      # Bump the suffix of the first zero-suffix entry to one if it's still zero
      for headline in headlines:
        if headline[0] == line and headline[1] == level and headline[2] == 0:
          headline[2] = 1
          break

      level_tracker[line] += 1
      headlines.append([line, level, level_tracker[line]])

  return headlines

def generate_toc(toc_headline: str, headlines: list[tuple[str, int]]) -> list[str]:
  res = []

  res.append(f'## {toc_headline}\n')

  min_level = min(map(lambda x: x[1], headlines))

  for line, level, suffix in headlines:

    # Don't include the toc headline in the toc...
    if line == toc_headline:
      continue

    headline_indent = '  ' * (level - min_level)
    anchor = line.lower().replace(' ', '-')

    # Append the suffix if necessary
    if suffix > 0:
      anchor = anchor + f'-{suffix}'

    res.append(f'{headline_indent}- [{line}](#{anchor})\n')

  return res