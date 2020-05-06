#!/usr/bin/env bash

# Ping the TfL API at minimum every 3 minutes
TIME_LIMIT=180

while true
do
    start_time="$(date -u +%s)"

    printf "\nRunning fill video store containers, storing local\n"
    docker run --rm --net=host -v /TfL_videos:/TfL_videos store_videos 0 911

    end_time="$(date -u +%s)"
    elapsed="$(($end_time-$start_time))"

    # Sleep for 3 minutes - elapsed time
    printf "\n\t\tFinished! To download all feeds took: $elapsed \n"
    if [[ "$elapsed" -lt "$TIME_LIMIT" ]]
    then
    sleep_duration="$((TIME_LIMIT-$elapsed))"
    printf "\n\t\t Sleeping for $sleep_duration seconds\n"
    sleep ${sleep_duration}
    fi
done



