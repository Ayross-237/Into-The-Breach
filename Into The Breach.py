from Support import *
import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, Callable

# Constants
ALLOWABLE_HEALTHS = [str(x) for x in range(0, MAX_BUILDING_HEALTH + 1)]
MECH_NAMES = (TANK_NAME, HEAL_NAME)
ENEMY_NAMES = (FIREFLY_NAME, SCORPION_NAME)

SIDEBAR_COLUMNS = 4
DEFAULT_BOARD_DIMS = 10
DISPLAY_CHARS = {
    TANK_SYMBOL: TANK_DISPLAY,
    HEAL_SYMBOL: HEAL_DISPLAY,
    SCORPION_SYMBOL: SCORPION_DISPLAY,
    FIREFLY_SYMBOL: FIREFLY_DISPLAY
}
COLOURS = {
    GROUND_SYMBOL: GROUND_COLOR,
    MOUNTAIN_SYMBOL: MOUNTAIN_COLOR,
    ALLOWABLE_HEALTHS[0]: DESTROYED_COLOR,
    tuple(ALLOWABLE_HEALTHS[1:]): BUILDING_COLOR
}

WIN_TEXT = "You Win!"
LOSE_TEXT = "You Lost!"
YES = 'yes'
MOUSE_BUTTONS = ['<Button-1>', '<Button-2>']
BUTTON_LABELS = [SAVE_TEXT, LOAD_TEXT, TURN_TEXT]
WIN_LOSE_TEXTS = [LOSE_TEXT, WIN_TEXT]
# Constants

class Tile():
    """The parent class for all tiles in the game that provides the basic
    tile behaviour."""
    
    def __init__(self) -> None:
        """Constructor for the tile."""
        self._symbol = TILE_SYMBOL
        self._name = TILE_NAME
        self._is_blocking = False

    def __repr__(self) -> str:
        """Returns a representation of the tile that can be used
        to create an identical instance of itself."""
        return f'{self._name}()'

    def __str__(self) -> str:
        """Returns the symbol that represents the tile."""
        return self._symbol

    def get_tile_name(self) -> str:
        """Returns the name of the tile type."""
        return self._name

    def is_blocking(self) -> bool:
        """Returns a boolean corresponding to whether a tile is blocking
        or not."""
        return self._is_blocking
    

class Ground(Tile):
    """The class representing a ground tile."""

    def __init__(self) -> None:
        """Constructor for the ground tile."""
        super().__init__()
        self._symbol = GROUND_SYMBOL
        self._name = GROUND_NAME


class Mountain(Tile):
    """The class representing a mountain tile."""

    def __init__(self) -> None:
        """Constructor for the mountain tile."""
        self._symbol = MOUNTAIN_SYMBOL
        self._name = MOUNTAIN_NAME
        self._is_blocking = True


class Building(Tile):
    """The class representing a building tile - the tile to be protected by
    the player."""

    def __init__(self, initial_health: int) -> None:
        """Constructs a building tile with the specified health.

        Parameters:
            initial_health: The initial health of the building.

        Preconditions:
            <initial_health> will be between 0 and 9 inclusive.
        """
        self._name = BUILDING_NAME
        self._health = initial_health

    def __repr__(self) -> str:
        """Returns the representation of the building that can be used to
        create an identical instance."""
        return f'{self._name}({self._health})'

    def __str__(self) -> str:
        """Returns the string representation of the building."""
        return str(self._health)

    def is_destroyed(self) -> bool:
        """Returns a boolean stating whether the given building has been
        destroyed or not."""
        return not self._health

    def is_blocking(self) -> bool:
        """Returns whether or not the building is blocking."""
        return self._health > 0

    def damage(self, damage: int) -> None:
        """Reduces the health of a non-destroyed building by <damage>, then
        rounds health up to 0 or down to MAX_BUILDING_HEALTH if it is < 0
        or > MAX_BUILDING_HEALTH respectively.

        Parameters:
            damage: The amount to reduce the building's health by.
        """
        if self._health:
            self._health -= damage
            # Keeps the health value between 0 and MAX_BUILDING_HEALTH
            if self._health > MAX_BUILDING_HEALTH:
                self._health = MAX_BUILDING_HEALTH
            elif self._health < 0:
                self._health = 0

    
