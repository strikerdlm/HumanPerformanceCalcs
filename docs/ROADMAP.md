# 🚀 Aerospace Medicine & Human Performance Calculator Suite — Development Roadmap

> **Document Status**: Living Document
> **Last Updated**: December 2025
> **Maintainer**: Dr. Diego Malpica

---

## Executive Summary

This roadmap outlines proposed enhancements based on a comprehensive review of scientific literature in aerospace medicine, occupational physiology, and human performance. The recommendations are organized by priority, complexity, and scientific domain.

### Current State Analysis

The application currently includes **29+ validated calculators** across:

- Atmospheric & Physiological (10 calculators)
- Clinical Calculators (6 calculators)
- Occupational Health & Safety (6 calculators)
- Environmental Monitoring (4 calculators)
- Fatigue & Circadian (3 calculators)

### Identified Gaps

Based on literature review, the following domains have significant potential for expansion:

1. Acceleration physiology (G-force effects beyond tolerance time)
2. Space medicine specific tools
3. Advanced thermoregulation models
4. Sensory/vision physiology
5. Vibration exposure assessment
6. Enhanced fatigue prediction models

---

## Phase 1: High-Priority Additions (0-6 months)

### 1.1 Predicted Heat Strain (PHS) Model — ISO 7933:2023

**Scientific Basis**: The PHS model is the current ISO standard for analytical determination of thermal stress in hot environments, superseding older indices for occupational settings.

**References**:

- ISO 7933:2023 — *Ergonomics of the thermal environment — Analytical determination and interpretation of heat stress using calculation of the predicted heat strain*
- Malchaire, J., Piette, A., Kampmann, B., et al. (2001). Development and validation of the predicted heat strain model. *Annals of Occupational Hygiene*, 45(2), 123-135.

**Key Features**:

- Core temperature prediction over exposure duration
- Required sweat rate calculation (SWreq)
- Maximum allowable exposure time
- Water loss estimation

**Complexity**: Medium
**Integration Priority**: High (extends existing WBGT capability)
**Status (App)**: Live — implemented in the Streamlit UI (Environmental Monitoring + Simulation Studio)

---

### 1.2 Universal Thermal Climate Index (UTCI)

**Scientific Basis**: UTCI is the state-of-the-art outdoor thermal comfort index, accounting for radiation, wind, humidity, and metabolic rate.

**References**:

- Jendritzky, G., de Dear, R., & Havenith, G. (2012). UTCI—why another thermal index? *International Journal of Biometeorology*, 56(3), 421-428.
- Bröde, P., Fiala, D., Błażejczyk, K., et al. (2012). Deriving the operational procedure for the Universal Thermal Climate Index (UTCI). *International Journal of Biometeorology*, 56(3), 481-494.

**Key Features**:

- 10-parameter calculation
- Accounts for clothing adaptation
- Valid across full range of outdoor conditions
- Standardized stress categories

**Complexity**: High
**Integration Priority**: High (complements WBGT for outdoor assessment)
**Status (App)**: Live — implemented in the Streamlit UI (Environmental Monitoring)

---

### 1.3 Cold Water Immersion Survival Time

**Scientific Basis**: Critical for aviation over water and maritime operations. Based on Hayward-Tikuisis survival prediction models.

**References**:

- Tikuisis, P. (1997). Prediction of survival time at sea based on observed body cooling rates. *Aviation, Space, and Environmental Medicine*, 68(5), 441-448.
- Hayward, J. S., Eckerson, J. D., & Collis, M. L. (1975). Effect of behavioral variables on cooling rate of man in cold water. *Journal of Applied Physiology*, 38(6), 1073-1077.
- Xu, X., Tikuisis, P., & Giesbrecht, G. (2005). A mathematical model for human brain cooling during cold-water near-drowning. *Journal of Applied Physiology*, 99(4), 1428-1435.

**Key Features**:

- Water temperature input
- Clothing insulation factor
- Body composition adjustment
- Predicted survival time curves
- Hypothermia stage timeline

**Complexity**: Medium
**Integration Priority**: High (critical for aviation safety planning)
**Status (App)**: Live — implemented in the Streamlit UI (Environmental Monitoring)

---

### 1.4 Bühlmann ZH-L16 Decompression Algorithm

