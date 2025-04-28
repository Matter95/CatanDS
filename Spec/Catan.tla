------------------------------- MODULE Catan -------------------------------
EXTENDS Integers, FiniteSets, Sequences, TLC

CONSTANT PossiblePlayers,                                             \* The set of players
         bot,                                                         \* bottom
         Lumber, Brick, Wool, Grain, Ore,                             \* Resource Types
         Monopoly, YearOfPlenty, RoadBuilding, Knight, VictoryPoint,  \* Development Cards
         ThreeToOne,                                                  \* Wharf Type
         Road, Village, City,                                         \* Building Type
         DevCard,                                                     \* Purchasable Item
         PhaseOne,PhaseTwo,                                           \* Initialization Phases
         DiceRoll, Trading, Building,                                 \* Turn Phases
         top                                                          \* top

chooseSeq(P) ==
  LET RECURSIVE helper(_)
    helper(S) ==
      IF S = {} THEN <<>>
      ELSE LET p == CHOOSE s \in S : TRUE IN
        <<p>> \o helper(S\{p})
  IN helper(P)

Players == CHOOSE 
            s \in SUBSET PossiblePlayers: 
              Cardinality(s) >= 2                     \* Players of the game
P == chooseSeq(Players)                               \* Player Order
            
RCT == {Lumber, Brick, Wool, Grain, Ore}              \* Resource Card Types         
PCT == {Monopoly, YearOfPlenty, RoadBuilding}         \* Progress Card Types
DCT == PCT \cup {Knight, VictoryPoint}                \* Development Card Types
RCP == <<19, 19, 19, 19, 19>>                         \* Resource Card Pool
DCP == <<2, 2, 2, 14, 5>>                             \* Development Card Pool
BCT == [m:0..2, yop:0..2, rb:0..2, k:0..14, vp:0..5]  \* Bought Card Types
ACT == [m:0..2, yop:0..2, rb:0..2, k:0..14]           \* Available Card Types
UCT == [k:0..14, vp:0..5]                             \* Unveiled Card Types
WT  == {ThreeToOne} \cup RCT                          \* Wharf Types
MT  == [                                              \* Map Tiles
        coords: [arr: 0..1, row: Int, col: Int], 
        res: RCT \cup {bot}, 
        n: 2..6 \cup 8..12 \cup {bot}
       ] 
