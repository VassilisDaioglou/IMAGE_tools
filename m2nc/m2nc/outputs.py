# pylint: disable=line-too-long
"""
class: WriteMaps
    - Contains methods for producing NetCDF maps and thier metadata

"""
import netCDF4
import datetime as dt
import subprocess
import numpy as np
from metadata import __version__, __name__, __reference__
from dirs import OutputDir

class WriteMaps:
    def __init__(self, outmap, title, varname, varunit, outname, timexist):
        self.outmap = outmap
        self.title = title
        self.varname = varname
        self.varunit = varunit
        self.outname = outname
        self.timexist = timexist

    def get_ncattributes(self):
        """
        netCDF Attributes to be used on all map outputs
        """
        title = self.title
        unit = self.varunit
        author = "Vassilis Daioglou"
        contact = "e-mail: v.daioglou@uu.nl | twitter: @vassican | ResearchGate: https://www.researchgate.net/profile/Vassilis_Daioglou"
        date = str(dt.datetime.now())
        model = "{} - Version {}".format(__name__, __version__)
        institution = "Copernicus Institute of Sustainable Development (https://www.uu.nl/en/research/copernicus-institute-of-sustainable-development)"
        institution2 = "PBL Netherlands Environmental Assessment Agency (http://www.pbl.nl/en)"
        references = __reference__
        disclaimer = "http://themasites.pbl.nl/models/image/index.php/IMAGE-rights"
        
        try: 
            repository = subprocess.check_output(['git', 'remote', '-v'])
            repository = repository.split()[1]
             
        except:
            repository = 'Not versioned'
        
        try:
            revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
            revision = revision.split()[0]
        except:
            revision = 'Not versioned'
        
        return title, unit, author, contact, date, model, repository, revision, institution, institution2, references, disclaimer

    def maptime2nc(self, dim1='EMPTY'):
        """
        Creates a netCDF file from a relevant array
        Array must contain at least two axes: latitude, longitude
            Optional additional axes (boolean):
                - Time
                - One extra dimenson (i.e. crop type)

        Parameters
        ------
        outmap: array with map to be created
        timexist: Boolean defining if there is a time dimension
        
        Dictionary of the definition of the first dimension
        outname: String with the name of the output file (excluding .nc)

        Attributes:
            title: String with the title of the intended output
            varname: String with the name of the variable being presented
            varunit: String with the unit of the variable being presented
        
        Proecdure:
            1. Creates an netCDF object (ncfile) in relevant output directory with relelvant name
            2. Defines dimension of ncfile (latitude, logitude, time, extra-dimension)
            3. Gets attributes of ncfile
            4. Created variables of the ncfile and fills inthe  contents of the dimensions 

        Code based on an original from Utpal Rai:
        https://iescoders.com/writing-netcdf4-data-in-python/

        TODO:
        Time dimension labels are wrong.
        """
        # Create nc-file with correct dimensions
        ncfile = netCDF4.Dataset(OutputDir.nc_out_dir + self.outname + '.nc', mode='w', format='NETCDF4_CLASSIC')
        
        if self.timexist:
            lat_dim = ncfile.createDimension('lat', len(self.outmap[0])) # latitude axis
            lon_dim = ncfile.createDimension('lon', len(self.outmap[0][0])) # longitude axis
            time_dim = ncfile.createDimension('time', len(self.outmap)) # time axis
        else:
            lat_dim = ncfile.createDimension('lat', len(self.outmap)) # latitude axis
            lon_dim = ncfile.createDimension('lon', len(self.outmap[0])) # longitude axis

        if dim1 != 'EMPTY':
            try:
                dim1_dim = ncfile.createDimension('dimension1', len(dim1)) # dim1 axis if dictionary
            except TypeError:
                dim1_dim = ncfile.createDimension('dimension1', dim1) # dim1 axis if scalar

        # Global Attributes
        ncfile.title, ncfile.unit, ncfile.author, ncfile.contact, ncfile.date, ncfile.model, ncfile.repository, ncfile.revision, ncfile.institution, ncfile.institution2, ncfile.references, ncfile.disclaimer = self.get_ncattributes()

        # Define variables concerning:
        #  (i) Latitude, (ii) Logitude, (iii) Time, (iv) Extra dimention
        # (iii) and (iv) are optional
        lat = ncfile.createVariable('lat', np.float32, ('lat',))
        lat.standard_name = 'latitude'
        lat.units = 'degrees_north'
        lon = ncfile.createVariable('lon', np.float32, ('lon',))
        lon.standard_name = 'longitude'
        lon.units = 'degrees_east'
        
        if self.timexist:
            time = ncfile.createVariable('time', np.float64, ('time',))
            time.units = 'days since 1970-01-01'
            time.standard_name = 'time'
        
        if dim1 != 'EMPTY':
            dim1_var = ncfile.createVariable('dimension1', np.float32, ('dimension1',))
            dim1_var.standard_name = str(dim1)
            dim1_var.units = '-'
        
        # Assign these variables to an ncfile
        if dim1 == 'EMPTY':
            if self.timexist:
                var = ncfile.createVariable(self.outname,np.float64,('time','lat','lon'))
            else:
                var = ncfile.createVariable(self.outname,np.float64,('lat','lon'))
        else:
            if self.timexist:
                var = ncfile.createVariable(self.outname,np.float64,('time','lat','lon','dimension1'))
            else:
                var = ncfile.createVariable(self.outname,np.float64,('lat','lon','dimension1'))
        
        var.standard_name = self.varname
        var.units = self.varunit

        # Writing data in first variable
        nlats = len(lat_dim)
        nlons = len(lon_dim)

        if self.timexist:
                ntimes = len(time_dim)

        if dim1 != 'EMPTY':
            ndim1 = len(dim1_dim)
     
        lat[:] = 90. - (180./nlats)*np.arange(nlats) # north pole to south pole
        lon[:] = -180. + (180./nlats)*np.arange(nlons) # 180degree longitude eastward
        if dim1 != 'EMPTY':
            dim1_var[:] = np.arange(ndim1) # 1st dimension length
        
        if self.timexist:
            time[:] = np.arange(ntimes) # times values 1:length
            var[:,:,:] = self.outmap[:,:,:]
        else:
            var[:,:] = self.outmap[:,:]

        if self.timexist:
            dates = [dt.datetime(1970,1,1,0),dt.datetime(1975,1,1,0),dt.datetime(1980,1,1,0),dt.datetime(1985,1,1,0),
                    dt.datetime(1990,1,1,0),dt.datetime(1995,1,1,0),dt.datetime(2000,1,1,0),dt.datetime(2005,1,1,0),
                    dt.datetime(2010,1,1,0),dt.datetime(2015,1,1,0),dt.datetime(2020,1,1,0),dt.datetime(2025,1,1,0),
                    dt.datetime(2030,1,1,0),dt.datetime(2035,1,1,0),dt.datetime(2040,1,1,0),dt.datetime(2045,1,1,0),
                    dt.datetime(2050,1,1,0),dt.datetime(2055,1,1,0),dt.datetime(2060,1,1,0),dt.datetime(2065,1,1,0),
                    dt.datetime(2070,1,1,0),dt.datetime(2075,1,1,0),dt.datetime(2080,1,1,0),dt.datetime(2085,1,1,0),
                    dt.datetime(2090,1,1,0),dt.datetime(2095,1,1,0),dt.datetime(2100,1,1,0)]

            time = netCDF4.date2num(dates, time.units)

        if dim1 != 'EMPTY':
            try:
                dim1_labels = dim1.values()                 # Assign dictionary values
                dim1_var = dim1_labels
            except AttributeError:
                dim1_labels = [i + 1 for i in range(dim1)]  # Simply set a list of indices
                dim1_var = dim1_labels

        ncfile.close()
