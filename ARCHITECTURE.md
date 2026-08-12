# Portfolio Intelligence & Adaptive Decision Engine

> Master architecture document — v1.0
> Filosofie: sistemul nu "ghicește prețul". Anticipează o distribuție de scenarii și alege acțiunea cu cel mai bun raport edge / risc / cost / capacitate de portofoliu.

Cercetare de fundamentare: forecastul trebuie evaluat în contextul costurilor de tranzacție, constrângerilor de portofoliu și utilității deciziei, nu doar al acurateței direcționale (utility-weighted forecasting & calibration under trading frictions). Validarea strategiilor trebuie făcută out-of-sample / walk-forward, cu conștientizarea survivorship bias și look-ahead bias, pentru a evita overfitting pe date istorice (CFA Institute, Backtesting & Simulation).

---

## 0. Principiu central

Nu optimizăm acuratețea predicției. Optimizăm calitatea deciziei sub incertitudine, dat fiind: edge așteptat, risc consumat, cost de execuție, capacitate de portofoliu (margin, corelații, lichiditate).

```
WHAT IS HAPPENING?
        v
WHAT COULD HAPPEN?
        v
WHAT ARE THE ALTERNATIVES?
        v
WHAT IF WE ARE WRONG?
        v
CAN THE PORTFOLIO AFFORD IT?
        v
IS THE EDGE REAL?
        v
IS EXECUTION WORTH IT?
        v
EXECUTE / WAIT
        v
WHAT HAPPENED?
        v
WHY DID IT HAPPEN?
        v
WAS OUR FORECAST GOOD?
        v
WAS OUR RISK MANAGEMENT GOOD?
        v
WHAT DID WE LEARN?
        v
HOW DOES THAT AFFECT NEXT TIME?
```

---

## 1. Workflow general

```
ACCOUNT STATE (equity / margin / exposure / PnL)
        v
MARKET STATE (price / liquidity / volatility / flow)
        v
MARKET REGIME (trend / range / reversal / stress)
        v
OPPORTUNITY SCANNER (BTC, ETH, EGLD, ... -> LONG / SHORT / WAIT)
        v
FORECAST ENGINE (probability + range + time, multi-horizon)
        v
SCENARIO TREE (PRIMARY / IF X / IF Y / INVALIDATION)
        v
PORTFOLIO SIMULATION ("ce se intampla daca?")
        v
CAPITAL ARBITER (edge vs risk vs correlation vs liquidity vs margin)
        v
REJECT  <---------->  APPROVE
                          v
                  EXECUTION PLANNER (price / size / order type / timing)
                          v
                      EXECUTION
                          v
                       POSITION
                     /          \
                 PROFIT          RISK
                     \          /
                    OUTCOME ENGINE
                          v
                 FORECAST vs REALITY
                          v
                  ERROR ATTRIBUTION
                          v
                 CALIBRATION ENGINE
                          v
                  NEXT DECISION
```

---

## 2. Cele 5 motoare centrale

### 2.1 Market Intelligence
Colectează și normalizează starea contului (equity, margin, exposure, PnL) și starea pieței (preț, lichiditate, volatilitate, flow), apoi clasifică regimul de piață: trend / range / reversal / stress. Scanează universul de active (BTC, ETH, EGLD, SOL, ...) și produce candidați LONG / SHORT / WAIT pentru motorul următor.

### 2.2 Forecast & Scenario Engine
Nu produce o singură probabilitate direcțională. Produce o distribuție:

```
CURRENT STATE
  Trend: bullish
  Regime: continuation
  Volatility: medium
  Liquidity: healthy
  Portfolio exposure: moderate

FORECAST (HORIZON = 30 min)
  P(up > +1%)   = 64%
  P(range)      = 23%
  P(down > -1%) = 13%

SCENARIO TREE
  PRIMARY: continuation
  IF X: breakout + volume confirmation -> increase opportunity quality
  IF Y: pullback + structure holds -> passive entry opportunity
  INVALIDATION: 15M structure breaks -> forecast invalid
```

Forecastul e produs pe minim 4 orizonturi simultane, fiecare cu rol diferit:

| Orizont | Rol | Exemplu |
|---|---|---|
| 5 min | execution forecast | bearish temporar |
| 15 min | setup forecast | pullback |
| 1 h | directional forecast | bullish |
| 4 h | regime forecast | bullish |

Regula de bază: un forecast de orizont scurt care contrazice un forecast de orizont lung nu invalidează automat forecastul de orizont lung — invalidarea se face explicit, prin regulile din scenario tree (ex. "15M structure breaks"), nu prin simpla contradicție de semn între orizonturi.

### 2.3 Portfolio Intelligence & Capital Arbiter
Agregă toate oportunitățile candidate și le clasează, nu după confidence brut, ci după un scor compus:

```
SCORE = f(expected_edge, risk, correlation, liquidity,
           execution_quality, portfolio_fit, forecast_calibration)
```

Exemplu de ranking (confidence și edge brute nu determină singure ordinea finală):