W   == {                                              \* Wharfs
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 0, row |-> 0,col |-> 1], res |-> bot, n |-> bot ], 
                t2 |-> [coords |-> [arr |-> 1, row |-> 0,col |-> 2], res |-> Ore, n |-> 10  ]
              ], 
                wt |-> ThreeToOne
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 0, row |-> 0,col |-> 3], res |-> bot  , n |-> bot ], 
                t2 |-> [coords |-> [arr |-> 1, row |-> 0,col |-> 3], res |-> Wool , n |-> 2   ]
              ], 
                wt |-> Grain
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 1, row |-> 0,col |-> 5], res |-> bot  , n |-> bot ], 
                t2 |-> [coords |-> [arr |-> 0, row |-> 1,col |-> 4], res |-> Brick, n |-> 10  ]
              ], 
                wt |-> Ore
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 0, row |-> 1,col |-> 0], res |-> bot  , n |-> bot ], 
                t2 |-> [coords |-> [arr |-> 0, row |-> 1,col |-> 1], res |-> Grain, n |-> 12  ]
              ], 
                wt |-> Lumber
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 5], res |-> Ore, n |-> 8   ], 
                t2 |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 6], res |-> bot, n |-> bot ]
              ], 
                wt |-> ThreeToOne
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 0, row |-> 2,col |-> 0], res |-> bot  , n |-> bot ],
                t2 |->[coords |-> [arr |-> 0, row |-> 2,col |-> 1], res |-> Lumber, n |-> 8   ] 
              ], 
                wt |-> Brick
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 0, row |-> 2,col |-> 4], res |-> Wool , n |-> 5   ], 
                t2 |-> [coords |-> [arr |-> 1, row |-> 2,col |-> 5], res |-> bot  , n |-> bot ]
              ], 
                wt |-> Wool
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 1, row |-> 2,col |-> 2], res |-> Brick, n |-> 5   ], 
                t2 |-> [coords |-> [arr |-> 0, row |-> 3,col |-> 1], res |-> bot  , n |-> bot ]
              ], 
                wt |-> ThreeToOne
  ],
  [coords |-> [
                t1 |-> [coords |-> [arr |-> 1, row |-> 2,col |-> 3], res |-> Grain, n |-> 6   ], 
                t2 |-> [coords |-> [arr |-> 0, row |-> 3,col |-> 3], res |-> bot  , n |-> bot ]
              ], 
                wt |-> ThreeToOne
  ]
}
ST  == {Village, City}                         \* Settlement Types
BT  == {Road} \cup ST                          \* Building Types
PIT == BT \cup {DevCard}                       \* Purchasable Item Types
BP  == <<15, 5, 4>>                            \* Building Pool
IP  == {PhaseOne, PhaseTwo}                    \* Initialization Phases
TP  == {bot, DiceRoll, Trading, Building, top} \* Turn Phases
M   == {                                       \* Map
  \* Top Row of Island
  [coords |-> [arr |-> 0, row |-> 0,col |-> 1], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 0,col |-> 2], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 0,col |-> 3], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 0,col |-> 4], res |-> bot, n |-> bot],
  
  \* First Row of Island
  [coords |-> [arr |-> 1, row |-> 0,col |-> 1], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 1, row |-> 0,col |-> 2], res |-> Ore, n |-> 10],
  [coords |-> [arr |-> 1, row |-> 0,col |-> 3], res |-> Wool, n |-> 2],
  [coords |-> [arr |-> 1, row |-> 0,col |-> 4], res |-> Lumber, n |-> 9],
  [coords |-> [arr |-> 1, row |-> 0,col |-> 5], res |-> bot, n |-> bot],
  
  \* Second Row of Island
  [coords |-> [arr |-> 0, row |-> 1,col |-> 0], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 1,col |-> 1], res |-> Grain, n |-> 12],
  [coords |-> [arr |-> 0, row |-> 1,col |-> 2], res |-> Brick, n |-> 6],
  [coords |-> [arr |-> 0, row |-> 1,col |-> 3], res |-> Wool, n |-> 4],
  [coords |-> [arr |-> 0, row |-> 1,col |-> 4], res |-> Brick, n |-> 10],
  [coords |-> [arr |-> 0, row |-> 1,col |-> 5], res |-> bot, n |-> bot],
  
  \* Third Row of Island
  [coords |-> [arr |-> 1, row |-> 1,col |-> 0], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 1, row |-> 1,col |-> 1], res |-> Grain, n |-> 9],
  [coords |-> [arr |-> 1, row |-> 1,col |-> 2], res |-> Lumber, n |-> 11],
  [coords |-> [arr |-> 1, row |-> 1,col |-> 3], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 1, row |-> 1,col |-> 4], res |-> Lumber, n |-> 3],
  [coords |-> [arr |-> 1, row |-> 1,col |-> 5], res |-> Ore, n |-> 8],
  [coords |-> [arr |-> 1, row |-> 1,col |-> 6], res |-> bot, n |-> bot],
  
  \* Fourth Row of Island
  [coords |-> [arr |-> 0, row |-> 2,col |-> 0], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 2,col |-> 1], res |-> Lumber, n |-> 8],
  [coords |-> [arr |-> 0, row |-> 2,col |-> 2], res |-> Ore, n |-> 3],
  [coords |-> [arr |-> 0, row |-> 2,col |-> 3], res |-> Grain, n |-> 4],
  [coords |-> [arr |-> 0, row |-> 2,col |-> 4], res |-> Wool, n |-> 5],
  [coords |-> [arr |-> 0, row |-> 2,col |-> 5], res |-> bot, n |-> bot],
    
  \* Fifth Row of Island
  [coords |-> [arr |-> 1, row |-> 2,col |-> 1], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 1, row |-> 2,col |-> 2], res |-> Brick, n |-> 5],
  [coords |-> [arr |-> 1, row |-> 2,col |-> 3], res |-> Grain, n |-> 6],
  [coords |-> [arr |-> 1, row |-> 2,col |-> 4], res |-> Wool, n |-> 11],
  [coords |-> [arr |-> 1, row |-> 2,col |-> 5], res |-> bot, n |-> bot],
    
  \* bot Row of Island
  [coords |-> [arr |-> 0, row |-> 3,col |-> 1], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 3,col |-> 2], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 3,col |-> 3], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 3,col |-> 4], res |-> bot, n |-> bot],
  [coords |-> [arr |-> 0, row |-> 3,col |-> 5], res |-> bot, n |-> bot]
}

