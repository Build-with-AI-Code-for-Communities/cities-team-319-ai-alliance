# Assessment of Coral Reef Health: Equipment, Survey Methods and Practical Criteria for Distinguishing Dead Coral in the Context of the Fourth Global Bleaching Event

**AI Alliance (Team 319)** — August 2026

## Abstract

Coral reefs are among the most biologically diverse and economically important marine ecosystems in the world, facing mounting pressure from climate change, ocean acidification, coastal development, and direct human activity. This paper presents a field methodology for assessing reef health, combining in-water survey techniques with satellite-derived heat-stress data. It draws on NOAA Coral Reef Watch (CRW) records of the Fourth Global Coral Bleaching Event (2023-2025), documents the equipment and transect/quadrat methods used to distinguish live coral from dead coral, defines the Coral Mortality Index (CMI), and covers permitting, diver safety, and low-impact field practice. CoralAI, this team's companion application, implements the same NOAA heat-stress thresholds described here as an AI-assisted rapid screening layer that complements — rather than replaces — the structured field methodology below.

## 1. Introduction

Coral reefs cover less than 0.1% of the ocean floor but support roughly 25% of all marine species, provide coastal storm protection, sustain fisheries, and underpin tourism economies. Reef-building corals form a symbiosis with zooxanthellae algae, which supply the coral with food and give it its color. When sea temperatures rise beyond tolerance, this relationship breaks down: the coral expels its algae, loses its pigment, and its white skeleton becomes visible through the translucent tissue. Prolonged thermal stress leads to starvation, disease susceptibility, and death, after which the exposed skeleton is colonized by algae and other organisms.

### Historical trajectory of global bleaching events

| Event | Years | % of Global Reef Area Under Heat Stress |
|---|---|---|
| Event 1 | 1998 | 21.0% |
| Event 2 | 2010 | 37.0% |
| Event 3 | 2014-2017 | 68.2% |
| Event 4 | 2023-2025 | 84.4% |

NOAA Coral Reef Watch recorded the Fourth Global Coral Bleaching Event as affecting 84.4% of the world's coral reefs — the largest and most severe event on record — prompting NOAA to extend its heat-stress alert scale (see Section 5.4).

| Physiological State | Field Visual Indicator | Biological Consequence | NOAA Heat Stress Context |
|---|---|---|---|
| Healthy | Pigmented tissue; polyps active | Structure-building continues | Normal to Bleaching Watch |
| Bleached | Tissue transparent; skeleton visible through it | Growth and reproduction slow | Bleaching Warning / Alert Level 1-2 |
| Recently Dead | Skeleton bare, no tissue | Live area lost; erosion risk begins | Alert Level 3-4 (mortality) |
| Long-Term Dead | Skeleton overgrown by algae/turf | Reef structure and rugosity change | Alert Level 5 (catastrophic mortality) |

Accurately distinguishing live coral cover from dead coral cover in the field is essential for validating satellite-derived heat-stress data and assessing reef survivability.

## 2. Objectives

1. Document the equipment needed for subtidal and deep-water reef assessment.
2. Describe field survey methods: Line Intercept Transects, Quadrat and Photo-Quadrat Sampling, and visual bleaching scoring.
3. Integrate remote-sensing data — NOAA Coral Reef Watch 5km products and Degree Heating Weeks (DHW) — with localized field observations.
4. Establish criteria for distinguishing dead, partially dead, and bleached coral.
5. Provide data-recording forms, percent-cover calculations, and the Coral Mortality Index (CMI).
6. Cover diving safety, environmental care, and regulatory compliance for marine science fieldwork.

## 3. Study Area Framework

Researchers should populate the following fields for each survey site, using site-specific coordinates and historical NOAA Coral Reef Watch data:

