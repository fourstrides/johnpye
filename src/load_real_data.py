#!/usr/bin/env python3
"""
Load real bid data from extraction results and create status.json for dashboard
"""

import json
import os
import sys
from datetime import datetime
import re

def parse_watchlist_data():
    """Parse watchlist data from CSV file."""
    watchlist_files = [
        "../data/watchlist_20251004_000755.csv",
        "../data/watchlist_20251003_223429.csv"
    ]
    
    watchlist_items = []
    
    for watchlist_file in watchlist_files:
        if not os.path.exists(watchlist_file):
            continue
            
        try:
            with open(watchlist_file, 'r') as f:
                content = f.read().strip()
            
            # Split by newlines and find data lines
            lines = content.split('\n')
            
            # Look for lines that contain URLs (these are data lines)
            for line in lines:
                if 'https://www.johnpyeauctions.co.uk/Event/LotDetails/' in line:
                    watchlist_item = parse_watchlist_csv_line(line)
                    if watchlist_item:
                        # Check if already exists (avoid duplicates)
                        existing = any(item['lot_number'] == watchlist_item['lot_number'] for item in watchlist_items)
                        if not existing:
                            watchlist_items.append(watchlist_item)
                            
        except Exception as e:
            print(f"⚠️  Error parsing watchlist file {watchlist_file}: {e}")
            continue
    
    return watchlist_items

def parse_watchlist_csv_line(line):
    """Parse individual watchlist CSV line."""
    try:
        # Split by comma, but handle quoted sections properly
        import csv
        from io import StringIO
        
        # Use CSV reader to handle complex quoting
        reader = csv.reader(StringIO(line))
        parts = next(reader)
        
        if len(parts) < 6:
            return None
        
        # Extract data - need to be more careful with field mapping
        current_bid = 'Unknown'
        title_info = 'Unknown'
        end_time = 'Unknown'
        url = 'https://www.johnpyeauctions.co.uk'
        
        # Find the URL field (most reliable identifier)
        for i, part in enumerate(parts):
            if 'https://www.johnpyeauctions.co.uk' in part:
                url = part
                # Previous fields should be current_bid, title_info, bid_amount, end_time
                if i >= 4:
                    end_time = parts[i-1]
                if i >= 3:
                    title_info = parts[i-3] if i-3 >= 0 else parts[1] if len(parts) > 1 else 'Unknown'
                if i >= 4:
                    current_bid = parts[i-4] if i-4 >= 0 else parts[0] if len(parts) > 0 and parts[0].startswith('£') else 'Unknown'
                break
        
        # Skip ended items
        if 'Ended' in title_info:
            return None
            
        # Extract lot number from title_info or URL
        lot_number = 'Unknown'
        title = 'Unknown Item'
        
        # Try to extract from URL first
        if 'LotDetails/' in url:
            try:
                lot_id = url.split('LotDetails/')[1].split('/')[0]
                lot_number = lot_id[-6:]  # Take last 6 digits as lot number
            except:
                pass
        
        # Extract title from URL (more reliable)
        if 'LotDetails/' in url:
            try:
                # Extract title from URL path
                url_parts = url.split('/')
                if len(url_parts) > 4:
                    raw_title = url_parts[-1].replace('-', ' ')
                    # Clean up common patterns
                    raw_title = re.sub(r'[A-Z]+\d+$', '', raw_title)  # Remove model codes at end
                    raw_title = re.sub(r'JP[A-Z]+\d+', '', raw_title)  # Remove JP codes
                    raw_title = raw_title.replace('ORIGINAL RRP', '').strip()
                    
                    if len(raw_title) > 5:  # Only use if meaningful
                        title = raw_title.title()  # Capitalize properly
            except:
                pass
        
        # Fallback: try to extract from title_info
        if title == 'Unknown Item' and 'CURRENT BID' not in title_info:
            # Clean up title
            title = title_info.split('[')[0].strip()  # Remove codes in brackets
            title = title.split('(')[0].strip()      # Remove RRP info
            title = title.replace('ORIGINAL RRP', '').strip()
            
            # Extract lot number from title if available
            lot_match = re.search(r'(\d+)\s*-\s*(.+)', title)
            if lot_match:
                lot_number = lot_match.group(1)
                title = lot_match.group(2).strip()
        
        # Clean up end time
        if 'Hours,' in end_time and 'Minutes' in end_time:
            end_time = end_time.strip()
        
        return {
            'title': title[:100],  # Truncate long titles
            'lot_number': lot_number,
            'current_bid': current_bid,
            'end_time': end_time,
            'url': url.strip(),
            'status': 'Watching'
        }
        
    except Exception as e:
        # Debug: print the problematic line
        # print(f"Error parsing line: {line[:100]}... Error: {e}")
        return None

