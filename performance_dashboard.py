import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from collections import Counter
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Page config
# Page config
st.set_page_config(
    page_title="Employee Performance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force light mode
st.markdown("""
<script>
    // Force Streamlit to light mode after page load
    document.addEventListener("DOMContentLoaded", function() {
        document.documentElement.setAttribute('data-theme', 'light');
        document.body.setAttribute('data-theme', 'light');
    });
</script>
""", unsafe_allow_html=True)



# Enhanced custom CSS with dark mode compatibility
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.1);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .stMetric {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Dark mode compatibility for metric cards */
    [data-theme="dark"] .stMetric {
        background: linear-gradient(145deg, #2d3748, #4a5568);
        border: 1px solid #4a5568;
        color: white;
    }

    /* 🔧 Fix Streamlit metric text visibility in dark/light mode */
    @media (prefers-color-scheme: dark) {
      div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1f2937, #374151) !important;
        border: 1px solid #374151 !important;
        border-radius: 12px !important;
      }

      div[data-testid="stMetric"] * {
        color: #e5e7eb !important; /* readable gray */
      }

      div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #ffffff !important; /* main value */
        font-weight: 700 !important;
      }

      div[data-testid="stMetric"] [data-testid="stMetricLabel"],
      div[data-testid="stMetric"] .stMetricLabel {
        color: #cbd5e1 !important; /* label text */
      }
    }

    @media (prefers-color-scheme: light) {
      div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #f8fafc, #e2e8f0) !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        color: #111827 !important;
      }
    }
    
    .role-header {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    .employee-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.2);
    }
    
    .insight-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.2);
    }
    
    .performance-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
    }
    
    .badge-excellent { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .badge-good { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
    .badge-average { background: linear-gradient(135deg, #ffecd2, #fcb69f); color: #333; }
    .badge-needs-improvement { background: linear-gradient(135deg, #ff9a9e, #fecfef); color: #333; }
    
    .dashboard-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 2rem;
    }
    
    [data-theme="dark"] .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .individual-feedback {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    [data-theme="dark"] .individual-feedback {
        background: rgba(102, 126, 234, 0.2);
        border: 1px solid rgba(102, 126, 234, 0.5);
        color: white;
    }
    
    .individual-feedback h4 {
        color: #667eea;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    [data-theme="dark"] .individual-feedback h4 {
        color: #a3b8ff;
    }
    
    .individual-feedback ul {
        list-style-type: none;
        padding-left: 0;
    }
    
    .individual-feedback li {
        padding: 0.3rem 0;
        border-bottom: 1px solid rgba(102, 126, 234, 0.1);
    }
    
    [data-theme="dark"] .individual-feedback li {
        border-bottom: 1px solid rgba(102, 126, 234, 0.3);
        color: #e2e8f0;
    }
    
    .chart-spacing {
        margin: 2rem 0;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


class EnhancedPerformanceDashboard:
    def __init__(self):
        self.weekly_data = None
        self.monthly_data = None
        
        # Enhanced color palette
        self.colors = {
            'primary': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
            'secondary': ['#a8edea', '#fed6e3', '#d299c2', '#fef9d7', '#eea2a2', '#bbc1bf'],
            'gradient_1': ['#667eea', '#764ba2'],
            'gradient_2': ['#f093fb', '#f5576c'],
            'gradient_3': ['#4facfe', '#00f2fe'],
            'performance': {
                'excellent': '#667eea',
                'good': '#f093fb', 
                'average': '#ffecd2',
                'needs_improvement': '#ff9a9e'
            }
        }
        
        self.column_mapping = {
            # Basic info
            'Name': ['Name', 'name', 'Employee Name', 'employee_name'],
            'Role': ['Role', 'role', 'Position', 'position'],
            'Week Start Date': ['Week Start Date', 'week_start', 'start_date', 'Week Start'],
            'Week End Date': ['Week End Date', 'week_end', 'end_date', 'Week End'],
            
            # Video Editor
            'Videos Created': ['How many videos did you create this week?', 'videos_created', 'videos'],
            'Video Clients': ['Which clients did you work for this week?', 'video_clients'],
            'Video Problems': ['Did you face any problems this week?', 'video_problems'],
            'Video Productivity': ['Overall productivity this week', 'video_productivity'],
            
            # Designer
            'Designs Created': ['How many designs did you create this week?', 'designs_created', 'designs'],
            'Design Types': ['What types of designs did you make?', 'design_types'],
            'Design Clients': ['Which clients did you work for this week?', 'design_clients'],
            'Design Problems': ['Did you face any problems this week?', 'design_problems'],
            'Design Productivity': ['Overall productivity this week', 'design_productivity'],
            
            # Account Manager
            'Scripts Produced': ['How many scripts did you produce this week?', 'scripts_produced', 'scripts'],
            'Posts Published': ['How many posts were published this week?', 'posts_published', 'posts'],
            'Client Meetings': ['How many client meetings did you attend this week?', 'client_meetings', 'meetings'],
            'Meeting Takeaways': ['Main takeaway from this week\'s client meetings', 'meeting_takeaways'],
            'AM Problems': ['Did you face any problems this week?', 'am_problems'],
            'AM Productivity': ['Overall productivity this week', 'am_productivity'],
            
            # Filmmaker
            'Projects Worked': ['How many projects did you work on this week?', 'projects_worked', 'projects'],
            'Filmmaker Clients Count': ['How many clients did you work with this week?', 'filmmaker_clients_count'],
            'Filmmaker Clients': ['Who were the clients?', 'filmmaker_clients'],
            'Filmmaker Problems': ['Did you face any problems this week?', 'filmmaker_problems'],
            'Filmmaker Productivity': ['Overall productivity this week', 'filmmaker_productivity'],
            
            # Team Leader
            'Leader Meetings': ['How many client meetings did you have this week?', 'leader_meetings'],
            'Week Review': ['Review of this week overall', 'week_review'],
            'Leader Problems': ['Did you face any problems this week?', 'leader_problems'],
            'Leader Productivity': ['Overall productivity this week', 'leader_productivity'],
            
            # Common
            'Other Comments': ['Any other comments?', 'other_comments', 'additional_comments']
        }

    def find_column(self, df, target_col):
        """Enhanced column finder with fuzzy matching"""
        if target_col in df.columns:
            return target_col
        
        possible_names = self.column_mapping.get(target_col, [target_col])
        for col in df.columns:
            for possible in possible_names:
                if possible.lower() in col.lower():
                    return col
        return None

    def clean_data(self, df):
        """Enhanced data cleaning with better employee identification"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Create a mapping of actual columns to standard names
        column_map = {}
        for standard_name in self.column_mapping.keys():
            actual_col = self.find_column(df, standard_name)
            if actual_col:
                column_map[actual_col] = standard_name
        
        # Rename columns
        df_clean = df.rename(columns=column_map)
        
        # Create unique employee identifier (Name + Role)
        if 'Name' in df_clean.columns and 'Role' in df_clean.columns:
            df_clean['Employee_ID'] = df_clean['Name'] + " (" + df_clean['Role'] + ")"
        
        # Fill missing values
        numeric_cols = ['Videos Created', 'Designs Created', 'Scripts Produced', 'Posts Published', 
                       'Client Meetings', 'Projects Worked', 'Filmmaker Clients Count', 'Leader Meetings']
        
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
        # Clean productivity scores (assuming 1-5 scale)
        productivity_cols = [col for col in df_clean.columns if 'Productivity' in col]
        for col in productivity_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(3)  # Default to 3
                # Ensure values are between 1-5
                df_clean[col] = df_clean[col].clip(1, 5)
        
        # Clean text columns
        text_cols = [col for col in df_clean.columns if col not in numeric_cols + productivity_cols + ['Week Start Date', 'Week End Date']]
        for col in text_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna('').astype(str)
        
        # Parse dates
        date_cols = ['Week Start Date', 'Week End Date']
        for col in date_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        return df_clean

    def get_performance_badge(self, score):
        """Generate performance badge based on score"""
        if score >= 4.5:
            return "excellent", "🌟 Excellent"
        elif score >= 3.5:
            return "good", "✨ Good"
        elif score >= 2.5:
            return "average", "📊 Average" 
        else:
            return "needs_improvement", "⚡ Needs Focus"

    def calculate_enhanced_metrics(self, df, role=None):
        """Enhanced metrics calculation with productivity analysis"""
        if df.empty:
            return {}
        
        if role:
            df_role = df[df['Role'] == role]
        else:
            df_role = df
        
        metrics = {}
        
        # Output metrics by role
        if role == 'Video Editor' or not role:
            if 'Videos Created' in df_role.columns:
                metrics['avg_videos'] = df_role['Videos Created'].mean()
                metrics['total_videos'] = df_role['Videos Created'].sum()
                metrics['max_videos'] = df_role['Videos Created'].max()
                metrics['min_videos'] = df_role['Videos Created'].min()
        
        if role == 'Designer' or not role:
            if 'Designs Created' in df_role.columns:
                metrics['avg_designs'] = df_role['Designs Created'].mean()
                metrics['total_designs'] = df_role['Designs Created'].sum()
                metrics['max_designs'] = df_role['Designs Created'].max()
                metrics['min_designs'] = df_role['Designs Created'].min()
        
        if role == 'Account Manager' or not role:
            if 'Scripts Produced' in df_role.columns:
                metrics['avg_scripts'] = df_role['Scripts Produced'].mean()
                metrics['total_scripts'] = df_role['Scripts Produced'].sum()
            if 'Posts Published' in df_role.columns:
                metrics['avg_posts'] = df_role['Posts Published'].mean()
                metrics['total_posts'] = df_role['Posts Published'].sum()
            if 'Client Meetings' in df_role.columns:
                metrics['avg_meetings'] = df_role['Client Meetings'].mean()
                metrics['total_meetings'] = df_role['Client Meetings'].sum()
        
        if role == 'Filmmaker' or not role:
            if 'Projects Worked' in df_role.columns:
                metrics['avg_projects'] = df_role['Projects Worked'].mean()
                metrics['total_projects'] = df_role['Projects Worked'].sum()
        
        # Enhanced productivity analysis
        productivity_cols = [col for col in df_role.columns if 'Productivity' in col]
        if productivity_cols:
            all_productivity = []
            for col in productivity_cols:
                scores = pd.to_numeric(df_role[col], errors='coerce').dropna()
                all_productivity.extend(scores.tolist())
            
            if all_productivity:
                metrics['avg_productivity'] = np.mean(all_productivity)
                metrics['productivity_std'] = np.std(all_productivity)
                metrics['productivity_min'] = np.min(all_productivity)
                metrics['productivity_max'] = np.max(all_productivity)
                
                # Performance distribution
                excellent = sum(1 for x in all_productivity if x >= 4.5)
                good = sum(1 for x in all_productivity if 3.5 <= x < 4.5)
                average = sum(1 for x in all_productivity if 2.5 <= x < 3.5)
                needs_improvement = sum(1 for x in all_productivity if x < 2.5)
                
                metrics['performance_distribution'] = {
                    'excellent': excellent,
                    'good': good,
                    'average': average,
                    'needs_improvement': needs_improvement
                }
        
        return metrics

    def create_enhanced_kpi_cards(self, metrics, period="Weekly"):
        """Create beautiful KPI cards with enhanced styling"""
        st.markdown(f'<h2 class="dashboard-header">📊 {period} Performance Overview</h2>', unsafe_allow_html=True)
        
        # Main metrics row
        cols = st.columns(4)
        
        with cols[0]:
            if 'total_videos' in metrics:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎬 Total Videos</h3>
                    <h1>{int(metrics['total_videos'])}</h1>
                    <p>Average: {metrics.get('avg_videos', 0):.1f} per person</p>
                </div>
                """, unsafe_allow_html=True)
        
        with cols[1]:
            if 'total_designs' in metrics:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎨 Total Designs</h3>
                    <h1>{int(metrics['total_designs'])}</h1>
                    <p>Average: {metrics.get('avg_designs', 0):.1f} per person</p>
                </div>
                """, unsafe_allow_html=True)
        
        with cols[2]:
            if 'total_scripts' in metrics:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📝 Total Scripts</h3>
                    <h1>{int(metrics['total_scripts'])}</h1>
                    <p>Average: {metrics.get('avg_scripts', 0):.1f} per person</p>
                </div>
                """, unsafe_allow_html=True)
        
        with cols[3]:
            if 'avg_productivity' in metrics:
                perf_level, perf_text = self.get_performance_badge(metrics['avg_productivity'])
                st.markdown(f"""
                <div class="metric-card">
                    <h3>⭐ Avg Productivity</h3>
                    <h1>{metrics['avg_productivity']:.1f}/5</h1>
                    <p>{perf_text}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Productivity distribution
        if 'performance_distribution' in metrics:
            st.markdown("### 📈 Team Performance Distribution")
            dist = metrics['performance_distribution']
            
            # Create donut chart for performance distribution
            labels = ['Excellent (4.5+)', 'Good (3.5-4.4)', 'Average (2.5-3.4)', 'Needs Focus (<2.5)']
            values = [dist['excellent'], dist['good'], dist['average'], dist['needs_improvement']]
            colors = ['#667eea', '#f093fb', '#ffecd2', '#ff9a9e']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values,
                hole=0.4,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_size=12
            )])
            
            fig.update_layout(
                title="Performance Score Distribution",
                height=400,
                showlegend=True,
                font=dict(family="Inter, sans-serif", size=12)
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def create_stunning_performance_chart(self, df, view_type="weekly"):
        """Create beautiful performance comparison charts"""
        if df.empty:
            st.warning("No data available for chart")
            return
        
        st.markdown('<div class="chart-spacing">', unsafe_allow_html=True)
        st.markdown("### 🚀 Individual Performance vs Team Average")
        
        # Group by Employee_ID to handle same names with different roles
        employee_performance = []
        
        for employee_id in df['Employee_ID'].unique():
            employee_data = df[df['Employee_ID'] == employee_id]
            role = employee_data['Role'].iloc[0]
            name = employee_data['Name'].iloc[0]
            
            performance_data = {
                'Employee_ID': employee_id,
                'Name': name,
                'Role': role,
                'Output': 0,
                'Productivity': 0
            }
            
            # Get role-specific output
            if role == 'Video Editor' and 'Videos Created' in df.columns:
                performance_data['Output'] = employee_data['Videos Created'].sum()
                performance_data['Output_Type'] = 'Videos'
            elif role == 'Designer' and 'Designs Created' in df.columns:
                performance_data['Output'] = employee_data['Designs Created'].sum()
                performance_data['Output_Type'] = 'Designs'
            elif role == 'Account Manager' and 'Scripts Produced' in df.columns:
                performance_data['Output'] = employee_data['Scripts Produced'].sum()
                performance_data['Output_Type'] = 'Scripts'
            elif role == 'Filmmaker' and 'Projects Worked' in df.columns:
                performance_data['Output'] = employee_data['Projects Worked'].sum()
                performance_data['Output_Type'] = 'Projects'
            else:
                performance_data['Output_Type'] = 'Tasks'
            
            # Get productivity score
            productivity_cols = [col for col in employee_data.columns if 'Productivity' in col]
            if productivity_cols:
                prod_scores = []
                for col in productivity_cols:
                    scores = pd.to_numeric(employee_data[col], errors='coerce').dropna()
                    prod_scores.extend(scores.tolist())
                if prod_scores:
                    performance_data['Productivity'] = np.mean(prod_scores)
            
            employee_performance.append(performance_data)
        
        perf_df = pd.DataFrame(employee_performance)
        
        if perf_df.empty:
            st.warning("No performance data available")
            return
        
        # Create subplot with better spacing
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=("📊 Work Output by Employee", "⭐ Productivity Scores"),
            vertical_spacing=0.15,  # Increased spacing
            specs=[[{"secondary_y": False}], [{"secondary_y": False}]]
        )
        
        # Sort by role for better visualization
        perf_df_sorted = perf_df.sort_values(['Role', 'Name'])
        
        # Create color map by role
        unique_roles = perf_df_sorted['Role'].unique()
        role_colors = {role: self.colors['primary'][i % len(self.colors['primary'])] 
                      for i, role in enumerate(unique_roles)}
        
        colors = [role_colors[role] for role in perf_df_sorted['Role']]
        
        # Output chart with better styling
        fig.add_trace(
            go.Bar(
                name='Work Output',
                x=perf_df_sorted['Employee_ID'],
                y=perf_df_sorted['Output'],
                marker_color=colors,
                text=perf_df_sorted['Output'],
                textposition='auto',
                textfont=dict(color='white', size=12),
                hovertemplate="<b>%{x}</b><br>Output: %{y}<br><extra></extra>",
                marker=dict(
                    line=dict(color='rgba(255,255,255,0.3)', width=1)
                )
            ),
            row=1, col=1
        )
        
        # Add average line for output
        avg_output = perf_df_sorted['Output'].mean()
        fig.add_hline(
            y=avg_output,
            line_dash="dash",
            line_color="rgba(255, 99, 71, 0.8)",
            line_width=2,
            annotation_text=f"Team Avg: {avg_output:.1f}",
            annotation_position="top right",
            row=1, col=1
        )
        
        # Productivity chart with enhanced colors
        productivity_colors = []
        for score in perf_df_sorted['Productivity']:
            if score >= 4.5:
                productivity_colors.append('#667eea')
            elif score >= 3.5:
                productivity_colors.append('#f093fb')
            elif score >= 2.5:
                productivity_colors.append('#4facfe')
            else:
                productivity_colors.append('#ff9a9e')
        
        fig.add_trace(
            go.Bar(
                name='Productivity Score',
                x=perf_df_sorted['Employee_ID'],
                y=perf_df_sorted['Productivity'],
                marker_color=productivity_colors,
                text=[f"{score:.1f}" for score in perf_df_sorted['Productivity']],
                textposition='auto',
                textfont=dict(color='white', size=12),
                hovertemplate="<b>%{x}</b><br>Productivity: %{y:.1f}/5<br><extra></extra>",
                marker=dict(
                    line=dict(color='rgba(255,255,255,0.3)', width=1)
                )
            ),
            row=2, col=1
        )
        
        # Add average line for productivity
        avg_productivity = perf_df_sorted['Productivity'].mean()
        fig.add_hline(
            y=avg_productivity,
            line_dash="dash",
            line_color="rgba(255, 99, 71, 0.8)",
            line_width=2,
            annotation_text=f"Team Avg: {avg_productivity:.1f}",
            annotation_position="top right",
            row=2, col=1
        )
        
        fig.update_layout(
            height=900,  # Increased height for better spacing
            showlegend=False,
            font=dict(family="Inter, sans-serif", size=12),
            title_text="Performance Analysis Dashboard",
            title_x=0.5,
            title_font=dict(size=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Update x-axis to show role info with better formatting
        fig.update_xaxes(
            tickangle=45, 
            row=1, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
        fig.update_xaxes(
            tickangle=45, 
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        )
        
        # Update y-axes with better styling
        fig.update_yaxes(
            row=1, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            title_font=dict(size=14)
        )
        fig.update_yaxes(
            row=2, col=1,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            title_font=dict(size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Performance insights
        self.display_performance_insights(perf_df)

    def display_performance_insights(self, perf_df):
        """Display AI-powered performance insights"""
        st.markdown("### 🔍 Performance Insights")
        
        # Top performers
        top_output = perf_df.nlargest(3, 'Output')
        top_productivity = perf_df.nlargest(3, 'Productivity')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Output Performers")
            for idx, performer in top_output.iterrows():
                st.markdown(f"""
                <div class="employee-card">
                    <h4>{performer['Name']} ({performer['Role']})</h4>
                    <p>📊 {performer['Output']} {performer.get('Output_Type', 'tasks')}</p>
                    <p>⭐ Productivity: {performer['Productivity']:.1f}/5</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### ⭐ Top Productivity Performers")
            for idx, performer in top_productivity.iterrows():
                perf_level, perf_text = self.get_performance_badge(performer['Productivity'])
                st.markdown(f"""
                <div class="employee-card">
                    <h4>{performer['Name']} ({performer['Role']})</h4>
                    <p>⭐ {performer['Productivity']:.1f}/5 - {perf_text}</p>
                    <p>📊 Output: {performer['Output']} {performer.get('Output_Type', 'tasks')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Performance correlations
        if len(perf_df) > 1:
            correlation = perf_df['Output'].corr(perf_df['Productivity'])
            
            st.markdown(f"""
            <div class="insight-box">
                <h4>📈 Output vs Productivity Correlation</h4>
                <p>Correlation coefficient: <strong>{correlation:.2f}</strong></p>
                <p>{'Strong positive correlation - Higher productivity leads to higher output!' if correlation > 0.7 
                   else 'Moderate correlation - Productivity and output are somewhat related.' if correlation > 0.3
                   else 'Weak correlation - Output and productivity scores vary independently.'}</p>
            </div>
            """, unsafe_allow_html=True)

    def create_role_comparison_chart(self, df):
        """Create beautiful role-based comparison chart"""
        st.markdown("### 📊 Performance by Role")
        
        role_stats = []
        for role in df['Role'].unique():
            role_data = df[df['Role'] == role]
            
            # Get productivity scores
            productivity_cols = [col for col in role_data.columns if 'Productivity' in col]
            productivity_scores = []
            
            for col in productivity_cols:
                scores = pd.to_numeric(role_data[col], errors='coerce').dropna()
                productivity_scores.extend(scores.tolist())
            
            if productivity_scores:
                role_stats.append({
                    'Role': role,
                    'Team_Size': len(role_data['Employee_ID'].unique()),
                    'Avg_Productivity': np.mean(productivity_scores),
                    'Productivity_Std': np.std(productivity_scores),
                    'Min_Productivity': np.min(productivity_scores),
                    'Max_Productivity': np.max(productivity_scores)
                })
        
        role_df = pd.DataFrame(role_stats)
        
        if not role_df.empty:
            # Create box plot for productivity distribution by role
            fig = go.Figure()
            
            colors = self.colors['primary'][:len(role_df)]
            
            for i, role in enumerate(role_df['Role']):
                role_data = df[df['Role'] == role]
                productivity_cols = [col for col in role_data.columns if 'Productivity' in col]
                all_scores = []
                
                for col in productivity_cols:
                    scores = pd.to_numeric(role_data[col], errors='coerce').dropna()
                    all_scores.extend(scores.tolist())
                
                fig.add_trace(go.Box(
                    y=all_scores,
                    name=role,
                    marker_color=colors[i % len(colors)],
                    boxmean='sd'
                ))
            
            fig.update_layout(
                title="Productivity Score Distribution by Role",
                yaxis_title="Productivity Score (1-5)",
                xaxis_title="Role",
                height=500,
                font=dict(family="Inter, sans-serif")
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Role summary table
            st.markdown("#### 📋 Role Performance Summary")
            display_df = role_df.copy()
            display_df['Avg_Productivity'] = display_df['Avg_Productivity'].round(2)
            display_df['Productivity_Std'] = display_df['Productivity_Std'].round(2)
            display_df.columns = ['Role', 'Team Size', 'Avg Productivity', 'Std Dev', 'Min Score', 'Max Score']
            st.dataframe(display_df, use_container_width=True)

    def enhanced_problems_analysis(self, df):
        """Enhanced problems and suggestions analysis with sentiment"""
        st.markdown("### 🔍 Issues & Improvement Analysis")
        
        # Collect all problems and suggestions
        problem_cols = [col for col in df.columns if 'Problems' in col]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚠️ Common Issues")
            all_problems = []
            problem_by_role = {}
            
            for col in problem_cols:
                problems = df[col].dropna().tolist()
                for i, problem in enumerate(problems):
                    if str(problem).strip() and str(problem).strip().lower() not in ['no', 'none', 'n/a']:
                        employee_role = df.iloc[i]['Role'] if i < len(df) else 'Unknown'
                        all_problems.append(str(problem))
                        
                        if employee_role not in problem_by_role:
                            problem_by_role[employee_role] = []
                        problem_by_role[employee_role].append(str(problem))
            
            if all_problems:
                # Count frequency
                problem_counter = Counter(all_problems)
                problem_df = pd.DataFrame(problem_counter.most_common(5), 
                                        columns=['Issue', 'Frequency'])
                
                # Create bar chart for common problems
                fig = px.bar(
                    problem_df, 
                    x='Frequency', 
                    y='Issue',
                    orientation='h',
                    color='Frequency',
                    color_continuous_scale=['#ff9a9e', '#667eea'],
                    title="Most Common Issues"
                )
                fig.update_layout(height=300, font=dict(family="Inter, sans-serif"))
                st.plotly_chart(fig, use_container_width=True)
                
                # Problems by role
                st.markdown("##### Issues by Role:")
                for role, problems in problem_by_role.items():
                    if problems:
                        unique_problems = list(set(problems))
                        st.markdown(f"**{role}:** {', '.join(unique_problems[:3])}")
            else:
                st.success("🎉 No significant issues reported!")
        
        with col2:
            st.markdown("#### 💡 Improvement Areas")
            
            # Analyze productivity scores to identify improvement areas
            low_performers = df[df.apply(lambda row: any(pd.to_numeric(row[col], errors='coerce') < 3 
                                                       for col in df.columns if 'Productivity' in col), axis=1)]
            
            if not low_performers.empty:
                improvement_areas = []
                for _, employee in low_performers.iterrows():
                    productivity_cols = [col for col in df.columns if 'Productivity' in col]
                    for col in productivity_cols:
                        score = pd.to_numeric(employee[col], errors='coerce')
                        if pd.notna(score) and score < 3:
                            improvement_areas.append({
                                'Employee': employee['Employee_ID'],
                                'Area': col.replace('Productivity', '').strip(),
                                'Score': score
                            })
                
                if improvement_areas:
                    imp_df = pd.DataFrame(improvement_areas)
                    
                    # Group by area
                    area_counts = imp_df['Area'].value_counts()
                    
                    fig = px.pie(
                        values=area_counts.values,
                        names=area_counts.index,
                        title="Areas Needing Focus",
                        color_discrete_sequence=self.colors['primary']
                    )
                    fig.update_layout(height=300, font=dict(family="Inter, sans-serif"))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.markdown("##### Focus Areas:")
                    for area, count in area_counts.head(3).items():
                        st.markdown(f"**{area}:** {count} team member(s) need support")
            else:
                st.success("🌟 All team members performing well!")

    def create_timeline_analysis(self, df):
        """Create timeline analysis for monthly data"""
        if 'Week Start Date' not in df.columns:
            return
        
        st.markdown("### 📅 Performance Timeline")
        
        # Group by week
        df['Week'] = df['Week Start Date'].dt.isocalendar().week
        
        # Calculate weekly metrics
        weekly_metrics = []
        for week in sorted(df['Week'].unique()):
            week_data = df[df['Week'] == week]
            
            metrics = {
                'Week': f"Week {week}",
                'Total_Output': 0,
                'Avg_Productivity': 0,
                'Team_Size': len(week_data['Employee_ID'].unique())
            }
            
            # Calculate total output
            output_cols = ['Videos Created', 'Designs Created', 'Scripts Produced', 'Projects Worked']
            for col in output_cols:
                if col in week_data.columns:
                    metrics['Total_Output'] += week_data[col].sum()
            
            # Calculate average productivity
            productivity_cols = [col for col in week_data.columns if 'Productivity' in col]
            all_productivity = []
            for col in productivity_cols:
                scores = pd.to_numeric(week_data[col], errors='coerce').dropna()
                all_productivity.extend(scores.tolist())
            
            if all_productivity:
                metrics['Avg_Productivity'] = np.mean(all_productivity)
            
            weekly_metrics.append(metrics)
        
        if len(weekly_metrics) > 1:
            weekly_df = pd.DataFrame(weekly_metrics)
            
            # Create dual-axis chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Total output
            fig.add_trace(
                go.Scatter(
                    x=weekly_df['Week'],
                    y=weekly_df['Total_Output'],
                    mode='lines+markers',
                    name='Total Output',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=False
            )
            
            # Average productivity
            fig.add_trace(
                go.Scatter(
                    x=weekly_df['Week'],
                    y=weekly_df['Avg_Productivity'],
                    mode='lines+markers',
                    name='Avg Productivity',
                    line=dict(color='#f093fb', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=True
            )
            
            fig.update_xaxes(title_text="Week")
            fig.update_yaxes(title_text="Total Output", secondary_y=False)
            fig.update_yaxes(title_text="Average Productivity Score", secondary_y=True)
            
            fig.update_layout(
                title="Weekly Performance Trends",
                height=400,
                font=dict(family="Inter, sans-serif"),
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekly insights
            best_week = weekly_df.loc[weekly_df['Total_Output'].idxmax()]
            st.markdown(f"""
            <div class="insight-box">
                <h4>📈 Weekly Performance Insight</h4>
                <p><strong>{best_week['Week']}</strong> was the most productive week with:</p>
                <ul>
                    <li>🎯 {best_week['Total_Output']} total outputs</li>
                    <li>⭐ {best_week['Avg_Productivity']:.1f} average productivity score</li>
                    <li>👥 {best_week['Team_Size']} active team members</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    def enhanced_individual_view(self, df, selected_employee_id):
        """Enhanced individual employee analysis"""
        employee_data = df[df['Employee_ID'] == selected_employee_id]
        if employee_data.empty:
            st.error("No data found for selected employee")
            return
        
        name = employee_data['Name'].iloc[0]
        role = employee_data['Role'].iloc[0]
        
        st.markdown(f'<h2 class="dashboard-header">👤 {name} - {role}</h2>', unsafe_allow_html=True)
        
        # Employee performance card
        individual_metrics = self.calculate_enhanced_metrics(employee_data, role)
        company_metrics = self.calculate_enhanced_metrics(df)
        
        # Get productivity score and badge
        if 'avg_productivity' in individual_metrics:
            perf_level, perf_text = self.get_performance_badge(individual_metrics['avg_productivity'])
            
            st.markdown(f"""
            <div class="role-header">
                <h3>{name}'s Performance Summary</h3>
                <p>Role: {role} | Productivity: {individual_metrics['avg_productivity']:.1f}/5 {perf_text}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance metrics comparison
        col1, col2, col3, col4 = st.columns(4)
        
        # Role-specific metrics
        if role == 'Video Editor' and 'avg_videos' in individual_metrics:
            with col1:
                delta = individual_metrics['avg_videos'] - company_metrics.get('avg_videos', 0)
                st.metric("Videos Created", f"{individual_metrics['total_videos']:.0f}", 
                         delta=f"{delta:+.1f} vs team avg")
        
        elif role == 'Designer' and 'avg_designs' in individual_metrics:
            with col1:
                delta = individual_metrics['avg_designs'] - company_metrics.get('avg_designs', 0)
                st.metric("Designs Created", f"{individual_metrics['total_designs']:.0f}",
                         delta=f"{delta:+.1f} vs team avg")
        
        elif role == 'Account Manager':
            if 'avg_scripts' in individual_metrics:
                with col1:
                    delta = individual_metrics['avg_scripts'] - company_metrics.get('avg_scripts', 0)
                    st.metric("Scripts Produced", f"{individual_metrics['total_scripts']:.0f}",
                             delta=f"{delta:+.1f} vs team avg")
            if 'avg_posts' in individual_metrics:
                with col2:
                    delta = individual_metrics['avg_posts'] - company_metrics.get('avg_posts', 0)
                    st.metric("Posts Published", f"{individual_metrics['total_posts']:.0f}",
                             delta=f"{delta:+.1f} vs team avg")
        
        elif role == 'Filmmaker' and 'avg_projects' in individual_metrics:
            with col1:
                delta = individual_metrics['avg_projects'] - company_metrics.get('avg_projects', 0)
                st.metric("Projects Worked", f"{individual_metrics['total_projects']:.0f}",
                         delta=f"{delta:+.1f} vs team avg")
        
        # Productivity comparison
        if 'avg_productivity' in individual_metrics:
            with col3:
                delta = individual_metrics['avg_productivity'] - company_metrics.get('avg_productivity', 0)
                st.metric("Productivity Score", f"{individual_metrics['avg_productivity']:.1f}/5",
                         delta=f"{delta:+.1f} vs team avg")
        
        # Performance radar chart
        self.create_individual_radar_chart(employee_data, df, name, role)
        
        # Weekly performance trend (if multiple weeks)
        if len(employee_data) > 1:
            self.create_individual_trend_chart(employee_data, name, role)
        
        # Individual feedback analysis with dark mode compatibility
        st.markdown("### 💬 Feedback & Comments")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="individual-feedback">
                <h4>⚠️ Issues Reported:</h4>
                <ul>
            """, unsafe_allow_html=True)
            
            problem_cols = [col for col in employee_data.columns if 'Problems' in col]
            problems_found = False
            for col in problem_cols:
                problems = employee_data[col].dropna().tolist()
                for problem in problems:
                    if str(problem).strip() and str(problem).strip().lower() not in ['no', 'none', 'n/a', '']:
                        st.markdown(f"<li>• {problem}</li>", unsafe_allow_html=True)
                        problems_found = True
            
            if not problems_found:
                st.markdown("<li>🎉 No issues reported!</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="individual-feedback">
                <h4>💭 Additional Comments:</h4>
                <ul>
            """, unsafe_allow_html=True)
            
            if 'Other Comments' in employee_data.columns:
                comments = employee_data['Other Comments'].dropna().tolist()
                comments_found = False
                for comment in comments:
                    if str(comment).strip() and str(comment).strip().lower() not in ['no', 'none', 'n/a', '']:
                        st.markdown(f"<li>• {comment}</li>", unsafe_allow_html=True)
                        comments_found = True
                
                if not comments_found:
                    st.markdown("<li>📝 No additional comments provided</li>", unsafe_allow_html=True)
            else:
                st.markdown("<li>📝 No additional comments provided</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)

    def create_individual_radar_chart(self, employee_data, company_data, name, role):
        """Create radar chart for individual performance"""
        st.markdown("### 🎯 Performance Radar")
        
        # Define categories based on role
        categories = []
        employee_scores = []
        company_averages = []
        
        if role == 'Video Editor':
            if 'Videos Created' in employee_data.columns:
                categories.append('Video Output')
                employee_scores.append(employee_data['Videos Created'].mean())
                company_averages.append(company_data[company_data['Role'] == role]['Videos Created'].mean())
        
        elif role == 'Designer':
            if 'Designs Created' in employee_data.columns:
                categories.append('Design Output')
                employee_scores.append(employee_data['Designs Created'].mean())
                company_averages.append(company_data[company_data['Role'] == role]['Designs Created'].mean())
        
        elif role == 'Account Manager':
            if 'Scripts Produced' in employee_data.columns:
                categories.append('Scripts')
                employee_scores.append(employee_data['Scripts Produced'].mean())
                company_averages.append(company_data[company_data['Role'] == role]['Scripts Produced'].mean())
            if 'Posts Published' in employee_data.columns:
                categories.append('Posts')
                employee_scores.append(employee_data['Posts Published'].mean())
                company_averages.append(company_data[company_data['Role'] == role]['Posts Published'].mean())
            if 'Client Meetings' in employee_data.columns:
                categories.append('Meetings')
                employee_scores.append(employee_data['Client Meetings'].mean())
                company_averages.append(company_data[company_data['Role'] == role]['Client Meetings'].mean())
        
        # Add productivity
        productivity_cols = [col for col in employee_data.columns if 'Productivity' in col]
        if productivity_cols:
            categories.append('Productivity')
            emp_prod = []
            comp_prod = []
            
            for col in productivity_cols:
                emp_scores = pd.to_numeric(employee_data[col], errors='coerce').dropna()
                comp_scores = pd.to_numeric(company_data[company_data['Role'] == role][col], errors='coerce').dropna()
                
                if not emp_scores.empty:
                    emp_prod.extend(emp_scores.tolist())
                if not comp_scores.empty:
                    comp_prod.extend(comp_scores.tolist())
            
            if emp_prod and comp_prod:
                employee_scores.append(np.mean(emp_prod))
                company_averages.append(np.mean(comp_prod))
        
        if len(categories) >= 3:  # Need at least 3 categories for radar chart
            # Normalize scores to 0-100 scale for better visualization
            max_scores = [max(emp, comp) for emp, comp in zip(employee_scores, company_averages)]
            
            employee_normalized = [(score / max_score * 100) if max_score > 0 else 0 
                                 for score, max_score in zip(employee_scores, max_scores)]
            company_normalized = [(score / max_score * 100) if max_score > 0 else 0 
                                for score, max_score in zip(company_averages, max_scores)]
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=employee_normalized + [employee_normalized[0]],  # Close the polygon
                theta=categories + [categories[0]],
                fill='toself',
                name=name,
                marker=dict(color='#667eea'),
                fillcolor='rgba(102, 126, 234, 0.3)'
            ))
            
            fig.add_trace(go.Scatterpolar(
                r=company_normalized + [company_normalized[0]],
                theta=categories + [categories[0]],
                fill='toself',
                name='Role Average',
                marker=dict(color='#f093fb'),
                fillcolor='rgba(240, 147, 251, 0.3)'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                height=400,
                font=dict(family="Inter, sans-serif")
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def create_individual_trend_chart(self, employee_data, name, role):
        """Create individual performance trend chart"""
        st.markdown("### 📈 Performance Trends")
        
        if 'Week Start Date' in employee_data.columns:
            employee_data_sorted = employee_data.sort_values('Week Start Date')
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Get role-specific output metric
            output_col = None
            if role == 'Video Editor' and 'Videos Created' in employee_data.columns:
                output_col = 'Videos Created'
            elif role == 'Designer' and 'Designs Created' in employee_data.columns:
                output_col = 'Designs Created'
            elif role == 'Account Manager' and 'Scripts Produced' in employee_data.columns:
                output_col = 'Scripts Produced'
            elif role == 'Filmmaker' and 'Projects Worked' in employee_data.columns:
                output_col = 'Projects Worked'
            
            if output_col:
                fig.add_trace(
                    go.Scatter(
                        x=employee_data_sorted['Week Start Date'],
                        y=employee_data_sorted[output_col],
                        mode='lines+markers',
                        name='Output',
                        line=dict(color='#667eea', width=3),
                        marker=dict(size=8)
                    ),
                    secondary_y=False
                )
            
            # Add productivity trend
            productivity_cols = [col for col in employee_data.columns if 'Productivity' in col]
            if productivity_cols:
                for col in productivity_cols:
                    productivity_scores = pd.to_numeric(employee_data_sorted[col], errors='coerce')
                    fig.add_trace(
                        go.Scatter(
                            x=employee_data_sorted['Week Start Date'],
                            y=productivity_scores,
                            mode='lines+markers',
                            name='Productivity',
                            line=dict(color='#f093fb', width=3),
                            marker=dict(size=8)
                        ),
                        secondary_y=True
                    )
            
            fig.update_xaxes(title_text="Week")
            if output_col:
                fig.update_yaxes(title_text="Output Count", secondary_y=False)
            fig.update_yaxes(title_text="Productivity Score", secondary_y=True)
            
            fig.update_layout(
                title=f"{name}'s Performance Over Time",
                height=400,
                font=dict(family="Inter, sans-serif")
            )
            
            st.plotly_chart(fig, use_container_width=True)

def main():
    st.markdown('<h1 class="dashboard-header">🚀 Advanced Performance Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    dashboard = EnhancedPerformanceDashboard()
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h2>📁 Data Management</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Weekly upload
        st.subheader("📅 Weekly Report")
        weekly_file = st.file_uploader("Upload Weekly CSV", type=['csv'], key="weekly")
        
        if weekly_file is not None:
            try:
                dashboard.weekly_data = dashboard.clean_data(pd.read_csv(weekly_file))
                st.success(f"✅ Weekly data loaded: {len(dashboard.weekly_data)} records")
                st.info(f"👥 {len(dashboard.weekly_data['Employee_ID'].unique())} unique employees found")
            except Exception as e:
                st.error(f"Error loading weekly data: {str(e)}")
        
        # Monthly upload
        st.subheader("📊 Monthly Analysis")
        st.markdown("Upload multiple weekly files:")
        
        monthly_files = []
        for i in range(1, 5):
            file = st.file_uploader(f"Week {i} CSV", type=['csv'], key=f"month_week_{i}")
            if file is not None:
                monthly_files.append(file)
        
        if len(monthly_files) >= 2:  # Allow partial monthly analysis
            try:
                monthly_dataframes = []
                for file in monthly_files:
                    df = dashboard.clean_data(pd.read_csv(file))
                    monthly_dataframes.append(df)
                
                dashboard.monthly_data = pd.concat(monthly_dataframes, ignore_index=True)
                st.success(f"✅ Monthly data loaded: {len(dashboard.monthly_data)} records from {len(monthly_files)} weeks")
                st.info(f"👥 {len(dashboard.monthly_data['Employee_ID'].unique())} unique employees found")
            except Exception as e:
                st.error(f"Error loading monthly data: {str(e)}")
        
        # Enhanced filters
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3>🔍 Smart Filters</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Role filter
        available_roles = []
        if dashboard.weekly_data is not None:
            available_roles.extend(dashboard.weekly_data['Role'].unique().tolist())
        if dashboard.monthly_data is not None:
            available_roles.extend(dashboard.monthly_data['Role'].unique().tolist())
        
        available_roles = list(set(available_roles))
        
        if available_roles:
            role_filter = st.selectbox("Filter by Role", ["All"] + available_roles)
        else:
            role_filter = "All"
        
        # Productivity filter
        productivity_filter = st.selectbox(
            "Filter by Performance Level",
            ["All", "Excellent (4.5+)", "Good (3.5-4.4)", "Average (2.5-3.4)", "Needs Focus (<2.5)"]
        )
    
    # Main content area
    if dashboard.weekly_data is None and dashboard.monthly_data is None:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    color: white; border-radius: 15px; margin: 2rem 0;">
            <h2>🚀 Welcome to Advanced Performance Analytics</h2>
            <p>Upload your CSV files to unlock powerful insights and beautiful visualizations!</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### ✨ Features:
        
        - **🎯 Smart Employee Identification**: Handles employees with same names but different roles
        - **📊 Beautiful Visualizations**: Modern charts with gradient colors and animations  
        - **🔍 Deep Analytics**: Productivity correlations, performance trends, and insights
        - **⚡ Real-time Filtering**: Filter by role, performance level, and more
        - **👤 Individual Profiles**: Detailed radar charts and personal analytics
        - **🏆 Performance Rankings**: Identify top performers and improvement areas
        """)
        return
    
    # Enhanced view selection with better styling
    view_tabs = st.tabs(["📅 Weekly Analytics", "📊 Monthly Insights", "👤 Individual Profiles", "🏆 Team Rankings"])
    
    with view_tabs[0]:  # Weekly View
        if dashboard.weekly_data is not None:
            df = dashboard.weekly_data.copy()
            
            # Apply filters
            if role_filter != "All":
                df = df[df['Role'] == role_filter]
            
            # Apply productivity filter
            if productivity_filter != "All":
                if productivity_filter == "Excellent (4.5+)":
                    df = df[df.apply(lambda row: any(pd.to_numeric(row[col], errors='coerce') >= 4.5 
                                                   for col in df.columns if 'Productivity' in col), axis=1)]
                elif productivity_filter == "Good (3.5-4.4)":
                    df = df[df.apply(lambda row: any(3.5 <= pd.to_numeric(row[col], errors='coerce') < 4.5 
                                                   for col in df.columns if 'Productivity' in col), axis=1)]
                elif productivity_filter == "Average (2.5-3.4)":
                    df = df[df.apply(lambda row: any(2.5 <= pd.to_numeric(row[col], errors='coerce') < 3.5 
                                                   for col in df.columns if 'Productivity' in col), axis=1)]
                elif productivity_filter == "Needs Focus (<2.5)":
                    df = df[df.apply(lambda row: any(pd.to_numeric(row[col], errors='coerce') < 2.5 
                                                   for col in df.columns if 'Productivity' in col), axis=1)]
            
            if not df.empty:
                # Enhanced KPI Cards
                metrics = dashboard.calculate_enhanced_metrics(df)
                dashboard.create_enhanced_kpi_cards(metrics, "Weekly")
                
                st.markdown("---")
                
                # Beautiful performance charts
                dashboard.create_stunning_performance_chart(df, "weekly")
                
                st.markdown("---")
                
                # Role comparison
                dashboard.create_role_comparison_chart(df)
                
                st.markdown("---")
                
                # Enhanced problems analysis
                dashboard.enhanced_problems_analysis(df)
                
            else:
                st.warning("🔍 No data matches your current filters. Try adjusting the filter settings.")
        else:
            st.info("📅 Please upload weekly CSV data to view weekly performance analytics")
    
    with view_tabs[1]:  # Monthly View
        if dashboard.monthly_data is not None:
            df = dashboard.monthly_data.copy()
            
            # Apply filters (same as weekly)
            if role_filter != "All":
                df = df[df['Role'] == role_filter]
            
            if not df.empty:
                # Monthly KPI Cards
                metrics = dashboard.calculate_enhanced_metrics(df)
                dashboard.create_enhanced_kpi_cards(metrics, "Monthly")
                
                st.markdown("---")
                
                # Timeline analysis
                dashboard.create_timeline_analysis(df)
                
                st.markdown("---")
                
                # Monthly performance chart
                dashboard.create_stunning_performance_chart(df, "monthly")
                
                st.markdown("---")
                
                # Role comparison for monthly data
                dashboard.create_role_comparison_chart(df)
                
                st.markdown("---")
                
                # Enhanced problems analysis
                dashboard.enhanced_problems_analysis(df)
                
            else:
                st.warning("🔍 No data matches your current filters for monthly analysis.")
        else:
            st.info("📊 Please upload multiple weekly CSV files to view monthly insights")
    
    with view_tabs[2]:  # Individual View
        # Employee selection
        available_employees = []
        display_data = dashboard.monthly_data if dashboard.monthly_data is not None else dashboard.weekly_data
        
        if display_data is not None:
            available_employees = sorted(display_data['Employee_ID'].unique())
        
        if available_employees:
            selected_employee = st.selectbox("🔍 Select Employee", available_employees)
            
            if selected_employee:
                dashboard.enhanced_individual_view(display_data, selected_employee)
        else:
            st.info("👤 Please upload data to view individual employee profiles")
    
    with view_tabs[3]:  # Team Rankings
        display_data = dashboard.monthly_data if dashboard.monthly_data is not None else dashboard.weekly_data
        
        if display_data is not None:
            st.markdown("### 🏆 Team Performance Rankings")
            
            # Calculate rankings
            employee_rankings = []
            
            for employee_id in display_data['Employee_ID'].unique():
                employee_data = display_data[display_data['Employee_ID'] == employee_id]
                role = employee_data['Role'].iloc[0]
                name = employee_data['Name'].iloc[0]
                
                # Calculate total output
                total_output = 0
                if role == 'Video Editor' and 'Videos Created' in employee_data.columns:
                    total_output = employee_data['Videos Created'].sum()
                elif role == 'Designer' and 'Designs Created' in employee_data.columns:
                    total_output = employee_data['Designs Created'].sum()
                elif role == 'Account Manager' and 'Scripts Produced' in employee_data.columns:
                    total_output = employee_data['Scripts Produced'].sum()
                elif role == 'Filmmaker' and 'Projects Worked' in employee_data.columns:
                    total_output = employee_data['Projects Worked'].sum()
                
                # Calculate average productivity
                productivity_cols = [col for col in employee_data.columns if 'Productivity' in col]
                avg_productivity = 0
                if productivity_cols:
                    all_scores = []
                    for col in productivity_cols:
                        scores = pd.to_numeric(employee_data[col], errors='coerce').dropna()
                        all_scores.extend(scores.tolist())
                    if all_scores:
                        avg_productivity = np.mean(all_scores)
                
                employee_rankings.append({
                    'Employee_ID': employee_id,
                    'Name': name,
                    'Role': role,
                    'Total_Output': total_output,
                    'Avg_Productivity': avg_productivity,
                    'Combined_Score': (total_output * 0.4) + (avg_productivity * 0.6 * 20)  # Weighted score
                })
            
            rankings_df = pd.DataFrame(employee_rankings)
            
            if not rankings_df.empty:
                # Sort by combined score
                rankings_df = rankings_df.sort_values('Combined_Score', ascending=False).reset_index(drop=True)
                rankings_df['Rank'] = range(1, len(rankings_df) + 1)
                
                # Create rankings visualization
                fig = px.bar(
                    rankings_df.head(10),  # Top 10 performers
                    x='Combined_Score',
                    y='Name',
                    color='Role',
                    orientation='h',
                    title="🏆 Top 10 Performers (Combined Score)",
                    color_discrete_sequence=dashboard.colors['primary'],
                    hover_data=['Total_Output', 'Avg_Productivity']
                )
                
                fig.update_layout(
                    height=600,
                    font=dict(family="Inter, sans-serif"),
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Rankings table with medals
                st.markdown("#### 🥇 Complete Rankings")
                
                display_rankings = rankings_df[['Rank', 'Name', 'Role', 'Total_Output', 'Avg_Productivity', 'Combined_Score']].copy()
                display_rankings['Avg_Productivity'] = display_rankings['Avg_Productivity'].round(2)
                display_rankings['Combined_Score'] = display_rankings['Combined_Score'].round(1)
                
                # Add medal emojis
                display_rankings['Medal'] = display_rankings['Rank'].apply(
                    lambda x: '🥇' if x == 1 else '🥈' if x == 2 else '🥉' if x == 3 else ''
                )
                
                # Reorder columns
                display_rankings = display_rankings[['Rank', 'Medal', 'Name', 'Role', 'Total_Output', 'Avg_Productivity', 'Combined_Score']]
                display_rankings.columns = ['Rank', 'Medal', 'Employee', 'Role', 'Total Output', 'Avg Productivity', 'Score']
                
                st.dataframe(
                    display_rankings,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Performance insights for rankings
                top_performer = rankings_df.iloc[0]
                avg_score = rankings_df['Combined_Score'].mean()
                
                st.markdown(f"""
                <div class="insight-box">
                    <h4>🌟 Top Performer Spotlight</h4>
                    <p><strong>{top_performer['Name']} ({top_performer['Role']})</strong> leads the team with:</p>
                    <ul>
                        <li>🎯 {top_performer['Total_Output']} total outputs</li>
                        <li>⭐ {top_performer['Avg_Productivity']:.1f}/5 productivity score</li>
                        <li>🏆 Combined score: {top_performer['Combined_Score']:.1f} (Team avg: {avg_score:.1f})</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Role-based rankings
                st.markdown("### 📊 Rankings by Role")
                
                for role in rankings_df['Role'].unique():
                    role_data = rankings_df[rankings_df['Role'] == role].head(3)
                    
                    if not role_data.empty:
                        st.markdown(f"#### {role} Top Performers")
                        
                        cols = st.columns(len(role_data))
                        
                        for i, (_, performer) in enumerate(role_data.iterrows()):
                            with cols[i]:
                                medal = '🥇' if i == 0 else '🥈' if i == 1 else '🥉'
                                st.markdown(f"""
                                <div class="employee-card">
                                    <h4>{medal} {performer['Name']}</h4>
                                    <p>📊 Output: {performer['Total_Output']}</p>
                                    <p>⭐ Productivity: {performer['Avg_Productivity']:.1f}/5</p>
                                    <p>🏆 Score: {performer['Combined_Score']:.1f}</p>
                                </div>
                                """, unsafe_allow_html=True)
            
            else:
                st.info("No ranking data available")
        else:
            st.info("🏆 Please upload data to view team rankings")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 10px; margin-top: 2rem;">
        <h4>📊 Advanced Performance Analytics Dashboard</h4>
        <p>Desidned and creation of Reda HEDDAD</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
