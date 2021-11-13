class RunFunction:
    """
    Flags which turn on or off specific functions

    m2nc: Converts m-maps to netCDF
    nc2m: Converts netCDF maps to m-maps
    list2m: Converts listed data (i.e. country data in excel) to m-map
    list2nc: Converts listed data (i.e. country data in excel) to netCDF
    """
    def __init__(self, m2nc=False, nc2m=False, list2m=False, list2nc=True):
        self.m2nc = m2nc
        self.nc2m = nc2m
        self.list2m = list2m
        self.list2nc = list2nc