class Board():
    """The class representing the game board."""

    def __init__(self, board: list[list[str]]) -> None:
        """Constructs a new board representing the state of <board>.

        Parameters:
            board: The board to be initialised.

        Preconditions:
            The length of every list within <board> is the same.
            The length of <board> is >= 1.
            The characters within the lists within <board> are all string
            representations of one of the tile subclasses.
        """
        self._state = []
        tiles = {'M': Mountain, ' ': Ground, 'T': Tile}
        # Creates the game state using class instances
        for row in board:
            state_row = []
            for tile in row:
                if tile in ALLOWABLE_HEALTHS:
                    state_row.append(Building(int(tile)))
                else:
                    state_row.append(tiles[tile]())
            self._state.append(state_row)

    def __repr__(self) -> str:
        """Returns a string that could be used to construct an identical
        board instance."""
        board_list = [[str(tile) for tile in row] for row in self._state]
        return f'{self.__class__.__name__}({board_list})'

    def __str__(self) -> str:
        """Returns a string representation of the board (the concatenation
        of all the tile symbols in a row from left to right where each row is
        represented on a new line)."""
        rows = [''.join([str(tile) for tile in row]) for row in self._state]
        return '\n'.join(rows)

    def get_dimensions(self) -> tuple[int, int]:
        """Returns the dimensions of the board in terms of number of tiles."""
        return len(self._state), len(self._state[0])

    def get_tile(self, position: tuple[int, int]) -> Tile:
        """Returns the tile at the given position on the board.

        Parameters:
            position: The location of the tile.

        Returns:
            The tile instance at the the given position.

        Preconditions:
            <position> is within the bounds of the board.
        """
        return self._state[position[0]][position[1]]
    
    def get_buildings(self) -> dict[tuple[int, int], Building]:
        """Returns a dictionary of the position of every building mapped
        to the building instance itself."""
        buildings = {
            (i, j): self.get_tile((i, j))
            for i in range(self.get_dimensions()[0])
            for j in range(self.get_dimensions()[1])
            if type(self.get_tile((i, j))) == Building
        }
        return buildings


class Entity():
    """The abstract class for entites."""
    
    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        """Constructs a new entity with the specified position, health,
        speed and strength.

        Parameters:
            position: The position of the entity.
            initial_health: The starting health of the entity.
            speed: The max distance the entity can travel in a single move.
            strength: The strength of the entity's attacks.
        """
        self._name = ENTITY_NAME
        self._symbol = ENTITY_SYMBOL
        self._position = position
        self._health = initial_health
        self._speed = speed
        self._strength = strength
        self._is_friendly = False

    def __repr__(self) -> str:
        """Returns the representation of the entity that can be used to create
        another identical instance."""
        return '{0}({1}, {2}, {3}, {4})'.format(
            self._name,
            self._position,
            self._health,
            self._speed,
            self._strength
        )

    def __str__(self) -> str:
        """Returns the string representation of the entity."""
        return '{0},{1},{2},{3},{4},{5}'.format(
            self._symbol,
            self._position[0],
            self._position[1],
            self._health,
            self._speed,
            self._strength
        )
            
    def get_symbol(self) -> str:
        """Returns the character that represents the entity type."""
        return self._symbol

    def get_name(self) -> str:
        """Returns the name of the entity type."""
        return self._name

    def get_position(self) -> tuple[int, int]:
        """Returns the current position, (row, column), of the entity."""
        return self._position

    def set_position(self, position: tuple[int, int]) -> None:
        """Moves the entity to the given position.

        Parameters:
            position: The (row, column) position to move the entity to.
        """
        self._position = position

    def get_health(self) -> int:
        """Returns the current health of the entity."""
        return self._health

    def get_speed(self) -> int:
        """Returns the speed of the entity."""
        return self._speed

    def get_strength(self) -> int:
        """Returns the strength of the entity."""
        return self._strength

    def damage(self, damage: int) -> None:
        """Reduces the health of the entity by <damage> if the entity is not
        destroyed.

        Parameters:
            damage: The amount of health the entity should lose.
        """
        if self._health:
            self._health -= damage
        # Constrains health to a non-negative value
        if self._health < 0:
            self._health = 0

    def is_alive(self) -> bool:
        """Returns a boolean corresponding to whether the entity is still       
        alive."""
        return self._health > 0
    
    def is_friendly(self) -> bool:
        """Returns whether or not the entity is friendly."""
        return self._is_friendly

    def get_targets(self) -> list[tuple[int, int]]:
        """Returns the (row, column) positions that would be attacked by the
        entity during the combat phase."""
        position = self._position
        targets = [
            (position[0] + offset[0], position[1] + offset[1])
            for offset in PLUS_OFFSETS
        ]
        return targets

    def attack(self, entity: "Entity") -> None:
        """Damages the selected entity by the amount specified by the
        attacking entity's strength.

        Parameters:
            entity: The entity that should be damaged.
        """
        entity.damage(self._strength)


