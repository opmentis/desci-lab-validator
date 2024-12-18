import logging
from typing import Dict
from services.model_service import ModelService
from services.relaxation import RelaxationService
from services.confidence import ConfidenceService
from services.client_service import ClientService
from config import settings
import asyncio
import json
import sys

logger = logging.getLogger(__name__)

class ValidatorService:
    def __init__(
        self,
        model_params_dir: str,
        api_url: str,
        use_gpu: bool = False
    ):
        """Initialize validator service"""
        self.model_service = ModelService(model_params_dir)
        self.relaxation_service = RelaxationService(use_gpu)
        self.confidence_service = ConfidenceService()
        self.client_service = ClientService(api_url)

    async def run(self, wallet_address: str):
        """Run validation loop"""
        while True:
            try:
                # Get next task from server
                logger.info("Getting next task from server")
                task = await self.client_service.get_next_task(wallet_address)

                if task == 0:
                    logger.warning("Sorry, your wallet is not registered. Kindly register to access Decentralizing Scientific Discovery Lab.")
                    logger.info("Shutting down gracefully...")
                    sys.exit(0)

                elif task == 2:
                    logger.warning("Sorry, your are not registered as a Validator.")
                    logger.info("Shutting down validator gracefully...")
                    sys.exit(0)

                logger.info(f"Got task: {task['task_id']}")
                if not task:
                    logger.info("No tasks available")
                    continue

                await self.client_service.update_task_status(task['task_id'], wallet_address, 'pending')

                # Get MSA results
                logger.info("Getting MSA features")
                msa_features = await self.client_service.get_msa_results(
                    task['task_id'],
                    wallet_address,
                    task['pointer_wallet'],                
                )
    
                # Run validation
                result_paths = await self.validate_structure(
                    msa_features,
                    run_relax=True
                )

                # Upload results
                logger.info("Uploading results")

                for i, (file_type, file_path) in enumerate(result_paths.items()):
                    await self.client_service.upload_validation_results(task['task_id'], 
                                                                        wallet_address, 
                                                                        str(file_path), 
                                                                        file_type)

                logger.info(f"Results uploaded...")

                # Update task status
                await self.client_service.update_task_status(task['task_id'], wallet_address, 'completed')

                logger.info(f"Task status updated...")

                await self.client_service.get_validator_info(wallet_address)

                logger.info("Hibernating validator service...")

                await asyncio.sleep(settings.TASK_POLL_INTERVAL)
    
            except Exception as e:
                logger.error(f"Error in validation loop: {str(e)}")
                await asyncio.sleep(5)
                continue

    async def validate_structure(
        self,
        msa_features: Dict,
        run_relax: bool = True
    ) -> Dict:
        """Run structure validation"""
        try:
            # Run model prediction
            logger.info("Running model prediction")
            prediction = await self.model_service.predict_structure(
                msa_features,
                run_relax=run_relax
            )

            # Calculate confidence metrics
            metrics = self.confidence_service.calculate_metrics(
                plddt=prediction['plddt'],
                pae=prediction.get('pae'),
                max_pae=prediction.get('max_pae')
            )

            # Prepare results for upload
            results = {
                'prediction.pdb': prediction['relaxed_pdb'],
                'metrics.json': {
                    'mean_plddt': metrics['mean_plddt']
                }
            }
            logger.info("Validation completed")

            with open('prediction.pdb', 'w') as pp:
                pp.write(prediction['relaxed_pdb'])
            
            with open('metrics.json', 'w') as json_file:
                    json.dump({
                    'mean_plddt': metrics['mean_plddt']
                }, json_file, indent=4)  

            result_path = {
                    'prediction': 'prediction.pdb',
                    'metrics': 'metrics.json'
                }

            if 'pae_json' in metrics:
                results['predicted_aligned_error.json'] = metrics['pae_json']

                with open('predicted_aligned_error.json', 'w') as pj:
                    json.dump(metrics['pae_json'], pj, indent=4) 

                result_path = {
                    'prediction': 'prediction.pdb',
                    'metrics': 'metrics.json',
                    'pae': 'predicted_aligned_error.json',
                }

            return result_path
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            raise 