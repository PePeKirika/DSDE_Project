import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import linregress
from pyvis.network import Network
import glob
import tempfile
import os

def get_file_path(path):
    return (glob.glob(f'{path}/*.csv'))[0]

# Page configuration
st.set_page_config(layout="wide")
st.title('Data Visualization')

# Load data
@st.cache_data
def load_Topic_Distribution_Data():
    return pd.read_csv(get_file_path('./output/Topic_Distribution_Count_Subject_Area_Data'))
df_Topic_Distribution_Data = load_Topic_Distribution_Data()
def load_Citedby_Prediction_Data():
    return pd.read_csv(get_file_path('./output/Citedby_Prediction_Data'))
df_Citedby_Prediction_Data = load_Citedby_Prediction_Data()

# Specify file paths
refs_file_path = get_file_path("./output/Citation_network_ref")  # Replace with the path to your 'refs' file
titles_file_path = get_file_path("./output/Citation_network_title_id")  # Replace with the path to your 'titles' file

# Sidebar controls for customization
st.header("Topic Distribution")
st.markdown("""
### Treemap Explanation
This treemap visualizes the distribution of **subject areas** across different years, with each block representing a subject area. The size of each block corresponds to the **count** (or frequency) of that subject area within the respective year.

- **Hierarchy**: The treemap is structured into layers:
  - The **top layer** represents the year (e.g., 2022, 2021, etc.).
  - The **second layer** contains various **subject areas** within each year.
- **Colors**: Different subject areas are color-coded, making it easier to distinguish between them.
- **Block Size**: Larger blocks indicate a higher count or frequency of a specific subject area in that year.

#### Example:
- In **2022**, the largest subject area is "Multidisciplinary" with a count of **309**.
- In **2023**, "Multidisciplinary" also leads with **191**, followed by "Chemistry (all)" with **132**.

The treemap allows a quick comparison of the prevalence of subject areas over the years.
""")
# Add sliders below the header
col1, col2 = st.columns(2)

with col1:
    font_size = st.slider("Font Size:", min_value=10, max_value=30, value=18)

with col2:
    head_count = st.slider("Number of Top Items per Year:", min_value=1, max_value=50, value=10)

# Process data for Treemap
df_Topic_Distribution_Data = df_Topic_Distribution_Data.sort_values(by=["date", "count"], ascending=[True, False])
df_Topic_Distribution_Data = df_Topic_Distribution_Data.groupby("date").head(head_count)

# Create Treemap
fig_Topic_Distribution_Data = px.treemap(
    df_Topic_Distribution_Data, 
    path=[px.Constant("Year"), 'date', 'subject_area', 'count'],  # Path of hierarchy
    values='count', 
    color='subject_area'
)

# Customize Treemap
fig_Topic_Distribution_Data.update_traces(
    textfont=dict(size=font_size)  # Dynamic font size from sidebar
)

fig_Topic_Distribution_Data.update_layout(
    margin=dict(t=50, l=25, r=25, b=25),
    height=600, 
    width=1400,
    
)

st.plotly_chart(fig_Topic_Distribution_Data, use_container_width=True)

fig_Citedby_Prediction_Data = px.scatter(df_Citedby_Prediction_Data, 
                x="prediction", 
                y="citedby_count",
                labels={"citedby_count": "Cited By Count", "prediction": "Predicted Cited By Count"},
                title="Scatter Plot of Cited By Count vs Predicted Cited By Count"
)

fig_Citedby_Prediction_Data.update_traces(
    marker=dict(color='rgba(31, 119, 180, 0.10)', size=10),
)

slope, intercept, r_value, p_value, std_err = linregress(df_Citedby_Prediction_Data['prediction'], df_Citedby_Prediction_Data['citedby_count'])

fig_Citedby_Prediction_Data.add_trace(go.Scatter(
    x=df_Citedby_Prediction_Data['prediction'],
    y=intercept + slope * df_Citedby_Prediction_Data['prediction'],
    mode='lines',
    name=f'Best Fit Line (R^2 = {r_value**2:.2f})',
    line=dict(color='rgba(255, 0, 0, 0.7)')
))

fig_Citedby_Prediction_Data.update_layout(
    margin=dict(t=50, l=25, r=25, b=25),
    height=600, 
    width=1400,
)

