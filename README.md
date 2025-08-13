# Weekly-Monthly-performance-dashboard

📊 Employee Performance Dashboard
Overview
The Employee Performance Dashboard is an interactive Streamlit web application designed to track, analyze, and visualize weekly and monthly performance metrics across different employee roles in a company.

It transforms uploaded CSV performance reports into insightful KPIs, charts, problem-suggestion analyses, and individual performance views, helping managers and team leads make data-driven decisions.

✨ Key Features
1. Data Upload & Processing
Weekly Analysis: Upload a single weekly CSV report.

Monthly Analysis: Upload 4 weekly CSV files for a full month’s aggregated analysis.

Automatic Column Mapping: Flexible column name detection for different CSV formats.

Data Cleaning:

Standardizes column names.

Fills missing numeric values with 0.

Parses dates into datetime objects.

2. Performance KPIs
Role-based and company-wide total and average metrics:

🎥 Video Editors – Videos Created

🎨 Designers – Designs Created

📝 Account Managers – Scripts Produced, Posts Published, Client Meetings

🎬 Filmmakers – Projects Worked

Productivity Scores aggregated across all roles.

3. Interactive Visualizations
Performance Charts: Compare individual performance against company averages.

Trend Analysis: Weekly performance trends for monthly data.

Custom Styling: Gradient headers, clean KPI cards, and well-structured tables.

4. Problem & Suggestion Analysis
Automatically extracts reported problems and suggestions for improvement.

Top 10 common issues table.

Word Clouds for quick thematic insights into challenges and ideas.

5. Individual Employee View
Detailed profile with:

Role and position.

Role-specific metrics.

Comparison against company averages.

Full weekly/monthly activity table.

Individual problems and suggestions.

🖥️ How to Use
1. Install Dependencies
bash
Copy code
pip install streamlit pandas plotly numpy matplotlib wordcloud
2. Run the App
bash
Copy code
streamlit run app.py
(Replace app.py with your file name if different)

3. Upload Data
Weekly View: Upload one weekly CSV in the sidebar.

Monthly View: Upload exactly 4 weekly CSV files (Week 1–Week 4).

CSV format must include at least:

Name, Role, Week Start Date, Week End Date

Role-specific metric columns (e.g., Videos Created, Designs Created, etc.)

The app automatically detects variations in column names (e.g., Name vs Employee Name).

4. Navigate Views
The dashboard has three tabs:

Tab	Purpose
📅 Weekly View	View company-wide KPIs, role summaries, and problems/suggestions for the week.
📊 Monthly View	See 4-week aggregated KPIs, trends, and issues.
👤 Individual View	Select an employee to view their personal performance breakdown.

📂 File Structure Example
graphql
Copy code
app.py               # Main Streamlit app
requirements.txt     # Dependencies list
weekly_report.csv    # Sample weekly CSV data
⚙️ Under the Hood – Main Components
PerformanceDashboard Class
Handles:

Column mapping & data cleaning.

Metric calculations per role.

KPI card rendering.

Word cloud creation.

Performance chart generation.

Problems & suggestions analysis.

Individual employee view rendering.

Technologies Used
Streamlit: Interactive UI framework.

Pandas: Data cleaning and transformation.

Plotly: Dynamic charts and visualizations.

Matplotlib: Word cloud rendering.

WordCloud: Problem/suggestion visual insights.

NumPy, Regex, Datetime: Supporting data manipulation and cleaning.

📸 Example Visuals
KPI Cards:

yaml
Copy code
Total Videos: 120  |  Avg: 6.0
Total Designs: 80  |  Avg: 4.0
Avg Productivity: 4.2/5
Charts:

Individual performance bars with a red dashed line for company averages.

Weekly trend line charts for monthly analysis.

Word Clouds:

Quick glance at recurring problems and suggestions.

🚀 Benefits
Provides actionable insights into productivity and challenges.

Role-specific analysis for targeted improvement.

Flexible with different CSV naming conventions.

Consolidates weekly reports into monthly overviews.

📌 Future Improvements
Add export to PDF report generation.

Enable multi-month trend comparison.

Integrate with Google Sheets API for real-time data fetching.

Add user authentication for secure internal access.
