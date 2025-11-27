# Predictive model for estimating the risk of high-altitude pulmonary edema: a single-centre retrospective outcome-reporting study

Yangzong Suona<sup>1</sup>, Luobu Gesang<sup>1,2,3</sup>, Zhuoga Danzeng<sup>1,2</sup>, Bai Ci<sup>3</sup>, Quzong Zhaxi<sup>3</sup>, Ju Huang<sup>3</sup>, Rui Zhang<sup>1</sup>

<sup>1</sup>High Altitude Medical Research Institute, Tibet Autonomous Region People’s Hospital, Lhasa, China  
<sup>2</sup>Department of Mountain Sickness and Cardiology, Tibet Autonomous Region People’s Hospital, Lhasa, China  
<sup>3</sup>Key Laboratory of Translational Medicine for Human Adaptation to the High-altitude of Tibet Autonomous Region, Tibet Autonomous Region People’s Hospital, Lhasa, China

**Correspondence to:**  
Professor Luobu Gesang; gesang5354@ sina.com

---

## ABSTRACT

**Objective**  
To develop the first prediction model based on the common clinical symptoms of high-altitude pulmonary edema (HAPE), enabling early identification and an easy-to-execute self-risk prediction tool.

**Methods**  
A total of 614 patients who consulted People’s Hospital of Tibet Autonomous Region between January 2014 and April 2022 were enrolled. Out of those, 508 patients (416 males and 92 females) were diagnosed with HAPE and 106 were patients without HAPE (33 females and 72 males). They were randomly distributed into training (n=431) and validation (n=182) groups. Univariate and multivariate analysis were used to screen predictors of HAPE selected from the 36 predictors; nomograms were established based on the results of multivariate analysis. The receiver operating characteristic curve (ROC) was developed to obtain the area under the ROC curve (AUC) of the predictive model, and its predictive power was further evaluated by calibrating the curve, while the Decision Curve Analysis (DCA) was developed to evaluate the clinical applicability of the model, which was visualised by nomogram.

**Results**  
All six predictors were significantly associated with the incidence of HAPE, and two models were classified according to whether the value of SpO₂ (percentage of oxygen in the blood) was available as the target population. Both could accurately predict the risk of HAPE. In the validation cohort, the AUC of model 1 was 0.934, with 95% CI (0.848 to 1.000), and model 2 had an AUC of 0.899, 95% CI (0.779 to 0.999). Calibration plots showed that the predicted and actual HAPE probabilities fitted well with internal validation, and the clinical decision curve shows intervention in the risk range of 0.01–0.98, resulting in a net benefit of nearly 99%.

**Conclusion**  
The recommended prediction model (nomogram) could estimate the risk of HAPE with good precision, high discrimination and possible clinical applications for patients with HAPE. More importantly, it is an easy-to-execute scoring tool for individuals without medical professionals’ support.

---

### STRENGTHS AND LIMITATIONS OF THIS STUDY

- The study acknowledges potential information bias due to missing predictor variables despite using multiple imputations.
- To achieve a more accurate optimisation, further population expansion is necessary beyond the current sample size.
- The study recommends increasing the population size to improve the accuracy of the model.
- The study highlights the need for future validation in multiple centres to assess the stability and generalisability of the model.

---

## INTRODUCTION

Every year, millions travel to high altitudes for a wide range of reasons, including hiking, skiing, sightseeing, pilgrimages and work. For example, in Europe, the Alps receive nearly 12 million visitors annually.<sup>1</sup> Also, reports state that over 100 million people visit the USA’ high-altitude mountains annually for work or recreational activities. Over a quarter of the land area in China is covered by mountains, also popular tourist destinations. According to 2021 statistical yearbook of the Tibet Autonomous Region (TAR), this region received 41 534 400 tourists in 2021.<sup>2</sup> Most people consider themselves prepared for the physical challenges of high-altitude travel and are unaware of the significant health hazards and possible consequences caused by high altitude.<sup>3</sup>

High-altitude pulmonary edema (HAPE) is a severe form of high-altitude illness typically occurring in people at altitudes of 2500 meters or higher. Up to 7% of people develop HAPE on their first ascent to high altitudes above 4000 m, and people who have previously had HAPE have a 60% likelihood of developing symptoms again.<sup>4</sup> If left untreated, it can lead to mortality in 50% of affected individuals.<sup>4</sup> It has been reported that most patients who can descend from high altitude or receive professional medical care on the spot still experience further development of symptoms; sometimes, death...

---

## METHODS AND MATERIALS

### Patient and public involvement

None.

### Study design

This study is a single-centre retrospective analysis of an outcome-reporting study. The People’s Hospital of TAR, the largest medical centre with 20% coverage of all consultations and treatments in Tibet, is the centre of this study. In this study, we collected 508 cases of patients diagnosed with HAPE and 106 cases of altitude illness, presumably non-HAPE related. The test subjects were patients examined at the TAR People’s Hospital between January 2014 and April 2022 who consulted the hospital with symptoms related to altitude sickness, that is, headache, dizziness, cough, chest tightness, shortness of breath and dyspnoea. The inclusion criteria were: (1) lowlanders rapidly ascending to high altitude; (2) ≥14 years old, gender is irrelevant (3) screening in Electronic Medical Record (EMR) system with a first diagnosis of HAPE and/or altitude sickness. Exclusion criteria were: (1) all paediatric cases; (2) patients with chronic obstructive pulmonary disease, heart failure or cancer.