class Mech(Entity):
    """The abstract class for mech entities."""
    
    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        super().__init__(position, initial_health, speed, strength)
        self._previous_position = None
        self._symbol = MECH_SYMBOL
        self._name = MECH_NAME
        self._active = True
        self._is_friendly = True

    def set_position(self, position: tuple[int, int]) -> None:
        """Moves the mech to the given position and updates its previous
        position.

        Parameters:
            position: The (row, column) position to move the mech to.
        """
        self._previous_position = self._position
        self._position = position

    def enable(self) -> None:
        """Sets the mech to active."""
        self._active = True
        
    def disable(self) -> None:
        """Sets the mech to inactive."""
        self._active = False

    def is_active(self) -> bool:
        """Returns a boolean corresponding to whether the mech is active."""
        return self._active


class TankMech(Mech):
    """The class for tank mechs."""
    
    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        super().__init__(position, initial_health, speed, strength)
        self._symbol = TANK_SYMBOL
        self._name = TANK_NAME

    def get_targets(self) -> list[tuple[int, int]]:
        """Returns the (row, column) positions that would be attacked by the
        tank mech during the combat phase."""
        position = self.get_position()
        targets = [
            (position[0] + i*offset[0], position[1] + i*offset[1])
            for i in range(1, TANK_RANGE + 1)
            for offset in PLUS_OFFSETS[:2]
        ]
        return targets
            

class HealMech(Mech):
    """The class for heal mechs."""
    
    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        super().__init__(position, initial_health, speed, strength)
        self._symbol = HEAL_SYMBOL
        self._name = HEAL_NAME

    def get_strength(self) -> int:
        """Returns the negative of the strength of the heal mech."""
        return -self._strength

    def attack(self, entity: "Entity") -> None:
        """Heals <entity> by the strength of the heal mech dealing the
        attack if an only if <entity> is friendly.

        Parameters:
            entity: The entity to be healed.
        """
        if entity.is_friendly():
            entity.damage(-self._strength)


class Enemy(Entity):
    """The abstract class for enemies."""

    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        super().__init__(position, initial_health, speed, strength)
        self._name = ENEMY_NAME
        self._symbol = ENEMY_SYMBOL
        self._objective = position

    def get_objective(self) -> tuple[int, int]:
        """Returns the position which is the enemy's objective position."""
        return self._objective

    def update_objective(
        self,
        entities: list[Entity],
        buildings: dict[tuple[int, int], Building]
    ) -> None:
        """Updates the objective position of the enemy.

        Parameters:
            entities: The list of entities in the game currently.
            buildings: A dictionary mapping the position of buildings to the
                       buildings themselves.

        Preconditions:
            <entities> is sorted in descending priority order.
        """
        self._objective = self._position


class Scorpion(Enemy):
    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        super().__init__(position, initial_health, speed, strength)
        self._name = SCORPION_NAME
        self._symbol = SCORPION_SYMBOL

    def get_targets(self) -> list[tuple[int, int]]:
        """Returns the (row, column) positions that would be attacked by the
        scorpion during the combat phase."""
        position = self.get_position()
        targets = [
            (position[0] + i*offset[0], position[1] + i*offset[1])
            for i in range(1, SCORPION_RANGE + 1)
            for offset in PLUS_OFFSETS
        ]
        return targets

    def update_objective(
        self,
        entities: list[Entity],
        buildings: dict[tuple[int, int], Building]
    ) -> None:
        """Updates the objective position of the scorpion.

        Parameters:
            entities: The list of entities in the game currently.
            buildings: A dictionary mapping the position of buildings to the
                       buildings themselves.

        Preconditions:
            <entities> is sorted in descending priority order.
        """
        greatest_health_mech = None
        greatest_health = 0
        
        for entity in entities:
            if (entity.get_name() in MECH_NAMES
                and entity.get_health() > greatest_health
                ):
                greatest_health_mech = entity
                greatest_health = entity.get_health()

        if greatest_health_mech:
            self._objective = greatest_health_mech.get_position()
        else:
            self._objective = self.get_position()
        

