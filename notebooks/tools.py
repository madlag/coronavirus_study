import urllib
import urllib.error
import datetime
import matplotlib
import matplotlib.pyplot as plt
import pathlib
import math
import copy
import numpy
import shutil
import sh

epsilon = 0.0001

def ffmpeg_run(command):
    for line in sh.ffmpeg(command,  _err_to_out=True, _iter=True, _out_bufsize=1000):
        print(line)

def to_gif_impl(src, width, dest, src_frame_rate = None):

    palette = "%s_palette.png" % dest

    filters = ""
    if width != None:
        filters += "scale=%s:-1:flags=lanczos," % width
    command = ["-vf", filters + "palettegen"]
    command = ["-i", src, "-y"] + command + [palette]
    print(" ".join(command))

    ffmpeg_run(command)

    command2 = ["-lavfi", filters + "paletteuse=dither=none"]

    if src_frame_rate != None:
        fr_command2 = ["-framerate", str(src_frame_rate)]
    else:
        fr_command2 = []

    command2 = fr_command2 + ["-i", src, "-i", palette, "-y"] + command2 + [dest]


    print(" ".join(command2))

    ffmpeg_run(command2)

class DataProvider:
    def __init__(self):
        self.country_data = None
        self.prepare_data_from_ecdc()

    def prepare_data_from_ecdc(self):
        for i in range(10):
            d = (datetime.datetime.now().date() - datetime.timedelta(days=i))
            try:
                self.prepare_data_from_ecdc_(d.isoformat())
                self.data_date = d
                break
            except urllib.error.HTTPError as e:
                continue

    def prepare_data_from_ecdc_(self, date):
        if self.country_data == None:
            country_data = {}

            import matplotlib.pyplot as plt
            import pandas as pd

            filename = "data/ecdc/" + date + ".xlsx"

            if not pathlib.Path(filename).exists():
                url = "https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-%s.xlsx" % date
                data = urllib.request.urlopen(url).read()
                f = open(filename, "wb")
                f.write(data)
                f.close()

            df = pd.read_excel(filename)
            for i in range(df.shape[0]):
                country = str(df["Countries and territories"][i])
                date = str(df["DateRep"][i])
                cases = int(df["Cases"][i])
                try:
                    deaths = int(df["Deaths"][i])
                except Exception as e:
                    deaths = 0

                if country not in country_data:
                    country_data[country] = []

                entry = {"date":date, "cases":cases, "deaths":deaths}
                country_data[country].append(entry)

            for country, data in country_data.items():
                data.sort(key = lambda x : x["date"])

                cases = 0
                deaths = 0
                for d in data:
                    cases += d["cases"]
                    deaths += d["deaths"]
                    d["cases"] = cases
                    d["deaths"] = deaths
            self.country_data = country_data

    def get_data(self):
        return self.country_data

    def get_data_for_country(self, country):
        return self.country_data[country], self.data_date

class DataProcessor:
    def __init__(self,
                 data_provider,
                 country = "Italy",
                 data_type = "deaths",
                 offset = None,
                 china_italy_offset = 37,
                 new_daily_points = None,
                 min_deaths = 5,
                 max_deaths = 500):
        self.data_provider = data_provider
        self.country = country
        self.data_type = data_type
        self.offset = offset
        self.china_italy_offset = china_italy_offset
        self.new_daily_points = new_daily_points or {}
        self.min_deaths = min_deaths
        self.max_deaths = max_deaths
        
    def prepare_mapping_for_china(self):
        data_type = self.data_type
        values_for_china, data_date = self.data_provider.get_data_for_country("China")
        mapping_for_china = {}
        for v in values_for_china:
            d = datetime.datetime.fromisoformat(v["date"]) + datetime.timedelta(days = -self.offset + self.china_italy_offset)
            d = d.isoformat()[:10]
            mapping_for_china[d] = v[data_type] + epsilon
        return mapping_for_china
        
    def analyze_data(self, x, y):
        assert(len(x) == len(y))
        filtered = ([],[])

        time_to_min_deaths = None
        for i, xx in enumerate(x) :
            yy = y[i]
            if yy > self.min_deaths:
                if time_to_min_deaths is None:
                    time_to_min_deaths = xx
                if yy < self.max_deaths:
                    filtered[0].append(xx)
                    filtered[1].append(math.log2(yy))
                
        if len(filtered[0]) <= 2:
            self.regression = None
            return
        
        coeff = numpy.polyfit(*filtered, 1)
        
        return coeff, time_to_min_deaths, len(filtered[0])

    def get_data(self, china_comparison = False):
        country = self.country
        data_type = self.data_type
        values, update_date = self.data_provider.get_data_for_country(self.country)
        values = copy.deepcopy(values)        
        
        if china_comparison:
            mapping_for_china = self.prepare_mapping_for_china()
        
        new_date = (update_date + datetime.timedelta(days = 1)).isoformat()
        if country in self.new_daily_points:
            values += [{"date":new_date, data_type:self.new_daily_points[country][self.data_type]}]

        start_time = datetime.datetime(2020, 1, 1)
        dates = [(datetime.datetime.fromisoformat(v["date"]) - start_time).days + self.offset for v in values]
        
        if china_comparison:
            y = [v[data_type]/mapping_for_china.get(v["date"][:10], epsilon) for v in values]
        else:
            y = [v[data_type] for v in values]

        return dates, y


