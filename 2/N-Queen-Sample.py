from typing import List, Tuple, Dict, Set
"""
N‑Queens with Obstacles  –  CSP skeleton.

Complete ALL TODO blocks; keep the public function signature unchanged.
You may add helpers or change the internal design as long as tests pass.
"""



# --------------------------------------------------------------------------- #
#  High‑level driver                                                          #
# --------------------------------------------------------------------------- #
def count_nqueens(
        n: int,
        obstacles: List[Tuple[int, int]]
) -> int:
    """Return the number of valid N‑Queens placements.

    Parameters
    ----------
    n : int
        Board size (N×N) and number of queens to place.
    obstacles : list[(int, int)]
        0‑based coordinates of blocked squares.

    Returns
    -------
    int
        Number of distinct solutions.
    """
    # ---------- TODO #1  Domain construction  --------------------------------
    # Build a dict: row -> set of columns still possible after removing blocks.
    domains: Dict[int, Set[int]] = build_domains(n, obstacles)

    # ---------- TODO #2  Back‑tracking search  -------------------------------
    # Implement complete search with MRV + consistency + forward checking.
    solution_count = backtrack(domains, assignment={})

    return solution_count


# --------------------------------------------------------------------------- #
#  Helper functions students must complete                                    #
# --------------------------------------------------------------------------- #
def build_domains(n: int, obstacles: List[Tuple[int, int]]) -> Dict[int, Set[int]]:
    """TODO - return initial domains (row -> set of legal columns)."""
    res = {}
    for i in range(n):
        res[i]=set()
        for j in range(n):
            if not (i,j) in obstacles:
                res[i].add(j)
    return res


def select_unassigned_var(domains: Dict[int, Set[int]],
                           assignment: Dict[int, int]) -> int:
    """TODO - return the row (variable) to assign next, using MRV."""
    unassigned = [row for row in domains if row not in assignment]
    if not unassigned:
        return None 
    return min(unassigned, key=lambda r: len(domains[r]))


def is_consistent(row: int, col: int,
                   assignment: Dict[int, int]) -> bool:
    """TODO – check column & diagonal constraints."""
    for placed_row, placed_col in assignment.items():
        if col == placed_col:
            return False
        if abs(row - placed_row) == abs(col - placed_col):
            return False
    return True


def forward_check(domains: Dict[int, Set[int]],
                   row: int,
                   col: int,
                   assignment: Dict[int, int]) -> Dict[int, Set[int]]:
    """
    TODO – return **new copied** domains after pruning values that
    conflict with the just‑chosen (row, col).  Ignore rows already assigned.

    Hints
    -----
    • Remove 'col' from every other row's domain.
    • Remove any column that gives identical major / minor diagonal index.
    """
    flag= 0
    new_domains = {
        row: set(cols) for row, cols in domains.items()
    }
    for i in domains.keys():
        if i in assignment.keys():
            continue
        domain = domains[i]
        tm_flag = 1
        for d_col in domain:
            
            if col == d_col:
                new_domains[i].remove(d_col)
                continue
            if abs(i-row) == abs(col-d_col):
                new_domains[i].remove(d_col)
                continue

            tm_flag = 0

        flag = flag or tm_flag
    return new_domains,flag


def backtrack(domains: Dict[int, Set[int]],
               assignment: Dict[int, int],) -> int:
    """Recursive back‑tracking search returning #solutions below this node."""
    row = select_unassigned_var(domains, assignment)
    if row is None:
        # print(assignment)
        return 1
    
    total = 0
    for col in domains[row]:
        if is_consistent(row, col, assignment):
            assignment[row] = col
            new_domains,flag = forward_check(domains, row, col,assignment)
            if flag:
                del assignment[row]
                continue
            total += backtrack(new_domains, assignment)
            del assignment[row]
    return total
    # TODO – implement back‑tracking with:
    #   • variable selection (MRV),
    #   • consistency test,
    #   • forward checking,
    #   • solution counting.
    raise NotImplementedError
n = int(input())
l = int(input())
o = []
for i in range(l):
    q,w = map(int,input().split(','))
    o.append((q,w))

print(count_nqueens(n,o))



