"""A base game"""
from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable


class Direction(enum.Enum):
    """Direction of movement."""

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


@dataclass
class Item:
    """An item in the game"""

    name: str
    description: str
    worry_description: str

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Item) and self.name == other.name


@dataclass
class GoldenApple(Item):
    """A golden apple"""

    name: str = "Golden Apple"
    description: str = "A golden apple"
    worry_description: str = "what if you eat it?"


@dataclass
class EncounterSummary:
    """A summary of an encounter"""

    inventory_additions: list[Item] = field(default_factory=list)
    inventory_removals: list[Item] = field(default_factory=list)
    character_additions: list[Character] = field(default_factory=list)
    character_removals: list[Character] = field(default_factory=list)


@dataclass
class EncounterResult(ABC):
    """The result of an encounter"""

    @property
    @abstractmethod
    def summary(self) -> EncounterSummary:
        """The summary of the encounter"""

    @property
    @abstractmethod
    def description(self) -> str:
        """The description of the encounter"""


@dataclass
class EmptyEncounterResult(EncounterResult):
    """The result of an encounter with no outcome"""

    @property
    def summary(self) -> EncounterSummary:
        """The summary of the encounter

        Returns:
            EncounterSummary: The summary of the encounter
        """
        return EncounterSummary()

    @property
    def description(self) -> str:
        """The description of the encounter

        Returns:
            str: The description of the encounter
        """
        return "Nothing happened."


@dataclass
class AnnottatedEncounterResult(EncounterResult):
    """The result of an encounter with an outcome"""

    annotation: str

    @property
    def summary(self) -> EncounterSummary:
        """The summary of the encounter

        Returns:
            EncounterSummary: The summary of the encounter
        """
        return EncounterSummary()

    @property
    def description(self) -> str:
        """The description of the encounter

        Returns:
            str: The description of the encounter
        """
        return self.annotation


@dataclass
class Transaction(EncounterResult):
    """A transaction between a player and an NPC"""

    item: Item
    exchanged_for: Item

    @property
    def summary(self) -> EncounterSummary:
        return EncounterSummary(
            inventory_additions=[self.item],
            inventory_removals=[self.exchanged_for],
        )

    @property
    def description(self) -> str:
        """The description of the encounter

        Returns:
            str: The description of the encounter
        """
        return f"You traded {self.exchanged_for.name} for {self.item.name}."


@dataclass
class CharacterSwap(EncounterResult):
    """A transformation into another character"""

    old_character: Character
    new_character: Character

    @property
    def summary(self) -> EncounterSummary:
        return EncounterSummary(
            character_additions=[self.new_character],
            character_removals=[self.old_character],
        )

    @property
    def description(self) -> str:
        """The description of the encounter

        Returns:
            str: The description of the encounter
        """
        return f"{self.old_character.name}, a {self.old_character.__class__.__name__} transformed into {self.new_character.name}, a {self.new_character.__class__.__name__}."


@dataclass
class Character(ABC):
    """An NPC in the game"""

    name: str
    weaknesses: list[Item] = field(default_factory=list)

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
            return AnnottatedEncounterResult(f"You killed {self.name}")
        return EmptyEncounterResult()

    def complain(self) -> str:
        """Complain about something

        Returns:
            str: The complaint
        """
        return (
            "I'm so worried about " + ", ".join(self.worries)
            if self.worries
            else "I'm not worried about anything."
        )


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

    def encounter(self, item: Item) -> EncounterResult:
        """Encounter the item

        Args:
            item (Item): The item to encounterwith

        Returns:
            EncounterResult: The result of the encounter
        """
        if isinstance(item, GoldenApple):
            return CharacterSwap(self, Student(self.name))
        return super().encounter(item)