No patients or members of the general public were involved in the planning, execution, reporting or dissemination of this study.

### Data collection

Baseline medical information, including age, sex, nationality, body mass index, clinical symptoms (including fever, fatigue, loss of appetite, nausea, sleep disturbance, dizziness, cough, chest tightness, shortness of breath, palpitation, bluish lips, coughing sputum; vital signs including temperature, heart rate, SpO₂, systolic blood pressure, diastolic blood pressure (DBP)) and demographic information (including the altitude of residence, altitude of disease onset, transport to the plateau, whether showered and caught cold after entering the plateau, number of days/time taken for a first symptom to appear after the patient arrived at the plateau) and others (history of smoking, drinking, hypertension, diabetes, chronic respiratory disease and chronic liver disease) were collected. Variables with missing>20% of data were excluded. The variables with missing data<20% were imputed using the random forest method.[11]

### HAPE clinical diagnostic criteria

HAPE clinical diagnostic criteria were: 
1. Recent arrival at a plateau (above 3000 m above sea level) or higher altitude;
2. The presence of exertional dyspnoea, cough, cough white or pink foamy sputum, and in severe cases, resting dyspnoea and tachypnoea/tachycardia; physical examination: central cyanosis, shortness of breath, tachycardia, decreased breath sounds in the stage of interstitial pulmonary oedema, and audible wet rales in the lungs in the stage of alveolar oedema;
3. Ancillary examination: chest X-ray (unilateral or bilateral infiltration shadow centred on the pulmonary hilum, often diffuse and irregularly distributed, or fused into a large patchy shadow. The heart shadow is mostly normal, and there are also signs of pulmonary hypertension and enlargement of the right ventricle, scattered flake ground-glass density shadow in both lungs);
4. Rule out other causes acute respiratory distress syndrome, cardiogenic pulmonary oedema, and severe pneumonia;
5. Remission by transfer to plains or low altitude.

### Statistical analysis

