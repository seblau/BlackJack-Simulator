BlackJack-Simulator with OMEGA II Card Counting
==============================================

Flexible BlackJack-Simulator written in Python. It takes a given basic strategy as input (defined in a .csv-file) and simulates that strategy over a given amount of time. The simulator also counts cards sticking to the [OMEGA II Count](http://www.countingedge.com/card-counting/advanced-omega-ii/), which basically gives every card some value. Depending on the current count the bet size gets adjusted.

    python BlackJack.py strategy/BasicStrategy.csv

Omega II Count:

| 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | J | Q | K | A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| +1 | +1 | +2 | +2 | +2 | +1 | 0 | -1 | -2 | -2 | -2 | -2 | 0 |

So, for example if there is a player-favorable count like +20 by 2 decks remaining, the simulator bets the standard bet times the specified *BET_SPREAD*.

### Result

The simulator provides a result per game played and an overall result summing up all the game results. The following output for example  indicates, that in game no. 67 the simulator won 18 hands more than he lost. On the other hand in game no. 68 the simulator lost 120 hands more than he won.

     ...
     WIN for Game no. 67: 18.000000
     WIN for Game no. 68: -120.000000
     ...

This graph display every game with its total won or lost hands. You can see that in some rare games about 60 more hands are lost/won than won/lost. If the expectation is positive, you have developed a *Winning BlackJack Strategy*, which is the case for the provided BasicStrategy plus the OMEGA II count.

![Gaussian Distribution](/documentation/gaussian.png?raw=true)

This graph displays the development of the count for each game. You can see that the card count in rare cases even exceeds 40 and is on average as you would expect 0.

![Counts Distribution](/documentation/counts.png?raw=true)

### Gaming Rules

The simulator plays with the following casino rules:

* Dealer stands on soft 17
* Double down after splitting hands is allowed
* No BlackJack after splitting hands
* 3 times 7 is counted as a BlackJack

### Configuration Variables

| Variable        | Description         |
| ------------- |-------------|
| *GAMES*  | The number of games that should be played |
| *ROUNDS_PER_GAME*  | The number of rounds that should be played per game |
| *SHOE_SIZE*   | The number of decks that are used |
| *SHOE_PENETRATION*  | Indicates the percentage of cards that still remain in the shoe, when the shoe gets reshuffled |
| *BET_SPREAD*  | The multiplier for the bet size in a player favorable counting situation |

### Sample Configuration

    GAMES = 1
    ROUNDS = 10
    SHOE_SIZE = 8
    SHOE_PENETRATION = 0.2 # reshuffle after 80% of all cards are played
    BET_SPREAD = 20.0 # Bet 20-times the money if the count is palyer-favorable
    
### Strategy

Any strategy can be feeded into the simulator as a .csv file. The default strategy that comes with this simulator looks like the following:

![Default Strategy](/documentation/strategy.png?raw=true)

* The first column shows both player's cards added up
* The first row shows the dealers up-card
* S ... Stand
* H ... Hit
* Sr ... Surrender
* D ... Double Down
* P ... Split
