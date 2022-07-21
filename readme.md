# Using Pyav to display video with no drops on a Raspberry PI 4

This is a simple proof of concept that show that it is possible
to display video on a raspbery pi 4 without frame drops.

## Sticking points

On the raspberry pi there is no hardware support for converting
from the yuv420p pixel format to RGB pixel format, this made it
so that we get quite a severe amount of frame drops even on a 
short video, we therefore don't do that conversion at all,
writing directly to a YV12 texture

## How was this tested?

A 20s 1920x1080 clip in flv format using the h264 encoder, feel
free to submit a PR if you have some other information

## Possible improvements

We are currently using `SDL_UpdateYUVTexture`, this is likely
not as efficient as what `SDL_LockTexture` and `SDL_UnlockTexture`
would be on a `SDL_TEXTUREACCES_STREAMING` texture would be,
there is some imcompatability between the YUV format that
ffmpeg spits out that the NV12 format the SDL accept, one of
them is buffered with 0s to the width of frame for the U and V
planes, I cannot remember which way around it is...
