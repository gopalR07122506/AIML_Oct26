
# Statistics – Complete Notes for Data Science & AIML

## 1. Introduction to Statistics

**Statistics:** Statistics is the process of collecting, organizing, analyzing and interpreting data to understand information and make decisions.

**Example:** Analyzing students' marks to calculate average marks and understand their performance.

### Important Basic Concepts

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Statistics | Collecting, analyzing and interpreting data. | Analyzing students' marks. |
| 2 | Data | Collection of facts, numbers or information. | 10, 20, 30, 40. |
| 3 | Population | Complete group of data we want to study. | All 500 students in a college. |
| 4 | Sample | Small part selected from the population. | 50 students selected from 500. |
| 5 | Parameter | Numerical value describing the entire population. | Average marks of all 500 students. |
| 6 | Statistic | Numerical value calculated from a sample. | Average marks of 50 students. |
| 7 | Variable | A feature that can have different values. | Age, salary, height. |
| 8 | Observation | A single record in a dataset. | One student's complete record. |
| 9 | Frequency | Number of times a value occurs. | 80 appears 3 times. |
| 10 | Distribution | Shows how data values are spread. | Most students score between 60 and 80. |

---

## 2. Measures of Central Tendency

Central Tendency helps us find the central or average value of data.

Example Dataset: `[10, 20, 20, 30, 40]`

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Mean | Average of all values. | (10+20+20+30+40)/5 = 24 |
| 2 | Median | Middle value after arranging data in order. | 20 |
| 3 | Mode | Value that occurs most frequently. | 20 |
| 4 | Weighted Mean | Average calculated using different weights. | (80×0.6)+(90×0.4) = 84 |
| 5 | Geometric Mean | Average calculated using the product and roots of values. | GM of 4 and 16 = 8 |

**Important:** Mean, Median and Mode are the three most commonly used measures of central tendency.

---

## 3. Measures of Dispersion

Dispersion helps us understand how much data values are spread or different from each other.

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Range | Difference between maximum and minimum values. | 50-10 = 40 |
| 2 | Variance | Measures how far values are spread from the mean. | Higher variance means more spread. |
| 3 | Standard Deviation | Measures how much values typically differ from the mean. | Low SD means values are closer to the mean. |
| 4 | Quartiles | Divide sorted data into four equal parts. | Q1=25th, Q2=50th, Q3=75th percentile. |
| 5 | IQR | Difference between Q3 and Q1. | IQR = Q3-Q1. |
| 6 | Percentile | Shows the value below which a given percentage of data falls. | 90th percentile means 90% of values are at or below it. |
| 7 | Outliers | Values that are unusually different from other values. | Salaries: 20k, 25k, 30k, 5 lakh. |

### Standard Deviation

- Low Standard Deviation: Values are close to the average.
- High Standard Deviation: Values are spread far from the average.

---

## 4. Types of Data

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Qualitative Data | Data describing categories or qualities. | Gender, city, color. |
| 2 | Quantitative Data | Data represented using numbers. | Age, salary, marks. |
| 3 | Discrete Data | Countable numerical values, generally whole numbers. | Number of students, cars. |
| 4 | Continuous Data | Values that can take any value within a range. | Height, weight, temperature. |
| 5 | Categorical Data | Data divided into different groups. | HR, IT, Sales. |
| 6 | Numerical Data | Data representing quantities. | Salary, age, marks. |

---

## 5. Probability

**Probability:** Probability tells us the chances of an event happening.

### Important Probability Concepts

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Probability | Possibility of an event happening. | Getting heads in a coin toss = 1/2. |
| 2 | Event | An outcome or group of outcomes we are interested in. | Getting an even number on a dice. |
| 3 | Independent Events | One event does not affect another event. | Tossing a coin twice. |
| 4 | Dependent Events | One event affects the probability of another. | Drawing two cards without replacement. |
| 5 | Conditional Probability | Probability of an event when another event has already occurred. | Probability of rain given cloudy weather. |
| 6 | Random Variable | Variable whose value depends on a random experiment. | Number obtained on a dice. |
| 7 | Expected Value | Average outcome expected over many repetitions. | Expected value of a dice = 3.5. |

