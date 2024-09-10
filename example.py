import requests
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mplcursors  # Import mplcursors for hover tooltips
from datetime import datetime, timedelta

# Function to fetch weather data
def fetch_weather_data(location):
    # Define the API endpoint and query parameters
    url = "https://visual-crossing-weather.p.rapidapi.com/history"

    # Calculate the start and end dates
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    querystring = {
        "startDateTime": start_date.strftime("%Y-%m-%dT00:00:00"),
        "aggregateHours": "24",
        "location": location,
        "endDateTime": end_date.strftime("%Y-%m-%dT00:00:00"),
        "unitGroup": "us",
        "dayStartTime": "0:00:00",  # Full day data
        "dayEndTime": "23:59:59",  # Full day data
        "contentType": "csv",
        "shortColumnNames": "false"
    }

    headers = {
        "x-rapidapi-key": "55434ad188msh5150b3ca21660e6p1507c7jsn46e145ceb6c2",
        "x-rapidapi-host": "visual-crossing-weather.p.rapidapi.com"
    }

    # Make the API request
    response = requests.get(url, headers=headers, params=querystring)

    # Check if the response is successful
    if response.status_code == 200:
        # Save the response content to a CSV file
        with open('weather_data.csv', 'wb') as file:
            file.write(response.content)
        print("Dataset saved as weather_data.csv")
        
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv('weather_data.csv')
        
        # Filter specific columns and format Date time
        df_filtered = df[['Date time', 'Temperature', 'Relative Humidity', 'Precipitation', 'Minimum Temperature', 'Maximum Temperature']]
        df_filtered['Date time'] = pd.to_datetime(df_filtered['Date time']).dt.strftime('%d-%m-%Y')
        print(df_filtered)
        
        return df_filtered
    else:
        messagebox.showerror("Error", f"Failed to retrieve data: {response.text}")
        return None

# Function to draw a line graph for rainfall with hover tooltips
def draw_rainfall_line_graph(df):
    df['Date time'] = pd.to_datetime(df['Date time'], format='%d-%m-%Y')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Date time'], df['Precipitation'], marker='o', linestyle='-', color='blue', label='Precipitation')
    ax.set_title('Rainfall Over the Last 7 Days')
    ax.set_xlabel('Date')
    ax.set_ylabel('Precipitation (inches)')
    ax.xaxis.set_tick_params(rotation=45)
    ax.grid(True)
    
    # Add hover tooltips using mplcursors
    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(
        f"Date: {sel.artist.get_xdata()[sel.target.index]:%d-%m-%Y}\nPrecipitation: {sel.artist.get_ydata()[sel.target.index]:.2f} inches"))
    
    plt.show()

# Function to draw a pie chart for rainfall with hover tooltips
def draw_rainfall_pie_chart(df):
    df['Date time'] = pd.to_datetime(df['Date time'], format='%d-%m-%Y')
    precipitation_data = df['Precipitation'].values
    labels = df['Date time'].dt.strftime('%d-%m-%Y').values

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(precipitation_data, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title('Rainfall Distribution Over the Last 7 Days')
    ax.axis('equal')
    
    # Add hover tooltips using mplcursors
    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(
        f"Date: {labels[sel.target.index]}\nPrecipitation: {precipitation_data[sel.target.index]:.2f} inches"))

    plt.show()

# Function to draw a graph for temperature
def draw_temperature_graph(df):
    df['Date time'] = pd.to_datetime(df['Date time'], format='%d-%m-%Y')
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date time'], df['Minimum Temperature'], marker='o', linestyle='-', color='orange', label='Min Temperature')
    plt.plot(df['Date time'], df['Maximum Temperature'], marker='o', linestyle='-', color='red', label='Max Temperature')
    plt.title('Temperature Over the Last 7 Days')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°F)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.show()

# Function to draw a graph for humidity
def draw_humidity_graph(df):
    df['Date time'] = pd.to_datetime(df['Date time'], format='%d-%m-%Y')
    
    plt.figure(figsize=(12, 6))
    plt.plot(df['Date time'], df['Relative Humidity'], marker='o', linestyle='-', color='green')
    plt.title('Humidity Over the Last 7 Days')
    plt.xlabel('Date')
    plt.ylabel('Relative Humidity (%)')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()

# Function to analyze and show weather summary
def show_weather_summary(df):
    max_temp = df['Maximum Temperature'].max()
    min_temp = df['Minimum Temperature'].min()
    max_rainfall = df['Precipitation'].max()
    max_humidity = df['Relative Humidity'].max()
    
    max_temp_date = df[df['Maximum Temperature'] == max_temp]['Date time'].values[0]
    min_temp_date = df[df['Minimum Temperature'] == min_temp]['Date time'].values[0]
    max_rainfall_date = df[df['Precipitation'] == max_rainfall]['Date time'].values[0]
    max_humidity_date = df[df['Relative Humidity'] == max_humidity]['Date time'].values[0]
    
    summary_text = (f"Maximum Temperature: {max_temp}°F on {max_temp_date}\n"
                    f"Minimum Temperature: {min_temp}°F on {min_temp_date}\n"
                    f"Maximum Rainfall: {max_rainfall} inches on {max_rainfall_date}\n"
                    f"Highest Humidity: {max_humidity}% on {max_humidity_date}")
    
    # Display summary text in the text widget
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, summary_text)

