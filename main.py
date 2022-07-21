import argparse
import time
import ctypes
import math
import av
import sdl2.ext
import sdl2
import numpy

parser = argparse.ArgumentParser(description="Video Wall Client")
parser.add_argument("file", type=str, help="Filename")
args = parser.parse_args()

sdl2.ext.common.init()
container = av.open(args.file)
window = sdl2.ext.Window("test", (0,0), flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
renderer = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC)

start_frame: float = 0
video_frame_time = 1 / float(container.streams.video[0].base_rate)
frame_gen = container.decode(video=0)
frame = None
gen_frame = True
present_frame_at = 0

start_frame = time.perf_counter()
frame = next(frame_gen)

texture = sdl2.SDL_CreateTexture(renderer.sdlrenderer, sdl2.SDL_PIXELFORMAT_YV12, sdl2.SDL_TEXTUREACCESS_STREAMING, frame.width, frame.height)

try:
    while True:
        present_frame_at = start_frame + frame.time
        if time.perf_counter() >= present_frame_at:
            print(math.floor(time.perf_counter() - present_frame_at))
            sdl2.SDL_UpdateYUVTexture(texture,
                    None,
                    ctypes.cast(frame.planes[0].buffer_ptr, ctypes.POINTER(ctypes.c_uint8)),
                    frame.planes[0].line_size,
                    ctypes.cast(frame.planes[1].buffer_ptr, ctypes.POINTER(ctypes.c_uint8)),
                    frame.planes[1].line_size,
                    ctypes.cast(frame.planes[2].buffer_ptr, ctypes.POINTER(ctypes.c_uint8)),
                    frame.planes[2].line_size)

            sdl2.SDL_RenderClear(renderer.sdlrenderer)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, None)
            sdl2.SDL_RenderPresent(renderer.sdlrenderer)
            frame = next(frame_gen)
        else:
            time.sleep(0)
except StopIteration:
    pass