def parse_bid_data_file():
    """Parse the real bid data from extraction file."""
    bid_file = "../data/bid_data_extraction.txt"
    
    if not os.path.exists(bid_file):
        print("❌ No bid data extraction file found")
        return []
    
    active_bids = []
    
    try:
        with open(bid_file, 'r') as f:
            content = f.read()
        
        # Split by BID ELEMENT sections
        sections = content.split('BID ELEMENT')
        
        for section in sections[1:]:  # Skip header
            if 'Lot ' not in section:
                continue
                
            lines = section.split('\n')
            
            # Extract the content section
            content_start = False
            bid_content = []
            
            for line in lines:
                if line.startswith('Content:'):
                    content_start = True
                    continue
                elif line.startswith('----'):
                    break
                elif content_start:
                    bid_content.append(line.strip())
            
            # Parse the bid content
            if bid_content:
                bid_text = '\n'.join(bid_content)
                parsed_bid = parse_individual_bid(bid_text)
                if parsed_bid:
                    active_bids.append(parsed_bid)
    
    except Exception as e:
        print(f"❌ Error parsing bid data: {e}")
    
    return active_bids

def parse_individual_bid(bid_text):
    """Parse an individual bid from text content."""
    try:
        lines = [line.strip() for line in bid_text.split('\n') if line.strip()]
        
        bid_data = {
            'title': 'Unknown',
            'lot_number': 'Unknown',
            'current_bid': '£0.00',
            'my_max_bid': '£0.00',
            'end_time': 'Unknown',
            'status': 'Unknown',
            'url': 'https://www.johnpyeauctions.co.uk/Account/Bidding/Active'
        }
        
        # Find the first line with Lot information
        for i, line in enumerate(lines):
            # Extract title and lot number
            if line.startswith('Lot ') and '-' in line:
                # Extract lot number
                lot_match = re.search(r'Lot (\d+)', line)
                if lot_match:
                    bid_data['lot_number'] = lot_match.group(1)
                
                # Extract title
                title_match = re.search(r'Lot \d+ - (.+?)(?:\[|:)', line)
                if title_match:
                    title = title_match.group(1).strip()
                    # Clean up the title
                    if '(ORIGINAL RRP' in title:
                        title = title.split('(ORIGINAL RRP')[0].strip()
                    bid_data['title'] = title
            
            # Extract current bid
            elif line == 'CURRENT BID' and i + 1 < len(lines):
                bid_data['current_bid'] = lines[i + 1]
            
            # Extract my max bid
            elif line == 'MY MAX BID' and i + 1 < len(lines):
                bid_data['my_max_bid'] = lines[i + 1]
            
            # Extract time remaining
            elif line.startswith('ENDS IN:') and i + 1 < len(lines):
                bid_data['end_time'] = lines[i + 1].strip()
            elif 'Hours, ' in line and 'Minutes' in line:
                bid_data['end_time'] = line.strip()
            
            # Extract status
            elif line in ['WINNING', 'OUTBID']:
                bid_data['status'] = line
        
        # Only return if we have essential data
        if bid_data['lot_number'] != 'Unknown' and bid_data['title'] != 'Unknown':
            return bid_data
            
    except Exception as e:
        print(f"❌ Error parsing individual bid: {e}")
    
    return None

