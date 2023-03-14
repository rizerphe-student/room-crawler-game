"""A basic game"""
from __future__ import annotations

import enum


class Direction(enum.Enum):
    """Direction of movement."""

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class Enemy:
    """An enemy in the game."""

    enemies_defeated = 0

    def __init__(self, name: str, description: str) -> None:
        """Initialize an enemy.

        Args:
            name (str): The name of the enemy
            description (str): The description of the enemy
        """
        self.name = name
        self.description = description
        self.conversation: str | None = None
        self.weakness: str | None = None

    def set_conversation(self, conversation: str) -> None:
        """Set the conversation of the enemy.

        Args:
            conversation (str): The conversation of the enemy
        """
        self.conversation = conversation

    def set_weakness(self, weakness: str) -> None:
        """Set the weakness of the enemy.

        Args:
            weakness (str): The weakness of the enemy
        """
        self.weakness = weakness

    def describe(self) -> None:
        """Describe the item."""
        print(f"{self.name} is here!")
        print(self.description)

    def talk(self) -> None:
        """Talk to the enemy."""
        if self.conversation is None:
            print("I have nothing to say to you.")
        print(f"[{self.name} says]: {self.conversation}")

    def fight(self, item_name: str) -> bool:
        """Fight the enemy.

        Args:
            item_name (str): The name of the item

        Returns:
            bool: True if the enemy is defeated, False otherwise
        """
        if self.weakness == item_name:
            Enemy.enemies_defeated += 1
            return True
        return False

    def get_defeated(self) -> int:
        """Get the number of enemies defeated.

        Returns:
            int: The number of enemies defeated
        """
        return Enemy.enemies_defeated


class Item:
    """An item in the game."""

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize an item.

        Args:
            name (str): The name of the item
            description (str): The description of the item
        """
        self.name = name
        self.description = description

    def set_description(self, description: str) -> None:
        """Set the description of the item.

        Args:
            description (str): The description of the item
        """
        self.description = description

    def describe(self) -> None:
        """Describe the item."""
        print(f"The [{self.name}] is here - {self.description}")

    def get_name(self) -> str:
        """Get the name of the item.

        Returns:
            str: The name of the item
        """
        return self.name


class Room:
    """A room in the game"""

    def __init__(self, name: str, description: str = "") -> None:
        """Initialize a room

        Args:
            name (str): The name of the room
            description (str): The description of the room. Defaults to "".
        """
        self.name = name
        self.description = description
        self.links: dict[Direction, Room] = {}
        self.character: Enemy | None = None
        self.item: Item | None = None

    def set_description(self, description: str) -> None:
        """Set the description of the room

        Args:
            description (str): The description of the room
        """
        self.description = description

    def set_character(self, character: Enemy) -> None:
        """Set the character in the room

        Args:
            character (Enemy): The character to set
        """
        self.character = character

    def get_character(self) -> Enemy | None:
        """Get the character in the room

        Returns:
            Enemy | None: The character in the room
        """
        return self.character

    def set_item(self, item: Item | None) -> None:
        """Set the item in the room

        Args:
            item (Item | None): The item to set
        """
        self.item = item

    def get_item(self) -> Item | None:
        """Get the item in the room

        Returns:
            Item | None: The item in the room
        """
        return self.item

    def link_room(self, other: Room, direction: str) -> None:
        """Link the room to another room

        Args:
            other (Room): The other room to link to
            direction (str): The direction to link the room to
        """
        self.links[Direction[direction.upper()]] = other
        reverse_direction = Direction((Direction[direction.upper()].value + 2) % 4)
        other.links[reverse_direction] = self

    def get_details(self) -> None:
        """Print the details of the room to the console"""
        print(self.name)
        print("--------------------")
        print(self.description)
        for direction, room in self.links.items():
            print(f"The {room.name} is {direction.name.lower()}.")

    def move(self, direction_name: str) -> Room:
        """Move to another room

        Args:
            direction_name (str): The direction to move to

        Returns:
            Room: The room moved to
        """
        direction = Direction[direction_name.upper()]
        if direction in self.links:
            return self.links[direction]
        print("You cannot go that way.")
        return self
