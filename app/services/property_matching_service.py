import pandas as pd
from typing import List, Dict, Any, Optional
import re
import os
import logging

logger = logging.getLogger(__name__)

class PropertyMatchingService:
    def __init__(self):
        self.properties_df = None
        self._load_properties()
    
    def _load_properties(self):
        """Load property data from CSV"""
        try:
            csv_path = "data/properties.csv"
            if os.path.exists(csv_path):
                self.properties_df = pd.read_csv(csv_path)
                logger.info(f"Loaded {len(self.properties_df)} properties from {csv_path}")
            else:
                logger.warning(f"Property CSV not found at {csv_path}, creating sample data")
                self._create_sample_data()
        except Exception as e:
            logger.error(f"Failed to load properties: {str(e)}")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample property data"""
        sample_data = {
            'unique_id': ['PROP001', 'PROP002', 'PROP003'],
            'Property Address': [
                '123 Innovation Drive Downtown',
                '456 Tech Plaza Midtown', 
                '789 Business Center Uptown'
            ],
            'Floor': [5, 8, 3],
            'Suite': ['A', 'B', 'C'],
            'Size (SF)': [2500, 3200, 1800],
            'Rent/SF/Year': [28.00, 32.00, 25.00],
            'Associate 1': ['John Smith', 'Lisa Brown', 'David Miller'],
            'BROKER Email ID': ['john@broker.com', 'lisa@broker.com', 'david@broker.com'],
            'Annual Rent': [70000, 102400, 45000],
            'Monthly Rent': [5833.33, 8533.33, 3750.00],
            'GCI On 3 Years': [210000, 307200, 135000]
        }
        self.properties_df = pd.DataFrame(sample_data)
        logger.info("Created sample property data")
    
    async def get_property_recommendations(
        self,
        conversation_history: List[Dict[str, str]],
        emotion_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Get property recommendations based on conversation and emotions"""
        
        # Extract requirements from conversation
        requirements = self._extract_requirements(conversation_history)
        
        # Apply emotion-based filtering
        if emotion_data:
            requirements = self._apply_emotion_filters(requirements, emotion_data)
        
        # Find matching properties
        matching_properties = self._find_matching_properties(requirements)
        
        # Format recommendations
        return self._format_property_recommendations(matching_properties, requirements)
    
    def _extract_requirements(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract property requirements from conversation"""
        requirements = {
            'min_size': None,
            'max_size': None,
            'max_rent_per_sf': None,
            'preferred_locations': [],
            'company_size': None,
            'industry': None,
            'culture_keywords': [],
            'must_haves': [],
            'nice_to_haves': []
        }
        
        # Analyze conversation for requirements
        full_conversation = ' '.join([msg['content'] for msg in conversation_history])
        text_lower = full_conversation.lower()
        
        # Extract size requirements using regex
        size_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*(?:sq\.?\s*ft\.?|square\s*feet?|sf)',
            r'(\d+)\s*people',
            r'team\s*of\s*(\d+)',
            r'(\d+)\s*employees'
        ]
        
        sizes = []
        for pattern in size_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    if 'people' in pattern or 'team' in pattern or 'employees' in pattern:
                        # Convert people to square feet (100-150 sf per person)
                        size = int(match.replace(',', '')) * 125
                    else:
                        size = int(match.replace(',', ''))
                    sizes.append(size)
                except:
                    continue
        
        if sizes:
            requirements['min_size'] = min(sizes)
            requirements['max_size'] = max(sizes) if len(sizes) > 1 else min(sizes) * 1.5
        
        # Extract budget requirements
        budget_patterns = [
            r'\$(\d+(?:\.\d{2})?)\s*(?:per\s*)?(?:sq\.?\s*ft\.?|square\s*foot|sf)',
            r'\$(\d{1,3}(?:,\d{3})*)\s*(?:per\s*)?month',
            r'budget.*?\$(\d{1,3}(?:,\d{3})*)'
        ]
        
        for pattern in budget_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                try:
                    budget = float(matches[0].replace(',', ''))
                    if 'month' in pattern:
                        # Convert monthly to per sf (assume 2000 sf average)
                        budget = (budget * 12) / 2000
                    requirements['max_rent_per_sf'] = budget
                    break
                except:
                    continue
        
        # Extract location preferences
        location_keywords = ['downtown', 'uptown', 'midtown', 'district', 'center']
        for keyword in location_keywords:
            if keyword in text_lower:
                requirements['preferred_locations'].append(keyword)
        
        # Extract culture keywords
        culture_keywords = [
            'collaborative', 'modern', 'traditional', 'creative', 'corporate', 
            'startup', 'professional', 'casual', 'innovative', 'tech'
        ]
        for keyword in culture_keywords:
            if keyword in text_lower:
                requirements['culture_keywords'].append(keyword)
        
        return requirements
    
    def _apply_emotion_filters(self, requirements: Dict[str, Any], emotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply emotion-based filtering to requirements"""
        
        enthusiasm_level = emotion_data.get('enthusiasm_level', 0.5)
        tone_analysis = emotion_data.get('tone_analysis', {})
        
        # High enthusiasm = willing to pay more, consider larger spaces
        if enthusiasm_level > 0.7:
            if requirements['max_rent_per_sf']:
                requirements['max_rent_per_sf'] *= 1.2
            if requirements['max_size']:
                requirements['max_size'] *= 1.1
        
        # Excited tone = prefer modern, innovative spaces
        if tone_analysis.get('excited', 0) > 0.6:
            requirements['culture_keywords'].extend(['modern', 'innovative', 'tech'])
        
        # Professional tone = prefer established areas
        if tone_analysis.get('professional', 0) > 0.7:
            requirements['culture_keywords'].extend(['professional', 'corporate'])
        
        return requirements
    
    def _find_matching_properties(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find properties matching the requirements"""
        if self.properties_df is None or self.properties_df.empty:
            return []
        
        filtered_df = self.properties_df.copy()
        
        # Apply size filters
        if requirements['min_size']:
            filtered_df = filtered_df[filtered_df['Size (SF)'] >= requirements['min_size']]
        
        if requirements['max_size']:
            filtered_df = filtered_df[filtered_df['Size (SF)'] <= requirements['max_size']]
        
        # Apply rent filters
        if requirements['max_rent_per_sf']:
            filtered_df = filtered_df[filtered_df['Rent/SF/Year'] <= requirements['max_rent_per_sf']]
        
        # Apply location filters
        if requirements['preferred_locations']:
            location_mask = filtered_df['Property Address'].str.contains(
                '|'.join(requirements['preferred_locations']), 
                case=False, 
                na=False
            )
            filtered_df = filtered_df[location_mask]
        
        # Calculate culture match scores
        if requirements['culture_keywords']:
            culture_scores = []
            for _, row in filtered_df.iterrows():
                property_text = f"{row['Property Address']}".lower()
                score = sum(1 for keyword in requirements['culture_keywords'] 
                          if keyword.lower() in property_text)
                culture_scores.append(score)
            
            filtered_df = filtered_df.copy()
            filtered_df['culture_score'] = culture_scores
            filtered_df = filtered_df.sort_values('culture_score', ascending=False)
        
        # Return top 3 matches
        return filtered_df.head(3).to_dict('records')
    
    def _format_property_recommendations(self, properties: List[Dict[str, Any]], requirements: Dict[str, Any]) -> str:
        """Format property recommendations for LLM context"""
        
        if not properties:
            return "I don't have any properties that exactly match your criteria right now, but let me search for alternatives."
        
        formatted_recommendations = []
        
        for prop in properties:
            recommendation = f"""
Property: {prop['Property Address']}
- Size: {prop['Size (SF)']:,} square feet
- Floor: {prop['Floor']}, Suite: {prop['Suite']}
- Rent: ${prop['Rent/SF/Year']}/SF/year (${prop['Monthly Rent']:,.2f}/month)
- Annual Rent: ${prop['Annual Rent']:,.2f}
- Contact: {prop['Associate 1']} ({prop['BROKER Email ID']})
            """.strip()
            
            if 'culture_score' in prop and prop['culture_score'] > 0:
                recommendation += f"\n- Culture Match: High"
            
            formatted_recommendations.append(recommendation)
        
        context = f"""
Based on your conversation, here are my top property recommendations:

{chr(10).join(formatted_recommendations)}

Requirements detected:
- Size range: {requirements.get('min_size', 'Any')} - {requirements.get('max_size', 'Any')} SF
- Max rent: ${requirements.get('max_rent_per_sf', 'Any')}/SF/year
- Culture keywords: {', '.join(requirements.get('culture_keywords', []))}
- Preferred locations: {', '.join(requirements.get('preferred_locations', []))}
        """
        
        return context
