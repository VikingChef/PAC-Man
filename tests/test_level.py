"""Tests for active Pac-Man level state and timer behaviour."""

from pacman.config.models import LevelConfig
from pacman.game.ghost_factory import create_ghosts
from pacman.game.ghost import GhostState
from pacman.game.level import Level
from pacman.game.pacgum import PacgumType
from pacman.game.player import Player
from pacman.maze.direction import Direction
from pacman.maze.maze import Maze
from pacman.maze.wall import Wall
from pacman.game.ghost import Ghost, GhostIdentity


def test_level_initializes_state() -> None:
    """Verify that Level stores and initializes relevant data."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Create the level with a known starting timer and empty pacgum state.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    # Verify that constructor input became the level's initial state.
    assert level.config == config
    assert level.maze == maze
    assert level.player == player
    assert level.remaining_time == 90
    assert level.pacgums == {}


def test_level_tick_reduces_remaining_time() -> None:
    """Verify that tick reduces the remaining level time."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    # Simulate ten elapsed seconds.
    level.tick(10)

    # The timer should decrease by exactly the elapsed amount.
    assert level.remaining_time == 80


def test_level_tick_does_not_go_below_zero() -> None:
    """Verify that tick does not go under zero."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    # Simulate more elapsed time than remains on the level timer.
    level.tick(100)

    # The timer should clamp at zero instead of becoming negative.
    assert level.remaining_time == 0


def test_time_is_up() -> None:
    """Verify that the level reports when time is up."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    # Reduce the timer exactly to zero.
    level.tick(90)

    # The property should report that time is up.
    assert level.is_time_up is True


def test_time_is_left() -> None:
    """Verify that the level reports time is not up before zero."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with a known amount of remaining time.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    # Reduce the timer to half its starting value.
    level.tick(45)

    # The property should report that time remains.
    assert level.is_time_up is False


def test_collect_pacgum_removes_and_returns_pacgum() -> None:
    """Verify that collecting a pacgum removes and returns it."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start the level with one known normal pacgum.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={
            (0, 0): PacgumType.PACGUM,
        },
    )

    # Collect the pacgum from its known position.
    collected = level.collect_pacgum((0, 0))

    # Collection should report the type of pacgum that was removed.
    assert collected == PacgumType.PACGUM

    # The collected pacgum should no longer remain in the level state.
    assert (0, 0) not in level.pacgums


def test_collect_pacgum_returns_none_when_empty() -> None:
    """Verify that collecting from an empty position returns None."""

    # Build the minimal dependencies needed for one active level.
    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    # Start with no pacgums so the requested position is empty.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    # Attempt to collect from a position containing no pacgum.
    collected = level.collect_pacgum((0, 0))

    # Empty positions should be handled normally rather than raising an error.
    assert collected is None


def test_level_is_not_complete_with_pacgums() -> None:
    """Verify that a level with pacgums remaining is not complete."""

    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={
            (0, 0): PacgumType.PACGUM,
        },
    )

    assert level.is_complete is False


def test_level_is_complete_without_pacgums() -> None:
    """Verify that a level without pacgums is complete."""

    config = LevelConfig(
        number=1,
        width=1,
        height=1,
    )

    maze = Maze([[Wall.NONE]])

    player = Player(
        spawn_position=(0, 0),
        spawn_direction=Direction.EAST,
    )

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[],
        time_limit=90,
        pacgums={},
    )

    assert level.is_complete is True


def test_ghosts_become_frightened() -> None:
    """Verify that frighten_ghosts changes all ghost states."""

    # Build a 21x21 open maze for the four ghosts.
    config = LevelConfig(
        number=1,
        width=21,
        height=21,
    )

    maze = Maze([
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ])

    player = Player(
        spawn_position=(10, 10),
        spawn_direction=Direction.EAST,
    )

    # Create the four ghosts at their designated spawn positions.
    ghosts = create_ghosts(maze)

    # Create the level with our player and four ghosts.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )

    # Verify that all ghosts initially start enraged.
    for ghost in level.ghosts:
        assert ghost.state == GhostState.ENRAGED

    # Change all ghosts to their frightened state.
    level.frighten_ghosts()

    # Verify that all ghosts change state after calling frighten_ghosts.
    for ghost in level.ghosts:
        assert ghost.state == GhostState.FRIGHTENED


