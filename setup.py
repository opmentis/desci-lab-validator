import os
import subprocess
import logging
from pathlib import Path
import urllib.request

logger = logging.getLogger(__name__)

PARAMS_URL = 'https://storage.googleapis.com/alphafold/alphafold_params_colab_2022-12-06.tar'
STEREO_CHEMICAL_PROPS_URL = 'https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt'

def setup_alphafold():
    """Download and setup AlphaFold parameters and dependencies"""
    try:
        # Create params directory
        params_dir = Path('./alphafold/data/params')
        params_dir.mkdir(parents=True, exist_ok=True)
        
        # Download parameters
        params_path = params_dir / os.path.basename(PARAMS_URL)
        logger.info("Downloading AlphaFold parameters...")
        urllib.request.urlretrieve(PARAMS_URL, params_path)
        
        # Extract parameters
        logger.info("Extracting parameters...")
        subprocess.run([
            'tar', '--extract', '--verbose',
            '--file', str(params_path),
            '--directory', str(params_dir),
            '--preserve-permissions'
        ], check=True)
        
        # Clean up tar file
        params_path.unlink()
        
        # Download stereo chemical props
        props_dir = Path('./alphafold/common')
        props_dir.mkdir(parents=True, exist_ok=True)
        props_path = props_dir / 'stereo_chemical_props.txt'
        
        logger.info("Downloading stereo chemical properties...")
        urllib.request.urlretrieve(STEREO_CHEMICAL_PROPS_URL, props_path)
        
        logger.info("Setup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        return False 