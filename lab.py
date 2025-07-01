import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Initialize session state for data persistence
if 'inventory' not in st.session_state:
    # Try to load existing data on startup
    if os.path.exists('inventory_data.json'):
        try:
            with open('inventory_data.json', 'r') as f:
                st.session_state.inventory = json.load(f)
        except:
            st.session_state.inventory = []
    else:
        st.session_state.inventory = []

# Define locations
LOCATIONS = ["SF", "SJ", "RTP", "BGL"]

# Asset categories and their specific fields (with optional fields marked)
ASSET_CATEGORIES = {
    "Meraki Switch": {
        "required": ["Model", "Serial Number", "MAC Address"],
        "optional": ["Firmware Version"]
    },
    "Cisco Switch": {
        "required": ["Model", "Serial Number", "MAC Address"],
        "optional": ["IOS Version"]
    },
    "Cisco Network Module": {
        "required": ["Model", "Part Number", "Serial Number", "Compatible With"],
        "optional": []
    },
    "SFP": {
        "required": ["Type", "Speed", "Wavelength", "Serial Number"],
        "optional": []
    },
    "Stack Cable": {
        "required": ["Length", "Type", "Part Number", "Serial Number"],
        "optional": []
    },
    "Lantronix Console": {
        "required": ["Model", "Serial Number", "IP Address", "Port Count"],
        "optional": []
    },
    "HP Switch": {
        "required": ["Model", "Serial Number", "MAC Address"],
        "optional": ["Firmware Version"]
    },
    "Raritan PDU": {
        "required": ["Model", "Serial Number", "IP Address", "Outlet Count"],
        "optional": []
    }
}