| Activ | Confidence | Expected edge | Rank final |
|---|---|---|---|
| EGLD LONG | 86 | 1.8% | #1 |
| ETH LONG | 79 | 1.4% | #2 |
| SOL SHORT | 74 | 2.0% | #3 |
| BTC LONG | 82 | 1.1% | #4 |

Rezultatul poate fi și `NO TRADE`, dacă toate candidatele consumă disproporționat de mult risc de portofoliu.

**What-If Engine** — înainte de aprobare, simulează impactul poziției noi pe portofoliul curent:

```
CURRENT PORTFOLIO -> ADD [ASSET] [SIDE] -> SIMULATE

Scenario A: BTC -2%, ETH -3%, EGLD -5%
Scenario B: BTC +2%, ETH +3%, EGLD +5%
Scenario C: volatility x2
Scenario D: correlations -> 1
Scenario E: liquidity drops 50%

-> Portfolio drawdown per scenariu
-> daca drawdown-ul agregat e disproportionat: REDUCE SIZE / WAIT / REJECT
```

**System Forecast** — motorul își anticipează propriile limite de execuție, nu doar piața:

```
MARKET FORECAST:    bullish 76%
EXECUTION FORECAST:  fill quality 61%
PORTFOLIO FORECAST:  risk impact high
COMBINED DECISION:   WAIT
```

### 2.4 Execution & Position Engine
Primește aprobarea de la Capital Arbiter și decide preț, mărime, tip de ordin și timing. Ține evidența poziției pe durata ei de viață (profit / risc) și predă rezultatul final motorului de Decision Memory.

### 2.5 Decision Memory & Adaptive Calibration
Fiecare decizie devine un caz structurat, nu doar o linie într-un jurnal de tranzacții:

```
CASE #18427
  Market: trend, volatility, volume, structure, orderbook
  Portfolio: exposure, correlation, risk
  Forecast: ...
  Plan: ...
  Outcome: ...
  Error: ...
  Lesson: ...
  Next similar setup: adjust confidence
```

Error attribution e granular, nu binar (win/loss):

```
FORECAST: correct   | ENTRY: bad      | EXECUTION: bad   | RISK: good     | EXIT: premature
FORECAST: wrong     | REGIME: wrong   | EXECUTION: good  | RISK: good
FORECAST: correct   | EXECUTION: excellent | RISK: excessive
```

Calibrarea se face empiric: daca sistemul declara confidence 80%, se verifica ulterior pe un sample de cazuri similare cate au fost efectiv corecte; daca empirical confidence ~= 73%, ajustarea de confidence devine parte din model, nu o presupunere.

**Trei niveluri de promovare a schimbarilor de strategie:**

```
OBSERVATION  -> inregistreaza ce merge / nu merge
CALIBRATION  -> ajusteaza confidence / ranking / setup quality
PROMOTION    -> activeaza modificarea SOLO dupa: sample suficient,
                walk-forward, out-of-sample, cost-aware validation,
                drawdown check
```

Nicio modificare de strategie nu devine activa direct din observatie sau calibrare — trece obligatoriu prin promotion.

---

## 3. Metrici de productivitate (nu numarul de trade-uri)

| Metrica | Formula | Ce masoara |
|---|---|---|
| Capital productivity | Profit generat / Risc consumat | eficienta capitalului |
| Risk productivity | Expected edge / Portfolio risk consumat | eficienta riscului |
| Capital efficiency | Net PnL / Capital-time occupied | eficienta timpului de capital blocat |
| Opportunity efficiency | Oportunitati bune luate / Oportunitati bune disponibile | rata de captare a oportunitatilor |
| Execution efficiency | Expected entry vs Actual entry | calitatea executiei |
| Decision efficiency | Decizii corecte / Decizii luate | calitatea deciziei, indiferent de PnL |

---

## 4. Riscuri de arhitectura si mitigari

- **Latenta pe fast path vs slow path**: Capital Arbiter + What-If Engine + Scenario Tree complet pot introduce latenta pe orizontul de executie (5 min). Solutie: separa un fast path (verificari ieftine, cache-uite: margin disponibil, corelatii curente, risc consumat) de un slow path (recalibrare, scenario tree complet), rulate la frecvente diferite.
- **Overfitting pe calibrare**: orice ajustare de confidence sau ranking trebuie sa treaca prin out-of-sample / walk-forward inainte de promotion, altfel calibrarea "invata" zgomotul din perioada de observatie.
- **Auto-sabotaj al learning-ului**: separarea stricta Observation / Calibration / Promotion previne ca o serie scurta de pierderi sau castiguri sa schimbe direct comportamentul live.

---

## 5. Surse de fundamentare

- Utility-Weighted Forecasting and Calibration for Risk-Adjusted Decisions under Trading Frictions — arXiv 2601.07852
- CFA Institute — Portfolio Risk and Return: Part II (corelatie si risc agregat de portofoliu)
- CFA Institute — Backtesting & Simulation (walk-forward, survivorship bias, look-ahead bias, overfitting)
