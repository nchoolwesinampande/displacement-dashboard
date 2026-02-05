"""
Data Processing Utilities
Functions for loading, processing, and analyzing displacement data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from datetime import datetime, timedelta


def load_and_process_data(filepath: str) -> pd.DataFrame:
    """
    Load and preprocess the displacement data.
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        Processed DataFrame
    """
    
    # Load data
    df = pd.read_csv(filepath)
    
    # Convert date column
    df['registration_date'] = pd.to_datetime(df['registration_date'])
    
    # Add derived columns
    df['registration_month'] = df['registration_date'].dt.to_period('M')
    df['registration_year'] = df['registration_date'].dt.year
    df['registration_quarter'] = df['registration_date'].dt.to_period('Q')
    
    # Calculate total individuals (beneficiary * household size)
    df['total_individuals'] = df['household_size']
    
    # Add binary columns for easier aggregation
    df['is_female_hoh'] = df['gender_hoh'] == 'Female'
    df['has_livelihood_support'] = df['livelihood_support'] == 'Yes'
    df['is_achieved'] = df['pathway_stage'] == 'Achieved'
    df['has_documentation'] = df['documentation_status'] == 'Complete'
    
    return df


def calculate_kpis(df: pd.DataFrame) -> Dict:
    """
    Calculate key performance indicators from the data.
    
    Args:
        df: Processed DataFrame
        
    Returns:
        Dictionary of KPI values
    """
    
    kpis = {}
    
    # Total beneficiaries (households)
    kpis['total_beneficiaries'] = len(df)
    
    # Total individuals reached
    kpis['total_individuals'] = df['household_size'].sum()
    
    # Solutions achieved
    kpis['solutions_achieved'] = len(df[df['pathway_stage'] == 'Achieved'])
    kpis['achievement_rate'] = kpis['solutions_achieved'] / kpis['total_beneficiaries'] if kpis['total_beneficiaries'] > 0 else 0
    
    # Female-headed households
    kpis['female_hoh_count'] = len(df[df['gender_hoh'] == 'Female'])
    kpis['female_hoh_percentage'] = kpis['female_hoh_count'] / kpis['total_beneficiaries'] if kpis['total_beneficiaries'] > 0 else 0
    
    # Livelihood support
    kpis['livelihood_support_count'] = len(df[df['livelihood_support'] == 'Yes'])
    kpis['livelihood_support_percentage'] = kpis['livelihood_support_count'] / kpis['total_beneficiaries'] if kpis['total_beneficiaries'] > 0 else 0
    
    # Documentation status
    kpis['complete_documentation'] = len(df[df['documentation_status'] == 'Complete'])
    kpis['documentation_rate'] = kpis['complete_documentation'] / kpis['total_beneficiaries'] if kpis['total_beneficiaries'] > 0 else 0
    
    # Shelter status breakdown
    kpis['emergency_shelter'] = len(df[df['shelter_status'] == 'Emergency'])
    kpis['transitional_shelter'] = len(df[df['shelter_status'] == 'Transitional'])
    kpis['permanent_shelter'] = len(df[df['shelter_status'] == 'Permanent'])
    
    # Displacement status breakdown
    kpis['idp_count'] = len(df[df['displacement_status'] == 'IDP'])
    kpis['returnee_count'] = len(df[df['displacement_status'] == 'Returnee'])
    kpis['host_community_count'] = len(df[df['displacement_status'] == 'Host Community'])
    
    # Solutions pathway breakdown
    kpis['return_pathway'] = len(df[df['solutions_pathway'] == 'Return'])
    kpis['local_integration_pathway'] = len(df[df['solutions_pathway'] == 'Local Integration'])
    kpis['relocation_pathway'] = len(df[df['solutions_pathway'] == 'Relocation'])
    
    # Stage breakdown
    kpis['assessment_stage'] = len(df[df['pathway_stage'] == 'Assessment'])
    kpis['planning_stage'] = len(df[df['pathway_stage'] == 'Planning'])
    kpis['implementation_stage'] = len(df[df['pathway_stage'] == 'Implementation'])
    kpis['achieved_stage'] = len(df[df['pathway_stage'] == 'Achieved'])
    
    # Average household size
    kpis['avg_household_size'] = df['household_size'].mean()
    
    # Regional coverage
    kpis['regions_covered'] = df['region'].nunique()
    kpis['districts_covered'] = df['district'].nunique()
    
    return kpis


def prepare_sankey_data(
    df: pd.DataFrame,
    source_col: str = 'displacement_status',
    middle_col: str = 'solutions_pathway',
    target_col: str = 'pathway_stage'
) -> Tuple[List, List, List]:
    """
    Prepare data for Sankey diagram visualization.
    
    Args:
        df: Processed DataFrame
        source_col: Source column name
        middle_col: Middle column name
        target_col: Target column name
        
    Returns:
        Tuple of (labels, sources, targets, values)
    """
    
    # Get unique values
    source_values = df[source_col].unique().tolist()
    middle_values = df[middle_col].unique().tolist()
    target_values = df[target_col].unique().tolist()
    
    # Create combined label list
    labels = source_values + middle_values + target_values
    
    # Create index mapping
    label_to_idx = {label: idx for idx, label in enumerate(labels)}
    
    # Calculate flows
    source_to_middle = df.groupby([source_col, middle_col]).size().reset_index(name='count')
    middle_to_target = df.groupby([middle_col, target_col]).size().reset_index(name='count')
    
    sources = []
    targets = []
    values = []
    
    # Source to middle flows
    for _, row in source_to_middle.iterrows():
        sources.append(label_to_idx[row[source_col]])
        targets.append(label_to_idx[row[middle_col]])
        values.append(row['count'])
    
    # Middle to target flows
    for _, row in middle_to_target.iterrows():
        sources.append(label_to_idx[row[middle_col]])
        targets.append(label_to_idx[row[target_col]])
        values.append(row['count'])
    
    return labels, sources, targets, values


def get_monthly_trends(
    df: pd.DataFrame,
    date_col: str = 'registration_date',
    value_col: Optional[str] = None
) -> pd.DataFrame:
    """
    Calculate monthly registration trends.
    
    Args:
        df: Processed DataFrame
        date_col: Date column name
        value_col: Optional value column for aggregation
        
    Returns:
        DataFrame with monthly trends
    """
    
    df = df.copy()
    df['month'] = df[date_col].dt.to_period('M')
    
    if value_col:
        monthly = df.groupby('month')[value_col].sum().reset_index()
        monthly.columns = ['month', 'value']
    else:
        monthly = df.groupby('month').size().reset_index(name='count')
        monthly.columns = ['month', 'value']
    
    monthly['month'] = monthly['month'].astype(str)
    monthly['cumulative'] = monthly['value'].cumsum()
    
    return monthly


def get_regional_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate summary statistics by region.
    
    Args:
        df: Processed DataFrame
        
    Returns:
        DataFrame with regional summary
    """
    
    summary = df.groupby('region').agg({
        'beneficiary_id': 'count',
        'household_size': 'sum',
        'is_female_hoh': 'sum',
        'is_achieved': 'sum',
        'has_livelihood_support': 'sum'
    }).reset_index()
    
    summary.columns = [
        'region', 'beneficiaries', 'individuals',
        'female_hoh', 'achieved', 'livelihood_support'
    ]
    
    # Calculate percentages
    summary['achievement_rate'] = (summary['achieved'] / summary['beneficiaries'] * 100).round(1)
    summary['female_hoh_rate'] = (summary['female_hoh'] / summary['beneficiaries'] * 100).round(1)
    
    return summary.sort_values('beneficiaries', ascending=False)


