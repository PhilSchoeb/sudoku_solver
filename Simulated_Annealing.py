# Voici le fichier contenant le code pour :
# le numéro 5 : Simulated annealing sans la propagation des contraintes

# Code de Philippe Schoeb et Nathan Bussière

from aima3.search import *
import time

# Schedule function
def sched(alpha=0.99):
    return lambda t: alpha*t if t > 1 * 10**(-20) else 0

# On a modifié cette fonction pour qu'elle fonctionne comme nous voulons
def simulated_annealing(problem, schedule=exp_schedule()):
    """[Figure 4.5] CAUTION: This differs from the pseudocode as it
    returns a state instead of a Node."""
    current = Node(problem.initial)
    T = 3  # initial temperature
    while True:
        T = schedule(T)
        if T == 0:
            return current.state
        neighbors = current.expand(problem)
        if not neighbors:
            return current.state
        next = random.choice(neighbors)
        delta_e = problem.value(next.state) - problem.value(current.state)
        if delta_e > 0 or probability(math.exp(delta_e / T)):
            current = next

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
carres = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]  # 9 carrés du problème
rangees = [cross(rows, c) for c in cols]
colonnes = [cross(r, cols) for r in rows]
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)


def display(state):
    "Display these values as a 2-D grid."
    width = 1+max(len(state[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        for c in cols:
            print(str(state[r+c][0]) + "-", end="")
            if c in '36' : print("|", end="")
        print("")
        if r in 'CF': print(line)
    print("\n")
    for r in rows:
        for c in cols:
            print(str(state[r + c][1]) + "-", end="")
            if c in '36': print("|", end="")
        print("")
        if r in 'CF': print(line)

def test():
    "A set of tests that must pass."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print('All tests pass.')

def solve(grid): return (parse_grid(grid))

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: (digits, editable)}, or
    return False if a contradiction is detected. editable is a boolean that indicates
    whether the value can be modified. i.e. the value was not given from the start"""

    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, (digits, True)) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))

def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s].
    Return values."""
    other_values = values[s][0].replace(d, '')
    for d2 in other_values:
        values[s] = (values[s][0].replace(d2, ''), values[s][1])
    return values


# Fill the sudoku with random values that respect the square constraint
def complete(values):
    for car in carres:
        dig_left = '123456789'
        for s in car:
            if len(values[s][0]) == 1:
                dig_left = dig_left.replace(str(values[s][0]), '')
                values[s] = (values[s][0], False)

        for s in car:
            if len(values[s][0]) != 1:
                index = random.randrange(len(dig_left))
                values[s] = (dig_left[index], True)
                dig_left = dig_left.replace(dig_left[index], '')
        assert len(dig_left) == 0
    return values

# Class for problem resolution
class Sudoku(Problem):
    def __init__(self, initial):
        super().__init__(initial)

    def actions(self, state):
        actions_possibles = []

        for car in carres:
            can_swap = []
            for s in car:
                if state[s][1]:
                    can_swap.append(s)
            for i in range(len(can_swap)):
                for j in range(i+1, len(can_swap)):
                    action = (can_swap[i], can_swap[j])
                    actions_possibles.append(action)

        return actions_possibles

    def result(self, state, action):
        new_state = state.copy()
        i = action[0]
        j = action[1]
        temp = state[i][0]
        new_state[i] = (state[j][0], True)
        new_state[j] = (temp, True)
        assert new_state[i][0] != temp
        assert new_state[i][1] and new_state[j][1]
        return new_state

    def goal_test(self, state):
        "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
        def unitsolved(unit): return set(state[s] for s in unit) == set(digits)
        b = state is not False and all(unitsolved(unit) for unit in unitlist)
        return b

    def value(self, state):  # put negative value so it can maximise score
        score = 0

        square_er = 0
        for car in carres:
            dig = digits
            for s in car:
                dig = dig.replace(str(state[s][0]), '')
            square_er += len(dig)
        assert square_er == 0

        row_er = 0
        for r in rangees:
            dig = digits
            for s in r:
                dig = dig.replace(str(state[s][0]), '')
            row_er += len(dig)
        assert 0 <= row_er

        col_er = 0
        for c in colonnes:
            dig = digits
            for s in c:
                dig = dig.replace(str(state[s][0]), '')
            col_er += len(dig)
            assert 0 <= col_er


        score = - row_er - col_er - square_er
        return score



def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return open(filename).read().strip().split(sep)

def solved(solution):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit): return set(solution[s][0] for s in unit) == set(digits)
    b1 = solution is not False
    b2 = all(unitsolved(unit) for unit in unitlist)
    return b1 and b2

def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""
    def solve_single(grid):
        start = time.time()
        values = solve(grid)

        if solved(values):
            print("Solved without Simulated annealing")
            t = time.time() - start
            return t, True, 1, 0

        values = complete(values)
        sudoku = Sudoku(values)
        initial_score = sudoku.value(values)
        solution = simulated_annealing(sudoku, sched())
        t = time.time()-start
        final_score = sudoku.value(solution)
        print("Using Simulated Annealing, went from %d to %d" % (initial_score, final_score))
        return t, solved(solution), 0, initial_score, final_score

    times, results, already, i_scores, f_scores = zip(*[solve_single(grid) for grid in grids])
    N = len(grids)
    if N >= 1:
        print("Simulated Annealing")
        print("Solved %d of %d %s puzzles, and %d were solved without Simulated annealing, (avg %.8f secs (%d Hz), "
              "max %.8f secs), average score from : %d to %d." % (sum(results), N, name, sum(already), sum(times)/N,
                                                                  N/(sum(times)), max(times), sum(i_scores)/N,
                                                                  sum(f_scores)/N))

hard1 = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
easy1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'

if __name__ == '__main__':
    test()
    #solve_all(easy1.strip().split("\n"), "sudoku", None)
    solve_all(from_file("100sudoku.txt"), "sudokus", None)