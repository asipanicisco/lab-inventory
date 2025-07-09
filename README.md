# MS Perfect Lab Inventory Management System

A comprehensive multi-location network equipment inventory management system built with Streamlit and Python.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Asset Categories](#asset-categories)
- [Data Management](#data-management)
- [CSV Import/Export](#csv-importexport)
- [Troubleshooting](#troubleshooting)

## 🔧 Overview

The MS Perfect Lab Inventory Management System is designed to track and manage network equipment across multiple laboratory locations. It provides a user-friendly interface for adding, editing, and tracking assets with detailed specifications, deployment information, and loan tracking.

### Supported Locations
- **SF** - San Francisco
- **SJ** - San Jose  
- **RTP** - Research Triangle Park
- **BGL** - Bangalore

## ✨ Features

### Core Features
- **Multi-location Support**: Manage inventory across 4 different lab locations
- **Asset Tracking**: Track detailed specifications for 8 different equipment categories
- **Status Management**: Monitor assets as Available, Deployed, or Loaned
- **Deployment Tracking**: Record rack, row, and position for deployed equipment
- **Loan Management**: Track who borrowed equipment, purpose, and expected return dates
- **Owner Assignment**: Assign assets to specific owners and track by order numbers

### User Interface
- **Location-based Views**: Separate tabs for each location with filtering capabilities
- **Global Dashboard**: Overview of all assets across all locations with utilization metrics
- **Search & Filter**: Search by asset ID, name, serial number, owner, or order number
- **Real-time Metrics**: View availability, deployment, and utilization statistics

### Data Management
- **CSV Import/Export**: Bulk import assets from CSV files with duplicate detection
- **Data Persistence**: Automatic saving to JSON file
- **Backup/Restore**: Manual save and load functionality
- **Data Validation**: Automatic validation of required fields and categories

## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd lab-inventory-management
   ```

2. **Install required packages**
   ```bash
   pip install streamlit pandas
   ```

3. **Run the application**
   ```bash
   streamlit run inventory_app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:8501`

## 📖 Usage

### Adding New Assets

1. Navigate to the **"➕ Add Asset"** tab
2. Fill in the required information:
   - Asset Name (required)
   - Location (select from dropdown)
   - Category (select from dropdown)
   - Status (Available/Deployed/Loaned)
3. Enter specifications based on the category
4. If status is "Deployed", enter rack/row/position
5. If status is "Loaned", enter borrower information
6. Click **"Add Asset"** to save

### Viewing and Managing Inventory

1. Go to **"📍 Locations"** tab
2. Select the location tab you want to view
3. Use search and filters to find specific assets:
   - Search by any field (ID, name, serial, etc.)
   - Filter by status (All/Available/Deployed/Loaned)
   - Filter by owner
4. Click on any asset to expand details
5. Use **Edit** button to modify asset information
6. Use **Delete** button (confirm twice) to remove assets

### Global Dashboard

The **"📊 Global Dashboard"** provides:
- Total asset count across all locations
- Availability and utilization metrics
- Assets by location breakdown
- Assets by owner analysis
- Active loans tracking
- Category distribution
- Top deployment racks
- Recent activity log

## 📦 Asset Categories

### Supported Equipment Types

1. **Meraki Switch**
   - Required: Model, Serial Number, MAC Address
   - Optional: Firmware Version

2. **Cisco Switch**
   - Required: Model, Serial Number, MAC Address
   - Optional: IOS Version

3. **Cisco Network Module**
   - Required: Model, Part Number, Serial Number, Compatible With

4. **SFP (Small Form-factor Pluggable)**
   - Required: Type, Speed, Wavelength, Serial Number

5. **Stack Cable**
   - Required: Length, Type, Part Number, Serial Number

6. **Lantronix Console**
   - Required: Model, Serial Number, IP Address, Port Count

7. **HP Switch**
   - Required: Model, Serial Number, MAC Address
   - Optional: Firmware Version

8. **Raritan PDU**
   - Required: Model, Serial Number, IP Address, Outlet Count

## 💾 Data Management

### Data Storage
- All inventory data is automatically saved to `inventory_data.json`
- The file is updated whenever changes are made
- Data includes all asset details, specifications, and history

### CSV Import/Export

#### Exporting Data
1. Go to **"💾 Data Management"** tab
2. Select export option:
   - All Locations
   - Specific Location
3. Click **"Download Inventory as CSV"**
4. Save the file to your computer

#### Importing Data
1. Prepare your CSV file with the following columns:
   - Asset ID (optional - will be generated if missing)
   - Name (required)
   - Network Name
   - Owner
   - Order Number
   - Location (must be SF, SJ, RTP, or BGL)
   - Category (must match supported categories)
   - Status (Available, Deployed, or Loaned)
   - Specification fields based on category
   - Deployment fields (if deployed): Rack, Row, Position
   - Loan fields (if loaned): Loaned To, Loan Purpose, Expected Return
   - Notes
   - Date Added

2. In the application:
   - Go to **"💾 Data Management"** tab
   - Click **"Choose a CSV file"**
   - Select your file
   - Review the preview
   - Click **"Import Data"**

#### Import Features
- **Duplicate Detection**: Automatically detects and skips assets with duplicate serial numbers
- **Data Validation**: Validates locations, categories, and required fields
- **Progress Tracking**: Shows import progress with detailed metrics
- **Error Reporting**: Provides detailed error messages for troubleshooting

### Backup and Restore
- Use **"Manual Save"** to force save current data
- Use **"Reload from File"** to restore from saved file
- Clear data by location or all data using the Danger Zone options

## 🔍 Search and Filter Tips

### Search Functionality
- Search is case-insensitive
- Searches across all fields including:
  - Asset ID
  - Name
  - Serial Number
  - Owner
  - Order Number
  - Network Name
  - Specifications

### Filter Options
- **Status Filter**: Show only Available, Deployed, or Loaned assets
- **Owner Filter**: Show assets assigned to specific owners
- **Location Tabs**: View assets from specific locations only

## ⚠️ Troubleshooting

### Common Issues

1. **"NaN" Asset IDs**
   - The system automatically fixes these on load
   - If persists, use "Reload from File" in Data Management

2. **Import Failures**
   - Check CSV column names match exactly
   - Ensure locations are SF, SJ, RTP, or BGL
   - Verify categories match supported types
   - Check for required fields based on category

3. **Duplicate Serial Numbers**
   - System prevents importing assets with duplicate serials
   - Check the duplicate report after import
   - Remove or update existing assets before re-importing

4. **Data Not Saving**
   - Check file permissions for `inventory_data.json`
   - Ensure sufficient disk space
   - Try manual save in Data Management tab

### Asset ID Format
- Legacy format: `AST-YYYYMMDDHHMMSS###`
- New format: `AST-YYYYMMDDHHMMSS-MICROSECONDS-XXXX`
- Both formats are supported

## 📊 Best Practices

1. **Regular Backups**: Export CSV backups regularly
2. **Consistent Naming**: Use consistent naming conventions for assets
3. **Complete Information**: Fill in all required fields for better tracking
4. **Serial Numbers**: Always include serial numbers to prevent duplicates
5. **Owner Assignment**: Assign owners to track responsibility
6. **Status Updates**: Keep deployment and loan status current

## 🔄 Version History

- **v2.1**: Current version with enhanced import/export and duplicate detection
- Features multi-location support, comprehensive asset tracking, and data validation

## 📝 License

This software is provided as-is for laboratory inventory management purposes.

---

For additional support or feature requests, please contact your system administrator.
