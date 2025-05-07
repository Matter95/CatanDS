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

\* Players of the game
Players == CHOOSE 
            s \in SUBSET PossiblePlayers: 
              Cardinality(s) >= 2                     
\* Player Order
P == chooseSeq(Players)                               
\* Resource Card Types
RCT == {Lumber, Brick, Wool, Grain, Ore}
RCTMAP == [Lumber |-> Lumber, Brick |-> Brick, Wool |-> Wool, Grain |-> Grain, Ore |-> Ore]
RCTST == <<"Lumber", "Brick", "Wool", "Grain", "Ore">>   
\* Progress Card Types
PCT == {Monopoly, YearOfPlenty, RoadBuilding}
PCTMAP == [Monopoly |-> "Monopoly", YearOfPlenty |-> "YearOfPlenty", RoadBuilding |-> "RoadBuilding"]
PCTST == <<"Monopoly", "YearOfPlenty", "RoadBuilding">>
\* Development Card Types
DCT == PCT \cup {Knight, VictoryPoint}                
\* Resource Card Pool
RCP == <<19, 19, 19, 19, 19>>                         
\* Development Card Pool
DCP == <<2, 2, 2, 14, 5>>                             
\* Bought Card Types
BCT == [Monopoly: 0..2, YearOfPlenty: 0..2, RoadBuilding: 0..2, Knight: 0..14]  
\* Available Card Types
ACT == [Monopoly: 0..2, YearOfPlenty: 0..2, RoadBuilding: 0..2, Knight: 0..14]           
\* Unveiled Card Types
UCT == [Knight: 0..14, VictoryPoint: 0..5]                             
\* Wharf Types
WT  == {ThreeToOne} \cup RCT                          
\* Map Tiles
MT  == [                                              
        coords: [arr: 0..1, row: Int, col: Int], 
        res: RCT \cup {bot}, 
        n: 2..6 \cup 8..12 \cup {bot}
       ]

