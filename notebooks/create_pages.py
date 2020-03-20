import jinja2


def create_pages(date, main_chart_countries, countries):
    countries_data = [dict(name=c) for c in countries]
    information = dict(date=date,
                       countries=countries_data,
                       main_chart_countries=", ".join([c.replace("_"," ") for c in main_chart_countries]))
    template_text = open("README.template.md").read()
    template = jinja2.Template(template_text)
    output = template.render(**information)
    outfile = open("../docs/README.md","w")
    outfile.write(output)
    outfile.close()


create_pages("2020-03-19", ["China", "South_Korea", "United_Kingdom", "France", "Italy", "Spain", "United_States_of_America"], ["China"])