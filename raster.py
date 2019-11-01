from osgeo import gdal
from osgeo import gdal_array
import numpy as np
import math
import helpers.extent as extent

# helpers


def bandKeyOfRaster(raster, bandIndex):
    return str(raster) + '-' + 'band' + str(bandIndex)


def read(rasters):
    # 检查众多栅格文件是否具有相同的地理空间参考与分辨率
    info = None
    for r in rasters:
        k = gdal.Open(r, gdal.GA_ReadOnly)
        if info == None:
            info = compareRasterInfo(k, None)
        else:
            if not compareRasterInfo(k, info):
                raise TypeError(
                    'all the raster must be the same projection and resolution')
    pixelResolution = info['resolution']
    projection = info['projection']
    # 计算各栅格的bounding box，并检查alignmeng是否都相同
    rasterObjs = []
    for r in rasters:
        dataset = gdal.Open(r, gdal.GA_ReadOnly)
        for bidx in range(1, dataset.RasterCount + 1):
            # geoTrans[0] top left x --> minx
            # geoTrans[1] w-e pixel resolution
            # geoTrans[2] 0
            # geoTrans[3] top left y --> miny
            # geoTrans[4] 0
            # geoTrans[5] n-s pixel resolution (negative value)
            geoTrans = dataset.GetGeoTransform()
            # bounding box: [minx, miny, max, maxy], top left is (minx, miny), bottom right is (max, maxy)
            minx = geoTrans[0]
            miny = geoTrans[3]
            maxx = minx + dataset.RasterXSize * pixelResolution
            maxy = miny + dataset.RasterYSize * pixelResolution
            bbox = [minx, miny, maxx, maxy]
            nodata = dataset.GetRasterBand(bidx).GetNoDataValue()
            # insert key with a value of default if the key not in the dict
            rasterObjs.append(
                {'bbox': bbox, 'file': r, 'band_index': bidx, 'nodata_value': nodata})
    for i_idx, i in enumerate(rasterObjs):
        for ii in rasterObjs[i_idx+1:]:
            bbox_i = i['bbox']
            bbox_ii = ii['bbox']
            minx_i = bbox_i[0]
            miny_i = bbox_i[1]
            minx_ii = bbox_ii[0]
            miny_ii = bbox_ii[1]
            if not math.isclose((abs(minx_i - minx_ii) / pixelResolution), 0) or not math.isclose((abs(miny_i - miny_ii) / pixelResolution), 0):
                raise ValueError('rasters must have the sampe alignment')
    # 所有栅格bbox相交
    intersectedBbox = None
    for rast in rasterObjs:
        bbox = rast['bbox']
        if intersectedBbox == None:
            intersectedBbox = bbox
        else:
            if extent.intersects(bbox, intersectedBbox):
                intersectedBbox = extent.getIntersection(bbox, intersectedBbox)
            else:
                raise Exception('bounding box intersection got empty')
    for rast in rasterObjs:
        rast['interestionBbox'] = intersectedBbox
    # bounding box转各个栅格数组的范围
    for rast in rasterObjs:
        bbox = rast['bbox']
        col_min = round((intersectedBbox[0] - bbox[0]) / pixelResolution)
        col_max = round((intersectedBbox[2] - bbox[0]) / pixelResolution)
        row_min = round((intersectedBbox[1] - bbox[1]) / pixelResolution)
        row_max = round((intersectedBbox[3] - bbox[1]) / pixelResolution)
        arr = gdal_array.LoadFile(rast['file'])
        arrSubset = arr[row_min:row_max, col_min:col_max]
        rast['array'] = arrSubset.flatten()
        arr = None
    # remove nodata cells
    mask = None
    for index, rast in enumerate(rasterObjs):
        arr = rast['array']
        nodata = rast['nodata_value'] = np.array(
            [rast['nodata_value']], dtype=arr.dtype)[0]
        boolArr = (arr == nodata)
        if index == 0:
            mask = boolArr
        else:
            mask = np.logical_and(mask, boolArr)
    for rast in rasterObjs:
        rast['array'] = np.delete(rast['array'], np.argwhere(mask))
    arrs = []
    for rast in rasterObjs:
        arrs.append(rast['array'])
    return (rasterObjs, np.array(arrs), mask, projection, pixelResolution, intersectedBbox)

#


def write(arr, mask, projection, resolution, bbox, nodata, path, format='GTiff'):
    xsize = round((bbox[2] - bbox[0])/resolution)
    ysize = round((bbox[3] - bbox[1])/resolution)
    bands = arr.shape[0]
    eType = gdal_array.NumericTypeCodeToGDALTypeCode(arr.dtype)
    driver = gdal.GetDriverByName(format)
    dst_ds = driver.Create(path, xsize=xsize, ysize=ysize,
                           bands=bands, eType=eType)
    dst_ds.SetGeoTransform([bbox[0], resolution, 0, bbox[1], 0, -resolution])
    dst_ds.SetProjection(projection)
    # write bands
    for bidx in range(1, bands + 1):
        finalArr = np.empty(mask.size, arr.dtype)
        finalArr[mask] = nodata
        finalArr[~mask] = arr[bidx - 1]
        finalArr = finalArr.reshape((ysize, xsize))
        band = dst_ds.GetRasterBand(bidx)
        band.SetNoDataValue(float(nodata))
        band.WriteArray(finalArr)
    dst_ds = None


def compareRasterInfo(rast, info):
    if info != None:
        resolution = info["resolution"]
        proj = info["projection"]
        return rast.GetGeoTransform()[1] == resolution and rast.GetProjection() == proj
    info = {"resolution": rast.GetGeoTransform(
    )[1], "projection": rast.GetProjection()}
    rast = None
    return info


def test():
    print(read(['/mnt/AllThings/JSY/RSEI/www/lst.tif', '/mnt/AllThings/JSY/RSEI/www/wet.tif',
                '/mnt/AllThings/JSY/RSEI/www/ndvi.tif', '/mnt/AllThings/JSY/RSEI/www/ndbsi.tif']))


if (__name__ == '__main__'):
    test()
