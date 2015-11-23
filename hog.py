"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

def roll_dice(num_rolls, dice=six_sided):
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    count, total, ones = 1, 0, 0
    while count<=num_rolls:
        dice_val=dice()
        if dice_val == 1:
            ones +=1
        total += dice_val
        count+=1
    if ones>0:
        return 1
    else:
        return total 


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'
    if num_rolls > 0:
        return roll_dice(num_rolls, dice)
    else:
        if (opponent_score%10) >= ((opponent_score//10)%10):
            return (opponent_score%10)+1
        else: 
            return ((opponent_score//10)%10) + 1

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """
    if ((score+opponent_score)%7==0):
        return four_sided
    else:
        return six_sided

def is_swap(score0, score1):
    """Return True if ending a turn with SCORE0 and SCORE1 will result in a
    swap.

    Swaps occur when the last two digits of the first score are the reverse
    of the last two digits of the second score.
    """
    return (((score0//10)%10) == (score1%10)) and (((score1//10)%10)== (score0%10))


def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, score0=0, score1=0, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first
    strategy1:  The strategy function for Player 1, who plays second
    score0   :  The starting score for Player 0
    score1   :  The starting score for Player 1
    """
    who = 0
    # Which player is about to take a turn, 0 (first) or 1 (second)
    
    while score0 <goal and score1 <goal:
        if who == 0:
            who_score, other_score, who_strategy =score0, score1, strategy0
        else:
            who_score, other_score, who_strategy=score1, score0, strategy1

        num_rolls=who_strategy(who_score, other_score)
        dice=select_dice(who_score, other_score)
        who_score+=take_turn(num_rolls, other_score, dice)
        if is_swap(who_score,other_score):
            who_score, other_score = other_score, who_score

        if who == 0:
            score0, score1, strategy0 =who_score, other_score, who_strategy
        else:
            score1, score0, strategy1=who_score, other_score, who_strategy
        who = other(who)
  
    return score0, score1

#######################
# Phase 2: Strategies #
#######################

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def averaged_dice(*args):
        count, total = 1, 0
        while count<=num_samples:
            total+=(fn(*args))
            count+=1
        return total/num_samples
    return averaged_dice
  
def max_scoring_num_rolls(dice=six_sided, num_samples=1000):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE over NUM_SAMPLES times.
    Assume that dice always return positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    count, old_max, maxo = 1, 0, 0
    while count<=10:
        new_max=make_averaged(roll_dice, num_samples=1000)(count, dice)
        if new_max>old_max:
            maxo=count
            old_max=new_max
        count+=1
    return maxo

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if False: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))


    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
        
    if take_turn(0, opponent_score, dice=six_sided)>=margin:
        return 0
    else:
        return num_rolls


def swap_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it results in a beneficial swap and
    rolls NUM_ROLLS if rolling 0 dice results in a harmful swap. It also
    rolls 0 dice if that gives at least MARGIN points and rolls NUM_ROLLS
    otherwise.
    """

    score_with0=score+take_turn(0, opponent_score, dice=six_sided)
    if is_swap(score_with0,opponent_score) and (score_with0!=opponent_score):
        if score_with0<opponent_score:
            return 0
        else: 
            return num_rolls
    else: 
        return bacon_strategy(score, opponent_score, margin, num_rolls)



def final_strategy(score, opponent_score):
    """Write a brief description of your final strategy.

    If you have a low score (1/4 or less of goal), play more riskily because 1) you have so little 
    to lose and 2)you need a lot more points to reach the goal. Either abstain when the margin is high, 
    or roll for a lot of points
    However, once your score is high (at least 3/4 of goal), then you need fewer points, and should 
    try to steadily gain those few points instead of focusing on a more high-risk, high-reward tactic.
    So, use a lower margin for rolling 0 and roll a low number (3) of dice otherwise.
    I also established a middle category of 25 to 75 percent of the goal that keeps a high margin for 
    rolling 0, but rolls slightly less (5) dice--in other words, it is a middle ground between the two 
    extremes of high and low.
    Finally, note that the values I set for margin and num_rolls, even for the low and high extremes, are
    relatively modest.  For example, the num_rolls for the risky, low play are still not so risky as to be
    10, since that level of risk of rolling 1s would probably offset its potential to return a large score.

    """
    if score<GOAL_SCORE*.25:
        return swap_strategy (score, opponent_score, margin=9, num_rolls=8)
    elif GOAL_SCORE*.25<=score<=GOAL_SCORE*.75:
        return swap_strategy (score, opponent_score, margin=9, num_rolls=5)
    else: 
        return swap_strategy (score, opponent_score, margin=3, num_rolls=3)
    


##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--final', action='store_true',
                        help='Display the final_strategy win rate against always_roll(5)')
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
    elif args.final:
        from hog_eval import final_win_rate
        win_rate = final_win_rate()
        print('Your final_strategy win rate is')
        print('    ', win_rate)
        print('(or {}%)'.format(round(win_rate * 100, 2)))
