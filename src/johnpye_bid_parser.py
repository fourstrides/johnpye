#!/usr/bin/env python3
"""
Improved bid data parser for John Pye auction pages
Correctly extracts current bid, your bid, and your max bid
"""

import re
from typing import Dict, Optional, Tuple
import logging
from selenium.webdriver.common.by import By

class JohnPyeBidParser:
    """Parser for John Pye bidding page elements"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_bid_element_improved(self, element) -> Optional[Dict]:
        """
        Parse a bid element from John Pye active bidding page
        Returns proper current_bid, my_bid, my_max_bid values
        """
        try:
            text = element.text.strip()
            if len(text) < 20:  # Skip very short elements
                return None
            
            # Extract basic information
            lot_number = self._extract_lot_number(text)
            if not lot_number:
                return None
            
            title = self._extract_title(text)
            current_bid, my_bid, my_max_bid = self._extract_bid_amounts_detailed(text, element)
            status = self._extract_status_improved(text)
            end_time = self._extract_time_improved(text)
            url = self._extract_url(element)
            
            return {
                'lot_number': lot_number,
                'title': title,
                'current_bid': current_bid,
                'my_bid': my_bid,
                'my_max_bid': my_max_bid,
                'status': status,
                'end_time': end_time,
                'url': url
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing bid element: {e}")
            return None
    
    def _extract_bid_amounts_detailed(self, text: str, element) -> Tuple[str, str, str]:
        """
        Extract current bid, my bid, and my max bid with proper distinction
        Based on John Pye page structure
        """
        try:
            # John Pye typically shows data in this format:
            # CURRENT BID
            # £350.00
            # MY MAX BID  
            # £340.00
            # WINNING/OUTBID
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            current_bid = "£0.00"
            my_bid = "£0.00" 
            my_max_bid = "£0.00"
            
            # Method 1: Look for specific patterns in the text
            current_bid_patterns = [
                r'CURRENT BID[^£]*£([\d,]+\.?\d*)',
                r'Current Bid[^£]*£([\d,]+\.?\d*)',
                r'current bid[^£]*£([\d,]+\.?\d*)',
            ]
            
            max_bid_patterns = [
                r'MY MAX BID[^£]*£([\d,]+\.?\d*)',
                r'My Max Bid[^£]*£([\d,]+\.?\d*)',
                r'my max bid[^£]*£([\d,]+\.?\d*)',
                r'MAX BID[^£]*£([\d,]+\.?\d*)',
                r'Max Bid[^£]*£([\d,]+\.?\d*)',
            ]
            
            # Extract current bid
            for pattern in current_bid_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    current_bid = f"£{match.group(1)}"
                    self.logger.debug(f"Found current bid: {current_bid}")
                    break
            
            # Extract max bid
            for pattern in max_bid_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    my_max_bid = f"£{match.group(1)}"
                    self.logger.debug(f"Found max bid: {my_max_bid}")
                    break
            
            # Method 2: Look for sequential price patterns
            if current_bid == "£0.00" or my_max_bid == "£0.00":
                all_prices = re.findall(r'£([\d,]+\.?\d*)', text)
                
                if len(all_prices) >= 2:
                    # Usually: current bid first, then max bid
                    current_bid = f"£{all_prices[0]}" if current_bid == "£0.00" else current_bid
                    my_max_bid = f"£{all_prices[1]}" if my_max_bid == "£0.00" else my_max_bid
                    self.logger.debug(f"Sequential extraction - Current: {current_bid}, Max: {my_max_bid}")
                
                elif len(all_prices) == 1:
                    # Only one price found - could be either
                    price = f"£{all_prices[0]}"
                    if current_bid == "£0.00":
                        current_bid = price
                    if my_max_bid == "£0.00":
                        my_max_bid = price
            
            # Method 3: Try to use element structure if available
            try:
                # Look for specific elements within this bid element
                price_elements = element.find_elements(By.CSS_SELECTOR, '[class*="bid"], [class*="price"], .amount')
                if len(price_elements) >= 2:
                    for i, elem in enumerate(price_elements[:2]):
                        price_text = elem.text.strip()
                        price_match = re.search(r'£([\d,]+\.?\d*)', price_text)
                        if price_match:
                            if i == 0 and current_bid == "£0.00":
                                current_bid = f"£{price_match.group(1)}"
                            elif i == 1 and my_max_bid == "£0.00":
                                my_max_bid = f"£{price_match.group(1)}"
            except:
                pass
            
            # Determine my_bid (usually same as max_bid unless we're winning at current)
            try:
                current_amount = float(current_bid.replace('£', '').replace(',', ''))
                max_amount = float(my_max_bid.replace('£', '').replace(',', ''))
                
                if current_amount <= max_amount:
                    # We can still bid up to our max, so our current bid might be the current amount
                    my_bid = current_bid
                else:
                    # We've been outbid, our bid is our max
                    my_bid = my_max_bid
                    
            except (ValueError, TypeError):
                my_bid = my_max_bid
            
            self.logger.info(f"Bid amounts - Current: {current_bid}, My: {my_bid}, Max: {my_max_bid}")
            return current_bid, my_bid, my_max_bid
            
        except Exception as e:
            self.logger.debug(f"Error extracting bid amounts: {e}")
            return "£0.00", "£0.00", "£0.00"
    
    def _extract_lot_number(self, text: str) -> Optional[str]:
        """Extract lot number from text"""
        patterns = [
            r'Lot\s*(\d+)\s*[-\s]',  # "Lot 123 -"
            r'LOT\s*(\d+)',          # "LOT 123"
            r'#(\d+)',               # "#123"
            r'\[([A-Z0-9]+)\]',      # "[JPTC85291]" - John Pye item codes
            r'(\d{5,})'              # 5+ digit numbers
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_title(self, text: str) -> str:
        """Extract item title"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find the line that looks like a product title (usually the longest descriptive line)
        for line in lines:
            if len(line) > 20 and any(word in line.lower() for word in ['tv', 'monitor', 'laptop', 'phone', 'tablet', 'soundbar', 'speaker']):
                return line
        
        # Fallback to first substantial line
        for line in lines:
            if len(line) > 10 and not line.lower().startswith(('lot', 'current', 'bid', 'my', 'max')):
                return line
        
        return lines[0] if lines else "Unknown Item"
    
    def _extract_status_improved(self, text: str) -> str:
        """Extract bidding status with better detection"""
        text_lower = text.lower()
        
        if 'winning' in text_lower:
            return 'Winning'
        elif 'outbid' in text_lower:
            return 'Outbid'
        elif 'ended' in text_lower:
            return 'Ended'
        else:
            return 'Active'
    
    def _extract_time_improved(self, text: str) -> str:
        """Extract exact remaining time with precise patterns"""
        
        # More comprehensive time patterns for exact timing
        time_patterns = [
            # Full "ENDS IN:" patterns with hours and minutes
            r'ENDS IN[^\n]*?(\d+)\s*Hours?[^\n]*?(\d+)\s*Minutes?',
            r'ENDS IN[^\n]*?(\d+)\s*Hour?[^\n]*?(\d+)\s*Minute?',
            
            # Just hours and minutes together
            r'(\d+)\s*Hours?[^\n]*?(\d+)\s*Minutes?',
            r'(\d+)\s*Hour?[^\n]*?(\d+)\s*Minute?',
            
            # Time in HH:MM format
            r'(\d{1,2}):(\d{2})(?:\s*(?:remaining|left))?',
            
            # Individual time units
            r'(\d+)\s*Hours?\s*(?:remaining|left)?',  # "6 Hours"
            r'(\d+)\s*Hour?\s*(?:remaining|left)?',   # "1 Hour" 
            r'(\d+)\s*Minutes?\s*(?:remaining|left)?', # "30 Minutes"
            r'(\d+)\s*Minute?\s*(?:remaining|left)?',  # "1 Minute"
            r'(\d+)\s*Days?\s*(?:remaining|left)?',   # "2 Days"
            r'(\d+)\s*Day?\s*(?:remaining|left)?',    # "1 Day"
            
            # Generic ENDS IN patterns
            r'ENDS IN[^\n]*?([\d\s\w:,]+)',
        ]
        
        # First, try to find hours and minutes combinations
        for pattern in time_patterns[:4]:  # First 4 patterns are for hours + minutes
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                if len(match.groups()) == 2:
                    hours = match.group(1)
                    minutes = match.group(2)
                    return f"{hours}h {minutes}m"
        
        # Then try HH:MM format
        hhmm_match = re.search(r'(\d{1,2}):(\d{2})(?:\s*(?:remaining|left))?', text, re.IGNORECASE)
        if hhmm_match:
            hours = int(hhmm_match.group(1))
            minutes = int(hhmm_match.group(2))
            if hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        
        # Then try individual time units
        for pattern in time_patterns[5:9]:  # Single unit patterns
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                number = match.group(1)
                if 'hour' in pattern.lower():
                    return f"{number}h" if number != '1' else f"{number}h"
                elif 'minute' in pattern.lower():
                    return f"{number}m" if number != '1' else f"{number}m"
                elif 'day' in pattern.lower():
                    return f"{number}d" if number != '1' else f"{number}d"
        
        # Special handling for "ENDS IN" patterns
        ends_in_match = re.search(r'ENDS IN[^\n]*?([\d\s\w:,]+)', text, re.IGNORECASE | re.DOTALL)
        if ends_in_match:
            time_str = ends_in_match.group(1).strip()
            # Parse complex time strings like "6 Hours, 30 Minutes"
            hours_match = re.search(r'(\d+)\s*Hours?', time_str, re.IGNORECASE)
            minutes_match = re.search(r'(\d+)\s*Minutes?', time_str, re.IGNORECASE)
            
            if hours_match and minutes_match:
                return f"{hours_match.group(1)}h {minutes_match.group(1)}m"
            elif hours_match:
                return f"{hours_match.group(1)}h"
            elif minutes_match:
                return f"{minutes_match.group(1)}m"
            else:
                return time_str[:20]  # Return first 20 chars as fallback
        
        # Final fallback - look for any numbers followed by time units
        fallback_patterns = [
            r'(\d+)\s*h(?:ours?)?',
            r'(\d+)\s*m(?:in(?:utes?)?)?',
            r'(\d+)\s*d(?:ays?)?',
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Time Unknown"
    
    def _extract_url(self, element) -> str:
        """Extract item URL"""
        try:
            links = element.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href')
                if href and 'johnpyeauctions.co.uk' in href and 'LotDetails' in href:
                    return href
        except:
            pass
        
        try:
            return element.find_element(By.TAG_NAME, 'a').get_attribute('href')
        except:
            return "https://www.johnpyeauctions.co.uk/Account/Bidding/Active"