### Probability Formula

P(A) = Favourable Outcomes / Total Outcomes

Example:

Probability of getting 4 when rolling a dice:

P(4) = 1/6

---

## 6. Statistical Distributions

**Distribution:** A distribution explains how values are spread or arranged in a dataset.

| Sr. No. | Distribution | Simple Definition | Example |
|---|---|---|---|
| 1 | Normal Distribution | Bell-shaped distribution where most values are around the mean. | Human heights often approximately follow a normal distribution. |
| 2 | Binomial Distribution | Counts successes in a fixed number of independent trials. | Number of heads in 10 coin tosses. |
| 3 | Poisson Distribution | Counts events occurring within a fixed time or space at a constant average rate. | Number of calls received per hour. |
| 4 | Uniform Distribution | All possible outcomes have equal probability. | Rolling a fair dice. |
| 5 | Skewed Distribution | Data is not distributed symmetrically. | Income distribution. |

### Types of Skewness

1. Positive Skewness: Long tail on the right side.
2. Negative Skewness: Long tail on the left side.
3. Zero Skewness: Distribution is approximately symmetrical.

---

## 7. Correlation and Covariance

**Correlation:** Measures the strength and direction of the relationship between two variables.

**Covariance:** Measures whether two variables tend to move in the same or opposite directions.

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Correlation | Measures relationship between two variables. | Study hours and marks. |
| 2 | Positive Correlation | Both variables tend to increase or decrease together. | More study hours, higher marks. |
| 3 | Negative Correlation | One variable increases while the other tends to decrease. | Higher price, lower demand. |
| 4 | Zero Correlation | No linear relationship between two variables. | Shoe size and exam marks. |
| 5 | Covariance | Measures how two variables move together. | Salary and spending. |

### Correlation Coefficient

Range: -1 to +1

| Value | Meaning |
|---|---|
| +1 | Perfect positive correlation. |
| 0 | No linear correlation. |
| -1 | Perfect negative correlation. |

**Note:** Correlation does not always mean causation.

---

## 8. Hypothesis Testing

**Hypothesis Testing:** A statistical method used to check whether an assumption or claim about a population is supported by sample data.

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Hypothesis | An assumption or claim we want to test. | New teaching method improves marks. |
| 2 | Null Hypothesis (H0) | Assumes there is no effect or difference. | Teaching method has no effect. |
| 3 | Alternative Hypothesis (H1) | Assumes there is an effect or difference. | Teaching method improves marks. |
| 4 | P-value | Measures how unusual the observed result is if H0 is true. | P-value = 0.03. |
| 5 | Significance Level | Threshold used to decide statistical significance. | Commonly 0.05. |
| 6 | Type I Error | Rejecting a true null hypothesis. | Concluding a medicine works when it does not. |
| 7 | Type II Error | Failing to reject a false null hypothesis. | Missing a real medicine effect. |

### P-value Rule

- P-value < 0.05: Reject the Null Hypothesis.
- P-value >= 0.05: Fail to reject the Null Hypothesis.

---

## 9. Important Statistical Tests

| Sr. No. | Test | Simple Definition | Example |
|---|---|---|---|
| 1 | Z-test | Tests a population mean or proportion using a normal approximation under suitable conditions. | Testing average product weight with known population SD. |
| 2 | T-test | Compares means between groups. | Comparing marks of two classes. |
| 3 | Chi-Square Test | Checks relationships between categorical variables or observed and expected counts. | Gender and product preference. |
| 4 | ANOVA | Compares means across three or more groups. | Comparing marks of three classes. |
| 5 | Correlation Test | Tests whether two variables have a statistical association. | Study hours and marks. |

