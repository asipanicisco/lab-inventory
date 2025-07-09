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
                    if item.get('asset_id') is None or str(item.get('asset_id')) in ['NaN', 'nan', 'null', '']:
                        item['asset_id'] = generate_asset_id()
                    if item.get('date_added') is None or str(item.get('date_added')) in ['NaN', 'nan', 'null', '']:
                        item['date_added'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.inventory = inventory_data
        except Exception as e:
            st.error(f"Error loading inventory: {e}")
            st.session_state.inventory = []
    else:
        st.session_state.inventory = []

# Initialize accessories inventory
if 'accessories_inventory' not in st.session_state:
    if os.path.exists('accessories_inventory.json'):
        try:
            with open('accessories_inventory.json', 'r') as f:
                st.session_state.accessories_inventory = json.load(f)
        except:
            st.session_state.accessories_inventory = []
    else:
        st.session_state.accessories_inventory = []

# Define locations
LOCATIONS = ["SF", "SJ", "RTP", "BGL"]

# Accessory categories for bulk tracking
ACCESSORY_CATEGORIES = {
    "SFP/Optics": ["GLC-TE", "GLC-SX-MM", "GLC-LH-SM", "SFP-10G-SR", "SFP-10G-LR", "QSFP-40G-SR4", "Other"],
    "Stack Cables": ["STACK-T1-50CM", "STACK-T1-1M", "STACK-T1-3M", "STACK-T2-50CM", "STACK-T2-1M", "STACK-T2-3M", "Other"],
    "Network Modules": ["C9300-NM-8X", "C9300-NM-4G", "C9300-NM-2Q", "C3850-NM-4-1G", "C3850-NM-2-10G", "Other"],
    "Power Cables": ["CAB-C13-C14-2M", "CAB-C13-C14-6FT", "CAB-C15-C14-10FT", "Other"],
    "Console Cables": ["CAB-CONSOLE-RJ45", "CAB-CONSOLE-USB", "Other"],
    "Ethernet Cables": ["CAT5E-1FT", "CAT5E-3FT", "CAT5E-5FT", "CAT5E-7FT", "CAT5E-10FT", "CAT5E-15FT", "CAT5E-25FT", "CAT6-1FT", "CAT6-3FT", "CAT6-5FT", "CAT6-7FT", "CAT6-10FT", "CAT6-15FT", "CAT6-25FT", "CAT6A-1FT", "CAT6A-3FT", "CAT6A-5FT", "CAT6A-10FT", "Other"],
    "Fiber Cables": ["LC-LC-SM-1M", "LC-LC-SM-3M", "LC-LC-SM-5M", "LC-LC-SM-10M", "LC-LC-MM-1M", "LC-LC-MM-3M", "LC-LC-MM-5M", "LC-LC-MM-10M", "LC-SC-SM-1M", "LC-SC-SM-3M", "LC-SC-MM-1M", "LC-SC-MM-3M", "MPO-MPO-12F-1M", "MPO-MPO-12F-3M", "MPO-MPO-12F-5M", "Other"],
    "Power Supplies (PSU)": ["PWR-C1-350WAC", "PWR-C1-715WAC", "PWR-C1-1100WAC", "PWR-C2-250WAC", "PWR-C2-640WAC", "PWR-C2-1025WAC", "PWR-C3-750WAC-R", "PWR-C4-950WAC-R", "PWR-C5-1KWAC", "PWR-C6-600WAC", "C3KX-PWR-350WAC", "C3KX-PWR-715WAC", "C3KX-PWR-1100WAC", "Other"]
}

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

def save_accessories_inventory():
    """Save accessories inventory to JSON file"""
    try:
        with open('accessories_inventory.json', 'w') as f:
            json.dump(st.session_state.accessories_inventory, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving accessories data: {e}")
        return False

def get_accessory_by_id(accessory_id):
    """Get accessory by ID"""
    for acc in st.session_state.accessories_inventory:
        if acc['accessory_id'] == accessory_id:
            return acc
    return None

def update_accessory_count(accessory_id, location, new_count):
    """Update accessory count for a specific location"""
    for acc in st.session_state.accessories_inventory:
        if acc['accessory_id'] == accessory_id:
            acc['quantities'][location] = new_count
            acc['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_accessories_inventory()
            return True
    return False

def get_assets_by_location(location):
    """Get all assets for a specific location"""
    return [asset for asset in st.session_state.inventory if asset.get('location') == location]

def display_location_inventory(location):
    """Display inventory for a specific location"""
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
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
    
    # Get unique teams for this location
    teams = ["All"] + sorted(list(set(asset.get('team', '') for asset in location_assets if asset.get('team', ''))))
    
    with col4:
        filter_team = st.selectbox(f"Filter by team",
                                  teams,
                                  key=f"team_{location}")
    
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
    
    if filter_team != "All":
        filtered_inventory = [
            asset for asset in filtered_inventory
            if asset.get('team', '') == filter_team
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
                display_cols = st.columns([2, 2, 1])
                
                with display_cols[0]:
                    st.write("**Basic Information:**")
                    st.write(f"Name: {asset_name}")
                    st.write(f"Network Name: {asset.get('network_name', 'N/A')}")
                    if asset.get('owner'):
                        st.write(f"Owner: {asset.get('owner')}")
                    if asset.get('team'):
                        st.write(f"Team: {asset.get('team')}")
                    if asset.get('order_number'):
                        st.write(f"Order Number: {asset.get('order_number')}")
                    if asset.get('tracking_number'):
                        st.write(f"Tracking Number: {asset.get('tracking_number')}")
                    st.write(f"Location: {asset['location']}")
                    st.write(f"Category: {asset['category']}")
                    st.write(f"Asset ID: {asset['asset_id']}")
                    st.write(f"Status: {asset['status']}")
                    st.write(f"Added: {asset['date_added']}")
                
                with display_cols[1]:
                    st.write("**Specifications:**")
                    for key, value in asset['specifications'].items():
                        st.write(f"{key}: {value}")
                
                with display_cols[2]:
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
                    edit_cols = st.columns(2)
                    with edit_cols[0]:
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
                        new_team = st.text_input(
                            "Team Name",
                            value=asset.get('team', ''),
                            key=f"team_{asset['asset_id']}"
                        )
                        new_order_number = st.text_input(
                            "Order Number",
                            value=asset.get('order_number', ''),
                            key=f"order_{asset['asset_id']}"
                        )
                        new_tracking_number = st.text_input(
                            "Tracking Number",
                            value=asset.get('tracking_number', ''),
                            key=f"tracking_{asset['asset_id']}"
                        )
                    with edit_cols[1]:
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
                        deploy_cols = st.columns(3)
                        with deploy_cols[0]:
                            rack = st.text_input("Rack", value=asset.get('deployment_info', {}).get('rack', ''), key=f"rack_{asset['asset_id']}")
                        with deploy_cols[1]:
                            row = st.text_input("Row", value=asset.get('deployment_info', {}).get('row', ''), key=f"row_{asset['asset_id']}")
                        with deploy_cols[2]:
                            position = st.text_input("Position", value=asset.get('deployment_info', {}).get('position', ''), key=f"pos_{asset['asset_id']}")
                    
                    # Loan information if loaned
                    elif new_status == "Loaned":
                        st.write("**Loan Information:**")
                        loan_cols = st.columns(2)
                        with loan_cols[0]:
                            loaned_to = st.text_input("Loaned To", value=asset.get('loan_info', {}).get('loaned_to', ''), key=f"loaned_to_{asset['asset_id']}")
                            purpose = st.text_input("Purpose", value=asset.get('loan_info', {}).get('purpose', ''), key=f"purpose_{asset['asset_id']}")
                        with loan_cols[1]:
                            loan_date = st.date_input("Loan Date", value=datetime.now(), key=f"loan_date_{asset['asset_id']}")
                            expected_return = st.date_input("Expected Return Date (Optional)", value=None, key=f"expected_return_{asset['asset_id']}")
                    
                    # Save and Cancel buttons
                    button_cols = st.columns(2)
                    with button_cols[0]:
                        if st.button("Save Changes", key=f"save_{asset['asset_id']}", type="primary"):
                            updated_data = {
                                "name": new_name,
                                "network_name": new_network_name,
                                "owner": new_owner,
                                "team": new_team,
                                "order_number": new_order_number,
                                "tracking_number": new_tracking_number,
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
                    
                    with button_cols[1]:
                        if st.button("Cancel", key=f"cancel_{asset['asset_id']}"):
                            st.session_state[f"edit_mode_{asset['asset_id']}"] = False
                            st.rerun()
    else:
        st.info(f"No assets found in {location}. Add some assets to get started!")

# Main navigation
main_tab1, main_tab2, main_tab3, main_tab4, main_tab5, main_tab6 = st.tabs(["📍 Locations", "➕ Add Asset", "📦 Accessories", "📊 Global Dashboard", "🔧 Bulk Edit", "💾 Data Management"])

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
        team = st.text_input("Team Name (Optional)", placeholder="e.g., Network Team, DevOps")
        order_number = st.text_input("Order Number (Optional)", placeholder="e.g., PO-2024-001")
        tracking_number = st.text_input("Tracking Number (Optional)", placeholder="e.g., 1Z999AA1012345678")
    
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
            if team:
                new_asset["team"] = team
            if order_number:
                new_asset["order_number"] = order_number
            if tracking_number:
                new_asset["tracking_number"] = tracking_number
                
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

# Tab 3: Accessories Bulk Tracking
with main_tab3:
    st.header("📦 Accessories Inventory (Bulk Tracking)")
    st.markdown("Track quantities of accessories without individual serial numbers")
    
    # Sub-tabs for management
    acc_tab1, acc_tab2, acc_tab3 = st.tabs(["📊 View Inventory", "➕ Add New Item", "📥 Quick Update"])
    
    # View Inventory Tab
    with acc_tab1:
        # Filter options
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            search_acc = st.text_input("🔍 Search accessories", placeholder="Search by model, description...")
        with col2:
            filter_category = st.selectbox("Filter by category", ["All"] + list(ACCESSORY_CATEGORIES.keys()))
        with col3:
            filter_location = st.selectbox("Filter by location", ["All Locations"] + LOCATIONS)
        
        # Get unique teams from accessories
        acc_teams = ["All"] + sorted(list(set(acc.get('team', '') for acc in st.session_state.accessories_inventory if acc.get('team', ''))))
        with col4:
            filter_acc_team = st.selectbox("Filter by team", acc_teams, key="acc_team_filter")
        
        # Display accessories
        filtered_accessories = st.session_state.accessories_inventory
        
        # Apply filters
        if search_acc:
            filtered_accessories = [
                acc for acc in filtered_accessories
                if search_acc.lower() in acc['model'].lower() or 
                   search_acc.lower() in acc.get('description', '').lower()
            ]
        
        if filter_category != "All":
            filtered_accessories = [
                acc for acc in filtered_accessories
                if acc['category'] == filter_category
            ]
        
        if filter_acc_team != "All":
            filtered_accessories = [
                acc for acc in filtered_accessories
                if acc.get('team', '') == filter_acc_team
            ]
        
        if filtered_accessories:
            # Group by category
            categories = {}
            for acc in filtered_accessories:
                if acc['category'] not in categories:
                    categories[acc['category']] = []
                categories[acc['category']].append(acc)
            
            # Display by category
            for category, items in categories.items():
                st.subheader(f"{category}")
                
                # Create a table-like display
                for item in items:
                    with st.expander(f"{item['model']} - {item.get('description', 'No description')}", expanded=False):
                        col1, col2 = st.columns([2, 3])
                        
                        with col1:
                            st.write("**Details:**")
                            st.write(f"Model: {item['model']}")
                            st.write(f"Part Number: {item.get('part_number', 'N/A')}")
                            st.write(f"Description: {item.get('description', 'N/A')}")
                            if item.get('team'):
                                st.write(f"Team: {item.get('team')}")
                            st.write(f"Unit Price: ${item.get('unit_price', 0):.2f}")
                            st.write(f"Last Updated: {item.get('last_updated', 'N/A')}")
                        
                        with col2:
                            st.write("**Quantities by Location:**")
                            
                            # Show quantities in a grid
                            q_cols = st.columns(len(LOCATIONS))
                            total_qty = 0
                            
                            for idx, loc in enumerate(LOCATIONS):
                                with q_cols[idx]:
                                    qty = item['quantities'].get(loc, 0)
                                    total_qty += qty
                                    
                                    if filter_location == "All Locations" or filter_location == loc:
                                        st.metric(loc, qty)
                            
                            st.write(f"**Total Quantity: {total_qty}**")
                            
                            # Quick update form
                            st.write("---")
                            st.write("**Quick Update:**")
                            update_col1, update_col2, update_col3 = st.columns([1, 1, 1])
                            
                            with update_col1:
                                update_loc = st.selectbox(
                                    "Location",
                                    LOCATIONS,
                                    key=f"update_loc_{item['accessory_id']}"
                                )
                            
                            with update_col2:
                                current_qty = item['quantities'].get(update_loc, 0)
                                new_qty = st.number_input(
                                    "New Quantity",
                                    min_value=0,
                                    value=current_qty,
                                    key=f"new_qty_{item['accessory_id']}"
                                )
                            
                            with update_col3:
                                st.write(" ")  # Spacer
                                if st.button("Update", key=f"update_btn_{item['accessory_id']}"):
                                    if update_accessory_count(item['accessory_id'], update_loc, new_qty):
                                        st.success(f"Updated {update_loc} quantity to {new_qty}")
                                        st.rerun()
        else:
            st.info("No accessories found. Add some items to get started!")
    
    # Add New Item Tab
    with acc_tab2:
        st.subheader("Add New Accessory Item")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_category = st.selectbox("Category *", list(ACCESSORY_CATEGORIES.keys()))
            
            # Show predefined models or allow custom
            model_options = ACCESSORY_CATEGORIES[new_category]
            if "Other" in model_options:
                model_options = model_options[:-1] + ["Custom (Enter Below)"] + ["Other"]
            
            selected_model = st.selectbox("Model *", model_options)
            
            if selected_model == "Custom (Enter Below)":
                new_model = st.text_input("Custom Model Name *")
            else:
                new_model = selected_model
            
            new_part_number = st.text_input("Part Number", key="acc_part_number")
            new_team = st.text_input("Team Name (Optional)", placeholder="e.g., Network Team, DevOps", key="acc_team_name")
            new_description = st.text_area("Description", height=100, key="acc_description")
        
        with col2:
            new_unit_price = st.number_input("Unit Price ($)", min_value=0.0, format="%.2f")
            
            st.write("**Initial Quantities:**")
            initial_quantities = {}
            for loc in LOCATIONS:
                initial_quantities[loc] = st.number_input(
                    f"{loc} Quantity",
                    min_value=0,
                    value=0,
                    key=f"init_qty_{loc}"
                )
        
        if st.button("Add Accessory Item", type="primary"):
            if new_model and new_model != "Custom (Enter Below)":
                # Check if this model already exists
                existing = next((acc for acc in st.session_state.accessories_inventory 
                               if acc['model'] == new_model and acc['category'] == new_category), None)
                
                if existing:
                    st.error(f"An item with model '{new_model}' already exists in {new_category}")
                else:
                    new_accessory = {
                        "accessory_id": f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
                        "category": new_category,
                        "model": new_model,
                        "part_number": new_part_number,
                        "team": new_team,
                        "description": new_description,
                        "unit_price": new_unit_price,
                        "quantities": initial_quantities,
                        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    st.session_state.accessories_inventory.append(new_accessory)
                    if save_accessories_inventory():
                        st.success(f"Added {new_model} to accessories inventory!")
                        st.balloons()
                        st.rerun()
            else:
                st.error("Please provide a model name")
    
    # Quick Update Tab
    with acc_tab3:
        st.subheader("Quick Quantity Updates")
        st.markdown("Quickly update multiple items at once")
        
        # Select location to update
        update_location = st.selectbox("Select Location to Update", LOCATIONS, key="bulk_update_loc")
        
        if st.session_state.accessories_inventory:
            # Group by category for easier updates
            st.write(f"### Updating quantities for: {update_location}")
            
            # Track changes
            changes = {}
            
            for category in ACCESSORY_CATEGORIES.keys():
                category_items = [acc for acc in st.session_state.accessories_inventory 
                                 if acc['category'] == category]
                
                if category_items:
                    st.write(f"**{category}**")
                    
                    # Create columns for compact display
                    for item in category_items:
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                        
                        with col1:
                            st.write(f"{item['model']}")
                        
                        with col2:
                            st.write(f"Current: {item['quantities'].get(update_location, 0)}")
                        
                        with col3:
                            new_value = st.number_input(
                                "New",
                                min_value=0,
                                value=item['quantities'].get(update_location, 0),
                                key=f"bulk_{item['accessory_id']}_{update_location}",
                                label_visibility="collapsed"
                            )
                            
                            if new_value != item['quantities'].get(update_location, 0):
                                changes[item['accessory_id']] = new_value
                        
                        with col4:
                            diff = new_value - item['quantities'].get(update_location, 0)
                            if diff > 0:
                                st.success(f"+{diff}")
                            elif diff < 0:
                                st.error(f"{diff}")
            
            # Apply all changes button
            if changes:
                st.write("---")
                if st.button(f"Apply {len(changes)} Changes", type="primary"):
                    for acc_id, new_qty in changes.items():
                        update_accessory_count(acc_id, update_location, new_qty)
                    st.success(f"Updated {len(changes)} items in {update_location}")
                    st.rerun()
        else:
            st.info("No accessories in inventory yet.")

# Tab 4: Global Dashboard
with main_tab4:
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
        
        # Owner and Team Analysis
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
            st.subheader("Assets by Team")
            team_counts = {}
            no_team_count = 0
            for asset in st.session_state.inventory:
                team = asset.get('team', '')
                if team:
                    team_counts[team] = team_counts.get(team, 0) + 1
                else:
                    no_team_count += 1
            
            if team_counts or no_team_count > 0:
                # Sort by count and show top teams
                sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for team, count in sorted_teams:
                    st.write(f"• **{team}**: {count} assets")
                if no_team_count > 0:
                    st.write(f"• **No Team Assigned**: {no_team_count} assets")
            else:
                st.info("No team information available")
        
        st.divider()
        
        # Active Loans
        col1, col2 = st.columns(2)
        
        with col1:
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
                if asset['status'] == "Deployed" and asset.get('deployment_info'):
                    rack = asset['deployment_info'].get('rack', '')
                    if rack:  # Only count if rack is not empty
                        rack_key = f"{asset['location']} - {rack}"
                        rack_counts[rack_key] = rack_counts.get(rack_key, 0) + 1
            
            if rack_counts:
                # Show top 10 racks
                top_racks = sorted(rack_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                for rack, count in top_racks:
                    st.write(f"• {rack}: {count} assets")
            else:
                st.info("No deployed assets with rack information yet")
        
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

# Tab 5: Bulk Edit
with main_tab5:
    st.header("🔧 Bulk Edit Assets")
    st.markdown("Update multiple assets at once")
    
    # Choose what to edit
    bulk_edit_tabs = st.tabs(["Edit Assets", "Edit Accessories"])
    
    # Bulk Edit Assets
    with bulk_edit_tabs[0]:
        st.subheader("Bulk Edit Assets")
        
        # Step 1: Select assets to edit
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bulk_location = st.selectbox("Filter by Location", ["All"] + LOCATIONS, key="bulk_edit_location")
        
        with col2:
            bulk_category = st.selectbox("Filter by Category", ["All"] + list(ASSET_CATEGORIES.keys()), key="bulk_edit_category")
        
        with col3:
            bulk_status = st.selectbox("Filter by Status", ["All", "Available", "Deployed", "Loaned"], key="bulk_edit_status")
        
        # Get filtered assets
        filtered_bulk_assets = st.session_state.inventory
        
        if bulk_location != "All":
            filtered_bulk_assets = [a for a in filtered_bulk_assets if a['location'] == bulk_location]
        
        if bulk_category != "All":
            filtered_bulk_assets = [a for a in filtered_bulk_assets if a['category'] == bulk_category]
        
        if bulk_status != "All":
            filtered_bulk_assets = [a for a in filtered_bulk_assets if a['status'] == bulk_status]
        
        if filtered_bulk_assets:
            st.write(f"Found {len(filtered_bulk_assets)} assets matching filters")
            
            # Step 2: Choose what to update
            st.subheader("Select Fields to Update")
            
            col1, col2 = st.columns(2)
            
            with col1:
                update_options = {
                    "Team": st.checkbox("Update Team", key="bulk_update_team"),
                    "Owner": st.checkbox("Update Owner", key="bulk_update_owner"),
                    "Location": st.checkbox("Update Location", key="bulk_update_location"),
                    "Status": st.checkbox("Update Status", key="bulk_update_status")
                }
            
            with col2:
                # Show input fields for selected options
                new_values = {}
                
                if update_options["Team"]:
                    new_values["team"] = st.text_input("New Team Name", key="bulk_new_team")
                
                if update_options["Owner"]:
                    new_values["owner"] = st.text_input("New Owner Name", key="bulk_new_owner")
                
                if update_options["Location"]:
                    new_values["location"] = st.selectbox("New Location", LOCATIONS, key="bulk_new_location")
                
                if update_options["Status"]:
                    new_values["status"] = st.selectbox("New Status", ["Available", "Deployed", "Loaned"], key="bulk_new_status")
            
            # Step 3: Preview changes
            if any(update_options.values()) and any(new_values.values()):
                st.subheader("Preview Changes")
                
                # Create a preview table
                preview_data = []
                for asset in filtered_bulk_assets[:10]:  # Show first 10 as preview
                    row = {
                        "Asset ID": asset['asset_id'],
                        "Name": asset['name'],
                        "Current Location": asset['location'],
                        "Current Status": asset['status'],
                        "Current Owner": asset.get('owner', 'N/A'),
                        "Current Team": asset.get('team', 'N/A')
                    }
                    
                    # Add new values
                    if "team" in new_values:
                        row["→ New Team"] = new_values["team"]
                    if "owner" in new_values:
                        row["→ New Owner"] = new_values["owner"]
                    if "location" in new_values:
                        row["→ New Location"] = new_values["location"]
                    if "status" in new_values:
                        row["→ New Status"] = new_values["status"]
                    
                    preview_data.append(row)
                
                df_preview = pd.DataFrame(preview_data)
                st.dataframe(df_preview)
                
                if len(filtered_bulk_assets) > 10:
                    st.info(f"Showing first 10 of {len(filtered_bulk_assets)} assets that will be updated")
                
                # Apply changes button
                col1, col2, col3 = st.columns([1, 1, 3])
                
                with col1:
                    if st.button("Apply Changes", type="primary", key="apply_bulk_changes"):
                        updated_count = 0
                        
                        for asset in filtered_bulk_assets:
                            # Update each field if selected
                            if "team" in new_values and new_values["team"]:
                                asset["team"] = new_values["team"]
                            if "owner" in new_values and new_values["owner"]:
                                asset["owner"] = new_values["owner"]
                            if "location" in new_values:
                                asset["location"] = new_values["location"]
                            if "status" in new_values:
                                asset["status"] = new_values["status"]
                                # Clear deployment/loan info if changing to Available
                                if new_values["status"] == "Available":
                                    asset["deployment_info"] = {}
                                    asset["loan_info"] = {}
                            
                            updated_count += 1
                        
                        save_inventory()
                        st.success(f"✅ Successfully updated {updated_count} assets!")
                        st.balloons()
                        st.rerun()
                
                with col2:
                    if st.button("Cancel", key="cancel_bulk_changes"):
                        st.rerun()
            
            # Additional bulk operations
            st.divider()
            st.subheader("Quick Actions")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Add prefix/suffix to names**")
                prefix = st.text_input("Prefix to add", key="bulk_prefix")
                suffix = st.text_input("Suffix to add", key="bulk_suffix")
                
                if st.button("Apply to Names", key="apply_name_changes"):
                    for asset in filtered_bulk_assets:
                        if prefix:
                            asset["name"] = prefix + asset["name"]
                        if suffix:
                            asset["name"] = asset["name"] + suffix
                    save_inventory()
                    st.success(f"Updated names for {len(filtered_bulk_assets)} assets")
                    st.rerun()
            
            with col2:
                st.write("**Clear field values**")
                clear_field = st.selectbox("Field to clear", ["Team", "Owner", "Order Number", "Tracking Number"], key="clear_field")
                
                if st.button("Clear Selected Field", key="clear_field_button"):
                    field_map = {
                        "Team": "team",
                        "Owner": "owner",
                        "Order Number": "order_number",
                        "Tracking Number": "tracking_number"
                    }
                    field_key = field_map[clear_field]
                    
                    for asset in filtered_bulk_assets:
                        if field_key in asset:
                            asset[field_key] = ""
                    
                    save_inventory()
                    st.success(f"Cleared {clear_field} for {len(filtered_bulk_assets)} assets")
                    st.rerun()
            
            with col3:
                st.write("**Export filtered assets**")
                if st.button("Export Filtered to CSV", key="export_filtered"):
                    # Convert filtered assets to DataFrame
                    export_data = []
                    for asset in filtered_bulk_assets:
                        row = {
                            'Asset ID': asset['asset_id'],
                            'Name': asset.get('name', ''),
                            'Team': asset.get('team', ''),
                            'Owner': asset.get('owner', ''),
                            'Location': asset['location'],
                            'Category': asset['category'],
                            'Status': asset['status']
                        }
                        export_data.append(row)
                    
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"filtered_assets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        else:
            st.info("No assets found matching the selected filters")
    
    # Bulk Edit Accessories
    with bulk_edit_tabs[1]:
        st.subheader("Bulk Edit Accessories")
        
        # Filter accessories
        col1, col2 = st.columns(2)
        
        with col1:
            acc_bulk_category = st.selectbox("Filter by Category", ["All"] + list(ACCESSORY_CATEGORIES.keys()), key="acc_bulk_category")
        
        with col2:
            acc_bulk_team = st.selectbox("Filter by Team", ["All"] + sorted(list(set(acc.get('team', '') for acc in st.session_state.accessories_inventory if acc.get('team', '')))), key="acc_bulk_team")
        
        # Get filtered accessories
        filtered_bulk_acc = st.session_state.accessories_inventory
        
        if acc_bulk_category != "All":
            filtered_bulk_acc = [a for a in filtered_bulk_acc if a['category'] == acc_bulk_category]
        
        if acc_bulk_team != "All":
            filtered_bulk_acc = [a for a in filtered_bulk_acc if a.get('team', '') == acc_bulk_team]
        
        if filtered_bulk_acc:
            st.write(f"Found {len(filtered_bulk_acc)} accessories matching filters")
            
            # Update options
            st.subheader("Bulk Update Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Update Team**")
                new_acc_team = st.text_input("New Team Name for Accessories", key="bulk_acc_team")
                
                if st.button("Update Team", key="update_acc_team"):
                    for acc in filtered_bulk_acc:
                        acc["team"] = new_acc_team
                    save_accessories_inventory()
                    st.success(f"Updated team for {len(filtered_bulk_acc)} accessories")
                    st.rerun()
            
            with col2:
                st.write("**Adjust Quantities**")
                adjustment_location = st.selectbox("Location", LOCATIONS, key="adj_location")
                adjustment_type = st.radio("Adjustment Type", ["Add", "Subtract", "Set to"], key="adj_type")
                adjustment_value = st.number_input("Value", min_value=0, key="adj_value")
                
                if st.button("Apply Quantity Adjustment", key="apply_qty_adj"):
                    for acc in filtered_bulk_acc:
                        current_qty = acc['quantities'].get(adjustment_location, 0)
                        
                        if adjustment_type == "Add":
                            acc['quantities'][adjustment_location] = current_qty + adjustment_value
                        elif adjustment_type == "Subtract":
                            acc['quantities'][adjustment_location] = max(0, current_qty - adjustment_value)
                        else:  # Set to
                            acc['quantities'][adjustment_location] = adjustment_value
                        
                        acc['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    
                    save_accessories_inventory()
                    st.success(f"Updated quantities for {len(filtered_bulk_acc)} accessories in {adjustment_location}")
                    st.rerun()
            
            # Show filtered accessories
            st.divider()
            st.subheader("Filtered Accessories")
            
            for acc in filtered_bulk_acc[:5]:  # Show first 5
                st.write(f"• **{acc['model']}** ({acc['category']}) - Team: {acc.get('team', 'N/A')}")
            
            if len(filtered_bulk_acc) > 5:
                st.info(f"Showing first 5 of {len(filtered_bulk_acc)} accessories")
        else:
            st.info("No accessories found matching the selected filters")

# Tab 6: Data Management
with main_tab6:
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
                        'Team': asset.get('team', ''),
                        'Order Number': asset.get('order_number', ''),
                        'Tracking Number': asset.get('tracking_number', ''),
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
                            if 'Team' in row and pd.notna(row['Team']):
                                new_asset["team"] = str(row['Team']).strip()
                            if 'Order Number' in row and pd.notna(row['Order Number']):
                                new_asset["order_number"] = str(row['Order Number']).strip()
                            if 'Tracking Number' in row and pd.notna(row['Tracking Number']):
                                new_asset["tracking_number"] = str(row['Tracking Number']).strip()
                            
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
    
    # Accessories Data Management
    st.header("Accessories Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export Accessories Data")
        
        if st.button("Download Accessories as CSV", key="download_acc_main"):
            if st.session_state.accessories_inventory:
                # Convert to DataFrame for export
                export_acc_data = []
                for acc in st.session_state.accessories_inventory:
                    # Create one row per location for easier management
                    for loc in LOCATIONS:
                        row = {
                            'Accessory ID': acc['accessory_id'],
                            'Category': acc['category'],
                            'Model': acc['model'],
                            'Part Number': acc.get('part_number', ''),
                            'Team': acc.get('team', ''),
                            'Description': acc.get('description', ''),
                            'Location': loc,
                            'Quantity': acc['quantities'].get(loc, 0),
                            'Unit Price': acc.get('unit_price', 0),
                            'Total Value': acc['quantities'].get(loc, 0) * acc.get('unit_price', 0),
                            'Last Updated': acc.get('last_updated', ''),
                            'Date Added': acc.get('date_added', '')
                        }
                        export_acc_data.append(row)
                
                df_acc = pd.DataFrame(export_acc_data)
                csv_acc = df_acc.to_csv(index=False)
                st.download_button(
                    label="Download Accessories CSV",
                    data=csv_acc,
                    file_name=f"accessories_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No accessories data to export!")
    
    with col2:
        st.subheader("Import Accessories Data")
        st.info("CSV should have columns: Category, Model, Part Number, Description, Location, Quantity, Unit Price")
        
        uploaded_acc_file = st.file_uploader("Choose an accessories CSV file", type="csv", key="acc_uploader")
        if uploaded_acc_file is not None:
            try:
                df_acc = pd.read_csv(uploaded_acc_file)
                st.write("Preview of uploaded accessories data:")
                st.dataframe(df_acc.head())
                
                if st.button("Import Accessories Data", key="import_acc_main"):
                    imported_acc_count = 0
                    updated_acc_count = 0
                    errors_acc = []
                    
                    # Group by Model to consolidate quantities
                    grouped = df_acc.groupby(['Category', 'Model'])
                    
                    for (category, model), group in grouped:
                        try:
                            # Check if accessory already exists
                            existing_acc = next((acc for acc in st.session_state.accessories_inventory 
                                               if acc['model'] == model and acc['category'] == category), None)
                            
                            if existing_acc:
                                # Update quantities
                                for _, row in group.iterrows():
                                    if 'Location' in row and row['Location'] in LOCATIONS:
                                        existing_acc['quantities'][row['Location']] = int(row.get('Quantity', 0))
                                existing_acc['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                updated_acc_count += 1
                            else:
                                # Create new accessory
                                first_row = group.iloc[0]
                                new_acc = {
                                    "accessory_id": f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}",
                                    "category": category,
                                    "model": model,
                                    "part_number": str(first_row.get('Part Number', '')),
                                    "team": str(first_row.get('Team', '')) if pd.notna(first_row.get('Team')) else '',
                                    "description": str(first_row.get('Description', '')),
                                    "unit_price": float(first_row.get('Unit Price', 0)),
                                    "quantities": {loc: 0 for loc in LOCATIONS},
                                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "date_added": datetime.now().strftime("%Y-%m-%d %H:%M")
                                }
                                
                                # Set quantities from all rows
                                for _, row in group.iterrows():
                                    if 'Location' in row and row['Location'] in LOCATIONS:
                                        new_acc['quantities'][row['Location']] = int(row.get('Quantity', 0))
                                
                                st.session_state.accessories_inventory.append(new_acc)
                                imported_acc_count += 1
                                
                        except Exception as e:
                            errors_acc.append(f"Error with {model}: {str(e)}")
                    
                    save_accessories_inventory()
                    
                    if imported_acc_count > 0 or updated_acc_count > 0:
                        st.success(f"Imported {imported_acc_count} new items, updated {updated_acc_count} existing items")
                        if errors_acc:
                            st.warning(f"Errors: {', '.join(errors_acc[:5])}")
                        st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading accessories file: {e}")
    
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
