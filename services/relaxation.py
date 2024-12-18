from alphafold.relax import relax, utils
from alphafold.common import protein
import logging
from typing import Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RelaxationService:
    def __init__(self, use_gpu: bool = False):
        """Initialize relaxation service
        
        Args:
            use_gpu: Whether to use GPU for relaxation
        """
        self.amber_relaxer = relax.AmberRelaxation(
            max_iterations=0,
            tolerance=2.39,
            stiffness=10.0,
            exclude_residues=[],
            max_outer_iterations=3,
            use_gpu=use_gpu
        )

    async def relax_structure(
        self,
        prot: protein.Protein,
        plddt: np.ndarray
    ) -> Tuple[str, np.ndarray]:
        """Relax protein structure using AMBER
        
        Args:
            prot: Protein object to relax
            plddt: Per-residue confidence scores
            
        Returns:
            Tuple containing:
            - Relaxed PDB string
            - Banded B-factors indicating confidence bands
        """
        try:
            logger.info("Starting AMBER relaxation")
            
            # Run AMBER relaxation
            relaxed_pdb, _, violations = await self._run_relaxation(prot)
            
            # Convert pLDDT to confidence bands for visualization
            banded_b_factors = self._get_confidence_bands(plddt)
            
            # Add confidence bands as B-factors
            final_pdb = utils.overwrite_b_factors(relaxed_pdb, banded_b_factors)
            
            logger.info(f"Relaxation complete with {len(violations)} violations")
            
            return final_pdb, banded_b_factors
            
        except Exception as e:
            logger.error(f"Relaxation failed: {str(e)}")
            raise

    async def _run_relaxation(
        self, 
        prot: protein.Protein
    ) -> Tuple[str, Optional[str], list]:
        """Run AMBER relaxation"""
        return self.amber_relaxer.process(prot=prot)

    def _get_confidence_bands(self, plddt: np.ndarray) -> np.ndarray:
        """Convert pLDDT to confidence bands
        
        Bands:
        0: Very low (pLDDT < 50)
        1: Low (70 > pLDDT > 50) 
        2: Confident (90 > pLDDT > 70)
        3: Very high (pLDDT > 90)
        """
        bands = [
            (0, 50),
            (50, 70), 
            (70, 90),
            (90, 100)
        ]
        
        banded_b_factors = []
        for score in plddt:
            for band_idx, (min_val, max_val) in enumerate(bands):
                if min_val <= score <= max_val:
                    banded_b_factors.append(band_idx)
                    break
                    
        return np.array(banded_b_factors) 