**Scientific Basis**: Industry-standard decompression model used in modern dive computers and altitude decompression planning.

**References**:

- Bühlmann, A. A. (1984). *Decompression-Decompression Sickness*. Springer-Verlag.
- Bühlmann, A. A. (2002). *Tauchmedizin: Barotrauma, Gasembolie, Dekompression, Dekompressionskrankheit* (5th ed.). Springer.
- Gerth, W. A., & Doolette, D. J. (2007). VVal-18 and VVal-18M thalmann algorithm-based air decompression tables and procedures. *Navy Experimental Diving Unit Technical Report*, NEDU TR 07-09.

**Key Features**:

- 16 tissue compartment modeling
- Gradient Factor support (GF-Lo, GF-Hi)
- Altitude adaptation corrections
- Conservative factor adjustments
- Real-time saturation tracking

**Complexity**: High
**Integration Priority**: Medium (extends existing tissue ratio calculator)
**Status (App)**: Live — implemented in the Streamlit UI (Atmospheric & Physiological)

---

### 1.5 Anti-G Straining Maneuver (AGSM) Effectiveness Model

**Scientific Basis**: Quantifies the benefit of AGSM techniques on G-tolerance.

**References**:

- Wood, E. H., Lambert, E. H., Baldes, E. J., & Code, C. F. (1946). Effects of acceleration in relation to aviation. *Federation Proceedings*, 5, 327-344.
- Whinnery, J. E. (1991). Methods for describing and quantifying +Gz-induced loss of consciousness. *Aviation, Space, and Environmental Medicine*, 62(8), 738-742.
- Eiken, O., & Mekjavic, I. B. (2016). Ischaemia-reperfusion and G-LOC: a review of the pathophysiology. *Aviation, Space, and Environmental Medicine*, 87(6), 584-594.

**Key Features**:

- Baseline G-tolerance estimation
- AGSM technique effectiveness rating
- Anti-G suit contribution
- Combined protection calculation
- G-tolerance envelope visualization

**Complexity**: Medium
**Integration Priority**: High (critical for fighter pilot operations)
**Status (App)**: Live — implemented in the Streamlit UI (Atmospheric & Physiological)

---

### 1.6 Spatial Disorientation (SD) Risk Assessment

**Scientific Basis**: Quantitative model for spatial disorientation risk based on vestibular physiology and flight conditions.

**References**:

- Benson, A. J. (1999). Spatial disorientation—common illusions. In: Ernsting, J., Nicholson, A. N., & Rainford, D. J. (Eds.), *Aviation Medicine* (3rd ed., pp. 437-454). Butterworth-Heinemann.
- Previc, F. H., & Ercoline, W. R. (2004). *Spatial Disorientation in Aviation*. Progress in Astronautics and Aeronautics, Vol. 203. AIAA.
- Cheung, B. (2013). Spatial disorientation: more than just illusion. *Aviation, Space, and Environmental Medicine*, 84(11), 1211-1214.
- Federal Aviation Administration (FAA). Spatial Disorientation — Airman Education Programs. https://www.faa.gov/pilots/training/airman_education/topics_of_interest/spatial_disorientation
- Houben, M. M. J., Meskers, A. J. H., Bos, J. E., & Groen, E. L. (2022). The perception threshold of the vestibular Coriolis illusion. *Journal of Vestibular Research*. (PubMed: 34924407)
- StatPearls. Physiology of Spatial Orientation. NCBI Bookshelf. https://www.ncbi.nlm.nih.gov/books/NBK518976/

**Key Features**:

- Flight condition inputs (IMC, night, NVG)
- Vestibular conflict probability
- Time since last horizon reference
- SD type classification
- Recommended countermeasures

**Complexity**: Medium
**Integration Priority**: High (addresses major cause of aviation mishaps)
**Status (App)**: Live — implemented in the Streamlit UI (Risk Assessment Tools)

---

## Phase 2: Medium-Priority Additions (6-12 months)

### 2.1 SAFTE/FAST Fatigue Model Integration

**Scientific Basis**: The Sleep, Activity, Fatigue, and Task Effectiveness (SAFTE) model and its Fatigue Avoidance Scheduling Tool (FAST) implementation are validated biomathematical fatigue prediction systems.

