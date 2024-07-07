from flask import Flask, request, render_template, send_file
import pandas as pd
import os

app = Flask(__name__)

def allocate_rooms(group_df, hostel_df):
    allocations = []

    # Prepare hostels
    hostels = hostel_df.to_dict(orient='records')

    for index, group in group_df.iterrows():
        group_id = group['Group ID']
        members = group['Members']
        gender = group['Gender']

        # Allocate rooms for the group
        allocated = False
        for hostel in hostels:
            if hostel['Gender'] in gender and hostel['Capacity'] >= members:
                allocations.append({
                    'Group ID': group_id,
                    'Hostel Name': hostel['Hostel Name'],
                    'Room Number': hostel['Room Number'],
                    'Members Allocated': members
                })
                hostel['Capacity'] -= members
                allocated = True
                break

        if not allocated:
            print(f"Could not allocate room for group {group_id}")

    return pd.DataFrame(allocations)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    group_file = request.files['group_file']
    hostel_file = request.files['hostel_file']

    group_df = pd.read_csv(group_file)
    hostel_df = pd.read_csv(hostel_file)

    allocation = allocate_rooms(group_df, hostel_df)

    output_path = os.path.join('data', 'allocation.csv')
    allocation.to_csv(output_path, index=False)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
