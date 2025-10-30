import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_match_distribution(df):
    """Create histogram of match rate distribution"""
    if df.empty:
        return create_empty_plot("No data available")
    
    try:
        fig = px.histogram(
            df, 
            x='final_match_rate',
            title='📊 Distribution of Match Rates',
            labels={'final_match_rate': 'Final Match Rate (%)'},
            color_discrete_sequence=['#3366CC'],
            nbins=15,
            opacity=0.8
        )
        
        fig.update_layout(
            showlegend=False,
            xaxis_title="Match Rate (%)",
            yaxis_title="Number of Candidates",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        # Add mean line
        mean_match = df['final_match_rate'].mean()
        fig.add_vline(x=mean_match, line_dash="dash", line_color="red", 
                     annotation_text=f"Mean: {mean_match:.1f}%")
        
        return fig
    except Exception as e:
        return create_error_plot(f"Error creating distribution: {e}")

def create_top_candidates_chart(df, top_n=10):
    """Create horizontal bar chart of top candidates"""
    if df.empty:
        return create_empty_plot("No data available")
    
    try:
        top_df = df.head(top_n).sort_values('final_match_rate', ascending=True)
        
        fig = px.bar(
            top_df, 
            x='final_match_rate', 
            y='fullname',
            title=f'🏆 Top {top_n} Candidates by Match Rate',
            labels={'final_match_rate': 'Match Rate (%)', 'fullname': 'Candidate'},
            color='final_match_rate',
            color_continuous_scale='Viridis',
            orientation='h',
            text='final_match_rate'
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_range=[0, 100],
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            showlegend=False
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside'
        )
        
        return fig
    except Exception as e:
        return create_error_plot(f"Error creating top candidates chart: {e}")

def create_experience_vs_match_scatter(df):
    """Create scatter plot of experience vs match rate"""
    if df.empty:
        return create_empty_plot("No data available")
    
    try:
        # Convert months to years for better readability
        df = df.copy()
        df['experience_years'] = df['years_of_service_months'] / 12
        
        fig = px.scatter(
            df, 
            x='experience_years', 
            y='final_match_rate',
            size='final_match_rate', 
            color='final_match_rate',
            hover_data=['fullname', 'grade', 'directorate'],
            title='📈 Experience vs Match Rate',
            labels={
                'experience_years': 'Experience (Years)', 
                'final_match_rate': 'Match Rate (%)',
                'grade': 'Grade Level'
            },
            color_continuous_scale='Plasma',
            size_max=15
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        return fig
    except Exception as e:
        return create_error_plot(f"Error creating scatter plot: {e}")

def create_strengths_analysis(df):
    """Analyze and visualize common strengths"""
    if df.empty or 'top_strengths' not in df.columns:
        return None
    
    try:
        all_strengths = []
        for strengths in df['top_strengths'].dropna():
            if strengths and isinstance(strengths, str):
                cleaned_strengths = [s.strip() for s in strengths.split(',')]
                all_strengths.extend(cleaned_strengths)
        
        if not all_strengths:
            return create_empty_plot("No strengths data available")
        
        strengths_counts = pd.Series(all_strengths).value_counts().head(10)
        
        fig = px.bar(
            strengths_counts, 
            title='💪 Top 10 Most Common Strengths',
            labels={'index': 'Strength', 'value': 'Frequency'},
            color=strengths_counts.values,
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45,
            height=400
        )
        
        return fig
    except Exception as e:
        return create_error_plot(f"Error creating strengths analysis: {e}")

def create_tgv_comparison_chart(df):
    """Create comparison of talent dimension scores"""
    if df.empty:
        return create_empty_plot("No data available")
    
    try:
        # Check if we have the category scores
        category_columns = ['competency_score', 'cognitive_score', 'work_efficiency_score', 'behavioral_score', 'experience_score']
        available_columns = [col for col in category_columns if col in df.columns]
        
        if not available_columns:
            return create_empty_plot("No category score data available")
        
        # Calculate average scores for each category
        avg_scores = {}
        for col in available_columns:
            avg_scores[col.replace('_score', '').title()] = df[col].mean()
        
        scores_df = pd.DataFrame(list(avg_scores.items()), columns=['Category', 'Average Score'])
        scores_df = scores_df.sort_values('Average Score', ascending=True)
        
        fig = px.bar(
            scores_df,
            x='Average Score',
            y='Category',
            title='📈 Average Scores by Talent Dimension',
            labels={'Average Score': 'Average Score (%)', 'Category': 'Talent Dimension'},
            color='Average Score',
            color_continuous_scale='Viridis',
            orientation='h'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            showlegend=False
        )
        
        return fig
    except Exception as e:
        return create_error_plot(f"Error creating category comparison: {e}")

def create_radar_chart(candidate_data):
    """Create radar chart for individual candidate profile"""
    try:
        categories = ['Competency', 'Cognitive', 'Work Efficiency', 'Behavioral', 'Experience']
        
        # Extract values from candidate data
        values = [
            candidate_data.get('competency_score', 0) if 'competency_score' in candidate_data else candidate_data.get('final_match_rate', 0) * 0.9,
            candidate_data.get('cognitive_score', 0) if 'cognitive_score' in candidate_data else candidate_data.get('final_match_rate', 0) * 0.8,
            candidate_data.get('work_efficiency_score', 0) if 'work_efficiency_score' in candidate_data else candidate_data.get('final_match_rate', 0) * 0.85,
            candidate_data.get('behavioral_score', 0) if 'behavioral_score' in candidate_data else candidate_data.get('final_match_rate', 0) * 0.75,
            candidate_data.get('experience_score', 0) if 'experience_score' in candidate_data else candidate_data.get('final_match_rate', 0) * 0.7
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=candidate_data['fullname'],
            line=dict(color='#3366CC')
        ))
        
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title=f"Profile Radar - {candidate_data['fullname']}",
            height=400
        )
        
        return fig
    except Exception as e:
        return create_error_plot(f"Error creating radar chart: {e}")

def create_empty_plot(message):
    """Create empty plot with message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    return fig

def create_error_plot(error_message):
    """Create error plot"""
    fig = go.Figure()
    fig.add_annotation(
        text=f"Error: {error_message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color="red")
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    return fig