**References**:

- Hursh, S. R., Redmond, D. P., Johnson, M. L., et al. (2004). Fatigue models for applied research in warfighting. *Aviation, Space, and Environmental Medicine*, 75(3), A44-A53.
- Van Dongen, H. P. A., Maislin, G., Mullington, J. M., & Dinges, D. F. (2003). The cumulative cost of additional wakefulness: dose-response effects on neurobehavioral functions and sleep physiology from chronic sleep restriction and total sleep deprivation. *Sleep*, 26(2), 117-126.

**Key Features**:

- Sleep history integration
- Performance effectiveness prediction
- Crew scheduling optimization
- Risk threshold alerting
- Multi-day forecasting

**Complexity**: High
**Integration Priority**: Medium (extends existing circadian models)

---

### 2.2 Night Vision Goggle (NVG) Performance Calculator

**Scientific Basis**: Quantifies visual performance degradation with NVG use under various conditions.

**References**:

- Rash, C. E., Verona, R. W., & Crowley, J. S. (1990). Human factors and safety considerations of night vision systems flight using thermal imaging systems. *USAARL Technical Report*, 90-10.
- Pinkus, A. R., & Task, H. L. (1998). Display system image quality metrics. *Human Factors Engineering Technical Advisory Group Report*.
- McLean, W. E. (2014). *Night Vision Manual for the Flight Surgeon*. USAFSAM Special Report.

**Key Features**:

- Ambient illumination assessment
- Visual acuity prediction
- Contrast sensitivity degradation
- Detection range estimation
- Minimum lighting requirements

**Complexity**: Medium
**Integration Priority**: Medium (specialized but critical for rotary-wing operations)

---

### 2.3 Whole-Body Vibration Exposure (ISO 2631)

**Scientific Basis**: ISO standard for evaluation of human exposure to whole-body vibration, critical for rotorcraft and ground vehicle operations.

**References**:

- ISO 2631-1:1997 — *Mechanical vibration and shock — Evaluation of human exposure to whole-body vibration — Part 1: General requirements*
- Griffin, M. J. (2012). *Handbook of Human Vibration*. Academic Press.
- Mansfield, N. J. (2005). *Human Response to Vibration*. CRC Press.

**Key Features**:

- Frequency-weighted acceleration input
- Daily exposure calculation (A(8))
- Health guidance caution zones
- Comfort assessment
- Spinal loading estimation

**Complexity**: Medium
**Integration Priority**: Medium (important for helicopter and ground vehicle operations)

---

### 2.4 Visual Acuity at Altitude Calculator

**Scientific Basis**: Hypoxia-induced degradation of visual function at altitude.

**References**:

- Kobrick, J. L., & Appleton, B. (1971). Effects of extended hypoxia on visual performance and retinal vascular state. *Journal of Applied Physiology*, 31(3), 357-362.
- Connolly, D. M., & Hosking, S. L. (2008). Oxygenation and visual function. *Aviation, Space, and Environmental Medicine*, 79(7), 735-743.
- Connolly, D. M., Barbur, J. L., Hosking, S. L., & Moorhead, I. R. (2008). Mild hypoxia impairs chromatic sensitivity in the mesopic range. *Investigative Ophthalmology & Visual Science*, 49(2), 820-827.

**Key Features**:

- Altitude input
- Supplemental oxygen status
- Visual acuity decrement prediction
- Color vision degradation assessment
- Dark adaptation impact

**Complexity**: Low
**Integration Priority**: Medium (extends altitude physiology capabilities)

---

### 2.5 Crew Duty Time Limit Calculators

**Scientific Basis**: Regulatory compliance calculators for FAA (14 CFR 117), EASA (ORO.FTL), and other aviation authorities.

**References**:

- FAA. (2012). Flightcrew Member Duty and Rest Requirements. *14 CFR Part 117*.
- EASA. (2016). Flight and Duty Time Limitations and Rest Requirements. *Commission Regulation (EU) No 83/2014*.
- Caldwell, J. A., Mallis, M. M., Caldwell, J. L., et al. (2009). Fatigue countermeasures in aviation. *Aviation, Space, and Environmental Medicine*, 80(1), 29-59.

**Key Features**:

