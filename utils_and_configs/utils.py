from utils_and_configs.config import *
from scrapetube import get_channel
from utils_and_configs.log_congfig import *
logger = logging.getLogger(__name__)

def get_channel_video_list(channel_url, limit=VIDEO_LIMIT):
    logger.info(f'Fetching videos for  channel {channel_url}')
    list_video_id = []
    for video in get_channel(channel_url=channel_url, limit=limit, sort_by='newest', sleep=1):
        if video.get('videoId'):
            list_video_id.append(video.get('videoId'))
    logger.info(f'Fetched {len(list_video_id)} for channel {channel_url}')
    return list_video_id


def get_time_string_from_period_of_time(period_of_time: str) -> str:
    if not period_of_time or not ('PT' in period_of_time):
        print(f'{period_of_time} Not in Period of Time Format')
        return ''

    duration_ = period_of_time.replace('PT', '')
    time_str = ''
    if 'H' in duration_:
        H = duration_.split('H')[0]
        duration_ = duration_.split('H')[1]
        time_str += f"{H.zfill(2)}:"
    else:
        time_str += f"00:"

    if 'M' in duration_:
        M = duration_.split('M')[0][-2:]
        duration_ = duration_.split('M')[1]
        time_str += f"{M.zfill(2)}:"
    else:
        time_str += f"00:"

    if 'S' in duration_:
        S = duration_.split('S')[0][-2:]
        time_str += f"{S.zfill(2)}"
    else:
        time_str += f"00"
    return time_str


def get_secs_from_time_string(time_string: str) -> int:
    if ":" not in time_string:
        return 0
    H, M, S = [int(i) for i in time_string.split(':')]
    duration_secs = H * 60 * 60 + M * 60 + S
    return duration_secs


if __name__ == '__main__':
    # test get_channel_video_list
    list_video_ids = get_channel_video_list(CHANNEL_URLS[0], limit=VIDEO_LIMIT)
    logger.info(list_video_ids)
