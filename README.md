BlackJack-Simulator
===================

Flexible BlackJack-Simulator written in Python. It takes a given basic strategy as input (defined in a .csv-file) and simulates that strategy over a given amount of time.
The result is the number of hands lost/won.

For example the output 117.0 indicates, that the simulator won 117 hands more than he lost. On the other hand the output -55.0 indicates, that the simulator lost 55 hands more than he won.

    python BlackJack.py strategy/BasicStrategy.csv

### Gaming Rules

The simulator plays with the following casino rules:

* Dealer stands on soft 17
* Double down after splitting hands is allowed
* No BlackJack after splitting hands
* 3 times 7 is counted as a BlackJack

### Configuration Variables

| Variable        | Description         |
| ------------- |-------------|
| *ROUNDS*  | The number of rounds that should be played |
| *SHOE_SIZE*   | The number of decks that are used |
| *SHOE_PENETRATION*  | Indicates the percentage of cards that still remain in the shoe, when the shoe gets reshuffled |

### Sample Configuration

    ROUNDS = 10
    SHOE_SIZE = 8
    SHOE_PENETRATION = 0.2 # reshuffle after 80% of all cards are played
