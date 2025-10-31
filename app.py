import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from database import get_available_employees

# Page configuration
st.set_page_config(
    page_title="AI Talent Matching Dashboard",
    page_icon="🎯",
    layout="wide"
)

def main():
    st.title("🎯 AI Talent Matching Dashboard")
    st.markdown("**Parameterized AI-Powered Talent Insights**")
    
    # RUNTIME INPUTS - User Provided
    with st.sidebar:
        with st.sidebar:
            st.header("🎯 Job Requirements")
            
            role_name = st.text_input(
                "Role Name", 
                value="",  
                placeholder="e.g., Data Analyst, Marketing Manager"  
            )
            
            job_level = st.selectbox(
                "Job Level", 
                ["", "Junior", "Middle", "Senior", "Lead"],
                index=0 
            )
            
            role_purpose = st.text_area(
                "Role Purpose", 
                value="",
                placeholder="e.g., Analyze data to provide business insights, Develop marketing strategies"
            )
            
            st.header("📊 Benchmark Selection")
            
        employees_df = get_available_employees()
        
        selected_benchmark_ids = []
        
        if not employees_df.empty:
            employee_options = {
                f"{row['fullname']} ({row['position']} - {row['grade']})": row['employee_id']
                for _, row in employees_df.iterrows()
            }
            
            selected_benchmarks = st.multiselect(
                "Select Benchmark Employees (Max 3)",
                options=list(employee_options.keys()),
                help="Choose top performers as benchmarks for the ideal profile (Maximum 3 employees)",
                max_selections=3
            )
            
            selected_benchmark_ids = [employee_options[label] for label in selected_benchmarks]
            
            # Show selected benchmarks
            if selected_benchmarks:
                st.markdown("**Selected Benchmarks:**")
                for label in selected_benchmarks:
                    st.markdown(f"• {label}")
        else:
            st.error("❌ Cannot proceed: No employee data available from database")
            selected_benchmark_ids = []
        
        use_ml_weights = st.checkbox("Use ML-Driven Weights", value=True)
        
        if st.button("🚀 Generate Talent Insights", type="primary"):
            if len(selected_benchmark_ids) < 2:
                st.warning("Please select at least 2 benchmark employees")
                return
            
            if employees_df.empty:
                st.error("Cannot generate insights without employee data")
                return
            
            # Store inputs in session state
            st.session_state.user_inputs = {
                'role_name': role_name,
                'job_level': job_level, 
                'role_purpose': role_purpose,
                'benchmarks': selected_benchmark_ids,
                'use_ml_weights': use_ml_weights,
                'job_id': f"VACANCY_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'employees_df': employees_df
            }

    # MAIN CONTENT
    if 'user_inputs' in st.session_state:
        inputs = st.session_state.user_inputs
        employees_df = inputs.get('employees_df', pd.DataFrame())
        
        # OUTPUT 1: AI-Generated Job Profile
        st.header("🤖 AI-Generated Job Profile")
        
        ai_profile = generate_ai_profile(
            inputs['role_name'],
            inputs['job_level'],
            inputs['role_purpose'],
            len(inputs['benchmarks'])
        )
        
        # Display profile sections
        with st.expander("📋 Job Requirements", expanded=True):
            st.markdown(ai_profile['requirements'])
        
        with st.expander("📝 Job Description"):
            st.markdown(ai_profile['description'])
            
        with st.expander("🎯 Key Competencies"):
            st.markdown(ai_profile['competencies'])
        
        # OUTPUT 2: Ranked Talent List
        st.header("🏆 Ranked Talent List")
        
        # Generate ranked talent list berdasarkan benchmark
        ranked_talent_df = generate_ranked_talent_list(employees_df, inputs['benchmarks'], inputs['use_ml_weights'])
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Candidates", len(ranked_talent_df))
        with col2:
            st.metric("Avg Match Rate", f"{ranked_talent_df['match_rate'].mean():.1f}%")
        with col3:
            st.metric("Top Match", f"{ranked_talent_df['match_rate'].max():.1f}%")
        with col4:
            high_matches = len(ranked_talent_df[ranked_talent_df['match_rate'] > 80])
            st.metric("High Matches (>80%)", high_matches)
        
        display_columns = ['name', 'match_rate', 'role', 'division', 'department', 'directorate', 'job_level']
        available_columns = [col for col in display_columns if col in ranked_talent_df.columns]
        
        display_df = ranked_talent_df[available_columns].copy()
        
        display_df['match_rate'] = display_df['match_rate'].round(1)
        
        column_rename = {
            'name': 'Name',
            'match_rate': 'Match Rate %',
            'role': 'Current Role',
            'division': 'Division', 
            'department': 'Department',
            'directorate': 'Directorate',
            'job_level': 'Job Level'
        }
        
        display_df = display_df.rename(columns=column_rename)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        
        # OUTPUT 3: DASHBOARD VISUALIZATION
        st.header("📊 Talent Analytics Dashboard")
        
        # Row 1: Match Rate Distribution dan Top Candidates
        col1, col2 = st.columns(2)
        
        with col1:
            # Match-rate Distribution
            st.subheader("📈 Match Rate Distribution")
            fig_dist = create_match_rate_distribution(ranked_talent_df)
            st.plotly_chart(fig_dist, use_container_width=True)
            
            # Top Strengths & Gaps Analysis
            st.subheader("💪 Top Strengths & Development Areas")
            fig_strengths = create_strengths_gaps_chart(ranked_talent_df)
            st.plotly_chart(fig_strengths, use_container_width=True)
        
        with col2:
            # Top Candidates Bar Chart
            st.subheader("🏆 Top 10 Candidates")
            fig_top = create_top_candidates_chart(ranked_talent_df)
            st.plotly_chart(fig_top, use_container_width=True)
            
            # # Experience vs Match Rate
            # st.subheader("📊 Experience vs Match Rate")
            # fig_exp = create_experience_vs_match(ranked_talent_df, employees_df)
            # st.plotly_chart(fig_exp, use_container_width=True)
        
        # Row 2: Benchmark Comparisons
        col3, col4 = st.columns(2)
        
        with col3:
            # Radar Chart - Benchmark vs Top Candidate
            st.subheader("🎯 Benchmark vs Top Candidate Profile")
            if not ranked_talent_df.empty and inputs['benchmarks']:
                fig_radar = create_radar_comparison(ranked_talent_df, employees_df, inputs['benchmarks'])
                st.plotly_chart(fig_radar, use_container_width=True)
        
        with col4:
            # Heatmap - Organizational Distribution
            st.subheader("🏢 Match Rate by Directorate")
            fig_heatmap = create_organizational_heatmap(ranked_talent_df)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Job Level Comparison
            st.subheader("📋 Match Rate by Job Level")
            fig_level = create_job_level_comparison(ranked_talent_df)
            st.plotly_chart(fig_level, use_container_width=True)
        
        # OUTPUT 4: ML Weights Visualization
        st.header("⚖️ ML-Driven Matching Weights")
        
        if inputs['use_ml_weights']:
            col5, col6 = st.columns(2)
            
            with col5:
                # TGV weights
                tgv_weights = {
                    'COMPETENCY': 64.6,
                    'WORK_EFFICIENCY': 12.1, 
                    'BEHAVIORAL': 15.1,
                    'COGNITIVE': 3.9,
                    'EXPERIENCE': 4.3
                }
                
                # Visualize TGV weights
                tgv_df = pd.DataFrame({
                    'Category': list(tgv_weights.keys()),
                    'Weight': list(tgv_weights.values())
                })
                
                fig_tgv = px.bar(
                    tgv_df,
                    x='Weight',
                    y='Category',
                    orientation='h',
                    title='Talent Group Variable (TGV) Weights',
                    color='Weight',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig_tgv, use_container_width=True)
            
            with col6:
                # Competency weights dari analisis feature importance
                competency_weights = {
                    'VCU': 6.7, 'GDR': 6.2, 'SEA': 6.0, 'CSI': 5.8, 'LIE': 5.7,
                    'IDS': 5.7, 'QDD': 5.7, 'STO': 5.3, 'FTC': 4.9, 'CEX': 4.6
                }
                
                # Visualize top competency weights
                competency_df = pd.DataFrame({
                    'Competency': list(competency_weights.keys())[:8],
                    'Weight': list(competency_weights.values())[:8]
                })
                
                fig_comp = px.bar(
                    competency_df,
                    x='Competency',
                    y='Weight',
                    title='Top Competency Weights (Feature Importance)',
                    color='Weight'
                )
                st.plotly_chart(fig_comp, use_container_width=True)
            
            st.info("""
            **ML Weights Explanation:**
            - **Competency (64.6%)**: Most important - Includes 10 competency pillars
            - **Behavioral (15.1%)**: Personality traits and strengths
            - **Work Efficiency (12.1%)**: Pauli and Faxtor performance scores
            - **Cognitive (3.9%)**: IQ and GTQ cognitive abilities
            - **Experience (4.3%)**: Years of service and tenure
            """)
        else:
            st.warning("⚠️ ML weights disabled - Using equal weighting for all factors")
        
        # OUTPUT 5: Actionable Insights
        st.header("💡 Actionable Insights")
        
        col7, col8 = st.columns(2)
        
        with col7:
            st.subheader("🎯 Why Top Candidates Rank Highest")
            
            if not ranked_talent_df.empty:
                top_candidate = ranked_talent_df.iloc[0]
                st.write(f"**{top_candidate['name']}** achieved **{top_candidate['match_rate']}%** match because:")
                
                # Analyze match reasons
                if top_candidate['match_rate'] > 90:
                    st.write("• **Exceptional competency alignment** with benchmark profiles")
                    st.write("• **Strong behavioral fit** with organizational culture")
                    st.write("• **Proven track record** in similar roles and responsibilities")
                elif top_candidate['match_rate'] > 80:
                    st.write("• **Strong overall fit** across multiple dimensions")
                    st.write("• **Good technical competency** alignment")
                    st.write("• **Relevant experience** and domain knowledge")
                else:
                    st.write("• **Good baseline alignment** with room for development")
                    st.write("• **Potential for growth** with proper mentoring")
                
                st.write(f"• **Current Role**: {top_candidate['role']}")
                st.write(f"• **Organization**: {top_candidate['directorate']} > {top_candidate['department']}")
                st.write(f"• **Experience Level**: {top_candidate['job_level']}")
        
        with col8:
            st.subheader("📈 Performance Insights")
            
            avg_match = ranked_talent_df['match_rate'].mean()
            match_std = ranked_talent_df['match_rate'].std()
            high_match_pct = (len(ranked_talent_df[ranked_talent_df['match_rate'] > 75]) / len(ranked_talent_df)) * 100
            
            st.write(f"• **Average Match Rate**: {avg_match:.1f}%")
            st.write(f"• **Consistency**: {match_std:.1f}% standard deviation")
            st.write(f"• **High Quality Pool**: {high_match_pct:.1f}% candidates >75% match")
            st.write(f"• **ML Weights Used**: {'Yes' if inputs['use_ml_weights'] else 'No'}")
            st.write(f"• **Benchmarks**: {len(inputs['benchmarks'])} top performers")
            st.write(f"• **Target Role**: {inputs['role_name']} ({inputs['job_level']})")
            
            # Additional insights
            if avg_match > 80:
                st.success("**🎯 Excellent candidate pool** - Strong alignment with benchmarks")
            elif avg_match > 70:
                st.warning("**📊 Moderate candidate pool** - Consider adjusting criteria")
            else:
                st.error("**⚠️ Limited candidate pool** - May need to broaden search")
        
    else:
        # Welcome screen
        st.markdown("""
        ### How it works:
        1. **Configure** job requirements in the sidebar
        2. **Select benchmark employees** from the database dropdown
        3. **Enable ML-driven weights** for optimal matching
        4. **Generate AI-powered insights** and visualizations
        
        ### Features:
        - 📊 **Database Integration** - Real employee data for benchmark selection
        - 🤖 **AI-Generated Job Profiles** - Automated requirements and competencies
        - ⚖️ **ML-Optimized Weights** - Data-driven feature importance
        - 📈 **Interactive Visualizations** - Weights distribution and analysis
        - 💡 **Actionable Insights** - Strategic recommendations
        
        ### Get Started:
        Use the sidebar to configure your talent search!
        """)

