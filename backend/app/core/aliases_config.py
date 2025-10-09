"""
Validatus v2.0 Aliases Configuration Service
Maps friendly names to canonical IDs for 5 segments, 28 factors, 210 layers
"""
import yaml
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ValidatusAliasesConfig:
    """Central configuration for all layer-factor-segment mappings"""
    
    def __init__(self):
        self.config = self._load_aliases_config()
        logger.info(f"✅ Loaded Validatus v2.0 configuration: {self.config['metadata']}")
        
    def _load_aliases_config(self) -> Dict:
        """Load the aliases configuration from YAML"""
        try:
            config_path = Path(__file__).parent / "validatus_aliases.yaml"
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            logger.error(f"Failed to load aliases configuration: {e}")
            # Return minimal fallback config
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict:
        """Fallback configuration if YAML loading fails"""
        return {
            'version': '2.0',
            'aliases': {'segments': {}, 'factors': {}, 'layers': {}},
            'reverse': {'segments': {}, 'factors': {}, 'layers': {}},
            'factor_groups': {},
            'layer_groups': {},
            'metadata': {'total_segments': 0, 'total_factors': 0, 'total_layers': 0}
        }
    
    # ===== Segment Methods =====
    
    def get_segment_id(self, friendly_name: str) -> Optional[str]:
        """Convert friendly name to canonical segment ID (e.g., 'Product_Intelligence' → 'S1')"""
        return self.config['aliases']['segments'].get(friendly_name)
    
    def get_segment_name(self, segment_id: str) -> Optional[str]:
        """Convert canonical ID to friendly name (e.g., 'S1' → 'Product_Intelligence')"""
        return self.config['reverse']['segments'].get(segment_id)
    
    def get_all_segments(self) -> Dict[str, str]:
        """Get all segment mappings {friendly_name: segment_id}"""
        return self.config['aliases']['segments']
    
    def get_all_segment_ids(self) -> List[str]:
        """Get all segment IDs [S1, S2, S3, S4, S5]"""
        return list(self.config['reverse']['segments'].keys())
    
    # ===== Factor Methods =====
    
    def get_factor_id(self, friendly_name: str) -> Optional[str]:
        """Convert friendly name to canonical factor ID"""
        return self.config['aliases']['factors'].get(friendly_name)
    
    def get_factor_name(self, factor_id: str) -> Optional[str]:
        """Convert canonical ID to friendly name"""
        return self.config['reverse']['factors'].get(factor_id)
    
    def get_factors_for_segment(self, segment_id: str) -> List[str]:
        """Get all factor IDs for a specific segment"""
        return self.config['factor_groups'].get(segment_id, [])
    
    def get_all_factor_ids(self) -> List[str]:
        """Get all factor IDs [F1, F2, ..., F28]"""
        return list(self.config['reverse']['factors'].keys())
    
    # ===== Layer Methods =====
    
    def get_layer_id(self, friendly_name: str) -> Optional[str]:
        """Convert friendly name to canonical layer ID"""
        return self.config['aliases']['layers'].get(friendly_name)
    
    def get_layer_name(self, layer_id: str) -> Optional[str]:
        """Convert canonical ID to friendly name"""
        return self.config['reverse']['layers'].get(layer_id)
    
    def get_layers_for_factor(self, factor_id: str) -> List[str]:
        """Get all layer IDs for a specific factor"""
        return self.config['layer_groups'].get(factor_id, [])
    
    def get_all_layer_ids(self) -> List[str]:
        """Get all layer IDs [L1_1, L1_2, ..., L28_10]"""
        return list(self.config['reverse']['layers'].keys())
    
    # ===== Hierarchy Navigation =====
    
    def get_segment_hierarchy(self, segment_id: str) -> Dict:
        """Get complete hierarchy for a segment: segment → factors → layers"""
        factors = self.get_factors_for_segment(segment_id)
        hierarchy = {
            'segment': {
                'id': segment_id,
                'name': self.get_segment_name(segment_id)
            },
            'factors': []
        }
        
        for factor_id in factors:
            factor_data = {
                'id': factor_id,
                'name': self.get_factor_name(factor_id),
                'layers': []
            }
            
            layers = self.get_layers_for_factor(factor_id)
            for layer_id in layers:
                factor_data['layers'].append({
                    'id': layer_id,
                    'name': self.get_layer_name(layer_id)
                })
            
            hierarchy['factors'].append(factor_data)
        
        return hierarchy
    
    def get_factor_for_layer(self, layer_id: str) -> Optional[str]:
        """Get parent factor ID for a given layer"""
        # Layer IDs format: L{factor_num}_{layer_num}
        # e.g., L1_1 → F1, L11_5 → F11
        try:
            parts = layer_id.split('_')
            if len(parts) >= 2 and parts[0].startswith('L'):
                factor_num = parts[0][1:]  # Remove 'L' prefix
                return f"F{factor_num}"
        except Exception as e:
            logger.error(f"Error extracting factor from layer {layer_id}: {e}")
        return None
    
    def get_segment_for_factor(self, factor_id: str) -> Optional[str]:
        """Get parent segment ID for a given factor"""
        # Search through factor_groups
        for segment_id, factor_list in self.config['factor_groups'].items():
            if factor_id in factor_list:
                return segment_id
        return None
    
    def get_segment_for_layer(self, layer_id: str) -> Optional[str]:
        """Get segment ID for a given layer (through its factor)"""
        factor_id = self.get_factor_for_layer(layer_id)
        if factor_id:
            return self.get_segment_for_factor(factor_id)
        return None
    
    # ===== Statistics and Metadata =====
    
    def get_configuration_summary(self) -> Dict:
        """Get complete configuration summary"""
        return {
            'version': self.config['version'],
            'metadata': self.config['metadata'],
            'counts': {
                'segments': len(self.get_all_segment_ids()),
                'factors': len(self.get_all_factor_ids()),
                'layers': len(self.get_all_layer_ids())
            },
            'distribution': {
                segment_id: {
                    'factor_count': len(self.get_factors_for_segment(segment_id)),
                    'layer_count': sum(
                        len(self.get_layers_for_factor(f)) 
                        for f in self.get_factors_for_segment(segment_id)
                    )
                }
                for segment_id in self.get_all_segment_ids()
            }
        }
    
    def validate_configuration(self) -> Dict[str, any]:
        """Validate configuration completeness and consistency"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        try:
            # Check segment count
            segment_count = len(self.get_all_segment_ids())
            if segment_count != 5:
                validation_results['errors'].append(f"Expected 5 segments, found {segment_count}")
                validation_results['valid'] = False
            
            # Check factor count
            factor_count = len(self.get_all_factor_ids())
            if factor_count != 28:
                validation_results['errors'].append(f"Expected 28 factors, found {factor_count}")
                validation_results['valid'] = False
            
            # Check layer count
            layer_count = len(self.get_all_layer_ids())
            if layer_count != 210:
                validation_results['errors'].append(f"Expected 210 layers, found {layer_count}")
                validation_results['valid'] = False
            
            # Check factor → segment mapping
            for factor_id in self.get_all_factor_ids():
                segment_id = self.get_segment_for_factor(factor_id)
                if not segment_id:
                    validation_results['warnings'].append(f"Factor {factor_id} not mapped to any segment")
            
            # Check layer → factor mapping
            for layer_id in self.get_all_layer_ids():
                factor_id = self.get_factor_for_layer(layer_id)
                if not factor_id:
                    validation_results['warnings'].append(f"Layer {layer_id} not mapped to any factor")
            
            validation_results['statistics'] = {
                'segments': segment_count,
                'factors': factor_count,
                'layers': layer_count,
                'avg_factors_per_segment': factor_count / segment_count if segment_count > 0 else 0,
                'avg_layers_per_factor': layer_count / factor_count if factor_count > 0 else 0
            }
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_results

# Global configuration instance
try:
    aliases_config = ValidatusAliasesConfig()
    # Log validation results
    validation = aliases_config.validate_configuration()
    if validation['valid']:
        logger.info(f"✅ Validatus v2.0 configuration validated successfully")
        logger.info(f"   Segments: {validation['statistics']['segments']}")
        logger.info(f"   Factors: {validation['statistics']['factors']}")
        logger.info(f"   Layers: {validation['statistics']['layers']}")
    else:
        logger.warning(f"⚠️ Configuration validation issues: {validation['errors']}")
except Exception as e:
    logger.error(f"Failed to initialize aliases configuration: {e}")
    aliases_config = None

