from tasks import celery_main_task
import logging

logging.basicConfig(filename='ksp_scraper.log', level=10
                    , format='%(asctime)s: %(module)s: %(funcName)s: %(levelname)s: %(message)s')

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.debug(f'start')
    celery_main_task()