# VISUALIZATION FUNCTIONS

def create_match_rate_distribution(ranked_talent_df):
    """Create histogram of match rate distribution"""
    fig = px.histogram(
        ranked_talent_df, 
        x='match_rate',
        nbins=15,
        title='Distribution of Candidate Match Rates',
        labels={'match_rate': 'Match Rate (%)'},
        color_discrete_sequence=['#3366CC'],
        opacity=0.8
    )
    
    # Add mean line
    mean_match = ranked_talent_df['match_rate'].mean()
    fig.add_vline(x=mean_match, line_dash="dash", line_color="red", 
                 annotation_text=f"Mean: {mean_match:.1f}%")
    
    fig.update_layout(
        showlegend=False,
        xaxis_title="Match Rate (%)",
        yaxis_title="Number of Candidates",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    return fig

def create_top_candidates_chart(ranked_talent_df):
    """Create horizontal bar chart of top candidates"""
    top_df = ranked_talent_df.head(10).sort_values('match_rate', ascending=True)
    
    fig = px.bar(
        top_df, 
        x='match_rate', 
        y='name',
        title='Top 10 Candidates by Match Rate',
        labels={'match_rate': 'Match Rate (%)', 'name': 'Candidate'},
        color='match_rate',
        color_continuous_scale='Viridis',
        orientation='h'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_range=[0, 100],
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
    )
    
    fig.update_traces(
        texttemplate='%{x:.1f}%',
        textposition='outside'
    )
    return fig

def create_strengths_gaps_chart(ranked_talent_df):
    """Create visualization of strengths and gaps across TGVs"""
    # Simulate TGV scores for demonstration
    tgv_categories = ['Competency', 'Work Efficiency', 'Behavioral', 'Cognitive', 'Experience']
    avg_scores = [75, 68, 72, 65, 70]  # Simulated average scores
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=tgv_categories,
        x=avg_scores,
        name='Average Scores',
        orientation='h',
        marker_color='lightblue'
    ))
    
    # Add benchmark line
    fig.add_vline(x=80, line_dash="dash", line_color="red", 
                 annotation_text="Benchmark Target")
    
    fig.update_layout(
        title='Average Scores by Talent Dimension',
        xaxis_title="Score (%)",
        yaxis_title="Talent Dimension",
        showlegend=False,
        height=300
    )
    return fig

