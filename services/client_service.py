import aiohttp
import logging
import pickle
import gzip
import base64
from typing import Dict, Optional
from tabulate import tabulate
import os

logger = logging.getLogger(__name__)

def log_dict_as_table(data_dict, logger=logger):
    headers = ['Attribute', 'Value']
    table_data = [[k, v] for k, v in data_dict.items()]
    table = tabulate(
        table_data,
        headers=headers,
        tablefmt='grid',  
        numalign='left',
        stralign='left'
    )
    
    separator = '-' * 80
    logger.info(f"\n{separator}\n{table}\n{separator}")

class ClientService:
    def __init__(self, api_url: str):
        """Initialize client service
        
        Args:
            api_url: Base URL for server API
        """
        self.api_url = api_url.rstrip('/')
        
    async def get_next_task(self, wallet_address: str) -> Optional[Dict]:
        """Get next validation task from server"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/validators/next",
                params={"wallet_address": wallet_address}
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
                
    async def get_msa_results(self, task_id: str, wallet: str, pointer_wallet: str) -> Dict:
        """Get MSA results for task"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/validators/msa/{task_id}",
                params={
                    "pointer_wallet": pointer_wallet,
                    "wallet": wallet
                    }
            ) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get MSA results: {await response.text()}")
                
                logger.info("Decoding MSA features...")
                data = await response.read()
                decoded_data = base64.b64decode(data)

                logger.info("Decompressing MSA features...")

                decompressed_data = gzip.decompress(decoded_data)

                logger.info("Loading MSA results...")
                # Deserialize the pickled data back into a NumPy array
                data = pickle.loads(decompressed_data)

                return data
                # return await response.json()
                        
    async def upload_validation_results(self, task_id: str, wallet: str, file_path: str, file_type: str) -> bool:
        try:      
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            form_data = aiohttp.FormData()
            form_data.add_field('file',
                            file_data,
                            filename=os.path.basename(file_path))
            
            async with aiohttp.ClientSession() as session:    
                async with session.post(
                    f"{self.api_url}/validators/results/{task_id}",
                    params={
                        "task_id": task_id,
                        "file_type": file_type,
                        "wallet": wallet
                    },
                    data=form_data
                ) as response:         
                    if response.status != 200:
                        error_detail = await response.json()
                        logger.error(f"Upload failed: {error_detail}")
                        return False
                    return True
                
        except Exception as e:
            logger.error(f"Error uploading result: {e}")
            raise

    async def update_task_status(self, task_id: str, wallet: str, status: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/validators/status/{task_id}",
                    params={
                        "wallet": wallet,
                        "status": status
                    }
                ) as response:
                    if response.status != 200:
                        error_detail = await response.json()
                        logger.error(f"Update failed: {error_detail}")
                        return False
                    return True
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            raise
            
    async def get_validator_info(self, wallet_address: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/incentives/customer/{wallet_address}") as response:
                    if response.status != 200:
                        return
                    response_data = await response.json()
                    log_dict_as_table(data_dict=response_data)
                
        except Exception as e:
            raise logger.error(f"Error getting validator info: {e}")