--------
    
isAdjacent(t1, t2) ==
  /\ t1 \in M /\ t2 \in M
  /\ LET 
    arr1   == t1.coords.arr
    row1   == t1.coords.row
    col1   == t1.coords.col
    arr2   == t2.coords.arr
    row2   == t2.coords.row
    col2   == t2.coords.col
    deltas == 
      IF arr1 = 0 
      THEN
        \* Top-left, Top-right, Left, Right, Bottom-left, Bottom-right
        {<<1, -1, 0>>, <<1, -1, 1>>, <<0, 0, -1>>, <<0, 0, 1>>, <<1, 0, 0>>,  <<1, 0, 1>>}
      ELSE
        \* Top-left, Top-right, Left, Right, Bottom-left, Bottom-right
        {<<-1, 0, -1>>, <<-1, 0, 0>>, <<0, 0, -1>>, <<0, 0, 1>>, <<-1, 1, -1>>, <<-1, 1, 0>>}
      IN 
        \E d \in deltas: arr2 = arr1 + d[1] /\ row2 = row1 + d[2] /\ col2 = col1 + d[3] 

allAdjacent(t1,t2,t3) ==
  /\ t1 \in M /\ t2 \in M /\ t3 \in M
  /\ isAdjacent(t1,t2)
  /\ isAdjacent(t1,t3)
  /\ isAdjacent(t2,t3)
    
isCenterTile(t) ==
  /\ t \in M
  /\ t.coords = [arr |-> 1, row|-> 1, col |-> 1]
    
isCoast(t1, t2) ==
  /\ t1 \in M /\ t2 \in M
  /\ ~isCenterTile(t1) /\ ~isCenterTile(t2)
  /\ \/ t1.res = bot /\ t2.res # bot
     \/t1.res # bot /\ t2.res = bot

ASSUME
  /\ M \subseteq MT \* Map is a subset of all possible map tiles 
  /\ \A t1, t2 \in M: t1.coords = t2.coords <=> t1 = t2 \* Map has no duplicate tiles
  /\ \A w \in W: w.wt \in WT /\ w.coords.t1 \in M /\ w.coords.t2 \in M \* all Wharf tiles are part of the map
  /\ \A w \in W: isAdjacent(w.coords.t1, w.coords.t2) /\ isCoast(w.coords.t1, w.coords.t2) \* All Wharfs are on a coast
  /\ Print("ASSUME", TRUE)

--------

reverse(seq) ==
  LET RECURSIVE helper(_) 
    helper(s) ==
      IF s = <<>> THEN s
      ELSE  Append(helper(Tail(s)), Head(s))
  IN helper(seq)

getIndex(el, seq) ==
  LET RECURSIVE helper(_) 
    helper(s) ==
      IF s = el THEN 0
      ELSE IF Head(s) = el
        THEN 1
        ELSE 1 + helper(Tail(s))
  IN helper(seq)

--------
       
VARIABLES I, \* Initialization State
          G  \* Game State

BNK ==                                    \* Bank 
    [
      RC:[l: 0..19, b: 0..19, w: 0..19, g: 0..19, o: 0..19], 
      DC:[m: 0..2, yop: 0..2, rb: 0..2, k: 0..14, vp: 0..5]
    ]
DP  == [m: 0..2, yop: 0..2, rb: 0..2]     \* Discard Pile
PH == [ 
        RC:[l: 0..19, b: 0..19, w: 0..19, g: 0..19, o: 0..19],
        DC:[m: 0..2, yop: 0..2, rb: 0..2, k: 0..14, vp: 0..5]
      ]    
