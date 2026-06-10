import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Define the tasks and schedule based on SPRINT_PLAN.md
tasks = [
    {"Task": "Foundation & Setup (Repo, Env, Skeleton)", "Start": 1, "Duration": 1, "Owner": "All"},
    {"Task": "Detection + Speech Pipelines", "Start": 2, "Duration": 1, "Owner": "Haseeb/Harsha"},
    {"Task": "Knowledge Base Ingestion", "Start": 2, "Duration": 2, "Owner": "Gowtham"},
    {"Task": "RIAR Alpha & Base Routing", "Start": 3, "Duration": 1, "Owner": "Haseeb"},
    {"Task": "Full RIAR & Orchestration", "Start": 4, "Duration": 1, "Owner": "Haseeb/Harsha"},
    {"Task": "Multilingual Evaluation & Testing", "Start": 4, "Duration": 1, "Owner": "Gowtham"},
    {"Task": "Full System Integration (E2E Flow)", "Start": 5, "Duration": 1, "Owner": "All"},
    {"Task": "Polish, UX & Performance Tuning", "Start": 6, "Duration": 1, "Owner": "All"},
    {"Task": "Final Evaluation & Paper Draft", "Start": 6, "Duration": 2, "Owner": "Gowtham/Haseeb"},
    {"Task": "Deployment & Final Presentation", "Start": 7, "Duration": 1, "Owner": "All"}
]

df = pd.DataFrame(tasks)
df = df.iloc[::-1] # Reverse for plotting top-to-bottom

# Setup plot
fig, ax = plt.subplots(figsize=(10, 6))

colors = {"All": "tab:purple", "Haseeb": "tab:blue", "Harsha": "tab:orange", "Gowtham": "tab:green", "Haseeb/Harsha": "tab:cyan", "Gowtham/Haseeb": "tab:pink"}

# Plot bars
for i, task in enumerate(df.itertuples()):
    ax.barh(task.Task, task.Duration, left=task.Start, color=colors[task.Owner], edgecolor='black', alpha=0.8)

# Format axes
ax.set_xlabel('Sprint Week')
ax.set_title('VidyaSahayak 7-Week Sprint Gantt Chart', fontsize=14, pad=20)
ax.set_xticks(np.arange(1, 9))
ax.set_xlim(0.5, 8.5)
ax.grid(axis='x', linestyle='--', alpha=0.7)

# Add legend
handles = [plt.Rectangle((0,0),1,1, color=colors[k], ec="black", alpha=0.8) for k in colors]
ax.legend(handles, colors.keys(), title="Ownership", loc='lower right')

plt.tight_layout()
plt.savefig('gantt_chart.png', dpi=300)
print("Saved gantt_chart.png")
