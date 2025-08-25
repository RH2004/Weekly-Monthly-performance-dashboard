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
    page_title="Continuous Performance Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced custom CSS
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

    .data-upload-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 10px 25px rgba(240, 147, 251, 0.1);
    }

    .file-counter {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        text-align: center;
        font-weight: 600;
    }

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

    .insight-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 6px 20px rgba(79, 172, 254, 0.2);
    }

    .employee-timeline-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(240, 147, 251, 0.2);
    }

    .data-management-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }

    .timeline-progress {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)


class ContinuousPerformanceDashboard:
    def __init__(self):
        # Initialize session state for storing all uploaded data
        if 'all_performance_data' not in st.session_state:
            st.session_state.all_performance_data = []
        if 'file_counter' not in st.session_state:
            st.session_state.file_counter = 0
        if 'employee_timeline' not in st.session_state:
            st.session_state.employee_timeline = {}

        # Enhanced color palette
        self.colors = {
            'primary': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
            'secondary': ['#a8edea', '#fed6e3', '#d299c2', '#fef9d7', '#eea2a2', '#bbc1bf'],
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
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(3)
                df_clean[col] = df_clean[col].clip(1, 5)

        # Clean text columns
        text_cols = [col for col in df_clean.columns if
                     col not in numeric_cols + productivity_cols + ['Week Start Date', 'Week End Date']]
        for col in text_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna('').astype(str)

        # Parse dates
        date_cols = ['Week Start Date', 'Week End Date']
        for col in date_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')

        # Add file upload timestamp
        df_clean['Upload_Timestamp'] = datetime.now()
        df_clean['File_Order'] = st.session_state.file_counter + 1

        return df_clean

    def add_data_to_timeline(self, new_data):
        """Add new data to the continuous timeline"""
        if not new_data.empty:
            # Increment file counter
            st.session_state.file_counter += 1

            # Add to all performance data
            st.session_state.all_performance_data.append({
                'data': new_data,
                'upload_time': datetime.now(),
                'file_order': st.session_state.file_counter
            })

            # Update employee timeline
            for _, row in new_data.iterrows():
                employee_id = row['Employee_ID']

                if employee_id not in st.session_state.employee_timeline:
                    st.session_state.employee_timeline[employee_id] = {
                        'name': row['Name'],
                        'role': row['Role'],
                        'history': []
                    }

                # Add this week's data to employee history
                week_data = {
                    'week_start': row.get('Week Start Date'),
                    'week_end': row.get('Week End Date'),
                    'file_order': st.session_state.file_counter,
                    'upload_time': datetime.now(),
                    'data': row.to_dict()
                }

                st.session_state.employee_timeline[employee_id]['history'].append(week_data)

    def get_consolidated_data(self):
        """Get all uploaded data consolidated into a single DataFrame"""
        if not st.session_state.all_performance_data:
            return pd.DataFrame()

        all_dfs = [item['data'] for item in st.session_state.all_performance_data]
        consolidated_df = pd.concat(all_dfs, ignore_index=True)

        return consolidated_df

    def get_employee_historical_data(self, employee_id):
        """Get historical data for a specific employee"""
        if employee_id not in st.session_state.employee_timeline:
            return pd.DataFrame()

        history = st.session_state.employee_timeline[employee_id]['history']

        if not history:
            return pd.DataFrame()

        # Convert history to DataFrame
        history_data = []
        for week in history:
            week_dict = week['data'].copy()
            week_dict['File_Order'] = week['file_order']
            week_dict['Upload_Time'] = week['upload_time']
            history_data.append(week_dict)

        return pd.DataFrame(history_data)

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

    def create_data_management_section(self):
        """Create the data management section in sidebar"""
        st.markdown("""
        <div class="data-management-header">
            <h2>📁 Continuous Data Tracking</h2>
        </div>
        """, unsafe_allow_html=True)

        # File upload counter
        st.markdown(f"""
        <div class="file-counter">
            📈 Files Uploaded: {st.session_state.file_counter}
        </div>
        """, unsafe_allow_html=True)

        # Upload new CSV
        st.subheader("📤 Add New Performance Data")
        new_file = st.file_uploader(
            "Upload New CSV Report",
            type=['csv'],
            key=f"new_upload_{st.session_state.file_counter}",
            help="Upload weekly performance reports to build a comprehensive timeline"
        )

        if new_file is not None:
            try:
                new_data = self.clean_data(pd.read_csv(new_file))
                if not new_data.empty:
                    self.add_data_to_timeline(new_data)
                    st.success(
                        f"✅ New data added: {len(new_data)} records from {len(new_data['Employee_ID'].unique())} employees")
                    st.rerun()
                else:
                    st.error("❌ No valid data found in the uploaded file")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

        # Data summary
        if st.session_state.all_performance_data:
            consolidated_df = self.get_consolidated_data()

            st.markdown("### 📊 Data Summary")
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Total Records", len(consolidated_df))
                st.metric("Unique Employees", len(consolidated_df['Employee_ID'].unique()))

            with col2:
                st.metric("Data Points", f"{len(st.session_state.all_performance_data)} reports")
                if 'Week Start Date' in consolidated_df.columns:
                    date_range = consolidated_df['Week Start Date'].max() - consolidated_df['Week Start Date'].min()
                    st.metric("Time Span", f"{date_range.days} days")

        # Timeline progress
        if st.session_state.employee_timeline:
            st.markdown("### 👥 Employee Tracking")
            for employee_id, timeline in st.session_state.employee_timeline.items():
                weeks_tracked = len(timeline['history'])
                st.markdown(f"""
                <div class="timeline-progress">
                    <strong>{timeline['name']} ({timeline['role']})</strong>
                    <br>📅 {weeks_tracked} report(s) tracked
                </div>
                """, unsafe_allow_html=True)

        # Clear data option
        st.markdown("---")
        if st.button("🗑️ Clear All Data", help="Remove all uploaded data and start fresh"):
            st.session_state.all_performance_data = []
            st.session_state.file_counter = 0
            st.session_state.employee_timeline = {}
            st.success("All data cleared!")
            st.rerun()

    def create_comprehensive_timeline_view(self):
        """Create a comprehensive timeline view of all data"""
        consolidated_df = self.get_consolidated_data()

        if consolidated_df.empty:
            st.info("📈 Upload performance reports to see timeline analysis")
            return

        st.markdown("### 📅 Comprehensive Performance Timeline")

        # Timeline metrics by file upload
        timeline_metrics = []
        for i, data_item in enumerate(st.session_state.all_performance_data):
            df = data_item['data']
            metrics = {
                'File_Order': data_item['file_order'],
                'Upload_Date': data_item['upload_time'].strftime('%Y-%m-%d %H:%M'),
                'Records': len(df),
                'Employees': len(df['Employee_ID'].unique()),
                'Total_Output': 0,
                'Avg_Productivity': 0
            }

            # Calculate total output
            output_cols = ['Videos Created', 'Designs Created', 'Scripts Produced', 'Projects Worked']
            for col in output_cols:
                if col in df.columns:
                    metrics['Total_Output'] += df[col].sum()

            # Calculate average productivity
            productivity_cols = [col for col in df.columns if 'Productivity' in col]
            all_productivity = []
            for col in productivity_cols:
                scores = pd.to_numeric(df[col], errors='coerce').dropna()
                all_productivity.extend(scores.tolist())

            if all_productivity:
                metrics['Avg_Productivity'] = np.mean(all_productivity)

            timeline_metrics.append(metrics)

        timeline_df = pd.DataFrame(timeline_metrics)

        # Create timeline visualization
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("📊 Total Output Over Time", "⭐ Average Productivity Over Time", "👥 Team Size Over Time"),
            vertical_spacing=0.1
        )

        # Output timeline
        fig.add_trace(
            go.Scatter(
                x=timeline_df['File_Order'],
                y=timeline_df['Total_Output'],
                mode='lines+markers',
                name='Total Output',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10),
                hovertemplate="Report: %{x}<br>Output: %{y}<br>Date: %{customdata}<extra></extra>",
                customdata=timeline_df['Upload_Date']
            ),
            row=1, col=1
        )

        # Productivity timeline
        fig.add_trace(
            go.Scatter(
                x=timeline_df['File_Order'],
                y=timeline_df['Avg_Productivity'],
                mode='lines+markers',
                name='Avg Productivity',
                line=dict(color='#f093fb', width=3),
                marker=dict(size=10),
                hovertemplate="Report: %{x}<br>Productivity: %{y:.1f}<br>Date: %{customdata}<extra></extra>",
                customdata=timeline_df['Upload_Date']
            ),
            row=2, col=1
        )

        # Team size timeline
        fig.add_trace(
            go.Scatter(
                x=timeline_df['File_Order'],
                y=timeline_df['Employees'],
                mode='lines+markers',
                name='Team Size',
                line=dict(color='#4facfe', width=3),
                marker=dict(size=10),
                hovertemplate="Report: %{x}<br>Team Size: %{y}<br>Date: %{customdata}<extra></extra>",
                customdata=timeline_df['Upload_Date']
            ),
            row=3, col=1
        )

        fig.update_layout(
            height=800,
            showlegend=False,
            font=dict(family="Inter, sans-serif"),
            title_text="Performance Timeline Analysis",
            title_x=0.5
        )

        fig.update_xaxes(title_text="Report Number", row=3, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Timeline insights
        if len(timeline_df) > 1:
            latest_output = timeline_df.iloc[-1]['Total_Output']
            previous_output = timeline_df.iloc[-2]['Total_Output']
            output_change = ((latest_output - previous_output) / previous_output * 100) if previous_output > 0 else 0

            latest_productivity = timeline_df.iloc[-1]['Avg_Productivity']
            previous_productivity = timeline_df.iloc[-2]['Avg_Productivity']
            productivity_change = ((
                                               latest_productivity - previous_productivity) / previous_productivity * 100) if previous_productivity > 0 else 0

            st.markdown(f"""
            <div class="insight-box">
                <h4>📈 Latest Performance Trends</h4>
                <p><strong>Output Change:</strong> {output_change:+.1f}% from previous report</p>
                <p><strong>Productivity Change:</strong> {productivity_change:+.1f}% from previous report</p>
                <p><strong>Team Growth:</strong> {timeline_df.iloc[-1]['Employees']} active employees</p>
            </div>
            """, unsafe_allow_html=True)

    def create_enhanced_individual_timeline(self, employee_id):
        """Create detailed individual employee timeline with trends"""
        employee_data = self.get_employee_historical_data(employee_id)

        if employee_data.empty:
            st.warning("No historical data available for this employee")
            return

        employee_info = st.session_state.employee_timeline[employee_id]
        name = employee_info['name']
        role = employee_info['role']

        st.markdown(f'<h2 class="dashboard-header">📈 {name}\'s Performance Journey</h2>', unsafe_allow_html=True)

        # Employee timeline summary
        st.markdown(f"""
        <div class="employee-timeline-card">
            <h3>{name} - {role}</h3>
            <p>📅 {len(employee_data)} reports tracked | 🕐 First report: {employee_data['Upload_Time'].min().strftime('%Y-%m-%d')}</p>
        </div>
        """, unsafe_allow_html=True)

        # Performance trends over time
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f"📊 {name}'s Output Trends", f"⭐ {name}'s Productivity Trends"),
            vertical_spacing=0.15
        )

        # Determine output column based on role
        output_col = None
        output_label = "Output"

        if role == 'Video Editor' and 'Videos Created' in employee_data.columns:
            output_col = 'Videos Created'
            output_label = 'Videos'
        elif role == 'Designer' and 'Designs Created' in employee_data.columns:
            output_col = 'Designs Created'
            output_label = 'Designs'
        elif role == 'Account Manager' and 'Scripts Produced' in employee_data.columns:
            output_col = 'Scripts Produced'
            output_label = 'Scripts'
        elif role == 'Filmmaker' and 'Projects Worked' in employee_data.columns:
            output_col = 'Projects Worked'
            output_label = 'Projects'

        # Plot output trends
        if output_col and output_col in employee_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=employee_data['File_Order'],
                    y=employee_data[output_col],
                    mode='lines+markers',
                    name=f'{output_label} Created',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=10),
                    hovertemplate=f"Report: %{{x}}<br>{output_label}: %{{y}}<extra></extra>"
                ),
                row=1, col=1
            )

            # Add trend line
            if len(employee_data) > 2:
                z = np.polyfit(employee_data['File_Order'], employee_data[output_col], 1)
                p = np.poly1d(z)
                fig.add_trace(
                    go.Scatter(
                        x=employee_data['File_Order'],
                        y=p(employee_data['File_Order']),
                        mode='lines',
                        name='Trend',
                        line=dict(color='rgba(102, 126, 234, 0.5)', width=2, dash='dash'),
                        hoverinfo='skip'
                    ),
                    row=1, col=1
                )

        # Plot productivity trends
        productivity_cols = [col for col in employee_data.columns if 'Productivity' in col]
        if productivity_cols:
            for i, col in enumerate(productivity_cols):
                productivity_scores = pd.to_numeric(employee_data[col], errors='coerce')

                fig.add_trace(
                    go.Scatter(
                        x=employee_data['File_Order'],
                        y=productivity_scores,
                        mode='lines+markers',
                        name=col.replace('Productivity', '').strip() or 'Productivity',
                        line=dict(color=self.colors['primary'][i % len(self.colors['primary'])], width=3),
                        marker=dict(size=10),
                        hovertemplate="Report: %{x}<br>Score: %{y:.1f}<extra></extra>"
                    ),
                    row=2, col=1
                )

        fig.update_layout(
            height=700,
            font=dict(family="Inter, sans-serif"),
            title_text=f"{name}'s Performance Timeline",
            title_x=0.5
        )

        fig.update_xaxes(title_text="Report Number", row=1, col=1)
        fig.update_xaxes(title_text="Report Number", row=2, col=1)
        fig.update_yaxes(title_text=output_label, row=1, col=1)
        fig.update_yaxes(title_text="Productivity Score", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

        # Performance statistics
        col1, col2, col3, col4 = st.columns(4)

        # Calculate statistics
        if output_col and output_col in employee_data.columns:
            avg_output = employee_data[output_col].mean()
            max_output = employee_data[output_col].max()

            with col1:
                st.metric(f"Avg {output_label}", f"{avg_output:.1f}")
            with col2:
                st.metric(f"Best Week", f"{max_output}")

        if productivity_cols:
            all_productivity = []
            for col in productivity_cols:
                scores = pd.to_numeric(employee_data[col], errors='coerce').dropna()
                all_productivity.extend(scores.tolist())

            if all_productivity:
                avg_productivity = np.mean(all_productivity)
                max_productivity = np.max(all_productivity)

                with col3:
                    st.metric("Avg Productivity", f"{avg_productivity:.1f}/5")
                with col4:
                    perf_level, perf_text = self.get_performance_badge(avg_productivity)
                    st.metric("Performance Level", perf_text)

        # Improvement trends
        if len(employee_data) > 1:
            st.markdown("### 📊 Performance Analysis")

            col1, col2 = st.columns(2)

            with col1:
                # Output improvement
                if output_col and output_col in employee_data.columns:
                    first_output = employee_data[output_col].iloc[0]
                    last_output = employee_data[output_col].iloc[-1]
                    output_improvement = ((last_output - first_output) / first_output * 100) if first_output > 0 else 0

                    st.markdown(f"""
                    <div class="insight-box">
                        <h4>📈 Output Improvement</h4>
                        <p><strong>{output_improvement:+.1f}%</strong> change from first to latest report</p>
                        <p>From {first_output} to {last_output} {output_label.lower()}</p>
                    </div>
                    """, unsafe_allow_html=True)

            with col2:
                # Productivity improvement
                if productivity_cols:
                    first_productivity = []
                    last_productivity = []

                    for col in productivity_cols:
                        first_score = pd.to_numeric(employee_data[col].iloc[0], errors='coerce')
                        last_score = pd.to_numeric(employee_data[col].iloc[-1], errors='coerce')

                        if pd.notna(first_score) and pd.notna(last_score):
                            first_productivity.append(first_score)
                            last_productivity.append(last_score)

                    if first_productivity and last_productivity:
                        first_avg = np.mean(first_productivity)
                        last_avg = np.mean(last_productivity)
                        productivity_improvement = ((last_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0

                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>⭐ Productivity Growth</h4>
                            <p><strong>{productivity_improvement:+.1f}%</strong> change in productivity</p>
                            <p>From {first_avg:.1f} to {last_avg:.1f} average score</p>
                        </div>
                        """, unsafe_allow_html=True)

        # Historical issues and comments
        st.markdown("### 💬 Historical Feedback")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ⚠️ Issues Timeline")
            problem_cols = [col for col in employee_data.columns if 'Problems' in col]

            issues_timeline = []
            for idx, row in employee_data.iterrows():
                for col in problem_cols:
                    if pd.notna(row[col]) and str(row[col]).strip() and str(row[col]).strip().lower() not in ['no',
                                                                                                              'none',
                                                                                                              'n/a',
                                                                                                              '']:
                        issues_timeline.append({
                            'Report': row['File_Order'],
                            'Issue': str(row[col]),
                            'Date': row['Upload_Time'].strftime('%Y-%m-%d')
                        })

            if issues_timeline:
                for issue in issues_timeline[-5:]:  # Show last 5 issues
                    st.markdown(f"**Report {issue['Report']}** ({issue['Date']}): {issue['Issue']}")
            else:
                st.success("🎉 No significant issues reported!")

        with col2:
            st.markdown("#### 💭 Comments Timeline")

            if 'Other Comments' in employee_data.columns:
                comments_timeline = []
                for idx, row in employee_data.iterrows():
                    if pd.notna(row['Other Comments']) and str(row['Other Comments']).strip() and str(
                            row['Other Comments']).strip().lower() not in ['no', 'none', 'n/a', '']:
                        comments_timeline.append({
                            'Report': row['File_Order'],
                            'Comment': str(row['Other Comments']),
                            'Date': row['Upload_Time'].strftime('%Y-%m-%d')
                        })

                if comments_timeline:
                    for comment in comments_timeline[-5:]:  # Show last 5 comments
                        st.markdown(f"**Report {comment['Report']}** ({comment['Date']}): {comment['Comment']}")
                else:
                    st.info("📝 No additional comments provided")
            else:
                st.info("📝 No additional comments provided")

    def create_enhanced_kpi_cards(self, metrics, period="All Time"):
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
                    <p>Average: {metrics.get('avg_videos', 0):.1f} per report</p>
                </div>
                """, unsafe_allow_html=True)

        with cols[1]:
            if 'total_designs' in metrics:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🎨 Total Designs</h3>
                    <h1>{int(metrics['total_designs'])}</h1>
                    <p>Average: {metrics.get('avg_designs', 0):.1f} per report</p>
                </div>
                """, unsafe_allow_html=True)

        with cols[2]:
            if 'total_scripts' in metrics:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📝 Total Scripts</h3>
                    <h1>{int(metrics['total_scripts'])}</h1>
                    <p>Average: {metrics.get('avg_scripts', 0):.1f} per report</p>
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

    def create_employee_comparison_heatmap(self):
        """Create a heatmap showing employee performance across all reports"""
        consolidated_df = self.get_consolidated_data()

        if consolidated_df.empty:
            return

        st.markdown("### 🔥 Employee Performance Heatmap")

        # Create performance matrix
        performance_matrix = []

        for employee_id in consolidated_df['Employee_ID'].unique():
            employee_data = consolidated_df[consolidated_df['Employee_ID'] == employee_id]
            employee_performance = []

            # Get performance for each report
            for file_order in sorted(consolidated_df['File_Order'].unique()):
                file_data = employee_data[employee_data['File_Order'] == file_order]

                if not file_data.empty:
                    # Calculate average productivity for this report
                    productivity_cols = [col for col in file_data.columns if 'Productivity' in col]
                    avg_productivity = 0

                    if productivity_cols:
                        all_scores = []
                        for col in productivity_cols:
                            scores = pd.to_numeric(file_data[col], errors='coerce').dropna()
                            all_scores.extend(scores.tolist())

                        if all_scores:
                            avg_productivity = np.mean(all_scores)

                    employee_performance.append(avg_productivity)
                else:
                    employee_performance.append(0)  # No data for this report

            performance_matrix.append({
                'Employee': employee_id,
                'Performance': employee_performance
            })

        # Create heatmap data
        if performance_matrix:
            employee_names = [item['Employee'] for item in performance_matrix]
            performance_data = [item['Performance'] for item in performance_matrix]
            file_orders = sorted(consolidated_df['File_Order'].unique())

            # Pad performance data to same length
            max_reports = len(file_orders)
            for i, perf in enumerate(performance_data):
                while len(perf) < max_reports:
                    perf.append(0)

            fig = go.Figure(data=go.Heatmap(
                z=performance_data,
                x=[f'Report {i}' for i in file_orders],
                y=employee_names,
                colorscale='RdYlBu_r',
                zmid=3,  # Middle value for color scale
                zmin=1,
                zmax=5,
                colorbar=dict(title="Productivity Score"),
                hoverongaps=False,
                hovertemplate="Employee: %{y}<br>Report: %{x}<br>Score: %{z:.1f}<extra></extra>"
            ))

            fig.update_layout(
                title="Employee Productivity Heatmap Across All Reports",
                height=max(400, len(employee_names) * 30),
                font=dict(family="Inter, sans-serif")
            )

            st.plotly_chart(fig, use_container_width=True)

    def create_long_term_rankings(self):
        """Create comprehensive long-term performance rankings"""
        consolidated_df = self.get_consolidated_data()

        if consolidated_df.empty:
            st.info("Upload performance data to view long-term rankings")
            return

        st.markdown("### 🏆 Long-term Performance Rankings")
        st.markdown("*Based on all uploaded reports*")

        # Calculate comprehensive rankings
        employee_rankings = []

        for employee_id in consolidated_df['Employee_ID'].unique():
            employee_data = consolidated_df[consolidated_df['Employee_ID'] == employee_id]
            employee_info = st.session_state.employee_timeline[employee_id]

            # Calculate metrics
            total_reports = len(employee_data)

            # Total output
            total_output = 0
            role = employee_info['role']

            if role == 'Video Editor' and 'Videos Created' in employee_data.columns:
                total_output = employee_data['Videos Created'].sum()
            elif role == 'Designer' and 'Designs Created' in employee_data.columns:
                total_output = employee_data['Designs Created'].sum()
            elif role == 'Account Manager' and 'Scripts Produced' in employee_data.columns:
                total_output = employee_data['Scripts Produced'].sum()
            elif role == 'Filmmaker' and 'Projects Worked' in employee_data.columns:
                total_output = employee_data['Projects Worked'].sum()

            # Average productivity
            productivity_cols = [col for col in employee_data.columns if 'Productivity' in col]
            avg_productivity = 0
            productivity_consistency = 0

            if productivity_cols:
                all_scores = []
                for col in productivity_cols:
                    scores = pd.to_numeric(employee_data[col], errors='coerce').dropna()
                    all_scores.extend(scores.tolist())

                if all_scores:
                    avg_productivity = np.mean(all_scores)
                    productivity_consistency = 1 / (np.std(all_scores) + 0.1)  # Higher = more consistent

            # Improvement trend (if multiple reports)
            improvement_score = 0
            if total_reports > 1 and productivity_cols:
                first_productivity = []
                last_productivity = []

                first_report = employee_data[employee_data['File_Order'] == employee_data['File_Order'].min()]
                last_report = employee_data[employee_data['File_Order'] == employee_data['File_Order'].max()]

                for col in productivity_cols:
                    if col in first_report.columns and col in last_report.columns:
                        first_score = pd.to_numeric(first_report[col].iloc[0], errors='coerce')
                        last_score = pd.to_numeric(last_report[col].iloc[0], errors='coerce')

                        if pd.notna(first_score) and pd.notna(last_score):
                            first_productivity.append(first_score)
                            last_productivity.append(last_score)

                if first_productivity and last_productivity:
                    first_avg = np.mean(first_productivity)
                    last_avg = np.mean(last_productivity)
                    improvement_score = (last_avg - first_avg) * 10  # Scale for ranking

            # Comprehensive score
            comprehensive_score = (
                    (total_output * 0.3) +
                    (avg_productivity * 20 * 0.4) +
                    (productivity_consistency * 10 * 0.2) +
                    (improvement_score * 0.1)
            )

            employee_rankings.append({
                'Employee_ID': employee_id,
                'Name': employee_info['name'],
                'Role': role,
                'Total_Reports': total_reports,
                'Total_Output': total_output,
                'Avg_Productivity': avg_productivity,
                'Consistency_Score': productivity_consistency,
                'Improvement_Score': improvement_score,
                'Comprehensive_Score': comprehensive_score
            })

        rankings_df = pd.DataFrame(employee_rankings)

        if not rankings_df.empty:
            rankings_df = rankings_df.sort_values('Comprehensive_Score', ascending=False).reset_index(drop=True)
            rankings_df['Rank'] = range(1, len(rankings_df) + 1)

            # Top performer spotlight
            top_performer = rankings_df.iloc[0]
            st.markdown(f"""
            <div class="insight-box">
                <h4>🌟 Long-term Top Performer</h4>
                <p><strong>{top_performer['Name']} ({top_performer['Role']})</strong></p>
                <ul>
                    <li>📊 {top_performer['Total_Output']} total outputs across {top_performer['Total_Reports']} reports</li>
                    <li>⭐ {top_performer['Avg_Productivity']:.1f}/5 average productivity</li>
                    <li>🎯 Comprehensive score: {top_performer['Comprehensive_Score']:.1f}</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            # Rankings visualization
            fig = px.bar(
                rankings_df.head(10),
                x='Comprehensive_Score',
                y='Name',
                color='Role',
                orientation='h',
                title="🏆 Top 10 Long-term Performers",
                color_discrete_sequence=self.colors['primary'],
                hover_data=['Total_Output', 'Avg_Productivity', 'Total_Reports']
            )

            fig.update_layout(
                height=600,
                font=dict(family="Inter, sans-serif"),
                yaxis={'categoryorder': 'total ascending'}
            )

            st.plotly_chart(fig, use_container_width=True)

            # Detailed rankings table
            st.markdown("#### 📊 Complete Long-term Rankings")

            display_rankings = rankings_df[['Rank', 'Name', 'Role', 'Total_Reports', 'Total_Output', 'Avg_Productivity',
                                            'Comprehensive_Score']].copy()
            display_rankings['Avg_Productivity'] = display_rankings['Avg_Productivity'].round(2)
            display_rankings['Comprehensive_Score'] = display_rankings['Comprehensive_Score'].round(1)

            # Add medals
            display_rankings['Medal'] = display_rankings['Rank'].apply(
                lambda x: '🥇' if x == 1 else '🥈' if x == 2 else '🥉' if x == 3 else ''
            )

            display_rankings = display_rankings[
                ['Rank', 'Medal', 'Name', 'Role', 'Total_Reports', 'Total_Output', 'Avg_Productivity',
                 'Comprehensive_Score']]
            display_rankings.columns = ['Rank', 'Medal', 'Employee', 'Role', 'Reports', 'Output', 'Avg Productivity',
                                        'Score']

            st.dataframe(display_rankings, use_container_width=True, hide_index=True)


def main():
    st.markdown('<h1 class="dashboard-header">🚀 Continuous Performance Analytics Dashboard</h1>',
                unsafe_allow_html=True)
    st.markdown("---")

    dashboard = ContinuousPerformanceDashboard()

    # Enhanced sidebar with continuous data management
    with st.sidebar:
        dashboard.create_data_management_section()

    # Get consolidated data
    consolidated_df = dashboard.get_consolidated_data()

    # Main content area
    if consolidated_df.empty:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    color: white; border-radius: 15px; margin: 2rem 0;">
            <h2>🚀 Welcome to Continuous Performance Analytics</h2>
            <p>Start by uploading your first CSV file to begin tracking employee performance over time!</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### ✨ New Features:

        - **📈 Continuous Tracking**: Keep adding CSV files to build comprehensive performance timelines
        - **🎯 Individual Journeys**: Track each employee's progress across multiple reports
        - **📊 Historical Analysis**: Compare performance trends and identify improvement patterns
        - **🔥 Performance Heatmaps**: Visualize team performance across all time periods
        - **⚡ Real-time Updates**: Dashboard updates automatically as you add new data
        - **🏆 Long-term Rankings**: See who consistently performs well over time
        - **💡 Trend Analysis**: Identify improving and declining performance patterns
        """)
        return

    # Enhanced view selection
    view_tabs = st.tabs(
        ["📊 Overview", "📈 Timeline Analysis", "👤 Individual Journey", "🔥 Performance Heatmap", "🏆 Long-term Rankings"])

    with view_tabs[0]:  # Overview
        metrics = dashboard.calculate_enhanced_metrics(consolidated_df)
        dashboard.create_enhanced_kpi_cards(metrics, f"All Time ({st.session_state.file_counter} reports)")

        st.markdown("---")

        # Latest vs First comparison
        if len(st.session_state.all_performance_data) > 1:
            first_data = st.session_state.all_performance_data[0]['data']
            latest_data = st.session_state.all_performance_data[-1]['data']

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📅 First Report Summary")
                first_metrics = dashboard.calculate_enhanced_metrics(first_data)
                if 'avg_productivity' in first_metrics:
                    st.metric("Team Productivity", f"{first_metrics['avg_productivity']:.1f}/5")
                st.metric("Team Size", len(first_data['Employee_ID'].unique()))

            with col2:
                st.markdown("#### 📅 Latest Report Summary")
                latest_metrics = dashboard.calculate_enhanced_metrics(latest_data)
                if 'avg_productivity' in latest_metrics and 'avg_productivity' in first_metrics:
                    productivity_change = latest_metrics['avg_productivity'] - first_metrics['avg_productivity']
                    st.metric("Team Productivity", f"{latest_metrics['avg_productivity']:.1f}/5",
                              delta=f"{productivity_change:+.1f}")

                size_change = len(latest_data['Employee_ID'].unique()) - len(first_data['Employee_ID'].unique())
                st.metric("Team Size", len(latest_data['Employee_ID'].unique()), delta=f"{size_change:+d}")

    with view_tabs[1]:  # Timeline Analysis
        dashboard.create_comprehensive_timeline_view()

    with view_tabs[2]:  # Individual Journey
        available_employees = list(st.session_state.employee_timeline.keys())

        if available_employees:
            # Sort employees by name for better UX
            available_employees.sort(key=lambda x: st.session_state.employee_timeline[x]['name'])

            selected_employee = st.selectbox(
                "🔍 Select Employee for Journey Analysis",
                available_employees,
                format_func=lambda
                    x: f"{st.session_state.employee_timeline[x]['name']} ({st.session_state.employee_timeline[x]['role']}) - {len(st.session_state.employee_timeline[x]['history'])} reports"
            )

            if selected_employee:
                dashboard.create_enhanced_individual_timeline(selected_employee)
        else:
            st.info("👤 Upload performance data to view individual employee journeys")

    with view_tabs[3]:  # Performance Heatmap
        dashboard.create_employee_comparison_heatmap()

    with view_tabs[4]:  # Long-term Rankings
        dashboard.create_long_term_rankings()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border-radius: 10px; margin-top: 2rem;">
        <h4>📊 Continuous Performance Analytics Dashboard</h4>
        <p>Designed and created by Reda HEDDAD</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
