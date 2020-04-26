# battleship

Last-minute Remote Game Jam submission.

## Inspiration

Game Grumps play-through of Space Quest 5 features a battleship-esqe minigame
against the game's eventual antagonist.

## Game Jam Scope

* Client-Server multiplayer.
* PVP-only: no AI.
* Single-lobby support: one active game at a time.
* Up-to-N players per game.
* Turn-based gameplay.

## Design

The game is divided into three phases:
1. Game Lobby
1. Game Setup
1. Game Turn

During the Game Lobby phase, players register a username and are provided an
identifying secret token. This token identifies them to the server and
represents a server-side mapping to the username. Players can change personal
settings during this time, such as their armada's name, color, etc. There may be
some lobby-level settings that could be changed at this time as well, such as
the map, available weapons, etc. Players can mark themselves as "ready" when
they have finished making any changes.

When all players have marked themselves as ready in the Game Lobby Phase, the
game transitions into the Game Setup phase.

During the Game Setup phase, players position their ships across the map. Each
player operates in a completely-isolated area of the map. Each isolated
player-map is equivalent, with the exception of changes in rotation. This adds
some variety without introducing player-specific advantages.

When all players have marked themselves as ready in the Game Setup Phase, the
game transitions into the Game Turn phase.

During the Game Turn phase, players queue up "launches" of various weapons and
utilities. Each player submits (or overrides a previous) launch, which will take
effect at different times based on the flight-time of the chosen weapon. When
a player has chosen their launch for the current turn, they can mark themselves
as "ready". When all players have marked themselves as "ready", the turn will
resolve (simultaneously for all players), and the next turn will begin.

While a player has any ships remaining, they can still participate in the Game
Turn phase. When a player loses all of their ships, they will be provided with
complete information about the player maps and launch queues.

Game Lobby API

* Register (Username) -> Token, Error
* Kick (Token, Username) -> Ack, Error
* Ready (Token, Ready) -> Ack, Error

Game Setup API

* Place ship (Token, Ship, Position, Rotation) -> Ack, Error
* Ready (Token, Ready) -> Ack, Error

Game Turn API

* Launch (Token, Weapon, Position) -> Ack, Error
* Ready (Token, Ready) -> Ack, Error
