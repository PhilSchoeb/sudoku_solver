# Voici le fichier contenant le code pour :
# le numéro 1 : Norvig search
# le numéro 2 : Random search
# le numéro 3 : Norvig avec heuristique naked pairs
# le numéro 3 : Norvig avec heuristique locked candidates (Norvig opti)


# Code de Philippe Schoeb et Nathan Bussière

import random
import time

## Solve Every Sudoku Puzzle

## See http://norvig.com/sudoku.html

## Throughout this program we have:
##   r is a row,    e.g. 'A'
##   c is a column, e.g. '3'
##   s is a square, e.g. 'A3'
##   d is a digit,  e.g. '9'
##   u is a unit,   e.g. ['A1','B1','C1','D1','E1','F1','G1','H1','I1']
##   grid is a grid,e.g. 81 non-blank chars, e.g. starting with '.18...7...
##   values is a dict of possible values, e.g. {'A1':'12349', 'A2':'8', ...}

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

digits   = '123456789'
rows     = 'ABCDEFGHI'
cols     = digits
squares  = cross(rows, cols)

rangees = [cross(r, cols) for r in rows]
colonnes = [cross(rows, c) for c in cols]
carres = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s],[]))-set([s]))
             for s in squares)

################ Unit Tests ################

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

################ Parse a Grid ################

def parse_grid(grid):
    """Convert grid to a dict of possible values, {square: digits}, or
    return False if a contradiction is detected."""
    ## To start, every square can be any digit; then assign values from the grid.
    values = dict((s, digits) for s in squares)
    for s, d in grid_values(grid).items():
        if d in digits and not assign(values, s, d):
            return False ## (Fail if we can't assign d to square s.)
    return values

def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))

################ Constraint Propagation ################
def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s] and propagate.
    Return values, except return False if a contradiction is detected."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False

