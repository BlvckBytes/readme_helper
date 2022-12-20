from abc import ABC, abstractmethod
from typing import Callable

class ACommand(ABC):

  @staticmethod
  @abstractmethod
  def generate_config() -> dict:
    pass

  @staticmethod
  @abstractmethod
  def invoke(readme_lines: list[str], index: int, args: list[str], logger: Callable[[str], None], config: dict):
    pass

  @staticmethod
  @abstractmethod
  def get_name() -> str:
    pass

  @staticmethod
  def is_option_enabled(option: str) -> bool:
    option = option.lower().strip()
    return option == 'yes' or option == 'true' or option == '1'