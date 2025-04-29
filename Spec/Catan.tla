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
RCTST == <<"Lumber", "Brick", "Wool", "Grain", "Ore">>               
\* Progress Card Types
PCT == {Monopoly, YearOfPlenty, RoadBuilding}
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

ASSUME
  \* Map is a subset of all possible map tiles
  /\ M \subseteq MT  
  \* Map has no duplicate tiles
  /\ \A t1, t2 \in M: t1.coords = t2.coords <=> t1 = t2 
  \* all Wharf tiles are part of the map
  /\ \A w \in W: w.wt \in WT /\ w.coords.t1 \in M /\ w.coords.t2 \in M 
  \* All Wharfs are on the coast
  /\ \A w \in W: isAdjacent(w.coords.t1, w.coords.t2) /\ isCoast(w.coords.t1, w.coords.t2) 

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

SumSeq(seq) == 
  LET RECURSIVE helper(_)
    helper(s) ==
      IF s = <<>> THEN 0
      ELSE Head(s) + helper(Tail(s))
   IN helper(seq)

SumFunc(func) == 
  LET RECURSIVE helper(_,_)
    helper(f,D) ==
      IF D = {} THEN 0 
        ELSE LET d == CHOOSE e \in D: TRUE
             IN f[d] + helper(f, D\{d})
   IN helper(func, DOMAIN func)

SumFuncIndex(func, ind) == 
  LET RECURSIVE helper(_,_,_)
    helper(f,D,i) ==
      IF D = {} THEN 0 
        ELSE LET d == CHOOSE e \in D: TRUE
             IN f[d[i]] + helper(f, D\{d}, i)
   IN helper(func, DOMAIN func, ind)


IterateRec(rec) == [d \in DOMAIN rec |-> (rec)[d]]

IsInSeq(el, seq) == \E d \in 1..Len(seq): seq[d] = el

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
DP  == [Monopoly: 0..2, YearOfPlenty: 0..2, RoadBuilding: 0..2]     
PH == [
        RC:[Lumber: 0..19, Brick: 0..19, Wool: 0..19, Grain: 0..19, Ore: 0..19],
        DC:[BC: BCT,
            AC: ACT,
            UC: UCT
           ]
      ]
