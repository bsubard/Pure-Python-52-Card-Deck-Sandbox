import pygame
import random
import sys

# --- Constants ---
# Screen
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
BG_COLOR = (0, 100, 0) # A nice green for the table

# Cards
CARD_WIDTH = 80
CARD_HEIGHT = 120
CARD_CORNER_RADIUS = 5
CARD_OUTLINE_WIDTH = 2

# Colors
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (200, 0, 0)
COLOR_GREY = (150, 150, 150)
COLOR_YELLOW_SELECT = (255, 255, 0) # Highlight for selected card

# Positions
DECK_POS = (30, 30)

# --- Core Classes ---

class Card:
    """ Represents a single playing card with front and back images. """
    def __init__(self, rank, suit_char, suit_color):
        self.rank = rank
        self.suit_char = suit_char
        self.suit_color = suit_color
        
        # is_flipped means 'face up'
        self.is_flipped = False
        self.image = self._create_image()
        self.back_image = self._create_back_image()
        self.rect = self.image.get_rect()

    def _create_image(self):
        """ Creates the front face of the card. """
        image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        image.fill(COLOR_WHITE)
        pygame.draw.rect(image, COLOR_BLACK, image.get_rect(), CARD_OUTLINE_WIDTH, CARD_CORNER_RADIUS)

        font = pygame.font.SysFont('arial', 20)
        rank_text = font.render(self.rank, True, self.suit_color)
        suit_text = font.render(self.suit_char, True, self.suit_color)
        
        image.blit(rank_text, (5, 5))
        image.blit(suit_text, (5, 25))
        
        big_suit_font = pygame.font.SysFont('arial', 40)
        big_suit_text = big_suit_font.render(self.suit_char, True, self.suit_color)
        pos = big_suit_text.get_rect(center=image.get_rect().center)
        image.blit(big_suit_text, pos)
        
        return image

    def _create_back_image(self):
        """ Creates the back of the card. """
        image = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        image.fill((20, 50, 150))
        pygame.draw.rect(image, COLOR_GREY, image.get_rect(), CARD_OUTLINE_WIDTH, CARD_CORNER_RADIUS)
        return image

    def flip(self):
        """ Toggles the card between face up and face down. """
        self.is_flipped = not self.is_flipped

    def draw(self, screen):
        """ Draws the appropriate side of the card to the screen. """
        if self.is_flipped:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.back_image, self.rect)
            
    def draw_highlight(self, screen):
        """ Draws a highlight border around the card. """
        pygame.draw.rect(screen, COLOR_YELLOW_SELECT, self.rect, 4, CARD_CORNER_RADIUS)

class Deck:
    """ Represents a deck of 52 cards, for drawing from. """
    def __init__(self):
        self.cards = self._generate()
        self.shuffle()
        # The visual representation of the deck on screen
        self.deck_rect = pygame.Rect(DECK_POS[0], DECK_POS[1], CARD_WIDTH, CARD_HEIGHT)

    def _generate(self):
        """ Generates a standard 52-card deck. """
        cards = []
        suits = {"♠": COLOR_BLACK, "♣": COLOR_BLACK, "♥": COLOR_RED, "♦": COLOR_RED}
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        for suit_char, color in suits.items():
            for rank in ranks:
                cards.append(Card(rank, suit_char, color))
        return cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        """ Removes and returns the top card from the deck, if any. """
        if self.cards:
            return self.cards.pop()
        return None

    def draw(self, screen):
        """ Draws the deck placeholder on the screen. """
        if self.cards:
            # Draw the back of the top card to represent the deck
            screen.blit(self.cards[0].back_image, self.deck_rect)
        else:
            # Draw an empty outline if the deck is empty
            pygame.draw.rect(screen, COLOR_GREY, self.deck_rect, 2, CARD_CORNER_RADIUS)

class Game:
    """ Main class to manage the game state, input, and rendering. """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Card Sandbox")
        self.clock = pygame.time.Clock()

        self.deck = Deck()
        self.cards_on_table = [] # All cards currently in play
        
        # For dragging cards
        self.held_card = None
        self.drag_offset = (0, 0)

    def run(self):
        """ The main game loop. """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                    
                if event.type == pygame.MOUSEBUTTONUP:
                    self.handle_mouse_up(event)
                            
                if event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

    def handle_mouse_down(self, event):
        pos = event.pos

        # LEFT CLICK (button 1)
        if event.button == 1:
            # Check if clicking on the deck to draw a new card
            if self.deck.deck_rect.collidepoint(pos):
                new_card = self.deck.draw_card()
                if new_card:
                    new_card.rect.center = pos
                    # We want the card to start face-down, so we DO NOT flip it here.
                    self.cards_on_table.append(new_card)
                    self.held_card = new_card
                    # Calculate offset for smooth dragging from click point
                    self.drag_offset = (pos[0] - new_card.rect.x, pos[1] - new_card.rect.y)
                return # Stop processing after drawing a card

            # Check if clicking on an existing card on the table
            # Iterate in reverse to select the top-most card
            for card in reversed(self.cards_on_table):
                if card.rect.collidepoint(pos):
                    self.held_card = card
                    # Move the selected card to the end of the list so it's drawn on top
                    self.cards_on_table.remove(card)
                    self.cards_on_table.append(card)
                    # Calculate offset
                    self.drag_offset = (pos[0] - card.rect.x, pos[1] - card.rect.y)
                    break
        
        # RIGHT CLICK (button 3)
        if event.button == 3:
            # Check for a card to flip
            for card in reversed(self.cards_on_table):
                if card.rect.collidepoint(pos):
                    card.flip()
                    break

    def handle_mouse_up(self, event):
        # On any mouse up, release the card
        if event.button == 1:
            self.held_card = None

    def handle_mouse_motion(self, event):
        # If a card is being held, move it with the mouse
        if self.held_card:
            pos = event.pos
            self.held_card.rect.x = pos[0] - self.drag_offset[0]
            self.held_card.rect.y = pos[1] - self.drag_offset[1]
        
    def draw(self):
        """ Renders everything to the screen. """
        self.screen.fill(BG_COLOR)
        
        # Draw the deck
        self.deck.draw(self.screen)

        # Draw all the cards on the table
        for card in self.cards_on_table:
            card.draw(self.screen)

        # Draw a highlight on the card being held
        if self.held_card:
            self.held_card.draw_highlight(self.screen)


if __name__ == "__main__":
    game = Game()
    game.run()