- **Site Location:** e.g. Direction Island Reef, Cocos (Keeling) Islands
- **Geographic Coordinates:** e.g. 12°05'14" S, 96°52'55" E
- **Reef Type:** Fringing / Barrier / Patch / Atoll Rim
- **Depth:** Reef Flat (1-3 m), Reef Crest (3-5 m), Fore-Reef Slope (8-15 m)
- **NOAA CRW Virtual Station:** e.g. Cocos (Keeling) Islands Virtual Station
- **Heat Stress History:** e.g. high Degree Heating Weeks during GCBE4 (2023-2025)

*(Field survey maps should show global site location, coastline/watershed context, and individual transect positions.)*

## 4. Materials and Equipment

| Category | Equipment | Purpose |
|---|---|---|
| In-Water Access & Safety | Mask, snorkel, open-heel fins | Visual reconnaissance and shallow-water assessment |
| In-Water Access & Safety | SCUBA assembly (cylinder, regulator, BCD) | Extended sub-surface monitoring |
| In-Water Access & Safety | Surface marker buoy & dive flag | Diver location signaling, vessel awareness |
| Sampling & Metrics | Fibreglass measuring tape (30/50 m) | Linear transect placement |
| Sampling & Metrics | PVC quadrat frames (0.5 x 0.5 m, 1 x 1 m) | Standardized area sampling |
| Sampling & Metrics | Vernier callipers / scale bar | Morphological measurement of colonies |
| Data Recording | Waterproof slates & synthetic paper | In situ data logging |
| Data Recording | CoralWatch Coral Health Chart | Colorimetric bleaching severity reference |
| Digital Imaging | Underwater camera + housing, video lights | Photo-quadrat capture and later analysis |
| Environmental Data | Handheld GPS, multi-parameter sonde | Coordinates; SST, salinity, pH, oxygen |
| Environmental Data | NOAA CRW satellite 5km DHW products | Remote heat-stress context for ground-truthing |

## 5. Field Methodology and Satellite Data Integration

```
Satellite Data (NOAA CRW 5km)  -> SST, HotSpot, and Degree Heating Week context
Line Intercept Transect (LIT)  -> Quantifies benthic substrate composition
Photo-Quadrat Sampling         -> Fixed-area imagery for later annotation/counting
In Situ Bleaching Scoring      -> CoralWatch chart scores feeding the field report
```

### 5.1 Line Intercept Transect (LIT)

1. **Placement:** Lay a measuring tape along a depth contour, kept taut against the substrate.
2. **Data collection:** The surveyor swims the tape, recording (in cm) each point where the substrate category changes.
3. **Categorization:** Live Coral (by genus/growth form), Dead Coral, Algal Turf, Macroalgae, Sand, Rubble, Hard Rock.

Percent cover for substrate category *i*:

```
Cover_i (%) = (sum of intercept lengths for category i / total transect length) x 100
```

### 5.2 Quadrat Sampling

1. **Placement:** 0.5x0.5 m or 1x1 m quadrats placed at regular intervals along the transect.
2. **Visual assessment:** Estimate percent cover of each substrate category within the frame.
3. **Replication:** Multiple quadrats per transect yield mean cover and standard deviation, capturing small-scale variability.

### 5.3 Photo-Transect Photogrammetry

1. **Image capture:** Photograph each quadrat at regular transect intervals.
2. **Annotation:** Analyze images with tools such as CPCe or CoralNet, sampling 20-50 random points per image for substrate classification.

### 5.4 Visual Bleaching Assessment & Satellite Ground-Truthing

Field bleaching observations directly validate global satellite monitoring. NOAA Coral Reef Watch's Bleaching Alert scale (extended after GCBE4 to capture unprecedented heat stress):

| Level | Threshold | Meaning |
|---|---|---|
| Watch | SST > Monthly Mean Maximum | Bleaching possible on the most sensitive reefs |
| Warning | HotSpot > 0 °C | Heat stress accumulating |
| Alert Level 1 | DHW >= 4 °C-weeks | Significant bleaching likely |
| Alert Level 2 | DHW >= 8 °C-weeks | Bleaching and some mortality likely |
| Alert Level 3 | DHW >= 12 °C-weeks | Mortality likely across many species |
| Alert Level 4 | DHW >= 16 °C-weeks | Widespread mortality across many species |
| Alert Level 5 | DHW >= 20 °C-weeks | Near-total mortality risk |