class Firefly(Enemy):
    def __init__(
        self,
        position: tuple[int, int],
        initial_health: int,
        speed: int,
        strength: int
    ) -> None:
        super().__init__(position, initial_health, speed, strength)
        self._name = FIREFLY_NAME
        self._symbol = FIREFLY_SYMBOL

    def get_targets(self) -> list[tuple[int, int]]:
        """Returns a list of the positions which are targets for the
        firefly."""
        position = self.get_position()
        targets = [
            (position[0] + i*offset[0], position[1] + i*offset[1])
            for i in range(1, FIREFLY_RANGE + 1)
            for offset in PLUS_OFFSETS[2:]
        ]
        return targets

    def update_objective(
        self,
        entities: list[Entity],
        buildings: dict[tuple[int, int], Building]
    ) -> None:
        """Updates the objective position of the firefly.

        Parameters:
            entities: The list of entities in the game currently.
            buildings: A dictionary mapping the position of buildings to the
                       buildings themselves.

        Preconditions:
            <entities> is sorted in descending priority order.
        """
        objective_building = None
        objective_health = MAX_BUILDING_HEALTH + 1
        objective_position = None
        
        for building_pos in buildings:
            building = buildings[building_pos]
            update_building = False
            
            if (0 < int(str(building)) < objective_health
                or (int(str(building)) == objective_health
                    and (building_pos[0] > objective_position[0]
                         or (building_pos[0] == objective_position[0]
                             and building_pos[1] > objective_position[1])))
                ):
                objective_building = building
                objective_health = int(str(building))
                objective_position = building_pos

        if objective_building:
            self._objective = objective_position
        else:
            self._objective = self.get_position()
        
        