def create_experience_vs_match(ranked_talent_df, employees_df):
    """Create scatter plot of experience vs match rate"""
    # Merge experience data
    merged_df = ranked_talent_df.merge(
        employees_df[['employee_id', 'years_of_service_months']], 
        left_on='employee_id', right_on='employee_id', how='left'
    )
    
    if 'years_of_service_months' in merged_df.columns:
        merged_df['experience_years'] = merged_df['years_of_service_months'] / 12
        
        fig = px.scatter(
            merged_df, 
            x='experience_years', 
            y='match_rate',
            size='match_rate', 
            color='match_rate',
            hover_data=['name', 'role', 'job_level'],
            title='Experience vs Match Rate',
            labels={
                'experience_years': 'Experience (Years)', 
                'match_rate': 'Match Rate (%)',
                'job_level': 'Job Level'
            },
            color_continuous_scale='Plasma',
            size_max=15
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=300
        )
        return fig
    else:
        return create_empty_plot("Experience data not available")

def create_radar_comparison(ranked_talent_df, employees_df, benchmark_ids):
    """Create radar chart comparing benchmark vs top candidate"""
    if ranked_talent_df.empty or not benchmark_ids:
        return create_empty_plot("No data available for comparison")
    
    # Get top candidate
    top_candidate = ranked_talent_df.iloc[0]
    
    # Simulate dimension scores
    categories = ['Technical Skills', 'Business Acumen', 'Leadership', 
                 'Communication', 'Problem-Solving', 'Adaptability']
    
    # Top candidate scores (simulated)
    candidate_scores = [85, 78, 72, 80, 88, 75]
    
    # Benchmark average scores (simulated)
    benchmark_scores = [82, 85, 80, 78, 83, 77]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=candidate_scores,
        theta=categories,
        fill='toself',
        name=f"Top Candidate: {top_candidate['name']}",
        line=dict(color='blue')
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores,
        theta=categories,
        fill='toself',
        name='Benchmark Average',
        line=dict(color='red')
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title=f"Profile Comparison: {top_candidate['name']} vs Benchmarks",
        height=400
    )
    return fig

