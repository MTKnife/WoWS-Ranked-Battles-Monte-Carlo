# -*- coding: utf-8 -*-
"""
This script runs a Monte Carlo simulation of progression through a
World of Warships Ranked Battles league, to the determine the probability
of qualifying for the next league, given a certain probabilty of winning
and number of games played.

Usage:
    sim_ranked.py [-h] [--stars=<int>] [--stop=<int>]...
                  [--win_rate=<float>] [--quals_win_rate=<float>]
                  [--games_played=<int>] [--runs=<int>]

Options:
    -h --help                   Show this screen.
    --stars=<int>               The total number of stars to qualify for
                                the next league, including stars for
                                qualification matches [default: 19]
    --stop=<int>                A point (expressed in number of stars
                                earned) at which a player can't lose any
                                stars. Supply this option multiple times
                                for multiple stops. Obviously, a player
                                can't drop below 0 stars, and so that
                                number is automatically added to the list.
                                The highest numbered stop is the point at
                                which the player moves into qualifications.
                                Enter an explicit value of 0 to indicate no
                                stops (as in the case of Gold League). By
                                default, the script uses the Bronze League
                                stops: 1, 2, 6, and 14.
    --win_rate=<float>]         The player's win rate in normal league play
                                [default: .50]
    --quals_win_rate=<float>    The player's win rate in quals matches
                                (that is, the player has passed the
                                 "stop"); if no value is supplied, the
                                normal win rate is used.
    --games_played=<int>        The maximum number of games to be played in
                                each simulation [default: 200]
    --runs=<int>                The number of times the simulation is to be
                                run [default: 1000]


"""

from docopt import docopt
import random
from numpy import empty
from statsmodels.stats.proportion import proportion_confint


DEFAULT_STOPS = [1, 2, 6, 14]


def sim_league(stars = 19, stops = [1, 2, 6, 14], win_rate = .50,
               quals_win_rate = None, games_played = 200):
    """
    Simulates one run through a Ranked Battles league.

    :param stars: The total number of stars to qualify for the next league,
        including stars for qualification matches
    :param stops: An iterable of points (expressed in number of stars
        earned) at which a player can't lose any more stars. Obviously, a
        player can't drop below 0 stars, and so that number is
        automatically added to the list.
    :param win_rate: The player's win rate in normal league play
    :param quals_win_rate: The player's win rate in quals matches (that
        is, once the player has passed the last point in "stops"); if no
        value is supplied here, the normal win rate is used.
    :param games_played: The number of games to simulate

    :returns: Total number of games played if the player qualifies for the
        next league, 0 otherwise

    """

    # Add 0 "stops", and turn it into a set, to speed searches.
    stops.append(0)
    stops = set(stops)
    quals_stop = max(stops)

    # Use the default for "quals_win_rate" if none was supplied.
    if not quals_win_rate:
        quals_win_rate = win_rate

    # Initialize the stars total.
    total_stars = 0

    # Each pass through this loop is a game.
    for game in range(games_played):

        cutoff = random.random()

        # If we won, increment the stars total, and check to see if we're
        # in quals now, or if we've qualified.
        if win_rate > cutoff:
            total_stars += 1
            if total_stars == quals_stop:
                win_rate = quals_win_rate
            elif total_stars == stars:
                return game + 1

        # If we lost, decrement the stars total, unless we're at a stop.
        else:
            if not total_stars in stops:
                total_stars -= 1

    # If we've passed through "games_played" games without returning, we've
    # failed to qualify.
    return 0


# Get the user-supplied options.
options = docopt(__doc__)

# Check inputs.
stars = int(options["--stars"])
if not stars > 0:
    raise ValueError('Please supply a positive integer for "stars".')
stops_text = options["--stop"]
if not stops_text:
    stops = DEFAULT_STOPS
else:
    stops = []
    for stop in stops_text:
        stops.append(int(stop))
    if min(stops) < 0:
        raise ValueError('Please supply a valid list of stops.')
win_rate = float(options["--win_rate"])
if win_rate < 0 or win_rate > 1:
    raise ValueError('The value of "win_rate" must be between 0 and 1 ' +
                     '(inclusive).')
quals_win_rate_text = (options["--quals_win_rate"])
if not quals_win_rate_text:
    quals_win_rate = win_rate
else:
    quals_win_rate = float(quals_win_rate_text)
    if win_rate < 0 or win_rate > 1:
        raise ValueError('The value of "quals_win_rate" must be between 0 ' +
                         'and 1 (inclusive).')
games_played = int(options["--games_played"])
if not games_played > 0:
    raise ValueError('Please supply a positive integer for "games_played".')
runs = int(options["--runs"])
if not runs > 0:
    raise ValueError('Please supply a positive integer for "runs".')

# Run the simulations.
results = empty(runs)
for run in range(runs):
    print("Starting run " + str(run + 1) + ".", end = "\r")
    results[run] = sim_league(stars = stars, stops = stops, win_rate = win_rate,
                              quals_win_rate = quals_win_rate,
                              games_played = games_played)

# Print the results.
num_quals = (results > 0).sum()
proportion_quals = num_quals / runs
conf_int = proportion_confint(num_quals, runs)

print("Proportion of qualifications: " + str(proportion_quals))
print("Confidence interval: " + str(round(conf_int[0], 3)) + " to " +
      str(round(conf_int[1], 3)))