def create_status_json(active_bids, watchlist_items):
    """Create status.json file for dashboard."""
    
    # Count statuses
    winning_count = len([bid for bid in active_bids if bid['status'] == 'WINNING'])
    outbid_count = len([bid for bid in active_bids if bid['status'] == 'OUTBID'])
    
    status_data = {
        'timestamp': datetime.now().isoformat(),
        'is_running': False,  # Not currently running
        'start_time': None,
        'active_bids_count': len(active_bids),
        'watchlist_count': len(watchlist_items),
        'active_bids': active_bids,
        'watchlist_items': watchlist_items,
        'summary': {
            'total_active_bids': len(active_bids),
            'winning_bids': winning_count,
            'outbid_bids': outbid_count,
            'total_watchlist': len(watchlist_items),
            'total_value_current': sum([float(re.sub(r'[£,]', '', bid['current_bid'])) for bid in active_bids if bid['current_bid'] != '£0.00']),
            'total_value_max': sum([float(re.sub(r'[£,]', '', bid['my_max_bid'])) for bid in active_bids if bid['my_max_bid'] != '£0.00'])
        }
    }
    
    # Save to status.json
    status_file = "../data/status.json"
    with open(status_file, 'w') as f:
        json.dump(status_data, f, indent=2)
    
    print(f"✅ Status data saved to {status_file}")
    return status_data

def main():
    """Main function."""
    print("📊 Loading Real Bid Data for Dashboard")
    print("=" * 50)
    
    # Parse bid data from extraction file
    print("🔍 Parsing bid data from extraction file...")
    active_bids = parse_bid_data_file()
    
    if not active_bids:
        print("❌ No bid data found")
        return False
    
    print(f"✅ Found {len(active_bids)} active bids")
    
    # Parse watchlist data
    print("🔍 Parsing watchlist data...")
    watchlist_items = parse_watchlist_data()
    print(f"✅ Found {len(watchlist_items)} watchlist items")
    
    # Show summary
    winning = len([bid for bid in active_bids if bid['status'] == 'WINNING'])
    outbid = len([bid for bid in active_bids if bid['status'] == 'OUTBID'])
    
    print(f"   🏆 Winning: {winning}")
    print(f"   🚨 Outbid: {outbid}")
    print(f"   👁️ Watching: {len(watchlist_items)}")
    
    # Display sample bids
    print("\n📋 Sample Bids Found:")
    for i, bid in enumerate(active_bids[:3]):  # Show first 3
        print(f"   {i+1}. Lot {bid['lot_number']}: {bid['title'][:40]}...")
        print(f"      Current: {bid['current_bid']}, Max: {bid['my_max_bid']}, Status: {bid['status']}")
    
    if len(active_bids) > 3:
        print(f"   ... and {len(active_bids) - 3} more")
        
    # Display sample watchlist
    if watchlist_items:
        print("\n👁️ Sample Watchlist Items:")
        for i, item in enumerate(watchlist_items[:3]):  # Show first 3
            print(f"   {i+1}. Lot {item['lot_number']}: {item['title'][:40]}...")
            print(f"      Current: {item['current_bid']}, Ends: {item['end_time']}")
        
        if len(watchlist_items) > 3:
            print(f"   ... and {len(watchlist_items) - 3} more")
    
    # Create status.json for dashboard
    print(f"\n💾 Creating status.json for dashboard...")
    status_data = create_status_json(active_bids, watchlist_items)
    
    # Calculate totals
    total_current = status_data['summary']['total_value_current']
    total_max = status_data['summary']['total_value_max']
    
    print(f"   📊 Total Current Value: £{total_current:.2f}")
    print(f"   💰 Total Max Bid Value: £{total_max:.2f}")
    
    print(f"\n🎉 SUCCESS! Dashboard data is ready.")
    print(f"   Visit http://localhost:8080 to see your {len(active_bids)} active bids and {len(watchlist_items)} watchlist items!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)