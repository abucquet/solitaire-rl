import random

class Card:
    
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.flipped = False
        
    def flip(self):
        self.flipped = not self.flipped
        
    def __str__(self):        
        return "{0} {1}".format(self.value,self.suit)
    
class Pile:
    
    def __init__(self):
        self.cards = []
        
    def addCard(self, Card):
        self.cards.insert(0,Card)
        
    def flipFirstCard(self):
        if len(self.cards)>0:
            self.cards[0].flip()
            
    def getFlippedCards(self):
        return [card for card in self.cards if card.flipped]
    
    def __str__(self):
        # if len(self.cards) > 0:
        #     print("Bottom card {}".format(str(self.cards[0])))

        returnedCards = [str(card) for card in reversed(self.getFlippedCards())]
        flippedDownCount = len(self.cards) - len(self.getFlippedCards())
        if flippedDownCount>0:
            returnedCards.insert(0,"{0} cards flipped down".format(flippedDownCount))
        return ", ".join(returnedCards)

class Deck: 
    
    def __init__(self, values, suits):
        self.cards = []
        self.cache = []
        self.side_pile = []
        self.populate(values,suits)
        self.shuffle()
        
    def __str__(self):
        deck = ", ".join([str(card) for card in self.cards])
        side = ", ".join([str(card) for card in self.side_pile])
        return deck + "/" + side

    def populate(self, values, suits):
        for suit in suits:
            for value in values:
                thisCard = Card(suit,value)
                self.cards.append(thisCard)  
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def getFirstCard(self):
        if len(self.cards)>0:
            return self.cards[0]
        else:
            return None
    
    def takeFirstCard(self, flip=True):
        if len(self.cards)>0:
            nextCard = self.cards.pop(0)
            if flip and len(self.cards)>0:
                self.cards[0].flip()
            return nextCard
        else:
            return None

    def getFirstSideCard(self):
        if len(self.side_pile)>0:
            return self.side_pile[-1]
        else:
            return None
    
    def takeFirstSideCard(self, flip=True):
        if len(self.side_pile)>0:
            nextCard = self.side_pile[-1]
            self.side_pile = self.side_pile[:-1]
            return nextCard
        else:
            return None
        
    def drawCard(self):
        if len(self.cards)>0:
            self.cards[0].flip()
            self.cards.append(self.cards.pop(0))
            self.cards[0].flip()

    def print_all(self):  
        print("Deck:", end=" ")
        for card in self.cards:
            print(card, end=" ")

        print("")
        print("Side Pile:", end=" ")
        for card in self.side_pile:
            print(card, end=" ")
        print("")


    def drawCardsToSide(self):
        if len(self.side_pile) > 0:
            for i in range(len(self.side_pile)):
                self.side_pile[i].flip()
                self.cards.append(self.side_pile[i])
            self.side_pile = []

        if len(self.cards)>0:
            for _ in range(3):
                if len(self.cards) > 0:
                    self.cards[0].flip()
                    self.side_pile.append(self.cards.pop(0))

    def copy(self, deep=True):
        new_deck = Deck([1], ["A"])
        new_deck.cards = self.cards[:]
        new_deck.cache = self.cache[:]
        new_deck.side_pile = self.side_pile[:]
        return new_deck