- Flight duty period calculation
- Rest requirement determination
- Cumulative limits tracking (7/28/365 day)
- Window of circadian low (WOCL) considerations
- Extension conditions assessment

**Complexity**: Medium
**Integration Priority**: Medium (operational planning tool)

---

### 2.6 Alveolar-arterial Oxygen Gradient (A-a gradient)

**Scientific Basis**: Important clinical parameter for assessing gas exchange efficiency.

**References**:

- West, J. B. (2011). *Respiratory Physiology: The Essentials* (9th ed.). Lippincott Williams & Wilkins.
- Mellemgaard, K. (1966). The alveolar-arterial oxygen difference: its size and components in normal man. *Acta Physiologica Scandinavica*, 67(1), 10-20.

**Key Features**:

- Age-adjusted normal range
- Altitude correction
- FiO₂ adjustment
- Clinical interpretation guidance
- Trending capability

**Complexity**: Low
**Integration Priority**: Medium (clinical utility)

---

### 2.7 Oxygen Delivery Index (DO₂I)

**Scientific Basis**: Quantifies oxygen delivery to tissues, critical for critical care and high-altitude physiology.

**References**:

- Shepherd, S. J., & Pearse, R. M. (2009). Role of central and mixed venous oxygen saturation measurement in perioperative care. *Anesthesiology*, 111(3), 649-656.
- Grocott, M. P., Martin, D. S., Levett, D. Z., et al. (2009). Arterial blood gases and oxygen content in climbers on Mount Everest. *New England Journal of Medicine*, 360(2), 140-149.

**Key Features**:

- Hemoglobin input
- Cardiac output estimation
- Oxygen saturation integration
- Altitude adjustment
- Critical threshold alerting

**Complexity**: Low
**Integration Priority**: Medium (clinical/research utility)

---

## Phase 3: Advanced Features (12-24 months)

### 3.1 Space Medicine Module

**Scientific Basis**: Dedicated calculator suite for spaceflight-specific physiological challenges.

**References**:

- Buckey, J. C. (2006). *Space Physiology*. Oxford University Press.
- Clément, G. (2011). *Fundamentals of Space Medicine* (2nd ed.). Springer.
- Thirsk, R., Kuipers, A., Mukai, C., & Williams, D. (2009). The space-flight environment: the International Space Station and beyond. *Canadian Medical Association Journal*, 180(12), 1216-1220.

**Sub-calculators**:

#### 3.1.1 Bone Loss Prediction

- Monthly bone mineral density loss estimation
- Countermeasure effectiveness modeling
- Fracture risk assessment post-flight

#### 3.1.2 Cardiovascular Deconditioning

- Orthostatic tolerance prediction
- Cardiac output deconditioning timeline
- Re-adaptation requirements

#### 3.1.3 Spaceflight-Associated Neuro-ocular Syndrome (SANS)

- Risk factor scoring
- Intracranial pressure estimation
- Visual changes prediction

#### 3.1.4 Galactic Cosmic Radiation (GCR) Exposure

- Mission dose accumulation
- Organ-specific equivalent doses
- Cancer risk estimation (REID)

#### 3.1.5 Space Motion Sickness Prediction

- Susceptibility scoring
- Adaptation timeline
- Countermeasure recommendations

**Complexity**: Very High
**Integration Priority**: Long-term (specialized user base)

---

### 3.2 Motion Sickness Integration (MSSQ Enhancement)

**Scientific Basis**: The Motion Sickness Susceptibility Questionnaire (MSSQ) already exists in legacy apps; this integrates it into the main application with enhanced predictive capabilities.

**References**:

- Golding, J. F. (1998). Motion sickness susceptibility questionnaire revised and its relationship to other forms of sickness. *Brain Research Bulletin*, 47(5), 507-516.
- Golding, J. F. (2006). Motion sickness susceptibility. *Autonomic Neuroscience*, 129(1-2), 67-76.
- Reason, J. T., & Brand, J. J. (1975). *Motion Sickness*. Academic Press.

**Key Features**:

- MSSQ-short questionnaire interface
- Individual susceptibility percentile
- Situation-specific risk prediction
- Prophylactic recommendations
- Habituation tracking

**Complexity**: Medium
**Integration Priority**: Medium (legacy app migration)

