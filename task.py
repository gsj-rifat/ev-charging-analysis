import pandas as pd
import matplotlib.pyplot as plt
import os

#load the session data
session = pd.read_feather('C://Users//nn//PycharmProjects//Qwello-hometask//data//sessions.ipc')

print("Session column:", session.columns)
print(session.head(5))

# convert time column
session['started_at'] = pd.to_datetime(session['started_at'])
session['stopped_at'] = pd.to_datetime(session['stopped_at'])

# question 1: What is the total charged energy during the time period?

total_kwh = session['charged_energy'].sum() / 1000
print( f"Total charged energy: {total_kwh: .2f} kwh")

# question 2: How many EVSEs have been active by week?
session['week'] = session ['started_at'].dt.isocalendar().week
active_eves = session.groupby('week')['evse_id'].nunique()
active_eves.plot(kind='bar', title='Active EVES by week')
plt.ylabel("Unique EVSEs")
plt.tight_layout()
#plt.show()

# question 3: Do you notice any behaviour differences between roaming, normal and ad-hoc?

user_types = session['type'].value_counts()
user_types.plot(kind= 'bar', title= 'Session count by user type')
plt.ylabel("Count")
plt.tight_layout()
#plt.show()

# question 4: How many one-phase or three-phase charging sessions were there?

#see the outlet options
#print("Outlets:", session['outlet'].unique())

#session duration in hour
session['duration_hr'] = (session['stopped_at'] - session['started_at']).dt.total_seconds() / 3600

#compute avarage power
session['avg_power_kw'] = session['charged_energy'] / 1000 / session['duration_hr']

def guess_phase(power):
    if power > 7:
        return  "three_phase"
    else:
        return "one_phase"
session['infered_phase'] = session['avg_power_kw'].apply(guess_phase)

#plotting
session['infered_phase'].value_counts().plot(kind = 'bar', title = "Inferred Phase type")
plt.ylabel("Count")
plt.tight_layout()
#plt.show()

# question 5: What’s the histogram of maximum charging power per session?

meter_root = 'C://Users//nn//PycharmProjects//Qwello-hometask//data//meter_values'
ipc_file_paths= []
for root, dirs, files in os.walk(meter_root):
    for file in files:
        if file.endswith('.ipc'):
            ipc_file_paths.append(os.path.join(root,file))


sample_ipc = ipc_file_paths[0]
df_sample = pd.read_feather(sample_ipc)
#print("Column names:", df_sample.columns)
#print(df_sample.head(5))

max_powers = []

for path in ipc_file_paths[0:500]:
    try:
        df = pd.read_feather(path)
        if 'power' in df.columns:
            max_power = df['power'].max()
            if pd.notnull(max_power):
                max_powers.append(max_power)
        elif all(col in df.columns for col in ['l1_power', 'l2_power', 'l3_power']):
            df['total_power'] = df['l1_power']+df['l2_power']+df['l3_power']
            max_power = df['total_power'].max()
            if pd.notnull(max_power):
                max_powers.append(max_power)

    except Exception as e:
        print("Could not find file")

#plot histogram
plt.figure()
plt.hist(max_powers, bins= 20)
plt.title("Histogram for Max power per session")
plt.xlabel("Max Power")
plt.ylabel("Number of sessions")
plt.tight_layout()
plt.show()