class CountryInfoStore:
    def __init__(self, data_provider, debug = False):
        self.data_provider = data_provider
        self.debug = debug

        self.build()

    def build(self):
        countries = self.data_provider.get_data().keys()

        valid_countries = {}

        black_list = ["Cases_on_an_international_conveyance_Japan"]

        for c in countries:
            if c in black_list:
                continue
            dp = DataProcessor(self.data_provider, c, offset = 0)
            x,y = dp.get_data()
            regression  = dp.analyze_data(x, y)

            if regression is not None:
                (a,b), time_to_min_deaths, data_points_count = regression
                #print(c, data_points_count)
                print(c, time_to_min_deaths)

                time_base = 1/a
                shift = b * time_base
                print(c, shift)
                valid_countries[c] = dict(country=c,
                                          deaths=y[-1],
                                          shift = time_to_min_deaths,
                                          trend_base_shift=shift,
                                          trend_time_base=time_base)

        italy_shift = valid_countries["Italy"]["shift"]
        for k,v in valid_countries.items():
            v["shift"] = round(v["shift"] - italy_shift)
            print(v, italy_shift)
            v["trend_base_shift"] += v["shift"]
            print(v)

        self.countries = valid_countries
        if self.debug:
            vc = list(valid_countries.values())
            vc.sort(key=lambda x : x["shift"])

            for c_info in vc:
                print('%s=%s,' % (c_info["country"], c_info))

    def get_country_info(self, country):
        return self.countries[country]

class CountryGraph:
    def __init__(self,
                 data_provider,
                 country_info_store,
                 country = "Italy",
                 log_axis = True,
                 data_type = "deaths",
                 china_comparison = False, 
                 plot_kwargs = None,
                 draw_reference = False,
                 start = 40,
                 end = 80):
        self.data_provider = data_provider
        self.country_info_store = country_info_store
        self.country = country
        self.log_axis = log_axis
        self.data_type = data_type
        self.china_comparison = china_comparison        
        self.plot_kwargs = plot_kwargs or {}
        self.country_info = self.country_info_store.get_country_info(self.country)
        self.offset = int(self.country_info["shift"])
        self.start = start
        self.end = end

        self.dp = DataProcessor(self.data_provider, self.country, self.data_type, offset = - self.offset)
        self.draw_reference = draw_reference


    def growth_reference_plot(self):
        time_base = self.country_info["trend_time_base"]
        shift = self.country_info["trend_base_shift"]

        dates = [x for x in range(self.start, self.end)]
        data = [max(1, 2 ** ((x + shift) / time_base)) for x in dates]

        while data[-1] > 5000:
            data = data[:-1]
            dates = dates[:-1]

        plt.plot(dates,
                 data,
                 label="%s: doubling every %02.2f days" % (self.country, time_base),
                 linestyle='dotted')

#                 linestyle='dotted')

    def plot(self, clip = 0):
        dates, values = self.dp.get_data(self.china_comparison)
        assert(len(dates) == len(values))
        dates = dates[:len(dates) - clip]
        values = values[:len(values) - clip]
        
        if self.log_axis:
            plt.yscale("log")
        label = self.country 
        offset = self.offset
        if offset != 0:
            label += " (%+d days)" % (offset)
        plt.plot(dates,
                values,
                label = label,
                ** self.plot_kwargs)

        if self.draw_reference:
            self.growth_reference_plot()




class MultiCountryGraph:
    def __init__(self,
                 data_provider,
                 country_info_store,
                 countries = ["Italy", "France"],
                 reference_for_countries = None,
                 sort_countries_by_offset = True,
                 log_axis = True,
                 data_type = "deaths",
                 china_comparison = False, 
                 growth_reference = True,
                 visually_impaired = True):
        self.data_provider = data_provider
        self.country_info_store = country_info_store
        self.countries = countries
        self.reference_for_countries = reference_for_countries or []
        if sort_countries_by_offset:
            self.countries.sort(key = lambda x : country_info_store.get_country_info(x)["shift"])

        self.log_axis = log_axis
        self.data_type = data_type
        self.china_comparison = china_comparison        
        self.growth_reference = growth_reference and not china_comparison
        
        self.visually_impaired = visually_impaired