class BreachModel():
    """The class for the model component of Into The Breach."""
    
    def __init__(self, board: Board, entities: list[Entity]) -> None:
        """Constructor for the breach model.

        Parameters:
            board: The board for the game.
            entites: The list of entities on the board.

        Preconditions:
            <entities> is sorted in descending priority order.
        """
        self._board = board
        self._entities = entities
        self._buildings = self._board.get_buildings()        

    def __str__(self) -> str:
        """Returns a string representation of the breach model which includes
        the string representations of the board and all entities currently in
        the game."""
        board_string = str(self._board)
        entities_string = '\n'.join([str(entity) for entity in self._entities])
        return board_string + '\n\n' + entities_string

    def get_board(self) -> Board:
        """Returns the current board instance."""
        return self._board

    def get_entities(self) -> list[Entity]:
        """Returns a list of the all entities in the game, listed in descending
        priority order starting from the first element."""
        return self._entities

    def has_won(self) -> bool:
        """Returns True if and only if the game is in a win state."""
        mechs_alive = [
            entity.get_name() in MECH_NAMES and entity.get_health() > 0
            for entity in self._entities
        ]
        buildings_alive = [
            int(str(self._buildings[building_pos])) > 0
            for building_pos in self._buildings
        ]
        enemies_alive = [
            entity.get_name() in ENEMY_NAMES and entity.get_health() > 0
            for entity in self._entities
        ]

        return (
            any(mechs_alive)
            and any(buildings_alive)
            and not any(enemies_alive)
        )

    def has_lost(self) -> bool:
        """Returns True if and only if the game is in a loss state."""
        mechs_alive = [
            entity.get_name() in MECH_NAMES and entity.get_health() > 0
            for entity in self._entities
        ]
        buildings_alive = [
            int(str(self._buildings[building_pos])) > 0
            for building_pos in self._buildings
        ]

        return not any(mechs_alive) or not any(buildings_alive)

    def entity_positions(self) -> dict[tuple[int, int], Entity]:
        """Returns a dictionary containing all entities, indexed by their
        position."""
        return {entity.get_position(): entity for entity in self._entities}

    def get_valid_movement_positions(
        self,
        entity: Entity
    )-> list[tuple[int, int]]:
        """Returns the list of positions that the given entity could move to
        during the relevant moving phase, with positions in higher rows
        appearing before ones in lower rows and positions further left
        in the same row appearing before positions further right.

        Parameters:
            entity: The entity to check the movement positions for.

        Returns:
            list[tuple[int, int]]: The sorted list of valid movement
                                   positions, (row, column).
        """
        board_dimensions = self._board.get_dimensions()
        current_pos = entity.get_position()
        speed = entity.get_speed()
        positions = [
            (i, j)
            for i in range(board_dimensions[0])
            for j in range(board_dimensions[1])
            if 0 < get_distance(self, current_pos, (i, j)) <= speed
        ]
        return positions

    def attempt_move(self, entity: Entity, position: tuple[int, int]) -> None:
        """Moves the entity to the specified position only if the entity is
        friendly, active and can move to that position according to the game
        rules. Disables the entity after a move is made.

        Parameters:
            entity: The entity to attempt movement.
            position: The position to attempt the movement to.
        """
        if (position in self.get_valid_movement_positions(entity)
            and entity.is_friendly()
            and entity.is_active()
            ):
            entity.set_position(position)
            entity.disable()

    def ready_to_save(self) -> bool:
        """Returns True only when no move has been made since the last call to
        end_turn."""
        mechs_not_active = [
            entity.get_name() in MECH_NAMES and not entity.is_active()
            for entity in self._entities
        ]
        return not any(mechs_not_active)

    def assign_objectives(self) -> None:
        """Updates the objectives of all enemies based on the current game
        state."""
        for entity in self._entities:
            if not entity.is_friendly():
                entity.update_objective(self._entities, self._buildings)

    def move_enemies(self) -> None:
        """Moves each enemy to the valid movement position that minimises the
        distance of the shortest valid path between the position and the
        enemy's position and enemy's objective. If there is a tie, the position
        in the lowest row is chosen and if there is another tie, then the
        position in the rightmost column is chosen. Enemies move in descending
        priority order."""
        enemies = [
            entity
            for entity in self._entities
            if not entity.is_friendly()
        ]

        for enemy in enemies:
            valid_movement_positions = self.get_valid_movement_positions(enemy)
            # Structure: [position, distance]
            best_move = [None, float('inf')]
            
            for position in valid_movement_positions:
                distance_to_objective = get_distance(
                    self,
                    enemy.get_objective(),
                    position,
                )

                if (0 < distance_to_objective < best_move[1]
                    or distance_to_objective == best_move[1]
                    ):
                    best_move = [position, distance_to_objective]

            if best_move[0]:
                enemy.set_position(best_move[0])

    def make_attack(self, entity: Entity) -> None:
        """Makes the given entity perform an attack against every tile that is
        a target.

        Parameters:
            entity: The entity that is to make attacks.
        """
        board_dimensions = self._board.get_dimensions()
        targets = entity.get_targets()
        entity_positions = self.entity_positions()
        for target in targets:
            if (0 <= target[0] <= board_dimensions[0] - 1
                and 0 <= target[1] <= board_dimensions[1] - 1
                ):
                tile = self._board.get_tile(target)
                entity_target = entity_positions.get(target)
                if str(tile) in ALLOWABLE_HEALTHS:
                    tile.damage(entity.get_strength())
                if entity_target:
                    entity.attack(entity_target)

    def end_turn(self) -> None:
        """Executes the attack and enemy movement phases and activates
        all mechs."""
        # Executes entity attacks
        for entity in self._entities:
            if entity.is_alive():
                self.make_attack(entity)
            if entity.get_name() in MECH_NAMES:
                entity.enable()
        # Removes any dead entities
        for pos in self.entity_positions():
            entity = self.entity_positions()[pos] 
            if not entity.is_alive():
                index = self._entities.index(entity)
                self._entities.pop(index)
        
        self.assign_objectives()
        self.move_enemies()