@dataclass
class Dragon(Enemy):
    """A dragon in the game"""

    alive: bool = True
    weaknesses: list[Item] = field(
        default_factory=lambda: [
            Item("Knife", "stabby stabby", "uhoh it's ebiller than me")
        ]
    )

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

    sells: list[Transaction] = field(default_factory=list)
    alive: bool = True

    def encounter(self, item: Item) -> EncounterResult:
        """Encounter the item

        Args:
            item (Item): The item to encounterwith

        Returns:
            EncounterResult: The result of the encounter
        """
        for transaction in self.sells:
            if transaction.exchanged_for == item:
                return transaction
        return EmptyEncounterResult()


@dataclass
class Student(Friend):
    """A student in the game"""

    weaknesses: list[Item] = field(
        default_factory=lambda: [
            Item("Exam", "An exam", "how well I did on my exam"),
            Item("Homework", "Homework", "how much homework I have"),
        ]
    )
    sells: list[Transaction] = field(
        default_factory=lambda: [
            Transaction(
                Item("Knife", "A knife", "how I'm going to kill myself"),
                Item("Exam results", "Exam results", "how well I did on my exam"),
            ),
            Transaction(
                GoldenApple(),
                Item("Burger", "A burger", "what I'm going to eat"),
            ),
        ]
    )

    @property
    def description(self) -> str:
        """The description of the character

        Returns:
            str: The description of the character
        """
        return "I'm a student. I'm worried about " + ", ".join(self.worries)


@dataclass
class Teacher(Friend):
    """A teacher in the game"""

    weaknesses: list[Item] = field(
        default_factory=lambda: [
            Item("Grades", "Grades", "how well my students did"),
            Item(
                "Homework",
                "Homework",
                "how much homework I have to grade",
            ),
        ]
    )
    sells: list[Transaction] = field(
        default_factory=lambda: [
            Transaction(
                Item("Exam results", "Exam results", "how well my students did"),
                Item("Cactus", "A cactus", "how I'm going to decorate my office"),
            ),
        ]
    )

    @property
    def description(self) -> str:
        """The description of the character

        Returns:
            str: The description of the character
        """
        return "I'm a teacher. I'm worried about " + ", ".join(self.worries)


@dataclass
class Command:
    """A command"""

    name: str
    documentation: str
    description: str
    action: Callable[[str, Game], None]


@dataclass
class Section:
    """A play area"""

    name: str
    attached_sections: dict[Direction, Section] = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)

    @property
    def actions(self) -> list[Command]:
        """Return all the actions that can be performed in this section

        Returns:
            list[Command]: All the actions that can be performed in this section
        """
        actions = []
        for direction, section in self.attached_sections.items():

            def act(_: str, game: Game, direction: Direction = direction) -> None:
                """Move to the section in the given direction

                Args:
                    _: str: The command
                    game (Game): The game
                    direction (Direction): The direction to move in
                """
                game.move(direction)

            actions.append(
                Command(
                    name=direction.name,
                    documentation=direction.name,
                    description=f"Go {direction.name} to {section.name}",
                    action=act,
                )
            )
        actions.append(
            Command(
                name="talk",
                documentation="talk <character>",
                description="Talk to a character",
                action=lambda character_name, game: (
                    print(character.greeting)
                    if (character := self.get_character(character_name))
                    else print("No such character")
                ),
            )
        )
        actions.append(
            Command(
                name="take",
                documentation="take <item>",
                description="Take an item",
                action=lambda item_name, game: game.take(self.get_item(item_name)),
            )
        )
        actions.append(
            Command(
                name="use",
                documentation="use <item> on <character>",
                description="Use an item on a character",
                action=lambda command_args, game: game.use(
                    self.get_character(command_args.split(" on ")[1]),
                    command_args.split(" on ")[0],
                ),
            )
        )
        return actions

    def attach(self, direction: Direction, section: Section) -> None:
        """Attach a section to this section

        Args:
            direction (Direction): The direction to attach the section
            section (Section): The section to attach
        """
        self.attached_sections[direction] = section
        reverse_direction = Direction(direction.value + 2 % 4)
        section.attached_sections[reverse_direction] = self

    def get_section(self, direction: Direction) -> Section | None:
        """Get the section in the given direction

        Args:
            direction (Direction): The direction to get the section in

        Returns:
            Section | None: The section in the given direction
        """
        return self.attached_sections.get(direction, None)

    def to_string(self) -> str:
        """Get a string representation of the section

        Returns:
            str: A string representation of the section
        """
        contents = [item.name for item in self.items] + [
            character.name for character in self.characters
        ]
        if not contents:
            return self.name
        return f"{self.name}, with " + ", ".join(contents) + "."

    def get_character(self, name: str) -> Character | None:
        """Get the character with the given name

        Args:
            name (str): The name of the character

        Returns:
            Character | None: The character with the given name
        """
        for character in self.characters:
            if character.name == name:
                return character
        return None

    def get_item(self, name: str) -> Item | None:
        """Get the item with the given name

        Args:
            name (str): The name of the item

        Returns:
            Item | None: The item with the given name
        """
        for item in self.items:
            if item.name == name:
                return item
        return None