def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2.
    Return values, except return False if a contradiction is detected."""
    if d not in values[s]:
        return values ## Already eliminated
    values[s] = values[s].replace(d,'')
    ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
    if len(values[s]) == 0:
        return False ## Contradiction: removed last value
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    ## (2) If a unit u is reduced to only one place for a value d, then put it there.
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False ## Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; assign it there
            if not assign(values, dplaces[0], d):
                return False
    return values


################ Display as 2-D grid ################
# Fonction modifiée car l'ancienne ne fonctionnait pas
def display(state):
    "Display these values as a 2-D grid."
    width = 1+max(len(state[s]) for s in squares)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        for c in cols:
            print(str(state[r+c]) + "-", end="")
            if c in '36' : print("|", end="")
        print("")
        if r in 'CF': print(line)

################ Search ################

def solve_norvig(grid): return norvig_search(parse_grid(grid))  # Use norvig_search

def solve_random(grid): return random_search(parse_grid(grid))  # Use random_search

def solve_norvig_heuristic(grid): return norvig_search_heuristic(parse_grid(grid))  # Use norvig with naked pairs

def solve_norvig_opti(grid): return norvig_search_opti(parse_grid(grid))  # Use norvig with locked candidates 2

# array contains multiple arrays and returns array without the values present twice or more
# array = [[1, 2, 3], [3, 4]] ---> [[1, 2], [4]]
def remove_mult(array):
    seen = []
    seen_twice = []
    for i in range(len(array)):
        for j in range(len(array[i])):
            if array[i][j] not in seen:
                seen.append(array[i][j])
            elif array[i][j] not in seen_twice:
                seen_twice.append(array[i][j])

    i = 0
    while i < len(array):
        j = 0
        while j < len(array[i]):
            if len(array[i]) <= j:
                break
            if array[i][j] in seen_twice:
                array[i].remove(array[i][j])
                continue
            j += 1
        i += 1
    return array

# locked candidates 2 heuristic
def locked_c2(values):
    for i in range(9):
        line = colonnes[i]
        compare_array = [[], [], []]
        for j in range(9):
            sq = line[j]
            if len(values[sq]) == 1:
                continue
            cary = j // 3
            for poss_val in values[sq]:
                if poss_val not in compare_array[cary]:
                    compare_array[cary].append(poss_val)

        remaining = remove_mult(compare_array)
        for j in range(len(remaining)):
            for value in remaining[j]:
                square_index = 3*j + (i // 3)
                for s in carres[square_index]:
                    if s not in line and len(values[s]) > 1:
                        if len(values[s]) == 2:
                            eliminate(values, s, value)
                            continue
                        values[s] = values[s].replace(value, '')
    return values


def norvig_search_opti(values):
    "Using depth-first search and propagation, try all possible values with new heuristic."
    if values is False:
        return False  # Failed earlier

    if all(len(values[s]) == 1 for s in squares):
        return values  # Solved!

    values = locked_c2(values)  # New heuristic !

    if values is False:
        return False

    if all(len(values[s]) == 1 for s in squares):
        return values  # Solved!

    # Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(norvig_search_opti(assign(values.copy(), s, d))
                for d in values[s])


# Une autre heuristique qu'on a essayé d'ajouter fonctionne sur tous les sudokus
def norvig_search_heuristic(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False  ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  ## Solved!

    # Heuristique qui rajoute du temps
    for unit in unitlist:
        candidat_potentiels = []
        for square in unit:
            if (len(values[square]) == 2):
                if (values[square] not in candidat_potentiels):
                    candidat_potentiels.append(values[square])
                else:
                    for s in unit:
                        if values[s] != values[square]:
                            for digit in values[square]:

                                if not eliminate(values.copy(), s, digit):
                                    return False

    # Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(norvig_search_heuristic(assign(values.copy(), s, d))
                for d in values[s])


def norvig_search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values ## Solved!

    # Chose the unfilled square s with the fewest possibilities
    n, s = min((len(values[s]), s) for s in squares if len(values[s]) > 1)
    return some(norvig_search(assign(values.copy(), s, d))
                for d in values[s])


def random_search(values):
    "Using depth-first search and propagation, try all possible values."
    if values is False:
        return False  # Failed earlier
    if all(len(values[s]) == 1 for s in squares):
        return values  # Solved!

    # Chose the unfilled quare s randomly
    count = 0
    unfilled_s = []
    for s in squares:
        if len(values[s]) > 1:
            count += 1
            unfilled_s.append(s)
    index = random.randrange(count)
    s = unfilled_s[index]

    return some(random_search(assign(values.copy(), s, d))
                for d in values[s])

################ Utilities ################

def some(seq):
    "Return some element of seq that is true."
    for e in seq:
        if e: return e
    return False

def from_file(filename, sep='\n'):
    "Parse a file into a list of strings, separated by sep."
    return open(filename).read().strip().split(sep)

def shuffled(seq):
    "Return a randomly shuffled copy of the input sequence."
    seq = list(seq)
    random.shuffle(seq)
    return seq

################ System test ################

def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results.
    When showif is a number of seconds, display puzzles that take longer.
    When showif is None, don't display any puzzles."""

    def time_solve_norvig(grid):
        start = time.time()
        values = solve_norvig(grid)
        t = time.time()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    def time_solve_random(grid):
        start = time.time()
        values = solve_random(grid)
        t = time.time()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    def time_solve_norvig_opti(grid):
        start = time.time()
        values = solve_norvig_opti(grid)
        t = time.time()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    def time_solve_norvig_heuristic(grid):
        start = time.time()
        values = solve_norvig_heuristic(grid)
        t = time.time()-start
        ## Display puzzles that take long enough
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    # Norvig
    times, results = zip(*[time_solve_norvig(grid) for grid in grids])
    N = len(grids)
    if N >= 1:
        print("NORVIG")
        print("Solved %d of %d %s puzzles (avg %.8f secs (%d Hz), max %.8f secs)." % (
            sum(results), N, name, sum(times)/N, N/sum(times), max(times)))

    # Random
    times, results = zip(*[time_solve_random(grid) for grid in grids])
    N = len(grids)
    if N >= 1:
        print("RANDOM")
        print("Solved %d of %d %s puzzles (avg %.8f secs (%d Hz), max %.8f secs)." % (
            sum(results), N, name, sum(times) / N, N / sum(times), max(times)))

    # Norvig naked pairs
    times, results = zip(*[time_solve_norvig_heuristic(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print("NORVIG WITH NAKED PAIRS")
        print("Solved %d of %d %s puzzles (avg %.8f secs (%d Hz), max %.8f secs)." % (
            sum(results), N, name, sum(times) / N, N / sum(times), max(times)))

    # Norvig locked candidates
    times, results = zip(*[time_solve_norvig_opti(grid) for grid in grids])
    N = len(grids)
    if N >= 1:
        print("NORVIG WITH LOCKED CANDIDATES 2")
        print("Solved %d of %d %s puzzles (avg %.8f secs (%d Hz), max %.8f secs)." % (
            sum(results), N, name, sum(times) / N, N / sum(times), max(times)))



def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)
    return values is not False and all(unitsolved(unit) for unit in unitlist)

def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments. Restart on contradictions.
    Note the resulting puzzle is not guaranteed to be solvable, but empirically
    about 99.8% of them are solvable. Some have multiple solutions."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s])==1 else '.' for s in squares)
    return random_puzzle(N) ## Give up and make a new puzzle

grid1  = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
grid2  = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
hard1  = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
resol1 = '000001600400080003050060001020000800000020010900700065080205079000007080090040006'
    
if __name__ == '__main__':
    test()
    # solve_all(resol1.strip().split('\n'), "sudoku", None)
    solve_all(from_file("100sudoku.txt"), "sudokus", None)


## References used:
## http://www.scanraid.com/BasicStrategies.htm
## http://www.sudokudragon.com/sudokustrategy.htm
## http://www.krazydad.com/blog/2005/09/29/an-index-of-sudoku-strategies/
## http://www2.warwick.ac.uk/fac/sci/moac/currentstudents/peter_cock/python/sudoku/
