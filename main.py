from config import *
from log_congfig import *
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, date, timedelta
from requests_html import HTMLSession, AsyncHTMLSession
import asyncio
from time import perf_counter
from utils import *
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

logger = logging.getLogger(__name__)

async def fetch_page_content(video_uid, session):
    # with HTMLSession() as session:
    logger.info(f'Fetching content of video - {video_uid} ...')
    # print(f'Fetching content of {video_uid} ...')
    url = f'https://www.youtube.com/watch?v={video_uid}'
    r = await session.get(url)
    logger.info(f'Done fetching content of video - {video_uid}')
    # print(f'{count_} Done fetching content of {video_uid}')
    return r.content, video_uid


def get_details(res_content, video_uid):
    logger.info(f'Extracting details for video - {video_uid}')
    # create beautiful soup object to parse HTML
    soup = BeautifulSoup(res_content, "html.parser")
    # initialize the result dictionary to store data
    result = {}

    result['video_uid'] = soup.find("meta", itemprop="videoId").get('content')
    result["title"] = soup.find("meta", itemprop="name").get('content')
    result["description"] = soup.find("meta", itemprop="description").get('content')
    result["paid"] = soup.find("meta", itemprop="paid").get('content')
    result["channel_id"] = soup.find("meta", itemprop="channelId").get('content')
    result["duration"] = soup.find("meta", itemprop="duration").get('content')
    result['duration_str'] = get_time_string_from_period_of_time(result['duration'])
    result['duration_secs'] = get_secs_from_time_string(result['duration_str'])
    result["views"] = int(soup.find("meta", itemprop="interactionCount").get('content'))

    result["date_published"] = soup.find("meta", itemprop="datePublished").get('content')
    result["date_upload"] = soup.find("meta", itemprop="uploadDate").get('content')
    result["genre"] = soup.find("meta", itemprop="genre").get('content')

    result["tags"] = ', '.join(
        [meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"})])

    data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
    data_json = json.loads(data)
    try:
        videoPrimaryInfoRenderer = \
            data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                'videoPrimaryInfoRenderer']
        # number of likes
        likes_label = \
            videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0][
                'segmentedLikeDislikeButtonRenderer']['likeButton']['toggleButtonRenderer'][
                'defaultText'].get('accessibility')
        if likes_label:
            likes_label = likes_label['accessibilityData']['label']  # "No likes" or "###,### likes"
            likes_str = likes_label.split(' ')[0].replace(',', '')
        else:
            likes_str = 'No'
        result["likes"] = int('0' if likes_str == 'No' else likes_str)
    except KeyError:
        logger.error(f'Primary Details exception for {video_uid}')
        result["likes"] = None

    try:
        videoSecondaryInfoRenderer = \
            data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1][
                'videoSecondaryInfoRenderer']
        # number of subscribers as str
        channel_subscribers = \
            videoSecondaryInfoRenderer['owner']['videoOwnerRenderer']['subscriberCountText']['accessibility'][
                'accessibilityData']['label']
    except KeyError:
        logger.error(f'Secondary Details exception for {video_uid}')
        channel_subscribers = None

    channel_tag = soup.find("meta", itemprop="channelId")['content']
    # channel name
    channel_name = soup.find("span", itemprop="author").next.next['content']

    channel_url = f"https://www.youtube.com/{channel_tag}"

    result['channel_name'] = channel_name
    result['channel_subscriber_base'] = channel_subscribers
    result['channel_url'] = channel_url
    result['channel_uid'] = result['channel_url'].replace('https://www.youtube.com/', '')
    result['updated_on'] = date.today()
    return result


async def do_work():
    start_fetch_channels = perf_counter()
    overall_list_of_videos = []
    for channel_url in CHANNEL_URLS:
        try:
            overall_list_of_videos.extend(get_channel_video_list(channel_url))
        except Exception as e:
            logger.error(e)
    logger.info(
        f'Fetched overall {len(overall_list_of_videos)} videos from {len(CHANNEL_URLS)} channels in {perf_counter() - start_fetch_channels}')

    start_fetch_video_details = perf_counter()
    with ThreadPoolExecutor(max_workers=MAX_THREAD_POOL_EXECUTOR) as executor:
        # with ThreadPoolExecutor(max_workers=1) as executor:
        # result = executor.map(fetch, list_of_video_uid_in_tracking_today)
        with AsyncHTMLSession() as session:
            # Set any session parameters here before calling `fetch`

            # Initialize the event loop
            loop = asyncio.get_event_loop()

            # Use list comprehension to create a list of
            # tasks to complete. The executor will run the `fetch`
            # function for each url in the urlslist
            tasks = [
                await loop.run_in_executor(
                    executor,
                    fetch_page_content,
                    *(video_id, session)
                    # Allows us to pass in multiple arguments to `fetch`
                )
                for count_, video_id in enumerate(overall_list_of_videos)
            ]

            # Initializes the tasks to run and awaits their results
            list_out = []
            for res_content, video_uid in await asyncio.gather(*tasks):
                list_out.append(get_details(res_content, video_uid))
    logger.info(
        f'Fetched details of {len(list_out)} videos in {perf_counter() - start_fetch_channels}')

    df_out = pd.DataFrame.from_records(list_out)
    start_write_csv = perf_counter()
    logger.info(f'Writing to csv at path - {OUTPUT_CSV_PATH}.')
    df_out.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
    logger.info(f'Wrote to csv at {OUTPUT_CSV_PATH} with shape - {df_out.shape}')


def main():
    start_time_program = perf_counter()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(do_work())
    loop.run_until_complete(future)
    print(f'Time taken for entire program = {perf_counter() - start_time_program}')


main()
