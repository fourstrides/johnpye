#!/usr/bin/env python3
"""
Simple bid deduplicator to fix duplicate entries
"""

def deduplicate_bids(bids):
    """Remove duplicate bids based on lot_number and title"""
    seen = set()
    deduplicated = []
    
    for bid in bids:
        # Create a unique key based on lot number and title
        key = f"{bid.get('lot_number', '')}-{bid.get('title', '')[:50]}"
        
        if key not in seen:
            seen.add(key)
            deduplicated.append(bid)
    
    return deduplicated

def enhance_bid_data(bid):
    """Enhance bid data to separate current_bid, my_bid, and my_max_bid"""
    # If we only have current_bid and my_max_bid, try to create better structure
    enhanced_bid = bid.copy()
    
    # Parse the current_bid and my_max_bid to determine actual status
    try:
        current_amount = float(bid.get('current_bid', '£0').replace('£', '').replace(',', ''))
        max_amount = float(bid.get('my_max_bid', '£0').replace('£', '').replace(',', ''))
        
        # Add my_bid field (could be same as current if we're winning)
        if bid.get('status', '').upper() == 'WINNING':
            enhanced_bid['my_bid'] = bid.get('current_bid', '£0.00')
        else:
            enhanced_bid['my_bid'] = bid.get('my_max_bid', '£0.00')
        
        # Ensure proper status based on amounts
        if max_amount >= current_amount and current_amount > 0:
            if bid.get('status', '').upper() != 'WINNING':
                # If amounts suggest we should be winning but status says otherwise
                # Trust the status from the website
                pass
        
    except (ValueError, TypeError):
        enhanced_bid['my_bid'] = bid.get('current_bid', '£0.00')
    
    return enhanced_bid

def deduplicate_watchlist(watchlist_items):
    """Remove duplicate watchlist items based on lot_number and title"""
    seen = set()
    deduplicated = []
    
    for item in watchlist_items:
        # Skip invalid or empty items
        if not item or not isinstance(item, dict):
            continue
            
        title = item.get('title', '')
        lot_number = item.get('lot_number', '')
        
        # Skip items that are just "View Item" or status words
        if title.lower() in ['view item', 'winning', 'outbid', 'lost', 'won', 'ended', 'active']:
            continue
            
        # Skip items without meaningful content
        if not title or len(title.strip()) < 10:
            continue
            
        # Create a unique key based on lot number and title
        key = f"{lot_number}-{title[:50]}"
        
        if key not in seen:
            seen.add(key)
            deduplicated.append(item)
    
    return deduplicated
