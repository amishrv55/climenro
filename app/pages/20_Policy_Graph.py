import os
import sys
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from datetime import date
from streamlit.components.v1 import html

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_DIR = os.path.join(BASE_DIR, "data")
GRAPH_PATH = os.path.join(DATA_DIR, "policy_nodes.json")

if SCRIPTS_DIR not in sys.path:
    sys.path.append(SCRIPTS_DIR)

from activity_emission_factor import (
    load_activity_table,
    load_country_factors,
    classify_policy,
    estimate_emission_impact,
    get_activity_row,
    get_displacement_ratio,
    build_policy_node,
)

# Streamlit config
st.set_page_config(page_title="🌿 Policy Graph Builder", layout="wide")
st.title("🌿 National Policy Graph Builder")

# Custom CSS for better styling
st.markdown("""
<style>
    .stSelectbox, .stTextInput, .stDateInput, .stNumberInput {
        margin-bottom: 1rem;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .node-info {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    .graph-container {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .country-tab {
        font-size: 1.1em;
        font-weight: bold;
        padding: 8px 15px;
    }
</style>
""", unsafe_allow_html=True)

# Load data
activity_df = load_activity_table(os.path.join(DATA_DIR, "activity_emission_factor.csv"))
country_df = load_country_factors(os.path.join(DATA_DIR, "country_composite_factor.csv"))

# Tabs
input_tab, graph_tab, db_tab = st.tabs(["➕ Add Policy", "🌐 Interactive Graph", "📁 Policy Database"])

# -------------------
# TAB 1: ADD POLICY
# -------------------
with input_tab:
    st.header("➕ Add New Policy Node")
    
    col1, col2 = st.columns(2)
    
    with col1:
        policy_text = st.text_area("Policy Description", height=150)
        country = st.selectbox("Select Country", country_df["Country"].unique())
    
    with col2:
        intent = st.text_input("Graph Intent / Central Goal", value="Net Zero 2030")
        title = st.text_input("Policy Title")
        date_issued = st.date_input("Date Issued", value=date.today())

    if policy_text:
        result = classify_policy(policy_text, activity_df)

        if result["matched"]:
            activity_row = get_activity_row(result, activity_df)
            input_type = activity_row.get("Required Input Type", "budget").lower()
            uses_displacement = activity_row.get("Uses Displacement", False)
            country_row = country_df[country_df["Country"] == country].iloc[0] if uses_displacement else None

            st.markdown(f"### Enter Input for `{input_type}`")
            user_input = st.number_input("Input Value", min_value=1.0, step=1.0)

            if st.button("Add to Graph", key="add_policy_button"):
                policy_node = build_policy_node(policy_text, country, user_input, 5000, activity_df, country_df)

                if policy_node:
                    # Generate unique node ID using title, date and first 8 chars of hash
                    unique_id = f"{title}_{date_issued}_{hash(policy_text)}"[:50]
                    
                    policy_node.update({
                        "Policy Title": title,
                        "Country": country,
                        "Date": str(date_issued),
                        "Graph Intent": intent,
                        # Add/modify these fields to ensure uniqueness:
                        "Policy Node": unique_id,  # This replaces the non-unique identifier
                        "Display Name": f"{title} ({date_issued})",  # Human-readable label
                        "Original Text": policy_text  # Store original policy text
                    })
                    
                    if os.path.exists(GRAPH_PATH):
                        with open(GRAPH_PATH, 'r') as f:
                            graph_data = json.load(f)
                    else:
                        graph_data = []

                    graph_data.append(policy_node)
                    with open(GRAPH_PATH, 'w') as f:
                        json.dump(graph_data, f, indent=2)

                    st.success("✅ Policy added to graph database.")
                else:
                    st.error("❌ Could not generate policy node.")
        else:
            st.error("❌ No matching activity found in database.")

# -------------------
# TAB 2: GRAPH (Plotly Version with Country Subgraphs)
# -------------------
# In the graph_tab section, replace the graph creation logic with this:

with graph_tab:
    st.header("🌐 Interactive Policy Intent Graph")
    
    if os.path.exists(GRAPH_PATH):
        with open(GRAPH_PATH, 'r') as f:
            policy_nodes = json.load(f)

        graph_intents = sorted(set(p["Graph Intent"] for p in policy_nodes))
        selected_intent = st.selectbox("Select Graph Intent", graph_intents, key="graph_intent_select")

        # Get all countries for this intent
        countries = sorted(set(node["Country"] for node in policy_nodes if node["Graph Intent"] == selected_intent))
        
        if len(countries) == 0:
            st.info("No policies found for this intent. Add a policy to begin.")
        else:
            # Create tabs for each country
            country_tabs = st.tabs([f"🇺🇳 All Countries"] + [f"🇺🇳 {country}" for country in countries])
            
            for i, country in enumerate([None] + countries):
                with country_tabs[i]:
                    # Create network graph
                    G = nx.DiGraph()
                    
                    # For country-specific view, use country as central node
                    if country:
                        central_node = f"{country} Policies"
                        G.add_node(central_node, 
                                  size=50, 
                                  color='blue',
                                  title=f"{selected_intent} - {country}",
                                  country=country)
                    else:
                        # For "All Countries" view, keep the original central intent
                        central_node = selected_intent
                        G.add_node(central_node, 
                                  size=50, 
                                  color='blue',
                                  title=selected_intent,
                                  country='Global')
                    
                    # Add policy nodes
                    for node in policy_nodes:
                        if (node["Graph Intent"] == selected_intent and 
                            (country is None or node["Country"] == country)):
                            
                            G.add_node(
                                node["Policy Node"],
                                size=node["Node Size"],
                                color=node["Node Color"],
                                impact=node["CO₂ Impact (Mt ±)"],
                                title=node["Policy Title"],
                                country=node["Country"],
                                date=node["Date"],
                                sector=node.get("Sector", "N/A"),
                                alignment=node.get("Alignment", "Neutral")
                            )
                            G.add_edge(central_node, node["Policy Node"])

                    # Only show graph if we have nodes
                    if len(G.nodes()) > 1:
                        # Get positions for all nodes using spring layout
                        pos = nx.spring_layout(G, k=0.8, iterations=100)
                        
                        # Create edges for Plotly
                        edge_x = []
                        edge_y = []
                        for edge in G.edges():
                            x0, y0 = pos[edge[0]]
                            x1, y1 = pos[edge[1]]
                            edge_x.extend([x0, x1, None])
                            edge_y.extend([y0, y1, None])

                        edge_trace = go.Scatter(
                            x=edge_x, y=edge_y,
                            line=dict(width=1.5, color='#888'),
                            hoverinfo='none',
                            mode='lines')

                        # Create nodes for Plotly
                        node_x = []
                        node_y = []
                        node_text = []
                        node_size = []
                        node_color = []
                        customdata = []
                        
                        for node in G.nodes():
                            x, y = pos[node]
                            node_x.append(x)
                            node_y.append(y)
                            node_data = G.nodes[node]
                            
                            # Node text (hover info)
                            text = f"<b>{node}</b><br>"
                            if 'title' in node_data:
                                text += f"Title: {node_data.get('title', 'N/A')}<br>"
                            if 'country' in node_data:
                                text += f"Country: {node_data.get('country', 'N/A')}<br>"
                            if 'impact' in node_data:
                                text += f"Impact: {node_data.get('impact', 0):.2f} Mt CO₂<br>"
                            if 'sector' in node_data:
                                text += f"Sector: {node_data.get('sector', 'N/A')}<br>"
                            if 'date' in node_data:
                                text += f"Date: {node_data.get('date', 'N/A')}"
                            
                            node_text.append(text)
                            node_size.append(node_data.get('size', 20) * 2)
                            node_color.append(node_data.get('color', 'gray'))
                            customdata.append([
                                node_data.get('impact', 0), 
                                node_data.get('title', node),
                                node_data.get('country', 'Global')
                            ])

                        node_trace = go.Scatter(
                            x=node_x, y=node_y,
                            mode='markers+text',
                            hoverinfo='text',
                            textposition='top center',
                            textfont=dict(size=10),
                            marker=dict(
                                showscale=False,
                                color=node_color,
                                size=node_size,
                                line_width=2,
                                line_color='DarkSlateGrey'
                            ),
                            customdata=customdata,
                            text=[n if len(n) < 20 else n[:17] + "..." for n in G.nodes()],
                            hovertext=node_text
                        )

                        # Create the figure with updated layout
                        title = f'<b>{selected_intent}' + (f' - {country}' if country else '') + '</b>'
                        fig = go.Figure(data=[edge_trace, node_trace],
                                     layout=go.Layout(
                                        title=dict(
                                            text=title,
                                            font=dict(size=16)
                                        ),
                                        showlegend=False,
                                        hovermode='closest',
                                        margin=dict(b=20, l=5, r=5, t=40),
                                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                        height=700,
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)',
                                        clickmode='event+select'
                                    ))
                        
                        # Add some interactivity
                        fig.update_traces(
                            marker=dict(sizemode='diameter'),
                            selector=dict(mode='markers+text')
                        )
                        
                        # Display the graph
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Node details section
                        st.markdown("### Node Details")
                        st.markdown("Click on a node in the graph to see details here", 
                                   help="Node information will appear here after selection")
                        
                        # Placeholder for node details (will be filled by JavaScript)
                        node_details = st.empty()
                        
                        # JavaScript to handle node clicks and update Streamlit
                        html("""
                        <script>
                        const doc = window.parent.document;
                        const iframe = doc.querySelector('iframe[title="streamlitApp"]');
                        const stComm = iframe.contentWindow.parent.document;
                        
                        // Listen for Plotly click events
                        iframe.contentWindow.addEventListener('plotly_click', function(event) {
                            const point = event.points[0];
                            if (point) {
                                const impact = point.customdata[0];
                                const title = point.customdata[1];
                                const country = point.customdata[2];
                                const text = point.hovertext;
                                
                                // Find the Streamlit text area and update it
                                const textAreas = stComm.querySelectorAll('.stTextArea textarea');
                                if (textAreas.length > 0) {
                                    textAreas[0].value = `Selected Node: ${point.text}\\n\\n${text}`;
                                    textAreas[0].dispatchEvent(new Event('input', {bubbles: true}));
                                }
                            }
                        });
                        </script>
                        """, height=0)
                    else:
                        st.info(f"No policies found for {country if country else 'this intent'}")
    else:
        st.info("No policy data available. Add a policy to begin.")