---

### 3.3 Psychomotor Vigilance Task (PVT) Performance Prediction

**Scientific Basis**: PVT is the gold standard for measuring fatigue-related performance degradation.

**References**:

- Dinges, D. F., & Powell, J. W. (1985). Microcomputer analyses of performance on a portable, simple visual RT task during sustained operations. *Behavior Research Methods, Instruments, & Computers*, 17(6), 652-655.
- Basner, M., & Dinges, D. F. (2011). Maximizing sensitivity of the psychomotor vigilance test (PVT) to sleep loss. *Sleep*, 34(5), 581-591.
- Lim, J., & Dinges, D. F. (2008). Sleep deprivation and vigilant attention. *Annals of the New York Academy of Sciences*, 1129, 305-322.

**Key Features**:

- Sleep history integration
- Predicted reaction time
- Lapse probability
- Time-on-task effects
- Recovery prediction

**Complexity**: High
**Integration Priority**: Medium (research tool)

---

### 3.4 Wells Score Calculators (DVT/PE)

**Scientific Basis**: Important clinical decision tools for venous thromboembolism risk assessment, relevant to long-duration flights and immobilization.

**References**:

- Wells, P. S., Anderson, D. R., Rodger, M., et al. (2003). Evaluation of D-dimer in the diagnosis of suspected deep-vein thrombosis. *New England Journal of Medicine*, 349(13), 1227-1235.
- Wells, P. S., Anderson, D. R., Rodger, M., et al. (2001). Excluding pulmonary embolism at the bedside without diagnostic imaging: management of patients with suspected pulmonary embolism presenting to the emergency department by using a simple clinical model and D-dimer. *Annals of Internal Medicine*, 135(2), 98-107.

**Key Features**:

- DVT probability scoring
- PE probability scoring
- Risk stratification
- D-dimer threshold guidance
- Travel-related risk adjustment

**Complexity**: Low
**Integration Priority**: Medium (clinical utility for travel medicine)

---

### 3.5 High-Altitude Cerebral Edema (HACE) Risk Score

**Scientific Basis**: Complements existing AMS and HAPE calculators.

**References**:

- Hackett, P. H., & Roach, R. C. (2004). High altitude cerebral edema. *High Altitude Medicine & Biology*, 5(2), 136-146.
- Wilson, M. H., Newman, S., & Imray, C. H. (2009). The cerebral effects of ascent to high altitudes. *Lancet Neurology*, 8(2), 175-191.
- Willmann, G., Fischer, M. D., Schatz, A., et al. (2014). Retinal vessel changes in altitude-associated retinal hemorrhages. *Investigative Ophthalmology & Visual Science*, 55(3), 1836-1843.

**Key Features**:

- Ascent rate assessment
- AMS progression tracking
- Neurological symptom scoring
- Descent urgency classification
- Treatment recommendations

**Complexity**: Medium
**Integration Priority**: Low (extension of existing altitude tools)

---

## Phase 4: Platform Enhancements (Ongoing)

### 4.1 API Development

**Objective**: RESTful API for programmatic access to calculator functions.

**Features**:

- OpenAPI/Swagger documentation
- Rate limiting
- Authentication options
- Batch calculation support

**Integration Priority**: High

---

### 4.2 Mobile Application

**Objective**: Native iOS/Android applications for field use.

**Features**:

- Offline calculation capability
- Quick reference guides
- Push notifications for limits
- Data synchronization

**Integration Priority**: Medium

---

### 4.3 Database Integration

**Objective**: Persistent storage for longitudinal tracking.

**Features**:

- Individual exposure history
- Trend analysis
- Regulatory reporting
- Export capabilities (FHIR, HL7)

**Integration Priority**: Medium

---

### 4.4 Machine Learning Enhancements

**Objective**: Data-driven model refinement.

**Features**:

- Individual susceptibility modeling
- Outcome prediction improvement
- Anomaly detection
- Personalized recommendations

**Integration Priority**: Long-term

---

## Implementation Recommendations

### Technical Considerations

1. **Modular Architecture**: Maintain the existing `calculators/` package structure for new additions
2. **Type Safety**: Continue using strict typing with dataclasses for results
3. **Validation**: Implement comprehensive input validation using existing `utils.py` patterns
4. **Testing**: Maintain ≥90% test coverage with pytest; add property-based tests for numerical algorithms
5. **Documentation**: Include peer-reviewed references for all new formulas

