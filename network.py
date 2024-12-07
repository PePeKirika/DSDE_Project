import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile
import os

# Streamlit configuration
st.set_page_config(page_title="Network Graph Viewer", layout="wide")

# Title and Description
st.title("Network Graph Viewer")
st.write("This app visualizes a network graph of publications and references based on the selected title. Choose a title from the dropdown to view its related references.")

# Specify file paths
refs_file_path = "output/Citation_network_ref/part-00000-41e9e2f9-d0bd-4426-bed9-c1d1c4d231da-c000.csv"  # Replace with the path to your 'refs' file
titles_file_path = "output/Citation_network_title_id/part-00000-fb71bd1e-c302-430b-9e59-817f1c0d2b4b-c000.csv"  # Replace with the path to your 'titles' file

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
            st.markdown("### Network Graph")
            st.markdown("The graph is interactive. You can zoom and drag nodes.")
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
