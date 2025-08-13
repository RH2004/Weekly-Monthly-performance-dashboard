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
st.set_page_config(
    page_title="Employee Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    .role-header {
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class PerformanceDashboard:
    def __init__(self):
        self.weekly_data = None
        self.monthly_data = None
        self.column_mapping = {
            # Basic info
            'Name': ['Name', 'name', 'Employee Name', 'employee_name'],
            'Role': ['Role', 'role', 'Position', 'position'],
            'Week Start Date': ['Week Start Date', 'week_start', 'start_date', 'Week Start'],
            'Week End Date': ['Week End Date', 'week_end', 'end_date', 'Week End'],
            
            # Video Editor
            'Videos Created': ['How many videos did you create this week?', 'videos_created', 'videos'],
            'Video Clients': ['Which clients did you work for this week? [Video Editor]', 'video_clients'],
            'Video Problems': ['Did you face any problems this week? [Video Editor]', 'video_problems'],
            'Video Productivity': ['Overall productivity this week [Video Editor]', 'video_productivity'],
            'Video Suggestions': ['Any suggestions for improvement? [Video Editor]', 'video_suggestions'],
            
            # Designer
            'Designs Created': ['How many designs did you create this week?', 'designs_created', 'designs'],
            'Design Types': ['What types of designs did you make?', 'design_types'],
            'Design Clients': ['Which clients did you work for this week? [Designer]', 'design_clients'],
            'Design Problems': ['Did you face any problems this week? [Designer]', 'design_problems'],
            'Design Productivity': ['Overall productivity this week [Designer]', 'design_productivity'],
            'Design Suggestions': ['Any suggestions for improvement? [Designer]', 'design_suggestions'],
            
            # Account Manager
            'Scripts Produced': ['How many scripts did you produce this week?', 'scripts_produced', 'scripts'],
            'Posts Published': ['How many posts were published this week?', 'posts_published', 'posts'],
            'Client Meetings': ['How many client meetings did you attend this week?', 'client_meetings', 'meetings'],
            'Meeting Takeaways': ['Main takeaway from this week\'s client meetings', 'meeting_takeaways'],
            'AM Problems': ['Did you face any problems this week? [Account Manager]', 'am_problems'],
            'AM Productivity': ['Overall productivity this week [Account Manager]', 'am_productivity'],
            'AM Suggestions': ['Any suggestions for improvement? [Account Manager]', 'am_suggestions'],
            
            # Filmmaker
            'Projects Worked': ['How many projects did you work on this week?', 'projects_worked', 'projects'],
            'Filmmaker Clients Count': ['How many clients did you work with this week?', 'filmmaker_clients_count'],
            'Filmmaker Clients': ['Who were the clients?', 'filmmaker_clients'],
            'Filmmaker Problems': ['Did you face any problems this week? [Filmmaker]', 'filmmaker_problems'],
            'Filmmaker Productivity': ['Overall productivity this week [Filmmaker]', 'filmmaker_productivity'],
            'Filmmaker Suggestions': ['Any suggestions for improvement? [Filmmaker]', 'filmmaker_suggestions'],
            
            # Team Leader
            'Leader Meetings': ['How many client meetings did you have this week?', 'leader_meetings'],
            'Week Review': ['Review of this week overall', 'week_review'],
            'Leader Problems': ['Did you face any problems this week? [Team Leader]', 'leader_problems'],
            'Leader Productivity': ['Overall productivity this week [Team Leader]', 'leader_productivity'],
            'Leader Suggestions': ['Any suggestions for improvement? [Team Leader]', 'leader_suggestions'],
            
            # Common
            'Other Comments': ['Any other comments?', 'other_comments', 'additional_comments']
        }

    def find_column(self, df, target_col):
        """Find the actual column name in the dataframe that matches our target"""
        if target_col in df.columns:
            return target_col
        
        possible_names = self.column_mapping.get(target_col, [target_col])
        for col in df.columns:
            for possible in possible_names:
                if possible.lower() in col.lower():
                    return col
        return None

    def clean_data(self, df):
        """Clean and standardize the dataframe"""
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
        
        # Fill missing values
        numeric_cols = ['Videos Created', 'Designs Created', 'Scripts Produced', 'Posts Published', 
                       'Client Meetings', 'Projects Worked', 'Filmmaker Clients Count', 'Leader Meetings']
        
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0)
        
        # Clean text columns
        text_cols = [col for col in df_clean.columns if col not in numeric_cols + ['Week Start Date', 'Week End Date']]
        for col in text_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna('').astype(str)
        
        # Parse dates
        date_cols = ['Week Start Date', 'Week End Date']
        for col in date_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        return df_clean

    def calculate_metrics(self, df, role=None):
        """Calculate performance metrics for given role or all roles"""
        if df.empty:
            return {}
        
        if role:
            df_role = df[df['Role'] == role]
        else:
            df_role = df
        
        metrics = {}
        
        # Video Editor metrics
        if role == 'Video Editor' or not role:
            if 'Videos Created' in df_role.columns:
                metrics['avg_videos'] = df_role['Videos Created'].mean()
                metrics['total_videos'] = df_role['Videos Created'].sum()
        
        # Designer metrics
        if role == 'Designer' or not role:
            if 'Designs Created' in df_role.columns:
                metrics['avg_designs'] = df_role['Designs Created'].mean()
                metrics['total_designs'] = df_role['Designs Created'].sum()
        
        # Account Manager metrics
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
        
        # Filmmaker metrics
        if role == 'Filmmaker' or not role:
            if 'Projects Worked' in df_role.columns:
                metrics['avg_projects'] = df_role['Projects Worked'].mean()
                metrics['total_projects'] = df_role['Projects Worked'].sum()
        
        # Productivity scores
        productivity_cols = [col for col in df_role.columns if 'Productivity' in col]
        if productivity_cols:
            all_productivity = []
            for col in productivity_cols:
                scores = pd.to_numeric(df_role[col], errors='coerce').dropna()
                all_productivity.extend(scores.tolist())
            if all_productivity:
                metrics['avg_productivity'] = np.mean(all_productivity)
        
        return metrics

    def create_wordcloud(self, text_data):
        """Create wordcloud from text data"""
        if not text_data or all(not str(x).strip() for x in text_data):
            return None
        
        # Combine all text
        combined_text = ' '.join([str(x) for x in text_data if str(x).strip()])
        
        # Remove common stop words and clean
        combined_text = re.sub(r'\b(the|and|or|but|in|on|at|to|for|of|with|by|from|up|about|into|through|during)\b', '', combined_text, flags=re.IGNORECASE)
        combined_text = re.sub(r'[^\w\s]', '', combined_text)
        
        if not combined_text.strip():
            return None
        
        try:
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis',
                max_words=50
            ).generate(combined_text)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            
            # Convert to base64 for display
            buf = BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode()
            plt.close()
            
            return img_str
        except:
            return None

    def display_kpi_cards(self, metrics, period="Weekly"):
        """Display KPI cards"""
        st.markdown(f"### 📊 {period} Company Overview")
        
        cols = st.columns(4)
        
        with cols[0]:
            if 'total_videos' in metrics:
                st.metric("Total Videos", int(metrics['total_videos']), 
                         delta=f"Avg: {metrics.get('avg_videos', 0):.1f}")
        
        with cols[1]:
            if 'total_designs' in metrics:
                st.metric("Total Designs", int(metrics['total_designs']), 
                         delta=f"Avg: {metrics.get('avg_designs', 0):.1f}")
        
        with cols[2]:
            if 'total_scripts' in metrics:
                st.metric("Total Scripts", int(metrics['total_scripts']), 
                         delta=f"Avg: {metrics.get('avg_scripts', 0):.1f}")
        
        with cols[3]:
            if 'avg_productivity' in metrics:
                st.metric("Avg Productivity", f"{metrics['avg_productivity']:.1f}/5", 
                         delta="Company Average")

    def create_performance_chart(self, df, view_type="weekly"):
        """Create performance comparison chart"""
        if df.empty:
            st.warning("No data available for chart")
            return
        
        # Calculate individual metrics vs company average
        roles = df['Role'].unique()
        
        fig = make_subplots(
            rows=len(roles), cols=1,
            subplot_titles=[f"{role} Performance" for role in roles],
            vertical_spacing=0.1
        )
        
        row = 1
        for role in roles:
            role_data = df[df['Role'] == role]
            
            # Get relevant metric column for this role
            if role == 'Video Editor' and 'Videos Created' in df.columns:
                metric_col = 'Videos Created'
                metric_name = 'Videos'
            elif role == 'Designer' and 'Designs Created' in df.columns:
                metric_col = 'Designs Created'
                metric_name = 'Designs'
            elif role == 'Account Manager' and 'Scripts Produced' in df.columns:
                metric_col = 'Scripts Produced'
                metric_name = 'Scripts'
            elif role == 'Filmmaker' and 'Projects Worked' in df.columns:
                metric_col = 'Projects Worked'
                metric_name = 'Projects'
            else:
                row += 1
                continue
            
            if metric_col in role_data.columns:
                individual_scores = role_data[metric_col].values
                names = role_data['Name'].values
                company_avg = df[metric_col].mean()
                
                fig.add_trace(
                    go.Bar(
                        name=f'Individual {metric_name}',
                        x=names,
                        y=individual_scores,
                        marker_color='lightblue'
                    ),
                    row=row, col=1
                )
                
                fig.add_hline(
                    y=company_avg,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Company Avg: {company_avg:.1f}",
                    row=row, col=1
                )
            
            row += 1
        
        fig.update_layout(height=300*len(roles), showlegend=True, title_text="Individual vs Company Performance")
        st.plotly_chart(fig, use_container_width=True)

    def display_problems_and_suggestions(self, df):
        """Display problems and suggestions analysis"""
        st.markdown("### 🔍 Problems & Suggestions Analysis")
        
        # Collect all problems and suggestions
        problem_cols = [col for col in df.columns if 'Problems' in col]
        suggestion_cols = [col for col in df.columns if 'Suggestions' in col]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Most Common Problems")
            all_problems = []
            for col in problem_cols:
                problems = df[col].dropna().tolist()
                all_problems.extend([str(p) for p in problems if str(p).strip()])
            
            if all_problems:
                # Count frequency
                problem_counter = Counter(all_problems)
                problem_df = pd.DataFrame(problem_counter.most_common(10), 
                                        columns=['Problem', 'Frequency'])
                st.dataframe(problem_df, use_container_width=True)
                
                # Word cloud for problems
                img_str = self.create_wordcloud(all_problems)
                if img_str:
                    st.markdown("##### Problems Word Cloud")
                    st.markdown(f'<img src="data:image/png;base64,{img_str}" width="100%">', unsafe_allow_html=True)
            else:
                st.info("No problems reported")
        
        with col2:
            st.markdown("#### Suggestions Summary")
            all_suggestions = []
            for col in suggestion_cols:
                suggestions = df[col].dropna().tolist()
                all_suggestions.extend([str(s) for s in suggestions if str(s).strip()])
            
            if all_suggestions:
                # Display recent suggestions
                st.markdown("##### Recent Suggestions:")
                for i, suggestion in enumerate(all_suggestions[-5:], 1):
                    st.markdown(f"**{i}.** {suggestion}")
                
                # Word cloud for suggestions
                img_str = self.create_wordcloud(all_suggestions)
                if img_str:
                    st.markdown("##### Suggestions Word Cloud")
                    st.markdown(f'<img src="data:image/png;base64,{img_str}" width="100%">', unsafe_allow_html=True)
            else:
                st.info("No suggestions provided")

    def display_individual_view(self, df, selected_employee):
        """Display individual employee performance"""
        employee_data = df[df['Name'] == selected_employee]
        if employee_data.empty:
            st.error("No data found for selected employee")
            return
        
        st.markdown(f"### 👤 {selected_employee} - Performance Overview")
        
        # Employee role and basic info
        role = employee_data['Role'].iloc[0]
        st.markdown(f'<div class="role-header"><h4>Role: {role}</h4></div>', unsafe_allow_html=True)
        
        # Individual metrics
        individual_metrics = self.calculate_metrics(employee_data, role)
        company_metrics = self.calculate_metrics(df)
        
        # Comparison metrics
        col1, col2, col3 = st.columns(3)
        
        if role == 'Video Editor' and 'avg_videos' in individual_metrics:
            with col1:
                st.metric("Videos Created", f"{individual_metrics['avg_videos']:.1f}", 
                         delta=f"{individual_metrics['avg_videos'] - company_metrics.get('avg_videos', 0):.1f} vs company avg")
        
        if role == 'Designer' and 'avg_designs' in individual_metrics:
            with col1:
                st.metric("Designs Created", f"{individual_metrics['avg_designs']:.1f}",
                         delta=f"{individual_metrics['avg_designs'] - company_metrics.get('avg_designs', 0):.1f} vs company avg")
        
        if 'avg_productivity' in individual_metrics:
            with col2:
                st.metric("Productivity Score", f"{individual_metrics['avg_productivity']:.1f}/5",
                         delta=f"{individual_metrics['avg_productivity'] - company_metrics.get('avg_productivity', 0):.1f} vs company avg")
        
        # Individual responses table
        st.markdown("#### 📋 Detailed Responses")
        
        # Select relevant columns for display
        display_cols = ['Week Start Date', 'Week End Date']
        
        # Add role-specific columns
        role_specific_cols = []
        if role == 'Video Editor':
            role_specific_cols = ['Videos Created', 'Video Clients', 'Video Problems', 'Video Productivity', 'Video Suggestions']
        elif role == 'Designer':
            role_specific_cols = ['Designs Created', 'Design Types', 'Design Clients', 'Design Problems', 'Design Productivity', 'Design Suggestions']
        elif role == 'Account Manager':
            role_specific_cols = ['Scripts Produced', 'Posts Published', 'Client Meetings', 'Meeting Takeaways', 'AM Problems', 'AM Productivity', 'AM Suggestions']
        elif role == 'Filmmaker':
            role_specific_cols = ['Projects Worked', 'Filmmaker Clients Count', 'Filmmaker Clients', 'Filmmaker Problems', 'Filmmaker Productivity', 'Filmmaker Suggestions']
        elif role == 'Team Leader':
            role_specific_cols = ['Leader Meetings', 'Week Review', 'Leader Problems', 'Leader Productivity', 'Leader Suggestions']
        
        display_cols.extend([col for col in role_specific_cols if col in employee_data.columns])
        display_cols.append('Other Comments')
        
        display_data = employee_data[display_cols].fillna('')
        st.dataframe(display_data, use_container_width=True)
        
        # Individual problems and suggestions
        st.markdown("#### 💡 Individual Feedback")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Problems Reported:**")
            problem_cols = [col for col in employee_data.columns if 'Problems' in col]
            for col in problem_cols:
                problems = employee_data[col].dropna().tolist()
                for problem in problems:
                    if str(problem).strip():
                        st.markdown(f"• {problem}")
        
        with col2:
            st.markdown("**Suggestions Made:**")
            suggestion_cols = [col for col in employee_data.columns if 'Suggestions' in col]
            for col in suggestion_cols:
                suggestions = employee_data[col].dropna().tolist()
                for suggestion in suggestions:
                    if str(suggestion).strip():
                        st.markdown(f"• {suggestion}")

