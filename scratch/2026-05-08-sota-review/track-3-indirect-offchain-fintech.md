# Track 3 — Indirect off-chain EM dollar/savings fintechs

Scope: closed-source, custodial fintechs in LATAM (Colombia-priority) and Africa
that compete for the same wage-earner wallet share Abrigo targets. None deliver
convex payoff or a premium-funded ratchet; all deliver some flavor of dollar
savings, USDC wrapper, or peso-stable balance with light yield. They are the
*UX moat* Abrigo must beat or sidestep — not the mechanism moat.

## 1. Players & products

| Player | Country / corridor | Product | URL | Regulatory wrapper |
|---|---|---|---|---|
| Littio | Colombia (LATAM expansion) | USD/EUR neobank account, USDC/EUROC under hood, 12% E.A. on digital dollars | [littio.co](https://littio.co/en/) | US partner-bank account; YC + Circle backed; Avalanche/OpenTrade rails ([Avalanche blog](https://www.avax.network/blog/colombian-neobank-littio-opentrade-interest-bearing-usd-accounts-avalanche)) |
| Bold | Colombia | SME PSP + corporate USD-adjacent products; not retail USD savings | [bold.co](https://bold.co/) | Colombian PSP; Series C $50M ([LatamList](https://latamlist.com/colombian-fintech-bold-raises-50m-series-c/)) |
| Movii | Colombia | Peso e-wallet + prepaid card | [movii.com.co](https://movii.com.co/) | SEDPE (Sociedad Especializada en Depósitos Electrónicos) |
| Powwi | Colombia | Peso e-wallet | [powwi.com](https://powwi.com/) | SEDPE, Fogafín-backed |
| Daviplata | Colombia | Peso mobile money (Davivienda) | [daviplata.com](https://www.daviplata.com/) | Bank subsidiary; primarily COP |
| Bancolombia A la Mano | Colombia | Peso digital wallet | [bancolombia.com](https://www.bancolombia.com/) | Bank subsidiary |
| Rappi Pay | Colombia + LATAM | Wallet + prepaid card; AstroPay USD/EUR FX checkout integration | [rappipay.com](https://rappipay.com/debito-colombia/) | Davivienda alliance; AstroPay partnership ([BusinessWire](https://www.businesswire.com/news/home/20250825148407/en/Rappi-and-AstroPay-Launch-Latin-Americas-First-Super-App-Wallet-Integration)) |
| Trii | Colombia | Retail brokerage (Colombian + US equities) | [trii.app](https://trii.app/) | SCV (sociedad comisionista) |
| Nubank | BR / MX / CO (131M users) | USDC in-app wallet with 4% fixed APY ≥10 USDC; crypto swap | [nubank.com.br](https://international.nubank.com.br/) | Banco múltiplo (BR); SOFIPO (MX); Compañía de Financiamiento (CO) ([Digital Watch](https://dig.watch/updates/brazilian-nubank-offers-4-annual-return-for-usdc-holders)) |
| Belo | Argentina (LATAM) | USDC/USDT savings, ~4–4.25% APY via OpenTrade; debit card | [belo.app](https://www.belo.app/en-us/ar/) | PSP (Argentina); OpenTrade institutional yield wrap |
| Lemon Cash | Argentina | USDC dep/wd, Earn 10%+ APY, BTC-backed Visa credit card | [lemon.me](https://lemon.me/en/) | PSAV (Argentina); Morpho-backed credit ([Morpho story](https://morpho.org/stories/lemon/)) |
| Buenbit | Argentina | USDT/USDC/DAI/NUARS daily yield (DeFi-routed via Nexo) | [buenbit.com](https://buenbit.com/) | PSAV; "Nexo by Buenbit" rebrand |
| Bitso / Bitso+ | MX/AR/BR/CO | USDC/USDT weekly yield ~4%, no lock | [bitso.com](https://bitso.com/) | Registered with CNBV (MX), CNV/CNAD (AR), local FinAuth (CO) |
| Valiu | CO / VE corridor | Synthetic-USD remittance + savings (BTC-backed) | [valiu.com](https://www.ycombinator.com/companies/valiu) | YC; mostly remittance now, savings deemphasized ([Decrypt](https://decrypt.co/57456/valiu-raise-bitcoin-dollar-remittances-latin-america)) |
| Mercury (stablecoin) | LATAM B2B | Multi-stable USD account for businesses | [mercury.com](https://mercury.com/) | US bank partner; B2B not retail wage earners |
| Wise | Global EM rails | Multi-currency account incl. some EM | [wise.com](https://wise.com/) | EMI (UK), MSB (US) |
| Fintual | CL / MX / Brasil-launching | Peso/real mutual-fund robo-advisor; some USD-share-class funds | [fintual.com](https://fintual.com/) | AGF (Chile) |
| Yellow Card | 20 African countries | USDC/USDT/PYUSD on/off-ramp + emerging yield | [yellowcard.io](https://yellowcard.io/) | First licensed stablecoin operator on continent; Visa partnership ([Cointelegraph](https://cointelegraph.com/news/visa-yellow-card-stablecoin-payments-africa)) |
| Chipper Cash | Pan-African | USD virtual account + USDC stablecoin balances | [chippercash.com](https://www.chippercash.com/) | Bridge bank partner; Ripple/RLUSD integrated ([Chipper blog](https://www.chippercash.com/blog/blog/stable-partnership)) |
| Kuda | Nigeria + diaspora | NGN-first neobank, savings buckets | [kuda.com](https://kuda.com/) | CBN microfinance bank license |
| Risevest | NGN diaspora (5 countries) | USD fixed-income, US real estate, US stocks | [risevest.com](https://risevest.com/) | SEC-Nigeria asset manager wrapper |
| Bamboo | NGN | US stocks/ETFs brokerage | [investbamboo.com](https://investbamboo.com/) | SEC-Nigeria sub-broker |
| Cowrywise | NGN | NGN + USD mutual funds, Halal savings | [cowrywise.com](https://cowrywise.com/) | SEC-Nigeria fund manager |

## 2. Mechanism table

| Player | Delivery mechanism | Yield source |
|---|---|---|
| Littio | USDC stored at custodian; OpenTrade tokenized T-bill / MMF wrap on Avalanche; user sees USD balance | T-bill / MMF (OpenTrade) — claims up to 12% E.A.; likely token + reward stack |
| Nubank | Native USDC wallet on Polygon (custodial); 4% fixed | Subsidized / treasury-backed flat rate |
| Bitso+ | USDC/USDT held custodially, lent or yield-routed; ~4% APY weekly | Lending desk / institutional borrower book |
| Belo | USDC/USDT custody; OpenTrade institutional vault | Tokenized MMF (OpenTrade) |
| Lemon Earn | USDC routed to Morpho (curated vault) | DeFi lending (Morpho) — claims 10%+ |
| Buenbit | DAI/USDC/USDT routed to Ethereum DeFi via Nexo backend | DeFi protocol yield |
| Valiu | Synthetic-USD = BTC + short-BTC perp (BitMEX-style hedge historically) | Mostly remittance now; savings dormant |
| Yellow Card | USDC/USDT custody + on/off-ramp; "earn yield" feature emerging | TBD — partner-vault |
| Chipper Cash | USDC virtual USD account; Ripple/RLUSD rails | Mostly transactional; minimal yield |
| Risevest | Pooled fund-of-funds investing in US fixed-income + REIT + equities | Underlying US asset returns (real yield) |
| Bamboo | Direct US brokerage exposure (sub-broker) | Equity returns |
| Cowrywise | Mutual-fund unit holdings (Naira + USD share classes) | Underlying fund returns |
| Littio peso/Daviplata/Movii/Powwi | Peso e-wallet, no FX/USD optionality at scale | None / interchange |

## 3. Coverage of Abrigo thesis components (7-axis scoring)

Permissionless = anyone with self-custody can interact. Convex = nonlinear payoff
(option-like). EM-FX-native = local-currency-pair instrument exposure (not pure
USD). Wage-accessible = $1–$10 ticket, KYC-light. Premium-funded ratchet =
recurring small premium converts into productive-capital position over time.
Open-source = published mechanism + code. Numo-rigor = documented mechanism /
quantitative whitepaper.

| Player | Permissionless | Convex | EM-FX-native | Wage-accessible | Premium-ratchet | Open-source | Numo-rigor (0–5) |
|---|---|---|---|---|---|---|---|
| Littio | No | No | Partial (USD↔COP) | Yes | No | No | 1 |
| Nubank USDC | No | No | No (USD only) | Yes | No | No | 1 |
| Bitso+ | No | No | Partial | Yes | No | No | 1 |
| Belo | No | No | Partial (ARS↔USD) | Yes | No | No | 1 |
| Lemon | No | No (BTC-collat is *linear* exposure) | Partial | Yes | No (closest: BTC-collat credit is asset-backed credit, not ratchet) | No | 2 |
| Buenbit | No | No | Yes (NUARS / NUPEN) | Yes | No | No | 1 |
| Valiu | No | No (synthetic-USD is *delta-1*) | Yes | Yes | No | No | 2 (BTC-hedge synthetic-dollar mechanism documented) |
| Yellow Card | No | No | Partial | Yes | No | No | 1 |
| Chipper Cash | No | No | Partial | Yes | No | No | 0 |
| Risevest | No | No (mutual fund linear) | No | Yes | Partial — DCA into US assets is *the closest analog* in this list | No | 2 |
| Bamboo | No | No | No | Yes | No | No | 1 |
| Cowrywise | No | No | Partial | Yes | Partial — recurring savings → mutual fund | No | 2 |
| Daviplata/A la Mano/Movii/Powwi/Bold | No | No | No | Yes | No | No | 0 |

**Highest design rigor in this cluster:** Valiu's BTC-hedged synthetic-dollar
construction and Risevest/Cowrywise's recurring-into-fund mechanic are the only
ones with public mechanism-level descriptions. None publish code. None offer
convexity. **The cluster's Numo-rigor ceiling is 2 — informative.** No
closed-source fintech in this set publishes a beta/payoff/Greeks-style analytic
artifact comparable to Numo's documentation.

## 4. UX moat — why a wage earner uses THIS instead of an on-chain hedge

The honest answer is **friction asymmetry**. A Colombian wage earner with
~$200/month savings capacity will pick Littio/Nubank over any on-chain hedge for
six reinforcing reasons:

1. **Onboarding**: Littio onboards in <3 minutes with cédula + selfie ([Littio](https://littio.co/en/)).
   Nubank Colombia onboards inside an existing app already used for COP.
   Belo/Lemon onboard with DNI + biometric. Bitso CO is the most KYC-heavy of
   this group but still phone-number-first. **Abrigo equivalent flow today
   requires wallet creation, seed-phrase custody, gas funding, Panoptic
   position construction — multi-orders-of-magnitude more friction.**

2. **Ticket size**: Littio min $0, Nubank min 10 USDC, Belo min ~$1, Cowrywise
   min ₦100. Premium economics are a non-issue. Abrigo's premium-funded ratchet
   structurally matches this — but only if gas + slippage are abstracted away.

3. **Fiat on/off-ramp UX**: PSE rails to Littio land in seconds; Nubank settles
   intraday COP↔USDC; Belo accepts ARS bank transfer. Abrigo settles on
   Panoptic — there is no native COP↔Panoptic-position rail. *This is the
   single biggest gap.*

4. **Regulatory comfort**: Littio is YC + Circle, Nubank is a regulated bank,
   Bitso/Belo are registered with local fintech authorities. Wage earners in
   Colombia/Argentina are conditioned by 2022's CeFi collapses (Vauld, Celsius
   echoes) and read "Superfinanciera-supervised" as a primary trust signal.
   Permissionless purity is *negative* signal for this cohort until proven
   otherwise.

5. **Brand trust + word-of-mouth**: Nubank's purple card and Daviplata's TV
   spend dwarf any DeFi marketing. Risevest/Cowrywise dominate Nigerian Twitter.

6. **Single-app surface**: A wage earner already has Nequi/Daviplata for COP
   payments. Adding Littio is a *near-zero* cognitive cost (open second app).
   Adding a Panoptic UI is a category change.

**What Abrigo must match or sidestep:** (a) abstract the wallet — embedded
account-abstraction onboarding with cédula-based KYC partner (Truora, Metamap);
(b) PSE/SPEI on-ramp with same-day premium debit; (c) regulatory wrapper that
*reads* as supervised (e.g., SEDPE-licensed front-end + permissionless
back-end); (d) brand the product as "ratchet" not "hedge" — wage earners do not
buy options, they buy *forced savings with upside*; (e) UI that hides Panoptic
entirely — the user sees a single COP balance + "convexity unit" counter.

## 5. Gaps Abrigo fills (relative to this cluster)

- **No convex payoff.** Every product in this cluster is *delta-1 to USD*
  (Littio/Nubank/Belo/Bitso/Yellow Card/Chipper) or *delta-1 to a US asset basket*
  (Risevest/Bamboo/Cowrywise). None pays out *more* in tail-EM-stress states.
  When Argentina's peso devalued 50% overnight, Belo holders made ARS-equivalent
  gains — but those are *linear* in ARS. Abrigo's premium-funded long-gamma /
  perpetual-put converts the same wage premium into *accelerated* capital
  capture during exactly the windows wage earners are most vulnerable.
- **No premium-funded ratchet.** Recurring deposits in this cluster buy more
  *units* of the same exposure. They do not *compound* into a structurally
  different position class. The closest analogs (Risevest DCA, Cowrywise
  circles) still terminate in linear exposure.
- **Custodial risk.** All listed are custodial. The 2022 EM CeFi blowups
  (Buenbit's UST exposure, Valiu's pivot away from savings) demonstrate this is
  a real risk premium wage earners pay implicitly.
- **Dollar-only optionality.** Most products give USD or US-asset exposure.
  Few give *EM-FX-native* exposure (Buenbit's NUARS/NUPEN are exceptions).
  Abrigo's Mento-native (COPm/BRLm/KESm) settlement is a thesis differentiator.
- **Closed-source mechanism.** No product in this cluster publishes code,
  formulas, or β estimates. Abrigo's open-source + Numo-grade documentation is
  a *credibility* differentiator with sophisticated users and regulators.
- **Gated by jurisdiction.** Risevest/Bamboo cannot legally onboard most LATAM
  wage earners. Littio cannot freely onboard Africans. Permissionless settlement
  *is* the cross-corridor advantage.

## 6. Partnership / integration candidates

- **Off-ramp partnerships (highest priority):** [Littio](https://littio.co/) and
  [Bitso](https://bitso.com/) for COP/MXN/ARS rails; [Yellow Card](https://yellowcard.io/)
  for African corridors. All three already custody USDC and could plausibly
  white-label "Abrigo convexity unit" as a *premium-funded savings tier* inside
  their existing app. Yellow Card's [recent Visa deal](https://cointelegraph.com/news/visa-yellow-card-stablecoin-payments-africa)
  signals appetite for consumer-facing structured products.
- **KYC-as-a-service:** Truora (Colombia), Metamap (LATAM-broad), Smile ID
  (Africa) — none surfaced above but all are standard partners for the listed
  fintechs.
- **Tokenized-MMF rails (treasury anchor for premium float):** [OpenTrade](https://www.opentrade.io/)
  is already plumbed into Littio + Belo and would be a natural premium-cash
  manager for an Abrigo treasury before convexity is deployed.
- **White-label candidates:** Cowrywise (recurring savings DNA) and Risevest
  (asset-manager DNA) are the two fintechs whose product mental-model is
  closest to "premium-funded ratchet." A white-labeled Abrigo "Convex Plan"
  inside Cowrywise would let an Abuja wage earner buy convexity from the
  most-trusted savings brand they already use.
- **Bancolombia A la Mano / Daviplata** (long-shot): regulator-blessed pesos
  rails; only realistic via a Superfinanciera sandbox.

## 7. Risk: who could pivot into our lane

**High-risk pivots:**

- **Nubank.** Has 131M users, custodial USDC at 4%, a crypto desk, and Pix
  rails. A "Nu Hedge" product (long-gamma USDC vs BRL via a partner desk) is
  the most plausible incumbent pivot. Nubank's R$45B 2026 Brazil investment
  ([BusinessWire](https://www.businesswire.com/news/home/20260427273702/en/Nubank-to-Invest-R$-45-Billion-in-Brazil-in-2026))
  signals appetite. **Mitigant for Abrigo: open-source mechanism + Mento-native
  EM-pair coverage Nubank cannot easily reproduce inside a banco-múltiplo
  wrapper.**
- **Bitso.** Already has the desk + the LATAM regulatory footprint. A "Bitso+
  Plus" structured-yield product is one product-meeting away. **Mitigant:
  partnership before pivot — Bitso as Abrigo on-ramp.**
- **Lemon Cash.** Already deploys to Morpho ([Morpho story](https://morpho.org/stories/lemon/));
  the leap from Morpho-yield to Panoptic-yield is small for a team that already
  thinks in DeFi primitives. **Highest-rigor pivot threat in this cluster.**
- **Yellow Card.** Stated "earn yield" intent on its product roadmap. Africa-side
  pivot risk concentrated here.

**Lower-risk:**

- Risevest/Bamboo/Cowrywise: regulated as asset managers; convex perps would
  require a new license class.
- Daviplata/A la Mano/Movii/Powwi: bank-subsidiary inertia; no crypto desk.
- Valiu: capital-constrained, narrowing remittance focus.

**Stablecoin integrations to watch:** Meta's [Polygon-routed USDC roll-out in
Colombia and Philippines](https://fortune.com/2026/04/29/meta-stablecoins-crypto-usdc-polygon-solana/),
BTG Pactual's BTG Dol, RLUSD's African expansion via Chipper. Each lowers the
premium-payment friction Abrigo depends on; none introduces convexity. Net:
**this category accelerates Abrigo's on-ramp side and leaves the convex moat
intact.**

## Summary signal for Track 3

Numo-rigor ceiling is **2/5** across the entire cluster. No closed-source EM
fintech publishes mechanism math; none offers convex payoff; none implements a
true premium-funded ratchet. The threat is *UX dominance*, not mechanism
dominance. Abrigo's correct posture is **partner with the on-ramps (Littio,
Bitso, Yellow Card) and out-design the incumbents on the one axis they
structurally cannot match: open-source convex EM-FX-native ratchet logic.**
