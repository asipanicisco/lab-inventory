import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os

# Helper functions - Define these first before using them
import random
import string

def generate_asset_id():
    """Generate unique asset ID with timestamp and random suffix"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # Add microseconds and random string for uniqueness
    microseconds = datetime.now().microsecond
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"AST-{timestamp}-{microseconds:06d}-{random_suffix}"

# Initialize session state for data persistence
if 'inventory' not in st.session_state:
    # Try to load existing data on startup
    if os.path.exists('inventory_data.json'):
        try:
            with open('inventory_data.json', 'r') as f:
                data = f.read()
                # Fix NaN values in JSON
                data = data.replace('"asset_id": NaN', '"asset_id": null')
                data = data.replace(': NaN', ': null')  # Fix any NaN values
                inventory_data = json.loads(data)
                # Fix null asset_ids and dates
                for item in inventory_data:
                    if item.get('asset_id') is None or str(item.get('asset_id')) == 'NaN' or str(item.get('asset_id')) == 'nan':
                        item['asset_id'] = generate_asset_id()
                    if item.get('date_added') is None or str(item.get('date_added')) == 'NaN' or str(item.get('date_added')) == 'nan':
                        item['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.inventory = inventory_data
        except Exception as e:
            st.error(f"Error loading inventory: {e}")
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

def save_inventory():
    """Save inventory to JSON file"""
    try:
        # Clean up any NaN values before saving
        cleaned_inventory = []
        for asset in st.session_state.inventory:
            cleaned_asset = asset.copy()
            # Fix asset_id if it's NaN
            if cleaned_asset.get('asset_id') is None or str(cleaned_asset.get('asset_id')) in ['NaN', 'nan', 'null', '']:
                cleaned_asset['asset_id'] = generate_asset_id()
            # Fix date_added if it's NaN
            if cleaned_asset.get('date_added') is None or str(cleaned_asset.get('date_added')) in ['NaN', 'nan', 'null', '']:
                cleaned_asset['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            cleaned_inventory.append(cleaned_asset)
        
        with open('inventory_data.json', 'w') as f:
            json.dump(cleaned_inventory, f, indent=2)
        
        # Update session state with cleaned data
        st.session_state.inventory = cleaned_inventory
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def load_inventory():
    """Load inventory from JSON file"""
    if os.path.exists('inventory_data.json'):
        try:
            with open('inventory_data.json', 'r') as f:
                data = f.read()
                # Fix NaN values in JSON
                data = data.replace('"asset_id": NaN', '"asset_id": null')
                data = data.replace(': NaN', ': null')  # Fix any NaN values
                inventory_data = json.loads(data)
                # Fix null asset_ids and dates
                for item in inventory_data:
                    if item.get('asset_id') is None or str(item.get('asset_id')) in ['NaN', 'nan', 'null', '']:
                        item['asset_id'] = generate_asset_id()
                    if item.get('date_added') is None or str(item.get('date_added')) in ['NaN', 'nan', 'null', '']:
                        item['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                return inventory_data
        except Exception as e:
            st.error(f"Error in load_inventory: {e}")
            return []
    return []

def get_asset_by_id(asset_id):
    """Get asset by ID"""
    for asset in st.session_state.inventory:
        if asset['asset_id'] == asset_id:
            return asset
    return None

def get_asset_by_serial(serial_number, category=None):
    """Get asset by serial number, optionally filtered by category"""
    if not serial_number:
        return None
    
    for asset in st.session_state.inventory:
        asset_serial = asset.get('specifications', {}).get('Serial Number', '')
        if asset_serial and asset_serial.strip().upper() == serial_number.strip().upper():
            if category is None or asset.get('category') == category:
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
                                    ["All", "Available", "Deployed", "Loaned"],
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
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_assets = len(location_inventory)
    available_assets = len([a for a in location_inventory if a['status'] == "Available"])
    deployed_assets = len([a for a in location_inventory if a['status'] == "Deployed"])
    loaned_assets = len([a for a in location_inventory if a['status'] == "Loaned"])
    
    with col1:
        st.metric("Total Assets", total_assets)
    with col2:
        st.metric("Available", available_assets)
    with col3:
        st.metric("Deployed", deployed_assets)
    with col4:
        st.metric("Loaned", loaned_assets)
    with col5:
        in_use = deployed_assets + loaned_assets
        st.metric("Utilization", f"{(in_use/total_assets*100):.1f}%" if total_assets > 0 else "0%")
    
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
                    elif asset['status'] == "Loaned":
                        st.write("**Loan Info:**")
                        loan_info = asset.get('loan_info', {})
                        st.write(f"Loaned to: {loan_info.get('loaned_to', 'N/A')}")
                        st.write(f"Purpose: {loan_info.get('purpose', 'N/A')}")
                        st.write(f"Loan date: {loan_info.get('loan_date', 'N/A')}")
                        if loan_info.get('expected_return'):
                            st.write(f"Expected return: {loan_info.get('expected_return')}")
                    
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
                        status_options = ["Available", "Deployed", "Loaned"]
                        current_status_index = status_options.index(asset['status']) if asset['status'] in status_options else 0
                        new_status = st.selectbox(
                            "Status", 
                            status_options,
                            index=current_status_index,
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
                    
                    # Loan information if loaned
                    elif new_status == "Loaned":
                        st.write("**Loan Information:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            loaned_to = st.text_input("Loaned To", value=asset.get('loan_info', {}).get('loaned_to', ''), key=f"loaned_to_{asset['asset_id']}")
                            purpose = st.text_input("Purpose", value=asset.get('loan_info', {}).get('purpose', ''), key=f"purpose_{asset['asset_id']}")
                        with col2:
                            loan_date = st.date_input("Loan Date", value=datetime.now(), key=f"loan_date_{asset['asset_id']}")
                            expected_return = st.date_input("Expected Return Date (Optional)", value=None, key=f"expected_return_{asset['asset_id']}")
                    
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
                                updated_data["loan_info"] = {}
                            elif new_status == "Loaned":
                                updated_data["loan_info"] = {
                                    "loaned_to": loaned_to,
                                    "purpose": purpose,
                                    "loan_date": loan_date.strftime("%Y-%m-%d"),
                                    "expected_return": expected_return.strftime("%Y-%m-%d") if expected_return else ""
                                }
                                updated_data["deployment_info"] = {}
                            else:
                                updated_data["deployment_info"] = {}
                                updated_data["loan_info"] = {}
                            
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
        status = st.selectbox("Initial Status *", ["Available", "Deployed", "Loaned"])
    
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
    loan_info = {}
    
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
    elif status == "Loaned":
        st.subheader("Loan Information")
        col1, col2 = st.columns(2)
        with col1:
            loan_info["loaned_to"] = st.text_input("Loaned To *")
            loan_info["purpose"] = st.text_input("Purpose *")
        with col2:
            loan_info["loan_date"] = st.date_input("Loan Date").strftime("%Y-%m-%d")
            expected_return = st.date_input("Expected Return Date (Optional)", value=None)
            if expected_return:
                loan_info["expected_return"] = expected_return.strftime("%Y-%m-%d")
    
    # Notes
    notes = st.text_area("Additional Notes", height=100)
    
    # Add button
    if st.button("Add Asset", type="primary"):
        # Check if all required fields are filled
        required_specs_filled = all(
            specifications.get(field) for field in ASSET_CATEGORIES[category]["required"]
        )
        
        valid_submission = False
        if status == "Available":
            valid_submission = name and required_specs_filled
        elif status == "Deployed":
            valid_submission = name and required_specs_filled and all(deployment_info.values())
        elif status == "Loaned":
            valid_submission = name and required_specs_filled and loan_info.get("loaned_to") and loan_info.get("purpose")
        
        if valid_submission:
            new_asset = {
                "asset_id": generate_asset_id(),
                "name": name,
                "network_name": network_name,
                "location": location,
                "category": category,
                "status": status,
                "specifications": specifications,
                "deployment_info": deployment_info,
                "loan_info": loan_info,
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
            if status == "Loaned":
                if not loan_info.get("loaned_to"):
                    missing_fields.append("Loaned To")
                if not loan_info.get("purpose"):
                    missing_fields.append("Purpose")
            
            st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")

# Tab 3: Global Dashboard
with main_tab3:
    st.header("Global Inventory Dashboard")
    
    if st.session_state.inventory:
        # Global summary metrics
        st.subheader("Overall Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_assets = len(st.session_state.inventory)
        available_assets = len([a for a in st.session_state.inventory if a['status'] == "Available"])
        deployed_assets = len([a for a in st.session_state.inventory if a['status'] == "Deployed"])
        loaned_assets = len([a for a in st.session_state.inventory if a['status'] == "Loaned"])
        in_use_assets = deployed_assets + loaned_assets
        
        with col1:
            st.metric("Total Assets (All Locations)", total_assets)
        with col2:
            st.metric("Available", available_assets)
        with col3:
            st.metric("Deployed", deployed_assets)
        with col4:
            st.metric("Loaned", loaned_assets)
        with col5:
            st.metric("Global Utilization", f"{(in_use_assets/total_assets*100):.1f}%" if total_assets > 0 else "0%")
        
        st.divider()
        
        # Location breakdown
        st.subheader("Assets by Location")
        location_counts = {}
        location_deployed = {}
        location_loaned = {}
        for asset in st.session_state.inventory:
            loc = asset['location']
            location_counts[loc] = location_counts.get(loc, 0) + 1
            if asset['status'] == "Deployed":
                location_deployed[loc] = location_deployed.get(loc, 0) + 1
            elif asset['status'] == "Loaned":
                location_loaned[loc] = location_loaned.get(loc, 0) + 1
        
        # Create location summary
        col1, col2 = st.columns(2)
        
        with col1:
            if location_counts:
                df_locations = pd.DataFrame([
                    {
                        'Location': loc,
                        'Total': location_counts.get(loc, 0),
                        'Available': location_counts.get(loc, 0) - location_deployed.get(loc, 0) - location_loaned.get(loc, 0),
                        'Deployed': location_deployed.get(loc, 0),
                        'Loaned': location_loaned.get(loc, 0)
                    }
                    for loc in LOCATIONS
                ])
                st.bar_chart(df_locations.set_index('Location')[['Available', 'Deployed', 'Loaned']])
        
        with col2:
            st.write("**Location Summary:**")
            for loc in LOCATIONS:
                total = location_counts.get(loc, 0)
                deployed = location_deployed.get(loc, 0)
                loaned = location_loaned.get(loc, 0)
                in_use = deployed + loaned
                utilization = (in_use/total*100) if total > 0 else 0
                st.write(f"**{loc}**: {total} assets ({utilization:.1f}% utilized)")
                st.caption(f"  Available: {total - in_use}, Deployed: {deployed}, Loaned: {loaned}")
        
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
            st.subheader("Active Loans")
            active_loans = [asset for asset in st.session_state.inventory if asset['status'] == "Loaned"]
            
            if active_loans:
                # Sort by loan date
                active_loans.sort(key=lambda x: x.get('loan_info', {}).get('loan_date', ''), reverse=True)
                
                for loan in active_loans[:10]:  # Show top 10 recent loans
                    loan_info = loan.get('loan_info', {})
                    asset_name = loan.get('name', 'Unnamed')
                    st.write(f"• **{asset_name}** → {loan_info.get('loaned_to', 'Unknown')}")
                    st.caption(f"  {loan['location']} | Since: {loan_info.get('loan_date', 'N/A')}")
                    if loan_info.get('expected_return'):
                        st.caption(f"  Expected return: {loan_info.get('expected_return')}")
            else:
                st.info("No active loans")
        
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
            status_emoji = "🟢" if asset['status'] == "Available" else "🔵" if asset['status'] == "Deployed" else "🟡"
            st.write(f"{status_emoji} [{asset['location']}] {asset['category']} - {asset_name} (SN: {serial_number}) - Added: {asset['date_added']}")
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
                    # Add loan info if loaned
                    elif asset['status'] == "Loaned":
                        row['Loaned To'] = asset.get('loan_info', {}).get('loaned_to', '')
                        row['Loan Purpose'] = asset.get('loan_info', {}).get('purpose', '')
                        row['Loan Date'] = asset.get('loan_info', {}).get('loan_date', '')
                        row['Expected Return'] = asset.get('loan_info', {}).get('expected_return', '')
                    
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
                    # Show column mapping helper
                    st.info("📋 CSV Import Started...")
                    
                    # Display the columns found in the CSV
                    st.write("**Columns found in your CSV:**")
                    st.write(", ".join(df.columns.tolist()))
                    
                    # Import logic implementation
                    imported_count = 0
                    updated_count = 0
                    skipped_count = 0
                    duplicate_count = 0
                    errors = []
                    duplicates = []
                    
                    # Create a progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    total_rows = len(df)
                    
                    for index, row in df.iterrows():
                        # Update progress
                        progress = (index + 1) / total_rows
                        progress_bar.progress(progress)
                        status_text.text(f'Processing row {index + 1} of {total_rows}...')
                        
                        try:
                            # Skip empty rows
                            if row.isna().all():
                                skipped_count += 1
                                continue
                            
                            # Extract base fields - handle different possible column names
                            csv_asset_id = None
                            if 'Asset ID' in row and pd.notna(row['Asset ID']):
                                csv_asset_id = str(row['Asset ID']).strip()
                                if csv_asset_id in ['NaN', 'nan', '', 'None']:
                                    csv_asset_id = None
                            
                            # Get name - this is critical
                            name = ''
                            if 'Name' in row and pd.notna(row['Name']):
                                name = str(row['Name']).strip()
                            
                            # Skip if no name
                            if not name:
                                errors.append(f"Row {index + 2} (Excel row): No name provided - skipping")
                                skipped_count += 1
                                continue
                            
                            # Get other fields with defaults
                            location = LOCATIONS[0]  # Default location
                            if 'Location' in row and pd.notna(row['Location']):
                                loc_value = str(row['Location']).strip().upper()
                                if loc_value in LOCATIONS:
                                    location = loc_value
                                else:
                                    errors.append(f"Row {index + 2}: Invalid location '{loc_value}', using default '{location}'")
                            
                            category = list(ASSET_CATEGORIES.keys())[0]  # Default category
                            if 'Category' in row and pd.notna(row['Category']):
                                cat_value = str(row['Category']).strip()
                                if cat_value in ASSET_CATEGORIES:
                                    category = cat_value
                                else:
                                    errors.append(f"Row {index + 2}: Invalid category '{cat_value}', using default '{category}'")
                            
                            status = 'Available'  # Default status
                            if 'Status' in row and pd.notna(row['Status']):
                                status_value = str(row['Status']).strip()
                                if status_value in ['Available', 'Deployed', 'Loaned']:
                                    status = status_value
                            
                            # Build specifications based on category
                            specifications = {}
                            serial_number = None
                            
                            if category in ASSET_CATEGORIES:
                                # First check for required fields
                                missing_required = []
                                for field in ASSET_CATEGORIES[category]["required"]:
                                    if field in row and pd.notna(row[field]):
                                        field_value = str(row[field]).strip()
                                        specifications[field] = field_value
                                        if field == "Serial Number":
                                            serial_number = field_value
                                    else:
                                        missing_required.append(field)
                                
                                # Warn about missing required fields but continue
                                if missing_required:
                                    errors.append(f"Row {index + 2}: Missing required fields for {category}: {', '.join(missing_required)}")
                                
                                # Add optional fields
                                for field in ASSET_CATEGORIES[category]["optional"]:
                                    if field in row and pd.notna(row[field]):
                                        specifications[field] = str(row[field]).strip()
                            
                            # Determine what to do with this asset
                            action = None
                            existing_asset = None
                            asset_id = None
                            
                            # First priority: Check by serial number
                            if serial_number:
                                existing_asset = get_asset_by_serial(serial_number, category)
                                if existing_asset:
                                    # Found by serial number
                                    if csv_asset_id and csv_asset_id == existing_asset.get('asset_id'):
                                        # Same ID and serial - this is an update
                                        action = 'update'
                                        asset_id = csv_asset_id
                                    else:
                                        # Different ID but same serial - this is a duplicate
                                        action = 'duplicate'
                                        duplicates.append({
                                            'row': index + 2,
                                            'name': name,
                                            'serial': serial_number,
                                            'category': category,
                                            'existing_name': existing_asset.get('name', 'Unknown'),
                                            'existing_location': existing_asset.get('location', 'Unknown'),
                                            'existing_id': existing_asset.get('asset_id', 'Unknown')
                                        })
                                        duplicate_count += 1
                                        continue
                                else:
                                    # Serial number not found - new asset
                                    action = 'new'
                                    asset_id = csv_asset_id if csv_asset_id else generate_asset_id()
                            else:
                                # No serial number - check by ID only
                                if csv_asset_id:
                                    existing_asset = get_asset_by_id(csv_asset_id)
                                    if existing_asset:
                                        action = 'update'
                                        asset_id = csv_asset_id
                                    else:
                                        action = 'new'
                                        asset_id = csv_asset_id
                                else:
                                    # No ID and no serial - definitely new
                                    action = 'new'
                                    asset_id = generate_asset_id()
                            
                            # Build deployment info if status is Deployed
                            deployment_info = {}
                            if status == "Deployed":
                                deployment_info = {
                                    "rack": str(row.get('Rack', '')).strip() if 'Rack' in row and pd.notna(row.get('Rack')) else '',
                                    "row": str(row.get('Row', '')).strip() if 'Row' in row and pd.notna(row.get('Row')) else '',
                                    "position": str(row.get('Position', '')).strip() if 'Position' in row and pd.notna(row.get('Position')) else '',
                                    "deployment_date": str(row.get('Deployment Date', datetime.now().strftime("%Y-%m-%d %H:%M")))
                                }
                            
                            # Build loan info if status is Loaned
                            loan_info = {}
                            if status == "Loaned":
                                loan_info = {
                                    "loaned_to": str(row.get('Loaned To', '')).strip() if 'Loaned To' in row and pd.notna(row.get('Loaned To')) else '',
                                    "purpose": str(row.get('Loan Purpose', '')).strip() if 'Loan Purpose' in row and pd.notna(row.get('Loan Purpose')) else '',
                                    "loan_date": str(row.get('Loan Date', datetime.now().strftime("%Y-%m-%d"))),
                                    "expected_return": str(row.get('Expected Return', '')).strip() if 'Expected Return' in row and pd.notna(row.get('Expected Return')) else ''
                                }
                            
                            # Build asset
                            new_asset = {
                                "asset_id": asset_id,
                                "name": name,
                                "network_name": str(row.get('Network Name', '')).strip() if 'Network Name' in row and pd.notna(row.get('Network Name')) else '',
                                "location": location,
                                "category": category,
                                "status": status,
                                "specifications": specifications,
                                "deployment_info": deployment_info,
                                "loan_info": loan_info,
                                "notes": str(row.get('Notes', '')).strip() if 'Notes' in row and pd.notna(row.get('Notes')) else '',
                                "date_added": str(row.get('Date Added', datetime.now().strftime("%Y-%m-%d %H:%M")))
                            }
                            
                            # Add optional fields if present
                            if 'Owner' in row and pd.notna(row['Owner']):
                                new_asset["owner"] = str(row['Owner']).strip()
                            if 'Order Number' in row and pd.notna(row['Order Number']):
                                new_asset["order_number"] = str(row['Order Number']).strip()
                            
                            # Perform the action
                            if action == 'update':
                                # Update existing asset
                                for i, asset in enumerate(st.session_state.inventory):
                                    if asset['asset_id'] == asset_id:
                                        st.session_state.inventory[i] = new_asset
                                        updated_count += 1
                                        break
                            elif action == 'new':
                                # Add new asset
                                st.session_state.inventory.append(new_asset)
                                imported_count += 1
                            
                        except Exception as e:
                            errors.append(f"Row {index + 2} (Excel row): {str(e)}")
                            import traceback
                            errors.append(f"  Details: {traceback.format_exc()}")
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Save after import
                    save_inventory()
                    
                    # Show detailed results
                    st.write("---")
                    st.write("**Import Summary:**")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Total Rows", total_rows)
                    with col2:
                        st.metric("Imported", imported_count)
                    with col3:
                        st.metric("Updated", updated_count) 
                    with col4:
                        st.metric("Skipped", skipped_count)
                    with col5:
                        st.metric("Duplicates", duplicate_count)
                    
                    # Show duplicate details if any
                    if duplicates:
                        st.error(f"⚠️ {duplicate_count} duplicate serial numbers found and skipped:")
                        with st.expander("View Duplicate Details", expanded=True):
                            for dup in duplicates:
                                st.write(f"**Row {dup['row']}**: {dup['name']} (Serial: {dup['serial']})")
                                st.caption(f"Already exists as: {dup['existing_name']} in {dup['existing_location']} (ID: {dup['existing_id']})")
                    
                    if imported_count > 0 or updated_count > 0:
                        success_msg = []
                        if imported_count > 0:
                            success_msg.append(f"{imported_count} new assets imported")
                        if updated_count > 0:
                            success_msg.append(f"{updated_count} existing assets updated")
                        st.success(f"✅ Success: {' and '.join(success_msg)}!")
                        
                        if errors:
                            with st.expander(f"⚠️ Warnings/Errors ({len(errors)} issues)", expanded=False):
                                for error in errors:
                                    st.text(error)
                        
                        if st.button("Refresh Page"):
                            st.rerun()
                    else:
                        st.error(f"❌ No assets were imported from {total_rows} rows.")
                        if errors:
                            st.warning("**Errors encountered:**")
                            for error in errors[:10]:  # Show first 10 errors
                                st.text(error)
                            if len(errors) > 10:
                                st.text(f"... and {len(errors) - 10} more errors")
                        
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
    st.caption("Multi-Location Lab Inventory Management System v2.1 | Auto-saves to inventory_data.json")
with col2:
    if st.session_state.inventory:
        if save_inventory():
            st.success("✓ Saved", icon="✅")
        else:
            st.error("Save failed", icon="❌")