1. **In-water scoring:** Each colony is scored against the CoralWatch Coral Health Chart (1 = bleached, 6 = fully pigmented).
2. **Satellite synthesis:** Field observations are cross-referenced with NOAA CRW's 5km DHW product. High-heat-stress observations can be submitted to NOAA CRW (coralreefwatch@noaa.gov) to help validate satellite models.

> **CoralAI implementation note:** CoralAI's backend (`app/services/noaa_service.py`) queries NOAA CRW's public ERDDAP endpoint for live SST, HotSpot, and DHW at each survey's coordinates, and derives the exact Watch/Warning/Alert Level 1-5 classification above from those values in real time — feeding directly into the app's Coral Risk Score.

## 6. Diagnostic Criteria: Live Coral vs. Dead Coral

```
Benthic object observed
├── Tissue present
│   ├── Full pigment       -> LIVE CORAL
│   └── Loss of pigment    -> BLEACHED CORAL
└── No tissue present
    ├── White skeleton       -> RECENTLY DEAD
    └── Overgrown skeleton   -> LONG-TERM DEAD
```

| Feature | Live Coral | Bleached Coral | Dead Coral |
|---|---|---|---|
| Surface tissue | Intact, opaque, pigmented | Transparent; skeleton visible through it | No live soft tissue present |
| Skeletal state | Corallite detail obscured by tissue | Corallites clearly defined through tissue | Recent: white/clean. Long-term: eroded |
| Colonization | Negligible (protected by mucus layer) | Minimal; increasingly susceptible | Extensive algal turf or macroalgae |

### 6.2 Intermediate States and Confusing Cases

- **Partial death:** A colony with both living and dead sections (or algae-covered sections) should be recorded as a percentage of live surface area, not a binary live/dead call.
- **Disease:** Black Band Disease, White Syndrome, and Stony Coral Tissue Loss Disease (SCTLD) present as a distinct advancing edge across the colony, leaving dead tissue behind it.

## 7. Data Analysis and Reporting

### 7.1 Equations

**Benthic cover percentage** for substrate category *i*:

```
Cover_i (%) = (sum of intercept lengths for category i / total transect length) x 100
```

**Coral Mortality Index (CMI)** — the proportion of surveyed coral cover that is dead:

```
CMI (%) = (DCC / (LCC + DCC)) x 100
```

Where `LCC` = Live Coral Cover (%) and `DCC` = Dead Coral Cover (%).

- CMI < 20%: Low mortality
- CMI 20-50%: Moderate mortality
- CMI > 50%: Severe reef damage

> **Scope note:** CMI requires percent live/dead cover measured across a full transect or set of quadrats — it is a site-level metric, not something a single photo can produce. CoralAI classifies individual photos (Healthy / Partially Bleached / Severely Bleached / Dead Coral / Unknown) as a rapid screening signal; it is not a substitute for a full LIT/quadrat survey when a formal CMI is required.

### 7.2 Field Data Entry Form

```
========================================================================
CORAL REEF HEALTH ASSESSMENT FIELD DATA SHEET
========================================================================
Site Name: ______________________   Date (YYYY-MM-DD): ________________
Latitude/Longitude: _____________   Surveyor Name(s): __________________
Depth (m): _______  Tide State: ___  NOAA CRW Alert Level: _____________
========================================================================
Transect | Segment    | Segment  | Substrate /   | Species /  | Health  | CoralWatch | Notes
ID       | Start (cm) | End (cm) | Coral Category| Genus      | Status  | Score(1-6) |
---------|------------|----------|----------------|------------|---------|------------|-------
T-01     | 0          | 120      | Live Coral     | Acropora   | Live    | 5/6        | colony
         |            |          |                | formosa    |         |            | intact
T-01     | 120        | 185      | Dead Coral     | Acropora sp| Long-   | N/A        | Turf
         |            |          |                |            | Term    |            | algae
T-01     | 185        | 240      | Macroalgae     | Sargassum  | N/A     | N/A        | Dense
         |            |          |                | sp.        |         |            | canopy
T-01     | 240        | 310      | Bleached Coral | Porites    | Bleached| 1/2        | Trans-
         |            |          |                | lutea      |         |            | lucent
T-01     | 310        | 500      | Sand / Rubble  | N/A        | N/A     | N/A        | Unconsol.
```