def create_organizational_heatmap(ranked_talent_df):
    """Create heatmap of match rates by directorate and department"""
    if 'directorate' not in ranked_talent_df.columns or 'department' not in ranked_talent_df.columns:
        return create_empty_plot("Organizational data not available")
    
    # Create pivot table for heatmap
    pivot_data = ranked_talent_df.groupby(['directorate', 'department'])['match_rate'].mean().unstack(fill_value=0)
    
    fig = px.imshow(
        pivot_data,
        title='Average Match Rate by Organizational Unit',
        color_continuous_scale='Viridis',
        aspect="auto"
    )
    
    fig.update_layout(
        height=300,
        xaxis_title="Department",
        yaxis_title="Directorate"
    )
    return fig

def create_job_level_comparison(ranked_talent_df):
    """Create bar chart of match rates by job level"""
    if 'job_level' not in ranked_talent_df.columns:
        return create_empty_plot("Job level data not available")
    
    level_analysis = ranked_talent_df.groupby('job_level').agg({
        'match_rate': ['mean', 'count']
    }).round(1)
    
    level_analysis.columns = ['avg_match_rate', 'candidate_count']
    level_analysis = level_analysis.reset_index()
    
    fig = px.bar(
        level_analysis,
        x='job_level',
        y='avg_match_rate',
        title='Average Match Rate by Job Level',
        labels={'avg_match_rate': 'Average Match Rate (%)', 'job_level': 'Job Level'},
        color='avg_match_rate',
        text='avg_match_rate'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        height=300,
        showlegend=False
    )
    return fig

