import jinja2

jloader=jinja2.FileSystemLoader(searchpath=".")
jenv = jinja2.Environment(loader=jloader, undefined=jinja2.StrictUndefined)

def apply_template(template_file_name, information, output_file_name):
    template = jenv.get_template(template_file_name)
    output = template.render(**information)
    outfile = open(output_file_name, "w")
    outfile.write(output)
    outfile.close()

def hr_cname(c):
    return c.replace("_", " ")

def create_pages(date, main_chart_countries_set, countries):
    global_url_prefix = "https://raw.githubusercontent.com/madlag/coronavirus_study/master/notebooks/graphs"
    blacklist = ["Cases_On_An_International_Conveyance_Japan"]
    most_impacted_countries_data = [dict(name=hr_cname(c), path=c) for c,info in countries.items() if info["most_impacted"] and c not in blacklist]
    other_countries_data = [dict(name=hr_cname(c), path=c) for c,info in countries.items() if not info["most_impacted"]]

    main_chart_countries_data = {}

    for name, main_chart_countries in main_chart_countries_set:
        main_chart_countries_data[name] = ", ".join([hr_cname(c) for c in main_chart_countries])

    informations = dict(date=date,
                       most_impacted_countries_data=most_impacted_countries_data,
                       other_countries_data=other_countries_data,
                       main_chart_countries_data=main_chart_countries_data,
                       url_prefix="%s/%s/%s" % (global_url_prefix, date, date))


    apply_template("README.template.md", informations, "../docs/README.md")

    for c, country_information in countries.items():
        most_impacted = country_information["most_impacted"]
        if most_impacted:
            growth_rate = "%02.2f" % country_information["trend_time_base"]
            sections = (("animated", "gif"), ("static", "png"))
        else:
            growth_rate = None
            sections = (("static", "png"),)

        deaths = country_information["deaths"]
        data_types = ["cases"]
        if deaths > 0:
            data_types = ["deaths", "cases"]

        chart_sections = {}
        for data_type in data_types:
            chart_sections[data_type] = []
            for chart_type, chart_suffix in sections:
                chart_sections[data_type].append(dict(data_type=data_type, data_type_string=data_type, chart_type=chart_type, chart_suffix=chart_suffix))
                chart_sections[data_type].append(dict(data_type="day_" + data_type, data_type_string="daily " + data_type, chart_type=chart_type, chart_suffix=chart_suffix))

        country_information = dict(date=date,
                                   country=dict(name=hr_cname(c),
                                                growth_rate = growth_rate,
                                                chart_sections=chart_sections,
                                                most_impacted = most_impacted),
                                   url_prefix="%s/%s/countries/%s/%s_%s" % (global_url_prefix, date, c, date, c),
                                   )
        apply_template("country.template.md",
                       country_information,
                       "../docs/countries/%s.md" % c)


if __name__ == "__main__":
    create_pages("2020-03-20", ["China", "South_Korea", "United_Kingdom", "France", "Italy", "Spain", "United_States_of_America"], ["China", "South_Korea"])