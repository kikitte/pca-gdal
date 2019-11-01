import os
import pca
import raster
import numpy as np

rasterObjs, arrs, mask, projection, pixelResolution, intersectedBbox = raster.read(['/mnt/AllThings/JSY/RSEI/www/lst.tif', '/mnt/AllThings/JSY/RSEI/www/wet.tif', '/mnt/AllThings/JSY/RSEI/www/ndvi.tif', '/mnt/AllThings/JSY/RSEI/www/ndbsi.tif'])

# pca transform
values, vectors, projected = pca.pcaFnc(arrs)

# min-max normalization for projected array
for bidx in range(projected.shape[0]):
    min = np.min(projected[bidx])
    max = np.max(projected[bidx])
    projected[bidx] = (projected[bidx] - min) / (max - min)

# save pca bands
outfile = '/home/kikat/pca.tif'
if os.path.exists(outfile):
    os.remove(outfile)
raster.write(projected, mask, projection, pixelResolution, intersectedBbox, np.finfo(arrs.dtype).min, outfile)