def test_ghosts_return_to_enraged_when_timer_expires() -> None:
    """Verify that ghosts return to ENRAGED when frightened timer expires."""

    # Build a 21x21 open maze for the four ghosts.
    config = LevelConfig(
        number=1,
        width=21,
        height=21,
    )

    maze = Maze([
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ])

    player = Player(
        spawn_position=(10, 10),
        spawn_direction=Direction.EAST,
    )

    # Create the four ghosts at their designated spawn positions.
    ghosts = create_ghosts(maze)

    # Create the level with our player and four ghosts.
    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )

    # Verify that all ghosts initially start enraged.
    for ghost in level.ghosts:
        assert ghost.state == GhostState.ENRAGED

    # Frighten all ghosts and start the six-second timer.
    level.frighten_ghosts()

    assert level.frightened_timer == 6

    # Simulate two seconds passing.
    level.tick(2)

    assert level.frightened_timer == 4

    # Verify that all ghosts retain frightened state.
    for ghost in level.ghosts:
        assert ghost.state == GhostState.FRIGHTENED

    # Simulate all 6 seconds passing.
    level.tick(4)

    assert level.frightened_timer == 0

    # Verify that all ghosts revert to enraged state.
    for ghost in level.ghosts:
        assert ghost.state == GhostState.ENRAGED


def test_enraged_ghost_moves_towards_player() -> None:
    """Verify that an enraged ghost moves closer to Pac-Man."""

    # Build an open maze with Pac-Man in the centre.
    config = LevelConfig(number=1, width=21, height=21)
    maze = Maze([
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ])
    player = Player(
        spawn_position=(10, 10),
        spawn_direction=Direction.EAST,
    )
    ghosts = create_ghosts(maze)

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )

    # Measure the first ghost's distance before movement.
    ghost = level.ghosts[0]
    old_distance = (
        abs(ghost.position[0] - player.position[0])
        + abs(ghost.position[1] - player.position[1])
    )

    level.move_ghosts()

    # The ghost should now be exactly one cell closer.
    new_distance = (
        abs(ghost.position[0] - player.position[0])
        + abs(ghost.position[1] - player.position[1])
    )

    assert new_distance == old_distance - 1
    assert player.position == (10, 10)


def test_frightened_ghost_moves_away_from_player() -> None:
    """Verify that a frightened ghost moves farther from Pac-Man."""

    # Build an open maze with Pac-Man in the centre.
    config = LevelConfig(number=1, width=21, height=21)
    maze = Maze([
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ])
    player = Player(
        spawn_position=(10, 10),
        spawn_direction=Direction.EAST,
    )
    ghosts = create_ghosts(maze)

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )

    # Activate frightened behaviour before moving the ghosts.
    level.frighten_ghosts()

    ghost = level.ghosts[0]
    old_distance = (
        abs(ghost.position[0] - player.position[0])
        + abs(ghost.position[1] - player.position[1])
    )

    level.move_ghosts()

    # The frightened ghost should move exactly one cell farther away.
    new_distance = (
        abs(ghost.position[0] - player.position[0])
        + abs(ghost.position[1] - player.position[1])
    )

    assert new_distance == old_distance + 1
    assert ghost.state == GhostState.FRIGHTENED
    assert player.position == (10, 10)


def test_all_ghosts_move_one_legal_cell() -> None:
    """Verify that every ghost makes one legal movement."""

    # Create a level with four ghosts in an open maze.
    config = LevelConfig(number=1, width=21, height=21)
    maze = Maze([
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ])
    player = Player(
        spawn_position=(10, 10),
        spawn_direction=Direction.EAST,
    )
    ghosts = create_ghosts(maze)

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )

    # Remember where everyone started.
    starting_positions = [ghost.position for ghost in ghosts]
    player_position = player.position

    level.move_ghosts()

    # Each ghost must move exactly one legal cell.
    assert len(ghosts) == 4

    for ghost, starting_position in zip(ghosts, starting_positions):
        dx = ghost.position[0] - starting_position[0]
        dy = ghost.position[1] - starting_position[1]

        assert (dx, dy) in [direction.value for direction in Direction]
        assert maze.can_move(starting_position, ghost.direction)

    # Ghost movement must not change Pac-Man's position.
    assert player.position == player_position


