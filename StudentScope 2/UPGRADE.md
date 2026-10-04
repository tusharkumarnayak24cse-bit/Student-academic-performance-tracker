# StudentScope dashboard upgrade

This upgrade is based on the saved original StudentScope project.

- Responsive two-row KPI layout on narrower screens.
- Marks obtained and maximum shown separately to prevent truncation.
- Refreshed hero, spacing, cards and subject progress bars.
- Gentle entrance and hover animations, respecting reduced-motion preferences.
- Existing CSV import/export, data editing, trends, prediction and target planner retained.

## Update your existing Render app

Replace app.py in your existing StudentScope GitHub repository with this app.py, then commit the change. Keep your existing Render service and its configuration. If automatic deploy is enabled, Render deploys the commit; otherwise use Manual Deploy → Deploy latest commit.

Run locally: pip install -r requirements.txt then streamlit run app.py.

Records remain temporary per browser session. Download a backup before refreshing or redeploying.

## Animated welcome
The welcome overlay presents all three team members in sequence and dismisses after approximately five seconds. Skip intro dismisses it immediately. It runs once per Streamlit session; widget interactions do not replay it. Reduced-motion users go straight to the dashboard.