#        self.linestyles = ['-', '--', '+', ':', 'solid']
        self.markers = [None,  "o", "s", "v", "P","X", "x"]
        if self.visually_impaired:
            if len(countries) > len(self.markers):
                raise Exception("Too many countries to plot")

        
    def plot_(self, filename = None, clip = 0):
        if filename != None:     
            matplotlib.use("Agg")  # Prevent showing stuff
            dpi = 160
        else:
            dpi = 80
            
        fig=plt.figure(figsize=(12, 8), dpi=dpi, facecolor='w', edgecolor='k')

        self.country_graphs = []
        for i, country in enumerate(self.countries):
            draw_reference = len(self.countries) == 1

            marker = self.markers[i] if self.visually_impaired else None                
            linewidth = 3 if marker == None else 1

            plot_kwargs = dict(linewidth=linewidth,
                               linestyle=None,
                               markersize=7, 
                               marker = marker)

            if country in self.reference_for_countries:
                draw_reference = True
            draw_reference = draw_reference and self.data_type == "deaths"

            g = CountryGraph(self.data_provider,
                             self.country_info_store,
                             country,
                             self.log_axis, 
                             self.data_type, 
                             self.china_comparison,                             
                             plot_kwargs,
                             draw_reference = draw_reference)
            g.plot(clip = clip)
            self.country_graphs.append(g)
            
        if self.growth_reference:
            self.growth_reference_plot()
            
        _ = plt.legend()
        data_date = self.data_provider.data_date
        title = "%s by country over time, %s data from ECDC.\n" % (self.data_type.capitalize(), data_date)
        title += "Dates are shifted for each country to facilitate comparison."
        if self.log_axis:
            title += "Logarithmic scale.\n"

        plt.title(title,
                  fontdict = {'fontweight' : "bold", 'verticalalignment': 'baseline'})
        plt.xlabel("Days since 01-01-2020 for Italy (use offset for other countries).\n Produced by https://github.com/madlag/coronavirus_study/")
        plt.ylabel(self.data_type)

        data_type_offset = 0 if self.data_type == "deaths" else - 14
        plt.xlim(40 + data_type_offset, 120 + data_type_offset)
        
        if filename is not None:
            fig.savefig(filename)           
            
    def plot(self, filename = None, clip = 0):
        try:
            backend_ =  matplotlib.get_backend() 
            self.plot_(filename, clip = clip)
        finally:
            matplotlib.use(backend_) # Reset backend

    def movie(self, movie_filename):
        max_back = 15

        try:
            shutil.rmtree("temp_dir")
        except:
            pass

        pathlib.Path("temp_dir").mkdir()

        for index in range(max_back):
            clip = max_back - index - 1
            self.plot(filename = "temp_dir/deaths_back_%03d.png" % index, clip=clip)

        for i in range(5):
            self.plot(filename = "temp_dir/deaths_back_%03d.png" % (max_back + i), clip=0)

        path = pathlib.Path("output.gif")
        to_gif_impl("temp_dir/deaths_back_%03d.png", None, str(path), 2)
        path.rename(movie_filename)

    def growth_reference_plot(self):
        china_italy_offset = 37
        reference_shift = dict(deaths=china_italy_offset + 12.5,
                               cases=china_italy_offset)
        reference_time_base = 2.2
        shift =  - reference_shift[self.data_type]
        time_base = reference_time_base

        plt.plot([max(1, 2**((x + shift) / time_base)) for x in range(0, 78)],
                 label="Doubling every %02.2f days" % time_base,       
                 linestyle='dotted')



data_provider = DataProvider()

country_info_store = CountryInfoStore(data_provider, debug = True)
all_countries = country_info_store.countries
data_date = data_provider.data_date

root = pathlib.Path("graphs/%s" % (data_date))
if not root.exists():
    root.mkdir(parents= True)


if True:
    g = MultiCountryGraph(data_provider,
                          country_info_store,
                          ["China", "South_Korea", "United_Kingdom", "France", "Italy", "Spain", "United_States_of_America"],
                          log_axis = True,
                          data_type = "deaths",
                          visually_impaired = False,
                          china_comparison = False)
    g.plot(root/("%s_%s.png" % (data_date, "main_comparison")))

for c in all_countries:
    print(c)
    for dt in ["deaths", "cases"]:
        countries = ["China", "Italy", "South_Korea"]
        references = [c]
        if c not in countries:
            countries.append(c)
        g = MultiCountryGraph(data_provider,
                              country_info_store,
                              countries,
                              reference_for_countries = references,
                              log_axis = True,
                              data_type = dt,
                              visually_impaired = True,
                              china_comparison = False,
                              growth_reference = len(references) == 0)
        dest_file_name = root / "countries" / c / ("%s_%s_%s.png" % (data_date, c, dt))
        g.plot(dest_file_name)

        dest_file_name = root / "countries" / c / ("%s_%s_%s.gif" % (data_date, c, dt))
        g.movie(dest_file_name)
