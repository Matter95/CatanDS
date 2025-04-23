------------------------------- MODULE Catan -------------------------------
EXTENDS Integers, FiniteSets, Sequences, TLC

CONSTANT PossiblePlayers,                                               \* The set of players
         bot,                                                           \* bot
         Lumber, Brick, Wool, Grain, Ore,                               \* Resource Types
         Monopoly, YearOfPlenty, RoadBuilding, Knight, VictoryPoint,    \* Development Cards
         ThreeToOne,                                                    \* Wharf Type
         Road, Village, City,                                           \* Building Type
         DevCard,                                                       \* Purchasable Item
         PhaseOne,PhaseTwo,                                             \* Initialization Phases
         DiceRoll, Trading, Building,                                   \* Turn Phases
         top                                                            \* top
            

RCT == {Lumber, Brick, Wool, Grain, Ore}                \* Resource Card Types         
PCT == {Monopoly, YearOfPlenty, RoadBuilding}           \* Progress Card Types
DCT == PCT \cup {Knight, VictoryPoint}                  \* Development Card Types
RCP == <<19, 19, 19, 19, 19>>                           \* Resource Card Pool
DCP == <<2, 2, 2, 14, 5>>                               \* Development Card Pool
BCT == [m:0..2, yop:0..2, rb:0..2, k:0..14, vp:0..5]    \* Bought Card Types
ACT == [m:0..2, yop:0..2, rb:0..2, k:0..14]             \* Available Card Types
UCT == [k:0..14, vp:0..5]                               \* Unveiled Card Types
WT == {ThreeToOne} \cup RCT                             \* Wharf Types
MT == [                                                 \* Map Tiles
        coords: [arr: 0..1, row: Int, col: Int], 
        res: RCT \cup {bot}, 
        n: 2..6 \cup 8..12 \cup {bot}
      ] 
