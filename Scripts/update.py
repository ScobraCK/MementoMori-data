import json
import logging
import os
import httpx
import asyncio

from api import API, get_version

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

logger = logging.getLogger(__name__)

async def update_master(api: API):
    path = './Master'
    os.makedirs(path, exist_ok=True)
    
    logger.info('Checking App Version')
    app_version_fp = os.path.join(path, "appversion")
    with open(app_version_fp, 'w') as f:
        f.write(f'{api.version}')  # simply overwrite
        
    logger.info('Checking Master Version')
    master_version_fp = os.path.join(path, "version")
    current_master_version = None
    with open(master_version_fp, 'r') as f:
        current_master_version = f.read().strip()
    if current_master_version == api.ortegamasterversion:
        logger.info('No change in master. Aborting')
        return
    
    logger.info('Updating Master')
    async with httpx.AsyncClient() as client:
        new_catalog = await api.get_master_catalog(client)
        
        catalog_fp = os.path.join(path, "master-catalog.json")
        if os.path.exists(catalog_fp):
            with open(catalog_fp, "rb") as f:
                old_catalog = json.load(f)["MasterBookInfoMap"]
        else:
            logger.info("Couldn't find old catalog")
            old_catalog = {}
        
    
        async def update_book(name, item):    
            fp = os.path.join(path, f"{name}.json")
            if (
                os.path.exists(fp)
                and name in old_catalog
                and item["Hash"] == old_catalog[name]["Hash"]
            ):
                return
            logger.info(f"Updating {name}")
            data = await api.get_master(name, client)
            with open(fp, "wb") as f:
                f.write(json.dumps(data, indent=4, ensure_ascii=False).encode("utf-8"))
        
        tasks = [update_book(name, item) for name, item in new_catalog["MasterBookInfoMap"].items()]
        await asyncio.gather(*tasks)   
         
    # delete old files
    for _, _, files in os.walk(path):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == '.json' and (name not in new_catalog["MasterBookInfoMap"].keys()):
                if name == 'master-catalog':
                    continue
                logger.info(f'Removing {file}')
                filename = os.path.join(path, file)
                os.remove(filename)
        
    logger.info('Saving Version')
    with open(catalog_fp, "wb") as f:
        f.write(json.dumps(new_catalog, indent=4, ensure_ascii=False).encode("utf-8"))
    with open(master_version_fp, 'w') as f:
        f.write(api.ortegamasterversion)

def update_notice(api):
    logger.info('Updating Notice')
    path = './Notice'
    os.makedirs(path, exist_ok=True)
        
if __name__ == "__main__":
    logger.info('Fetching Version')
    version = get_version()
    
    if version:
        try:
            api = API(version)
            api.getDataUri()
            asyncio.run(update_master(api))
            logger.info('Done')
        except Exception as e:
            logger.info(f"Failed to update: {e}")
    else:
        logger.info('Aborting.')
    
    
    