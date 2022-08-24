import vapoursynth as vs
import kagefunc as kgf
from vsutil import depth, get_y
from vsTAAmbk import TAAmbk
import G41Fun as fun
import havsfunc as haf

__version__ = 0.14

core = vs.core
 

"""
A template to remaster bad DVD encode RAW from 480p to 1080p, by using the waifu2x upscaler.
 
Pros: Sharpen, no noise
Cons: Details lost, weird lineart sometimes
"""


file = r'[hentai]video.mp4'
#src = core.ffms2.Source(source=file)
src = core.lsmas.LWLibavSource(source=file)
src16 = depth(src, 16)

if src16.height != 480:
    src16 = src16.resize.Spline36(848, 480)

luma = get_y(src16)

aa = TAAmbk(luma, aatype='Eedi3', nsize=4, nns=4, mytpe=1, down8=False, opencl=True)

sharp = core.warp.AWarpSharp2(aa, thresh=50, blur=3, type=0, depth=16) # Reduce large lineart
sharp = core.asharp.ASharp(sharp, t=0.5, hqbf=True) # Normal sharp
sharp = core.std.ShufflePlanes([sharp, src16], [0, 1, 2], vs.YUV) # Merge sharp luma
sharp = fun.Hysteria(sharp, sstr=0.5) # Make lineart darker

convert = core.fmtc.resample(clip=sharp, css='444')
convert = core.fmtc.matrix(clip=convert, mat='709', col_fam=vs.RGB)
convert = core.fmtc.bitdepth(clip=convert, bits=32)

waifu = core.w2xnvk.Waifu2x(convert, noise=3, model=2).resize.Spline36(1920, 1080)
reconvert = core.fmtc.bitdepth(clip=waifu, bits=16)
reconvert = core.fmtc.matrix (clip=reconvert, mat='709', col_fam=vs.YUV, bits=16)
reconvert = core.fmtc.resample(clip=reconvert, css='420')

resharp = haf.LSFmod(reconvert, strength=50, defaults='Slow') # Sharp again a little bit
deband = core.f3kdb.Deband(resharp, y=48, cb=48, cr=48, grainy=48, grainc=48, output_depth=16)
grain = kgf.adaptive_grain(deband)

output = depth(grain, 10)
#src16.set_output(0)
output.set_output()