\* Wharfs
W   == {
  [coords |-> {
                [coords |-> [arr |-> 0, row |-> 0,col |-> 1], res |-> bot, n |-> bot ], 
                [coords |-> [arr |-> 1, row |-> 0,col |-> 2], res |-> Ore, n |-> 10  ]
              }, 
              wt |-> ThreeToOne
  ],
  [coords |-> {
                [coords |-> [arr |-> 0, row |-> 0,col |-> 3], res |-> bot  , n |-> bot ], 
                [coords |-> [arr |-> 1, row |-> 0,col |-> 3], res |-> Wool , n |-> 2   ]
              }, 
              wt |-> Grain
  ],
  [coords |-> {
                [coords |-> [arr |-> 1, row |-> 0,col |-> 5], res |-> bot  , n |-> bot ], 
                [coords |-> [arr |-> 0, row |-> 1,col |-> 4], res |-> Brick, n |-> 10  ]
              }, 
              wt |-> Ore
  ],
  [coords |-> {
                [coords |-> [arr |-> 0, row |-> 1,col |-> 0], res |-> bot  , n |-> bot ], 
                [coords |-> [arr |-> 0, row |-> 1,col |-> 1], res |-> Grain, n |-> 12  ]
              }, 
              wt |-> Lumber
  ],
  [coords |-> {
                [coords |-> [arr |-> 1, row |-> 1,col |-> 5], res |-> Ore, n |-> 8   ], 
                [coords |-> [arr |-> 1, row |-> 1,col |-> 6], res |-> bot, n |-> bot ]
              }, 
              wt |-> ThreeToOne
  ],
  [coords |-> {
                [coords |-> [arr |-> 0, row |-> 2,col |-> 0], res |-> bot  , n |-> bot ],
                [coords |-> [arr |-> 0, row |-> 2,col |-> 1], res |-> Lumber, n |-> 8   ] 
              }, 
              wt |-> Brick
  ],
  [coords |-> {
                [coords |-> [arr |-> 0, row |-> 2,col |-> 4], res |-> Wool , n |-> 5   ], 
                [coords |-> [arr |-> 1, row |-> 2,col |-> 5], res |-> bot  , n |-> bot ]
              }, 
              wt |-> Wool
  ],
  [coords |-> {
                [coords |-> [arr |-> 1, row |-> 2,col |-> 2], res |-> Brick, n |-> 5   ], 
                [coords |-> [arr |-> 0, row |-> 3,col |-> 1], res |-> bot  , n |-> bot ]
              }, 
              wt |-> ThreeToOne
  ],
  [coords |-> {
                [coords |-> [arr |-> 1, row |-> 2,col |-> 3], res |-> Grain, n |-> 6   ], 
                [coords |-> [arr |-> 0, row |-> 3,col |-> 3], res |-> bot  , n |-> bot ]
              }, 
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
    
  \* Bottom Row of Island
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

\* All viable coordinate triplets
CT == {{k[1], k[2], k[3]}: k \in {t \in M \X M \X M: 
        allAdjacent(t[1],t[2],t[3]) /\ (t[1].res # bot \/ t[2].res # bot \/ t[3].res # bot)}} 
\* All viable coordinate pairs
CD == {{k[1], k[2]}: k \in {t \in M \X M \X M: 
        isAdjacent(t[1],t[2]) /\ (t[1].res # bot \/ t[2].res # bot)}}

ASSUME
  \* Map is a subset of all possible map tiles
  /\ M \subseteq MT  
  \* Map has no duplicate tiles
  /\ \A t1, t2 \in M: t1.coords = t2.coords <=> t1 = t2 
  \* all Wharf tiles are part of the map
  /\ \A w \in W: w.wt \in WT /\ \A t \in w.coords: t \in M 
  \* All Wharfs are on the coast
  /\ \A w \in W: \E t1, t2 \in w.coords: isAdjacent(t1, t2) /\ isCoast(t1, t2) 

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

SumFunc(func) == 
  LET RECURSIVE helper(_,_)
    helper(f,D) ==
      IF D = {} THEN 0 
        ELSE LET d == CHOOSE e \in D: TRUE
             IN f[d] + helper(f, D\{d})
   IN helper(func, DOMAIN func)

AddRec(rec1, rec2) == [i \in DOMAIN rec1 |-> rec1[i] + rec2[i]]
SubRec(rec1, rec2) == [i \in DOMAIN rec1 |-> rec1[i] - rec2[i]]  
AddRecEl(rec1, d, n) == [i \in DOMAIN rec1 |-> IF i = d THEN rec1[i] + n ELSE rec1[i]]    

SumResFunc(func) == 
  LET RECURSIVE helper(_,_)
    helper(f,D) ==
      IF D = {} THEN [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]
        ELSE LET c == CHOOSE c \in D: TRUE
          IN 
            IF c.res = Lumber     THEN AddRecEl(helper(f, D\{c}), "Lumber", f[c])
            ELSE IF c.res = Brick THEN AddRecEl(helper(f, D\{c}), "Brick",  f[c])  
            ELSE IF c.res = Wool  THEN AddRecEl(helper(f, D\{c}), "Wool",   f[c])
            ELSE IF c.res = Grain THEN AddRecEl(helper(f, D\{c}), "Grain",  f[c])
            ELSE IF c.res = Ore   THEN AddRecEl(helper(f, D\{c}), "Ore",    f[c])
            ELSE AddRecEl(helper(f, D\{c}), Lumber, 0)
   IN helper(func, DOMAIN func)

SumResRecs(func) == 
  LET RECURSIVE helper(_,_)
    helper(f,D) ==
      IF D = {} THEN [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0] 
        ELSE LET d == CHOOSE e \in D: TRUE
             IN AddRec(f[d], helper(f, D\{d}))
   IN helper(func, DOMAIN func)

IterateRec(rec) == [d \in DOMAIN rec |-> (rec)[d]]

--------
       
VARIABLES I, \* Initialization State
          G  \* Game State
\* Bank
BNK ==                                     
    [
      RC:[Lumber: 0..19, Brick: 0..19, Wool: 0..19, Grain: 0..19, Ore: 0..19], 
      DC:[Monopoly: 0..2, YearOfPlenty: 0..2, RoadBuilding: 0..2, Knight: 0..14, VictoryPoint: 0..5]
    ]
\* Discard Pile
DP == [Monopoly: 0..2, YearOfPlenty: 0..2, RoadBuilding: 0..2]     
PH == [
        RC:[Lumber: 0..19, Brick: 0..19, Wool: 0..19, Grain: 0..19, Ore: 0..19],
        DC:[BC: BCT,
            AC: ACT,
            UC: UCT
           ]
      ]
\* Hands      
H   == [Players -> PH] 
\* Player Buildings
PB == [Road: 0..15, Village: 0..5, City: 0..4] 
\* Buildings
B   == [Players -> PB] 
\* Settlement Points
S   == [CT -> [own: Players \cup {bot}, st: ST \cup {bot}]]       
\* Road Points 
R   == [CD -> [own: Players \cup {bot}]]
         
TypeOK ==   
  \* Initialization State
  /\ I \in [ip: IP, ap: Players]      
  \* Game State
  /\ G \in [ap: Players, bnk: BNK, dp: DP, h: H, b: B, s: S, r: R, ba: M, tp: TP]

--------

isAdjacentSettlement(s1,s2) ==
  /\ s1 \in DOMAIN G.s 
  /\ s2 \in DOMAIN G.s
  /\ \E t1,t2 \in s1: t1 # t2 /\ t1 \in s2/\ t2 \in s2
  
isAdjacentRoadToSettlement(s,r) ==
  /\ s \in DOMAIN G.s
  /\ r \in DOMAIN G.r
  /\ r \subseteq s
  
isAdjacentRoad(r1,r2) ==
  /\ r1 \in DOMAIN G.r
  /\ r2 \in DOMAIN G.r
  /\ \E s \in DOMAIN G.s: isAdjacentRoadToSettlement(s,r1) /\ isAdjacentRoadToSettlement(s,r2)
  
settlementHasNoBandit(s) ==
  /\ s \in DOMAIN G.s
  /\ ~G.ba \in s
    
roadHasNoBandit(r) ==
  /\ r \in DOMAIN G.r
  /\ ~G.ba \in r
    
tileHasNoBandit(t) ==
  /\ t \in M
  /\ ~G.ba # t
  
buildable(s) == 
  /\ s \in DOMAIN G.s
  /\ settlementHasNoBandit(s)
  /\ \A as \in DOMAIN G.s: isAdjacentSettlement(s,as) => G.s[as].own = bot
  
--------

InitPhaseOne ==
  /\ G.tp = bot
  /\ I.ip = PhaseOne
  /\ I.ap \in Players
  \* choose where to settle with a village
  /\ \E sp \in DOMAIN G.s: G.s[sp].own = bot /\ buildable(sp)
    \* choose a road adjacent to the chosen settlement
    /\ \E rp \in DOMAIN G.r: G.r[rp].own = bot /\ isAdjacentRoadToSettlement(sp,rp) /\ roadHasNoBandit(rp)
    
    /\ G' = [G EXCEPT !.b[I.ap].Road    = G.b[I.ap].Road    - 1,
                      !.b[I.ap].Village = G.b[I.ap].Village - 1,
                      !.s[sp] = [own |-> I.ap, st |-> Village], 
                      !.r[rp] = [own |-> I.ap]
            ]
    /\ IF getIndex(I.ap, P) = Cardinality(Players)
            THEN 
              I' = [I EXCEPT  !.ap = reverse(P)[1],
                              !.ip = PhaseTwo
                   ]
            ELSE 
              I' = [I EXCEPT  !.ap = P[(getIndex(I.ap, P) + 1) % (Cardinality(Players) + 1)]]

InitPhaseTwo ==
  /\ G.tp = bot
  /\ I.ip = PhaseTwo
  /\ I.ap \in Players
  \* choose where to settle with the second village
  /\ \E sp \in DOMAIN G.s: G.s[sp].own = bot /\ buildable(sp)
    \* choose a road adjacent to the chosen settlement
    /\ \E rp \in DOMAIN G.r: G.r[rp].own = bot /\ isAdjacentRoadToSettlement(sp,rp) /\ roadHasNoBandit(rp)
      /\ I' = [I EXCEPT !.ap = IF getIndex(I.ap, reverse(P)) = Cardinality(Players) THEN @
                               ELSE reverse(P)[(getIndex(I.ap, reverse(P)) + 1) % (Cardinality(Players) + 1)]]
      \* receive resources from adjacent tiles to chosen settlement
      /\ LET gain == SumResFunc([c \in {s \in sp: s.res # bot} |-> 1])
         IN G' = [G EXCEPT !.h[I.ap].RC = gain,
                           !.bnk.RC     = SubRec(@, gain),
                           !.b[I.ap].Road    = @ - 1,
                           !.b[I.ap].Village = @ - 1,
                           !.s[sp] = [own |-> I.ap, st |-> Village], 
                           !.r[rp] = [own |-> I.ap],
                           !.tp = IF getIndex(I.ap, reverse(P)) = Cardinality(Players) THEN DiceRoll ELSE bot  
                  ] 
--------
  
hasSettlementOnTile(t,p) ==
  /\ \E s \in DOMAIN G.s: G.s[s].own = p
    /\ t \in s
    
BanditMoves == {t \in M: t # G.ba /\ t.res = bot => isCenterTile(t)}

SumResourcesSinglePlayer(p) == SumFunc(IterateRec(G.h[p].RC))

SumResourceAllPlayers(rct) == SumFunc([p \in Players |-> (G.h[p].RC)[rct]])

ResourceGainPlayer(p,d) ==
  LET 
    V == {s \in UNION {sp \in DOMAIN G.s: G.s[sp].own # bot /\ G.s[sp].st = Village}: s.n = d} 
    C == {s \in UNION {sp \in DOMAIN G.s: G.s[sp].own # bot /\ G.s[sp].st = City}: s.n = d}
  IN
    SumResFunc([c \in (V \cup C) |-> IF c \in C THEN 2 ELSE 1])

\* NOTE: I wanted this to be the set of all possible loss choices for all players, but could not find the correct notation
\* example: p2 less than 8 cards, p1 |-> [Lumber |-> 4, Brick |-> 4, Wool |-> 0, Grain |-> 0, Ore |-> 0]
\* what I got: 
\*             { p1 :> {[Lumber |-> 4, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0],
\*                      [Lumber |-> 3, Brick |-> 1, Wool |-> 0, Grain |-> 0, Ore |-> 0],
\*                      [Lumber |-> 2, Brick |-> 2, Wool |-> 0, Grain |-> 0, Ore |-> 0],
\*                      [Lumber |-> 1, Brick |-> 3, Wool |-> 0, Grain |-> 0, Ore |-> 0],
\*                      [Lumber |-> 0, Brick |-> 4, Wool |-> 0, Grain |-> 0, Ore |-> 0]
\*                      } @@
\*               p2 :> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]
\*             }
\* what I wanted: 
\*             {{ p1 :> [Lumber |-> 4, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0] @@
\*                p2 :> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]},
\*                p1 :> [Lumber |-> 3, Brick |-> 1, Wool |-> 0, Grain |-> 0, Ore |-> 0] @@
\*                p2 :> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]},
\*                p1 :> [Lumber |-> 2, Brick |-> 2, Wool |-> 0, Grain |-> 0, Ore |-> 0] @@
\*                p2 :> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]},
\*                p1 :> [Lumber |-> 1, Brick |-> 3, Wool |-> 0, Grain |-> 0, Ore |-> 0] @@
\*                p2 :> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]},
\*                p1 :> [Lumber |-> 0, Brick |-> 4, Wool |-> 0, Grain |-> 0, Ore |-> 0] @@
\*                p2 :> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]}
\*             }
\* Now I just pick one of the possible elements in all p with CHOOSE ending with a single choice per player

ResourceLossChoices == 
  [p \in Players |-> IF SumResourcesSinglePlayer(p) <= 7 
  THEN [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0]
  ELSE CHOOSE l \in [Lumber:  0..G.h[p].RC.Lumber, 
                     Brick:   0..G.h[p].RC.Brick, 
                     Wool:    0..G.h[p].RC.Wool, 
                     Grain:   0..G.h[p].RC.Grain, 
                     Ore:     0..G.h[p].RC.Ore
                    ]: SumFunc(IterateRec(l)) = SumResourcesSinglePlayer(p) \div 2]

--------
DiceRollPhase ==
  /\  G.tp = DiceRoll
  /\  \E d \in 1..12: IF d = 7
    THEN 
    LET loss == ResourceLossChoices
    IN
      \* choose a tile to move the bandit to
      \E t \in BanditMoves: \E q \in Players: q # G.ap /\ hasSettlementOnTile(t,q) /\
        \* random resource from adjacent player of t
        \E res \in DOMAIN G.bnk.RC: G.h[q].RC[res] >= 0
          /\ G' = [G EXCEPT !.bnk.RC = AddRec(@, SumResRecs(loss)),
                            !.h = [p \in Players |-> 
                                     \* Can steal resource from player (even after loosing resources)
                                    [RC |-> IF G.h[q].RC[res] - loss[q][res] > 0 
                                            THEN IF p = G.ap THEN AddRecEl(SubRec(G.h[p].RC, loss[p]), res, 1)
                                                 ELSE IF p = q THEN AddRecEl(SubRec(G.h[p].RC, loss[p]), res, -1)
                                                 ELSE SubRec(G.h[p].RC, loss[p])
                                            ELSE SubRec(G.h[p].RC, loss[p]),
                                     \* Move bought cards to available cards
                                     DC |-> [BC |-> [Monopoly|-> 0, YearOfPlenty|-> 0, RoadBuilding|-> 0, Knight|-> 0],
                                             AC |-> AddRec(G.h[p].DC.AC, G.h[p].DC.BC),
                                             UC |-> G.h[p].DC.UC
                                            ]
                                    ]
                                  ],
                            !.ba = t,
                            !.tp = Trading
                  ]
          /\ UNCHANGED(I)
    ELSE
    LET
      \* resource gain for all players given the current dice roll
      gain == [p \in Players |-> ResourceGainPlayer(p,d)]
    IN
      \* if bank does not have all the resources, do not change state and continue (otherwise will violate typeOK)
      /\ IF \A res \in DOMAIN G.bnk.RC: G.bnk.RC[res] >= SumResRecs(gain)[res]
         THEN 
           /\ G' = [G EXCEPT !.bnk.RC = SubRec(@, SumResRecs(gain)),
                             !.h = [p \in Players |-> 
                                     [RC |-> AddRec(G.h[p].RC, gain[p]), 
                                      \* Move bought cards to available cards
                                      DC |-> [BC |-> [Monopoly|-> 0, YearOfPlenty|-> 0, RoadBuilding|-> 0, Knight|-> 0],
                                              AC |-> AddRec(G.h[p].DC.AC, G.h[p].DC.BC),
                                              UC |-> G.h[p].DC.UC
                                             ]
                                     ]
                                   ],
                             !.tp = Trading
                   ]
           /\ UNCHANGED(I)
         ELSE
           /\ UNCHANGED<<I,G>>
       
