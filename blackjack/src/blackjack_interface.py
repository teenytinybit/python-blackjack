# Module for Blackjack inteface class and methods
import os
from tkinter import *
from PIL import ImageTk, Image
from tkinter import font as tkFont
from blackjack_misc import Actions, ACCEPTED_BETS
from cards import BlackjackCardSet, RANKS, SUITS

COLOR = {
    'play_btn_text' : '#bfffad',       # light green
    'quit_btn_text' : '#ffaaa8',       # light red
    'play_btn' : '#337402',            # dark dreen
    'quit_btn' : '#8d0402',            # dark red 
    'brown': '#664638',                # medium brown
    'dark_brown': '#482f23',           # dark brown
    'white': '#ffffff',                # white
    'stand_btn': '#7a7a7a',
    'stand_btn_text': '#dedede',
    'hit_btn': '#c26b00',              # dark orange
    'hit_btn_text': '#ffca8a',         # orange
    'double_btn': '#088ca1',
    'double_btn_text': '#aaf2fd',
    'split_btn': '#0a8a72',
    'split_btn_text': '#80f9e3',
    'pale_yellow': '#f1e27e',
    'ok_btn': '#7a7a7a',
    'ok_btn_text': '#dedede',
    'gray': '#788275'
}

CARD_HEIGHT = 112
CARD_WIDTH = DECK_HEIGHT = 80
DECK_WIDTH = 126
CHIP_DIAM = (150, 90)
BTN_HEIGHT = 50
BTN_WIDTH = 142
SCORE_DISP_HEIGHT = 40


