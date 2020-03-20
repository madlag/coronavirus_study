import jinja2

def apply_template(template_file_name, information, output_file_name):
    template_text = open(template_file_name).read()
    template = jinja2.Template(template_text)
    output = template.render(**information)
    outfile = open(output_file_name, "w")
    outfile.write(output)
    outfile.close()

def hr_cname(c):
    return c.replace("_", " ")

def create_pages(date, main_chart_countries, countries):
    global_url_prefix = "https://raw.githubusercontent.com/madlag/coronavirus_study/master/notebooks/graphs"
    countries_data = [dict(name=hr_cname(c), path=c) for c in countries]
    information = dict(date=date,
                       countries=countries_data,
                       main_chart_countries=", ".join([hr_cname(c) for c in main_chart_countries]),
                       url_prefix="%s/%s/%s" % (global_url_prefix, date, date))

    apply_template("README.template.md", information, "../docs/README.md")

    for c in countries:
        country_information = dict(date=date,
                                   country=dict(name=hr_cname(c)),
                                   url_prefix="%s/%s/countries/%s/%s_%s" % (global_url_prefix, date, c, date, c))
        apply_template("country.template.md",
                       country_information,
                       "../docs/countries/%s.md" % c)


if __name__ == "__main__":
    create_pages("2020-03-20", ["China", "South_Korea", "United_Kingdom", "France", "Italy", "Spain", "United_States_of_America"], ["China", "South_Korea"])