--------

PlayerPorts(p) == {w \in W: \E sp \in DOMAIN G.s: w.coords \subseteq sp /\ G.s[sp].own = p} 

--------
     
EmptyTrade ==
  /\ G.tp = Trading
  /\ G' = [G EXCEPT !.tp = Building]
  /\ UNCHANGED(I)

TradeFourToOne ==
  /\ G.tp = Trading
  \* choose a resource to trade with
  /\ \E give \in {res \in DOMAIN G.bnk.RC: G.h[G.ap].RC[res] >= 4}:
       \* choose a resource to trade for
       \E receive \in {res \in DOMAIN G.bnk.RC: G.bnk.RC[res] > 0}:
         /\ G' = [G EXCEPT !.bnk.RC = AddRecEl(AddRecEl(@, give, 4), receive, -1),
                           !.h[G.ap].RC = AddRecEl(AddRecEl(@, give, -4), receive, 1)
                 ]
         /\ UNCHANGED(I)
  
TradeThreeToOne ==
  /\ G.tp = Trading
  \* choose a resource to trade with (needs 3:1 port)
  /\ \E give \in {res \in DOMAIN G.bnk.RC: G.h[G.ap].RC[res] >= 3 /\ \E w \in PlayerPorts(G.ap): w.wt = ThreeToOne}:
       \* choose a resource to trade for
       \E receive \in {res \in DOMAIN G.bnk.RC: G.bnk.RC[res] > 0}:
         /\ G' = [G EXCEPT !.bnk.RC = AddRecEl(AddRecEl(@, give, 3), receive, -1),
                           !.h[G.ap].RC = AddRecEl(AddRecEl(@, give, -3), receive, 1)
                 ]
         /\ UNCHANGED(I)
