
from tkinter import *

from games import *
from monteCarlo import *

gBoard = None
root = None
buttons = []
frames = []
x_pos = []
o_pos = []

sym = ""
result = None
choices = None
gSize = 3

def create_frames(root):
    """
    This function creates the necessary structure of the game.
    """
    global gBoard
    gBoard = TicTacToe(gSize, gSize, -1)
   
    for _ in range(gSize):
        framei = Frame(root)
        create_arow(framei)
        framei.pack(side = BOTTOM)
        frames.append(framei)

    uiFrame = Frame(root)
    buttonExit = Button(uiFrame, height=1, width=4, text="Exit", command=lambda: exit_game(root))
    buttonExit.pack(side=LEFT)
    uiFrame.pack(side=TOP)
    buttonReset = Button(uiFrame, height=1, width=4, text="Reset", command=lambda: reset_game())
    buttonReset.pack(side=LEFT)

    """Timer is used with MinMax, AlphaBeta, and MonteCarlo players"""
    timeFrame = Frame(root)
    timeFrame.pack(side=TOP)
    timeLabel = Label(timeFrame, text="Timer:", width=10, fg="green")
    timeLabel.pack(side=LEFT)

    timeStr = StringVar()
    timeStr.set(str("-1"))  # -1 means no time limit for search
    
    def timerCallback(event):
        global gBoard
        dstr = event.widget.get().strip()
        #print("Time limit in seconds: ", dstr)
        if dstr.isdigit():
            if int(dstr) > 0:
                print("Time limit in seconds: ", int(dstr))
                gBoard.timer = int(dstr)
            else:
                print("Warning! Timer value must be positive")
        return True
    
    timeEntry = Entry(timeFrame, width =7, textvariable=timeStr)
    timeEntry.bind('<KeyRelease>', timerCallback)
    timeEntry.pack(side = LEFT)


def create_arow(frame):
    """
    creates the buttons for one row of the board .
    """
    buttons_in_frame = []

    for _ in range(gSize):
        button = Button(frame, bg = "yellow", height=1, width=2, text=" ", padx=2, pady=2)
        button.config(command=lambda btn=button: on_click(btn))
        button.pack(side=LEFT)
        buttons_in_frame.append(button)

    buttons.append(buttons_in_frame)

def on_click(button):
    """
    This function determines the action of any button.
    """
    global gBoard, choices, sym, result, x_pos, o_pos
    #print("onClick: button.text=", button['text'])
    sym = "X"

    button.config(text=sym, state='disabled', disabledforeground="red")  # For cross

    x, y = get_coordinates(button)
    x += 1
    y += 1
    x_pos.append((x, y))
    state1 = gen_state((x, y), to_move=sym, x_positions=x_pos,  o_positions=o_pos, h=gBoard.k, v=gBoard.k)

    #check human player victory:
    if gBoard.compute_utility(state1.board.copy(), (x, y), state1.to_move)==gBoard.k:
        result.set("You win :)")
        disable_game(state1)
        return

    result.set("O Turn!")
    Tk.update(root)
    time.sleep(0.5)

    sym = "O"
    state2 = gen_state((x, y), to_move=sym, x_positions=x_pos, o_positions=o_pos, h=gBoard.k, v=gBoard.k)
    a = b = None
    #try:
    if(len(state2.moves) > 0):
        choice = choices.get()
        if "Random" in choice:
            a, b = random_player(gBoard, state2)
        elif "MinMax" in choice:
            a, b = minmax_player(gBoard, state2)
        elif "AlphaBeta" in choice:
            a, b = alpha_beta_player(gBoard, state2)
        elif "MonteCarlo" in choice:
            mcSearch = MCTS(gBoard, state2)
            a, b = mcSearch.monteCarloPlayer()

    if a == None or b == None:
        disable_game(state2)
        result.set("It is a draw")
        return
    
    if 1 <= a <= gSize and 1 <= b <= gSize:
        o_pos.append((a, b))
        button_to_change = buttons[a-1][b-1]

        board = state2.board.copy()
        move = (a, b)
        board[move] = sym
        button_to_change.config(text=sym, state='disabled', disabledforeground="black")

        if gBoard.compute_utility(board, move, sym) == -gBoard.k:
            result.set("You lose :(")
            disable_game(state2)
        elif len(board) == gBoard.maxDepth:
            disable_game(state2)
            result.set("It is a draw")
        else:
            result.set("Your Turn!")


def get_coordinates(button):
    """
    This function returns the coordinates of the button clicked.
    """
    for x in range(len(buttons)):
        for y in range(len(buttons[x])):
            if buttons[x][y] == button:
                return x, y


def reset_game():
    """
    This function will reset all the tiles to the initial null value.
    """
    global gBoard, x_pos, o_pos, frames

    x_pos = []
    o_pos = []
    result.set("Your Turn!")
    for x in frames:
        for y in x.winfo_children():
            y.config(text=" ", state='normal')
    
    gBoard.reset()


def disable_game(st):
    """
    This function deactivates the game after a win, loss or draw.
    """
    global gBoard
    gBoard.display(st)
    global frames
    for x in frames:
        for y in x.winfo_children():
            y.config(state='disabled')


def exit_game(root):
    """
    This function will exit the game by killing the root.
    """
    root.destroy()


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        gSize = int(sys.argv[1])
        gSize =  int(sys.argv[1])
        gkmatch = int(sys.argv[1])
    else:
        gSize = 3
        gSize = 3
        gkmatch = 3

    root = Tk()
    root.title("TicTacToe")
    width = gSize * 80
    height = gSize * 80
    geoStr = str(width) + "x" + str(height)
    root.geometry(geoStr)  
    root.resizable(1, 1)  # To remove the maximize window option
    result = StringVar()
    result.set("Your Turn!")
    w = Label(root, textvariable=result, fg = "brown")
    w.pack(side=BOTTOM)
    create_frames(root)
    choices = StringVar(root)
    choices.set("Random")
    menu = OptionMenu(root, choices, "Random", "MinMax", "AlphaBeta", "MonteCarlo")
    menu.pack(side=TOP) 

    root.mainloop()