st.header("Citedby Prediction Data")
st.markdown("""
### Scatter Plot Explanation
This scatter plot shows the relationship between the **actual citation counts** (`Cited By Count`) and the **predicted citation counts** (`Predicted Cited By Count`) for a given dataset.

- **X-Axis**: Represents the predicted values of citation counts (`Predicted Cited By Count`).
- **Y-Axis**: Represents the actual citation counts (`Cited By Count`).
- **Data Points**: Each dot represents an observation, comparing actual and predicted citation counts for a specific record.
- **Best Fit Line**: A regression line is added to show the general trend in the data, with the R-squared value (`R² = 0.30`) indicating how well the model's predictions align with the actual values.
""")

st.plotly_chart(fig_Citedby_Prediction_Data, use_container_width=True)



#Network graph
try:
    # Load CSV files
    refs_df = pd.read_csv(refs_file_path)
    titles_df = pd.read_csv(titles_file_path)

    # Ensure consistent data types (convert IDs to strings)
    refs_df["SGR_id"] = refs_df["SGR_id"].astype(str)
    refs_df["Ref"] = refs_df["Ref"].astype(str)
    titles_df["SGR_id"] = titles_df["SGR_id"].astype(str)

    # Create the PyVis network graph
    net = Network(height="750px", width="100%", notebook=False, directed=False)

    # Adjust layout (optional)
    net.force_atlas_2based()  # Enables the ForceAtlas2 layout, which helps in node distribution

    # Adjust the parameters of ForceAtlas2 for better spacing
    net.set_options("""
    var options = {
      "physics": {
        "enabled": true,
        "barnesHut": {
          "gravitationalConstant": -20000,
          "centralGravity": 0.2,
          "springLength": 250,
          "springConstant": 0.02,
          "damping": 0.4 
        }
      }
    }
    """)

    st.header("Network of References and Citations")
    st.markdown("""
    ### This network graph visualizes the relationships between a publication and its references or citations.

    - **Blue Node**: Represents the central publication being analyzed (the one being referenced by others).  
    - **Red Nodes**: Represent other publications that cite or are cited by the central publication.  

    #### Graph Dynamics:  
    1. **Edges (Lines)**: Indicate the connection between the central publication (blue node) and related publications (red nodes).  
    2. **Interactivity**:  
    - Nodes can be zoomed and dragged for better visualization.  
    - It helps identify key relationships in citation patterns.  

    #### Purpose:
    This visualization is particularly useful for analyzing the impact or relevance of a publication within a research domain by tracking who references or cites it.
    """)

    # Create a select box for the user to choose a title
    title_options = titles_df['title'].unique()  # Get unique titles from titles_df
    selected_title = st.selectbox("Select a publication title:", title_options)

    if selected_title:
        # Filter titles_df to find the SGR_id(s) matching the selected title
        matched_titles = titles_df[titles_df['title'] == selected_title]

        if not matched_titles.empty:
            # Filter references based on matching titles
            filtered_refs_df = refs_df[refs_df['SGR_id'].isin(matched_titles['SGR_id'])]

            # Add nodes for the matched SGR_ids and their references
            for _, row in filtered_refs_df.iterrows():
                # Add the SGR_id node
                sgr_id = row["SGR_id"]
                sgr_id_title = matched_titles[matched_titles["SGR_id"] == sgr_id]["title"].values
                if len(sgr_id_title) > 0:
                    sgr_id_title = sgr_id_title[0]
                else:
                    pass
                    #sgr_id_title = f"SGR_id{row['SGR_id']}"  # Default label if no title is found
                
                # Add node for SGR_id
                net.add_node(sgr_id, label=sgr_id_title, title=sgr_id_title, color="blue", size=20)

                # Add the Ref node
                ref = row["Ref"]
                ref_title = titles_df[titles_df["SGR_id"] == ref]["title"].values
                if len(ref_title) > 0:
                    ref_title = ref_title[0]
                    net.add_node(ref, label=ref_title, title=ref_title, color="red", size=10)
                else:
                    #ref_title = f"Ref{ref}"  # Default label if no title is found
                    pass
                # Add node for Ref
                #net.add_node(ref, label=ref_title, title=ref_title, color="red", size=10)

                # Add edge between SGR_id and Ref
                if ref in net.get_nodes():
                    net.add_edge(sgr_id, ref)

            # Save the graph to a temporary HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                graph_path = tmp_file.name
                net.save_graph(graph_path)

            # Display the graph in Streamlit
            
            st.components.v1.html(open(graph_path, "r").read(), height=800)

            # Display matched titles
            st.write(f"### References related to '{selected_title}'")
            st.write(matched_titles)

            # Cleanup temporary file
            os.unlink(graph_path)
        else:
            st.write("No references found for the selected title.")
    else:
        st.write("Select a title to view its references.")

except Exception as e:
    st.error(f"An error occurred while processing the files: {e}")