class Game:
    "A basic game class"

    def __init__(self, start_section: Section) -> None:
        """Initialize the game

        Args:
            start_section (Section): The starting section
        """
        self.current_section = start_section
        self.inventory: list[Item] = []

    def show_commands(self) -> None:
        """Show the commands"""
        print("Commands:")
        for command in self.current_section.actions:
            print(f"  {command.documentation}: {command.description}")

    def output_state(self) -> None:
        """Output the state of the game"""
        print(self.current_section.to_string())

    def use(self, character: Character | None, item_name: str) -> None:
        """Use an item on a character

        Args:
            character (Character): The character to use the item on
            item_name (str): The name of the item to use
        """
        if not character:
            print("No such character")
            return
        for item in self.inventory:
            if item.name == item_name:
                result = character.encounter(item)
                self.apply_result(result)

    def take(self, item: Item | None) -> None:
        """Take an item

        Args:
            item (Item): The item to take
        """
        if not item:
            print("No such item")
            return
        self.inventory.append(item)
        self.current_section.items.remove(item)

    def apply_result(self, result: EncounterResult) -> None:
        """Apply the result of an encounter

        Args:
            result (EncounterResult): The result of the encounter
        """
        summary = result.summary
        self.inventory = [
            item for item in self.inventory if item not in summary.character_removals
        ] + summary.inventory_additions
        self.current_section.characters = [
            character
            for character in self.current_section.characters
            if character not in summary.character_removals
        ] + summary.character_additions
        print(result.description)

    def move(self, direction: Direction) -> None:
        """Go in a direction

        Args:
            direction (Direction): The direction to go
        """
        section = self.current_section.get_section(direction)
        if section is None:
            print("You can't go that way")
        else:
            self.current_section = section

    def iteration(self) -> None:
        """Perform one iteration of the game"""
        self.output_state()
        self.show_commands()
        command = input("What do you want to do? ")
        print()
        for action in self.current_section.actions:
            if command.startswith(action.name):
                action.action(" ".join(command.split(" ")[1:]), self)
                return
        print("No such command")

    def mainloop(self) -> None:
        """The main loop of the game"""
        while True:
            self.iteration()
            print()


def main() -> None:
    """The main function"""
    start_section = Section(name="The start")
    end_section = Section(name="The end")
    start_section.attach(Direction.NORTH, end_section)
    teacher = Teacher(name="Mr. Smith")
    end_section.characters.append(teacher)
    zombie = Zombie(name="Jack")
    start_section.characters.append(zombie)
    item = Item(
        name="Homework",
        description="A book about Python",
        worry_description="A book about Python",
    )
    start_section.items.append(item)
    cactus = Item(
        name="Cactus",
        description="A cactus",
        worry_description="A cactus",
    )
    start_section.items.append(cactus)
    dragon = Dragon(name="Smaug")
    end_section.characters.append(dragon)
    game = Game(start_section)
    golden_apple = GoldenApple()
    end_section.items.append(golden_apple)
    game = Game(start_section)
    game.mainloop()


if __name__ == "__main__":
    main()