TradeTwoToOne ==
  /\ G.tp = Trading
  \* choose a resource to trade with (needs specific 2:1 port)
  /\ \E give \in {rct \in DOMAIN G.bnk.RC: G.h[G.ap].RC[rct] >= 2 /\ \E w \in PlayerPorts(G.ap): w.wt \in RCT  /\ w.wt = RCTMAP[rct]}:
       \* choose a resource to trade for
       \E receive \in {rct \in DOMAIN G.bnk.RC: G.bnk.RC[rct] > 0}:
         /\ G' = [G EXCEPT !.bnk.RC = AddRecEl(AddRecEl(@, give, 2), receive, -1),
                           !.h[G.ap].RC = AddRecEl(AddRecEl(@, give, -2), receive, 1)
                 ]
         /\ UNCHANGED(I)

--------

RoadCost    == [Lumber |-> 1, Brick |-> 1, Wool |-> 0, Grain |-> 0, Ore |-> 0]
VillageCost == [Lumber |-> 1, Brick |-> 1, Wool |-> 1, Grain |-> 1, Ore |-> 0]
CityCost    == [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 2, Ore |-> 3]
DevCardCost == [Lumber |-> 0, Brick |-> 0, Wool |-> 1, Grain |-> 1, Ore |-> 1]

CanBuildRoad ==
  \* Player has the needed resources and game pieces
  /\ \A res \in DOMAIN RoadCost: G.h[G.ap].RC[res] >= RoadCost[res]
  /\ G.b[G.ap].Road > 0

