from card_elements import Card, Deck, Pile
import numpy as np

VALUES = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
    
SUITS = { #keys are unicode symbols for suits
    u'\u2660': "black",
    u'\u2665': "red",
    u'\u2663': "black",
    u'\u2666': "red",
}

NUM_PLAY_PILES = 7

VISITED = 1
NOT_VISITED = 0

TO_BLOCK = 1
TO_PILE = 2
DEAL_CARDS = 3

class Game:
    
    def __init__(self):
        self.deck = Deck(VALUES, SUITS)
        self.playPiles = []
        for i in range(NUM_PLAY_PILES):
            thisPile = Pile()
            [thisPile.addCard(self.deck.takeFirstCard(flip=False)) for j in range(i+1)]
            thisPile.flipFirstCard()  
            self.playPiles.append(thisPile)
        self.blockPiles = {suit: Pile() for suit in SUITS}
        self.deck.cards[0].flip()
        self.cache = {}
        self.stored_state = None
        self.visited = set()
    
    def getGameElements(self):
        returnObject = {
            "deck": str(self.deck),
            "playPiles": [str(pile) for pile in self.playPiles],
            "blockPiles": {suit: str(pile) for suit, pile in self.blockPiles.items()}
        }
        return returnObject
        
    def checkCardOrder(self,higherCard,lowerCard):
        if lowerCard.value == "K": return False
        suitsDifferent = SUITS[higherCard.suit] != SUITS[lowerCard.suit]
        valueConsecutive = VALUES[VALUES.index(higherCard.value)-1] == lowerCard.value
        return suitsDifferent and valueConsecutive
    
    def checkIfCompleted(self):
        deckEmpty = len(self.deck.cards)==0
        pilesEmpty = all(len(pile.cards)==0 for pile in self.playPiles)
        blocksFull = all(len(pile.cards)==13 for suit,pile in self.blockPiles.items())
        return deckEmpty and pilesEmpty and blocksFull
            
    def addToBlock(self, card):
        # print("Called addToBlock on card {}".format(card))
        # print(self.blockPiles[card.suit])
        if card is None:
            return False
        elif len(self.blockPiles[card.suit].cards)>0:
            highest_value = self.blockPiles[card.suit].cards[0].value
            if VALUES[VALUES.index(highest_value)+1] == card.value:
                self.blockPiles[card.suit].cards.insert(0,card)
                return True
            else:
                return False   
        else: 
            if card.value=="A":
                self.blockPiles[card.suit].cards.insert(0,card)
                return True
            else:
                return False

    def can_add_to_block(self, card):
        if card is None:
            return False
        elif len(self.blockPiles[card.suit].cards)>0:
            highest_value = self.blockPiles[card.suit].cards[0].value
            if highest_value == "K": return False
            return VALUES[VALUES.index(highest_value)+1] == card.value  
        else: 
            return card.value=="A"
    
    def get_valid_moves(self, verbose=False):

        #Pre: flip up unflipped pile end cards -> do this automatically
        [pile.cards[0].flip() for pile in self.playPiles if len(pile.cards)>0 and not pile.cards[0].flipped]
         
        # for pile in self.playPiles:
        #     print(pile)

        valid_moves = []

        #1: check if there are any play pile cards you can play to block piles
        for i, pile in enumerate(self.playPiles):
            if len(pile.cards) > 0 and self.can_add_to_block(pile.cards[0]):
                valid_moves.append((TO_BLOCK, i, -1))
            
        #2: check if cards in deck can be added
        if self.can_add_to_block(self.deck.getFirstSideCard()):
            valid_moves.append((TO_BLOCK, -1, -1))
            
        #3: move kings to open piles
        for i, pile in enumerate(self.playPiles):
            if len(pile.cards)==0: #pile has no cards
                for j, pile2 in enumerate(self.playPiles):
                    if len(pile2.cards)>1 and pile2.cards[0].value == "K":
                        valid_moves.append((TO_PILE, j, i))
                    
                if self.deck.getFirstSideCard() is not None and self.deck.getFirstSideCard().value == "K":
                    valid_moves.append((TO_PILE, -1, i))
            
        #4: add drawn card to playPiles 
        for i, pile in enumerate(self.playPiles):
            if len(pile.cards)>0 and self.deck.getFirstSideCard() is not None:
                if self.checkCardOrder(pile.cards[0], self.deck.getFirstSideCard()):
                    valid_moves.append((TO_PILE, -1, i))
                            
        #5: move around cards in playPiles
        for i, pile1 in enumerate(self.playPiles):
            pile1_flipped_cards = pile1.getFlippedCards()
            if len(pile1_flipped_cards)>0: # if we have flipped cards on the pile
                for j, pile2 in enumerate(self.playPiles):
                    pile2_flipped_cards = pile2.getFlippedCards()
                    if i != j and len(pile2_flipped_cards)>0:
                        
                        # check whether or not we can move any number of cards
                        for transfer_cards_size in range(1,len(pile1_flipped_cards)+1):
                            cards_to_transfer = pile1_flipped_cards[:transfer_cards_size]
                            if self.checkCardOrder(pile2.cards[0],cards_to_transfer[-1]):
                                pile1_downcard_count = len(pile1.cards) - len(pile1_flipped_cards)
                                pile2_downcard_count = len(pile2.cards) - len(pile2_flipped_cards)
                                valid_moves.append((TO_PILE, i, j, transfer_cards_size))
                                # if pile2_downcard_count < pile1_downcard_count:
                                #     [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                #     pile1.cards = pile1.cards[transfer_cards_size:]
                                #     if verbose:
                                #         print("Moved {0} cards between piles: {1}".format(
                                #             transfer_cards_size,
                                #             ", ".join([str(card) for card in cards_to_transfer])
                                #                                                          ))
                                # elif pile1_downcard_count==0 and len(cards_to_transfer) == len(pile1.cards):
                                #     [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                #     pile1.cards = []
                                #     if verbose:
                                #         print("Moved {0} cards between piles: {1}".format(
                                #             transfer_cards_size,
                                #             ", ".join([str(card) for card in cards_to_transfer])
                                #                                                          ))
        # add three to the side pile
        valid_moves.append((DEAL_CARDS, -1, -1))

        return valid_moves    

    def takeTurn(self, verbose=False):
                
        #Pre: flip up unflipped pile end cards -> do this automatically
        [pile.cards[0].flip() for pile in self.playPiles if len(pile.cards)>0 and not pile.cards[0].flipped]
         
        #1: check if there are any play pile cards you can play to block piles
        for pile in self.playPiles:
            if len(pile.cards) > 0 and self.addToBlock(pile.cards[0]):
                card_added = pile.cards.pop(0)
                if verbose:
                    print("Adding play pile card to block: {0}".format(str(card_added)))
                return True
            
        #2: check if cards in deck can be added
        if self.addToBlock(self.deck.getFirstCard()):
            card_added = self.deck.takeFirstCard()
            if verbose:
                print("Adding card from deck to block: {0}".format(str(card_added)))
            return True
            
        #3: move kings to open piles
        for pile in self.playPiles:
            if len(pile.cards)==0: #pile has no cards
                for pile2 in self.playPiles:
                    if len(pile2.cards)>1 and pile2.cards[0].value == "K":
                        card_added = pile2.cards.pop(0)
                        pile.addCard(card_added)
                        if verbose:
                            print("Moving {0} from Pile to Empty Pile".format(str(card_added)))
                        return True
                    
                if self.deck.getFirstCard() is not None and self.deck.getFirstCard().value == "K":
                    card_added = self.deck.takeFirstCard()
                    pile.addCard(card_added)
                    if verbose:
                        print("Moving {0} from Deck to Empty Pile".format(str(card_added)))
                    return True
            
        #4: add drawn card to playPiles 
        for pile in self.playPiles:
            if len(pile.cards)>0 and self.deck.getFirstCard() is not None:
                if self.checkCardOrder(pile.cards[0],self.deck.getFirstCard()):
                    card_added = self.deck.takeFirstCard()
                    pile.addCard(card_added) 
                    if verbose:
                        print("Moving {0} from Deck to Pile".format(str(card_added)))
                    return True
                            
        #5: move around cards in playPiles
        for pile1 in self.playPiles:
            pile1_flipped_cards = pile1.getFlippedCards()
            if len(pile1_flipped_cards)>0:
                for pile2 in self.playPiles:
                    pile2_flipped_cards = pile2.getFlippedCards()
                    if pile2 is not pile1 and len(pile2_flipped_cards)>0:
                        for transfer_cards_size in range(1,len(pile1_flipped_cards)+1):
                            cards_to_transfer = pile1_flipped_cards[:transfer_cards_size]
                            if self.checkCardOrder(pile2.cards[0],cards_to_transfer[-1]):
                                pile1_downcard_count = len(pile1.cards) - len(pile1_flipped_cards)
                                pile2_downcard_count = len(pile2.cards) - len(pile2_flipped_cards)
                                if pile2_downcard_count < pile1_downcard_count:
                                    [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                    pile1.cards = pile1.cards[transfer_cards_size:]
                                    if verbose:
                                        print("Moved {0} cards between piles: {1}".format(
                                            transfer_cards_size,
                                            ", ".join([str(card) for card in cards_to_transfer])
                                                                                         ))
                                    return True
                                elif pile1_downcard_count==0 and len(cards_to_transfer) == len(pile1.cards):
                                    [pile2.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                                    pile1.cards = []
                                    if verbose:
                                        print("Moved {0} cards between piles: {1}".format(
                                            transfer_cards_size,
                                            ", ".join([str(card) for card in cards_to_transfer])
                                                                                         ))
                                    return True


        return False
     
    def do_move(self, move):
        if len(move) == 4: # move a bunch of cards from pile a to b
            _, pile_origin_i, pile_dest_i, transfer_cards_size = move
            pile_origin = self.playPiles[pile_origin_i]
            pile_dest = self.playPiles[pile_dest_i]
            pile_dest_flipped_cards = pile_dest.getFlippedCards()
            pile_origin_flipped_cards = pile_origin.getFlippedCards()

            pile_dest_downcard_count = len(pile_dest.cards) - len(pile_dest_flipped_cards)
            pile_origin_downcard_count = len(pile_origin.cards) - len(pile_origin_flipped_cards)
            
            cards_to_transfer = pile_origin_flipped_cards[:transfer_cards_size]
            # print("Transfering cards {}".format([str(c) for c in cards_to_transfer]))

            if len(cards_to_transfer) < len(pile_origin.cards):
                [pile_dest.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                pile_origin.cards = pile_origin.cards[transfer_cards_size:] 
                
            elif len(cards_to_transfer) == len(pile_origin.cards):
                [pile_dest.cards.insert(0,card) for card in reversed(cards_to_transfer)]
                pile_origin.cards = []
            return True

        elif len(move) == 3:
            action, origin, _ = move

            if action == TO_BLOCK:
                if origin == -1: # deck
                    if self.addToBlock(self.deck.getFirstSideCard()):
                        self.deck.takeFirstSideCard()
                        return True
                else: # play pile i
                    pile = self.playPiles[origin]
                    # print(pile)
                    if len(pile.cards) > 0 and self.addToBlock(pile.cards[0]):
                        card_added = pile.cards.pop(0)
                        return True
                return False

            if action == TO_PILE: # from deck to play_pile + move kings
                #move kings to open piles
                action, origin, dest = move

                if origin == -1: # deck
                    card_added = self.deck.takeFirstSideCard()
                    self.playPiles[dest].addCard(card_added)
                    return True 
                else: # play pile i
                    pile_dest = self.playPiles[dest]
                    pile_origin = self.playPiles[origin]
                    # print("Origin ", str(pile_origin))
                    # print("Dest ", str(pile_dest))
                    pile_dest.addCard(pile_origin.cards[0])
                    card_added = pile_origin.cards.pop(0)
                    return True

            if action == DEAL_CARDS:
                self.deck.drawCardsToSide()
                return True

        return False

    def check_state(self):

        correct = True

        for suit, pile in self.blockPiles.items():
            if len(pile.cards) == 0: continue
            prev_card = pile.cards[0]
            for card in pile.cards[1:]:
                if VALUES.index(prev_card.value) != (VALUES.index(card.value) + 1):
                    print("Pile {}: {}".format(suit, pile))
                    correct = False
                prev_card = card

        for i, pile in enumerate(self.playPiles):
            if len(pile.cards) == 0: continue
            prev_card = pile.cards[0]
            for card in pile.cards[1:]:
                if not card.flipped: break
                if VALUES.index(prev_card.value) != (VALUES.index(card.value) - 1):
                    print("Pile {}: {}".format(i, pile)) 
                    correct = False  
                prev_card = card

        return correct

    def undo_move(self):
        self.deck, self.playPiles, self.blockPiles = self.stored_state

    def state_to_str(self):
        state = ""

        # add all the play Piles
        for p in self.playPiles:
            state += str(p)

        # deck + side_pile
        state += str(self.deck)

        # block piles
        for s in SUITS:
            state += str(self.blockPiles[s])

        return state

    def already_visited(self):
        str_state = self.state_to_str()

        if str_state not in self.visited:
            self.visited.add(str_state)
            return False
        return True

    def current_state(self):
        # block piles
        sorted_lengths = sorted([len(self.blockPiles[s].cards) for s in SUITS])
        block_pile_lengths = ",".join([str(l) for l in sorted_lengths])
        
        # play piles
        sorted_lengths = sorted([len(p.cards) for p in self.playPiles])
        play_pile_lengths = ",".join([str(l) for l in sorted_lengths])

        # play piles flipped
        lengths = [len(p.cards) for p in self.playPiles]
        flipped_lengths = [len(p.getFlippedCards()) for p in self.playPiles]
        sorted_flip = [
            f for _, f in sorted(zip(lengths, flipped_lengths))
        ]
        play_pile_flipped_lengths = ",".join([str(l) for l in sorted_flip])

        # deck length is implicit if we know the others

        return "/".join([
            block_pile_lengths, play_pile_lengths #, play_pile_flipped_lengths
            ])
    
    def game_over(self):
        # win game
        if sum([len(b.cards) for _, b in self.blockPiles.items()]) == 52:
            return True, True

        # lose game
        if len(self.get_valid_moves()) == 0:
            return True, False

        # game still on
        return False, False

    def get_reward(self, move):
        if move[0] == TO_BLOCK:
            return 6 # move card to block pile: very good!

        if move[0] == TO_PILE:
            if len(move) != 4:
                return 2 # move card from deck to play pile
            else:
                return move[3] # move cards between play piles

        if move[0] == DEAL_CARDS:
            return 0 # deal cards: neutral

        return 0

    def step(self, move):

        self.stored_state = [
            self.deck.copy(deep=True),
            self.playPiles.copy(),
            self.blockPiles.copy()
        ]

        move_made = self.do_move(move)
        reward = self.get_reward(move)
        game_over, win = self.game_over()
        visited = False

        if game_over and win:
            reward += 100
        elif game_over and not win:
            reward -= 100

        if self.already_visited():
            reward -= 100
            visited = True

        # reorder the playPiles in order of size
        def get_length(pile):
            return len(pile.cards)
        self.playPiles = sorted(self.playPiles, key=get_length)

        return self.current_state(), reward, move_made, game_over, win, visited

    def simulate(self, draw = False, verbose=False):
        while True:

            if self.already_visited():
                return False

            valid_moves = self.get_valid_moves()
            self.deck.print_all()
            print("Block piles")
            [print(v) for c, v in self.blockPiles.items()]
            print(valid_moves)


            move = None
            if len(valid_moves) == 1:
                move = valid_moves[0]
            elif len(valid_moves[:-1]) > 1:
                idx = np.random.choice(list(range(1, len(valid_moves[:-1]))))
                move = valid_moves[idx]
            else:
                move = valid_moves[0]
            
            move_done = self.do_move(move)
            print(move_done, move)
            if move[0] == 3:
                self.deck.print_all()
                #return

            if not move_done: return

        # for move in valid_moves:
        #     if not self.do_move(move): continue
        #     self.simulate()
        #     self.undo_move()
        
    