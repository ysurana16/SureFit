import pandas as pd
import numpy as np

def recommend_sizes_with_risk(currentChart, referenceChart, referenceSize, garmentType):
    """
    Recommends sizes based on fit probability and calculates confidence scores and risk levels.
    
    Parameters:
    currentChart (pd.DataFrame): Size chart for the current brand.
    referenceChart (pd.DataFrame): Size chart for the reference brand.
    referenceSize (str): The size in the reference chart that the user prefers.
    garmentType (str): Type of garment (e.g., 'top', 'dress', 'pants', 'skirt').

    Returns:
    pd.DataFrame: A DataFrame with recommended sizes, fit probabilities, confidence labels, and confidence scores.
    """
    # Priority weights for garment types
    priority_weights = {
        'top': {'bust': 0.4, 'shoulder': 0.3, 'waist': 0.2, 'hip': 0.1},
        'dress': {'bust': 0.3, 'shoulder': 0.2, 'waist': 0.3, 'hip': 0.2},
        'pant': {'bust': 0.1, 'shoulder': 0.1, 'waist': 0.4, 'hip': 0.4},
        'skirt': {'bust': 0.0, 'shoulder': 0.0, 'waist': 0.5, 'hip': 0.5},
    }
    weights = priority_weights.get(garmentType.lower(), {})
    if not weights:
        raise ValueError(f"Garment type '{garmentType}' not supported.")

    # Reference measurements
    referenceMeasurements = referenceChart[referenceChart['size'] == referenceSize]
    if referenceMeasurements.empty:
        raise ValueError(f"Reference size '{referenceSize}' not found in the reference chart.")
    referenceMeasurements = referenceMeasurements.iloc[0]

    # Fit Probability and Confidence Score
    size_columns = set(currentChart.columns) & set(referenceChart.columns) - {'size'}
    scores = []
    confidence_labels = []

    for _, row in currentChart.iterrows():
        total_difference = 0
        penalty_factor = 1  # Default penalty factor (no penalty)

        # Calculate total difference and penalty
        for col in size_columns:
            if col in weights:
                if pd.isna(row[col]) or pd.isna(referenceMeasurements[col]):
                    continue
                diff = abs(row[col] - referenceMeasurements[col])
                print(diff)
                weighted_diff = weights[col] * diff
                total_difference += weighted_diff

                # Penalize if the current size is smaller (tightness)
                if row[col] < referenceMeasurements[col]:
                    penalty_factor *= (1 - weights[col])  # Apply penalty for tightness

        # Fit probability score
        score = 1 / (1 + total_difference)  # Basic fit score (low difference = better fit)
        score *= np.sqrt(penalty_factor)  # Apply tightness penalty

        # Confidence label based on numerical score
        if score >= 0.5:
            confidence_label = "High"
        elif score >= 0.4:
            confidence_label = "Medium"
        else:
            confidence_label = "Low"

        scores.append(score)
        confidence_labels.append(confidence_label)

    # Combine results into a DataFrame
    result_df = currentChart[['size']].copy()
    result_df['Fit Probability (%)'] = [round(score * 100, 2) for score in scores]
    result_df['Confidence Label'] = confidence_labels

    # Sort by Fit Probability in descending order
    result_df = result_df.sort_values(by='Fit Probability (%)', ascending=False).reset_index(drop=True)

    # Take top three sizes
    top_scores = result_df['Fit Probability (%)'].iloc[:2].values / 100
    exp_scores = np.power(10, top_scores)  # Calculate powers of 10 for steep weighting
    amplified_scores = np.power(exp_scores, 10)  # Square to increase the difference more steeply
    softmax_scores = amplified_scores / amplified_scores.sum()  # Normalize by the sum
    confidence_scores = np.round(softmax_scores * 100, 2)

    # Assign confidence scores to the DataFrame
    result_df['Recommendation Score'] = 0.0  # Initialize to 0
    for i, score in enumerate(confidence_scores):
        result_df.loc[i, 'Recommendation Score'] = score

    return result_df