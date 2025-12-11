#!/usr/bin/env python3
"""
Super Intelligent Parser - Extremely accurate KPI naming
Uses deep analysis and validation to ensure precision
"""
import sys
import json
import pandas as pd
import numpy as np
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional

class SuperIntelligentParser:
    """Super intelligent parser with extreme accuracy"""
    
    def __init__(self):
        # Comprehensive pattern dictionaries
        self.financial_terms = {
            'revenue': ['revenue', 'sales', 'income', 'earnings', 'proceeds'],
            'expense': ['expense', 'cost', 'spending', 'outgoing', 'expenditure'],
            'profit': ['profit', 'margin', 'gain', 'earnings'],
            'tax': ['tax', 'fee', 'levy', 'duty', 'charge', 'taxamount'],
            'payment': ['payment', 'paid', 'transaction', 'charge', 'amount'],
            'discount': ['discount', 'rebate', 'deduction', 'reduction'],
            'refund': ['refund', 'return', 'reversal'],
            'tip': ['tip', 'tips', 'gratuity', 'gratuities'],
            'deferred': ['deferred', 'pending', 'outstanding']
        }
        
        self.operational_terms = {
            'count': ['count', 'quantity', 'number', 'items', 'units', 'qty', 'total'],
            'average': ['average', 'avg', 'mean', 'per', '/'],
            'total': ['total', 'sum', 'aggregate', 'grand total', 'overall'],
            'percentage': ['percent', 'percentage', 'rate', 'ratio', 'pct', '%']
        }
        
        self.category_terms = {
            'service': ['service', 'mode', 'type', 'method'],
            'payment_method': ['payment type', 'payment method', 'cash', 'credit', 'debit', 'card'],
            'location': ['location', 'place', 'region', 'venue', 'store'],
            'time_period': ['lunch', 'dinner', 'breakfast', 'day', 'night', 'period'],
            'product': ['product', 'item', 'category', 'menu', 'goods']
        }
    
    def analyze_column_with_precision(self, labels: List[str], values: List[float], 
                                     column_index: int, all_columns_data: Dict) -> Dict[str, Any]:
        """
        Ultra-precise column analysis using multiple signals
        Analyzes the COMBINATION of labels to understand what the column represents
        """
        if not labels or not values:
            return self._create_safe_name(column_index, 'unknown')
        
        # Normalize labels
        labels_normalized = [str(l).strip().lower() for l in labels if l]
        labels_text = ' '.join(labels_normalized[:30])  # Use more labels for accuracy
        
        # Statistical analysis
        stats = self._compute_precise_stats(values)
        
        # CRITICAL: Analyze the combination of labels to understand column meaning
        # This is key - a column with "Net sales", "Gratuity", "Tax", "Tips" represents Total Revenue
        column_meaning = self._analyze_label_combination(labels_normalized, labels_text, stats)
        
        # Multi-signal analysis
        signals = {
            'label_analysis': self._analyze_labels_precisely(labels_normalized, labels_text),
            'value_analysis': self._analyze_values_precisely(values, stats),
            'context_analysis': self._analyze_context(labels_normalized, column_index, all_columns_data),
            'pattern_matching': self._precise_pattern_match(labels_text, labels_normalized, stats),
            'column_meaning': column_meaning  # New: combination analysis
        }
        
        # Combine signals with confidence scoring
        result = self._synthesize_signals(signals, labels_text, stats, column_index)
        
        return result
    
    def _analyze_label_combination(self, labels: List[str], labels_text: str, stats: Dict) -> Dict[str, Any]:
        """
        Analyze the combination of labels to understand what the column represents
        This is critical for accuracy - looks at ALL labels together
        """
        # IMPORTANT: Check combinations FIRST (most accurate), then individual labels
        # This ensures we understand the column's true meaning
        # Order matters - check more specific patterns first
        
        # Extract all indicators first
        has_net_sales = any('net sales' in str(l).lower() for l in labels)
        has_gratuity = any('gratuity' in str(l).lower() for l in labels)
        has_tax = any('tax' in str(l).lower() for l in labels)
        has_tips = any('tip' in str(l).lower() and 'tip' != 'tips' or 'tips' in str(l).lower() for l in labels)
        has_total = any(str(l).lower().strip() == 'total' for l in labels)  # Exact match
        has_revenue = any('revenue' in str(l).lower() for l in labels)
        
        # Check for service mode pattern FIRST (more specific than revenue)
        has_service_mode = any('service mode' in str(l).lower() for l in labels)
        has_service_daypart = any('service / day part' in str(l).lower() or 'service/day part' in str(l).lower() for l in labels)
        has_total_guests = any('total guests' in str(l).lower() for l in labels)
        has_avg_guest = any('avg/guest' in str(l).lower() or 'average/guest' in str(l).lower() for l in labels)
        has_total_payments = any('total payments' in str(l).lower() for l in labels)
        has_avg_payment = any('avg/payment' in str(l).lower() or 'average/payment' in str(l).lower() for l in labels)
        has_total_orders = any('total orders' in str(l).lower() for l in labels)
        has_avg_order = any('avg/order' in str(l).lower() or 'average/order' in str(l).lower() for l in labels)
        has_net_sales_in_service = has_net_sales and (has_service_mode or has_service_daypart)
        
        # Service mode pattern - check if this column is in service mode context
        if has_service_mode or has_service_daypart:
            # This is definitely a service mode column
            if has_total_guests:
                return {'name': 'Service Mode - Guest Count', 'confidence': 0.96, 'reason': 'service_guest_count'}
            elif has_avg_guest:
                return {'name': 'Service Mode - Avg per Guest', 'confidence': 0.96, 'reason': 'service_avg_guest'}
            elif has_total_payments:
                return {'name': 'Service Mode - Payment Count', 'confidence': 0.96, 'reason': 'service_payment_count'}
            elif has_avg_payment:
                return {'name': 'Service Mode - Avg per Payment', 'confidence': 0.96, 'reason': 'service_avg_payment'}
            elif has_total_orders:
                return {'name': 'Service Mode - Order Count', 'confidence': 0.96, 'reason': 'service_order_count'}
            elif has_avg_order:
                return {'name': 'Service Mode - Avg per Order', 'confidence': 0.96, 'reason': 'service_avg_order'}
            elif has_net_sales_in_service:
                return {'name': 'Service Mode Sales', 'confidence': 0.95, 'reason': 'service_mode_sales'}
            else:
                return {'name': 'Service Mode Metrics', 'confidence': 0.93, 'reason': 'service_mode'}
        
        # Check for payment type pattern SECOND (before revenue)
        
        # Check for payment type pattern SECOND (before revenue)
        has_payment_type = any('payment type' in str(l).lower() for l in labels)
        has_cash = any(str(l).lower().strip() == 'cash' for l in labels)  # Exact match
        has_credit = any('credit' in str(l).lower() for l in labels)
        has_debit = any('debit' in str(l).lower() for l in labels)
        has_gift_card = any('gift card' in str(l).lower() for l in labels)
        has_other_payment = any(str(l).lower().strip() == 'other' for l in labels)
        
        payment_count = sum([has_payment_type, has_cash, has_credit, has_debit, has_gift_card, has_other_payment])
        
        if payment_count >= 2:
            # This is a payment-related column
            if has_payment_type:
                # Payment type section - check which specific types
                if has_cash and not has_credit and not has_debit:
                    return {'name': 'Cash Payments', 'confidence': 0.95, 'reason': 'cash_only'}
                elif (has_credit or has_debit) and not has_cash:
                    return {'name': 'Credit/Debit Payments', 'confidence': 0.95, 'reason': 'card_only'}
                elif has_cash and (has_credit or has_debit):
                    return {'name': 'Payment Type Amount', 'confidence': 0.95, 'reason': 'payment_type_pattern'}
                else:
                    return {'name': 'Payment Type Amount', 'confidence': 0.94, 'reason': 'payment_type_pattern'}
            elif has_cash:
                return {'name': 'Cash Amount', 'confidence': 0.93, 'reason': 'cash_payment'}
            elif has_credit or has_debit:
                return {'name': 'Credit/Debit Amount', 'confidence': 0.93, 'reason': 'card_payment'}
        
        # Check for revenue summary pattern THIRD (after service and payment)
        revenue_count = sum([has_net_sales, has_gratuity, has_tax, has_tips, has_total, has_revenue])
        
        if revenue_count >= 3:  # Multiple revenue indicators
            if has_total and stats['max'] > 5000:
                return {'name': 'Total Revenue', 'confidence': 0.96, 'reason': 'total_revenue_with_indicators'}
            elif has_net_sales and has_gratuity and has_tax:
                return {'name': 'Total Revenue', 'confidence': 0.95, 'reason': 'revenue_components'}
            elif has_net_sales and has_gratuity:
                return {'name': 'Revenue Summary', 'confidence': 0.93, 'reason': 'revenue_summary'}
            elif has_net_sales:
                return {'name': 'Net Sales', 'confidence': 0.92, 'reason': 'net_sales_primary'}
            else:
                return {'name': 'Revenue Summary', 'confidence': 0.90, 'reason': 'revenue_summary'}
        
        # Check for sales category pattern
        if 'sales category' in labels_text or ('sales' in labels_text and 'category' in labels_text):
            # Check which categories appear
            if 'food' in labels_text:
                return {'name': 'Food Sales', 'confidence': 0.93, 'reason': 'food_category'}
            elif 'wine' in labels_text or 'beer' in labels_text:
                return {'name': 'Beverage Sales', 'confidence': 0.93, 'reason': 'beverage_category'}
            else:
                return {'name': 'Sales by Category', 'confidence': 0.91, 'reason': 'sales_category'}
        
        # Check for revenue center pattern
        if 'revenue center' in labels_text:
            if 'dining room' in labels_text:
                return {'name': 'Dining Room Sales', 'confidence': 0.94, 'reason': 'dining_room'}
            elif 'uber eats' in labels_text:
                return {'name': 'Uber Eats Sales', 'confidence': 0.94, 'reason': 'uber_eats'}
            elif 'doordash' in labels_text:
                return {'name': 'DoorDash Sales', 'confidence': 0.94, 'reason': 'doordash'}
            else:
                return {'name': 'Revenue Center Sales', 'confidence': 0.92, 'reason': 'revenue_center'}
        
        # Check for dining options pattern
        if 'dining option' in labels_text:
            if 'dine in' in labels_text:
                return {'name': 'Dine-In Sales', 'confidence': 0.94, 'reason': 'dine_in'}
            elif 'delivery' in labels_text:
                return {'name': 'Delivery Sales', 'confidence': 0.94, 'reason': 'delivery'}
            elif 'takeout' in labels_text:
                return {'name': 'Takeout Sales', 'confidence': 0.94, 'reason': 'takeout'}
        
        # Check for time period pattern (already handled above, but keep as fallback)
        if has_lunch and not has_sales_category:
            return {'name': 'Lunch Sales', 'confidence': 0.90, 'reason': 'lunch_period'}
        elif has_dinner and not has_sales_category:
            return {'name': 'Dinner Sales', 'confidence': 0.90, 'reason': 'dinner_period'}
        
        # Check for specific metrics with exact label matching
        for label in labels:
            label_lower = str(label).lower().strip()
            if label_lower == 'total guests' and stats.get('is_integer', False):
                return {'name': 'Total Guests', 'confidence': 0.98, 'reason': 'guest_count'}
            elif label_lower == 'total orders' and stats.get('is_integer', False):
                return {'name': 'Total Orders', 'confidence': 0.98, 'reason': 'order_count'}
            elif label_lower == 'total payments' and stats.get('is_integer', False):
                return {'name': 'Total Payments', 'confidence': 0.98, 'reason': 'payment_count'}
            elif label_lower == 'avg/guest' or label_lower == 'average/guest':
                return {'name': 'Average per Guest', 'confidence': 0.98, 'reason': 'avg_per_guest'}
            elif label_lower == 'avg/payment' or label_lower == 'average/payment':
                return {'name': 'Average per Payment', 'confidence': 0.98, 'reason': 'avg_per_payment'}
            elif label_lower == 'avg/order' or label_lower == 'average/order':
                return {'name': 'Average per Order', 'confidence': 0.98, 'reason': 'avg_per_order'}
            elif label_lower == 'net sales':
                # Only return Net Sales if it's the primary indicator (not part of revenue summary)
                if revenue_count < 3:  # Not a revenue summary column
                    return {'name': 'Net Sales', 'confidence': 0.98, 'reason': 'net_sales_exact'}
            elif label_lower == 'gross sales':
                return {'name': 'Gross Sales', 'confidence': 0.98, 'reason': 'gross_sales_exact'}
            elif label_lower == 'tax amount':
                return {'name': 'Tax Amount', 'confidence': 0.98, 'reason': 'tax_amount_exact'}
            elif label_lower in ['tips', 'tip']:
                return {'name': 'Tips', 'confidence': 0.98, 'reason': 'tips_exact'}
            elif label_lower == 'gratuity':
                return {'name': 'Gratuity', 'confidence': 0.98, 'reason': 'gratuity_exact'}
            elif label_lower == 'total' and stats['max'] > 1000:
                return {'name': 'Total Amount', 'confidence': 0.97, 'reason': 'total_exact'}
        
        return {'name': None, 'confidence': 0.0}
    
    def _compute_precise_stats(self, values: List[float]) -> Dict[str, float]:
        """Compute precise statistical measures"""
        if not values:
            return {}
        
        values_array = np.array(values)
        return {
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'mean': float(np.mean(values_array)),
            'median': float(np.median(values_array)),
            'std': float(np.std(values_array)),
            'sum': float(np.sum(values_array)),
            'count': len(values),
            'range': float(np.max(values_array) - np.min(values_array)),
            'is_integer': all(v == int(v) for v in values_array),
            'is_positive': all(v >= 0 for v in values_array),
            'is_percentage_range': 0 <= np.min(values_array) <= 100 and 0 <= np.max(values_array) <= 100
        }
    
    def _analyze_labels_precisely(self, labels: List[str], labels_text: str) -> Dict[str, Any]:
        """Precise label analysis"""
        analysis = {
            'primary_terms': [],
            'secondary_terms': [],
            'category_hints': [],
            'confidence': 0.0
        }
        
        # Find exact matches in financial terms
        for category, terms in self.financial_terms.items():
            matches = [term for term in terms if term in labels_text]
            if matches:
                analysis['primary_terms'].append((category, matches))
        
        # Find operational terms
        for category, terms in self.operational_terms.items():
            matches = [term for term in terms if term in labels_text]
            if matches:
                analysis['secondary_terms'].append((category, matches))
        
        # Find category hints
        for category, terms in self.category_terms.items():
            matches = [term for term in terms if term in labels_text]
            if matches:
                analysis['category_hints'].append((category, matches))
        
        # Calculate confidence based on match quality
        if analysis['primary_terms']:
            analysis['confidence'] = 0.9
        elif analysis['secondary_terms']:
            analysis['confidence'] = 0.7
        else:
            analysis['confidence'] = 0.5
        
        return analysis
    
    def _analyze_values_precisely(self, values: List[float], stats: Dict) -> Dict[str, Any]:
        """Precise value type analysis"""
        analysis = {
            'type': 'unknown',
            'scale': 'unknown',
            'confidence': 0.0
        }
        
        # Percentage detection (precise)
        if stats.get('is_percentage_range', False) and stats['max'] <= 100:
            if stats['max'] <= 100 and stats['min'] >= 0:
                analysis['type'] = 'percentage'
                analysis['confidence'] = 0.95
        
        # Count detection (precise)
        elif stats.get('is_integer', False) and stats['max'] < 10000:
            if stats['mean'] < 1000:
                analysis['type'] = 'count'
                analysis['confidence'] = 0.9
        
        # Amount detection
        elif stats['max'] > 0:
            analysis['type'] = 'amount'
            if stats['max'] > 100000:
                analysis['scale'] = 'large'
            elif stats['max'] > 1000:
                analysis['scale'] = 'medium'
            else:
                analysis['scale'] = 'small'
            analysis['confidence'] = 0.8
        
        return analysis
    
    def _analyze_context(self, labels: List[str], column_index: int, 
                        all_columns_data: Dict) -> Dict[str, Any]:
        """Analyze context from other columns"""
        analysis = {
            'relative_position': column_index / max(len(all_columns_data), 1),
            'similar_columns': [],
            'unique_context': []
        }
        
        # Find similar columns
        for other_idx, other_data in all_columns_data.items():
            if other_idx != column_index:
                other_labels = [str(l).lower() for l in other_data.get('labels', [])]
                common_labels = set(labels) & set(other_labels)
                if len(common_labels) > 2:
                    analysis['similar_columns'].append(other_idx)
        
        return analysis
    
    def _precise_pattern_match(self, labels_text: str, labels: List[str], 
                              stats: Dict) -> Dict[str, Any]:
        """Precise pattern matching with validation"""
        # Check for exact label matches first (highest priority)
        exact_matches = {
            'net sales': {'name': 'Net Sales', 'validation': lambda s: s['max'] > 100},
            'gross sales': {'name': 'Gross Sales', 'validation': lambda s: s['max'] > 100},
            'total': {'name': 'Total Amount', 'validation': lambda s: s['max'] > 1000},
            'tax amount': {'name': 'Tax Amount', 'validation': lambda s: True},
            'tips': {'name': 'Tips', 'validation': lambda s: True},
            'gratuity': {'name': 'Gratuity', 'validation': lambda s: True},
            'total guests': {'name': 'Total Guests', 'validation': lambda s: s['max'] < 10000},
            'total payments': {'name': 'Total Payments', 'validation': lambda s: s['max'] < 10000},
            'total orders': {'name': 'Total Orders', 'validation': lambda s: s['max'] < 10000},
            'avg/guest': {'name': 'Average per Guest', 'validation': lambda s: s['max'] < 10000},
            'avg/payment': {'name': 'Average per Payment', 'validation': lambda s: s['max'] < 10000},
            'avg/order': {'name': 'Average per Order', 'validation': lambda s: s['max'] < 10000}
        }
        
        # Check for exact label matches
        for label in labels:
            label_lower = str(label).lower().strip()
            if label_lower in exact_matches:
                match_data = exact_matches[label_lower]
                try:
                    if match_data['validation'](stats):
                        return {
                            'name': match_data['name'],
                            'confidence': 0.98,
                            'pattern': label_lower
                        }
                except:
                    pass
        
        # Pattern-based matching (secondary priority)
        patterns = {
            'net_sales': {
                'keywords': ['net sales', 'net revenue'],
                'validation': lambda s: s['max'] > 1000,
                'name': 'Net Sales'
            },
            'gross_sales': {
                'keywords': ['gross sales', 'gross revenue'],
                'validation': lambda s: s['max'] > 1000,
                'name': 'Gross Sales'
            },
            'total_revenue': {
                'keywords': ['total', 'revenue summary'],
                'validation': lambda s: s['max'] > 5000,
                'name': 'Total Revenue'
            },
            'revenue_summary': {
                'keywords': ['revenue', 'sales'],
                'validation': lambda s: s['max'] > 1000 and ('net sales' in labels_text or 'gross sales' in labels_text or 'total' in labels_text),
                'name': 'Revenue Summary'
            },
            'tax_amount': {
                'keywords': ['tax amount', 'tax', 'fee'],
                'validation': lambda s: s['max'] < 10000,
                'name': 'Tax Amount'
            },
            'tips_gratuity': {
                'keywords': ['tip', 'tips', 'gratuity'],
                'validation': lambda s: s['max'] < 5000,
                'name': 'Tips & Gratuity'
            },
            'service_mode_sales': {
                'keywords': ['service mode', 'net sales'],
                'validation': lambda s: s['max'] > 1000,
                'name': 'Service Mode Sales'
            },
            'payment_type_amount': {
                'keywords': ['payment type', 'cash', 'credit', 'debit'],
                'validation': lambda s: s['max'] > 0,
                'name': 'Payment Type Amount'
            },
            'guest_count': {
                'keywords': ['total guests', 'guests', 'guest'],
                'validation': lambda s: (s.get('is_integer', False) and s['max'] < 10000) or s['max'] < 500,
                'name': 'Guest Count'
            },
            'order_count': {
                'keywords': ['total orders', 'orders', 'order'],
                'validation': lambda s: (s.get('is_integer', False) and s['max'] < 10000) or s['max'] < 500,
                'name': 'Order Count'
            },
            'payment_count': {
                'keywords': ['total payments', 'payments'],
                'validation': lambda s: (s.get('is_integer', False) and s['max'] < 10000) or s['max'] < 500,
                'name': 'Payment Count'
            },
            'average_per_guest': {
                'keywords': ['avg/guest', 'average/guest', 'per guest'],
                'validation': lambda s: s['max'] < 10000,
                'name': 'Average per Guest'
            },
            'average_per_payment': {
                'keywords': ['avg/payment', 'average/payment', 'per payment'],
                'validation': lambda s: s['max'] < 10000,
                'name': 'Average per Payment'
            },
            'average_per_order': {
                'keywords': ['avg/order', 'average/order', 'per order'],
                'validation': lambda s: s['max'] < 10000,
                'name': 'Average per Order'
            }
        }
        
        best_match = None
        best_score = 0
        
        for pattern_name, pattern_data in patterns.items():
            # Check keyword matches - prioritize exact phrase matches
            keyword_matches = 0
            for kw in pattern_data['keywords']:
                if kw in labels_text:
                    # Exact phrase match gets higher score
                    if any(kw in label.lower() for label in labels):
                        keyword_matches += 2
                    else:
                        keyword_matches += 1
            
            if keyword_matches > 0:
                # Validate with stats
                try:
                    if pattern_data['validation'](stats):
                        score = keyword_matches * 10  # Weight keyword matches
                        if score > best_score:
                            best_score = score
                            best_match = {
                                'name': pattern_data['name'],
                                'confidence': min(0.95, 0.75 + (keyword_matches * 0.05)),
                                'pattern': pattern_name
                            }
                except:
                    pass
        
        return best_match or {'name': None, 'confidence': 0.0}
    
    def _synthesize_signals(self, signals: Dict, labels_text: str, 
                           stats: Dict, column_index: int) -> Dict[str, Any]:
        """Synthesize all signals into final result"""
        column_meaning = signals.get('column_meaning', {})
        pattern_match = signals['pattern_matching']
        label_analysis = signals['label_analysis']
        value_analysis = signals['value_analysis']
        
        # Priority 1: Column meaning from label combination (HIGHEST confidence - most accurate)
        if column_meaning.get('confidence', 0) > 0.9:
            return {
                'display_name': column_meaning['name'],
                'description': self._create_precise_description(column_meaning['name'], stats),
                'confidence': column_meaning['confidence'],
                'value_type': value_analysis.get('type', 'amount'),
                'value_scale': value_analysis.get('scale', 'medium')
            }
        
        # Priority 2: Precise pattern match
        if pattern_match.get('confidence', 0) > 0.8:
            return {
                'display_name': pattern_match['name'],
                'description': self._create_precise_description(pattern_match['name'], stats),
                'confidence': pattern_match['confidence'],
                'value_type': value_analysis.get('type', 'amount'),
                'value_scale': value_analysis.get('scale', 'medium')
            }
        
        # Priority 2: Strong label + value combination
        if label_analysis.get('confidence', 0) > 0.7 and value_analysis.get('confidence', 0) > 0.7:
            primary_term = label_analysis['primary_terms'][0][0] if label_analysis['primary_terms'] else None
            secondary_term = label_analysis['secondary_terms'][0][0] if label_analysis['secondary_terms'] else None
            
            if primary_term:
                name = self._construct_name_from_terms(primary_term, secondary_term, labels_text, stats)
                return {
                    'display_name': name,
                    'description': self._create_precise_description(name, stats),
                    'confidence': 0.85,
                    'value_type': value_analysis.get('type', 'amount'),
                    'value_scale': value_analysis.get('scale', 'medium')
                }
        
        # Priority 3: Value type + context
        if value_analysis.get('confidence', 0) > 0.7:
            name = self._construct_name_from_value_type(value_analysis, labels_text, stats, column_index)
            return {
                'display_name': name,
                'description': self._create_precise_description(name, stats),
                'confidence': 0.75,
                'value_type': value_analysis.get('type', 'amount'),
                'value_scale': value_analysis.get('scale', 'medium')
            }
        
        # Fallback: Safe generic name
        return self._create_safe_name(column_index, value_analysis.get('type', 'unknown'))
    
    def _construct_name_from_terms(self, primary: str, secondary: Optional[str], 
                                   labels_text: str, stats: Dict) -> str:
        """Construct precise name from terms"""
        # Check for exact label matches first
        for label in labels_text.split():
            label_lower = label.lower()
            if label_lower == 'sales' and 'net' in labels_text:
                return 'Net Sales'
            elif label_lower == 'sales' and 'gross' in labels_text:
                return 'Gross Sales'
            elif label_lower == 'sales':
                return 'Sales Amount'
            elif label_lower == 'revenue':
                return 'Revenue Amount'
            elif label_lower == 'tax':
                return 'Tax Amount'
            elif label_lower in ['tip', 'tips']:
                return 'Tips'
            elif label_lower == 'gratuity':
                return 'Gratuity'
        
        # Check for modifiers
        if 'net' in labels_text:
            prefix = 'Net '
        elif 'gross' in labels_text:
            prefix = 'Gross '
        elif 'total' in labels_text:
            prefix = 'Total '
        else:
            prefix = ''
        
        # Primary term
        primary_name = primary.replace('_', ' ').title()
        
        # Secondary term
        if secondary:
            if secondary == 'average':
                return f'{prefix}Average {primary_name}'
            elif secondary == 'count':
                return f'{primary_name} Count'
            elif secondary == 'total':
                return f'Total {primary_name}'
        
        # Check for category hints with more precision
        if 'payment type' in labels_text or ('payment' in labels_text and 'type' in labels_text):
            return f'{prefix}{primary_name} (Payment Type)'
        elif 'service mode' in labels_text or ('service' in labels_text and 'mode' in labels_text):
            return f'{prefix}{primary_name} (Service Mode)'
        elif 'lunch' in labels_text:
            return f'{prefix}{primary_name} (Lunch)'
        elif 'dinner' in labels_text:
            return f'{prefix}{primary_name} (Dinner)'
        elif 'cash' in labels_text and 'payment' not in labels_text:
            return 'Cash Amount'
        elif 'credit' in labels_text or 'debit' in labels_text:
            return 'Credit/Debit Amount'
        
        return f'{prefix}{primary_name}'
    
    def _construct_name_from_value_type(self, value_analysis: Dict, labels_text: str, 
                                       stats: Dict, column_index: int) -> str:
        """Construct name from value type analysis"""
        value_type = value_analysis.get('type', 'amount')
        scale = value_analysis.get('scale', 'medium')
        
        if value_type == 'count':
            # Try to infer what is being counted
            if 'guest' in labels_text:
                return 'Guest Count'
            elif 'order' in labels_text:
                return 'Order Count'
            elif 'payment' in labels_text:
                return 'Payment Count'
            else:
                return 'Item Count'
        
        elif value_type == 'percentage':
            return 'Percentage'
        
        elif value_type == 'amount':
            # Use scale and context
            if scale == 'large':
                if 'total' in labels_text:
                    return 'Total Amount'
                else:
                    return 'Large Amount'
            elif scale == 'medium':
                return 'Amount'
            else:
                return 'Small Amount'
        
        return f'Column {column_index}'
    
    def _create_precise_description(self, name: str, stats: Dict) -> str:
        """Create precise description"""
        if 'Sales' in name or 'Revenue' in name:
            return f'Sales and revenue amounts (Range: ${stats.get("min", 0):.2f} - ${stats.get("max", 0):.2f})'
        elif 'Tax' in name:
            return f'Tax and fee amounts (Total: ${stats.get("sum", 0):.2f})'
        elif 'Tip' in name or 'Gratuity' in name:
            return f'Tips and gratuity amounts (Total: ${stats.get("sum", 0):.2f})'
        elif 'Count' in name:
            return f'Count of items (Total: {int(stats.get("sum", 0))} items)'
        elif 'Average' in name:
            return f'Average value (Mean: ${stats.get("mean", 0):.2f})'
        elif 'Payment' in name:
            return f'Payment transaction amounts (Total: ${stats.get("sum", 0):.2f})'
        else:
            return f'{name} values (Range: {stats.get("min", 0):.2f} - {stats.get("max", 0):.2f})'
    
    def _improve_generic_name(self, labels: List[str], values: List[float], 
                             column_index: int, all_columns_data: Dict) -> Optional[Dict[str, Any]]:
        """Try to improve a generic name with deeper analysis"""
        if not labels or not values:
            return None
        
        labels_normalized = [str(l).strip().lower() for l in labels if l]
        labels_text = ' '.join(labels_normalized[:30])
        stats = self._compute_precise_stats(values)
        
        # Check for revenue summary pattern FIRST (highest priority - multiple revenue components)
        has_net_sales = any('net sales' in l for l in labels_normalized)
        has_gratuity = any('gratuity' in l for l in labels_normalized)
        has_tax = any('tax' in l for l in labels_normalized)
        has_tips = any('tip' in l for l in labels_normalized)
        has_total = any(str(l).strip() == 'total' for l in labels)
        revenue_count = sum([has_net_sales, has_gratuity, has_tax, has_tips, has_total])
        
        if revenue_count >= 3 and stats['max'] > 1000:
            if has_total and stats['max'] > 5000:
                return {'display_name': 'Total Revenue', 'confidence': 0.96, 'value_type': 'amount'}
            elif has_net_sales and has_gratuity and has_tax:
                return {'display_name': 'Total Revenue', 'confidence': 0.95, 'value_type': 'amount'}
        
        # Check for service mode indicators SECOND (more specific)
        has_service_mode = any('service mode' in l or 'service / day part' in l for l in labels_normalized)
        if has_service_mode:
            if any('net sales' in l for l in labels_normalized):
                return {'display_name': 'Service Mode Sales', 'confidence': 0.93, 'value_type': 'amount'}
            elif any('total guests' in l for l in labels_normalized):
                return {'display_name': 'Service Mode - Guest Count', 'confidence': 0.93, 'value_type': 'count'}
            elif any('avg/guest' in l for l in labels_normalized):
                return {'display_name': 'Service Mode - Avg per Guest', 'confidence': 0.93, 'value_type': 'amount'}
            elif any('avg/payment' in l for l in labels_normalized):
                return {'display_name': 'Service Mode - Avg per Payment', 'confidence': 0.93, 'value_type': 'amount'}
            elif any('avg/order' in l for l in labels_normalized):
                return {'display_name': 'Service Mode - Avg per Order', 'confidence': 0.93, 'value_type': 'amount'}
        
        # Check for delivery service pattern (Uber Eats, DoorDash) - SECOND PRIORITY
        has_uber_eats = any('uber eats' in l for l in labels_normalized)
        has_doordash = any('doordash' in l or 'door dash' in l for l in labels_normalized)
        if has_uber_eats or has_doordash:
            if has_uber_eats and has_doordash:
                return {'display_name': 'Delivery Service Sales', 'confidence': 0.94, 'value_type': 'amount'}
            elif has_uber_eats:
                return {'display_name': 'Uber Eats Sales', 'confidence': 0.95, 'value_type': 'amount'}
            elif has_doordash:
                return {'display_name': 'DoorDash Sales', 'confidence': 0.95, 'value_type': 'amount'}
        
        # Check for payment type section - be more specific
        has_payment_type = any('payment type' in l for l in labels_normalized)
        has_cash_exact = any(str(l).strip().lower() == 'cash' for l in labels)
        has_credit_debit = any('credit' in l.lower() or 'debit' in l.lower() for l in labels)
        has_gift_card = any('gift card' in l.lower() for l in labels)
        has_other = any(str(l).strip().lower() == 'other' for l in labels)
        
        # Payment type section - if it has payment type label AND multiple payment methods
        if has_payment_type and (has_cash_exact or has_credit_debit or has_gift_card or has_other):
            # Count how many payment methods
            payment_methods = sum([has_cash_exact, has_credit_debit, has_gift_card, has_other])
            if payment_methods >= 2:
                return {'display_name': 'Payment Type Amount', 'confidence': 0.93, 'value_type': 'amount'}
            elif has_cash_exact:
                return {'display_name': 'Cash Payments', 'confidence': 0.92, 'value_type': 'amount'}
            elif has_credit_debit:
                return {'display_name': 'Credit/Debit Payments', 'confidence': 0.92, 'value_type': 'amount'}
        
        # Also check if it's a payment column without the "payment type" label but has multiple payment methods
        if not has_service_mode and not has_uber_eats and not has_doordash:
            if (has_cash_exact and has_credit_debit) or (has_cash_exact and has_gift_card) or (has_credit_debit and has_gift_card):
                return {'display_name': 'Payment Type Amount', 'confidence': 0.91, 'value_type': 'amount'}
        
        # Check for sales category
        has_food = any('food' in l for l in labels_normalized)
        has_beverage = any('beverage' in l or 'wine' in l or 'beer' in l for l in labels_normalized)
        has_lunch = any('lunch' in l for l in labels_normalized)
        has_dinner = any('dinner' in l for l in labels_normalized)
        
        if has_food or has_beverage:
            if has_food and not has_beverage:
                return {'display_name': 'Food Sales', 'confidence': 0.92, 'value_type': 'amount'}
            elif has_beverage and not has_food:
                return {'display_name': 'Beverage Sales', 'confidence': 0.92, 'value_type': 'amount'}
            elif has_lunch:
                return {'display_name': 'Lunch Sales', 'confidence': 0.91, 'value_type': 'amount'}
            elif has_dinner:
                return {'display_name': 'Dinner Sales', 'confidence': 0.91, 'value_type': 'amount'}
            else:
                return {'display_name': 'Sales by Category', 'confidence': 0.90, 'value_type': 'amount'}
        
        # Check for revenue center
        if any('revenue center' in l for l in labels_normalized):
            if any('dining room' in l for l in labels_normalized):
                return {'display_name': 'Dining Room Sales', 'confidence': 0.92, 'value_type': 'amount'}
            elif has_uber_eats:
                return {'display_name': 'Uber Eats Sales', 'confidence': 0.92, 'value_type': 'amount'}
        
        return None
    
    def _find_best_context_label(self, unique_labels: List[str], all_labels: List[str]) -> Optional[str]:
        """Find the best label to use as context"""
        if not unique_labels:
            return None
        
        # Prioritize meaningful labels
        priority_keywords = ['service mode', 'payment type', 'revenue center', 'sales category', 
                           'dining room', 'uber eats', 'cash', 'credit', 'debit', 'lunch', 'dinner']
        
        for label in unique_labels:
            label_lower = str(label).lower()
            for keyword in priority_keywords:
                if keyword in label_lower:
                    # Extract a short, meaningful context
                    if len(label) <= 25:
                        return label[:25]
                    else:
                        # Extract the key part
                        for kw in priority_keywords:
                            if kw in label_lower:
                                idx = label_lower.find(kw)
                                start = max(0, idx - 5)
                                end = min(len(label), idx + len(kw) + 10)
                                return label[start:end].strip()
        
        # Use the shortest unique label
        shortest = min(unique_labels, key=len)
        return shortest[:25] if len(shortest) <= 25 else shortest[:22] + '...'
    
    def _create_safe_name(self, column_index: int, value_type: str) -> Dict[str, Any]:
        """Create a safe fallback name"""
        return {
            'display_name': f'Data Column {column_index}',
            'description': f'Data values from column {column_index}',
            'confidence': 0.5,
            'value_type': value_type,
            'value_scale': 'unknown'
        }
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse file with super intelligence"""
        try:
            # Read file
            try:
                df_raw = pd.read_excel(file_path, header=None)
            except:
                df_raw = pd.read_csv(file_path, header=None)
            
            # Detect structure
            structure_type = self._detect_structure(df_raw)
            
            if structure_type == 'summary_report':
                return self._parse_summary_format_precise(df_raw)
            else:
                return self._parse_standard_table_precise(df_raw)
                
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_structure(self, df: pd.DataFrame) -> str:
        """Detect structure type"""
        if df.shape[1] > 1:
            first_col_text_ratio = df.iloc[:, 0].astype(str).str.contains(r'[a-zA-Z]', regex=True).sum() / len(df)
            other_cols_numeric_ratio = 0
            
            for col_idx in range(1, min(6, df.shape[1])):
                numeric_count = pd.to_numeric(df.iloc[:, col_idx], errors='coerce').notna().sum()
                other_cols_numeric_ratio += numeric_count / len(df)
            
            other_cols_numeric_ratio /= (df.shape[1] - 1)
            
            if first_col_text_ratio > 0.5 and other_cols_numeric_ratio < 0.3:
                return 'summary_report'
        
        return 'standard_table'
    
    def _parse_summary_format_precise(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """Parse summary format with precision"""
        data_rows = []
        current_section = None
        
        for idx, row in df_raw.iterrows():
            first_col = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            
            if not first_col or first_col == 'nan':
                continue
            
            # Detect section headers
            if any(kw in first_col.lower() for kw in ['summary', 'report', 'section']):
                if len(first_col) < 50:
                    current_section = first_col
                    continue
            
            # Find numeric values
            row_values = {}
            for col_idx in range(1, len(row)):
                val = row.iloc[col_idx]
                if pd.notna(val):
                    try:
                        float_val = float(val)
                        row_values[col_idx] = float_val
                    except:
                        pass
            
            if row_values:
                data_rows.append({
                    'label': first_col,
                    'section': current_section or 'Main',
                    'values': row_values
                })
        
        # Build column data for analysis
        all_col_indices = sorted(set().union(*[row['values'].keys() for row in data_rows]))
        
        # Collect all column data for context analysis
        all_columns_data = {}
        for col_idx in all_col_indices:
            labels_in_col = []
            values_in_col = []
            for row in data_rows:
                if col_idx in row['values']:
                    labels_in_col.append(row['label'])
                    values_in_col.append(row['values'][col_idx])
            all_columns_data[col_idx] = {
                'labels': labels_in_col,
                'values': values_in_col
            }
        
        # Intelligently name columns with precision
        column_names = {}
        column_metadata_list = []
        used_names = {}  # Track used names to avoid duplicates
        
        for col_idx in all_col_indices:
            col_data = all_columns_data[col_idx]
            analysis = self.analyze_column_with_precision(
                col_data['labels'], col_data['values'], col_idx, all_columns_data
            )
            
            # ALWAYS try to improve names with better analysis (run improvement first)
            improved_analysis = self._improve_generic_name(col_data['labels'], col_data['values'], col_idx, all_columns_data)
            if improved_analysis and improved_analysis.get('confidence', 0) > 0.80:
                # Use improved name if it's better
                base_name = improved_analysis['display_name']
                stats = self._compute_precise_stats(col_data['values'])
                analysis = {
                    'display_name': improved_analysis['display_name'],
                    'description': self._create_precise_description(improved_analysis['display_name'], stats),
                    'confidence': improved_analysis.get('confidence', 0.85),
                    'value_type': improved_analysis.get('value_type', 'amount'),
                    'value_scale': analysis.get('value_scale', 'medium')
                }
            else:
                # Use original analysis
                base_name = analysis['display_name']
            
            final_name = base_name
            
            if base_name in used_names:
                # Add meaningful context from unique labels
                other_col_data = all_columns_data[used_names[base_name]]
                unique_labels = set(col_data['labels']) - set(other_col_data['labels'])
                
                if unique_labels:
                    # Find the most distinctive label
                    context_label = self._find_best_context_label(list(unique_labels), col_data['labels'])
                    if context_label:
                        final_name = f'{base_name} ({context_label})'
                    else:
                        final_name = f'{base_name} - Column {col_idx}'
                else:
                    # Use position-based naming only as last resort
                    position_names = {1: 'Primary', 2: 'Secondary', 3: 'Tertiary'}
                    if col_idx in position_names:
                        final_name = f'{base_name} ({position_names[col_idx]})'
                    else:
                        final_name = f'{base_name} - Column {col_idx}'
            
            used_names[final_name] = col_idx
            column_names[col_idx] = final_name
            
            # Ensure description exists
            description = analysis.get('description', self._create_precise_description(final_name, self._compute_precise_stats(col_data['values'])))
            
            column_metadata_list.append({
                'original': f'Column_{col_idx}',
                'clean': f'Column_{col_idx}',
                'display_name': final_name,
                'type': 'numeric',
                'description': description,
                'confidence': analysis.get('confidence', 0.5),
                'value_type': analysis.get('value_type', 'amount'),
                'value_scale': analysis.get('value_scale', 'medium')
            })
        
        # Build structured data
        structured_data = []
        for row in data_rows:
            record = {'Label': row['label'], 'Section': row['section']}
            for col_idx in all_col_indices:
                col_name = column_names.get(col_idx, f'Column_{col_idx}')
                record[col_name] = row['values'].get(col_idx, None)
            structured_data.append(record)
        
        df = pd.DataFrame(structured_data)
        
        # Process numeric columns - be more lenient to capture all numeric data
        numeric_columns = []
        categorical_columns = ['Label', 'Section']
        
        for col in df.columns:
            if col not in ['Label', 'Section']:
                converted = pd.to_numeric(df[col], errors='coerce')
                # Lower threshold to capture more columns (at least 1 value or 10% of rows)
                non_null_count = converted.notna().sum()
                if non_null_count > 0 and non_null_count >= max(1, len(df) * 0.1):  # At least 1 value or 10% of rows
                    df[col] = converted
                    numeric_columns.append(col)
                else:
                    categorical_columns.append(col)
        
        return {
            'data': df.replace({np.nan: None}).to_dict('records'),
            'columns': df.columns.tolist(),
            'column_metadata': column_metadata_list,
            'shape': [int(df.shape[0]), int(df.shape[1])],
            'numericColumns': numeric_columns,
            'categoricalColumns': categorical_columns,
            'totalRows': int(df.shape[0]),
            'format': 'summary_report'
        }
    
    def _parse_standard_table_precise(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """Parse standard table with precision"""
        # Detect header
        header_row = None
        for idx in range(min(5, len(df_raw))):
            row = df_raw.iloc[idx]
            text_count = sum(1 for val in row if pd.notna(val) and isinstance(val, str))
            if text_count > len(row) * 0.5:
                header_row = idx
                break
        
        if header_row is not None:
            df = df_raw.iloc[header_row+1:].copy()
            df.columns = df_raw.iloc[header_row].values
            df = df.reset_index(drop=True)
        else:
            df = df_raw.copy()
            df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
        
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Process columns
        numeric_columns = []
        categorical_columns = []
        column_metadata_list = []
        
        all_columns_data = {}
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if converted.notna().sum() / len(df) > 0.5:
                df[col] = converted
                numeric_columns.append(col)
                all_columns_data[col] = {
                    'labels': [str(col)],
                    'values': df[col].dropna().tolist()
                }
            else:
                categorical_columns.append(col)
        
        # Analyze numeric columns
        for col in numeric_columns:
            col_data = all_columns_data[col]
            analysis = self.analyze_column_with_precision(
                col_data['labels'], col_data['values'], 
                numeric_columns.index(col), all_columns_data
            )
            column_metadata_list.append({
                'original': str(col),
                'clean': str(col),
                'display_name': analysis['display_name'],
                'type': 'numeric',
                'description': analysis['description'],
                'confidence': analysis.get('confidence', 0.5)
            })
        
        return {
            'data': df.replace({np.nan: None}).to_dict('records'),
            'columns': df.columns.tolist(),
            'column_metadata': column_metadata_list,
            'shape': [int(df.shape[0]), int(df.shape[1])],
            'numericColumns': numeric_columns,
            'categoricalColumns': categorical_columns,
            'totalRows': int(df.shape[0]),
            'format': 'standard_table'
        }


def parse_file_super_intelligently(file_path: str) -> Dict[str, Any]:
    """Main entry point"""
    parser = SuperIntelligentParser()
    result = parser.parse_file(file_path)
    
    print(json.dumps(result), file=sys.stdout)
    sys.stdout.flush()
    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Missing file path'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    parse_file_super_intelligently(file_path)