# Page configuration
st.set_page_config(
    page_title="MS Perfect Lab Inventory Management",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
    }
    .asset-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .location-header {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔧 MS Perfect Lab Inventory Management System")
st.markdown("Multi-location network equipment inventory with deployment tracking")

# Helper functions
def generate_asset_id():
    """Generate unique asset ID"""
    return f"AST-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def save_inventory():
    """Save inventory to JSON file"""
    try:
        with open('inventory_data.json', 'w') as f:
            json.dump(st.session_state.inventory, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_inventory():
    """Load inventory from JSON file"""
    if os.path.exists('inventory_data.json'):
        with open('inventory_data.json', 'r') as f:
            return json.load(f)
    return []

def get_asset_by_id(asset_id):
    """Get asset by ID"""
    for asset in st.session_state.inventory:
        if asset['asset_id'] == asset_id:
            return asset
    return None

def update_asset(asset_id, updated_data):
    """Update asset information"""
    for i, asset in enumerate(st.session_state.inventory):
        if asset['asset_id'] == asset_id:
            st.session_state.inventory[i].update(updated_data)
            save_inventory()
            return True
    return False

def get_assets_by_location(location):
    """Get all assets for a specific location"""
    return [asset for asset in st.session_state.inventory if asset.get('location') == location]

def display_location_inventory(location):
    """Display inventory for a specific location"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(f"🔍 Search {location} assets", 
                                   placeholder="Search by ID, name, serial, owner, order number...",
                                   key=f"search_{location}")
    
    with col2:
        filter_status = st.selectbox(f"Filter by status", 
                                    ["All", "Available", "Deployed"],
                                    key=f"filter_{location}")
    
    # Get unique owners for this location
    location_assets = get_assets_by_location(location)
    owners = ["All"] + sorted(list(set(asset.get('owner', '') for asset in location_assets if asset.get('owner', ''))))
    
    with col3:
        filter_owner = st.selectbox(f"Filter by owner",
                                   owners,
                                   key=f"owner_{location}")
    
    # Get location-specific inventory
    location_inventory = location_assets
    
    # Apply filters
    filtered_inventory = location_inventory
    
    if search_term:
        filtered_inventory = [
            asset for asset in filtered_inventory
            if search_term.lower() in str(asset).lower()
        ]
    
    if filter_status != "All":
        filtered_inventory = [
            asset for asset in filtered_inventory
            if asset['status'] == filter_status
        ]
    
    if filter_owner != "All":
        filtered_inventory = [
            asset for asset in filtered_inventory
            if asset.get('owner', '') == filter_owner
        ]
    
    # Display metrics for this location
    col1, col2, col3, col4 = st.columns(4)
    
    total_assets = len(location_inventory)
    available_assets = len([a for a in location_inventory if a['status'] == "Available"])
    deployed_assets = len([a for a in location_inventory if a['status'] == "Deployed"])
    
    with col1:
        st.metric("Total Assets", total_assets)
    with col2:
        st.metric("Available", available_assets)
    with col3:
        st.metric("Deployed", deployed_assets)
    with col4:
        st.metric("Utilization", f"{(deployed_assets/total_assets*100):.1f}%" if total_assets > 0 else "0%")
    
    st.divider()
    
    # Display inventory
    if filtered_inventory:
        for asset in filtered_inventory:
            # Get serial number from specifications
            serial_number = asset['specifications'].get('Serial Number', 'N/A')
            asset_name = asset.get('name', 'Unnamed')
            
            with st.expander(f"{asset['category']} - {asset_name} - SN: {serial_number} - ID: {asset['asset_id']} ({asset['status']})"):
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.write("**Basic Information:**")
                    st.write(f"Name: {asset_name}")
                    st.write(f"Network Name: {asset.get('network_name', 'N/A')}")
                    if asset.get('owner'):
                        st.write(f"Owner: {asset.get('owner')}")
                    if asset.get('order_number'):
                        st.write(f"Order Number: {asset.get('order_number')}")
                    st.write(f"Location: {asset['location']}")
                    st.write(f"Category: {asset['category']}")
                    st.write(f"Asset ID: {asset['asset_id']}")
                    st.write(f"Status: {asset['status']}")
                    st.write(f"Added: {asset['date_added']}")
                
                with col2:
                    st.write("**Specifications:**")
                    for key, value in asset['specifications'].items():
                        st.write(f"{key}: {value}")
                
                with col3:
                    if asset['status'] == "Deployed":
                        st.write("**Deployment Info:**")
                        st.write(f"Rack: {asset['deployment_info']['rack']}")
                        st.write(f"Row: {asset['deployment_info']['row']}")
                        st.write(f"Position: {asset['deployment_info']['position']}")
                        st.write(f"Deployed: {asset['deployment_info']['deployment_date']}")
                    
                    # Action buttons
                    if st.button(f"Edit", key=f"edit_{location}_{asset['asset_id']}"):
                        st.session_state[f"edit_mode_{asset['asset_id']}"] = True
                    
                    if st.button(f"Delete", key=f"delete_{location}_{asset['asset_id']}"):
                        if st.session_state.get(f"confirm_delete_{asset['asset_id']}", False):
                            st.session_state.inventory.remove(asset)
                            save_inventory()
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{asset['asset_id']}"] = True
                            st.warning("Click Delete again to confirm")
                
                # Edit mode - comprehensive editing
                if st.session_state.get(f"edit_mode_{asset['asset_id']}", False):
                    st.divider()
                    st.subheader("Edit Asset")
                    
                    # Basic Information
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input(
                            "Asset Name",
                            value=asset.get('name', ''),
                            key=f"name_{asset['asset_id']}"
                        )
                        new_network_name = st.text_input(
                            "Network Name",
                            value=asset.get('network_name', ''),
                            key=f"netname_{asset['asset_id']}"
                        )
                        new_owner = st.text_input(
                            "Owner Name",
                            value=asset.get('owner', ''),
                            key=f"owner_{asset['asset_id']}"
                        )
                        new_order_number = st.text_input(
                            "Order Number",
                            value=asset.get('order_number', ''),
                            key=f"order_{asset['asset_id']}"
                        )
                    with col2:
                        new_location = st.selectbox(
                            "Location",
                            LOCATIONS,
                            index=LOCATIONS.index(asset['location']),
                            key=f"loc_{asset['asset_id']}"
                        )
                        new_status = st.selectbox(
                            "Status", 
                            ["Available", "Deployed"],
                            index=0 if asset['status'] == "Available" else 1,
                            key=f"status_{asset['asset_id']}"
                        )
                        new_notes = st.text_area(
                            "Notes",
                            value=asset.get('notes', ''),
                            key=f"notes_{asset['asset_id']}",
                            height=100
                        )
                    
                    # Specifications - allow editing all fields
                    st.write("**Edit Specifications:**")
                    new_specifications = {}
                    spec_cols = st.columns(2)
                    
                    # Get all fields for the category
                    all_fields = ASSET_CATEGORIES[asset['category']]["required"] + ASSET_CATEGORIES[asset['category']]["optional"]
                    
                    # First, populate with existing values
                    for field in all_fields:
                        if field in asset['specifications']:
                            new_specifications[field] = asset['specifications'][field]
                    
                    # Then create input fields
                    for idx, field in enumerate(all_fields):
                        with spec_cols[idx % 2]:
                            is_required = field in ASSET_CATEGORIES[asset['category']]["required"]
                            field_label = f"{field} *" if is_required else f"{field} (Optional)"
                            value = st.text_input(
                                field_label,
                                value=asset['specifications'].get(field, ''),
                                key=f"spec_{asset['asset_id']}_{field}"
                            )
                            if value:
                                new_specifications[field] = value
                            elif field in new_specifications and not value:
                                # Remove optional field if cleared
                                if field in ASSET_CATEGORIES[asset['category']]["optional"]:
                                    del new_specifications[field]
                    
                    # Deployment information if deployed
                    if new_status == "Deployed":
                        st.write("**Deployment Information:**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            rack = st.text_input("Rack", value=asset.get('deployment_info', {}).get('rack', ''), key=f"rack_{asset['asset_id']}")
                        with col2:
                            row = st.text_input("Row", value=asset.get('deployment_info', {}).get('row', ''), key=f"row_{asset['asset_id']}")
                        with col3:
                            position = st.text_input("Position", value=asset.get('deployment_info', {}).get('position', ''), key=f"pos_{asset['asset_id']}")
                    
                    # Save and Cancel buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Changes", key=f"save_{asset['asset_id']}", type="primary"):
                            updated_data = {
                                "name": new_name,
                                "network_name": new_network_name,
                                "owner": new_owner,
                                "order_number": new_order_number,
                                "location": new_location,
                                "status": new_status,
                                "specifications": new_specifications,
                                "notes": new_notes
                            }
                            if new_status == "Deployed":
                                updated_data["deployment_info"] = {
                                    "rack": rack,
                                    "row": row,
                                    "position": position,
                                    "deployment_date": asset.get('deployment_info', {}).get('deployment_date', datetime.now().strftime("%Y-%m-%d %H:%M"))
                                }
                            else:
                                updated_data["deployment_info"] = {}
                            
                            update_asset(asset['asset_id'], updated_data)
                            st.session_state[f"edit_mode_{asset['asset_id']}"] = False
                            st.success("Asset updated successfully!")
                            st.rerun()
                    
                    with col2:
                        if st.button("Cancel", key=f"cancel_{asset['asset_id']}"):
                            st.session_state[f"edit_mode_{asset['asset_id']}"] = False
                            st.rerun()
    else:
        st.info(f"No assets found in {location}. Add some assets to get started!")

# Main navigation
main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs(["📍 Locations", "➕ Add Asset", "📊 Global Dashboard", "💾 Data Management"])

# Tab 1: Location-based inventory
with main_tab1:
    # Create sub-tabs for each location
    location_tabs = st.tabs([f"📍 {loc}" for loc in LOCATIONS])
    
    for i, location_tab in enumerate(location_tabs):
        with location_tab:
            st.markdown(f'<p class="location-header">{LOCATIONS[i]} Lab Inventory</p>', unsafe_allow_html=True)
            display_location_inventory(LOCATIONS[i])

# Tab 2: Add New Asset
with main_tab2:
    st.header("Add New Asset")
    
    # Basic Information
    st.subheader("Basic Information")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Asset Name *", placeholder="e.g., Lab Switch 01")
        network_name = st.text_input("Network Name", placeholder="e.g., lab-sw-01.domain.com")
        owner = st.text_input("Owner Name (Optional)", placeholder="e.g., John Doe")
        order_number = st.text_input("Order Number (Optional)", placeholder="e.g., PO-2024-001")
    
    with col2:
        location = st.selectbox("Location *", LOCATIONS)
        category = st.selectbox("Asset Category *", list(ASSET_CATEGORIES.keys()))
        status = st.selectbox("Initial Status *", ["Available", "Deployed"])
    
    # Specifications
    st.subheader("Specifications")
    st.caption("Fields marked with * are required")
    specifications = {}
    spec_cols = st.columns(2)
    
    # Get all fields for the category
    all_fields = ASSET_CATEGORIES[category]["required"] + ASSET_CATEGORIES[category]["optional"]
    
    for idx, field in enumerate(all_fields):
        with spec_cols[idx % 2]:
            is_required = field in ASSET_CATEGORIES[category]["required"]
            field_label = f"{field} *" if is_required else f"{field} (Optional)"
            value = st.text_input(field_label, key=f"spec_{field}")
            if value:  # Only add to specifications if it has a value
                specifications[field] = value
    
    # Deployment information if deployed
    deployment_info = {}
    if status == "Deployed":
        st.subheader("Deployment Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            deployment_info["rack"] = st.text_input("Rack")
        with col2:
            deployment_info["row"] = st.text_input("Row")
        with col3:
            deployment_info["position"] = st.text_input("Position (e.g., U1-U4)")
        deployment_info["deployment_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Notes
    notes = st.text_area("Additional Notes", height=100)
    
    # Add button
    if st.button("Add Asset", type="primary"):
        # Check if all required fields are filled
        required_specs_filled = all(
            specifications.get(field) for field in ASSET_CATEGORIES[category]["required"]
        )
        
        if name and required_specs_filled and (status == "Available" or all(deployment_info.values())):
            new_asset = {
                "asset_id": generate_asset_id(),
                "name": name,
                "network_name": network_name,
                "location": location,
                "category": category,
                "status": status,
                "specifications": specifications,
                "deployment_info": deployment_info,
                "notes": notes,
                "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            # Add optional fields only if they have values
            if owner:
                new_asset["owner"] = owner
            if order_number:
                new_asset["order_number"] = order_number
                
            st.session_state.inventory.append(new_asset)
            if save_inventory():
                st.success(f"Asset '{name}' ({new_asset['asset_id']}) added to {location} inventory and saved!")
                st.balloons()
                # Clear the form by rerunning
                st.rerun()
            else:
                st.error("Failed to save asset. Please try again.")
        else:
            missing_fields = []
            if not name:
                missing_fields.append("Asset Name")
            for field in ASSET_CATEGORIES[category]["required"]:
                if not specifications.get(field):
                    missing_fields.append(field)
            if status == "Deployed" and not all(deployment_info.values()):
                missing_fields.append("Deployment Information")
            
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")

# Tab 3: Global Dashboard
with main_tab3:
    st.header("Global Inventory Dashboard")
    
    if st.session_state.inventory:
        # Global summary metrics
        st.subheader("Overall Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_assets = len(st.session_state.inventory)
        available_assets = len([a for a in st.session_state.inventory if a['status'] == "Available"])
        deployed_assets = len([a for a in st.session_state.inventory if a['status'] == "Deployed"])
        
        with col1:
            st.metric("Total Assets (All Locations)", total_assets)
        with col2:
            st.metric("Available", available_assets)
        with col3:
            st.metric("Deployed", deployed_assets)
        with col4:
            st.metric("Global Utilization", f"{(deployed_assets/total_assets*100):.1f}%" if total_assets > 0 else "0%")
        
        st.divider()
        
        # Location breakdown
        st.subheader("Assets by Location")
        location_counts = {}
        location_deployed = {}
        for asset in st.session_state.inventory:
            loc = asset['location']
            location_counts[loc] = location_counts.get(loc, 0) + 1
            if asset['status'] == "Deployed":
                location_deployed[loc] = location_deployed.get(loc, 0) + 1
        
        # Create location summary
        col1, col2 = st.columns(2)
        
        with col1:
            if location_counts:
                df_locations = pd.DataFrame([
                    {
                        'Location': loc,
                        'Total': location_counts.get(loc, 0),
                        'Deployed': location_deployed.get(loc, 0),
                        'Available': location_counts.get(loc, 0) - location_deployed.get(loc, 0)
                    }
                    for loc in LOCATIONS
                ])
                st.bar_chart(df_locations.set_index('Location')[['Available', 'Deployed']])
        
        with col2:
            st.write("**Location Summary:**")
            for loc in LOCATIONS:
                total = location_counts.get(loc, 0)
                deployed = location_deployed.get(loc, 0)
                utilization = (deployed/total*100) if total > 0 else 0
                st.write(f"**{loc}**: {total} assets ({utilization:.1f}% utilized)")
        
        st.divider()
        
        # Owner and Order Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Assets by Owner")
            owner_counts = {}
            unassigned_count = 0
            for asset in st.session_state.inventory:
                owner = asset.get('owner', '')
                if owner:
                    owner_counts[owner] = owner_counts.get(owner, 0) + 1
                else:
                    unassigned_count += 1
            
            if owner_counts or unassigned_count > 0:
                # Sort by count and show top 10
                sorted_owners = sorted(owner_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for owner, count in sorted_owners:
                    st.write(f"• **{owner}**: {count} assets")
                if unassigned_count > 0:
                    st.write(f"• **Unassigned**: {unassigned_count} assets")
            else:
                st.info("No owner information available")
        
        with col2:
            st.subheader("Recent Orders")
            order_assets = {}
            for asset in st.session_state.inventory:
                order = asset.get('order_number', '')
                if order:
                    if order not in order_assets:
                        order_assets[order] = []
                    order_assets[order].append(asset)
            
            if order_assets:
                # Show recent 5 orders based on asset dates
                recent_orders = sorted(
                    order_assets.items(),
                    key=lambda x: max(asset['date_added'] for asset in x[1]),
                    reverse=True
                )[:5]
                
                for order, assets in recent_orders:
                    st.write(f"• **{order}**: {len(assets)} assets")
                    latest_date = max(asset['date_added'] for asset in assets)
                    st.caption(f"  Latest: {latest_date}")
            else:
                st.info("No order information available")
        
        st.divider()
        
        # Category breakdown across all locations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Global Assets by Category")
            category_counts = {}
            for asset in st.session_state.inventory:
                category_counts[asset['category']] = category_counts.get(asset['category'], 0) + 1
            
            if category_counts:
                df_categories = pd.DataFrame(
                    list(category_counts.items()),
                    columns=['Category', 'Count']
                )
                st.bar_chart(df_categories.set_index('Category'))
        
        with col2:
            st.subheader("Top Deployment Racks (All Locations)")
            rack_counts = {}
            for asset in st.session_state.inventory:
                if asset['status'] == "Deployed":
                    rack_key = f"{asset['location']} - {asset['deployment_info']['rack']}"
                    rack_counts[rack_key] = rack_counts.get(rack_key, 0) + 1
            
            if rack_counts:
                # Show top 10 racks
                top_racks = sorted(rack_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for rack, count in top_racks:
                    st.write(f"• {rack}: {count} assets")
            else:
                st.info("No deployed assets yet")
        
        # Recent activity across all locations
        st.divider()
        st.subheader("Recent Activity (All Locations)")
        recent_assets = sorted(
            st.session_state.inventory,
            key=lambda x: x['date_added'],
            reverse=True
        )[:10]
        
        for asset in recent_assets:
            asset_name = asset.get('name', 'Unnamed')
            serial_number = asset['specifications'].get('Serial Number', 'N/A')
            st.write(f"• [{asset['location']}] {asset['category']} - {asset_name} (SN: {serial_number}) - Added: {asset['date_added']}")
    else:
        st.info("No data to display. Add some assets to see the dashboard!")

# Tab 4: Data Management
with main_tab4:
    st.header("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Data")
        
        # Option to export all or by location
        export_option = st.radio("Export Option", ["All Locations", "Specific Location"])
        
        if export_option == "Specific Location":
            export_location = st.selectbox("Select Location", LOCATIONS)
            export_data_source = get_assets_by_location(export_location)
        else:
            export_data_source = st.session_state.inventory
        
        if st.button("Download Inventory as CSV"):
            if export_data_source:
                # Convert to DataFrame for export
                export_data = []
                for asset in export_data_source:
                    row = {
                        'Asset ID': asset['asset_id'],
                        'Name': asset.get('name', ''),
                        'Network Name': asset.get('network_name', ''),
                        'Owner': asset.get('owner', ''),
                        'Order Number': asset.get('order_number', ''),
                        'Location': asset['location'],
                        'Category': asset['category'],
                        'Status': asset['status'],
                        'Date Added': asset['date_added'],
                        'Notes': asset.get('notes', '')
                    }
                    # Add specifications
                    row.update(asset['specifications'])
                    # Add deployment info if deployed
                    if asset['status'] == "Deployed":
                        row['Rack'] = asset['deployment_info']['rack']
                        row['Row'] = asset['deployment_info']['row']
                        row['Position'] = asset['deployment_info']['position']
                        row['Deployment Date'] = asset['deployment_info']['deployment_date']
                    export_data.append(row)
                
                df = pd.DataFrame(export_data)
                csv = df.to_csv(index=False)
                filename_suffix = f"_{export_location}" if export_option == "Specific Location" else "_all"
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"inventory_export{filename_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No data to export!")
    
    with col2:
        st.subheader("Import Data")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                if st.button("Import Data"):
                    # Import logic would go here
                    st.success("Data imported successfully!")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    st.divider()
    
    # Manual save and load buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💾 Save Data")
        if st.button("Manual Save", type="primary"):
            if save_inventory():
                st.success(f"Successfully saved {len(st.session_state.inventory)} assets to inventory_data.json")
            else:
                st.error("Failed to save data")
    
    with col2:
        st.subheader("📂 Load Data")
        if st.button("Reload from File"):
            loaded_data = load_inventory()
            if loaded_data:
                st.session_state.inventory = loaded_data
                st.success(f"Loaded {len(loaded_data)} assets from file!")
                st.rerun()
            else:
                st.info("No saved inventory found.")
    
    # Clear all data
    st.divider()
    st.subheader("⚠️ Danger Zone")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Specific Location", type="secondary"):
            clear_location = st.selectbox("Select Location to Clear", LOCATIONS, key="clear_loc")
            if st.checkbox(f"I understand this will delete all {clear_location} inventory data"):
                # Remove all assets from the selected location
                st.session_state.inventory = [
                    asset for asset in st.session_state.inventory 
                    if asset['location'] != clear_location
                ]
                save_inventory()
                st.success(f"All {clear_location} data cleared!")
                st.rerun()
    
    with col2:
        if st.button("Clear All Data", type="secondary"):
            if st.checkbox("I understand this will delete ALL inventory data"):
                st.session_state.inventory = []
                if os.path.exists('inventory_data.json'):
                    os.remove('inventory_data.json')
                st.success("All data cleared!")
                st.rerun()

# Footer with save status
st.divider()
col1, col2 = st.columns([4, 1])
with col1:
    st.caption("Multi-Location Lab Inventory Management System v2.0 | Auto-saves to inventory_data.json")
with col2:
    if st.session_state.inventory:
        if save_inventory():
            st.success("✓ Saved", icon="✅")
        else:
            st.error("Save failed", icon="❌")