CanBuildVillage ==
  \* Player has the needed resources and game pieces
  /\ \A res \in DOMAIN VillageCost: G.h[G.ap].RC[res] >= VillageCost[res]
  /\ G.b[G.ap].Village > 0

CanBuildCity ==
  \* Player has the needed resources and game pieces
  /\ \A res \in DOMAIN CityCost: G.h[G.ap].RC[res] >= CityCost[res]
  /\ G.b[G.ap].City > 0

CanBuyDevCard ==
  \* Player has the needed resources and bank still has cards
  /\ \A res \in DOMAIN DevCardCost: G.h[G.ap].RC[res] >= DevCardCost[res]
  /\ SumFunc(IterateRec(G.bnk.DC)) > 0

RoadsOnMap == {rp \in DOMAIN G.r: G.r[rp].own # bot}
PlayerRoadsOnMap(p) == {rp \in DOMAIN G.r: G.r[rp].own = p}
AllRoadSets == [p \in Players |-> {s \in SUBSET PlayerRoadsOnMap(p): Cardinality(s) >= 5}]
isPath(seq) ==
  /\ \A i \in 1..(Len(seq) - 1): 
    /\ seq[i] \in RoadsOnMap 
    /\ seq[i+1] \in RoadsOnMap 
    /\ isAdjacentRoad(seq[i], seq[i+1])
  /\ \A i, j \in DOMAIN seq: i # j => seq[i] # seq[j]  /\ G.r[seq[i]].own = G.r[seq[j]].own

Max(set) == CHOOSE el \in set: \A n \in set: el >= n 

AllPaths == [p \in Players |->{Cardinality(r): r \in {rt \in AllRoadSets[p]: rt # {} /\ isPath(chooseSeq(rt))}}]

PlayerPoints(p) == 
  LET 
    \* All Villages and Cities owned by this player
    V == {sp \in DOMAIN G.s: G.s[sp].own = p /\ G.s[sp].st = Village} 
    C == {sp \in DOMAIN G.s: G.s[sp].own = p /\ G.s[sp].st = City}
    \* Player with the most Knights (threshold at least 3) gets 2 points
    MightiestArmy == IF G.h[p].DC.UC.Knight >= 3 /\ \A q \in Players: q # p /\ G.h[p].DC.UC.Knight >= G.h[q].DC.UC.Knight
                     THEN 2 
                     ELSE 0
    \* Player with the longest road (threshold at least 5) gets 2 points
    LongestRoad == IF Cardinality(AllPaths[G.ap]) > 0 /\ Max(AllPaths[G.ap]) > 5 /\ \A q \in Players: q # p /\ Max(AllPaths[G.ap]) >= Max(AllPaths[q])
                   THEN 2
                   ELSE 0
  IN
    SumFunc([c \in (V \cup C) |-> IF c \in C THEN 2 ELSE 1]) + G.h[p].DC.UC.VictoryPoint + MightiestArmy + LongestRoad

--------
     
EmptyBuild ==
  /\ G.tp = Building
  \* check if a player has enough points to win the game, if not continue
  /\ G' = [G EXCEPT !.tp = IF PlayerPoints(G.ap) >= 10 THEN top ELSE DiceRoll]
  /\ UNCHANGED(I)

BuildRoad ==
  /\ G.tp = Building
  /\ CanBuildRoad
  \* choose a road
  /\ \E rp \in DOMAIN G.r: G.r[rp].own = bot /\ roadHasNoBandit(rp) /\ 
      \* either there is an adjacent road or settlement, owned by the player
      (\E rpt \in DOMAIN G.r: (isAdjacentRoad(rp, rpt) /\ G.r[rpt].own = G.ap) \/ 
       \E sp \in DOMAIN G.s: G.s[sp].own = G.ap /\ isAdjacentRoadToSettlement(sp, rp)) 
    /\ G' = [G EXCEPT !.bnk.RC = AddRec(@, RoadCost),
                      !.h[G.ap].RC = SubRec(@, RoadCost),
                      !.b[G.ap].Road = @ - 1,
                      !.r[rp] = [own |-> G.ap]
            ]
    /\ UNCHANGED(I)
    
BuildVillage ==
  /\ G.tp = Building
  /\ CanBuildVillage
  \* choose a space for a village
  /\ \E sp \in DOMAIN G.s: G.s[sp].own = bot /\ buildable(sp) /\
     \* there is an adjacent road owned by the player
     \E rp \in DOMAIN G.r: G.r[rp].own = G.ap /\ isAdjacentRoadToSettlement(sp, rp)
    /\ G' = [G EXCEPT !.bnk.RC = AddRec(@, VillageCost),
                      !.h[G.ap].RC = SubRec(@, VillageCost), 
                      !.b[G.ap].Village = @ - 1,
                      !.s[sp] = [own |-> G.ap, st |-> Village]
            ]
    /\ UNCHANGED(I)

BuildCity ==
  /\ G.tp = Building
  /\ CanBuildCity
  \* choose a village to upgrade
  /\ \E sp \in DOMAIN G.s: G.s[sp].own = G.ap /\ G.s[sp].st = Village /\
     settlementHasNoBandit(sp)
    /\ G' = [G EXCEPT !.bnk.RC = AddRec(@, CityCost),
                      !.h[G.ap].RC = SubRec(@, CityCost), 
                      !.b[G.ap].Village = @ + 1,
                      !.b[G.ap].City = @ - 1,
                      !.s[sp] = [own |-> G.ap, st |-> City]
            ]
    /\ UNCHANGED(I)
    
BuyDevCard ==
  /\ G.tp = Building
  /\ CanBuyDevCard
  \* randomly get a development card, Victory Points are instantly revealed
  /\ \E dc \in DOMAIN G.bnk.DC: G.bnk.DC[dc] > 0
    /\ G' = [G EXCEPT !.bnk.RC = AddRec(@, DevCardCost),
                      !.h[G.ap].RC = SubRec(@, DevCardCost), 
                      !.bnk.DC = AddRecEl(@, dc, -1),
                      !.h[G.ap].DC = IF dc = "VictoryPoint" 
                                     THEN [BC |-> @.BC, 
                                           AC |-> @.AC, 
                                           UC |-> AddRecEl(@.UC, dc, 1)
                                          ]
                                     ELSE [BC |-> AddRecEl(@.BC, dc, 1), 
                                           AC |-> @.AC, 
                                           UC |-> @.UC
                                          ]
            ]
    /\ UNCHANGED(I)
    
