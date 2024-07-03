junction(X;Y) :- edge(X,Y,_).
requires_water(X) :- snaps_to(U,X), not is_tank(U).
tank(X) :- snaps_to(Y,X), is_tank(Y).
tank_height(X,H) :- tank(X), snaps_to(Y,X), height(Y,H).

{ pipe(X,Y,K,samedir):   edge(X,Y,K) } 1 :- junction(Y).
{ pipe(Y,X,K,inversion): edge(X,Y,K) } 1 :- junction(X).
:- pipe(X,Y,_,_), pipe(Y,X,_,_).

tank_reach(T,X) :- tank(T), pipe(T,X,_,_).
tank_reach(T,Y) :- tank_reach(T,X), pipe(X,Y,_,_).
tank_reach(T,T) :- tank(T).
:~ requires_water(X), not tank_reach(_,X). [1@70,X]

primary_tank(T) :- tank(T), not pipe(_,T,_,_).
:- not primary_tank(_).
:~ primary_tank(T). [1@60,T]

secondary_tank(T) :- tank(T), pipe(_,T,_,_).
connected_to_a_primary_tank(T) :- secondary_tank(T), primary_tank(Tp), tank_reach(Tp,T).
:- secondary_tank(T), not connected_to_a_primary_tank(T).

pressure_issue(X) :- tank_reach(T,X), tank_height(T,HT), height(X,HX), HT <= HX+25.
:~ requires_water(X), pressure_issue(X). [1@50,X]

avoid_road_type(residential; living_street).
:~ pipe(X,Y,K,_), highway(X,Y,K,Type), avoid_road_type(Type). [1@40,X,Y,K]

:~ pump(X,Y,K,C), pipe(X,Y,K,_). [C@20,X,Y,K]
:~ not pump(X,Y,K,C), pipe(X,Y,K,samedir),   height(X,HX), height(Y,HY), HY > HX. [1@20,X,Y,K,samedir]
:~ not pump(X,Y,K,C), pipe(X,Y,K,inversion), height(X,HX), height(Y,HY), HX > HY. [1@20,X,Y,K,inversion]

% Number of pipes
:~ pipe(X,Y,K,_). [1@10,X,Y,K]

:~. [0@70]
:~. [0@60]
:~. [0@50]
:~. [0@40]
:~. [0@30]
:~. [0@20]
:~. [0@10]

#show.
#show pipe/4.
#defined pump/4.
