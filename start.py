
from bs4 import BeautifulSoup
import requests
import ast
import os
from pyecharts import options as opts
from pyecharts.charts import Map, Page, Pie, WordCloud
from pyecharts.globals import SymbolType
import time
t = str(time.time())
URL = "https://3g.dxy.cn/newh5/view/pneumonia"          # data source
data_route = ".\\map" + t+".html"                              # the html save route
save_route = ".\\data" + t + ".txt"                              # the back-up data save route
fp = open(save_route, "w")
fp.close()

def check_empty(file_name):
    """for back up data, check if the data file is empty, if empty, delete it."""
    if os.stat(file_name).st_size == 0:
        pass
    else:
        os.remove(file_name)


def get_data(url):
    """ get data from 丁香园 and process then"""
    result_list = []
    try:
        r = requests.get(url)
        rt = r.text.encode("ISO-8859-1").decode("utf-8")
        soup = BeautifulSoup(rt, "html.parser")
        print("get data from : "+ url)
    except:
        print("wrong")

    result = str(soup.select('#getAreaStat'))[:-25]

    result = result.replace('[<script id="getAreaStat">try { window.getAreaStat = [', "").split("]},")
    check_empty(save_route)
    for item in result:
        # print(item)
        i = item.split(',"comment"')
        print(i)
        p = i[0] + "}"
        print(p)
        with open(save_route, "a") as f:
            """backup the data"""
            f.writelines(p)
        tran_dict = ast.literal_eval(p)
        result_list.append(tran_dict)
    print(result_list)
    return result_list


data = get_data(URL)


# 感染人数
confirmedCount = [[data[i].get("provinceShortName"), data[i].get("confirmedCount")] for i in range(len(data))]
print("感染人数", confirmedCount)
total_confirmedCount = 0
for i in confirmedCount:
    total_confirmedCount += i[1]        # count the total confirmed people

# 治愈人数
curedCount = [[data[i].get("provinceShortName"), -1*data[i].get("curedCount")]
              for i in range(len(data)) if data[i].get("curedCount") != 0]
print("治愈人数", curedCount)
total_curedCount = 0        # count the total cured people
for i in curedCount:
    total_curedCount += i[1]


# 死亡人数
deadCount = [[data[i].get("provinceShortName"), data[i].get("deadCount")]
             for i in range(len(data)) if data[i].get("deadCount") != 0]
print("死亡人数", deadCount)
total_deadCount = 0
for i in deadCount:     # count the total dead people
    total_deadCount += i[1]

total = [["未治愈人数", total_confirmedCount + total_curedCount - total_deadCount],["治愈人数", -1*total_curedCount], ["死亡人数", total_deadCount]]


def map_map():
    """add the element in to the html file"""
    map = (         # map type chart
        Map(init_opts=opts.InitOpts(width="6"))
        .add(
            "地图",
            [],
        )
        .add(
            "感染病例",
            [i for i in confirmedCount]
            )
        .add(
            "痊愈病例",
            [j for j in curedCount]
        )
        .add(
            "死亡病例",
            [k for k in deadCount]
        )
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(min_= -1000, max_=1000, border_color="#ccc", border_width=2,
                                              background_color="#eee",

                                              range_color=["lightskyblue", "lightyellow", "red"],
                                              range_opacity=0.5),
            title_opts=opts.TitleOpts(title="2019-nCov中国疫情"),
        )
    )

    wordcloud = (           # add word cloud chart
        WordCloud(init_opts=opts.InitOpts(width="600"))
        .add("", confirmedCount, word_size_range=[20, 200], shape=SymbolType.DIAMOND)
        .set_global_opts(title_opts=opts.TitleOpts(title=""),
                         visualmap_opts=opts.VisualMapOpts(max_=500, range_color=["gold", "red"]))
    )
    piec = (        # add pie chart 1
        Pie()
        .add(
            "",
            confirmedCount,
            radius=["40%", "75%"],
            rosetype="area",
            )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=" "),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_top="15%", pos_left="2%"
            ),
        )
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    piec2 = (           # add pie chart 2
        Pie()
        .add(
            "",
            total,
            radius=["40%", "75%"],

            )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=" "),
            legend_opts=opts.LegendOpts(
                orient="vertical", pos_top="15%", pos_left="2%"
            ),
        )
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    page = (        # let map, wordcloud, pie1 and pie2 show in the same page
        Page()
        .add(map)
        .add(wordcloud)
        .add(piec)
        .add(piec2)
    )
    return page


if __name__ == "__main__":
    m = map_map()
    m.render(path=data_route)