# -------------------
# TAB 3: DATABASE
# -------------------
# In the db_tab section, replace the current implementation with this:

with db_tab:
    st.header("📁 Policy Graph Dataset")
    if os.path.exists(GRAPH_PATH):
        with open(GRAPH_PATH, 'r') as f:
            graph_data = json.load(f)

        df = pd.DataFrame(graph_data)
        
        # Convert date strings to datetime for proper filtering
        df['Date'] = pd.to_datetime(df['Date'])

        # Filters - expanded by default
        with st.expander("🔍 Filter Policies", expanded=True):
            cols = st.columns(4)
            
            with cols[0]:
                title_filter = st.text_input("Filter by Title")
            with cols[1]:
                country_filter = st.multiselect("Filter by Country", options=df["Country"].unique())
            with cols[2]:
                sector_filter = st.multiselect("Filter by Sector", options=df["Sector"].unique())
            with cols[3]:
                intent_filter = st.multiselect("Filter by Graph Intent", options=df["Graph Intent"].unique())
            
            cols = st.columns(3)
            with cols[0]:
                date_range = st.date_input(
                    "Date Range",
                    value=[date.today().replace(day=1), date.today()],
                    key="date_range"
                )
            with cols[1]:
                alignment_filter = st.multiselect(
                    "Filter by Alignment",
                    options=["Positive", "Negative", "Neutral"]
                )
            with cols[2]:
                min_impact, max_impact = st.slider(
                    "CO₂ Impact Range (Mt)",
                    min_value=float(df["CO₂ Impact (Mt ±)"].min()),
                    max_value=float(df["CO₂ Impact (Mt ±)"].max()),
                    value=(float(df["CO₂ Impact (Mt ±)"].min()), float(df["CO₂ Impact (Mt ±)"].max()))
                )

        # Apply filters
        filtered_df = df.copy()
        
        # Text filters
        if title_filter:
            filtered_df = filtered_df[filtered_df["Policy Title"].str.contains(title_filter, case=False)]
        
        # Multi-select filters
        if country_filter:
            filtered_df = filtered_df[filtered_df["Country"].isin(country_filter)]
        if sector_filter:
            filtered_df = filtered_df[filtered_df["Sector"].isin(sector_filter)]
        if intent_filter:
            filtered_df = filtered_df[filtered_df["Graph Intent"].isin(intent_filter)]
        if alignment_filter:
            filtered_df = filtered_df[filtered_df["Alignment"].isin(alignment_filter)]
        
        # Date range filter
        if len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered_df = filtered_df[
                (filtered_df["Date"] >= start_date) & 
                (filtered_df["Date"] <= end_date)
            ]
        
        # Impact range filter
        filtered_df = filtered_df[
            (filtered_df["CO₂ Impact (Mt ±)"] >= min_impact) & 
            (filtered_df["CO₂ Impact (Mt ±)"] <= max_impact)
        ]

        # Enhanced dataframe display with better column configuration
        try:
            st.dataframe(
                filtered_df.sort_values("Date", ascending=False),
                column_config={
                    "Policy Node": st.column_config.TextColumn("Node ID", width="medium"),
                    "Policy Title": st.column_config.TextColumn("Title", width="large"),
                    "Country": st.column_config.TextColumn("Country", width="small"),
                    "Date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
                    "Sector": st.column_config.TextColumn("Sector", width="medium"),
                    "CO₂ Impact (Mt ±)": st.column_config.NumberColumn(
                        "CO₂ Impact (Mt)",
                        format="%.2f",
                        width="small"
                    ),
                    "Alignment": st.column_config.TextColumn("Alignment", width="small"),
                    "Node Color": st.column_config.ColorColumn("Color", disabled=True)
                },
                column_order=[
                    "Policy Title",
                    "Country",
                    "Date",
                    "Sector",
                    "CO₂ Impact (Mt ±)",
                    "Alignment",
                    "Graph Intent"
                ],
                hide_index=True,
                use_container_width=True,
                height=600
            )
        except Exception as e:
            # Fallback for older Streamlit versions
            st.dataframe(
                filtered_df.sort_values("Date", ascending=False),
                hide_index=True,
                use_container_width=True
            )

        # Delete functionality
        st.subheader("🗑️ Delete Policy")
        
        if not filtered_df.empty:
            # Create a mapping of Policy Node to display text
            delete_options = []
            for node_id in filtered_df["Policy Node"].unique():
                try:
                    title = filtered_df[filtered_df['Policy Node'] == node_id]['Policy Title'].iloc[0]
                    date_part = node_id.split('_')[1] if '_' in node_id else "Unknown Date"
                    display_text = f"{title} ({date_part})"
                    delete_options.append((node_id, display_text))
                except:
                    continue
            
            if delete_options:
                # Convert to dictionary for selectbox
                delete_options_dict = dict(delete_options)
                selected_display = st.selectbox(
                    "Select Policy to Delete",
                    options=list(delete_options_dict.keys()),
                    format_func=lambda x: delete_options_dict[x]
                )
                
                if st.button("Delete Selected Policy", key="delete_button"):
                    updated_data = [node for node in graph_data if node["Policy Node"] != selected_display]
                    with open(GRAPH_PATH, 'w') as f:
                        json.dump(updated_data, f, indent=2)
                    st.success(f"✅ Deleted selected policy. Please refresh page.")
            else:
                st.warning("No deletable policies found in current filters")
        else:
            st.warning("No policies match current filters")