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