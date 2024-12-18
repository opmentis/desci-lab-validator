from alphafold.common import confidence
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ConfidenceService:
    def calculate_metrics(
        self,
        plddt: np.ndarray,
        pae: Optional[np.ndarray] = None,
        max_pae: Optional[float] = None
    ) -> Dict:
        """Calculate confidence metrics"""
        metrics = {
            'mean_plddt': float(np.mean(plddt))
        }
        
        if pae is not None and max_pae is not None:
            metrics['pae_json'] = confidence.pae_json(
                pae=pae,
                max_pae=float(max_pae)
            )
            
        return metrics 