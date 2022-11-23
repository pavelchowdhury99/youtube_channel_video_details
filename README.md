# Answers 

## 1. Python script to get data from youtube for a channel (Justin Bieber's)
1. This repository has a [main.py](https://github.com/pavelchowdhury99/youtube_channel_video_details/blob/main/main.py) file which along with config settings in utils_and_config module will serve for this problem.
2. This repo can be cloned and with venv having the modules listed in requirements.txt, we can replicated the process in other local machines.
3. To change channel, changes number of thread, to remove or add limits for testing, change log file paths and output file path we can configure at [config.py inside utils_and_config](https://github.com/pavelchowdhury99/youtube_channel_video_details/blob/main/utils_and_configs/config.py).
4. To change logging levels use [log_config](https://github.com/pavelchowdhury99/youtube_channel_video_details/blob/main/utils_and_configs/log_congfig.py).
5. Subset of output is at [output.csv](https://github.com/pavelchowdhury99/youtube_channel_video_details/blob/main/out.csv), we can alter the video_limit [here](https://github.com/pavelchowdhury99/youtube_channel_video_details/blob/4d2a1ed89b7dee158ef5b4021e6be798b83421ec/utils_and_configs/config.py#L7) to scale up.

## 3. Machine's State Identification
This repo has a [process_log.sql](https://github.com/pavelchowdhury99/youtube_channel_video_details/blob/main/process_log.sql) which uses MsSql to solve for this, it can be tested in MsQSQL online IDEs like [sqliteoneline.com](https://sqliteonline.com/).
