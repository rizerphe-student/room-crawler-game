"""A base game"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Item:
    """An item in the game"""

    name: str
    description: str
    worry_description: str


@dataclass
class EncounterResult(ABC):
    """The result of an encounter"""


@dataclass
class EmptyEncounterResult(EncounterResult):
    """The result of an encounter with no outcome"""


@dataclass
class Transaction(EncounterResult):
    """A transaction between a player and an NPC"""

    item: Item
    exchanged_for: Item


@dataclass
class CharacterSwap(EncounterResult):
    """A transformation into another character"""

    new_character: Character


@dataclass
class Character(ABC):
    """An NPC in the game"""

    name: str
    sells: list[Transaction]
    weaknesses: list[Item]

    @property
    @abstractmethod
    def description(self) -> str:
        """The description of the character"""

    @property
    def worries(self) -> list[str]:
        """The worries of the character

        Returns:
            list[str]: The worries of the character
        """
        return [item.worry_description for item in self.weaknesses]

    @property
    @abstractmethod
    def alive(self) -> bool:
        """Whether the character is alive

        Returns:
            bool: Whether the character is alive
        """

    @property
    def in_game(self) -> bool:
        """Whether the character is in the game

        Returns:
            bool: Whether the character is in the game
        """
        return self.alive

    @property
    def greeting(self) -> str:
        """The greeting of the character

        Returns:
            str: The greeting of the character
        """
        return f"Hello I am {self.name} - {self.description}"

    @abstractmethod
    def encounter(self, item: Item) -> EncounterResult:
        """Encounter the item
        Updates the internal state

        Args:
            item (Item): The item to encounterwith

        Returns:
            EncounterResult: The result of the encounter
        """


@dataclass
class Enemy(Character):
    """An enemy in the game"""

    alive: bool = True

    @property
    def greeting(self) -> str:
        """The greeting of the character

        Returns:
            str: The greeting of the character
        """
        return super().greeting + "\n" + self.complain()

    def get_attacked_with(self, item: Item) -> bool:
        """Attack the enemy with an item

        Args:
            item (Item): The item to attack with

        Returns:
            bool: Whether the attack was successful
        """
        return item in self.weaknesses

    def encounter(self, item: Item) -> EncounterResult:
        """Encounter the item

        Args:
            item (Item): The item to encounterwith

        Returns:
            EncounterResult: The result of the encounter
        """
        if self.get_attacked_with(item):
            self.alive = False
        return EmptyEncounterResult()

    def complain(self) -> str:
        """Complain about something

        Returns:
            str: The complaint
        """
        return "I'm so worried about " + ", ".join(self.worries)


@dataclass
class Zombie(Enemy):
    """A zombie in the game"""

    alive: bool = False

    @property
    def in_game(self) -> bool:
        """Whether the character is in the game

        Returns:
            bool: Whether the character is in the game
        """
        return True

    @property
    def description(self) -> str:
        """The description of the character

        Returns:
            str: The description of the character
        """
        return "I'm a zombie woo hoo! I'm also dead."


@dataclass
class Dragon(Enemy):
    """A dragon in the game"""

    alive: bool = True

    @property
    def description(self) -> str:
        """The description of the character

        Returns:
            str: The description of the character
        """
        return "An ebil dragon :3"


@dataclass
class Friend(Character):
    """A friend in the game"""

    alive: bool = True

    def encounter(self, item: Item) -> EncounterResult:
        """Encounter the item

        Args:
            item (Item): The item to encounterwith

        Returns:
            EncounterResult: The result of the encounter
        """
        for transaction in self.sells:
            if transaction.item == item:
                self.sells.remove(transaction)
                self.weaknesses.append(transaction.exchanged_for)
                return transaction
        return EmptyEncounterResult()