--------

\* Monopoly card steals all cards of a chosen resource in the hand of other players. 
\* The card is put into the discard pile after playing.
PlayMonopoly ==
  /\ \E res \in DOMAIN G.bnk.RC:
    LET gain == SumResourceAllPlayers(res)
    IN
      G' = [G EXCEPT !.dp.Monopoly = @ + 1,
                     !.h = [p \in Players |-> 
                              \* Monopolize one resource from all players 
                              [RC |-> IF p = G.ap THEN AddRecEl(G.h[p].RC, res, (gain - G.h[p].RC[res]))
                                      ELSE AddRecEl(G.h[p].RC, res, -G.h[p].RC[res]),
                                      \* Move bought cards to available cards
                               DC |-> IF p = G.ap 
                                      THEN [BC |-> G.h[p].DC.BC,
                                            AC |-> AddRecEl(G.h[p].DC.AC, "Monopoly", -1),
                                            UC |-> G.h[p].DC.UC
                                           ]
                                      ELSE G.h[p].DC
                              ]
                           ]
            ]
  /\ UNCHANGED(I) 

\* Year of plenty lets the player choose two resource cards to receive. Put onto the discard pile after playing.
PlayYearOfPlenty ==
  \E res1 \in DOMAIN G.bnk.RC: G.bnk.RC[res1] > 0 /\
    \E res2 \in DOMAIN G.bnk.RC: G.bnk.RC[res2] > 0
      /\ G' = [G EXCEPT !.bnk.RC = AddRecEl(AddRecEl(@, res1, -1), res2, -1),
                        !.h[G.ap].RC = AddRecEl(AddRecEl(@, res1, 1), res2, 1),
                        !.h[G.ap].DC.AC.YearOfPlenty = @ - 1,
                        !.dp.YearOfPlenty = @ + 1
              ]
      /\ UNCHANGED(I) 