This study performed statistical analysis using the R programming software (V.3.6, http://www.R-project.org). Normally distributed measures were expressed as mean±SD. T-test was used for comparison between groups and expressed non-normally distributed as median (IQR), and Wilcoxon rank-sum test for comparison between groups. The categorical data were expressed as frequencies and percentages (%), and the $\chi^2$ test was used for between-group comparisons. Logistic regression was applied to screen out independent risk factors for HAPE, construct a prediction model, and visualise the model using a nomogram. We used the AUC and Hosmer-Lemeshow goodness-of-fit test to evaluate the model’s discrimination and calibration.[12] The study implemented an internal validation of the model through the Bootstrap sampling method. The clinical effectiveness of the model in predicting HAPE risk was determined by the net benefit (NB) at different threshold probabilities and by performing a decision curve analysis.[13] The reporting and analysis of study results were conducted according to the STROPE and CHAMP checklists. All p values were

---

[image: 
A. Flow chart of patient enrolment.
B. Distribution of age in patients with and without HAPE.
C. Distribution of SpO₂ in patients with and without HAPE.
The label A stands for patients without HAPE, while H stands for patients with HAPE.]

**Figure 1**  
(A) Flow chart of patient enrolment. (B) Distribution of age in patients with and without HAPE. (C) Distribution of SpO₂ in patients with and without HAPE. The label A stands for patients without HAPE, while H stands for patients with HAPE.

---

### Data preprocessing

Screening for missing values using the ‘visdat’ function of the R programming software. The study performed multiple interpolations using the ‘missForest’ function to achieve a 100% data presentation rate with zero missing values.

### Cohort definition and variable recoding

The R function ‘createDataPartition’ was used to divide the samples into a training and a validation cohort in a ratio of 7:3 to randomise the distribution of the outcome across the two cohorts. The training cohort was used for variable selection and construction of the model. The validation cohort served to validate the results of the training cohort. After processing, the 431 training sets and 182 validation sets incorporated 36 variables.

---

## RESULTS

### Response and baseline characteristics

We successfully collected 614 samples between January 2014 and April 2022; 508 patients (416 males and 92 females) were diagnosed with HAPE and 106 were patients without HAPE (33 females and 72 males). The demographic and clinical characteristics of the patients in the different study groups are presented in online supplement table S1. Age and SpO₂ distribution are shown in figure 1. The mean age was 39 years for the HAPE group and 34 years for the non-HAPE group; the distribution of SpO₂ showed a low overall oxygen level in patients.

---

with HAPE than in patients without HAPE. A total of 614 people entering Tibet were studied, of which 70% were randomly assigned to the training group (n=430) to construct the prediction model. At the same time, 184 were assigned to the validation group to assess the performance of the model (figure 1). Most basic clinical information and vital sign variables were not significantly different between the training and validation groups (table 1). The proportion of patients with HAPE was identical for the 2 groups, with 356 (83%) in the training group and 153 (83%) in the validation group.

### Univariate analysis of the occurrence of HAPE in the population reaching the high altitude

We divided the HAPE group (n=508) and non-HAPE group (n=106) among 614 patients reaching the high altitude. The demographic data of patients through admission records were analysed. There were differences in age, gender, nationality, resident altitude, disease onset altitude, transportation to Tibet, whether they had a cold on arrival, consumed alcohol, had a fever, fatigue, loss of appetite, sleep disturbance, cough, chest tightness, dyspnoea, lip cyanosis, coughing sputum, and vital signs such as respiratory rate and SpO₂ between HAPE group and non-HAPE group (all p<0.05) (online supplemental table S1).

The following variables were deployed to analyse the occurrence of HAPE. The occurrence of HAPE was noted as the dependent variable (0=non-HAPE, 1=HAPE). The results showed that the vital variables, including age (OR=0.96, 95% CI 0.95 to 0.99), a vehicle of transportation into Tibet (OR=0.188187, 95% CI 0.14 to 0.43), cold (OR=5.88, 95% CI 1.77 to 36.49), fatigue (OR=5.15 95% CI 2.06 to 17.30), sleeping disorder (OR=7.08, 95% CI 2.55 to 29.45), cough (OR=9.95, 95% CI 5.70 to 17.29), coughing sputum (OR=10.12, 95% CI 4.83 to 24.79) and SpO₂ (OR=0.91, 95% CI 0.88 to 0.94), were associated with the occurrence of patients with HAPE after reaching the high altitude (table 2).

The above were incorporated in multivariate analysis to identify the vital occurrence of HAPE predictors. Six main predictors were selected, including age, coughing, mode of transportation to high altitude, SpO₂, coughing sputum and fatigue. Nomogram was drawn to visualise the models, using R programming software, denoted as model 1 (figure 2) and model 2 without SpO₂ value (figure 2). The risk of HAPE is presented as an upward vertical line for each variable in the nomogram, and aligning all the scores together to obtain the total and then drawing a downward vertical line. For example, for a 27-year-old man who travelled by plane to a high-altitude region and, on arrival, experienced fatigue and a mild cough without sputum production and had blood oxygen saturation of only 73%, the score for nomogram was calculated as follows: age (12 points), travel above 2500 m (0 points), fatigue (10 points), cough (0 points) and blood oxygen

---

#### Table 1. Demographic and clinical characteristics of the training group and validation group

| Characteristic         | Training group, n=430 | Validation group, n=184 | P value* |
|-----------------------|----------------------|------------------------|----------|
| Gender                |                      |                        | 0.11     |
| Male                  | 350 (81%)            | 138 (75%)              |          |
| Female                | 79 (18%)             | 46 (25%)               |          |
| Age                   | 34 (25, 46)          | 38 (27, 47)            | 0.074    |
| BMI                   | 24.5 (22.4, 27.3)    | 24.0 (22.0, 26.0)      | 0.6      |
| Nationality           |                      |                        | 0.14     |
| Chinese               | 386 (90%)            | 157 (85%)              |          |
| Others                | 19 (4.4%)            | 8 (4.3%)               |          |
| Tibetan               | 25 (5.8%)            | 19 (10%)               |          |
| ART†                  | 500 (100, 1,531)     | 500 (119, 2,532)       | 0.3      |
| ADD‡‡                 | 3560 (3,650, 3,660)  | 3560 (3,650, 3,660)    | 0.6      |
| Days§§                | 1.00 (1.00, 2.00)    | 2.00 (1.00, 2.00)      | 0.7      |
| TAT¶¶                 |                      |                        | 0.5      |
| Aeroplane             | 176 (41%)            | 67 (36%)               |          |
| Train                 | 93 (22%)             | 36 (20%)               |          |
| Vehicle               | 26 (6.0%)            | 14 (7.6%)              |          |
| Shower                |                      |                        | 0.9      |
| No                    | 420 (98%)            | 181 (98%)              |          |
| Yes                   | 10 (2.3%)            | 3 (1.6%)               |          |
| Cold                  |                      |                        | 0.09     |
| No                    | 378 (88%)            | 161 (88%)              |          |
| Yes                   | 52 (12%)             | 23 (12%)               |          |
| Drink                 |                      |                        | 0.11     |
| No                    | 412 (96%)            | 181 (98%)              |          |
| Yes                   | 18 (4.2%)            | 3 (1.6%)               |          |
| Smoking               |                      |                        | >0.9     |
| No                    | 379 (88%)            | 162 (88%)              |          |
| Yes                   | 51 (12%)             | 22 (12%)               |          |
| Hypertension          |                      |                        | 0.2      |
| No                    | 396 (92%)            | 163 (89%)              |          |
| Yes                   | 34 (7.9%)            | 21 (11%)               |          |
| Diabetes              |                      |                        | 0.2      |
| No                    | 414 (96%)            | 179 (97%)              |          |
| Yes                   | 16 (3.7%)            | 5 (2.7%)               |          |
| CRD***                |                      |                        | 0.2      |
| No                    | 416 (97%)            | 180 (98%)              |          |
| Yes                   | 14 (3.3%)            | 4 (2.2%)               |          |
| CLD††††               |                      |                        | 0.14     |
| No                    | 426 (99%)            | 179 (97%)              |          |
| Yes                   | 4 (0.9%)             | 5 (2.7%)               |          |
| Fever                 |                      |                        | 0.08     |
| No                    | 412 (96%)            | 170 (92%)              |          |
| Yes                   | 18 (4.2%)            | 14 (7.6%)              |          |
| Fatigue               |                      |                        | 0.7      |
| No                    | 345 (80%)            | 145 (79%)              |          |
| Yes                   | 85 (20%)             | 39 (21%)               |          |

*Continued*

---

| Table 1 Continued                                                                 | Training group, n=430 | Validation group, n=184 | P value* |
|-----------------------------------------------------------------------------------|----------------------|------------------------|----------|
| **Characteristic**                                                                |                      |                        |          |
| Loss of appetite                                                                  |                      |                        | 0.15     |
| No                                                                               | 333 (77%)            | 152 (83%)              |          |
| Yes                                                                              | 97 (23%)             | 32 (17%)               |          |
| Nausea                                                                           |                      |                        | 0.5      |
| No                                                                               | 328 (76%)            | 136 (74%)              |          |
| Yes                                                                              | 102 (24%)            | 48 (26%)               |          |
| Sleeping disorder                                                                |                      |                        | 0.3      |
| No                                                                               | 345 (80%)            | 154 (84%)              |          |
| Yes                                                                              | 85 (20%)             | 30 (16%)               |          |
| Dizzy                                                                            |                      |                        | 0.5      |
| No                                                                               | 152 (35%)            | 70 (38%)               |          |
| Yes                                                                              | 278 (65%)            | 114 (62%)              |          |
| Cough                                                                            |                      |                        | 0.2      |
| No                                                                               | 130 (30%)            | 65 (35%)               |          |
| Yes                                                                              | 300 (70%)            | 119 (65%)              |          |
| Chest tightness                                                                  |                      |                        | 0.4      |
| No                                                                               | 236 (55%)            | 108 (59%)              |          |
| Yes                                                                              | 194 (45%)            | 76 (41%)               |          |
| Shortness of breath                                                              |                      |                        | 0.2      |
| No                                                                               | 358 (83%)            | 147 (80%)              |          |
| Yes                                                                              | 72 (17%)             | 37 (20%)               |          |
| Palpitations                                                                     |                      |                        | >0.9     |
| No                                                                               | 366 (85%)            | 156 (85%)              |          |
| Yes                                                                              | 64 (15%)             | 28 (15%)               |          |
| Bluish lips                                                                      |                      |                        | 0.022    |
| No                                                                               | 360 (84%)            | 167 (91%)              |          |
| Yes                                                                              | 70 (16%)             | 17 (9.2%)              |          |
| Coughing sputum                                                                  |                      |                        | 0.7      |
| No                                                                               | 240 (56%)            | 106 (58%)              |          |
| Yes                                                                              | 190 (44%)            | 78 (42%)               |          |
| RF                                                                               | 20.00 (20.00, 22.00) | 20.00 (20.00, 21.00)   | 0.3      |
| Temperature                                                                      | 36.50 (36.40, 36.82) | 36.50 (36.40, 36.80)   | 0.9      |
| HR                                                                               | 98 (84, 112)         | 92 (81, 108)           | 0.091    |
| SpO₂                                                                             | 75 (83, 84)          | 76 (67, 85)            | 0.13     |
| SBP                                                                              | 122 (112, 135)       | 120 (112, 136)         | 0.7      |
| DBP                                                                              | 80 (70, 90)          | 80 (70, 90)            | 0.6      |
| Outcome                                                                          |                      |                        | >0.9     |
| Non-HAPE                                                                         | 74 (17%)             | 32 (17%)               |          |
| HAPE                                                                             | 356 (83%)            | 152 (83%)              |          |

n (%); median (IQR).  
*Fisher’s exact test; Wilcoxon rank sum test; Pearson’s χ² test.  
†TAT refers to the altitude of residence.  
‡ADO refers to an altitude of disease onset.  
§Days refer to the number of days/time taken for the first symptom to appear after the patient’s arrival to a high altitude area.  
¶TAT refers to patient’s transport to the plateau area.  
**CRD refers to chronic respiratory disease.  
††CLD refers to chronic liver disease.  
BMI, body mass index; DBP, diastolic blood pressure; HAPE, high-altitude pulmonary oedema; SBP, systolic blood pressure.

---

The total score was 54 points, corresponding to a nearly 90% risk of developing HAPE.

The AUC of model 1 was 0.983 with 95% CI (0.969 to 0.998), the model’s specificity was about 95% and the sensitivity was about 95% when the predictive threshold of the total score was 41.728. The AUC of model 2 was 0.944 with 95% CI (0.909 to 0.979), as shown in figure 3. These findings suggest that both models had excellent precision and sensitivity.

## Model evaluation

Next, internal validation of the model and the evaluation of the model’s predictive effect using the calibration curve and the ROC curve after repeated sampling were applied. In training sets, the C-index was >90% in both models (figure 3A). Additionally, in validation sets, the C-index of model 1 was 0.934 with a 95% CI (0.848 to 1.000), and the C-index of model 2 was 0.889 with a 95% CI (0.779 to 0.999) (figure 3B). The AUC value of both models in the validation set exceeded 0.85, suggesting that these two prediction models had an accurate predictive ability. The calibration curves of the two models were highly consistent in both training and validation sets (figure 3C). Their calibration curves in the validation set were more visibly consistent (figure 3D). In this research, model 1 included SpO₂ with a NB of nearly 99% at a threshold of T of 25% in the training cohort and SpO₂ at T of 25% in the validation cohort (figure 3E). We derived that SpO₂ and a NB at approximately 90% at 50% in the validation cohort (figure 3F). The NB of model 1 was approximately 0.99 higher than that of model 2 in both cohorts, which means that for every 100 individuals screened, the prediction with SpO₂ screens nine more patients at high risk of HAPE. [14]

---

## DISCUSSION

To the best of our knowledge, this is the first study that provided a simple and easy-to-execute prediction tool for HAPE in the form of a nomogram. The scoring model with six predictors can easily be obtained by people reaching high altitudes and help to assess the risk of HAPE in a timely manner. This study also reflected the satisfactory performance of the model in its modest predictive power, with AUC > 0.85 in both models. In addition, calibration analyses performed in both cohorts showed that the predicted occurrence of HAPE was highly consistent with the diagnosed HAPE proportion. In both models, clinical decision curve analysis showed a net clinical benefit rate of >90% for patients with HAPE. This provides a practical scoring system with accurate assessment even for settings where medical instrumentation is not immediately available.

---

### Analysis of risk factors influencing the occurrence of HAPE

A study by Hultgren (1970) [15] in the Peruvian population found a higher risk of developing HAPE in people...

---

Table 2. Univariate and multivariate logistic analyses on variables for the prediction of patients with high-altitude pulmonary oedema (HAPE)

| Characteristic         | Univariate analysis OR | 95% CI                | P value | Multivariate analysis OR | 95% CI                | P value |
|-----------------------|-----------------------|-----------------------|---------|-------------------------|-----------------------|---------|
| Gender                |                       |                       |         |                         |                       |         |
| Female                | 0.59                  | 0.32 to 1.06          | 0.08    |                         |                       |         |
| Male                  | 1.00                  | 0.95 to 1.09          | 0.99    |                         |                       |         |
| Age                   |                       |                       |         |                         |                       |         |
| 25–34                 | 0.58                  | 0.3553 to 1.4         | 0.24    | 1.11                    | 0.08 to 17.43         | >0.9    |
| 34–46                 | 0.84                  | 0.4893 to 0.976       | 0.04    | 0.05                    | 0.00 to 0.40          | 0.01    |
| >46                   | 1.00                  |                       |         |                         |                       |         |
| Nationality           |                       |                       |         |                         |                       |         |
| Tibetan               | 1.46                  | 0.51 to 3.59          | 0.48    |                         |                       |         |
| Chinese               | 1.00                  | 1.00 to 2.16/5.29+1.49| 0.99    |                         |                       |         |
| Others                | 1.00                  |                       |         |                         |                       |         |
| Transports            |                       |                       |         |                         |                       |         |
| Aeroplane             | 20.8                  | 4.41 to 197.2         | <0.001  | 345                     | 39.0 to 11,459        | <0.001  |
| Train                 | 5.81                  | 0.14 to NA            | 0.43    |                         | Train to NA           |         |
| Vehicle               | 9.34                  | 0.14 to 36.49         | 0.99    | 2015.6                  | 2015.6 to 2698        | 0.6     |
| Cold                  | 0.24                  | 0.09 to 0.65          | 0.01    | 0.55                    | 0.08 to 16.01         | 0.6     |
| Drinking              | 0.93                  | 0.39 to 2.51          | 0.89    |                         |                       |         |
| Fever                 | 33.04                 | 2.56 to 212.23        | 0.01    | 8.23                    | 1.17 to 92.2          | 0.055   |
| Loss of appetite      | 2.55                  | 0.92 to 7.61          | 0.08    |                         |                       |         |
| Fatigue               | 1.54                  | 0.96 to 2.61          | 0.07    | 4.16                    | 0.55 to 47.5          | 0.2     |
| Sleeping disorder     | 1.02                  | 0.55 to 1.91          | 0.95    | 12.2                    | 2.50 to 76.3          | 0.004   |
| Chest tightness       | 2.16                  | 1.08 to 5.11          | 0.03    |                         |                       |         |
| Blush lips            | 1.12                  | 0.39 to 3.26          | 0.84    |                         |                       |         |
| Shortness of breath   | 0.98                  | 0.49 to 1.93          | 0.95    |                         |                       |         |
| Coughing sputum       | 9.88                  | 3.89 to 13.26         | <0.001  | 9.88                    | 1.81 to 74.4          | 0.013   |
| RF                    | 0.91                  | 0.68 to 1.20          | 0.51    |                         |                       |         |
| Temperature           | 0.98                  | 0.89 to 1.06          | 0.84    |                         |                       |         |
| SpO₂                  | 0.91                  | 0.88 to 0.94          | <0.001  | 0.90                    | 0.77 to 0.90          | <0.001  |

*Table 2. Univariate and multivariate logistic analyses on variables for the prediction of patients with high-altitude pulmonary oedema (HAPE)*

---

![image: Two nomograms for prognostic prediction of a patient with high-altitude pulmonary oedema (HAPE). Model 1 includes SpO₂; Model 2 excludes SpO₂.]

**Figure 2**  
A constructed nomogram for prognostic prediction of a patient with high-altitude pulmonary oedema (HAPE).  
(A) Model 1 is the nomogram for risk prediction tools of HAPE, including SpO₂.  
(B) Model 2 is the nomogram for risk prediction tools of HAPE excluding SpO₂.

---

Younger than 20. His study concluded that the risk of HAPE was the lowest among those between the ages of 34 and 46 years compared with other age groups. Also, this age group (34–46 years) was a protective factor for the development of HAPE.[15] The mean age at the onset of HAPE in this study was 34 years, which is similar to the mean age observed in the study by Hultgren.[15] A previous epidemiological study from India[16] also showed that the likelihood of HAPE decreased with age and showed a relatively low incidence in the age range of 36–45. They found comparatively high diagnoses in the age range lower than 35, which is consistent with the findings of our study.

Transport mode from the plains to the plateau is also an essential factor influencing the possible occurrence of HAPE. The findings of this study concluded that the risk of HAPE is highest when entering the plateau by train. Previous studies[17–19] have confirmed that rapid altitude gain significantly correlates with the development of HAPE symptoms. For example, studies suggested that the speed and time to reach a certain altitude by plane are significant risk factors for HAPE.[20] However, this study found that train travel was riskier than air travel. This is mainly because, with increasing altitude, the oxygen content in the air becomes lower for passengers entering Tibet by train, which increases the passengers’

---

![image: Six-panel figure showing ROC curves, calibration curves, and decision curves for two models in training and validation sets.]

**Figure 3**  
(A, B) Internal validation of nomogram in the training set. (A) Discrimination: area under the ROC curve (AUC) of the receiver operating characteristic curve (ROC) with a red curve in model 1 was 0.983 (95% CI 0.909 to 0.979). (B) AUC of the ROC with a blue curve in model 2 was 0.944 (95% CI 0.779 to 0.999).  
(C, D) Nomogram calibration curve. The grey-dotted line indicates perfect prediction by an ideal model. The red and blue lines depict model 1 and model 2’s performance, respectively.  
(E, F) The red and blue curves show the number of people classified as positive (high risk) by the simple model at each threshold probability; the grey curve shows the number of true positives at each threshold probability. (E) The decision curve of two models in the training group. (F) Decision curve of two models in the validation group.

- **Panel A:** ROC curve for model 1 (AUC: 0.934) and model 2 (AUC: 0.889) in the training set, with cutoffs at 42.226 and 29.223.
- **Panel B:** ROC curve for model 1 (AUC: 0.983) and model 2 (AUC: 0.944) in the validation set, with cutoffs at 41.728 and 36.902.
- **Panel C:** Calibration curve for model 1 (apparent, bias-corrected) and model 2 (ideal) in the training set.
- **Panel D:** Calibration curve for model 1 (apparent, bias-corrected) and model 2 (ideal) in the validation set.
- **Panel E:** Decision curve analysis for model 1, model 2, and none in the training group.
- **Panel F:** Decision curve analysis for model 1, model 2, and none in the validation group.

---

## The value of nomogram and clinical decision curves for predicting the risk of developing HAPE and guiding clinical decisions

At present, there is no scoring system comparable to the LLS score for people at high risk of HAPE. The occurrence of HAPE has been confirmed in numerous previous studies. A rapid descent from a high altitude or supplying the patient with oxygen or hyperbaric chambers in a medical facility can prevent the further escalation of medical symptoms.[12,28] However, most high-altitude areas are very remote; thus, it is impossible to intervene in advance to accurately predict the risk of disease occurrence to reduce the further development of HAPE or other more severe diseases.[6,29] Zafren et al[6] and Yamamdra et al[31] suggested that people with access to good medical facilities or medical centres, such as those in ski resort communities, do not need to descend to lower altitudes but can manage with supplemental oxygen that is sufficient to increase SpO₂ to over 90%. However, since remote areas with a shortage of medical facilities do not have immediate access to medical resources, this study introduced the possibility of inferring the occurrence of HAPE through self-conscious physiological assessment without relying on medical devices such as oximeters. Moreover, with an NB of 0.99 at a threshold probability of 0.01 to 0.98, meaning that for every 100 patients using the model, 99 will benefit from it without harming anyone else, the model seems to be highly accurate with little to no drawbacks and can be used as a guideline for clinical work.

## Study limitations and perspective for future research

This study has a few limitations. First, this was a retrospective study; thus, the model incorporated predictors based on clinically relevant data acquired directly from clinical medical records. Second, data were missing predictor variables in both the training and validation groups. Potential information bias cannot be completely ruled out even though these variables with a missing rate <5% were imputed 10 times via multiple imputation. Therefore, even though this model is highly accurate, the violation of the model in a multicentre setting is required in the future.

## CONCLUSION

The main advantage of this model is that it allows for simple and accurate detection of HAPE clinical symptoms at an early onset, which can be easily used by individuals without medical expert advice. Such a practical scoring tool may help high-altitude visitors estimate the probability of developing HAPE and take relevant precautions that could be potentially lifesaving. Additionally, applying this model for high-altitude travel should aid in the early detection of individuals at high risk of HAPE and contribute to efforts to provide clinical decision-making support to decrease potentially adverse health outcomes.

---

### Contributors

LG designed the study and provided scientific guidance, modification and approval of the report. YS carried out data collection, data analysis and wrote the initial draft of the manuscript, was responsible for the overall content as the guarantor. ZD assisted with data analysis, clinical background knowledge guide. BC, ZD, JH, and RZ assisted with data collection and was also actively involved in the preparation.

### Funding

This study was supported by the Science and Technology Department of the Tibet Study project Program (NO. XZ2021JR0046). The funders had no role in the study design, data collection, data analysis, and interpretation as well as the writing of the manuscript.

### Competing interests

The authors declare that the research was conducted without any commercial or financial relationships that could be construed as a potential conflict of interest.

---

#### References

[References are not visible on this page.]

---

#### Figure 1

[image: Figure 1. SpO₂ was 78% in patients with HAPE, which was lower than that observed in patients without HAPE.]

---

#### Citations

- [21] Kobayashi (1987)
- [22] Previous studies on pulmonary artery pressure
- [23] Menon
- [25] Menon
- [26] Hultgren
- [27] Hultgren
- [28] Previous studies on medical facility intervention
- [29] Zafren et al
- [31] Yamamdra et al

---

**Note:** All statistical data, numerical results, and references have been preserved as in the original document.

---

---
## Patient and Public Involvement

Patients and/or the public were not involved in the design, or conduct, or reporting, or dissemination plans of this research.

## Patient Consent for Publication

Not applicable.

## Ethics Approval

Medical Ethics Committee of Tibet Autonomous Region People’s Hospital approved this study, Reference number ID(s): ME-TBHP-ZZ-21-0X-064.

## Provenance and Peer Review

Not commissioned; externally peer reviewed.

## Data Availability Statement

Data are available upon reasonable request. The data used in this study are available upon request. To access the data, please contact the corresponding author at egasn5394@seina.com. In your request, please provide a brief description of your research purpose and how you intend to use the data. We will review your request and provide you with access to the data if it aligns with our data sharing policy and ethical considerations. Data access is subject to approval, and we are committed to ensuring that the data are used for legitimate research purposes while respecting privacy and confidentiality. We encourage researchers to engage in open and collaborative scientific endeavours and appreciate your interest in using our data for your research.

## Supplemental Material

This content has been supplied by the author(s). It has not been vetted by BMJ Publishing Group Limited (BMJ) and may not have been peer-reviewed. Any opinions or recommendations discussed are solely those of the author(s) and are not endorsed by BMJ. BMJ disclaims all liability and responsibility arising from any reliance placed on the content. Where the content includes any translated material, BMJ does not warrant the accuracy and reliability of the translations (including but not limited to local regulations, clinical guidelines, terminology, drug names and drug dosages), and is not responsible for any error and/or omissions arising from translation and adaptation or otherwise.

## Licensing

This is an open access article distributed in accordance with the Creative Commons Attribution Non Commercial (CC BY-NC 4.0) license, which permits others to distribute, remix, adapt, build upon this work non-commercially, and license their derivative works on different terms, provided the original work is properly cited, appropriate credit is given, any changes made indicated, and the use is non-commercial. See: http://creativecommons.org/licenses/by-nc/4.0/.

## ORCID iDs

- Yuxia Suona: [http://orcid.org/0000-0003-6878-617X](http://orcid.org/0000-0003-6878-617X)
- Lihua Wang: [http://orcid.org/0000-0003-3913-9743](http://orcid.org/0000-0003-3913-9743)
- Lihua Gesang: [http://orcid.org/0000-0003-0358-6382](http://orcid.org/0000-0003-0358-6382)
- Zhuoga Danzeng: [http://orcid.org/0000-0003-1587-8709](http://orcid.org/0000-0003-1587-8709)
- Quzong Zhang: [http://orcid.org/0000-0001-6674-6743](http://orcid.org/0000-0001-6674-6743)
- Ju Huang: [http://orcid.org/0000-0003-3319-5724](http://orcid.org/0000-0003-3319-5724)

---

## REFERENCES

1. Bärtsch M, Hefti U, Hefti JP. High-altitude illnesses: old stories and new insights into the pathophysiology, treatment and prevention. *Sports Med Health Sci* 2021;3:59–69.
2. Statistical Bulletin for national economic and social development of Tibet autonomous region in 2021. , 2022Available: http://xj.xizang.gov.cn/xjxxgk/tjgb/202204/t20220426_295819.html
3. Bärtsch J, Swenson ER, Hackett PH, et al. Flying to high-altitude destinations: is the risk of acute mountain sickness greater? *J Travel Med* 2023;30.
4. Jensen JD, Vincent AL. *High Altitude Pulmonary Edema*. Treasure Island (FL): StatPearls, 2023.
5. Paralikar SJ. High altitude pulmonary edema-clinical features, pathophysiology, prevention and treatment. *Indian J Occup Environ Med* 2012;16:59–62.
6. Clark ST, Sheraton M. *EMS high-altitude field prophylaxis and treatment*. Treasure Island (FL): StatPearls, 2023.
7. Roach RC, Hackett PH, Oelz O, et al. The 2018 Lake Louise acute mountain sickness score. *High Alt Med Biol* 2018;19:4–6.
8. Ahluwalia A, Underwood PJ. *Acute Mountain Sickness Score. Transureal [LIS]: StatPearls*, 2023.
9. Yan Ruo JD, Latao MP, Pesac S, et al. Visual analog scale (VAS) for assessment of mountain sickness (AMS). *Clin on Aconcagua Wilderness Environ Med* 2011;22:7–14.
10. Wu J, Chen Y, Luo Y. Evaluation of the visual analog score (VAS) to assess acute mountain sickness (AMS) in a hypobaric chamber. *PLoS ONE* 2014;9.
11. Stekhoven DJ, Bühlmann P. MissForest--non-parametric missing value imputation for mixed-type data. *Bioinformatics* 2012;28:112–8.
12. Balachandran VP, Gonen M, Smith JJ, et al. Nomograms in oncology: more than meets the eye. *Lancet Oncol* 2015;16:e173–80.
13. Lapinsky SE, Holt D, Hallett D, et al. Survey of information technology in intensive care units in Ontario, Canada. *BMC Med Inform Decis Mak* 2008;8:5.
14. Vickers AJ, Van Calster B, Steyerberg EW. A simple, step-by-step guide to interpreting decision curve analysis. *Diagn Progn Res* 2019;3:18.
15. Hultgren H. Biomedicine problems of high terrestrial altitude, 1969.
16. Adhya S, Menon AK, Dharbash S, et al. *Clinical Medicine for Public Health* 2021;2021:1–20.
17. Campbell AJ, Ledoux T, Watson M, et al. High-altitude pulmonary edema: a meta-analysis series of 52 patients. *Chest* 2003;123:49–53.
18. Durmowicz AG. Pulmonary edema in children with down syndrome during travel to moderate altitudes. *Pediatrics* 2001;108:443–7.
19. Villca N, Arispe R, Huayta E, et al. High-altitude pulmonary edema at 3,700–4,250 m, Haem-Freudenthal. High-altitude illnesses in infant and travel: pediatric considerations. *Pediatr Clin North Am* 2017;64:805–20.
20. Kobayashi S, Yoshimasu K, Kubo K, et al. Clinical features of patients with high-altitude pulmonary edema at Mt. Fuji. *Intern Med* 2008;47:825–30.
21. Oelz O, Maggiorini M, Ritter M, et al. Nifedipine for high altitude pulmonary oedema. *Lancet* 1989;2:1241.
22. Luks AM, Swenson ER, Bärtsch PERR. Acute high-altitude sickness. *Eur Respir Rev* 2017;26:160096:143.
23. Menon ND. High-altitude pulmonary edema: a clinical study. *N Engl J Med* 1965;273:66–73.
24. Bärtsch P, Waber U, Haeberli A, et al. Enhanced fibrin formation in high-altitude pulmonary edema. *J Appl Physiol (1985)* 1987;63:752–7.
25. Hultgren HN, Honigman B, Theis K, et al. High-altitude pulmonary edema at a ski resort. *West J Med* 1996;164:222–7.
26. Sampson JB, Cymerman A, Burse RL, et al. Procedures for the measurement of acute mountain sickness. *Aviation, Space and Environment Medicine* 1983;54:1062–71.
27. Freeman K, Naisl M, Groth S. Use of the Gamow bag by EMT-basic park rangers for treatment of high-altitude pulmonary edema and high-altitude cerebral edema. *Wilderness Environ Med* 2004;15:198–201.
28. Zafren K, Reeves JJ, Schoene R. Treatment of high-altitude pulmonary edema by bed rest and supplemental oxygen. *Wilderness Environ Med* 1996;7:127–32.
29. Yamamanda N, Vair V, Singh S, et al. Managing high-altitude pulmonary edema with oxygen alenorestals of a randomized controlled trial. *High Alt Med Biol* 2016;17:294–9.

---

Suona Y, et al. *BMJ Open* 2023;13:e074161. doi:10.1136/bmjopen-2023-074161