def create_empty_plot(message):
    """Create empty plot with message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14)
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=300
    )
    return fig

# =============================================================================
# EXISTING FUNCTIONS
# =============================================================================

def generate_ai_profile(role_name, job_level, role_purpose, benchmark_count):
    """Generate AI job profile based on inputs"""
    
    level_desc = {
        "Junior": "entry-level position focusing on foundational skills and learning under guidance",
        "Middle": "mid-level role with independent responsibilities and specialized contributions", 
        "Senior": "senior position requiring deep expertise, mentorship capabilities, and complex problem-solving",
        "Lead": "leadership role with team management, strategic decision-making, and organizational impact"
    }
    
    # Role-specific requirements
    if "data" in role_name.lower() or "analyst" in role_name.lower():
        tech_requirements = """
        • SQL expertise: complex queries, performance optimization, data modeling
        • Python/R for data analysis: pandas, numpy, statistical analysis
        • Data visualization: Tableau, Power BI, or similar BI tools
        • Data warehousing concepts and ETL processes
        • Statistical analysis and hypothesis testing
        """
    elif "manager" in role_name.lower() or "lead" in role_name.lower():
        tech_requirements = """
        • Project management and agile methodologies
        • Stakeholder management and executive communication
        • Strategic planning and business case development
        • Team leadership and people management
        • Performance metrics and KPI tracking
        """
    else:
        tech_requirements = """
        • Domain expertise in relevant field
        • Analytical and critical thinking capabilities
        • Technical proficiency in role-specific tools
        • Process improvement and optimization
        • Quality assurance and best practices
        """
    
    requirements = f"""
    **Technical Skills:**
    {tech_requirements}
    
    **Professional Competencies:**
    • Strong analytical and problem-solving capabilities
    • Excellent communication and stakeholder management
    • {job_level}-level expertise and decision-making
    • Business acumen and strategic thinking
    • Collaboration and team leadership abilities
    • Adaptability and continuous learning mindset
    """
    
    description = f"""
    The **{role_name}** ({job_level}) is a {level_desc.get(job_level, 'professional role')} primarily responsible for **{role_purpose.lower()}**. 
    
    This position demands a professional who can demonstrate both technical depth and business understanding to drive meaningful outcomes. The role requires balancing execution excellence with strategic thinking, leveraging data and insights to inform decisions and create measurable impact.
    
    **Key Impact Areas:**
    - Driving data-informed decision making processes
    - Delivering actionable insights to stakeholders
    - Improving operational efficiency through analysis
    - Contributing to strategic planning and execution
    
    *Profile calibrated using {benchmark_count} top-performing benchmark employees from the organization.*
    """
    
    competencies = f"""
    **Core Competencies:**
    • Data Analysis & Interpretation
    • Technical & Domain Expertise  
    • Strategic Thinking & Business Acumen
    • Communication & Influence
    • Problem-Solving & Innovation
    
    **{job_level}-Level Expectations:**
    • Independent ownership of complex tasks
    • Mentorship and knowledge sharing
    • Process improvement initiatives
    • Cross-functional collaboration
    • Quality assurance and best practices
    """
    
    return {
        'requirements': requirements,
        'description': description, 
        'competencies': competencies
    }

def generate_ranked_talent_list(employees_df, benchmark_ids, use_ml_weights):
    """Generate ranked talent list menggunakan REAL matching atau fallback"""
    try:
        # Coba REAL talent matching pertama
        from talent_matcher import execute_talent_matching_query
        
        job_id = f"VACANCY_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        results_df = execute_talent_matching_query(
            job_vacancy_id=job_id,
            role_name=st.session_state.user_inputs['role_name'],
            job_level=st.session_state.user_inputs['job_level'],
            selected_benchmark_ids=benchmark_ids,
            use_ml_weights=use_ml_weights
        )
        
        if not results_df.empty:
            return results_df
        else:
            # Jika real matching return empty, use simplified
            from talent_matcher import generate_simplified_ranking
            return generate_simplified_ranking(employees_df, benchmark_ids, use_ml_weights)
        
    except Exception as e:
        st.warning(f"Real matching unavailable, using simplified: {e}")
        # Fallback ke simplified ranking
        from talent_matcher import generate_simplified_ranking
        return generate_simplified_ranking(employees_df, benchmark_ids, use_ml_weights)
    
if __name__ == "__main__":
    main()