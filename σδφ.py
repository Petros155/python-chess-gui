import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox  # για μηνύματα τέλους παιχνιδιού
from PIL import Image, ImageTk  # το pillow για τα png


class ChessCanvas:
    """Η μία και μοναδική κλάση"""

    def __init__(self, root):
        """###################################### η constructor! ######################################"""
        self.root = root  # το παράθυρο
        self.root.title("Our_Chess")  # το όνομα του παραθύρου μας!
        self.square_size = 80  # το μέγεθος για κάθε τετραγωνάκι στη σκακιέρα
        self.canvas = tk.Canvas(root,  # ο καμβάς θα έχει 8χ8 τέτοια τετραγωνάκια
                                width=8 * self.square_size,
                                height=8 * self.square_size)
        self.canvas.pack(side="left")  # τοποθετούμε τη σκακιέρα αριστερά
        self.board = [  # λίστα με το τι υπάρχει στο ταμπλό
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['  ', '  ', '  ', '  ', '  ', '  ', '  ', '  '],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.images = {}  # οι εικόνες σε ένα λεξικό (πχ κλειδί το wR και τιμή η εικόνα του λευκού πύργου!)
        self.valid_moves = []  # λίστα με κινήσεις που είναι εφικτές

        self.selected_square = None  # κλικαρισμένο τετράγωνο
        self.hovered_square = None  # τετράγωνο στο οποίο αιωρείται ο κέρσορας

        self.move_history = []  # λίστα ιστορικού κινήσεων

        # πλαίσιο για ιστορικό κινήσεων
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(side="right", padx=10)

        self.history_label = tk.Label(self.text_frame, text="Ιστορικό Κινήσεων", font=("Arial", 12, "bold"))
        self.history_label.pack()

        self.history_box = tk.Text(self.text_frame, width=40, height=30, state="disabled", bg="#f5f5f5",
                                   font=("Courier", 10))
        self.history_box.pack()

        # κουμπί αποθήκευσης
        save_button = tk.Button(self.text_frame, text="Αποθήκευση Παρτίδας", command=self.save_history)
        save_button.pack(pady=10)

        # εδώ αναφέρουμε τις μεθόδους!
        self.load_images()  # για τη μέθοδο για τις εικόνες
        self.draw_board()  # για να ζωγραφίσει το ταμπλό
        self.canvas.bind("<Button-1>", self.on_click)  # όταν γίνεται αριστερό κλικ
        self.canvas.bind("<Motion>", self.on_hover)  # και όταν απλά αιωρείται ο κέρσορας από πάνω

        self.current_player = 'w'  # αρχίζουν να παίζουν τα

        # φτιάχνουμε flag για τέλος παιχνιδιού
        self.has_move = False
        self.game_over = False  # νέο flag

        # φτιάχνουμε flags για την επίτευξη του ροκέ (αν έχουν κουνηθεί ο βασιλιάς και ο πύργος σε κάθε περίπτωση)
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_kingside_moved = False
        self.white_rook_queenside_moved = False
        self.black_rook_kingside_moved = False
        self.black_rook_queenside_moved = False

        # ζητάμε τα δύο ονόματα και τα λέμε first_guy, second_guy
        self.first_guy, self.second_guy = self.ask_for_player_names()

    def load_images(self):
        """############################## από εδώ και πέρα οι μέθοδοι μας ##############################
        Πρώτα φορτώνουμε τις εικόνες…"""

        pieces = ['bP', 'bR', 'bN', 'bB', 'bQ', 'bK',
                  'wP', 'wR', 'wN', 'wB', 'wQ', 'wK']
        for piece in pieces:
            img = Image.open(f"chess_pieces/{piece}.png")  # ανοίγουμε τα png από το chess_pieces
            img = img.resize((self.square_size, self.square_size),  # μέγεθος όσο τα τετράγωνα (σαν να λέγαμε 80χ80)
                             Image.Resampling.LANCZOS)
            self.images[piece] = ImageTk.PhotoImage(
                img)  # γεμίζουμε το images με κάθε img (τα img είναι το κάθε κομμάτι)

    def draw_board(self):
        """Ζωγραφίζουμε το ταμπλό"""

        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size  #
                y1 = row * self.square_size  # το σημείο που αρχίζει το κάθε τετράγωνο

                x2 = x1 + self.square_size  #
                y2 = y1 + self.square_size  # το σημείο που τελειώνει

                if self.valid_moves and (row, col) in self.valid_moves:
                    # να φαίνονται με σκούρο και με ανοιχτό πράσινο οι εφικτές κινήσεις
                    if (row + col) % 2 == 0:
                        color = "#aaffaa"
                    else:
                        color = "#66aa66"
                elif self.hovered_square == (row, col):
                    color = "#a9a9a9"  # το γκρι χρωματάκι του hover
                else:
                    if (row + col) % 2 == 0:  # το άθροισμα γραμμής στήλης κάθε μαύρου τετραγώνου είναι ζυγό!
                        color = "#f0d9b5"  # σκούρο…
                    else:
                        color = "#b58863"  # ανοιχτό…

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')  # φτιάχνει όλο το ταμπλό

                piece = self.board[row][col]  # η λίστα στη constructor με τα κομμάτια
                if piece.strip() and piece in self.images:
                    self.canvas.create_image(x1, y1, anchor="nw", image=self.images[piece])

    def on_click(self, event):
        """Όταν κλικάρουμε"""

        if self.game_over:
            return  # δεν επιτρέπονται κινήσεις μετά το τέλος
        col = event.x // self.square_size
        row = event.y // self.square_size

        if not (0 <= row < 8 and 0 <= col < 8):
            return
        clicked = (row, col)

        if self.selected_square:  # αν έχουμε κάνει κλικ σε κάποιο τετράγωνο…
            if clicked in self.valid_moves:  # και το επόμενο κλικ σε τετράγωνο είναι σε επιτρεπτή θέση
                self.move_piece(self.selected_square, clicked)  # μετακινούμε το κομμάτι από το 1ο τετράγωνο στο 2ο

            # τελειώσαμε με την κίνηση άρα τώρα το ιστορικό καθαρίζεται
            self.selected_square = None
            self.valid_moves = []
            self.draw_board()
        else:
            piece = self.board[row][col]
            if piece.strip() and piece[0] == self.current_player:  # ΘΕΤΟΥΜΕ ΧΡΩΜΑ
                self.selected_square = clicked  # επιλεγμένο τετράγωνο
                # αρχικές κινήσεις
                piece_type = piece[1]
                if piece_type == 'P':
                    moves = self.get_pawn_moves(row, col)
                elif piece_type == 'R':
                    moves = self.get_rook_moves(row, col)
                elif piece_type == 'N':
                    moves = self.get_knight_moves(row, col)
                elif piece_type == 'B':
                    moves = self.get_bishop_moves(row, col)
                elif piece_type == 'Q':
                    moves = self.get_queen_moves(row, col)
                elif piece_type == 'K':
                    moves = self.get_king_moves(row, col)
                # φιλτράρουμε τις κινήσεις που αφήνουν σε έλεγχο
                self.valid_moves = self.filter_legal_moves((row, col), moves)
                self.draw_board()

    def on_hover(self, event):
        """Όταν αιωρείται ο κέρσορας πάνω από κάποιο κουτάκι"""

        col = event.x // self.square_size
        row = event.y // self.square_size

        if (row, col) != self.hovered_square:
            self.hovered_square = (row, col)
            self.draw_board()

    def filter_legal_moves(self, from_sq, moves):
        """Φιλτράρουμε τις κινήσεις έτσι ώστε να μην αγνοείται το ρουά"""

        legal = []
        fr, fc = from_sq
        orig_piece = self.board[fr][fc]
        for to_square in moves:
            tr, tc = to_square
            captured = self.board[tr][tc]
            # προσωρινή μετακίνηση
            self.board[tr][tc] = orig_piece
            self.board[fr][fc] = '  '
            in_check = self.is_in_check(self.current_player)
            # επαναφορά
            self.board[fr][fc] = orig_piece
            self.board[tr][tc] = captured
            if not in_check:
                legal.append(to_square)
        return legal


    def is_in_check(self, color):
        """Αν ο βασιλιάς βρίσκεται υπό ρουά"""
        # εντοπίζει τον βασιλιά
        king_pos = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == color + 'K':
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        # ελέγχει όλες τις κινήσεις αντιπάλου
        opp = 'b' if color == 'w' else 'w'
        for r in range(8):
            for c in range(8):
                if self.board[r][c].startswith(opp):
                    pt = self.board[r][c][1]
                    if pt == 'P':
                        moves = self.get_pawn_moves(r, c)
                    elif pt == 'R':
                        moves = self.get_rook_moves(r, c)
                    elif pt == 'N':
                        moves = self.get_knight_moves(r, c)
                    elif pt == 'B':
                        moves = self.get_bishop_moves(r, c)
                    elif pt == 'Q':
                        moves = self.get_queen_moves(r, c)
                    elif pt == 'K':
                        moves = self.get_king_moves(r, c)
                    else:
                        moves = []
                    if king_pos in moves:
                        return True
        return False


    def check_end_of_game(self):
        """Έλεγχος για το τέλος του παιχνιδιού"""

        next_color = self.current_player
        # όλες οι κινήσεις του επόμενου παίκτη
        self.has_move = False
        for r in range(8):
            for c in range(8):
                if self.board[r][c].startswith(next_color):
                    pt = self.board[r][c][1]
                    if pt == 'P':
                        moves = self.get_pawn_moves(r, c)
                    elif pt == 'R':
                        moves = self.get_rook_moves(r, c)
                    elif pt == 'N':
                        moves = self.get_knight_moves(r, c)
                    elif pt == 'B':
                        moves = self.get_bishop_moves(r, c)
                    elif pt == 'Q':
                        moves = self.get_queen_moves(r, c)
                    elif pt == 'K':
                        moves = self.get_king_moves(r, c)
                    else:
                        moves = []
                    legal = self.filter_legal_moves((r, c), moves)
                    if legal:
                        self.has_move = True
                        break
            if self.has_move:
                break
        if not self.has_move:
            if self.is_in_check(next_color):
                # checkmate
                if next_color == 'b':
                    winner = self.first_guy
                elif next_color == 'w':
                    winner = self.second_guy

                messagebox.showinfo("Τέλος Παιχνιδιού", f"Νικητής: {winner}")
            else:
                # stalemate
                messagebox.showinfo("Τέλος Παιχνιδιού", "Ισοπαλία.")
            self.game_over = True

    def get_pawn_moves(self, row, col):
        """Οι κινήσεις του πιονιού (στρατιώτη)"""

        moves = []
        piece = self.board[row][col]

        if piece[0] == 'w':  # κατεύθυνση
            direction = -1  # για τα άσπρα
            starting_row = 6  # άσπρα…
        else:
            direction = 1  # και τα μαύρα
            starting_row = 1  # μαύρα

        # μία θέση μπροστά
        if 0 <= row + direction < 8 and self.board[row + direction][col] == '  ':
            moves.append((row + direction, col))
            # δύο θέσεις μπροστά από αρχική θέση
            if row == starting_row and self.board[row + 2 * direction][col] == '  ':
                moves.append((row + 2 * direction, col))

        # φάγωμα αριστερά
        if col > 0 and 0 <= row + direction < 8 and self.board[row + direction][col - 1].strip() and \
                self.board[row + direction][col - 1][0] != piece[0]:
            moves.append((row + direction, col - 1))

        # φάγωμα δεξιά
        if col < 7 and 0 <= row + direction < 8 and self.board[row + direction][col + 1].strip() and \
                self.board[row + direction][col + 1][0] != piece[0]:
            moves.append((row + direction, col + 1))

        return moves

    def get_rook_moves(self, row, col):
        """Οι κινήσεις του πύργου"""

        moves = []
        piece = self.board[row][col]
        color = piece[0]

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # πάνω, κάτω, αριστερά, δεξιά

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target.strip() == '':
                    moves.append((r, c))
                elif target[0] != color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves

    def get_knight_moves(self, row, col):
        """Οι κινήσεις του ίππου"""

        moves = []
        piece = self.board[row][col]
        color = piece[0]

        knight_jumps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in knight_jumps:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target.strip() == '' or target[0] != color:
                    moves.append((r, c))

        return moves

    def get_bishop_moves(self, row, col):
        """Οι κινήσεις του αξιωματικού"""

        moves = []
        piece = self.board[row][col]
        color = piece[0]

        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # οι διαγώνιες

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target.strip() == '':
                    moves.append((r, c))
                elif target[0] != color:
                    moves.append((r, c))
                    break
                else:
                    break
                r += dr
                c += dc

        return moves

    def get_queen_moves(self, row, col):
        """Οι κινήσεις της βασίλισσας"""

        return self.get_rook_moves(row, col) + self.get_bishop_moves(row, col)

    def get_king_moves(self, row, col):
        """Οι κινήσεις του βασιλιά"""

        moves = []
        piece = self.board[row][col]
        color = piece[0]

        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1), (0, 1),
                      (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                target = self.board[r][c]
                if target.strip() == '' or target[0] != color:
                    moves.append((r, c))

        # ΕΠΙΤΡΕΠΟΥΜΕ ΡΟΚΕ ΓΙΑ ΑΣΠΡΑ
        if piece == 'wK' and row == 7 and col == 4 and not self.white_king_moved:
            # μικρό ροκέ
            if not self.white_rook_kingside_moved and self.board[7][5] == '  ' and self.board[7][6] == '  ':
                moves.append((7, 6))  # g1

            # μεγάλο ροκέ
            if not self.white_rook_queenside_moved and self.board[7][1] == '  ' and self.board[7][2] == '  ' and \
                    self.board[7][3] == '  ':
                moves.append((7, 2))  # c1

        # ΡΟΚΕ ΓΙΑ ΜΑΥΡΑ
        if piece == 'bK' and row == 0 and col == 4 and not self.black_king_moved:
            # μικρό ροκέ
            if not self.black_rook_kingside_moved and self.board[0][5] == '  ' and self.board[0][6] == '  ':
                moves.append((0, 6))  # g8

            # μεγάλο ροκέ
            if not self.black_rook_queenside_moved and self.board[0][1] == '  ' and self.board[0][2] == '  ' and \
                    self.board[0][3] == '  ':
                moves.append((0, 2))  # c8

        return moves

    def ask_for_player_names(self):
        """Ζητάμε τα ονόματα των παικτών"""

        player_1_name = simpledialog.askstring("Παίχτης 1", "Πληκτρολόγησε ένα όνομα:")
        player_2_name = simpledialog.askstring("Παίχτης 2", "Πληκτρολόγησε ένα όνομα:")
        return [player_1_name, player_2_name]

    def make_move_and_write_in_history(self, from_square, to_square, piece):
        """Κάνουμε την κίνηση (αν είναι φυσιολογική) και την καταγράφουμε στο ιστορικό"""

        fr, fc = from_square
        tr, tc = to_square

        # Μετακίνηση (για φυσιολογικές, απλές κινήσεις)
        self.board[tr][tc] = piece
        self.board[fr][fc] = '  '

        # Δημιουργία κειμένου για την κίνηση
        from_notation = f"{chr(fc + 97)}{8 - fr}"
        to_notation = f"{chr(tc + 97)}{8 - tr}"
        player = "⚪️" if piece[0] == 'w' else "⚫️"
        name = self.first_guy if player == "⚪️" else self.second_guy  # για να έχουμε και τα usernames!
        move_text = f"{len(self.move_history) + 1}. {name}({player}): {from_notation} → {to_notation}"

        # Καταγραφή
        self.move_history.append(move_text)

        self.history_box.config(state="normal")
        self.history_box.insert("end", move_text + "\n")
        self.history_box.config(state="disabled")
        self.history_box.see("end")

    def record_castling(self, player_color, side):  # side: "short" ή "long"
        """Γράφουμε το ροκέ που έγινε στο ιστορικό"""

        text = "Ο-Ο" if side == "short" else "Ο-Ο-Ο"
        player = "⚪" if player_color == 'w' else "⚫"
        name = self.first_guy if player == "⚪️" else self.second_guy  # για να έχουμε και τα usernames!
        move_text = f"{len(self.move_history) + 1}. {name}({player}): {text}"
        self.move_history.append(move_text)
        if hasattr(self, "history_box"):
            self.history_box.config(state="normal")
            self.history_box.insert("end", move_text + "\n")
            self.history_box.config(state="disabled")
            self.history_box.see("end")



    def move_piece(self, from_square, to_square):
        """Μετακίνηση από το κλικαρισμένο μας κουτάκι στο επόμενο κουτάκι"""

        fr, fc = from_square
        tr, tc = to_square
        piece = self.board[fr][fc]  # το κομμάτι

        def promotion():
            """Κάνουμε προαγωγή το πιόνι όταν φτάσει στο τέλος του ταμπλό"""

            if piece[1] == 'P' and ((piece[0] == 'w' and tr == 0) or (piece[0] == 'b' and tr == 7)):
                our_choice = simpledialog.askstring("Προαγωγή:", "Διαλέξτε: Q, R, B, N")
                if our_choice == 'Q':
                    self.board[tr][tc] = piece[0] + 'Q'
                elif our_choice == 'R':
                    self.board[tr][tc] = piece[0] + 'R'
                elif our_choice == 'B':
                    self.board[tr][tc] = piece[0] + 'B'
                elif our_choice == 'N':
                    self.board[tr][tc] = piece[0] + 'N'
                else:
                    self.board[tr][tc] = piece[0] + 'Q'

        # Να παίζουν πρώτα τα άσπρα, μετά τα μαύρα κ.ο.κ.
        # Επίσης, έλεγχος αν κουνήθηκε κάτι που θα απαγορεύει να γίνει ροκέ

        # ΑΣΠΡΑ
        if self.current_player == 'w':
            if piece[0] == 'w':
                #### ΡΟΚΕ ####
                if piece == 'wK' and from_square == (7, 4):
                    #### ΜΙΚΡΟ ΡΟΚΕ ####
                    if not self.white_king_moved and not self.white_rook_kingside_moved:
                        if to_square == (7, 6):
                            if self.board[7][5] == '  ' and self.board[7][6] == '  ':
                                self.board[7][6] = 'wK'
                                self.board[7][5] = 'wR'
                                self.board[7][4] = '  '
                                self.board[7][7] = '  '
                                self.white_king_moved = True
                                self.white_rook_kingside_moved = True
                                # μόλις γίνεται το ροκέ, το καταγράφουμε και στο πινακάκι με το ιστορικό κινήσεων
                                self.record_castling('w', 'short')

                                self.current_player = 'b'
                                self.check_end_of_game()  # έλεγχος τέλους
                                return
                    #### ΜΕΓΑΛΟ ΡΟΚΕ ####
                    if not self.white_king_moved and not self.white_rook_queenside_moved:
                        if to_square == (7, 2):
                            if self.board[7][1] == '  ' and self.board[7][2] == '  ' and self.board[7][3] == '  ':
                                self.board[7][2] = 'wK'
                                self.board[7][3] = 'wR'
                                self.board[7][0] = '  '
                                self.board[7][1] = '  '
                                self.board[7][4] = '  '
                                self.white_king_moved = True
                                self.white_rook_queenside_moved = True
                                self.record_castling('w', 'long')
                                self.current_player = 'b'
                                self.check_end_of_game()  # έλεγχος τέλους
                                return

                # για τις φυσιολογικές κινήσεις…
                self.make_move_and_write_in_history(from_square, to_square, piece)

                # προαγωγή πιονιού
                promotion()
                self.check_end_of_game()  # έλεγχος τέλους

                # και να δούμε αν αυτό που κουνήσαμε ήταν ή βασιλιάς ή πύργος
                if piece == 'wK':
                    self.white_king_moved = True
                if piece == 'wR':
                    if from_square == (7, 0):
                        self.white_rook_queenside_moved = True
                    elif from_square == (7, 7):
                        self.white_rook_kingside_moved = True
                self.current_player = 'b'  # τώρα παίζουν τα μαύρα
                self.check_end_of_game()  # έλεγχος τέλους

        # ΜΑΥΡΑ
        if self.current_player == 'b':
            if piece[0] == 'b':
                #### ΡΟΚΕ ####
                if piece == 'bK' and from_square == (0, 4):
                    #### ΜΙΚΡΟ ΡΟΚΕ ####
                    if not self.black_king_moved and not self.black_rook_kingside_moved:
                        if to_square == (0, 6):
                            if self.board[0][5] == '  ' and self.board[0][6] == '  ':
                                self.board[0][6] = 'bK'
                                self.board[0][5] = 'bR'
                                self.board[0][4] = '  '
                                self.board[0][7] = '  '
                                self.black_king_moved = True
                                self.black_rook_kingside_moved = True
                                self.record_castling('b', 'short')
                                self.current_player = 'w'
                                self.check_end_of_game()  # έλεγχος τέλους
                                return
                    #### ΜΕΓΑΛΟ ΡΟΚΕ ####
                    if not self.black_king_moved and not self.black_rook_queenside_moved:
                        if to_square == (0, 2):
                            if self.board[0][1] == '  ' and self.board[0][2] == '  ' and self.board[0][3] == '  ':
                                self.board[0][2] = 'bK'
                                self.board[0][3] = 'bR'
                                self.board[0][0] = '  '
                                self.board[0][1] = '  '
                                self.board[0][4] = '  '
                                self.black_king_moved = True
                                self.black_rook_queenside_moved = True
                                self.record_castling('b', 'notshort')
                                self.current_player = 'w'
                                self.check_end_of_game()  # έλεγχος τέλους
                                return

                # για τις φυσιολογικές κινήσεις
                self.make_move_and_write_in_history(from_square, to_square, piece)
                # προαγωγή πιονιού
                promotion()
                self.check_end_of_game()  # έλεγχος τέλους

                # ελέγχουμε και για τα μαύρα τι κουνήθηκε
                if piece == 'bK':
                    self.black_king_moved = True
                if piece == 'bR':
                    if from_square == (0, 0):
                        self.black_rook_queenside_moved = True
                    elif from_square == (0, 7):
                        self.black_rook_kingside_moved = True
                self.current_player = 'w'  # τώρα παίζουν τα άσπρα

    def save_history(self):
        """Αποθήκευση του ιστορικού"""

        with open("game_history.txt", "w", encoding="utf-8") as file:
            for move in self.move_history:
                file.write(move + "\n")
        popup = tk.Toplevel(self.root)
        tk.Label(popup, text="Η παρτίδα αποθηκεύτηκε ως 'game_history.txt'").pack(padx=20, pady=10)
        tk.Button(popup, text="OK", command=popup.destroy).pack(pady=5)


# Τρέχουμε την εφαρμογή
root = tk.Tk()
app = ChessCanvas(root)
root.mainloop()