H   == [p \in Players |-> PH] \* Hands
PB == [r: 0..15, v: 0..5, c: 0..4] 
B   == [p \in Players |-> PB] \* Buildings
S   == [                                  \* Settlement Points
         coords: {{k[1], k[2], k[3]}: k \in {t \in M \X M \X M: allAdjacent(t[1],t[2],t[3]) /\ 
         (t[1].res # bot \/ t[2].res # bot \/ t[3].res # bot)}}, 
         own: Players \cup {bot}, 
         st: ST \cup {bot}
       ] 
R   == [  \* Road Points
         coords: {{k[1], k[2]}: k \in {t \in M \X M: isAdjacent(t[1],t[2]) /\ 
         (t[1].res # bot \/ t[2].res # bot)}}, 
         own: Players \cup {bot}
       ]
         
TypeOK ==   
  /\ I \in [ip: IP, ap: Players]      \* Initialization State
\*  /\ Print("ALL", G \in [ap: Players, bnk: BNK, dp: DP, h: \A p \in Players: G.h[p] \in PH, b: \A p \in Players: G.b[p] \in PB, s: SUBSET S, r: SUBSET R, ba: M, tp: TP])
\*  /\ Print("AP", G.ap \in Players)
  /\ G.ap \in Players                 \* Game           State
\*  /\ Print("BNK", G.bnk \in BNK)
  /\ G.bnk \in BNK                    
\*  /\ Print("DP", G.dp \in DP)
  /\ G.dp \in DP
\*  /\ Print("H", \A p \in Players: G.h[p] \in PH)
  /\ \A p \in Players: G.h[p] \in PH
\*  /\ Print("B", \A p \in Players: G.b[p] \in PB)
  /\ \A p \in Players: G.b[p] \in PB
\*  /\ Print("S", G.s \subseteq S)
  /\ G.s \subseteq S
\*  /\ Print("R", G.r \subseteq R)
  /\ G.r \subseteq R
\*  /\ Print("BA", G.ba \in M)
  /\ G.ba \in M
\*  /\ Print("TP", G.tp \in TP)
  /\ G.tp \in TP

--------

isAdjacentSettlement(s1,s2) ==
  /\ s1 \in G.s 
  /\ s2 \in G.s
  /\ \E t1,t2 \in s1.coords: t1 # t2 /\ t1 \in s2.coords /\ t2 \in s2.coords
  
isAdjacentRoadToSettlement(s,r) ==
  /\ s \in G.s
  /\ r \in G.r
  /\ r.coords \subseteq s.coords
  
isAdjacentRoad(r1,r2) ==
  /\ r1 \in G.r
  /\ r2 \in G.r
  /\ \E s \in G.s: isAdjacentRoadToSettlement(s,r1) /\ isAdjacentRoadToSettlement(s,r2)
  
settlementHasNoBandit(s) ==
  /\ s \in G.s
  /\ ~G.ba \in s.coords
    
roadHasNoBandit(r) ==
  /\ r \in G.r
  /\ ~G.ba \in r.coords
    
tileHasNoBandit(t) ==
  /\ t \in M
  /\ ~G.ba # t
  
buildable(s) == 
  /\ s \in G.s
  /\ settlementHasNoBandit(s)
  /\ \A as \in G.s: isAdjacentSettlement(s,as) => as.own = bot
  
--------

InitPhaseOne ==
  /\ Print("INITPHASEONE", TRUE)
  /\ G.tp = bot
  /\ I.ip = PhaseOne
  /\ I.ap \in Players
  
  /\ \E sp \in G.s: sp.own = bot /\ buildable(sp)
    /\ \E rp \in G.r: rp.own = bot /\ isAdjacentRoadToSettlement(sp,rp) /\ roadHasNoBandit(rp)
    
    /\ G' = [G EXCEPT !.b[I.ap].r = G.b[I.ap].r - 1, \* remove 1 road
                        !.b[I.ap].v = G.b[I.ap].v - 1, \* remove 1 village
                        !.s = (G.s \ {sp}) \cup {[coords |-> sp.coords, own |-> I.ap, st |-> Village]}, \* change settlement point 
                        !.r = (G.r \ {rp}) \cup {[coords |-> rp.coords, own |-> I.ap]}] \* change road point
    /\ IF getIndex(I.ap, P) = Cardinality(Players)
            THEN 
              I' = [I EXCEPT  !.ap = reverse(P)[1], \* next player
                              !.ip = PhaseTwo]  \* next phase
            ELSE 
              I' = [I EXCEPT  !.ap = P[(getIndex(I.ap, P) + 1) % (Cardinality(Players) + 1)]] \* next player

--------  

InitPhaseTwo ==
  /\ Print("INITPHASETWO", TRUE)
  /\ G.tp = bot
  /\ I.ip = PhaseTwo
  /\ I.ap \in Players
 
  /\ \E sp \in G.s: sp.own = bot /\ buildable(sp)
    /\ \E rp \in G.r: rp.own = bot /\ isAdjacentRoadToSettlement(sp,rp) /\ roadHasNoBandit(rp)
    /\ LET gain == <<0,0,0,0,0>>
    IN
      /\ \A c \in {c \in M \X RCT: c[1] \in sp.coords /\ tileHasNoBandit(c[1]) /\ c[1].res = c[2]}: gain[getIndex(c, RCT)] = gain[getIndex(c, RCT)] + 1
      /\ I' = [I EXCEPT !.ap = reverse(P)[(getIndex(I.ap, reverse(P)) + 1) % (Cardinality(Players) + 1)]] \* next player
      /\ G' = [G EXCEPT !.bnk.RC.l = G.bnk.RC.l - gain[1],
                        !.bnk.RC.b = G.bnk.RC.b - gain[2],
                        !.bnk.RC.w = G.bnk.RC.w - gain[3],
                        !.bnk.RC.g = G.bnk.RC.g - gain[4],
                        !.bnk.RC.o = G.bnk.RC.o - gain[5],
                        !.h[I.ap].RC.l = G.h[I.ap].RC.l + gain[1], 
                        !.h[I.ap].RC.b = G.h[I.ap].RC.b + gain[2],
                        !.h[I.ap].RC.w = G.h[I.ap].RC.w + gain[3],
                        !.h[I.ap].RC.g = G.h[I.ap].RC.g + gain[4],
                        !.h[I.ap].RC.o = G.h[I.ap].RC.o + gain[5],
                        !.b[I.ap].r = G.b[I.ap].r - 1, \* remove 1 road
                        !.b[I.ap].v = G.b[I.ap].v - 1, \* remove 1 village
                        !.s = (G.s \ {sp}) \cup {[coords |-> sp.coords, own |-> I.ap, st |-> Village]},  \* change settlement point 
                        !.r = (G.r \ {rp}) \cup {[coords |-> rp.coords, own |-> I.ap]},                  \* change road point
                        !.tp = IF getIndex(I.ap, P) = Cardinality(Players) THEN DiceRoll ELSE bot              \* change turn phase
            ] 
--------

Init ==
  /\ Print("INIT", TRUE)
  /\ I = [ip |-> PhaseOne, ap |-> P[1]] \* Initialization State
  /\ G = [                              \* Game State
           ap  |-> P[1], 
           bnk |-> [
                     RC |-> [l |-> 19, b |-> 19, w |-> 19, g |-> 19, o |-> 19], 
                     DC |-> [m |-> 2, yop |-> 2, rb |-> 2, k |-> 14, vp |-> 5]
                   ],
           dp  |-> [m |-> 0, yop |-> 0, rb |-> 0],
           h   |-> [p \in Players |-> [
                      RC |-> [l |-> 0, b |-> 0, w |-> 0, g |-> 0, o |-> 0],
                      DC |-> [m |-> 0, yop |-> 0, rb |-> 0, k |-> 0, vp |-> 0]
                   ]],
           b   |-> [p \in Players |-> [r |-> 15, v |-> 5, c |-> 4]],
           s   |-> {s \in S: s.own = bot /\ s.st = bot},
           r   |-> {r \in R: r.own = bot},
           ba  |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 3], res |-> bot, n |-> bot],
           tp  |-> bot
         ]

Next == 
  \/ InitPhaseOne
  \/ InitPhaseTwo

Spec == Init /\ [][Next]_<<G, I>>

=============================================================================
\* Modification Histor
\* Last modified Wed Apr 23 17:46:25 CEST 2025 by tim_mm
\* Created Tue Apr 22 17:19:51 CEST 2025 by tim_m
