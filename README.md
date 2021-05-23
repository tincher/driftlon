# Driftlon / Lestimator
Driftlon tries to learn how to predict future professional LoL-players, using the public available ranked games on their private profiles.

## Data Retrieval
The data-fetcher fetches and combines data from multiple sources.

#### Leaguepedia
From [Leaguepedia](https://lol.fandom.com) I get the list of active players.
I only use those players to be pro-level who have played more than 20 games.
This way I filter for only the best of the best and have a pretty harsh entry requirement.
Currently only those players from the best leagues are considered.
These leagues are the LCK, LEC, LCS and the LPL (leagues who continue to succeed at international events).

#### TrackingThePros (TTP)
[TrackingThePros (TTP)](https://www.trackingthepros.com/) provides the list of soloq account names for each player.
Players who are not listed by TTP are ignored.

Leaguepedia also delivers us a list of each the players soloq accounts.
These lists are probably not complete, since Leaguepedia is only a wiki.
An alternative to be explored could be [LOLProps](https://lolpros.gg/) which was still in development at the start of this project.

#### Riot Games
The official [Riot Games API](https://developer.riotgames.com/) provides the data for the games played.
For each account of each player the games from the last 2 patches are retrieved.
All data is saved to support multiple ways of preprocessing.
For each game saved the number of games played, the timestamp of retrieval and the player ID is saved alongside the game data itself.

## Preprocessor
The preprocessor prepares the data and filters unnecessary data points to reduce complexity.
Currently the filtering is done by the suggestions of an expert (player who was in Diamond 2).
In the future I plan to do a correlation analysis and use those variables that seem logical.
The filtered attributes for each match get standardized (z-score).

## Model
The most logical model would be a Recurrent Neural Network.
The experiments using a LSTM and GRU cell have yet to deliver a good model.
Old models have been lost, so currently I plan to rewrite the Neural Nets using PyTorch.
Conventional losses could reach their limits, as the data is heavily unbalanced.
An idea could be to balance by pro games played.