## 8. Regulatory, Safety, and Environmental Practice

### 8.1 Permits and Compliance

- Obtain research permits from the relevant marine area managers, fisheries departments, or environmental authorities before starting fieldwork.
- Follow access rules for marine protected areas, reserves, and traditional sea territories.

### 8.2 Diver Safety

- All science divers require appropriate training/certification (e.g. PADI Advanced Open Water, AAUS Scientific Diver) and a current dive medical.
- Observe depth limits, bottom time, dive-computer guidance, safety stops, and the buddy system.
- Maintain an emergency action plan: oxygen kit, first aid, working communications, and a route to the nearest hospital.

### 8.3 Low-Impact Field Methods

- Maintain neutral buoyancy to avoid fin contact with fragile coral; secure tapes, slates, and camera gear so nothing drags across the reef.
- Use reef-safe sunscreen free of oxybenzone and octinoxate.
- Rinse and disinfect dive gear, wetsuits, and tools with fresh water between sites to prevent spreading coral disease or invasive algae.

## 9. Discussion Framework

```
Synthesize field findings
├── Local Cover:  quantify LCC vs DCC, calculate CMI
├── Driver Link:  correlate field cover with SST, DHW, pH, land-use
└── Global Context: compare local metrics against NOAA CRW GCBE4 data (~84.4% impacted)
```

Researchers are encouraged to use this framework to contextualize site-level findings within the documented global thermal-stress trends of the Fourth Global Coral Bleaching Event.

## 10. Conclusion

Reliable coral reef monitoring combines standardized equipment, transect and quadrat methods, and clear criteria for distinguishing live from dead coral. Paired with satellite products such as NOAA Coral Reef Watch's Degree Heating Weeks, field data lets researchers place a single reef's condition within the broader context of global heat-stress events. Conducted safely, in compliance with local regulations, and with careful low-impact technique, this methodology yields data that supports both local reef protection and global monitoring efforts — the same NOAA thresholds it documents are implemented directly in CoralAI's risk engine (Section 5.4).

## References

- English, S., Wilkinson, C., & Baker, V. (Eds.). (1997). *Survey Manual for Tropical Marine Resources*. Australian Institute of Marine Science.
- Hill, J., & Wilkinson, C. (2004). *Methods for Ecological Monitoring of Coral Reefs*. Australian Institute of Marine Science.
- Hodgson, G., Hill, J., Kiene, W., Maun, L., Mihaly, J., Liebeler, J., Shuman, C., & Torres, R. (2006). *Reef Check Instruction Manual: A Guide to Reef Check Coral Reef Monitoring*. Reef Check Foundation.
- National Oceanic and Atmospheric Administration (NOAA) Coral Reef Watch. (2026). *Global Coral Bleaching Status Update & Data Submission*. U.S. Department of Commerce. https://coralreefwatch.noaa.gov/satellite/research/coral_bleaching_report.php
- NOAA National Environmental Satellite, Data and Information Service (NESDIS). (2026). *World's Fourth Mass Coral Bleaching Event Likely Ended in 2025*. National Oceanic and Atmospheric Administration. https://www.nesdis.noaa.gov/news/worlds-fourth-mass-coral-bleaching-event-likely-ended-2025
- Siebeck, U.E., Marshall, N.J., Kluter, A., & Hoegh-Guldberg, O. (2006). Monitoring coral bleaching using a colour reference card. *Coral Reefs*, 25(3), 453-460.