---

## 10. Statistics Concepts Used in Machine Learning

| Sr. No. | Concept | Simple Definition | Example |
|---|---|---|---|
| 1 | Sampling | Selecting a subset of data from a population. | Selecting 100 customers from 10,000. |
| 2 | Random Sampling | Selecting observations randomly. | Randomly selecting 50 students. |
| 3 | Sampling Bias | When the selected sample does not represent the population properly. | Surveying only high-income customers. |
| 4 | Normalization | Scaling data into a fixed range, often 0 to 1. | Scaling salary values between 0 and 1. |
| 5 | Standardization | Transforming data to mean 0 and standard deviation 1. | Standardizing age and salary. |
| 6 | Central Limit Theorem | Under suitable conditions, sample means become approximately normally distributed as sample size increases. | Taking many samples and calculating their average marks. |
| 7 | Confidence Interval | A range used to estimate an unknown population parameter. | Estimating average salary between ₹30k and ₹35k. |
| 8 | Bias | Error caused by assumptions or limitations in a model. | Model consistently underestimates house prices. |
| 9 | Overfitting | Model learns training data too closely and performs poorly on new data. | 99% training accuracy but 65% testing accuracy. |
| 10 | Underfitting | Model is too simple to learn important patterns. | Low accuracy on both training and testing data. |

---

## 11. Important Statistics Formulas

| Concept | Formula |
|---|---|
| Mean | Sum of values / Number of values |
| Range | Maximum - Minimum |
| Population Variance | Σ(x-μ)² / N |
| Sample Variance | Σ(x-x̄)² / (n-1) |
| Standard Deviation | Square root of Variance |
| IQR | Q3 - Q1 |
| Probability | Favourable Outcomes / Total Outcomes |
| Z-score | (x-μ) / σ |
| Population Covariance | Σ(x-μx)(y-μy) / N |
| Correlation | Cov(X,Y) / (σx × σy) |

Where:
- μ = Population Mean
- x̄ = Sample Mean
- N = Population Size
- n = Sample Size
- σ = Population Standard Deviation

---

## 12. Python Practical – Statistics Using NumPy and SciPy

```python
import numpy as np
from scipy import stats

# Sample Dataset
data = [10, 20, 20, 30, 40, 50, 60]

# Mean
print("Mean:", np.mean(data))

# Median
print("Median:", np.median(data))

# Mode
print("Mode:", stats.mode(data, keepdims=False).mode)

# Minimum
print("Minimum:", np.min(data))

# Maximum
print("Maximum:", np.max(data))

# Range
print("Range:", np.max(data) - np.min(data))

# Population Variance
print("Variance:", np.var(data))

# Population Standard Deviation
print("Standard Deviation:", np.std(data))

# Percentile
print("75th Percentile:", np.percentile(data, 75))

# Quartiles
print("Quartiles:", np.percentile(data, [25, 50, 75]))

# IQR
q1, q3 = np.percentile(data, [25, 75])
print("IQR:", q3 - q1)

# Correlation
x = [10, 20, 30, 40, 50]
y = [15, 25, 35, 45, 55]

print("Correlation:", np.corrcoef(x, y)[0, 1])
```

---

## 13. Recommended Learning Order

1. Basic Statistics
2. Types of Data
3. Mean, Median and Mode
4. Range, Variance and Standard Deviation
5. Quartiles, Percentiles and IQR
6. Probability
7. Statistical Distributions
8. Correlation and Covariance
9. Sampling and Confidence Intervals
10. Hypothesis Testing
11. Z-test, T-test, Chi-Square and ANOVA
12. Statistics Concepts in Machine Learning

**Final Note:** Focus more on Mean, Median, Mode, Variance, Standard Deviation, Probability, Normal Distribution, Correlation, P-value and Hypothesis Testing. These concepts are very important for Data Science, EDA and Machine Learning.