\* Hands      
H   == [p \in Players |-> PH] 
\* Player Buildings
PB == [Road: 0..15, Village: 0..5, City: 0..4] 
\* Buildings
B   == [p \in Players |-> PB] 
\* Settlement Points
S   == [
         coords: {{k[1], k[2], k[3]}: k \in {t \in M \X M \X M: allAdjacent(t[1],t[2],t[3]) /\ 
         (t[1].res # bot \/ t[2].res # bot \/ t[3].res # bot)}}, 
         own: Players \cup {bot}, 
         st: ST \cup {bot}
       ]
\* Road Points 
R   == [
         coords: {{k[1], k[2]}: k \in {t \in M \X M: isAdjacent(t[1],t[2]) /\ 
         (t[1].res # bot \/ t[2].res # bot)}}, 
         own: Players \cup {bot}
       ]
         
TypeOK ==   
  /\ I \in [ip: IP, ap: Players]      \* Initialization State
\*  /\ Print("AP", G.ap \in Players)
  /\ G.ap \in Players
\*  /\ Print("BNK", G.bnk \in BNK)
  /\ G.bnk \in BNK                    
\*  /\ Print("DP", G.dp \in DP)
  /\ G.dp \in DP
\*  /\ Print("AC", \A p \in Players: G.h[p].DC.AC \in ACT)
\*  /\ Print("BC", \A p \in Players: G.h[p].DC.BC \in BCT)
\*  /\ Print("UC", \A p \in Players: G.h[p].DC.UC \in UCT)
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
  /\ G.tp = bot
  /\ I.ip = PhaseOne
  /\ I.ap \in Players
  
  /\ \E sp \in G.s: sp.own = bot /\ buildable(sp)
    /\ \E rp \in G.r: rp.own = bot /\ isAdjacentRoadToSettlement(sp,rp) /\ roadHasNoBandit(rp)
    
    /\ G' = [G EXCEPT !.b[I.ap].Road    = G.b[I.ap].Road    - 1,
                      !.b[I.ap].Village = G.b[I.ap].Village - 1,
                      !.s = (G.s \ {sp}) \cup {[coords |-> sp.coords, own |-> I.ap, st |-> Village]}, 
                      !.r = (G.r \ {rp}) \cup {[coords |-> rp.coords, own |-> I.ap]}
            ]
    /\ IF getIndex(I.ap, P) = Cardinality(Players)
            THEN 
              I' = [I EXCEPT  !.ap = reverse(P)[1],
                              !.ip = PhaseTwo
                   ]
            ELSE 
              I' = [I EXCEPT  !.ap = P[(getIndex(I.ap, P) + 1) % (Cardinality(Players) + 1)]]

\* TRIAL FOR SHORTER GAME STATE UPDATE
\* !.bnk.RC = [r \in RCT |-> G.bnk.RC[RCTMAP[r]] = @ - gain[getIndex(RCTMAP[r],RCTST)]],

InitPhaseTwo ==
  /\ G.tp = bot
  /\ I.ip = PhaseTwo
  /\ I.ap \in Players
 
  /\ \E sp \in G.s: sp.own = bot /\ buildable(sp)
    /\ \E rp \in G.r: rp.own = bot /\ isAdjacentRoadToSettlement(sp,rp) /\ roadHasNoBandit(rp)
    /\ LET gain == <<0,0,0,0,0>>
    IN
      /\ \A c \in {c \in M \X RCT: c[1] \in sp.coords /\ tileHasNoBandit(c[1]) /\ c[1].res = c[2]}: gain[getIndex(c, RCT)] = gain[getIndex(c, RCT)] + 1
      /\ Print(gain, TRUE)
      /\ I' = [I EXCEPT !.ap = reverse(P)[(getIndex(I.ap, reverse(P)) + 1) % (Cardinality(Players) + 1)]] \* next player
      /\ G' = [G EXCEPT !.bnk.RC.Lumber = @ - gain[1],
                        !.bnk.RC.Brick  = @ - gain[2],
                        !.bnk.RC.Wool   = @ - gain[3],
                        !.bnk.RC.Grain  = @ - gain[4],
                        !.bnk.RC.Ore    = @ - gain[5],
                        !.h[I.ap].RC.Lumber = @ + gain[1],
                        !.h[I.ap].RC.Brick  = @ + gain[2],
                        !.h[I.ap].RC.Wool   = @ + gain[3],
                        !.h[I.ap].RC.Grain  = @ + gain[4],
                        !.h[I.ap].RC.Ore    = @ + gain[5],
                        !.b[I.ap].Road    = @ - 1,
                        !.b[I.ap].Village = @ - 1,
                        !.s = (@ \ {sp}) \cup {[coords |-> sp.coords, own |-> I.ap, st |-> Village]}, 
                        !.r = (@ \ {rp}) \cup {[coords |-> rp.coords, own |-> I.ap]},
                        !.tp = IF getIndex(I.ap, P) = Cardinality(Players) THEN DiceRoll ELSE bot  
              ] 

--------

isOwnedByPlayer(p,s) ==
  /\ p \in Players
  /\ s \in G.s
  /\ s.own = p
 
isVillage(s) ==
  /\ s \in G.s
  /\ s.st = Village

isCity(s) ==
  /\ s \in G.s
  /\ s.st = City
  
hasSettlementOnTile(t,p) ==
  /\ \E s \in G.s: s.own = p
    /\ t \in s.coords
    
validBanditMoves == {t \in M: t # G.b}

SumResourcesSinglePlayer(p) == SumFunc(IterateRec(G.h[p].RC))

SumResourceAllPlayers(rct) == SumFunc([p \in Players |-> (G.h[p].RC)[rct]])

SumDevelopmentAllPlayers(dct) == 
  IF IsInSeq(dct, PCTST)
  THEN SumFunc([p \in Players |-> (G.h[p].DC.BC)[dct]]) + 
        SumFunc([p \in Players |-> (G.h[p].DC.AC)[dct]])
  ELSE IF dct = "Knight"
  THEN SumFunc([p \in Players |-> (G.h[p].DC.BC)[dct]]) + 
        SumFunc([p \in Players |-> (G.h[p].DC.AC)[dct]]) + 
        SumFunc([p \in Players |-> (G.h[p].DC.UC)[dct]])
  ELSE SumFunc([p \in Players |-> (G.h[p].DC.UC)[dct]])

NrPlayerRoadsOnMap(p) == SumFunc([r \in G.r |-> IF r.own = p THEN 1 ELSE 0])

NrPlayerSettlementOnMap(p, st) == SumFunc([s \in G.s |-> IF s.own = p /\ s.st = st THEN 1 ELSE 0])

PlayerRoadsOnMap(p) == {r \in R: r.own = p}

PlayerSettlementOnMap(p) == {s \in S: s.own = p}

TilesWithNumber(d) == {t \in M: t.n = d}

ResourceTilesForPlayer(p, d) == 
  {t \in TilesWithNumber(d): \E s \in PlayerSettlementOnMap(p): t \in s.coords /\ tileHasNoBandit(t)}

ResourceGainPlayer(p,d) ==
  LET gain == <<0,0,0,0,0>>
  IN \A t \in ResourceTilesForPlayer(p,d): gain[getIndex(t, t.res)] = gain[getIndex(t, t.res)] + 1

ResourceLossPlayer(p) ==
  LET loss == <<0,0,0,0,0>>
      CardSum == SumResourcesSinglePlayer(p)
  IN 
    IF CardSum > 7
    THEN
      LET RECURSIVE helper(_,_)
        helper(s, n) == IF SumSeq(s) = (n \div 2)
          THEN loss
          ELSE CHOOSE c \in RCTST: G.H[p].RC[c] - (s[getIndex(c, RCTST)] + 1) 
            /\ s[getIndex(c, RCTST)] = s[getIndex(c, RCTST)] + 1 
      IN helper(loss, CardSum)
    ELSE loss

  
--------

DiceRollPhase ==
  /\  G.tp = DiceRoll
  /\  LET d     == CHOOSE n \in 2..12: TRUE
          loss  == [p \in Players |-> ResourceLossPlayer(p)]
          gain  == [p \in Players |-> ResourceGainPlayer(p,d)]
      IN
        IF d = 7
          THEN
            \* Move Bandit to a tile of another player, steal 1 Card (Tile, Player, Resource)
            /\ Print(loss, TRUE)
            /\ Print(gain, TRUE)            
            /\ LET bm == CHOOSE m \in {BM \in validBanditMoves \X Players \X RCT: 
                              BM[2] # G.ap /\ hasSettlementOnTile(BM[1], BM[2])}: TRUE
               IN
                /\ G' = [G EXCEPT !.h[bm[2]].RC.bm[3]  = G.h[I.ap].RC.bm[3] - 1, \* stolen resource
                                  !.h[bm[2]].RC.bm[3]  = G.h[I.ap].RC.bm[3] - 1, \* stolen resource
                                  !.bnk.RC.Lumber = @ - SumFuncIndex(gain,1) + SumFuncIndex(loss,1),
                                  !.bnk.RC.Brick  = @ - gain[2] + loss[2],
                                  !.bnk.RC.Wool   = @ - gain[3] + loss[3],
                                  !.bnk.RC.Grain  = @ - gain[4] + loss[4],
                                  !.bnk.RC.Ore    = @ - gain[5] + loss[5],
                                  !.h[G.ap].RC.Lumber = @ + gain[1], 
                                  !.h[G.ap].RC.Brick  = @ + gain[2],
                                  !.h[G.ap].RC.Wool   = @ + gain[3],
                                  !.h[G.ap].RC.Grain  = @ + gain[4],
                                  !.h[G.ap].RC.Ore    = @ + gain[5]
                        ]
                /\ UNCHANGED(I)
          ELSE
            /\ Print(gain, TRUE) 
            /\ G' = [G EXCEPT !.bnk.RC.Lumber = @ - gain[1],
                              !.bnk.RC.Brick  = @ - gain[2],
                              !.bnk.RC.Wool   = @ - gain[3],
                              !.bnk.RC.Grain  = @ - gain[4],
                              !.bnk.RC.Ore    = @ - gain[5],
                              !.h[G.ap].RC.Lumber = @ + gain[1], 
                              !.h[G.ap].RC.Brick  = @ + gain[2],
                              !.h[G.ap].RC.Wool   = @ + gain[3],
                              !.h[G.ap].RC.Grain  = @ + gain[4],
                              !.h[G.ap].RC.Ore    = @ + gain[5]
                    ]
            /\ UNCHANGED(I)
       
--------

ConservationOfResourceCards == 
  /\ \A i \in 1..Len(RCTST): SumResourceAllPlayers(RCTST[i]) + G.bnk.RC[RCTST[i]] = RCP[i]
  
ConservationOfBuildings ==
  /\ \A p \in Players: 
       G.b[p].Road    + NrPlayerRoadsOnMap(p)                = BP[1]
    /\ G.b[p].Village + NrPlayerSettlementOnMap(p, Village)  = BP[2]
    /\ G.b[p].City    + NrPlayerSettlementOnMap(p, City)     = BP[3]

ConservationOfDevelopmentCards ==
  /\ \A i \in 1..Len(PCTST):  SumDevelopmentAllPlayers(PCTST[i]) + G.dp[PCTST[i]] + G.bnk.DC[PCTST[i]] = DCP[i]
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
           s   |-> {s \in S: s.own = bot /\ s.st = bot},
           r   |-> {r \in R: r.own = bot},
           ba  |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 3], res |-> bot, n |-> bot],
           tp  |-> bot
         ]

Next == 
  \/ InitPhaseOne
  \/ InitPhaseTwo
  \/ DiceRollPhase

Spec == Init /\ [][Next]_<<G, I>>

=============================================================================
\* Modification Histor
\* Last modified Wed Apr 23 17:46:25 CEST 2025 by tim_mm
\* Created Tue Apr 22 17:19:51 CEST 2025 by tim_m