class TextInterface(object):
    def __init__(self):
        self.name = "Text Interface"
        self.alive = True
        self.MARGIN = 21
        self.BORDER_LENGTH = self.MARGIN + 4
        self.GAME_BORDER = 54

    def _addCardsBorder(self):
        border = "- " * (self.BORDER_LENGTH // 2)
        print(border.center(self.BORDER_LENGTH))

    def _addBorder(self):
        print("=" * self.BORDER_LENGTH)

    def _addGameBorder(self):
        print("=" * self.GAME_BORDER + "\n")

    def clear(self):
        return

    def close(self):
        self.alive = False
        print("Game closed. Thank you for playing!\n")

    def _displayCards(self, cards):
        card_display = ""
        for c in cards:
            if not c.isHidden():
                card_name = (c.getRank() + " of " + c.getSuit()).title()
                card_display += "| " + card_name.center(self.MARGIN) + " |\n"
            else:
                card_display += "| " + "**Card Hidden**".center(self.MARGIN) + " |\n"
        card_display = card_display[:-1]
        print(card_display)
        self._addCardsBorder()

    def _displayScore(self, hand: BlackjackCardSet):
        low_score = hand.getScore()[0]
        high_score = hand.getScore()[1]
        score_display = "Total value: " + str(low_score)
        score_display += " or " + str(high_score) if high_score > 0 else ""
        print("| " + score_display.center(self.MARGIN) + " |")
        self._addBorder()
        print("")

    def getAction(self, actions):
        btn_options = [f"'{a.value}'" for a in actions]
        action_msg = ""
        if Actions.SPLIT in actions:
            btn_options.remove(f"'{Actions.SPLIT.value}'")
            action_msg += "\nType 'split' if you'd like to split cards. "
        if Actions.DOUBLE in actions:
            btn_options.remove(f"'{Actions.DOUBLE.value}'")
            action_msg += "\nType 'double' to double the bet. "
        action_msg += f"\nType {' or '.join(btn_options)} to proceed. "
        # TODO: make stand and hit default options or check for them

        action = input(action_msg)
        while action not in [a.value for a in actions]:
            action = input(action_msg)
        return Actions(action)

    def getBet(self, balance):
        bet = 0
        available = [ab for ab in ACCEPTED_BETS if ab <= balance]
        while bet not in available:
            bet = input("Bets available {" + ", ".join([str(a) for a in available]) + "}\nType in bet amount: ")
            try:
                bet = float(bet)
            except:
                bet = 0
        return bet

    def greet(self):
        print("Welcome to the game of Blackjack!\n")

    def initializeView(self):
        self._addGameBorder()

    def isAlive(self):
        return self.alive

    def setAsideCardSet(self, idx, bust=None):
        return

    def showOutcomeMessage(self, outcome, button_text='back', no_button=False):
        print(outcome)

    def showSettledCardView(self, hand, idx=-1):
        return

    def updateBalanceDisplay(self, balance):
        print('Your balance: ', balance)

    def updateCardView(self, hand: BlackjackCardSet, is_dealer=False):
        whose = "Dealer's" if is_dealer else "Your"
        title = (whose + " cards:").center(self.MARGIN)
        self._addBorder()
        print("| " + title + " |\n| " + " " * self.MARGIN + " |")
        self._displayCards(hand.getCards())
        self._displayScore(hand)

    def wantsToPlay(self):
        btn = ""
        while btn not in ['start', 'exit']:
            btn = input("Please type 'start' to begin or 'exit' to leave: ")
        return btn == 'start'


class GraphicInterface(object):
    def __init__(self):
        self.name = "Graphic Interface"
        self.alive = True
        self.HEIGHT = 12 * 60   # 720
        self.WIDTH = 18 * 60    # 1080
        self.fontname = ['Matura MT Script Capitals', 'Footlight MT Light', 'Footlight MT Std']
        self.assets = self._loadAssets()
        self.cardview = {'player': [], 'dealer': []}
        self.set_aside = {}
        self.split_card_holder = None
        self.win = self._initWin()

        game_win = self. _getGameCanvas()
        play_btn =  game_win.children['play']        
        play_btn.update()
        btn_y = play_btn.winfo_y()
        padd_x = 50
        padd_y = 60
        self.area_coords = {
            'player': (
                padd_x * 4,                     # x0
                btn_y - padd_y - CARD_HEIGHT,   # y0
                self.WIDTH - padd_x * 4,        # x1
                btn_y - padd_y),                # y1
            'dealer': (
                padd_x * 4, 
                padd_y, 
                self.WIDTH - padd_x * 4, 
                padd_y + CARD_HEIGHT),
            'buttons': (
                padd_x * 3, 
                btn_y, 
                self.WIDTH - padd_x * 3, 
                btn_y + BTN_HEIGHT)
        }
        self.area_coords['deck'] = (
                self.area_coords['dealer'][2] - padd_x,
                self.area_coords['dealer'][3] + padd_y, 
                self.area_coords['dealer'][2] + DECK_WIDTH - padd_x, 
                self.area_coords['dealer'][3] + DECK_HEIGHT + padd_y)

        half_area = 250
        self.area_coords['outcome'] = (
                (self.area_coords['dealer'][0] + self.area_coords['dealer'][2]) // 2 - half_area,
                self.area_coords['dealer'][3] + padd_y, 
                (self.area_coords['dealer'][0] + self.area_coords['dealer'][2]) // 2 + half_area,
                self.area_coords['dealer'][3] + DECK_HEIGHT + padd_y)

        self.area_coords['split'] = (
            padd_x // 2, 
            self.area_coords['dealer'][3] + padd_y * 2, 
            padd_x // 2 + CARD_WIDTH + CARD_WIDTH // 5, 
            self.area_coords['dealer'][3] + padd_y * 2 + CARD_HEIGHT)

        self.area_coords['bet'] = (
            padd_x,
            self.area_coords['dealer'][3],  
            padd_x + CHIP_DIAM[1], 
            self.area_coords['dealer'][3] + CHIP_DIAM[1])
   
    def _loadAssets(self):
        assets = {
            # 'bg' : 'game_bg_grid.png',
            'bg' : 'game_bg.png',
            'round_bg': 'round_bg.png',
            'bal' : 'balance.png',
            'play' : 'play_btn.png',
            'quit' : 'exit_btn.png',
            'msg_brd': 'msg_board.png',
            'bet10': 'bet10.png',
            'bet25': 'bet25.png',
            'bet50': 'bet50.png',
            'bet100': 'bet100.png',
            'bet10_sm': 'bet10_small.png',
            'bet25_sm': 'bet25_small.png',
            'bet50_sm': 'bet50_small.png',
            'bet100_sm': 'bet100_small.png',
            'hit': 'hit_btn.png',
            'split': 'split_btn.png',
            'stand': 'stand_btn.png',
            'double': 'double_btn.png',
            'deck': 'deck.png',
            'hidden': 'hidden_card.png',
            'score': 'score.png',
            'ok': 'ok_btn.png'
        }

        fldr = os.path.join(os.getcwd(), 'blackjack', 'assets')
        for k, v in assets.items():
            assets[k] = os.path.join(fldr, v)

        card_assets = {}
        for rank in RANKS:
            for suit in SUITS:
                card_nm = rank[0] + '_' + suit
                card_fl = card_nm + '.png'
                card_assets[card_nm] = os.path.join(fldr, 'cards', card_fl)
        assets.update(card_assets)

        # validate paths exist
        for k in assets.keys():
            if not os.path.exists(assets[k]):
                raise FileNotFoundError("Could not find an asset", assets[k])
        return assets

    def _initWin(self):
        root = Tk()
        # set window size
        root.maxsize(self.WIDTH, self.HEIGHT) # width x height
        root.minsize(self.WIDTH, self.HEIGHT)
        root.title("Blackjack Game")
        root.iconbitmap(os.path.join(os.getcwd(), 'blackjack', 'assets', 'playing-card.ico'))

        def close_window():
            self.alive = False
            game_win = self.win.children['!canvas']
            bet_opts = game_win.find_withtag('bet_option')
            table_el = game_win.find_withtag('play_table')
            if len(bet_opts) > 0:
                x, y = game_win.coords(bet_opts[0])
                game_win.event_generate("<Button-1>", x=x, y=y)
            if len(table_el) > 0:
                btn_seq = ['ok', 'stand'] * 4
                # btn_seq = btn_seq + ['ok'] * 5
                for name in btn_seq:
                    if name in game_win.children.keys():
                        bt = game_win.children[name]
                        bt.update()
                        x, y = bt.winfo_x(), bt.winfo_y()
                        bt.event_generate("<Button-1>", x=x, y=y)
            exit_btn = game_win.children['quit']
            exit_btn.update()
            x, y = exit_btn.winfo_x(), exit_btn.winfo_y()
            exit_btn.event_generate("<Button-1>", x=x, y=y)

        root.protocol("WM_DELETE_WINDOW", close_window)

        font = tkFont.Font(family=self.fontname[0], size=14)
        half_h, half_w = self.HEIGHT // 2, self.WIDTH // 2

        # create game area with background
        game_win = Canvas(root, width=self.WIDTH, height=self.HEIGHT, highlightthickness=0)
        game_win.place(x=0, y=0)
        bg_img = PhotoImage(name='main_bg', file=self.assets['bg'])
        game_win.create_image(half_w, half_h, image=bg_img)
        game_win.images = {'main_bg': bg_img}

        # add balance display to game area
        balance_img = PhotoImage(name='balance', file=self.assets['bal'])
        img_w, img_h = balance_img.width(), balance_img.height()
        game_win.create_image(half_w, self.HEIGHT - img_h + 20, image=balance_img, tags=('balance'))
        game_win.images['balance'] = balance_img

        def on_enter(e):
            btn = e.widget
            btn['foreground'] = COLOR[btn.winfo_name() + '_btn_text']

        def on_leave(e):
            btn = e.widget
            btn['foreground'] = 'black'

        # add play and quit buttons
        main_btns = {}
        for bt_name in ['play', 'quit']:
            bt_img = PhotoImage(name=bt_name + '_button', file=self.assets[bt_name])
            btn_config = {
                'compound': CENTER, 'font': font, 'activeforeground': COLOR['white'],
                'text': bt_name.capitalize(), 'name': bt_name
            }
            btn_config['background'] = btn_config['activebackground'] = COLOR[bt_name + '_btn']
            main_btns[bt_name] = self._createButton(game_win, btn_config, bt_img)
            main_btns[bt_name].bind("<Enter>", on_enter)
            main_btns[bt_name].bind("<Leave>", on_leave)

        main_btns['play'].place(x=half_w + BTN_WIDTH // 2, y=self.HEIGHT - (img_h * 2 + 30))
        main_btns['quit'].place(x=half_w - BTN_WIDTH * 1.5, y=self.HEIGHT - (img_h * 2 + 30))      

        game_win.place()
        return root

    def _displayMainScreenMgs(self, text):
        half_h, half_w = self.HEIGHT // 2, self.WIDTH // 2
        font = tkFont.Font(family=self.fontname[1], size=20)
        game_win = self._getGameCanvas()

        # add frame image for to form message board
        if 'message_frame' in game_win.images.keys():
            msg_frame_img = game_win.images['message_frame']
        else:
            msg_frame_img = PhotoImage(name='message_frame', file=self.assets['msg_brd'])
            game_win.images['message_frame'] = msg_frame_img
        frame_brdr, frame_top = 17, 32
        msg_frame_id = game_win.create_image(half_w, half_h - 100, image=msg_frame_img, tags=('main_screen'))
        frame_x, frame_y = game_win.coords(msg_frame_id)

        # add greeting message with background
        x0 = frame_x - msg_frame_img.width() // 2 + frame_brdr
        y0 = frame_y - msg_frame_img.height() // 2 + frame_top + frame_brdr
        x1 = x0 + msg_frame_img.width() - frame_brdr * 2,
        y1 = y0 + msg_frame_img.height() - frame_brdr * 2 - frame_top
        greeting_box = game_win.create_rectangle((x0, y0, x1, y1), fill=COLOR['brown'], tags=('main_screen'))
        game_win.tag_lower(greeting_box, msg_frame_id)
        text_config = {
            'text': text, 
            'font': font, 
            'fill': 'white'
        }
        game_win.create_text((frame_x, frame_y + frame_brdr), **text_config, tags=('main_msg', 'main_screen'))

    def greet(self):
        greeting = "Welcome to the game of Blackjack!"
        self._displayMainScreenMgs(greeting)
         
    def wantsToPlay(self):
        game_win = self._getGameCanvas()
        half_w = self.WIDTH // 2

        message = "Select 'Play' to start another round."
        if not game_win.find_withtag('main_msg'):
            self._displayMainScreenMgs(message)

        # restore play and quit buttons
        play_btn = game_win.children['play']
        quit_btn = game_win.children['quit']
        play_btn.place(x=half_w + BTN_WIDTH // 2, y=self.area_coords['buttons'][1])
        quit_btn.place(x=half_w - BTN_WIDTH * 1.5, y=self.area_coords['buttons'][1])

        play_var = BooleanVar()
        def on_click(e):
            btn = e.widget
            play_var.set(btn['text'] == "Play")

        play_btn.bind("<Button-1>", on_click)
        quit_btn.bind("<Button-1>", on_click)
        game_win.wait_variable(play_var)
        if not play_var.get():
            self.win.destroy()
        return play_var.get()  

    def isAlive(self):
        return self.alive

    def _getGameCanvas(self):
        return self.win.children['!canvas']

    def updateBalanceDisplay(self, balance):
        if not self.isAlive():
            return
        game_win = self._getGameCanvas()
        bal_x, bal_y = game_win.coords(game_win.find_withtag('balance')[0])
        disp_bottom_shape = 8

        # check if previous balance amount displayed
        bal_text = game_win.find_withtag('money')
        if bal_text:
            game_win.itemconfig(bal_text, text=str(balance))
        else:
            # add balance amount on top into the balance window
            text_config = {
                'text': str(balance), 
                'font': tkFont.Font(family=self.fontname[2], size=20), 
                'fill': COLOR['dark_brown']
            }
            game_win.create_text((bal_x, bal_y - disp_bottom_shape), **text_config, tags=('money'))

    def _createBets(self, available):
        game_win = self._getGameCanvas()
        half_h, half_w = self.HEIGHT // 2, self.WIDTH // 2

        if len(available) > 1:
            space_x = half_w // 4 * len(available)
            move_x = space_x // (len(available) - 1)
        else:
            space_x = 0
            move_x = 0    
        start_x = half_w - space_x // 2
        move_y = 50
        
        bet_coord = {}
        for i in range(len(available)):
            av = available[i]
            bet_coord[str(av)] = (start_x + move_x * i, half_h - move_y * i)
        
        bet_imgs= {}
        for a_bet in available:
            s_bet = str(a_bet)
            if s_bet in game_win.images.keys():
                bet_img = game_win.images[s_bet]
            else:
                bet_img = PhotoImage(name=s_bet, file=self.assets['bet' + s_bet])
            game_win.create_image(bet_coord[s_bet], image=bet_img, tags=('bet_option', 'bet_screen'))
            bet_imgs[s_bet] = bet_img
        game_win.images.update(bet_imgs)
        return bet_imgs
   
    def getBet(self, balance):
        self._clearScreen('main_screen')
        available = [ab for ab in ACCEPTED_BETS if ab <= balance] 
        game_win = self._getGameCanvas()
        half_h, half_w = self.HEIGHT // 2, self.WIDTH // 2
        bet_imgs = self._createBets(available)

        # text field stating "select bet amount"
        text_config = {
            'text': "Select bet amount", 
            'font': tkFont.Font(family=self.fontname[1], size=20), 
            'fill': 'white'
        }
        game_win.create_text((half_w, half_h + 100), **text_config, tags=('bet_screen'))

        bet = IntVar()
        def on_click(e):
            bet_img_id = e.widget.find_closest(e.x, e.y)[0]
            bet_name = e.widget.itemcget(bet_img_id, 'image')
            e.widget.images['current_bet'] = PhotoImage(file=self.assets['bet' + bet_name + '_sm'])
            bet.set(int(bet_name))

        game_win.tag_bind('bet_option', "<Button-1>", on_click)
        game_win.wait_variable(bet)
        game_win.tag_unbind('bet_option', "<Button-1>")
        game_win.delete('bet_screen')
        # for b in bet_imgs.keys(): 
        #     del game_win.images[b]
        return bet.get()
 
    def _setupPlayingArea(self):
        game_win = self._getGameCanvas()
        # selected bet goes to the leftmost side
        current_bet_img = game_win.images['current_bet']
        x = (self.area_coords['bet'][0] + self.area_coords['bet'][2]) // 2
        y = (self.area_coords['bet'][1] + self.area_coords['bet'][3]) // 2
        game_win.create_image(x, y, image=current_bet_img, tags=('play_table'))

        # deck display
        deck_img = PhotoImage(file=self.assets['deck'])
        x = (self.area_coords['deck'][0] + self.area_coords['deck'][2]) // 2
        y = (self.area_coords['deck'][1] + self.area_coords['deck'][3]) // 2
        game_win.create_image(x, y, image=deck_img, tags=('play_table'))
        game_win.images['deck'] = deck_img

        # outcome message display
        x1, y1, x2, y2 = self.area_coords['outcome']
        alpha = int(0.5 * 255)
        fill = COLOR['brown']
        fill = (int(fill[1:3],16),int(fill[3:5],16),int(fill[5:7],16)) + (alpha,)
        image = Image.new('RGBA', (x2-x1, y2-y1), fill)
        game_win.images['outcome_area'] = ImageTk.PhotoImage(image)
        game_win.create_image(x1, y1, image=game_win.images['outcome_area'], anchor='nw', tags=('play_table'))

        # card ownership labels
        text_config = {
                'font': tkFont.Font(family=self.fontname[2], size=20), 
                'fill': COLOR['white']
            }
        for owner in ['player', 'dealer']:
            text_config['text'] = f"Dealer's cards: " if owner == 'dealer' else f"Your cards: "
            text_config['tags'] = (owner + '_ownership', 'play_table')
            x = (self.area_coords[owner][0] + self.area_coords[owner][2]) // 2
            y = self.area_coords[owner][3] - (self.area_coords[owner][3] - self.area_coords[owner][1]) - 22
            game_win.create_text((x, y), **text_config)

    def initializeView(self):
        self._setupPlayingArea()

    def updateCardView(self, hand: BlackjackCardSet, is_dealer=False):
        if not self.isAlive():
            return
        owner = 'dealer' if is_dealer else 'player'
        game_win = self._getGameCanvas()
        game_win.delete(owner + '_cardview')

        single_shift = CARD_WIDTH * 0.9
        coords = self.area_coords[owner]
        cards = hand.getCards()
        card_num = len(cards)

        total_len = (card_num * single_shift) + CARD_WIDTH * 0.1
        center_x = (coords[0] + coords[2]) // 2
        side_shift = (total_len - CARD_WIDTH) // 2
        start_x = center_x - side_shift
        start_y = (coords[1] + coords[3]) // 2

        for i in range(card_num):
            suit, rank = cards[i].getSuit(), cards[i].getRank()
            fl_name = rank + '_' + suit
            if cards[i].isHidden():
                fl_name = 'hidden'
            if i <= len(self.cardview[owner]) - 1:
                card_img = self.cardview[owner][i]
                if card_img.cget('file') != self.assets[fl_name]:
                    card_img.configure(file=self.assets[fl_name])
                    self.cardview[owner][i] = card_img
            else:
                card_img = PhotoImage(file=self.assets[fl_name])
                self.cardview[owner].append(card_img)
            game_win.create_image(start_x + single_shift * i, start_y, 
                                    image=card_img, tags=(owner + '_cardview', 'play_table'))
        score = str(hand.getScore()[0])
        offset = 120 if owner == 'player' else 130
        if hand.getScore()[1] > 0:
            score += f" ({str(hand.getScore()[1])})"
            offset = 150 if owner == 'player' else 160
        score_text_id = game_win.find_withtag(owner + '_score')
        sc_x, sc_y = game_win.coords(game_win.find_withtag(owner + '_ownership')[0])
        if score_text_id:
            game_win.itemconfig(score_text_id, text=score)
            game_win.coords(score_text_id[0], (sc_x + offset, sc_y))
        else:
            text_config = {
                'text': score, 
                'font': tkFont.Font(family=self.fontname[2], size=20), 
                'fill': COLOR['white']
            }
            game_win.create_text((sc_x + offset, sc_y), **text_config, 
                                            tags=(owner + '_score', 'play_table'))
 
    def _createButton(self, win, config, image=None):
        config['image'] = image
        new_btn = Button(win, **config)
        new_btn.image = image
        return new_btn

    def getAction(self, actions):
        game_win = self._getGameCanvas()
        btn_options = [a.value for a in actions]

        action = StringVar()
        def on_click(e):
            btn = e.widget
            action.set(btn.winfo_name())

        def on_enter(e):
            btn = e.widget
            btn['foreground'] = COLOR[btn.winfo_name() + '_btn_text']

        def on_leave(e):
            btn = e.widget
            btn['foreground'] = 'black'

        font = tkFont.Font(family=self.fontname[0], size=14)
        game_btns = {}
        space = 50
        total_w = (BTN_WIDTH + space) * len(btn_options) - space
        offset = (self.WIDTH - total_w) // 2
        for bt_name in btn_options:
            if bt_name in game_win.children.keys():
                game_btns[bt_name] = game_win.children[bt_name]
            else:
                bt_img = PhotoImage(name=bt_name + '_button', file=self.assets[bt_name])
                btn_config = {
                    'compound': CENTER, 'font': font, 'activeforeground': COLOR['white'],
                    'text': bt_name.capitalize(), 'name': bt_name
                }
                btn_config['background'] = btn_config['activebackground'] = COLOR[bt_name + '_btn']
                game_btns[bt_name] = self._createButton(game_win, btn_config, bt_img)
                game_btns[bt_name].bind("<Enter>", on_enter)
                game_btns[bt_name].bind("<Leave>", on_leave)
            game_btns[bt_name].bind("<Button-1>", on_click)
            game_btns[bt_name].place(x=offset, y=self.area_coords['buttons'][1])
            offset += space + BTN_WIDTH
        
        if not self.isAlive():
            return Actions.STAND

        game_win.wait_variable(action)
        for bt_name in btn_options: game_win.children[bt_name].place_forget()
        if Actions(action.get()) == Actions.DOUBLE:
            current_bet_img = game_win.images['current_bet']
            x = (self.area_coords['bet'][0] + self.area_coords['bet'][2]) // 2
            y = (self.area_coords['bet'][1] + self.area_coords['bet'][3]) // 2
            game_win.create_image(x + 35, y + 25, image=current_bet_img, tags=('play_table'))
        return Actions(action.get())

    def setAsideCardSet(self, prev_idx):
        game_win = self._getGameCanvas()
        game_win.delete('player_cardview')
        # transfer cards in current card view to historical storage
        self.set_aside[str(prev_idx)] = self.cardview['player']
        self.cardview['player'] = []
        # graphics for setting aside
        sets_held = len(self.set_aside)
        prev_cardset = self.set_aside[str(prev_idx)]
        coords = self.area_coords['split']
        num_based_shift = 24 // len(prev_cardset)
        shift_x = CARD_WIDTH // 10 + num_based_shift
        shift_y = CARD_HEIGHT + 25
        start_x = (coords[0] + coords[2]) // 2
        start_y = coords[1] + 60 + shift_y * (sets_held - 1)
        
        single_card_angle = 5
        start_angle = single_card_angle * len(prev_cardset)
        rotate = (start_angle * 2) // (len(prev_cardset) - 1)
        # collect all cards into another obj and squash them together
        for i in range(len(prev_cardset)):
            img_rot = ImageTk.getimage(prev_cardset[i])
            img_rot = img_rot.rotate(start_angle - rotate * i, expand=True)
            img_rot = ImageTk.PhotoImage(img_rot)
            prev_cardset[i] = img_rot
            game_win.create_image(start_x + shift_x * i, start_y + 2 * i, 
                                    image=img_rot, tags=('set_aside', 'play_table'))

    def moveSplitCard(self, action='hold'):
        game_win = self._getGameCanvas()
        if action == 'release':
            self._waitOKButton('play next')
            del game_win.images['split_card_area']
            game_win.delete('split_card')
            self.split_card_holder = None
        else:
            self.split_card_holder = self.cardview['player'].pop()
            x, y = self.area_coords['player'][2] + 20, self.area_coords['player'][3] + 25
            game_win.create_image(x, y, image=self.split_card_holder, tags=('split_card', 'play_table'))
            # fade card image
            alpha = int(0.6 * 255)
            fill = COLOR['gray']
            fill = (int(fill[1:3],16),int(fill[3:5],16),int(fill[5:7],16)) + (alpha,)
            image = Image.new('RGBA', (CARD_WIDTH, CARD_HEIGHT), fill)
            game_win.images['split_card_area'] = ImageTk.PhotoImage(image)
            game_win.create_image(x, y, image=game_win.images['split_card_area'], tags=('split_card', 'play_table'))

    def showSettledCardView(self, hand, idx):
        self.updateCardView(hand)
        # free completed cards holder
        if str(idx) in self.set_aside.keys():
            del self.set_aside[str(idx)]

    def showOutcomeMessage(self, outcome, button_text='back', no_button=False):
        game_win = self._getGameCanvas()
        bust_msg = outcome[:4].lower() == 'bust'
        text_exists = game_win.find_withtag('outcome')
        if text_exists and not bust_msg:
            old_text = game_win.itemcget(text_exists[0], 'text')
            outcome = old_text.replace('\n', ' ') + outcome
            game_win.itemconfig(text_exists[0], text=outcome)
        else:
            text_config = {
                'font': tkFont.Font(family=self.fontname[1], size=20), 
                'fill': COLOR['pale_yellow'],
                'text': outcome,
                'tags': ('outcome', 'play_table')
            }
            x = (self.area_coords['outcome'][0] + self.area_coords['outcome'][2]) // 2
            y = (self.area_coords['outcome'][1] + self.area_coords['outcome'][3]) // 2 + 20
            game_win.create_text((x, y), **text_config)

        if not no_button:
            self._waitOKButton(button_text)

    def _waitOKButton(self, bt_text):
        game_win = self._getGameCanvas()
        ok = BooleanVar()
        def on_click(e):
            game_win.delete('outcome')
            ok.set(True)
        
        def on_enter(e):
            btn = e.widget
            btn['foreground'] = COLOR[btn.winfo_name() + '_btn_text']

        def on_leave(e):
            btn = e.widget
            btn['foreground'] = 'black'

        font = tkFont.Font(family=self.fontname[0], size=14)
        bt_name = 'ok'
        if bt_name in game_win.children.keys():
            ok_btn = game_win.children[bt_name]
            ok_btn['text'] = bt_text.capitalize()
        else:
            ok_btn_img = PhotoImage(name=bt_name + '_button', file=self.assets[bt_name])
            btn_config = {
                    'compound': CENTER, 'font': font, 'activeforeground': COLOR['white'],
                    'text': bt_text.capitalize(), 'name': bt_name
            }
            btn_config['background'] = btn_config['activebackground'] = COLOR[bt_name + '_btn']
            ok_btn = self._createButton(game_win, btn_config, ok_btn_img)
            ok_btn.bind("<Enter>", on_enter)
            ok_btn.bind("<Leave>", on_leave)
        ok_btn.bind("<Button-1>", on_click)
        ok_btn.place(x=(self.WIDTH - BTN_WIDTH) // 2, y=self.area_coords['buttons'][1] - BTN_HEIGHT)
        if self.isAlive():
            game_win.wait_variable(ok)
        ok_btn.place_forget()

    def _clearScreen(self, group):
        game_win = self._getGameCanvas()
        if group == 'main_screen':
            for btn in ['play','quit']:
                game_win.children[btn].place_forget()
        elif group == 'play_table':
            for btn in ['hit', 'split', 'stand', 'double']:
                if btn in game_win.children.keys():
                    game_win.children[btn].place_forget()
            self.cardview = {'player': [], 'dealer': []}
            self.set_aside = {}
        game_win.delete(group)

    def clear(self):
        self._clearScreen('play_table')

    def close(self):
        game_win = self._getGameCanvas()

        text_config = {
            'text': "Insufficient balance", 
            'font': tkFont.Font(family=self.fontname[1], size=20), 
            'fill': 'white'
        }
        game_win.create_text((self.WIDTH // 2, self.HEIGHT // 2), **text_config)

        quit_btn = game_win.children['quit']
        quit_btn.place(x=(self.WIDTH - BTN_WIDTH) // 2, y=self.area_coords['buttons'][1])

        exit_var = BooleanVar()
        def on_click(e):
            exit_var.set(True)
        quit_btn.bind("<Button-1>", on_click)
        game_win.wait_variable(exit_var)
        self.win.destroy()
        return exit_var.get()
