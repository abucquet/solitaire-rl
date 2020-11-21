import pprint
from tqdm import tqdm

from solitaire import Game

import random
import numpy as np

import pickle
import time


N_GAMES_TO_PLAY = 1

def get_q_value(q_table, state, action):
    if state not in q_table:
        q_table[state] = {}

    if action not in q_table[state]:
        q_table[state][action] = np.random.randint(-3, 3)

    return q_table[state][action]

#### TODOs
#### Decompose until a play_game method, that way we can evaluate the perf after training
#### Change reward function

def main(epsilons, n_train, n_test, filename=None, save=False):
    win = 0

    # Hyperparameters
    alpha = 0.2
    gamma = 0.9

    stages = []

    q_table = {} # dict of states to dict of actions to value

    # For plotting metrics
    all_total_moves = []
    all_win_loss = []
    how_far_from_win = []
    n_win_train = 0
    n_win_test = 0

    for i in range(1, n_train + n_test):
        if i <= n_train * 1/4:
            epsilon = epsilons[0]
        elif i > n_train * 1/4:
            epsilon = epsilons[1]
        elif i > n_train * 2/4:
            epsilon = epsilons[2]
        elif i > n_train * 3/4:
            epsilon = epsilons[3]
        elif i > n_train:
            epsilon = epsilons[4]
        
        thisGame = Game()

        epochs, penalties, reward, = 0, 0, 0
        game_over = False
        visited_count = 0
        moves_made = 0
        
        while (not game_over) and (visited_count < 100):
            state = thisGame.current_state()

            assert thisGame.check_state(), thisGame.state_to_str()

            current_actions = thisGame.get_valid_moves()

            if (random.uniform(0, 1) < epsilon) or (state not in q_table):
                action_i = np.random.choice(range(len(current_actions))) # Explore action space
                action = current_actions[action_i]
            else:
                possible_known_actions = [
                    a for a in q_table[state].keys() if a in current_actions
                ]
                if len(possible_known_actions) == 0:
                    action_i = np.random.choice(range(len(current_actions)))
                    action = current_actions[action_i]
                else:
                    best_action = np.argmax([q_table[state][a] for a in possible_known_actions])
                    action = possible_known_actions[best_action] # Exploit learned values

            next_state, reward, move_made, game_over, win, visited = thisGame.step(action) 
            
            if not move_made: continue
            if visited:
                visited_count += 1
                thisGame.undo_move()
                continue

            moves_made += 1
            
            old_value = get_q_value(q_table, state, action)
            next_max = 0
            if next_state in q_table:
                next_max = np.max(list(q_table[state].values()))
            
            # print(old_value, reward, next_max)
            new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
            q_table[state, action] = new_value

            if reward in [-10, -100]:
                penalties += 1

            state = next_state
        
            epochs += 1
        
        all_total_moves.append(moves_made)
        all_win_loss.append(win)
        how_far_from_win.append(
            52 - sum([len(p.cards) for k, p in thisGame.blockPiles.items()])
            )
        if win: 
            if i <= n_train:
                n_win_train += 1
            else:
                n_win_test += 1

        if i % 1 == 0:
            #clear_output(wait=True)
            if win:
                print(f"Episode: {i} /--/ Moves to end {moves_made} /--/ WIN")
            else:
                print(f"Episode: {i} /--/ Moves to end {moves_made}")

    all_win_loss = np.array(all_win_loss)
    all_total_moves = np.array(all_total_moves)
    how_far_from_win = np.array(how_far_from_win)

    print("Training finished.\n")
    print("Won {} games in train and {} in test".format(n_win_train, n_win_test))
    print("Mean number of moves for winning games: {}".format(
        np.mean(all_total_moves[all_win_loss == True])
        ))
    print("Mean number of moves for losing games: {}".format(
        np.mean(all_total_moves[all_win_loss == False])
        ))
    print("Mean distance from win: {}".format(
        np.mean(how_far_from_win[all_win_loss == False])
        ))

    if save == True:
        with open(filename, "wb") as f:
            pickle.dump((q_table, all_total_moves, all_win_loss, how_far_from_win), f)
    
if __name__ == "__main__":
    # hyperparams
    epsilons = [0.9, 0.9, 0.7, 0.5, 0.1]
    n_train = 20000
    n_test = 5000

    filename = "results/small_granular_reward_205k_games_high_epsilon"
    start = time.time()
    main(epsilons, n_train, n_test, filename, save=True)
    print("Time elapsed: {} minutes".format((time.time() - start)/60))

