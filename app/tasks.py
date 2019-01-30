from app import scheduler, MINS
from app.qbo import refresh_stored_tokens
from app.utils import fetch


@scheduler.task('interval', id='do_refresh', minutes=MINS)
def refresh():
    with scheduler.app.app_context():
        if fetch('refresh_token') is not None:
            refresh_stored_tokens()
            scheduler.app.logger.info('Scheduled QBO token refresh.')
        else:
            scheduler.app.logger.info('QBO tokens not refreshed because no \
                    token stored.')
