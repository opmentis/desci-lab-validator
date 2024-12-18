#!/usr/bin/env python3
import asyncio
import logging
import argparse
from services.validator_service import ValidatorService
from config import settings
from utils.logging import setup_logging
from pathlib import Path
from setup import setup_alphafold

# Setup logging first
setup_logging()

logger = logging.getLogger(__name__)

async def main(wallet_address: str, api_url: str):
    """Main entry point"""
    try:
        logger.info("Starting OpMentis Decentralized Protein Structure Validation")
        
        # Setup GPU environment if enabled
        settings.setup_gpu_env()
        if settings.USE_GPU:
            logger.info("GPU support enabled")
        
        # Run setup if needed
        params_dir = Path('./alphafold/data/params')
        if not params_dir.exists():
            logger.info("First-time setup: downloading AlphaFold parameters...")
            if not setup_alphafold():
                raise Exception("Failed to setup AlphaFold")
        
        # Initialize validator service
        validator = ValidatorService(
            model_params_dir=settings.MODEL_PARAMS_DIR,
            api_url=api_url,
            use_gpu=settings.USE_GPU
        )
        
        logger.info(f"Validator initialized with wallet: {wallet_address}")
        
        try:
            await validator.run(wallet_address)
        except KeyboardInterrupt:
            logger.info("\nShutting down validator gracefully...")
            
    except Exception as e:
        logger.error(f"Critical error: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpMentis DeSci Validator")
    parser.add_argument(
        "--wallet", 
        required=True,
        help="Your wallet address"
    )
    parser.add_argument(
        "--api-url",
        default=settings.API_URL,
        help="API endpoint URL"
    )
    
    args = parser.parse_args()
    
    asyncio.run(main(
        wallet_address=args.wallet,
        api_url=args.api_url
    )) 