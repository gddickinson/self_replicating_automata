"""Langton's self-reproducing loop (1984): the published rule table and the standard initial loop.

Source: C. G. Langton, "Self-reproduction in cellular automata", Physica D 10 (1984) 135-144.
The 219 transitions below are the table distributed with Golly (Rules/Langtons-Loops.rule), which takes them
from H. Sayama's loops.java (http://necsi.org/postdocs/sayama/sdsr/java/loops.java; "Self-Replicating Loops & Ant,
Programmed by Eli Bachmutsky, Copyleft Feb.1999"). Each entry is CNESWC': centre, north, east, south, west and the
new centre state; the table applies in all four rotations of (N, E, S, W) (Golly's "rotate4"). A neighbourhood
with no entry leaves the cell unchanged. States 0-7; von Neumann neighbourhood.

Pure data + one helper: no numpy, matplotlib or GUI imports. Mirrored by web/static/langton_table.js.
"""

LANGTON_RULES_CNESWC = """
000000 000012 000020 000030 000050 000063 000071 000112 000122 000132 000212 000220
000230 000262 000272 000320 000525 000622 000722 001022 001120 002020 002030 002050
002125 002220 002322 005222 012321 012421 012525 012621 012721 012751 014221 014321
014421 014721 016251 017221 017255 017521 017621 017721 025271 100011 100061 100077
100111 100121 100211 100244 100277 100511 101011 101111 101244 101277 102026 102121
102211 102244 102263 102277 102327 102424 102626 102644 102677 102710 102727 105427
111121 111221 111244 111251 111261 111277 111522 112121 112221 112244 112251 112277
112321 112424 112621 112727 113221 122244 122277 122434 122547 123244 123277 124255
124267 125275 200012 200022 200042 200071 200122 200152 200212 200222 200232 200242
200250 200262 200272 200326 200423 200517 200522 200575 200722 201022 201122 201222
201422 201722 202022 202032 202052 202073 202122 202152 202212 202222 202272 202321
202422 202452 202520 202552 202622 202722 203122 203216 203226 203422 204222 205122
205212 205222 205521 205725 206222 206722 207122 207222 207422 207722 211222 211261
212222 212242 212262 212272 214222 215222 216222 217222 222272 222442 222462 222762
222772 300013 300022 300041 300076 300123 300421 300622 301021 301220 302511 401120
401220 401250 402120 402221 402326 402520 403221 500022 500215 500225 500232 500272
500520 502022 502122 502152 502220 502244 502722 512122 512220 512422 512722 600011
600021 602120 612125 612131 612225 700077 701120 701220 701250 702120 702221 702251
702321 702525 702720
""".split()

# The standard initial loop (10 rows x 14 columns; ' ' = state 0): data path of 1s with the 7-0 and 4-0 signals,
# inside a sheath of 2s, with the construction arm extending to the right along the bottom.
LANGTON_INITIAL_LOOP = [
    " 22222222",
    "2170140142",
    "2022222202",
    "272    212",
    "212    212",
    "202    212",
    "272    212",
    "21222222122222",
    "20710710711111",
    " 2222222222222",
]


def build_rule_table() -> dict:
    """(C, N, E, S, W) -> new state for all four rotations of every published rule (first entry wins)."""
    table = {}
    for rule in LANGTON_RULES_CNESWC:
        c, n, e, s, w, new = (int(ch) for ch in rule)
        nbrs = (n, e, s, w)
        for k in range(4):
            rot = nbrs[k:] + nbrs[:k]
            table.setdefault((c,) + rot, new)
    return table
