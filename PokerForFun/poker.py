from functools import total_ordering, reduce
from collections import Counter
from itertools import combinations
from abc import abstractmethod

import random

@total_ordering
class Card:
    def __init__(self, val_, suits_):
        
        assert(2 <= val_ & val_ <= 14)
        assert(suits_ in ['Spd', 'Hrt', 'Dmd', 'Clb'])
        
        self.val = int(val_)
        self.suits = suits_
        
    def __eq__(self, other):
        return self.val == other.val
    def __lt__(self, other):
        return self.val < other.val
    
    def __repr__(self):
        mapping = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
        return '%s-%s'%(self.suits, self.val if self.val not in mapping.keys() else mapping[self.val])
    
    def __hash__(self):
        return hash((self.val, self.suits))

class Hand:
    
    def __init__(self, cards_=[]):
        assert(len(cards_) == 2)
        self.cards = cards_
        
    def curent_hand(self):
        return Two_Cards(self.cards)
        
    def best_hand_with_deck(self, deck):
        assert(len(deck) in [3, 4, 5])
        all_cards = set(self.cards).union(deck)
        
        return max([Five_Cards(any_five) for any_five in combinations(all_cards, 5)])
    
    def make_combo(self, deck=[]):
        if not deck:
            return self.curent_hand()
        else:
            return self.best_hand_with_deck(deck)
    
    def __repr__(self):
        return str(sorted(self.cards, reverse=True))


class Card_Combo:
    
    level_mapping = {
        9: 'STRF', #'Straight flush'
        8: 'FOUR', #'Four of a kind'
        7: 'FULH', #'Full house'
        6: 'FLSH', #'Flush',
        5: 'STRT', #'Straight',
        4: 'THRE', #'Three of a kind',
        3: 'TWPR', #'Two pair',
        2: 'PAIR', #'Pair',
        1: 'NONE', #'High Card'
    }
    
    def __init__(self, cards_):
        self.cards = cards_
        
    def sorted_nums(self, exclude=[]):
        return sorted([card.val for card in self.cards if card.val not in exclude], reverse=True)
    
    def __eq__(self, other):
        return False if self.level != other.level else self.sorted_nums() == other.sorted_nums()
    
    @abstractmethod
    def __lt__(self, other):
        pass
    
    def __repr__(self):
        return '{%s(%s)}'%(self.level_mapping[self.level], self.level) + str(sorted(self.cards, reverse=True))
    
    def compare(self, other):
        '''1: win, 0: even, -1: lose'''
        print(self.level_mapping[self.level], '-', self.level_mapping[other.level])
        if self > other:
            return 1
        elif self < other:
            return -1
        elif self == other:
            return 0

@total_ordering
class Two_Cards(Card_Combo):
    
    def __init__(self, cards_):
        assert(len(cards_) == 2)
        
        Card_Combo.__init__(self, cards_)
        self.level = 2 if self.cards[0] == self.cards[1] else 1
    
    def __lt__(self, other):
        
        assert(type(self) == type(other))
        
        if self.level < other.level:
            return True   
        elif self.level > other.level:
            return False
        elif self.level == 2:
            return self.cards[0] < other.cards[0]
        else:
            return self.sorted_nums() < other.sorted_nums()

@total_ordering
class Five_Cards(Card_Combo):
    
    def __init__(self, cards_=[]):
        
        assert(len(cards_) == 5)
        Card_Combo.__init__(self, cards_)
        self.counter = Counter([card.val for card in self.cards])
        
        nums = sorted(self.counter.values())
        
        if nums == [1, 4]:
            self.level = 8
        elif nums == [2, 3]:
            self.level = 7
        elif nums == [1, 1, 3]:
            self.level = 4
        elif nums == [1, 2, 2]:
            self.level = 3
        elif nums == [1, 1, 1, 2]:
            self.level = 2
        else:
            FLUSH = self.__check_flush__(self.cards)
            STRAIGHT = self.__check_straight__(self.cards)
            
            if FLUSH & STRAIGHT:
                self.level = 9
            elif FLUSH:
                self.level = 6
            elif STRAIGHT:
                self.level = 5
            else:
                self.level = 1
    
    @staticmethod
    def __check_flush__(cards):
        return len(set([card.suits for card in cards])) == 1
    
    @staticmethod
    def __check_straight__(cards):
        return max(cards).val - min(cards).val == 4 or sorted([card.val for card in cards], reverse=True) == [14, 4, 3, 2, 1]
    
    def __lt__(self, other):
        
        assert(type(self) == type(other))
        
        if self.level < other.level:
            return True
        
        elif self.level > other.level:
            return False
        
        # levels tie
        elif self.level in [8, 4, 2]:
            # four of a kind, three of a kind, one pair
            P_self = self.counter.most_common(1)[0][0]
            P_other = other.counter.most_common(1)[0][0]
            
            if P_self < P_other:
                return True
            elif P_self > P_other:
                return False
            else:
                return self.sorted_nums([P_self]) < other.sorted_nums([P_other])
        
        elif self.level == 7:
            # full house
            P_self = self.counter.most_common(1)[0][0]
            P_other = other.counter.most_common(1)[0][0]
            
            if P_self < P_other:
                return True
            elif P_self > P_other:
                return False
            else:
                return self.counter.most_common(2)[1][0] < other.counter.most_common(2)[1][0]
        
        elif self.level == 3:
            # two pairs
            P_self = sorted([c[0] for c in self.counter.most_common(2)], reverse=True)
            P_other = sorted([c[0] for c in other.counter.most_common(2)], reverse=True)
            
            if P_self < P_other:
                return True
            elif P_self > P_other:
                return False
            else:
                return self.sorted_nums(P_self) < other.sorted_nums(P_other)
            
        elif self.level in [9, 6, 5, 1]:
            # Straight flush, Flush, Straight, High Card
            return self.sorted_nums() < other.sorted_nums()

class Pool:
    def __init__(self, excluded=[]):
        Q = reduce(lambda a, b: a + b, [[Card(i, suit) for i in range(2, 15)] for suit in ['Spd', 'Hrt', 'Dmd', 'Clb']])
        self.queue = list(set(Q) - set(excluded))
        random.shuffle(self.queue)
        
    def draw(self, n=1):
        assert(n < len(self.queue))
        return [self.queue.pop() for i in range(n)]
    
    @property
    def n_remain(self):
        return len(self.queue)