class GameGrid(AbstractGrid):
    """The view component that displays the board and entities."""
        
    def redraw(
        self,
        board: Board,
        entities: list[Entity],
        highlighted: list[tuple[int, int]] = None,
        movement: bool = False
    ) -> None:
        """Clears and redraws the GameGrid with the provided information.

        Parameters:
            board: The current game board.
            entities: The current list of entities.
            higlighted: The current list of highlighed tiles.
            movement: A boolean stating whether or not the user is attempting
                      a move.
        """
        self.clear()
        self.set_dimensions(board.get_dimensions())
        
        for i in range(board.get_dimensions()[0]):
            for j in range(board.get_dimensions()[1]):
                tile = board.get_tile((i, j))
                if (i, j) in highlighted:
                    if movement:
                        self.color_cell((i, j), MOVE_COLOR)
                    else:
                        self.color_cell((i, j), ATTACK_COLOR)
                else:
                    for key in COLOURS:
                        if str(tile) in key:
                            self.color_cell((i, j), COLOURS[key])
                            break # Stops the loop from unnecessary checking
                        
                if str(tile) in ALLOWABLE_HEALTHS[1:]:
                    self.annotate_position((i, j), str(tile), ENTITY_FONT)
                
        for entity in entities:
            self.annotate_position(
                entity.get_position(),
                DISPLAY_CHARS[entity.get_symbol()],
                ENTITY_FONT
            )

    def bind_click_callback(
        self,
        click_callback: Callable[[tuple[int, int]], None]
    )-> None:
        """Binds button-1 and button-2 to a function that calls the provided
        click_callback at the (row, column) position where the click was
        made.

        Parameters:
            click_callback: The callable to call when the mouse click is made.
        """
        click_function = lambda event: click_callback(
            self.pixel_to_cell(event.x, event.y)
        )
        for button in MOUSE_BUTTONS:
            self.bind(button, click_function)

    
