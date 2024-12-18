from alphafold.model import model, config, data
from alphafold.common import protein
import numpy as np
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, model_params_dir: str):
        """Initialize model service
        
        Args:
            model_params_dir: Directory containing AlphaFold params
        """
        self.model_params_dir = model_params_dir
        self.model_names = config.MODEL_PRESETS['monomer'] + ('model_2_ptm',)
        
    async def predict_structure(
        self, 
        msa_features: Dict,
        run_relax: bool = True,
        max_recycles: int = 3
    ) -> Dict:
        """Run AlphaFold prediction pipeline
        
        Args:
            msa_features: MSA features from miner
            run_relax: Whether to run AMBER relaxation
            max_recycles: Max number of recycling iterations
            
        Returns:
            Dictionary containing:
            - unrelaxed_protein: Protein object before relaxation
            - relaxed_pdb: Relaxed PDB string if run_relax=True
            - plddt: Per-residue confidence scores
            - pae: Predicted aligned error if available
        """
        results = {}
        
        # Run prediction for each model
        for model_name in self.model_names:
            cfg = config.model_config(model_name)
            cfg.model.num_recycle = max_recycles
            
            params = data.get_model_haiku_params(
                model_name, 
                self.model_params_dir
            )
            
            model_runner = model.RunModel(cfg, params)
            
            # Process features and run prediction
            logger.info('Processing features...')
            processed_features = model_runner.process_features(
                msa_features, 
                random_seed=0
            )

            logger.info('Running prediction...')
            prediction = model_runner.predict(processed_features, random_seed=0)

            # Store results
            logger.info('Storing results...')
            results[model_name] = {
                'plddt': prediction['plddt'],
                'unrelaxed_protein': self._get_unrelaxed_protein(
                    processed_features,
                    prediction
                )
            }
            
            if 'predicted_aligned_error' in prediction:
                results[model_name]['pae'] = prediction['predicted_aligned_error']
                
        # Select best model and optionally relax
        best_model = self._select_best_model(results)
        
        if run_relax:
            relaxed_pdb = await self._run_relaxation(
                best_model['unrelaxed_protein']
            )
            best_model['relaxed_pdb'] = relaxed_pdb
            
        return best_model
            
    def _get_unrelaxed_protein(
        self,
        processed_features: Dict,
        prediction: Dict
    ) -> protein.Protein:
        """Convert prediction to Protein object"""
        logger.info("Converting prediction to Protein object...")
        # Set b-factors to per-residue plddt
        final_atom_mask = prediction['structure_module']['final_atom_mask']
        b_factors = prediction['plddt'][:, None] * final_atom_mask
        
        return protein.from_prediction(
            processed_features,
            prediction,
            b_factors=b_factors,
            remove_leading_feature_dimension=True  # For monomer model
        )
        
    def _select_best_model(self, results: Dict) -> Dict:
        """Select best model based on mean pLDDT"""
        # Calculate mean pLDDT for each model
        model_scores = {
            name: np.mean(model['plddt']) 
            for name, model in results.items()
        }
        
        # Select model with highest mean pLDDT
        best_model_name = max(model_scores, key=model_scores.get)
        return results[best_model_name]
        
    async def _run_relaxation(self, prot: protein.Protein) -> str:
        """Run AMBER relaxation"""
        from alphafold.relax import relax
        
        relaxer = relax.AmberRelaxation(
            max_iterations=0,
            tolerance=2.39,
            stiffness=10.0,
            exclude_residues=[],
            max_outer_iterations=3,
            use_gpu=False  # Set via config if needed
        )
        
        relaxed_pdb, _, _ = relaxer.process(prot=prot)
        return relaxed_pdb 