#!/usr/bin/env python3
"""
Auction Item data class for representing individual auction items.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import re


@dataclass
class AuctionItem:
    """Represents an auction item from John Pye Auctions."""
    
    title: str
    lot_number: str
    current_bid: str
    end_time: str
    url: str
    last_updated: Optional[datetime] = None
    previous_bid: Optional[str] = None
    bid_count: Optional[int] = None
    reserve_met: Optional[bool] = None
    
    def __post_init__(self):
        """Initialize additional fields after object creation."""
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def parse_bid_amount(self) -> float:
        """Parse the current bid amount as a float."""
        try:
            # Remove currency symbols and commas, extract numeric value
            bid_str = re.sub(r'[£,$]', '', self.current_bid)
            bid_str = bid_str.replace(',', '')
            return float(bid_str)
        except (ValueError, TypeError):
            return 0.0
    
    def parse_lot_number(self) -> str:
        """Extract clean lot number from the lot number string."""
        try:
            # Remove "Lot " prefix if present
            lot_num = re.sub(r'^Lot\s*', '', self.lot_number, flags=re.IGNORECASE)
            return lot_num.strip()
        except (AttributeError, TypeError):
            return self.lot_number or ""
    
    def has_bid_increased(self, previous_item: 'AuctionItem') -> bool:
        """Check if the bid has increased compared to a previous version."""
        try:
            current_amount = self.parse_bid_amount()
            previous_amount = previous_item.parse_bid_amount()
            return current_amount > previous_amount
        except (AttributeError, TypeError):
            return False
    
    def time_remaining(self) -> str:
        """Calculate time remaining until auction ends."""
        # This would need to be implemented based on the actual format
        # of the end_time string from the website
        return self.end_time
    
    def is_ending_soon(self, threshold_minutes: int = 60) -> bool:
        """Check if auction is ending within the specified threshold."""
        # Implementation would depend on parsing the end_time format
        # For now, return False as placeholder
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the auction item to a dictionary for serialization."""
        return {
            'title': self.title,
            'lot_number': self.lot_number,
            'current_bid': self.current_bid,
            'current_bid_amount': self.parse_bid_amount(),
            'end_time': self.end_time,
            'url': self.url,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'previous_bid': self.previous_bid,
            'bid_count': self.bid_count,
            'reserve_met': self.reserve_met
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuctionItem':
        """Create an AuctionItem from a dictionary."""
        # Convert ISO format back to datetime if present
        last_updated = None
        if data.get('last_updated'):
            try:
                last_updated = datetime.fromisoformat(data['last_updated'])
            except ValueError:
                pass
        
        return cls(
            title=data.get('title', ''),
            lot_number=data.get('lot_number', ''),
            current_bid=data.get('current_bid', ''),
            end_time=data.get('end_time', ''),
            url=data.get('url', ''),
            last_updated=last_updated,
            previous_bid=data.get('previous_bid'),
            bid_count=data.get('bid_count'),
            reserve_met=data.get('reserve_met')
        )
    
    def __str__(self) -> str:
        """String representation of the auction item."""
        return f"Lot {self.lot_number}: {self.title} - {self.current_bid}"
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"AuctionItem(title='{self.title}', "
                f"lot_number='{self.lot_number}', "
                f"current_bid='{self.current_bid}', "
                f"end_time='{self.end_time}')")