def get_pathway_progress(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate progress through pathways.
    
    Args:
        df: Processed DataFrame
        
    Returns:
        DataFrame with pathway progress
    """
    
    # Define stage order
    stage_order = ['Assessment', 'Planning', 'Implementation', 'Achieved']
    
    progress = df.groupby(['solutions_pathway', 'pathway_stage']).size().unstack(fill_value=0)
    
    # Reorder columns
    progress = progress.reindex(columns=stage_order, fill_value=0)
    
    # Calculate totals and percentages
    progress['Total'] = progress.sum(axis=1)
    progress['Achievement Rate'] = (progress['Achieved'] / progress['Total'] * 100).round(1)
    
    return progress


def calculate_period_comparison(
    df: pd.DataFrame,
    current_start: datetime,
    current_end: datetime,
    previous_start: datetime,
    previous_end: datetime
) -> Dict:
    """
    Compare metrics between two time periods.
    
    Args:
        df: Processed DataFrame
        current_start: Start of current period
        current_end: End of current period
        previous_start: Start of previous period
        previous_end: End of previous period
        
    Returns:
        Dictionary with comparison metrics
    """
    
    current_df = df[
        (df['registration_date'] >= current_start) &
        (df['registration_date'] <= current_end)
    ]
    
    previous_df = df[
        (df['registration_date'] >= previous_start) &
        (df['registration_date'] <= previous_end)
    ]
    
    comparison = {
        'current_beneficiaries': len(current_df),
        'previous_beneficiaries': len(previous_df),
        'beneficiary_change': len(current_df) - len(previous_df),
        
        'current_achieved': len(current_df[current_df['pathway_stage'] == 'Achieved']),
        'previous_achieved': len(previous_df[previous_df['pathway_stage'] == 'Achieved']),
        'achieved_change': len(current_df[current_df['pathway_stage'] == 'Achieved']) - 
                          len(previous_df[previous_df['pathway_stage'] == 'Achieved']),
        
        'current_individuals': current_df['household_size'].sum(),
        'previous_individuals': previous_df['household_size'].sum(),
        'individuals_change': current_df['household_size'].sum() - previous_df['household_size'].sum()
    }
    
    return comparison


def export_to_excel(df: pd.DataFrame, filepath: str, summary: bool = True) -> None:
    """
    Export data to Excel with multiple sheets.
    
    Args:
        df: Processed DataFrame
        filepath: Output file path
        summary: Whether to include summary sheets
    """
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        # Raw data
        df.to_excel(writer, sheet_name='Raw Data', index=False)
        
        if summary:
            # Regional summary
            regional = get_regional_summary(df)
            regional.to_excel(writer, sheet_name='Regional Summary', index=False)
            
            # Pathway progress
            pathway = get_pathway_progress(df)
            pathway.to_excel(writer, sheet_name='Pathway Progress')
            
            # Monthly trends
            monthly = get_monthly_trends(df)
            monthly.to_excel(writer, sheet_name='Monthly Trends', index=False)
            
            # KPIs
            kpis = calculate_kpis(df)
            kpi_df = pd.DataFrame(list(kpis.items()), columns=['Indicator', 'Value'])
            kpi_df.to_excel(writer, sheet_name='KPIs', index=False)