class SideBar(AbstractGrid):
    """The sidebar that displays all alive entities and their attributes."""

    def __init__(
        self,
        master: tk.Widget,
        dimensions: tuple[int, int],
        size: tuple[int, int],
        **kwargs
    )-> None:
        """Constructs the sidebar with the specified dimensions.

        Parameters:
            master: The widget that the sidebar should be packed into.
            dimensions: (#rows, #columns)
            size: (width in pixels, height in pixels)
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._master = master
        self._dimensions = dimensions
        self._size = size
        
    def display(self, entities: list[Entity]) -> None:
        """Clears the sidebar, then redraws the header and the relevant
        properties on the sidebar.

        Parameters:
            entities: The list of entities present in the game.

        Preconditions:
            <entities> is sorted in descending priority order.
        """
        self.clear()
        self.set_dimensions((len(entities) + 1, SIDEBAR_COLUMNS))
        # Draws headings
        for i, word in enumerate(SIDEBAR_HEADINGS):
            self.annotate_position((0, i), word, SIDEBAR_FONT)
        # Draws entity information
        for row in range(1, self._dimensions[0]):
            entity = entities[row - 1]
            entity_attributes = [
                DISPLAY_CHARS[entity.get_symbol()],
                str(entity.get_position()),
                entity.get_health(),
                entity.get_strength()
            ]
            for column in range(self._dimensions[1]):
                self.annotate_position(
                    (row, column),
                    entity_attributes[column],
                    SIDEBAR_FONT
                )
                    

class ControlBar(tk.Frame):
    """The control bar, a frame that holds the control buttons."""

    def __init__(
        self,
        master: tk.Widget,
        save_callback: Optional[Callable[[], None]] = None,
        load_callback: Optional[Callable[[], None]] = None,
        turn_callback: Optional[Callable[[], None]] = None,
        **kwargs
    )-> None:
        """Constructor for the control bar.

        Parameters:
            master: The widget that the control bar should be packed into.
            save_callback: The callback to call when the user hits save_game.
            load_callback: The callback to call when the user hits load_game.
            turn_callback: The callback to call when the user hits end_turn.
        """
        super().__init__(master)
        callbacks = {
            SAVE_TEXT: save_callback,
            LOAD_TEXT: load_callback,
            TURN_TEXT: turn_callback
        }
        for label in BUTTON_LABELS:
            function_caller = tk.Button(
                self,
                text=label,
                command=callbacks[label]
            )
            function_caller.pack(side=tk.LEFT, expand=tk.TRUE)


class BreachView():
    """The class for the view."""

    def __init__(
        self,
        root: tk.Tk,
        board_dims: tuple[int, int],
        save_callback: Optional[Callable[[], None]] = None,
        load_callback: Optional[Callable[[], None]] = None,
        turn_callback: Optional[Callable[[], None]] = None,
    )-> None:
        """Constructs the view component of Into The Breach including all
        child components of the view.

        Parameters:
            root: The window to create the view in.
            board_dims: The dimensions of the game board.
            save_callback: The callback to call when the user hits save_game.
            load_callback: The callback to call when the user hits load_game.
            turn_callback: The callback to call when the user hits end_turn.
        """
        root.title(BANNER_TEXT)
        banner = tk.Label(root, text=BANNER_TEXT, font=BANNER_FONT)
        banner.pack(side=tk.TOP, fill=tk.X)
        
        display_section = tk.Frame(root)
        self._grid = GameGrid(
            display_section,
            board_dims,
            (GRID_SIZE, GRID_SIZE)
        )
        self._grid.pack(side=tk.LEFT)
        self._sidebar = SideBar(
            display_section,
            # Arbitrary placeholders. Board dims gets overriden when redraw is
            # called in the __init__ method of the controller
            (DEFAULT_BOARD_DIMS, DEFAULT_BOARD_DIMS),
            (SIDEBAR_WIDTH, GRID_SIZE)
        )
        self._sidebar.pack(side=tk.LEFT)
        display_section.pack(side=tk.TOP)
            
        self._control_bar = ControlBar(
            root,
            save_callback,
            load_callback,
            turn_callback,
        )
        self._control_bar.pack(side=tk.TOP, fill=tk.X)

    def bind_click_callback(
        self,
        click_callback:Callable[[tuple[int, int]], None]
    )-> None:
        """Binds a click event handler to the instantiated GameGrid based on
        click_callback.

        Parameters:
            click_callback: The callback to call when the user clicks on the
                            GameGrid.
        """
        self._grid.bind_click_callback(click_callback)

    def redraw(
        self,
        board: Board,
        entities: list[Entity],
        highlighted: list[tuple[int, int]] = None,
        movement: bool = False
    )-> None:
        """Redraws the instantiated GameGrid and SideBar based on the given
        board, list of entities and tile highlight information.

        Parameters:
            board: The current game board.
            entities: The current list of entities.
            higlighted: The current list of highlighed tiles.
            movement: A boolean stating whether or not the user is attempting
                      a move.
        """
        self._grid.redraw(board, entities, highlighted, movement)
        self._sidebar.display(entities)                              
        

class IntoTheBreach():
    """The class for the controller component of Into The Breach."""

    def __init__(self, root: tk.Tk, game_file: str) -> None:
        """Instantiates the controller. Creates instances of BreachModel and
        BreachView, and redraws display to show the initial game state.

        Parameters:
            root: The window to create the game in.
            game_file: The game file to open.
        """
        self._master = root
        self._focussed_entity = None
        self._highlighted = []
        self._move = False
        self._game_file = game_file
        
        tiles, entities = read_file(game_file)
        self._model = BreachModel(Board(tiles), entities)
        self._view = BreachView(
            root,
            (len(tiles), len(tiles[0])),
            self._save_game,
            self._load_game,
            self._end_turn
        )
        self._view.bind_click_callback(self._handle_click)
        self.redraw()

    def redraw(self) -> None:
        """Redraws the view based on the state of the model and the current
        focussed entity."""
        self._highlighted = []
        if self._focussed_entity and self._move:
            self._highlighted = self._model.get_valid_movement_positions(
                self._focussed_entity
            )
        elif self._focussed_entity and not self._move:
            self._highlighted = self._focussed_entity.get_targets()
            
        self._view.redraw(
            self._model.get_board(),
            self._model.get_entities(),
            self._highlighted,
            self._move
        )

    def set_focussed_entity(self, entity: Optional[Entity]) -> None:
        """Sets the given entity to be the one on which to base
        highlighting or clears the focussed entity if None is given.

        Parameters:
            entity: The entity to set as the focussed entity.
        """
        self._focussed_entity = entity

    def make_move(self, position: tuple[int, int]) -> None:
        """Attempts to move the focussed entity to the given position
        and then clears the focussed entity.

        Parameters:
            position: The position to try and move the focussed entity to.
        """
        self._model.attempt_move(self._focussed_entity, position)
        self._highlighted = []

    def load_model(self, file_path: str) -> None:
        """Replaces the current game state with a new state based on the
        provided file. If an IO error occurs, an error messagebox is
        displayed.

        Parameters:
            file_path: The path to the file which should be loaded.

        Preconditions:
            If the file opens, it will contain a perfect string
            representation of a valid breach model.
        """
        if read_file(file_path):
            tiles, entities = read_file(file_path)
            self._model = BreachModel(Board(tiles), entities)
            self.set_focussed_entity(None)
            self._highlighted_tiles = []
            self._move = False
            self._game_file = file_path
            self.redraw()

    def _save_game(self) -> None:
        """Saves the file using a filedialog if no moves have been made
        before the save attempt. If a move has been made, an error messagebox
        is shown."""
        if self._model.ready_to_save():
            filename = tk.filedialog.asksaveasfilename()
            if filename:
                with open(filename, 'w') as file:
                    file.write(str(self._model))
        else:
            tk.messagebox.showerror(
                title=INVALID_SAVE_TITLE,
                message=INVALID_SAVE_MESSAGE
            )
            
    def _load_game(self) -> None:
        """Uses the file specified by the user in the filedialog to load the
        game state in the specified file. If an IO error occurs an error
        messagebox is displayed."""
        file = tk.filedialog.askopenfilename()
        self.load_model(file)

    def _end_turn(self) -> None:
        """Executes the attack phase, enemy movement phase, and termination
        checking. If the user wins or loses, a messagebox will be displayed."""
        self._model.end_turn()
        self._focussed_entity = None
        self._move = False
        self.redraw()
        
        if self._model.has_won() or self._model.has_lost():
            # Used to display the correct message
            index = int(self._model.has_won())
            
            if tk.messagebox.askquestion(
                title=WIN_LOSE_TEXTS[index],
                message=WIN_LOSE_TEXTS[index] + ' ' + PLAY_AGAIN_TEXT
            ) == YES:
                self.load_model(self._game_file)
            else:
                self._master.destroy()

    def _handle_click(self, position: tuple[int, int]) -> None:
        """Handler for a click from the user at the given (row, column)
        position.

        Parameters:
            position: The (row, column) position of the click.
        """
        entities_pos = self._model.entity_positions()
        entity = entities_pos.get(position)
        # Updates the focussed entity and highlighting colour
        if entity:
            if(self._focussed_entity != entity
                and entity.is_friendly()
                and entity.is_active()):
                self.set_focussed_entity(entity)
                self._move = True
            elif self._focussed_entity != entity:
                self.set_focussed_entity(entity)
                self._move = False
        else:
            # Moves a mech if the user has interacted accordingly
            if (self._focussed_entity
                and self._focussed_entity.is_friendly()
                and self._focussed_entity.is_active()
                and position in self._highlighted):
                self.make_move(position)

            self.set_focussed_entity(None)
            self._move = False
            
        self.redraw()


def play_game(root: tk.Tk, file_path: str) -> None:
    """Creates a controller instance in the specified window and from the file
    at the specified file path."""
    IntoTheBreach(root, file_path)
    root.mainloop()


def main() -> None:
    """Constructs the game window and calls the play_game function with the
    level 1 file."""
    root = tk.Tk()
    play_game(root, 'levels/level1.txt')
    

def read_file(game_file: str) -> tuple[list[list[str]], list[list[Entity]]]:
    """Reads a game file and returns a list of the tiles and a list of the
    entities in the file.

    Parameters:
        game_file: The file to be read.

    Returns:
        tuple[list[list[str]], list[list[Entity]]]: A tuple of the list of
                                                    list of tiles as their
                                                    string representations
                                                    and the list of list of
                                                    entities as objects.                                      
    """
    tiles = []
    entities = []
    entity_map = {
        TANK_SYMBOL: TankMech,
        HEAL_SYMBOL: HealMech,
        SCORPION_SYMBOL: Scorpion,
        FIREFLY_SYMBOL: Firefly
    }
    try:
        with open(game_file, 'r') as file:
            line = file.readline().strip()
            # Reads the tile portion
            while line != '':
                tiles.append([char for char in line])
                line = file.readline().strip()
                
            line = file.readline().strip() # Skips the blank line in the file
            
            # Reads the entity portion
            while line != '':
                attributes = line.split(',')
                entity = entity_map[attributes[0]](
                    (int(attributes[1]), int(attributes[2])),
                    int(attributes[3]),
                    int(attributes[4]),
                    int(attributes[5])
                )
                entities.append(entity)
                line = file.readline().strip()
                
        return tiles, entities
    
    except IOError as error:
        tk.messagebox.showerror(
            title=IO_ERROR_TITLE,
            message=IO_ERROR_MESSAGE + str(error)
        )
    

if __name__ == "__main__":
    main()