W == {                                                  \* Wharfs
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 0, row |-> 0,col |-> 1], res |-> bot, n |-> bot], 
                    t2 |-> [coords |-> [arr |-> 1, row |-> 0,col |-> 2], res |-> Ore, n |-> 10]
                ], 
                wt |-> ThreeToOne
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 0, row |-> 0,col |-> 3], res |-> bot, n |-> bot], 
                    t2 |-> [coords |-> [arr |-> 1, row |-> 0,col |-> 3], res |-> Wool, n |-> 2]
                ], 
                wt |-> Grain
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 1, row |-> 0,col |-> 5], res |-> bot, n |-> bot], 
                    t2 |-> [coords |-> [arr |-> 0, row |-> 1,col |-> 4], res |-> Brick, n |-> 10]
                ], 
                wt |-> Ore
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 0, row |-> 1,col |-> 0], res |-> bot, n |-> bot], 
                    t2 |-> [coords |-> [arr |-> 0, row |-> 1,col |-> 1], res |-> Grain, n |-> 12]
                ], 
                wt |-> Lumber
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 5], res |-> Ore, n |-> 8], 
                    t2 |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 6], res |-> bot, n |-> bot]
                ], 
                wt |-> ThreeToOne
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 0, row |-> 2,col |-> 0], res |-> bot, n |-> bot],
                    t2 |->[coords |-> [arr |-> 0, row |-> 2,col |-> 1], res |-> Lumber, n |-> 8] 
                ], 
                wt |-> Brick
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 0, row |-> 2,col |-> 4], res |-> Wool, n |-> 5], 
                    t2 |-> [coords |-> [arr |-> 1, row |-> 2,col |-> 5], res |-> bot, n |-> bot]
                ], 
                wt |-> Wool
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 1, row |-> 2,col |-> 2], res |-> Brick, n |-> 5], 
                    t2 |-> [coords |-> [arr |-> 0, row |-> 3,col |-> 1], res |-> bot, n |-> bot]
                ], 
                wt |-> ThreeToOne
    ],
    [coords |-> [
                    t1 |-> [coords |-> [arr |-> 1, row |-> 2,col |-> 3], res |-> Grain, n |-> 6], 
                    t2 |-> [coords |-> [arr |-> 0, row |-> 3,col |-> 3], res |-> bot, n |-> bot]
                ], 
                wt |-> ThreeToOne
    ]
}
ST == {Village, City}                         \* Settlement Types
BT == {Road} \cup ST                          \* Building Types
PIT == BT \cup {DevCard}                      \* Purchasable Item Types
BP == <<15, 5, 4>>                            \* Building Pool
IP == {PhaseOne, PhaseTwo}                    \* Initialization Phases
TP == {bot, DiceRoll, Trading, Building, top} \* Turn Phases
M == {                                        \* Map
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

    
isAdjacent(t1, t2) ==
    /\ t1 \in M /\ t2 \in M
    /\ LET 
        arr1 == t1.coords.arr
        row1 == t1.coords.row
        col1 == t1.coords.col
        arr2 == t2.coords.arr
        row2 == t2.coords.row
        col2 == t2.coords.col
        deltas == IF arr1 = 0 
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

--------

count(el, seq) ==
   LET RECURSIVE helper(_)
       helper(s) ==
           IF s = <<>> THEN 0
           ELSE IF Head(s) = el
                THEN 1 + helper(Tail(s))
                ELSE helper(Tail(s))
   IN helper(seq)

reverse(seq) ==
   LET RECURSIVE helper(_) 
       helper(s) ==
            IF s = <<>> THEN s
            ELSE  Append(helper(Tail(s)), Head(s))
   IN helper(seq)
     
--------
       
VARIABLE Players, \* Players of the game
         P,       \* The ordering of players
         I,       \* Initialization State
         G        \* Game State
         
BNK ==                                  \* Bank 
    [
      RC:[l: 0..19, b: 0..19, w: 0..19, g: 0..19, o: 0..19], 
      DC:[m: 0..2, yop: 0..2, rb: 0..2, k: 0..14, vp: 0..5]
    ]
DP == [m: 0..2, yop: 0..2, rb: 0..2]    \* Discard Pile
PH ==                                   \* Player Hand
    [
      RC:[l: 0..19, b: 0..19, w: 0..19, g: 0..19, o: 0..19], 
      DC:[m: 0..2, yop: 0..2, rb: 0..2, k: 0..14, vp: 0..5]
    ]
H == [Players -> PH]                    \* Hands 
PB == [r: 0..15, v: 0..5, c: 0..4]      \* Player Buildings
B == [Players -> PB]                    \* Buildings
S == [                                  \* Settlement Points
       coords: {t \in M \X M \X M: allAdjacent(t[1],t[2],t[3]) /\ 
       (t[1].res # bot \/ t[2].res # bot \/ t[3].res # bot)}, 
       own: Players \cup {bot}, 
       st: ST
     ] 
R == [                                  \* Road Points
       coords: {t \in M \X M: isAdjacent(t[1],t[2]) /\ 
       (t[1].res # bot \/ t[2].res # bot)}, 
       own: Players \cup {bot}
     ] 
         
TypeOK ==   
    /\ Players \subseteq PossiblePlayers /\ Cardinality(Players) >= 2
    /\ P \in Seq(Players) /\ \A p \in Players: count(p,P) = 1 
    /\ I \in [                          \* Initialization State
               ip: IP, 
               ap: P
             ]    
    /\ G \in [                          \* Game State
               ap: P, 
               bnk: BNK, 
               dp: DP, 
               h: H, 
               bu: B, 
               s: S, 
               r: R, 
               ba: M, 
               tp: TP
             ] 

Init ==
    /\ Players \subseteq PossiblePlayers /\ Cardinality(Players) >= 2
    /\ P \in Seq(Players) /\ \A p \in Players: count(p,P) = 1 
    /\ I = [ip |-> PhaseOne, ap |-> P[1]] \* Initialization State
    /\ G = [                              \* Game State
            ap  |-> P[1], 
            bnk |-> {[l: 19, b: 19, w: 19, g: 19, o: 19], [m: 2, yop: 2, rb: 2, k: 14, vp: 5]},
            dp  |-> [m: 0, yop: 0, rb: 0],
            s   |-> {\A s \in S: s.own = bot /\ s.st = bot},
            r   |-> {\A r \in R: r.own = {bot}},
            ba  |-> [coords |-> [arr |-> 1, row |-> 1,col |-> 2], res |-> bot, n |-> bot],
            tp  |-> bot
       ]
    
Empty ==
    /\ I.ip = PhaseOne
    /\ G.tp = bot
    /\ UNCHANGED <<G, I>>

Next == 
    \/ Empty


Spec == Init /\ [][Next]_<<G,I>>


=============================================================================
\* Modification Histor
\* Last modified Wed Apr 23 17:46:25 CEST 2025 by tim_mm
\* Created Tue Apr 22 17:19:51 CEST 2025 by tim_m
