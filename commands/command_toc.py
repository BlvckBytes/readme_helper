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
  def invoke(readme_lines: list[str], index: int, args: list[str], logger: Callable[[str], None], config: dict):

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

def find_headlines(readme_lines: list[str]) -> list[tuple[str, int]]:
  headlines = []

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

    headlines.append((line, level))

  return headlines

def generate_toc(toc_headline: str, headlines: list[tuple[str, int]]) -> list[str]:
  res = []

  res.append(f'## {toc_headline}\n')

  min_level = min(map(lambda x: x[1], headlines))

  for line, level in headlines:

    # Don't include the toc headline in the toc...
    if line == toc_headline:
      continue

    res.append(f'{("  " * (level - min_level))}- [{line}](#{line.lower().replace(" ", "-")})\n')

  return res