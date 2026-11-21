"""Original Phase 4 authoring inputs. Offline only; never imported by the API."""


def q(prompt, options, correct, explanation, code=None, *, output=False, bug=False):
    return {
        "prompt": prompt,
        "options": options,
        "correct": correct,
        "explanation": explanation,
        "code": code,
        "verify_stdout": output,
        "question_type": "bug_identification"
        if bug
        else "code_tracing"
        if code
        else "multiple_choice",
    }


CONTENT = {
    "call_stack": {
        "title": "Keep each active call separate",
        "body": (
            "A call frame holds that call's parameters, local variables and r"
            "eturn point. Calling another function suspends the caller. A ret"
            "urn removes the newest active frame and resumes its caller. Draw"
            " frames from oldest to newest; count active frames separately fr"
            "om the total number of calls. This lesson provides context, not "
            "correctness evidence."
        ),
        "questions": [
            q(
                "Immediately before leaf returns, which frame is the newest active frame?",
                ["main", "middle", "leaf", "All three return together"],
                2,
                (
                    "main called middle, and middle called leaf. leaf is newest and r"
                    "eturns before its suspended callers."
                ),
                (
                    "def leaf():\n    return 7\ndef middle():\n    return leaf()\ndef mai"
                    "n():\n    return middle()\n\nmain()"
                ),
            ),
            q(
                "What does the outer call print after the inner call returns?",
                ["4", "9", "2", "6"],
                1,
                (
                    "The inner frame has n=2 and returns 4. Its local n does not repl"
                    "ace the outer frame's n=9."
                ),
                (
                    "def show(n):\n    if n == 2:\n        return n * 2\n    show(2)\n   "
                    " print(n)\n\nshow(9)"
                ),
                output=True,
            ),
            q(
                (
                    "Count only active frames of depth, including the initial call. W"
                    "hat is the maximum number before any return?"
                ),
                ["1", "2", "3", "4"],
                3,
                (
                    "depth(3), depth(2), depth(1) and depth(0) are simultaneously act"
                    "ive at the boundary; that is four frames."
                ),
                "def depth(n):\n    if n == 0:\n        return\n    depth(n - 1)\n\ndepth(3)",
            ),
            q(
                "Which order is printed as suspended calls resume?",
                ["[1, 2, 3]", "[3, 2, 1]", "[0, 1, 2, 3]", "[3]"],
                0,
                (
                    "The boundary returns first. The frame for n=1 appends before n=2"
                    ", which appends before n=3."
                ),
                (
                    "order = []\ndef unwind(n):\n    if n == 0:\n        return\n    unwi"
                    "nd(n - 1)\n    order.append(n)\nunwind(3)\nprint(order)"
                ),
                output=True,
            ),
            q(
                "When helper returns 5, where does execution resume in caller?",
                [
                    "At the start of caller with x reset",
                    "Inside a new helper frame",
                    "At y = x + 1 with caller's x equal to 5",
                    "At return y before assigning y",
                ],
                2,
                (
                    "The call expression receives the return value, assigns x=5, then"
                    " caller proceeds to its next statement."
                ),
                (
                    "def helper():\n    return 5\ndef caller():\n    x = helper()\n    y "
                    "= x + 1\n    return y"
                ),
            ),
            q(
                (
                    "How many recur frames remain active immediately after recur(0) r"
                    "eturns to recur(1)? Count recur only."
                ),
                ["0", "1", "2", "3"],
                2,
                (
                    "The frame recur(0) is removed. recur(1) and its suspended caller"
                    " recur(2) remain, so two recur frames are active."
                ),
                (
                    "def recur(n):\n    if n == 0:\n        return 0\n    value = recur("
                    "n - 1)\n    return value + 1\n\nrecur(2)"
                ),
            ),
        ],
    },
    "recursive_progress": {
        "title": "Choose a measure that must decrease",
        "body": (
            "State the input domain and a nonnegative measure of remaining wo"
            "rk. On every recursive branch that can run, the measure must str"
            "ictly decrease toward a reachable stopping condition. Changing a"
            " value is not sufficient if it can cycle or skip the boundary. F"
            "or multiple branches, check every branch. No readiness changes m"
            "erely from reading this lesson."
        ),
        "questions": [
            q(
                (
                    "For a positive integer n with stopping condition n == 0, which r"
                    "ecursive argument reaches that boundary for every permitted n?"
                ),
                ["n + 1", "n - 1", "n", "n + 2"],
                1,
                (
                    "Subtracting one strictly decreases the nonnegative remaining cou"
                    "nt and eventually reaches zero."
                ),
            ),
            q(
                (
                    "For initial n=3, which change fixes progress while keeping the s"
                    "tated domain and n == 0 boundary?"
                ),
                ["Use walk(n + 1)", "Use walk(n)", "Remove the if", "Use walk(n - 1)"],
                3,
                (
                    "The current branch increases n away from zero. Subtracting one m"
                    "akes the boundary reachable."
                ),
                (
                    "def walk(n):  # n is a nonnegative integer\n    if n == 0:\n      "
                    "  return\n    walk(n + 1)"
                ),
                bug=True,
            ),
            q(
                (
                    "The input may be any nonnegative integer. Why is n - 2 with only"
                    " n == 0 an invalid termination argument?"
                ),
                [
                    "Odd positive inputs pass from 1 to -1 and never reach zero",
                    "Even inputs never change",
                    "Subtracting two always increases n",
                    "Zero calls itself",
                ],
                0,
                (
                    "Even inputs reach zero, but odd inputs skip it. A proof must cov"
                    "er the entire stated domain."
                ),
            ),
            q(
                (
                    "For each pair (left, right) below, the interval is nonempty. Whi"
                    "ch quantity strictly decreases in search(left + 1, right)?"
                ),
                ["right + left", "right", "right - left + 1", "The number of previous calls"],
                2,
                (
                    "The inclusive interval length drops by one while right stays fix"
                    "ed. It can serve as a progress measure."
                ),
            ),
            q(
                (
                    "How many reductions does steps count from its initial positive i"
                    "nteger argument before reaching zero?"
                ),
                ["1", "2", "3", "4"],
                3,
                (
                    "Integer halving follows 9 → 4 → 2 → 1 → 0, four strict reduction"
                    "s before the boundary returns zero."
                ),
                (
                    "def steps(n):\n    if n == 0:\n        return 0\n    return 1 + ste"
                    "ps(n // 2)\nprint(steps(9))"
                ),
                output=True,
            ),
            q(
                (
                    "For n > 0, solve recurses on both n - 1 and n. With a boundary a"
                    "t n == 0, which branch violates progress?"
                ),
                [
                    "Only solve(n)",
                    "Only solve(n - 1)",
                    "Both always decrease n",
                    "Neither branch can run",
                ],
                0,
                (
                    "solve(n) receives the unchanged positive state and can repeat fo"
                    "rever. Each reachable branch needs its own decreasing measure."
                ),
                "def solve(n):\n    if n == 0:\n        return 0\n    return solve(n - 1) + solve(n)",
            ),
        ],
    },
    "recursive_tracing": {
        "title": "Trace calls, then unwind returned values",
        "body": (
            "Write each argument on descent until a boundary returns a known "
            "result. Then substitute that result into the suspended caller, o"
            "ne frame at a time. Keep work before a recursive call distinct f"
            "rom work after it. In branching recursion, finish the first bran"
            "ch before adding the second according to the stated evaluation o"
            "rder. Trace the given code rather than assuming a familiar formu"
            "la."
        ),
        "questions": [
            q(
                "For nonnegative n, what does this program print?",
                ["0", "3", "6", "9"],
                2,
                "add_down(0)=0; returns unwind as 1, then 3, then 6.",
                (
                    "def add_down(n):\n    if n == 0:\n        return 0\n    return n + "
                    "add_down(n - 1)\nprint(add_down(3))"
                ),
                output=True,
            ),
            q(
                "Which sequence is printed by work before and after the recursive call?",
                ["[2, 1, -1, -2]", "[1, 2, -2, -1]", "[-2, -1, 1, 2]", "[2, -2, 1, -1]"],
                0,
                (
                    "Positive values are appended on descent (2,1). Negative values a"
                    "re appended on return (-1,-2)."
                ),
                (
                    "seen = []\ndef visit(n):\n    if n == 0:\n        return\n    seen.a"
                    "ppend(n)\n    visit(n - 1)\n    seen.append(-n)\nvisit(2)\nprint(see"
                    "n)"
                ),
                output=True,
            ),
            q(
                "Only nonnegative n is allowed. What is printed?",
                ["3", "6", "7", "8"],
                3,
                "grow(0)=1, then doubling at each of three returning frames gives 2,4,8.",
                (
                    "def grow(n):\n    if n == 0:\n        return 1\n    return 2 * grow"
                    "(n - 1)\nprint(grow(3))"
                ),
                output=True,
            ),
            q(
                "The empty product is defined as 1. What does product_from(1) print for the fixed list?",
                ["4", "12", "24", "0"],
                1,
                (
                    "The suffix starting at index 1 contains 3 and 4. The boundary re"
                    "turns 1, so the product is 3*4*1=12."
                ),
                (
                    "values = [2, 3, 4]\ndef product_from(i):\n    if i == len(values):"
                    "\n        return 1\n    return values[i] * product_from(i + 1)\npri"
                    "nt(product_from(1))"
                ),
                output=True,
            ),
            q(
                "For n=2, what value is printed after both recursive branches return?",
                ["2", "3", "4", "5"],
                2,
                "Each n=1 branch returns 1+1=2; the n=2 frame adds the two returned values to get 4.",
                (
                    "def leaves(n):\n    if n == 0:\n        return 1\n    return leaves"
                    "(n - 1) + leaves(n - 1)\nprint(leaves(2))"
                ),
                output=True,
            ),
            q(
                "For nonnegative n, trace the code and choose the printed result.",
                ["2", "4", "5", "8"],
                2,
                (
                    "mystery(0)=2, then the three returning frames add 1 each: 3,4,5."
                    " It does not return the argument n."
                ),
                (
                    "def mystery(n):\n    if n == 0:\n        return 2\n    return myste"
                    "ry(n - 1) + 1\nprint(mystery(3))"
                ),
                output=True,
            ),
        ],
    },
    "recurrence_relations": {
        "title": "Give each smaller state a precise meaning",
        "body": (
            "A recurrence expresses a defined state's value through smaller s"
            "tates. Include both the recurrence's valid index range and its b"
            "oundary values. Counting alternatives adds their counts; choosin"
            "g a best alternative often uses min or max. Do not confuse a rec"
            "urrence for the answer with one for runtime. Verify a small exam"
            "ple independently."
        ),
        "questions": [
            q(
                (
                    "S(n) is the sum 1+…+n for integer n≥0, and S(0)=0. Which recurre"
                    "nce matches this definition?"
                ),
                [
                    "S(n)=S(n-1)+n for n≥1",
                    "S(n)=S(n-1)*n for n≥1",
                    "S(n)=S(n+1)+n for n≥1",
                    "S(n)=n for every n",
                ],
                0,
                "The terms up to n-1 contribute S(n-1); adding the final term n gives the required sum.",
            ),
            q(
                (
                    "An empty string has one construction. A length-n string uses onl"
                    "y symbols A or B. Which pair correctly counts all strings?"
                ),
                [
                    "C(0)=0; C(n)=2+C(n-1)",
                    "C(0)=1; C(n)=2*C(n-1)",
                    "C(0)=2; C(n)=C(n-1)",
                    "C(0)=1; C(n)=C(n-1)+1",
                ],
                1,
                (
                    "Each shorter string has two possible final symbols; the empty st"
                    "ring supplies the initial one construction."
                ),
            ),
            q(
                "A sequence is defined by a(0)=1 and a(n)=a(n-1)+2 for n≥1. What is a(3)?",
                ["3", "5", "6", "7"],
                3,
                "Starting from 1, three increments of two produce 3,5,7.",
            ),
            q(
                (
                    "ways(n) counts ordered paths climbing n stairs using steps of 1 "
                    "or 2. ways(0)=1 and ways(1)=1. For n≥2, which recurrence separat"
                    "es paths by their final step?"
                ),
                [
                    "ways(n)=ways(n-1)*ways(n-2)",
                    "ways(n)=ways(n-1)+1",
                    "ways(n)=ways(n-1)+ways(n-2)",
                    "ways(n)=2*n",
                ],
                2,
                (
                    "A final one-step comes from n-1 and a final two-step from n-2. T"
                    "hese disjoint alternatives add."
                ),
            ),
            q(
                (
                    "best(i) is the maximum score obtainable after choosing exactly o"
                    "ne option at stage i; each choice adds its score to best(i-1). O"
                    "ption scores are 3 and 8. Which transition matches that definiti"
                    "on?"
                ),
                [
                    "min(best(i-1)+3, best(i-1)+8)",
                    "max(best(i-1)+3, best(i-1)+8)",
                    "best(i-1)+3+8",
                    "best(i-1)*8",
                ],
                1,
                (
                    "Exactly one option is chosen, and the objective is maximum total"
                    " score. Adding both would violate the choice constraint."
                ),
            ),
            q(
                (
                    "T(n) counts calls in a routine that makes one smaller call and p"
                    "erforms one unit of additional work. T(0)=1. Which runtime recur"
                    "rence matches n≥1?"
                ),
                ["T(n)=T(n-1)+1", "T(n)=n*T(n-1)", "T(n)=2*T(n-1)+1", "T(n)=T(n+1)-1"],
                0,
                (
                    "One smaller call contributes T(n-1), and the present call adds o"
                    "ne. This models work, rather than a problem's numeric answer."
                ),
            ),
        ],
    },
    "overlapping_subproblems": {
        "title": "Look for repeated complete states",
        "body": (
            "Two calls overlap when they ask for the same defined subproblem "
            "under the same fixed inputs. Trace the state arguments, not just"
            " the function name or the shape of its code. Independent recursi"
            "ve branches can revisit a state; a single decreasing chain need "
            "not do so. Caching helps repeated work only when a complete, sta"
            "ble state identifies the same answer."
        ),
        "questions": [
            q(
                (
                    "f(4) expands to f(3)+f(2), and f(3) expands to f(2)+f(1). Which "
                    "non-boundary state is requested twice?"
                ),
                ["f(4)", "f(3)", "f(2)", "There is no repeated state"],
                2,
                "f(2) occurs directly under f(4) and again under f(3), so those requests overlap.",
            ),
            q(
                (
                    "Which recursion pattern has no repeated state within one invocat"
                    "ion, assuming n starts at 4 and the boundary is n==0?"
                ),
                [
                    "f(n-1)+f(n-2)",
                    "One call to f(n-1)",
                    "Two separate calls to f(n-1)",
                    "f(n-1)+f(n-1)+f(n-1)",
                ],
                1,
                (
                    "A single chain visits 4,3,2,1,0 once each. Branching into the sa"
                    "me or converging states creates repetition."
                ),
            ),
            q(
                (
                    "A path-counting state is (row,column) on one fixed grid. Which t"
                    "wo calls ask for exactly the same subproblem?"
                ),
                [
                    "paths(1,2) and paths(2,1)",
                    "paths(0,2) and paths(1,2)",
                    "paths(1,1) and paths(1,2)",
                    "paths(1,2) and paths(1,2)",
                ],
                3,
                (
                    "The ordered pair identifies a cell. Exchanging coordinates or ch"
                    "anging one coordinate generally changes the subproblem."
                ),
            ),
            q(
                "The function's counter records every invocation. How many calls use the state n=1?",
                ["1", "2", "3", "4"],
                1,
                "f(3) calls f(2) and f(1); f(2) also calls f(1), so n=1 is requested twice.",
                (
                    "calls = []\ndef f(n):\n    calls.append(n)\n    if n <= 1:\n        "
                    "return 1\n    return f(n - 1) + f(n - 2)\nf(3)\nprint(calls.count(1"
                    "))"
                ),
                output=True,
            ),
            q(
                (
                    "Which observation is sufficient to justify avoiding duplicate co"
                    "mputation with a cache, for a pure function on fixed input data?"
                ),
                [
                    "Its code contains a loop",
                    "It has at least two local variables",
                    "The same complete state is requested again and has the same answer",
                    "Its answer is always positive",
                ],
                2,
                (
                    "Repeated requests to the same complete stable state are reusable"
                    ". Loops, local-variable counts and positivity do not establish o"
                    "verlap."
                ),
            ),
            q(
                (
                    "A trace visits states (i,remaining) = (0,3),(1,2),(1,3),(2,2),(2"
                    ",2). Which state represents repeated work?"
                ),
                ["(0,3)", "(1,2)", "(1,3)", "(2,2)"],
                3,
                (
                    "Only the complete pair (2,2) appears more than once. Sharing jus"
                    "t i or remaining is insufficient to identify the same state."
                ),
            ),
        ],
    },
    "state_definition": {
        "title": "Name the exact question each state answers",
        "body": (
            "Define a state in one sentence before choosing its representatio"
            "n. Retain every changing variable that can affect the answer, wh"
            "ile treating declared fixed input data as fixed. Distinguish pos"
            "ition from value, prefix from suffix, and capacity from items al"
            "ready used. A state key is sufficient only if equal keys always "
            "mean the same remaining subproblem."
        ),
        "questions": [
            q(
                (
                    "On a fixed list values, dp[i] means the sum of the first i entri"
                    "es. Which entries belong to dp[2]?"
                ),
                [
                    "values[0] and values[1]",
                    "values[1] and values[2]",
                    "Only values[2]",
                    "Every entry after index 2",
                ],
                0,
                (
                    "The first two entries are at indices 0 and 1. The state counts a"
                    " prefix length, not the index of an included final element."
                ),
            ),
            q(
                (
                    "A fixed list has values [5,2,7]. dp[i] means the sum of the firs"
                    "t i entries. What is dp[2]?"
                ),
                ["2", "7", "9", "14"],
                1,
                "The prefix of length two contains 5 and 2, whose sum is 7.",
            ),
            q(
                (
                    "A subproblem chooses from items starting at index i under remain"
                    "ing capacity c; item data is fixed. Which state key retains both"
                    " changing constraints?"
                ),
                ["i only", "c only", "The sum i+c", "(i,c)"],
                3,
                (
                    "Both the remaining items and available capacity affect the subpr"
                    "oblem. Their pair preserves both; the sum can collide."
                ),
            ),
            q(
                (
                    "A state dp[i] is defined as the best score using exactly the fir"
                    "st i items. Which statement correctly describes dp[0]?"
                ),
                [
                    "It uses item at index 0",
                    "It uses no items",
                    "It uses all items",
                    "It means the score is unknown forever",
                ],
                1,
                (
                    "A prefix containing zero items is empty. Its numeric boundary va"
                    "lue depends on the objective, but its meaning is no items."
                ),
            ),
            q(
                (
                    "Two path-counting queries share a fixed grid but use different r"
                    "ow and column coordinates. Why can a cache keyed only by row be "
                    "wrong?"
                ),
                [
                    "A row index cannot be an integer",
                    "A cache must always use text keys",
                    "Different columns in the same row can have different remaining path counts",
                    "Every grid cell has the same answer",
                ],
                2,
                (
                    "Omitting column merges distinct cells. A complete state key must"
                    " distinguish subproblems whose answers can differ."
                ),
            ),
            q(
                (
                    "For a fixed string s, suffix(i) counts vowels in s[i:]. What cha"
                    "nging information is sufficient to identify this subproblem?"
                ),
                [
                    "The start index i",
                    "The number of calls so far",
                    "The last character counted anywhere",
                    "The length of an unrelated string",
                ],
                0,
                (
                    "With s fixed, i identifies the entire remaining suffix. The coun"
                    "ter of past calls is not part of the question being answered."
                ),
            ),
        ],
    },
    "state_transitions": {
        "title": "Build a state only from valid predecessor states",
        "body": (
            "Translate the state meaning into cases for the last choice or ad"
            "ded element. Check that predecessor indices are valid, represent"
            " the intended smaller problem and use the right combining operat"
            "ion. Sum disjoint counts; use min or max for an optimization obj"
            "ective. An impossible predecessor must stay impossible rather th"
            "an silently becoming a zero-cost solution."
        ),
        "questions": [
            q(
                (
                    "dp[i] is the sum of the first i entries of a fixed list a, with "
                    "dp[0]=0. Which transition is correct for i≥1?"
                ),
                [
                    "dp[i]=dp[i-1]+a[i]",
                    "dp[i]=dp[i-1]+a[i-1]",
                    "dp[i]=dp[i+1]+a[i-1]",
                    "dp[i]=a[0]",
                ],
                1,
                (
                    "The newly included entry has index i-1, since dp uses prefix len"
                    "gth rather than zero-based item index."
                ),
            ),
            q(
                "What prefix totals does this transition produce?",
                ["[0, 2, 6, 7]", "[2, 4, 1]", "[0, 2, 4, 1]", "[0, 7, 7, 7]"],
                0,
                "Starting at zero, the transitions add 2, then 4, then 1: totals 2,6,7.",
                "a = [2, 4, 1]\ndp = [0]\nfor value in a:\n    dp.append(dp[-1] + value)\nprint(dp)",
                output=True,
            ),
            q(
                (
                    "cost[i] is the cost to land at stair i. best[i] is minimum total"
                    " cost to reach i from i-1 or i-2, with earlier boundaries alread"
                    "y defined. For i≥2, which transition is correct?"
                ),
                [
                    "best[i]=max(best[i-1],best[i-2])",
                    "best[i]=cost[i]+best[i-1]+best[i-2]",
                    "best[i]=cost[i]+min(best[i-1],best[i-2])",
                    "best[i]=min(cost[i-1],cost[i-2])",
                ],
                2,
                (
                    "Choose the cheaper valid predecessor, then add the landing cost."
                    " Adding both predecessor costs combines two alternative paths in"
                    "correctly."
                ),
            ),
            q(
                (
                    "ways[i] counts ordered stair paths using steps 1 or 3, with ways"
                    "[0]=1 and ways[j]=0 for j<0. Which transition counts paths by th"
                    "eir final step for i≥1?"
                ),
                [
                    "ways[i]=ways[i-1]*ways[i-3]",
                    "ways[i]=ways[i-2]+ways[i-3]",
                    "ways[i]=ways[i-1]+3",
                    "ways[i]=ways[i-1]+ways[i-3]",
                ],
                3,
                (
                    "The final step is either 1 from i-1 or 3 from i-3. The disjoint "
                    "path counts add; negative predecessors contribute zero."
                ),
            ),
            q(
                (
                    "An unreachable predecessor has cost INF, where INF exceeds every"
                    " feasible finite path cost. What should the transition do with t"
                    "hat alternative?"
                ),
                [
                    "Keep it unreachable rather than treating it as zero cost",
                    "Always choose it because INF is a boundary",
                    "Replace its cost with zero",
                    "Delete the destination state even if another predecessor is reachable",
                ],
                0,
                (
                    "An impossible route must not become a cheap candidate. Other rea"
                    "chable alternatives can still determine the destination."
                ),
            ),
            q(
                (
                    "dp[i] counts ordered paths reaching i with steps 1 or 2. Earlier"
                    " entries are already correct. Which line fixes this transition f"
                    "or i≥2?"
                ),
                [
                    "dp[i] = dp[i-1] * dp[i-2]",
                    "dp[i] = dp[i-1] + dp[i-2]",
                    "dp[i] = dp[i+1] + dp[i+2]",
                    "dp[i] = i * 2",
                ],
                1,
                (
                    "Paths ending with step 1 and step 2 are disjoint alternatives. T"
                    "heir counts must be added, not multiplied."
                ),
                "# Incorrect line inside the loop:\ndp[i] = dp[i-1] * dp[i-2]",
                bug=True,
            ),
        ],
    },
    "dp_base_cases": {
        "title": "Initialize the state meaning, including the empty case",
        "body": (
            "Boundary states encode the smallest valid subproblems. State the"
            "ir mathematical meaning: an empty sum is 0, an empty product is "
            "1, and an empty construction may count as one way. These values "
            "are not interchangeable. Keep impossible states distinct from va"
            "lid empty states. Check the smallest input before running any tr"
            "ansition."
        ),
        "questions": [
            q(
                (
                    "dp[i] is the sum of the first i list entries. What value represe"
                    "nts the empty prefix dp[0]?"
                ),
                ["1", "The first list entry", "0", "The list length"],
                2,
                "An empty prefix contains no addends, so its sum is zero.",
            ),
            q(
                (
                    "ways[n] counts ordered stair paths using steps 1 or 2. Staying a"
                    "t step 0 with no moves counts as one path. Which boundaries are "
                    "correct?"
                ),
                [
                    "ways[0]=1 and ways[1]=1",
                    "ways[0]=0 and ways[1]=0",
                    "ways[0]=0 and ways[1]=1",
                    "ways[0]=2 and ways[1]=2",
                ],
                0,
                "The stated empty path supplies ways[0]=1; exactly one one-step path supplies ways[1]=1.",
            ),
            q(
                (
                    "A minimum-coin state dp[a] is the fewest coins needed to make am"
                    "ount a; coins have positive integer values. Which initialization"
                    " distinguishes empty from impossible amounts?"
                ),
                [
                    "Set every amount to zero",
                    "Set every amount to one",
                    "Set dp[0] to INF and all others to zero",
                    "Set dp[0]=0 and all positive amounts to INF before transitions",
                ],
                3,
                (
                    "Zero amount needs zero coins. Positive amounts are not known rea"
                    "chable until transitions find actual coins."
                ),
            ),
            q(
                (
                    "A product-prefix state multiplies the first i entries. The produ"
                    "ct of no factors is defined as 1. What is dp[0]?"
                ),
                ["0", "1", "The first entry", "-1"],
                1,
                (
                    "One is the multiplicative identity; starting at zero would erase"
                    " every subsequent product."
                ),
            ),
            q(
                (
                    "In an obstacle-free grid, only moves right or down are allowed f"
                    "rom (0,0). There is exactly one empty path to the starting cell."
                    " What is paths[0][0]?"
                ),
                ["0", "The grid area", "1", "Two, one for each move direction"],
                2,
                (
                    "The state counts paths reaching the cell, not outgoing direction"
                    "s. The defined empty path gives one at the origin."
                ),
            ),
            q(
                (
                    "The DP counts strings of length n over A or B; the empty string "
                    "counts as one string. Which boundary fixes the program's smalles"
                    "t input n=0?"
                ),
                ["dp[0] = 0", "dp[0] = 1", "dp[0] = 2", "dp[0] = n + 2"],
                1,
                (
                    "The stated empty string must already be represented once before "
                    "doubling for each added symbol."
                ),
                (
                    "dp = [0] * (n + 1)\n# Fill dp[0] here.\nfor i in range(1, n + 1):\n"
                    "    dp[i] = 2 * dp[i-1]"
                ),
                bug=True,
            ),
        ],
    },
    "memoization": {
        "title": "Cache complete states before repeating their work",
        "body": (
            "In top-down evaluation, check whether a complete state is alread"
            "y cached before expanding it. On a miss, compute from valid smal"
            "ler states, store the result and return it. Test cache membershi"
            "p rather than the truthiness of a numeric result, since zero may"
            " be valid. A cache must be scoped to the fixed input data or inc"
            "lude that data in its key; do not reuse answers across different"
            " problems accidentally."
        ),
        "questions": [
            q(
                "For a pure solve(i,remaining) on fixed item data, which cache key is complete?",
                ["i", "remaining", "i+remaining", "(i,remaining)"],
                3,
                (
                    "Both changing arguments can affect the answer; a complete key mu"
                    "st distinguish their ordered pair."
                ),
            ),
            q(
                (
                    "A computed answer may be zero. Which check reliably distinguishe"
                    "s cached from uncached states?"
                ),
                ["if memo.get(key):", "if key in memo:", "if key > 0:", "if len(memo) == key:"],
                1,
                (
                    "Membership tests whether the key exists even when its stored val"
                    "ue is zero. Truthiness would incorrectly treat zero as a miss."
                ),
            ),
            q(
                (
                    "The expansion counter increases only on a cache miss. What is pr"
                    "inted after requesting the same state twice?"
                ),
                ["1", "2", "3", "0"],
                0,
                (
                    "The first request stores 25. The second finds the same key befor"
                    "e expansion, so the miss counter remains one."
                ),
                (
                    "memo = {}\nmisses = []\ndef square(n):\n    if n in memo:\n        r"
                    "eturn memo[n]\n    misses.append(n)\n    memo[n] = n * n\n    retur"
                    "n memo[n]\nsquare(5)\nsquare(5)\nprint(len(misses))"
                ),
                output=True,
            ),
            q(
                (
                    "When should a newly computed deterministic state result normally"
                    " be inserted into the cache?"
                ),
                [
                    "Only after the entire program exits",
                    "Before knowing its value, as an arbitrary zero",
                    "After its dependencies have produced the result and before returning it",
                    "Only after that state is requested a third time",
                ],
                2,
                (
                    "Store the completed result on a miss so the next identical reque"
                    "st can reuse it. A placeholder zero would be an incorrect answer"
                    "."
                ),
            ),
            q(
                (
                    "A cache keyed only by start index is reused for suffix sums of t"
                    "wo different lists. What is a valid repair?"
                ),
                [
                    "Keep every old answer because indices match",
                    (
                        "Use a fresh cache per fixed list, or include the list identity/c"
                        "ontent in a stable complete key"
                    ),
                    "Change all stored answers to zero",
                    "Use only the length of the cache as the key",
                ],
                1,
                (
                    "The fixed input changed, so equal indices may no longer identify"
                    " equal subproblems. Separate cache scope or a complete key preve"
                    "nts cross-input reuse."
                ),
            ),
            q(
                "Why does this code recompute a cached zero, and which check fixes it?",
                [
                    "Zero keys cannot be stored; use negative keys",
                    "The dictionary is immutable; replace it with a list",
                    "Python forbids zero return values; return one",
                    "Zero is falsey; test key in memo instead",
                ],
                3,
                (
                    "memo.get(key) may return the valid cached value zero. Membership"
                    " checks existence independently of that value's truthiness."
                ),
                "if memo.get(key):\n    return memo[key]\n# Otherwise compute the state again.",
                bug=True,
            ),
        ],
    },
    "tabulation": {
        "title": "Choose an order that computes dependencies first",
        "body": (
            "Bottom-up evaluation fills a table from initialized boundaries t"
            "oward larger states. For every transition, verify that each read"
            " refers to a state already computed in the chosen order. Follow "
            "dependency direction rather than assuming every table must be fi"
            "lled left-to-right. In-place updates can change the meaning of a"
            " transition; preserve the required previous-stage values or use "
            "a second row."
        ),
        "questions": [
            q(
                (
                    "dp[0] and dp[1] are initialized; dp[i]=dp[i-1]+dp[i-2] for 2≤i≤n"
                    ". Which fill order makes dependencies available?"
                ),
                [
                    "i=n down to 2",
                    "Any random order",
                    "i=2 up to n",
                    "Compute only dp[n] without earlier entries",
                ],
                2,
                (
                    "Both predecessor indices are smaller than i, so increasing order"
                    " computes them before use."
                ),
            ),
            q(
                "With the stated initialized boundaries, what is printed?",
                ["4", "5", "6", "8"],
                1,
                "The table becomes 0,1,1,2,3,5. Reading already-computed smaller indices yields dp[5]=5.",
                (
                    "dp = [0, 1, 0, 0, 0, 0]\nfor i in range(2, 6):\n    dp[i] = dp[i-1"
                    "] + dp[i-2]\nprint(dp[5])"
                ),
                output=True,
            ),
            q(
                "A suffix table has dp[n]=0 and dp[i]=a[i]+dp[i+1] for 0≤i<n. Which fill order is valid?",
                [
                    "i=n-1 down to 0",
                    "i=0 up to n-1",
                    "Only even indices",
                    "Every index simultaneously without reading dp[i+1]",
                ],
                0,
                (
                    "Each state needs the next larger index. Moving right-to-left ens"
                    "ures that suffix result has already been computed."
                ),
            ),
            q(
                (
                    "A 0/1 item has a positive integer weight and can be used at most"
                    " once. An in-place capacity update reads dp[c-weight] from befor"
                    "e this item. Which capacity order avoids using the same item rep"
                    "eatedly?"
                ),
                [
                    "Always increase c from weight",
                    "Only update c=weight",
                    "Update every c to zero first",
                    "Decrease c from the maximum capacity to weight",
                ],
                3,
                (
                    "Descending capacity leaves smaller source capacities at the prev"
                    "ious item stage during this item's updates. Increasing order can"
                    " reuse a value just updated for the same item."
                ),
            ),
            q(
                (
                    "For the recurrence dp[i]=dp[i-1]+a[i-1], which bug explains wron"
                    "g totals when filling i from n down to 1 on a fresh zero table?"
                ),
                [
                    "All tables forbid zero boundaries",
                    "It reads dp[i-1] before that state has been computed",
                    "Python cannot index lists backwards",
                    "Addition is not allowed in tabulation",
                ],
                1,
                (
                    "This recurrence depends on smaller indices; descending order rea"
                    "ds default entries instead of computed prefix totals."
                ),
            ),
            q(
                (
                    "Every table state dp[i] depends only on initialized dp[0] and pr"
                    "eviously computed dp[i-1]. What property makes an increasing bot"
                    "tom-up pass valid?"
                ),
                [
                    "The final answer must equal n",
                    "The table contains exactly two states",
                    "Every dependency is available before its state is evaluated",
                    "The code must use recursion internally",
                ],
                2,
                (
                    "A valid evaluation order respects dependencies. It does not depe"
                    "nd on the numeric answer, table size or use of recursive calls."
                ),
            ),
        ],
    },
}