\* The player can place two roads onto the map without paying. Put onto the discard pile after playing.
PlayRoadBuilding ==
  /\ G.b[G.ap].Road >= 2
  /\ \E rp1 \in DOMAIN G.r: G.r[rp1].own = bot /\ roadHasNoBandit(rp1) /\ 
       \* Adjacent to a road the player owns
       (\E rpt \in DOMAIN G.r: (isAdjacentRoad(rp1, rpt) /\ G.r[rpt].own = G.ap) \/ 
        \* Adjacent to a settlement the player owns
        \E sp \in DOMAIN G.s: G.s[sp].own = G.ap /\ isAdjacentRoadToSettlement(sp, rp1))
     /\ \E rp2 \in DOMAIN G.r: G.r[rp2].own = bot /\ rp1 # rp2 /\ roadHasNoBandit(rp2) /\
         \* Adjacent to the newly built road
         (isAdjacentRoad(rp1, rp2) \/ 
          \* Adjacent to a road the player owns
          \E rpt \in DOMAIN G.r: (isAdjacentRoad(rp2, rpt) /\ G.r[rpt].own = G.ap) \/ 
          \* Adjacent to a settlement the player owns
          \E sp \in DOMAIN G.s: G.s[sp].own = G.ap /\ isAdjacentRoadToSettlement(sp, rp2))
            /\ G' = [G EXCEPT !.h[G.ap].DC.AC.RoadBuilding = @ - 1,
                              !.dp.RoadBuilding = @ + 1,
                              !.b[G.ap].Road = @ - 2,
                              !.r[rp1] = [own |-> G.ap],
                              !.r[rp2] = [own |-> G.ap]
                    ]
            /\ UNCHANGED(I)
            
\* Move the bandit and steal a resource if another player is adjacent to the robbers field. 
\* Knight cards are unveiled after activation and work towards the mightiest army points.            
PlayKnight ==
  \E t \in BanditMoves: \E q \in Players: q # G.ap /\ hasSettlementOnTile(t,q) /\
    \* random resource from adjacent player of t
    \E res \in DOMAIN G.bnk.RC: G.h[q].RC[res] >= 0 /\
      \* Can steal resource from player
      IF G.h[q].RC[res] > 0
      THEN 
        /\ G' = [G EXCEPT !.h[G.ap].RC = AddRecEl(G.h[G.ap].RC, res, 1),
                          !.h[q].RC    = AddRecEl(G.h[q].RC, res, -1),
                          !.h[G.ap].DC.AC.Knight = @ - 1,
                          !.h[G.ap].DC.UC.Knight = @ + 1,
                          !.ba = t
              ]
        /\ UNCHANGED(I)
      ELSE
        /\ G' = [G EXCEPT !.h[G.ap].DC.AC.Knight = @ - 1,
                          !.h[G.ap].DC.UC.Knight = @ + 1,
                          !.ba = t
                ]
        /\ UNCHANGED(I)

\* Play a card in the Available Card set of a players hand 
PlayDevCard == 
  /\ G.tp \in {Trading, Building}
  /\ \E dc \in DOMAIN G.h[G.ap].DC.AC: G.h[G.ap].DC.AC[dc] > 0 /\
    IF dc = "Monopoly" THEN UNCHANGED<<G,I>> \*PlayMonopoly
    ELSE IF dc = "YearOfPlenty" THEN UNCHANGED<<G,I>> \*PlayYearOfPlenty
    ELSE IF dc = "RoadBuilding" THEN UNCHANGED<<G,I>> \*PlayRoadBuilding
    ELSE UNCHANGED<<G,I>> \*PlayKnight

--------

NrPlayerRoadsOnMap(p) == SumFunc([d \in DOMAIN G.r |-> IF G.r[d].own = p THEN 1 ELSE 0])

NrPlayerSettlementOnMap(p, st) == SumFunc([d \in DOMAIN G.s |-> IF G.s[d].own = p /\ G.s[d].st = st THEN 1 ELSE 0])