def test_ghost_collision_detected() -> None:
    """Verify that a ghost sharing the player's position is detected."""

    # Create a small open maze.
    config = LevelConfig(number=1, width=3, height=3)
    maze = Maze([
        [Wall.NONE for _ in range(3)]
        for _ in range(3)
    ])

    player = Player(
        spawn_position=(1, 1),
        spawn_direction=Direction.EAST,
    )

    ghost = Ghost(
        spawn_position=(1, 1),
        identity=GhostIdentity.EGO_MACHINE,
        spawn_direction=Direction.WEST,
    )

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[ghost],
        time_limit=90,
        pacgums={},
    )

    assert level.check_ghost_collision() == [ghost]


def test_ghost_collision_is_none() -> None:
    """Verify that a ghost does not trigger fake collision."""

    # Create a small open maze.
    config = LevelConfig(number=1, width=3, height=3)
    maze = Maze([
        [Wall.NONE for _ in range(3)]
        for _ in range(3)
    ])

    player = Player(
        spawn_position=(1, 1),
        spawn_direction=Direction.EAST,
    )

    ghost = Ghost(
        spawn_position=(0, 0),
        identity=GhostIdentity.EGO_MACHINE,
        spawn_direction=Direction.WEST,
    )

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=[ghost],
        time_limit=90,
        pacgums={},
    )

    assert level.check_ghost_collision() == []


def test_multiple_ghost_collisions() -> None:
    """Verify that all ghosts sharing the player's cell are detected."""

    # Create a small open maze.
    config = LevelConfig(number=1, width=3, height=3)
    maze = Maze([
        [Wall.NONE for _ in range(3)]
        for _ in range(3)
    ])

    player = Player(
        spawn_position=(1, 1),
        spawn_direction=Direction.EAST,
    )

    # Place two ghosts on Pac-Man and one elsewhere.
    ghosts = [
        Ghost((1, 1), GhostIdentity.EGO_MACHINE, Direction.WEST),
        Ghost((1, 1), GhostIdentity.TERF_HAG, Direction.NORTH),
        Ghost((0, 0), GhostIdentity.ORANGE_PUNCHLINE, Direction.EAST),
    ]

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={},
    )

    # Only the two ghosts sharing Pac-Man's cell should be returned.
    assert level.check_ghost_collision() == ghosts[:2]


def test_reset_positions_preserves_level_progress() -> None:
    """Verify that resetting positions preserves level progress."""

    # Create a level with four ghosts and a pacgum.
    config = LevelConfig(number=1, width=21, height=21)
    maze = Maze([
        [Wall.NONE for _ in range(21)]
        for _ in range(21)
    ])

    player = Player(
        spawn_position=(10, 10),
        spawn_direction=Direction.EAST,
    )
    ghosts = create_ghosts(maze)

    level = Level(
        config=config,
        maze=maze,
        player=player,
        ghosts=ghosts,
        time_limit=90,
        pacgums={(11, 10): PacgumType.PACGUM},
    )

    # Simulate movement, collecting a pacgum, and time passing.
    player.move(maze, Direction.EAST)
    level.collect_pacgum(player.position)

    level.move_ghosts()
    level.frighten_ghosts()
    level.tick(3)

    # Reset characters without restarting the level.
    level.reset_positions()

    # Everyone should return to their original spawn positions.
    assert player.position == player.spawn_position

    for ghost in ghosts:
        assert ghost.position == ghost.spawn_position
        assert ghost.direction == ghost.spawn_direction
        assert ghost.state == GhostState.ENRAGED

    # Frightened mode ends, but level progress remains unchanged.
    assert level.frightened_timer == 0
    assert level.remaining_time == 87
    assert level.pacgums == {}
