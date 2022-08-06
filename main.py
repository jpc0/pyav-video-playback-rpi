import argparse
import time
import ctypes
import math
import av
import sdl2.ext
import sdl2
import itertools

parser = argparse.ArgumentParser(description="Video Wall Client")
parser.add_argument("file", type=str, help="Filename")
args = parser.parse_args()

sdl2.ext.common.init()

window = sdl2.ext.Window("test", (0, 0), flags=sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
renderer = sdl2.ext.Renderer(window, flags=sdl2.SDL_RENDERER_ACCELERATED)

container = av.open(args.file)
print(float(container.streams.video[0].duration * container.streams.video[0].time_base))
# frame_gen = itertools.cycle(container.decode(video=0))
frame_gen = container.decode(video=0)

start_frame = time.perf_counter()
frame = next(frame_gen)
print(f"Frame.index: {frame.index}")

texture = sdl2.SDL_CreateTexture(
    renderer.sdlrenderer,
    sdl2.SDL_PIXELFORMAT_IYUV,
    sdl2.SDL_TEXTUREACCESS_STREAMING,
    frame.width,
    frame.height,
)

try:
    while True:
        present_frame_at = start_frame + frame.time
        if time.perf_counter() >= present_frame_at:
            print(math.floor(time.perf_counter() - present_frame_at))
            """
            sdl2.SDL_UpdateYUVTexture(texture,
                    None,
                    ctypes.cast(frame.planes[0].buffer_ptr, ctypes.POINTER(ctypes.c_uint8)),
                    frame.planes[0].line_size,
                    ctypes.cast(frame.planes[1].buffer_ptr, ctypes.POINTER(ctypes.c_uint8)),
                    frame.planes[1].line_size,
                    ctypes.cast(frame.planes[2].buffer_ptr, ctypes.POINTER(ctypes.c_uint8)),
                    frame.planes[2].line_size)
            """
            pixels = ctypes.c_void_p()
            linesize = ctypes.c_int()
            sdl2.SDL_LockTexture(texture, None, pixels, linesize)
            if pixels.value is not None:
                pixels_address = pixels.value
                pixels_u_address = pixels_address + frame.planes[0].buffer_size
                pixels_v_address = pixels_u_address + frame.planes[1].buffer_size
                sdl2.SDL_memcpy(
                    pixels,
                    frame.planes[0].buffer_ptr,
                    frame.planes[0].buffer_size,
                )
                sdl2.SDL_memcpy(
                    ctypes.c_void_p(pixels_u_address),
                    frame.planes[1].buffer_ptr,
                    frame.planes[1].buffer_size
                )
                sdl2.SDL_memcpy(
                    ctypes.c_void_p(pixels_v_address),
                    frame.planes[2].buffer_ptr,
                    frame.planes[2].buffer_size
                )
            sdl2.SDL_UnlockTexture(texture)

            sdl2.SDL_RenderClear(renderer.sdlrenderer)
            sdl2.SDL_RenderCopy(renderer.sdlrenderer, texture, None, None)
            sdl2.SDL_RenderPresent(renderer.sdlrenderer)
            frame = next(frame_gen)
            if frame.index == 0:
                print(f"Frame.index: {frame.index}")
                start_frame = time.perf_counter()
        else:
            time.sleep(0)
except StopIteration:
    pass