### Development Workflow

1. Create calculator module in `calculators/` directory
2. Add comprehensive unit tests in `tests/`
3. Integrate into Streamlit UI
4. Update README.md with new calculator documentation
5. Add to CLI interface via `run_calculator.py`

### Quality Assurance

- All calculations must match published reference implementations within 1% tolerance
- Boundary conditions must be explicitly tested
- Edge cases (zero, negative, extreme values) must be handled gracefully
- Performance testing for time-critical calculations

---

## Priority Summary Table

| Calculator                  | Phase | Complexity | Priority  | Domain        |
| --------------------------- | ----- | ---------- | --------- | ------------- |
| PHS Model (ISO 7933)        | 1     | Medium     | High      | Heat Stress   |
| UTCI                        | 1     | High       | High      | Thermal       |
| Cold Water Survival         | 1     | Medium     | High      | Cold Stress   |
| Bühlmann ZH-L16            | 1     | High       | Medium    | Decompression |
| AGSM Effectiveness          | 1     | Medium     | High      | G-Force       |
| Spatial Disorientation Risk | 1     | Medium     | High      | Vestibular    |
| SAFTE/FAST Model            | 2     | High       | Medium    | Fatigue       |
| NVG Performance             | 2     | Medium     | Medium    | Vision        |
| Whole-Body Vibration        | 2     | Medium     | Medium    | Vibration     |
| Visual Acuity at Altitude   | 2     | Low        | Medium    | Vision        |
| Crew Duty Time Limits       | 2     | Medium     | Medium    | Regulatory    |
| A-a Gradient                | 2     | Low        | Medium    | Respiratory   |
| Oxygen Delivery Index       | 2     | Low        | Medium    | Respiratory   |
| Space Medicine Module       | 3     | Very High  | Long-term | Space         |
| MSSQ Integration            | 3     | Medium     | Medium    | Motion        |
| PVT Prediction              | 3     | High       | Medium    | Fatigue       |
| Wells Scores                | 3     | Low        | Medium    | Clinical      |
| HACE Risk                   | 3     | Medium     | Low       | Altitude      |

---

## References Summary

### Thermal Physiology

1. ISO 7933:2023 - Predicted Heat Strain
2. Jendritzky et al. (2012) - UTCI
3. Tikuisis (1997) - Cold water survival

### Acceleration Physiology

4. Wood et al. (1946) - G-tolerance foundations
5. Whinnery (1991) - G-LOC quantification
6. Benson (1999) - Spatial disorientation

### Fatigue & Human Factors

7. Hursh et al. (2004) - SAFTE model
8. Van Dongen et al. (2003) - Sleep debt effects
9. Dinges & Powell (1985) - PVT methodology

### Vision & Sensory

10. Rash et al. (1990) - NVG considerations
11. Connolly & Hosking (2008) - Hypoxia and vision

### Decompression

12. Bühlmann (1984) - ZH-L16 algorithm
13. Gerth & Doolette (2007) - Validation studies

### Space Medicine

14. Buckey (2006) - Space physiology fundamentals
15. Clément (2011) - Space medicine overview

### Vibration

16. ISO 2631-1:1997 - Whole-body vibration
17. Griffin (2012) - Human vibration handbook

### Clinical

18. Wells et al. (2003) - DVT clinical rules
19. West (2011) - Respiratory physiology

---

## Version History

| Version | Date          | Changes                  |
| ------- | ------------- | ------------------------ |
| 1.1     | December 2025 | Initial roadmap creation |

---

## Contributing

Contributions to this roadmap are welcome. Please consider:

1. **Scientific Rigor**: All proposed calculators must have peer-reviewed scientific basis
2. **Clinical Relevance**: Tools should address real operational or clinical needs
3. **Validation Data**: Proposals should include methods for validation
4. **Implementation Feasibility**: Consider computational requirements and data availability

---

*This roadmap represents a comprehensive analysis of opportunities to enhance the Aerospace Medicine & Human Performance Calculator Suite. Priorities may be adjusted based on user feedback, available resources, and emerging scientific developments.*