SumDevelopmentAllPlayers(dct) == 
  IF dct \in DOMAIN G.dp
  THEN SumFunc([p \in Players |-> (G.h[p].DC.BC)[dct]]) + 
         SumFunc([p \in Players |-> (G.h[p].DC.AC)[dct]])
  ELSE IF dct = "Knight"
  THEN SumFunc([p \in Players |-> (G.h[p].DC.BC)[dct]]) + 
         SumFunc([p \in Players |-> (G.h[p].DC.AC)[dct]]) + 
         SumFunc([p \in Players |-> (G.h[p].DC.UC)[dct]])
  ELSE SumFunc([p \in Players |-> (G.h[p].DC.UC)[dct]])

--------

ConservationOfResourceCards == 
  /\ \A rct \in DOMAIN G.bnk.RC: SumResourceAllPlayers(rct) + G.bnk.RC[rct] = RCP[getIndex(rct, RCTST)]
  
ConservationOfBuildings ==
  /\ \A p \in Players: 
       G.b[p].Road    + NrPlayerRoadsOnMap(p)                = BP[1]
    /\ G.b[p].Village + NrPlayerSettlementOnMap(p, Village)  = BP[2]
    /\ G.b[p].City    + NrPlayerSettlementOnMap(p, City)     = BP[3]

ConservationOfDevelopmentCards ==
  /\ \A dct \in DOMAIN G.dp:  SumDevelopmentAllPlayers(dct) + 
        G.dp[dct] + 
        G.bnk.DC[dct] = 
        DCP[getIndex(PCTMAP[dct], PCTST)]
  /\ SumDevelopmentAllPlayers("Knight")       + G.bnk.DC.Knight       = DCP[4]
  /\ SumDevelopmentAllPlayers("VictoryPoint") + G.bnk.DC.VictoryPoint = DCP[5]
  
--------

Init ==
  \* Initialization State
  /\ I = [ip |-> PhaseOne, ap |-> P[1]] 
  \* Game State
  /\ G = [                              
           ap  |-> P[1], 
           bnk |-> [
                     RC |-> [Lumber |-> 19, Brick |-> 19, Wool |-> 19, Grain |-> 19, Ore |-> 19], 
                     DC |-> [Monopoly |-> 2, YearOfPlenty |-> 2, RoadBuilding |-> 2, Knight |-> 14, VictoryPoint |-> 5]
                   ],
           dp  |-> [Monopoly |-> 0, YearOfPlenty |-> 0, RoadBuilding |-> 0],
           h   |-> [p \in Players |-> [
                      RC |-> [Lumber |-> 0, Brick |-> 0, Wool |-> 0, Grain |-> 0, Ore |-> 0],
                      DC |-> [BC |-> [Monopoly|-> 0, YearOfPlenty|-> 0, RoadBuilding|-> 0, Knight|-> 0],
                              AC |-> [Monopoly|-> 0, YearOfPlenty|-> 0, RoadBuilding|-> 0, Knight|-> 0],
                              UC |-> [Knight|-> 0, VictoryPoint|-> 0]
                      ]
                   ]],
           b   |-> [p \in Players |-> [Road |-> 15, Village |-> 5, City |-> 4]],
           s   |-> [c \in CT |-> [own |-> bot, st |-> bot]],
           r   |-> [c \in CD |-> [own |-> bot]],
           ba  |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 3], res |-> bot, n |-> bot],
           tp  |-> bot
         ]

Next == 
  \/ InitPhaseOne
  \/ InitPhaseTwo
  \/ DiceRollPhase
  \/ EmptyTrade
  \/ TradeFourToOne
  \/ TradeThreeToOne
  \/ TradeTwoToOne
  \/ EmptyBuild
  \/ BuildRoad
  \/ BuildVillage
  \/ BuildCity
  \/ BuyDevCard
  \/ PlayDevCard

Spec == Init /\ [][Next]_<<G, I>>

WeakFairness ==
    /\ WF_<<G, I>>(InitPhaseOne)
    /\ WF_<<G, I>>(InitPhaseTwo)
    /\ WF_<<G, I>>(DiceRollPhase)
    /\ WF_<<G, I>>(EmptyTrade)
    /\ WF_<<G, I>>(TradeFourToOne)
    /\ WF_<<G, I>>(TradeThreeToOne)
    /\ WF_<<G, I>>(TradeTwoToOne)
    /\ WF_<<G, I>>(EmptyBuild)
    /\ WF_<<G, I>>(BuildRoad)
    /\ WF_<<G, I>>(BuildVillage)
    /\ WF_<<G, I>>(BuildCity)
    /\ WF_<<G, I>>(BuyDevCard)
    /\ WF_<<G, I>>(PlayDevCard)
    
FairSpec ==
    /\ Spec
    /\ WeakFairness

GameEnded == G.tp = top
EventuallyAlwaysGameEnded == <>[]GameEnded

THEOREM Liveness == FairSpec => EventuallyAlwaysGameEnded
THEOREM Safety == Spec => /\ TypeOK
                          /\ ConservationOfResourceCards
                          /\ ConservationOfDevelopmentCards
                          /\ ConservationOfBuildings
                          
=============================================================================
\* Modification Histor
\* Last modified Wed Apr 23 17:46:25 CEST 2025 by tim_m
\* Created Tue Apr 22 17:19:51 CEST 2025 by tim_m