# Function to display the weather data in a table
def show_data_table(df):
    # Hide other widgets
    input_frame.pack_forget()
    result_text.pack_forget()
    navigation_frame.pack_forget()
    
    # Clear any existing data in the treeview
    for i in tree.get_children():
        tree.delete(i)
    
    # Insert new data into the treeview
    for index, row in df.iterrows():
        tree.insert("", "end", values=(row['Date time'], row['Temperature'], row['Relative Humidity'], 
                                       row['Precipitation'], row['Minimum Temperature'], row['Maximum Temperature']))
    
    # Configure the Treeview appearance
    style = ttk.Style()
    style.configure("Treeview", background="black", foreground="black", fieldbackground="black")
    style.configure("Treeview.Heading", background="yellow", foreground="black")

    tree.pack(fill='both', expand=True)

    # Add a back button to go back to the search page
    back_button.pack(fill='x', padx=20, pady=10)

# Function to handle the back button click
def on_back_button_clicked():
    # Show the input and navigation frames
    input_frame.pack(fill='x', expand=True)
    result_text.pack(fill='x', padx=20, pady=10)
    navigation_frame.pack(fill='x', expand=True)
    
    # Hide the treeview and back button
    tree.pack_forget()
    back_button.pack_forget()

# Function to handle the search button click
def on_search_button_clicked():
    location = location_entry.get()
    if location:
        global weather_data
        weather_data = fetch_weather_data(location)
        if weather_data is not None:
            # Enable navigation buttons
            for btn in navigation_buttons:
                btn.config(state='normal')
            # Show weather summary
            show_weather_summary(weather_data)
    else:
        messagebox.showwarning("Input Error", "Please enter a location")

# Function to handle navigation button click for rainfall line graph
def on_show_rainfall_line_graph():
    draw_rainfall_line_graph(weather_data)

# Function to handle navigation button click for rainfall pie chart
def on_show_rainfall_pie_chart():
    draw_rainfall_pie_chart(weather_data)

# Function to handle navigation button click for temperature graph
def on_show_temperature_graph():
    draw_temperature_graph(weather_data)

# Function to handle navigation button click for humidity graph
def on_show_humidity_graph():
    draw_humidity_graph(weather_data)

# Create the main application window
root = tk.Tk()
root.title("Weather Data Viewer")
root.configure(bg='black')  # Set the background color to black

# Create a frame for the input section
input_frame = tk.Frame(root, pady=20, padx=20, bg='black')
input_frame.pack(fill='x', expand=True)

# Create and place the input widgets within the frame
tk.Label(input_frame, text="Enter the location (e.g., Washington,DC,USA):", bg='black', fg='yellow').grid(row=0, column=0, pady=5)
location_entry = tk.Entry(input_frame, width=50)
location_entry.grid(row=1, column=0, pady=5)
search_button = tk.Button(input_frame, text="Search", command=on_search_button_clicked, bg='yellow', fg='black')
search_button.grid(row=1, column=1, padx=10)

# Create a text widget for displaying results
result_text = tk.Text(root, height=8, wrap='word', bg='black', fg='white')
result_text.pack(fill='x', padx=20, pady=10)

# Create a frame for the navigation buttons
navigation_frame = tk.Frame(root, pady=20, padx=20, bg='black')
navigation_frame.pack(fill='x', expand=True)

# Create navigation buttons within the frame
navigation_buttons = []
btn_rainfall_line = tk.Button(navigation_frame, text="Rainfall Line Graph", state='disabled', command=on_show_rainfall_line_graph, bg='yellow', fg='black')
btn_rainfall_line.pack(side=tk.LEFT, padx=10)
navigation_buttons.append(btn_rainfall_line)

btn_rainfall_pie = tk.Button(navigation_frame, text="Rainfall Pie Chart", state='disabled', command=on_show_rainfall_pie_chart, bg='yellow', fg='black')
btn_rainfall_pie.pack(side=tk.LEFT, padx=10)
navigation_buttons.append(btn_rainfall_pie)

btn_temperature = tk.Button(navigation_frame, text="Temperature Graph", state='disabled', command=on_show_temperature_graph, bg='yellow', fg='black')
btn_temperature.pack(side=tk.LEFT, padx=10)
navigation_buttons.append(btn_temperature)

btn_humidity = tk.Button(navigation_frame, text="Humidity Graph", state='disabled', command=on_show_humidity_graph, bg='yellow', fg='black')
btn_humidity.pack(side=tk.LEFT, padx=10)
navigation_buttons.append(btn_humidity)

# Create a button to show the data table
btn_show_data = tk.Button(navigation_frame, text="Show Data", state='disabled', command=lambda: show_data_table(weather_data), bg='yellow', fg='black')
btn_show_data.pack(side=tk.LEFT, padx=10)
navigation_buttons.append(btn_show_data)

# Create a Treeview widget to display the data table
tree = ttk.Treeview(root, columns=('Date', 'Temperature', 'Relative Humidity', 'Precipitation', 'Min Temperature', 'Max Temperature'), show='headings', height=10)
tree.heading('Date', text='Date')
tree.heading('Temperature', text='Temperature (°F)')
tree.heading('Relative Humidity', text='Relative Humidity (%)')
tree.heading('Precipitation', text='Precipitation (inches)')
tree.heading('Min Temperature', text='Min Temperature (°F)')
tree.heading('Max Temperature', text='Max Temperature (°F)')
tree.pack_forget()  # Hide initially

# Create a back button to return to the search page
back_button = tk.Button(root, text="Back", command=on_back_button_clicked, bg='yellow', fg='black')
back_button.pack_forget()

# Run the Tkinter event loop
root.mainloop()