def main():
    st.title("📊 Employee Weekly & Monthly Performance Dashboard")
    st.markdown("---")
    
    dashboard = PerformanceDashboard()
    
    # Sidebar for uploads and controls
    with st.sidebar:
        st.header("📁 Data Upload")
        
        # Weekly upload
        st.subheader("Weekly Report")
        weekly_file = st.file_uploader("Upload Weekly CSV", type=['csv'], key="weekly")
        
        if weekly_file is not None:
            try:
                dashboard.weekly_data = dashboard.clean_data(pd.read_csv(weekly_file))
                st.success(f"✅ Weekly data loaded: {len(dashboard.weekly_data)} records")
            except Exception as e:
                st.error(f"Error loading weekly data: {str(e)}")
        
        # Monthly upload
        st.subheader("Monthly Report")
        st.markdown("Upload 4 weekly CSV files for monthly analysis:")
        
        monthly_files = []
        for i in range(1, 5):
            file = st.file_uploader(f"Week {i} CSV", type=['csv'], key=f"month_week_{i}")
            if file is not None:
                monthly_files.append(file)
        
        if len(monthly_files) == 4:
            try:
                monthly_dataframes = []
                for file in monthly_files:
                    df = dashboard.clean_data(pd.read_csv(file))
                    monthly_dataframes.append(df)
                
                dashboard.monthly_data = pd.concat(monthly_dataframes, ignore_index=True)
                st.success(f"✅ Monthly data loaded: {len(dashboard.monthly_data)} records")
            except Exception as e:
                st.error(f"Error loading monthly data: {str(e)}")
        
        # Filters
        st.markdown("---")
        st.header("🔍 Filters")
        
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
    
    # Main content area
    if dashboard.weekly_data is None and dashboard.monthly_data is None:
        st.info("👆 Please upload CSV files to get started")
        st.markdown("""
        ### How to use this dashboard:
        
        1. **Weekly View**: Upload a single weekly CSV file
        2. **Monthly View**: Upload 4 weekly CSV files for comprehensive monthly analysis
        3. **Individual View**: Select an employee to see their detailed performance
        
        The dashboard will automatically:
        - Calculate company-wide averages
        - Compare individual performance to company benchmarks
        - Analyze common problems and suggestions
        - Display interactive charts and visualizations
        """)
        return
    
    # View selection
    view_tabs = st.tabs(["📅 Weekly View", "📊 Monthly View", "👤 Individual View"])
    
    with view_tabs[0]:  # Weekly View
        if dashboard.weekly_data is not None:
            df = dashboard.weekly_data
            if role_filter != "All":
                df = df[df['Role'] == role_filter]
            
            if not df.empty:
                # KPI Cards
                metrics = dashboard.calculate_metrics(df)
                dashboard.display_kpi_cards(metrics, "Weekly")
                
                st.markdown("---")
                
                # Performance charts
                dashboard.create_performance_chart(df, "weekly")
                
                st.markdown("---")
                
                # Role breakdown table
                st.markdown("### 📋 Weekly Performance by Role")
                role_summary = df.groupby('Role').agg({
                    'Name': 'count',
                    'Videos Created': 'sum',
                    'Designs Created': 'sum',
                    'Scripts Produced': 'sum',
                    'Posts Published': 'sum',
                    'Projects Worked': 'sum'
                }).fillna(0)
                role_summary.columns = ['Team Members', 'Total Videos', 'Total Designs', 'Total Scripts', 'Total Posts', 'Total Projects']
                st.dataframe(role_summary, use_container_width=True)
                
                st.markdown("---")
                
                # Problems and suggestions
                dashboard.display_problems_and_suggestions(df)
                
            else:
                st.warning("No data available for the selected filters")
        else:
            st.info("Please upload weekly CSV data to view weekly performance")
    
    with view_tabs[1]:  # Monthly View
        if dashboard.monthly_data is not None:
            df = dashboard.monthly_data
            if role_filter != "All":
                df = df[df['Role'] == role_filter]
            
            if not df.empty:
                # Monthly KPI Cards
                metrics = dashboard.calculate_metrics(df)
                dashboard.display_kpi_cards(metrics, "Monthly")
                
                st.markdown("---")
                
                # Monthly trend analysis
                st.markdown("### 📈 Monthly Trends")
                
                # Create weekly aggregation for trend
                df['Week'] = df['Week Start Date'].dt.isocalendar().week
                weekly_trends = df.groupby('Week').agg({
                    'Videos Created': 'sum',
                    'Designs Created': 'sum',
                    'Scripts Produced': 'sum',
                    'Posts Published': 'sum',
                    'Projects Worked': 'sum'
                }).reset_index()
                
                # Trend chart
                fig = go.Figure()
                
                metrics_to_plot = [
                    ('Videos Created', 'blue'),
                    ('Designs Created', 'green'),
                    ('Scripts Produced', 'red'),
                    ('Posts Published', 'orange'),
                    ('Projects Worked', 'purple')
                ]
                
                for metric, color in metrics_to_plot:
                    if metric in weekly_trends.columns and weekly_trends[metric].sum() > 0:
                        fig.add_trace(go.Scatter(
                            x=weekly_trends['Week'],
                            y=weekly_trends[metric],
                            mode='lines+markers',
                            name=metric,
                            line=dict(color=color)
                        ))
                
                fig.update_layout(
                    title="Weekly Performance Trends",
                    xaxis_title="Week Number",
                    yaxis_title="Count",
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Monthly performance chart
                dashboard.create_performance_chart(df, "monthly")
                
                st.markdown("---")
                
                # Monthly problems and suggestions
                dashboard.display_problems_and_suggestions(df)
                
            else:
                st.warning("No data available for the selected filters")
        else:
            st.info("Please upload 4 weekly CSV files to view monthly analysis")
    
    with view_tabs[2]:  # Individual View
        # Employee selection
        available_employees = []
        if dashboard.weekly_data is not None:
            available_employees.extend(dashboard.weekly_data['Name'].unique().tolist())
        if dashboard.monthly_data is not None:
            available_employees.extend(dashboard.monthly_data['Name'].unique().tolist())
        
        available_employees = list(set(available_employees))
        
        if available_employees:
            selected_employee = st.selectbox("Select Employee", sorted(available_employees))
            
            # Use monthly data if available, otherwise weekly
            display_data = dashboard.monthly_data if dashboard.monthly_data is not None else dashboard.weekly_data
            
            if display_data is not None and selected_employee:
                dashboard.display_individual_view(display_data, selected_employee)
        else:
            st.info("Please upload data to view individual performance")

if __name__ == "__main__":
    main()