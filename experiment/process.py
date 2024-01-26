import os
import json
import datetime
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Line
from pyecharts.charts import EffectScatter
from pyecharts import options as opts
from pyecharts.charts import Pie
from pyecharts.commons.utils import JsCode
import numpy as np
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
from wordcloud import WordCloud, STOPWORDS
from pyecharts.globals import ThemeType



class Wechat:
    def __init__(self, dir_name, file_name):
        self.workplace_dir = dir_name
        self.file_name = file_name
        self.data = None
        self.content_list = []
        self.structure = []
        self.dataFrame = None
        self.read_and_get_utilize()
        self.transform_DataFrame()

    def read_and_get_utilize(self):
        if self.file_name.endswith('.json'):
            try:
                with open(self.file_name, encoding='utf-8') as f:
                    self.data = json.load(f)
                    print("-------数据载入成功-------")
                    for item in self.data:
                        time_stamp = item['msgCreateTime']
                        real_time = datetime.datetime.fromtimestamp(
                                    time_stamp).strftime('%Y-%m-%d %H:%M:%S')
                        item['realTime'] = real_time
            except:
                pass
    
    def transform_DataFrame(self):
        for sta in self.data:
            one = sta['mesDes']
            twe = sta['messageType']
            three = sta['msgContent']
            year = sta['realTime'][:4]
            month = sta['realTime'][5:7]
            day = sta['realTime'][8:10]
            hour = sta['realTime'][11:13]
            total = [one, twe, three, year, month, day, hour]
            self.structure.append(total)
        self.dataFrame = pd.DataFrame(self.structure, columns=['mesDes',
                                                      'messageType',
                                                      'msgContent',
                                                      'year',
                                                      'month',
                                                      'day',
                                                      'hour'])  # 储存了所有聊天记录的数量，而不仅是文本信息。
        
    def process_content(self):
        for dic in self.data:
            if dic["messageType"] == 1:
                content = dic["msgContent"]
                if dic["mesDes"] == 1:
                    msg = content.strip().split(":\n")[0].replace("\n", " ").replace("\r", " ")
                else:
                    msg = content.strip().replace("\n", " ").replace("\r", " ")
                self.content_list.append(msg)
            
        return self.content_list

    def calculate_24hours_records(self):
        series = self.dataFrame.groupby('hour').size()
        l1 = list(series.index)
        l1_mos = l1[1:] + ['24'] #为了直观，将0点改为24点
        l2 = [int(a) for a in series.values]
        l2_mos = l2[1:] + [l2[0]]
        l3 = [int(b/2) for b in series.values]
        l3_mos = l3[1:] + [l3[0]]


        bar = Bar()
        bar.add_xaxis(l1_mos)
        bar.add_yaxis("柱状图", l2_mos, label_opts=opts.LabelOpts(position="top"), itemstyle_opts=opts.ItemStyleOpts(color="#f07c82"),)

        line = Line()
        line.add_xaxis(l1_mos)
        line.add_yaxis("折线图",l3_mos,is_smooth=True, label_opts=opts.LabelOpts(is_show=False),linestyle_opts=opts.LineStyleOpts(color="#621624"),)

        effect_scatter = EffectScatter()
        effect_scatter.add_xaxis(l1_mos)
        effect_scatter.add_yaxis(
            series_name="涟漪特效",
            y_axis = l3_mos,
            symbol = "circle",  # 涟漪特效的形状
            effect_opts=opts.EffectOpts(scale=4),  # 设置涟漪效果的大小
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color="#73575c"),
        )

        line.overlap(bar)
        line.overlap(effect_scatter)

        # 配置图表选项
        line.set_global_opts(
            title_opts=opts.TitleOpts(title="一整年的日均聊天记录分布计数图"),
            tooltip_opts=opts.TooltipOpts(is_show=True),
            xaxis_opts=opts.AxisOpts(name="24-hour", axislabel_opts=opts.LabelOpts(font_size=16)),  # 设置横坐标标注
            yaxis_opts=opts.AxisOpts(name="聊天记录总数", axislabel_opts=opts.LabelOpts(font_size=16)),  # 设置纵坐标标注

        )

        line.render("./pictures/calculate_24hours_records.html")

    def statistics_records_catalogies(self):
        calculated_catalogies_series = self.dataFrame.groupby('messageType').size()
        matching = {1:'文本', 3:'图片', 34:'语音', 47:'表情包', 43:'视频', 48:'位置', 49:'文件信息', 10000:'系统信息',42:'视频号',50:'链接',11000:'通话'}
        calculated_catalogies_series = calculated_catalogies_series.rename(index=matching)
        inner_x_data = [str(calculated_catalogies_series.idxmax())]
        inner_y_data = [int(calculated_catalogies_series.max())]
        inner_data_pair = [list(w) for w in zip(inner_x_data, inner_y_data)]

        series_without_max = calculated_catalogies_series.drop(index=calculated_catalogies_series.idxmax())
        outer_x_data = [str(sid) for sid in series_without_max.index]
        outer_y_data = [int(a) for a in series_without_max.values]
        outer_data_pair = [list(z) for z in zip(outer_x_data, outer_y_data)]

        (
            Pie(init_opts=opts.InitOpts(width="1000px", height="600px"))
            .add(
                series_name="信息类别",
                data_pair=inner_data_pair,
                radius=[0, "30%"],
                label_opts=opts.LabelOpts(position="inner"),
            )
            .add(
                series_name="信息类别",
                radius=["40%", "55%"],
                data_pair=outer_data_pair,
                label_opts=opts.LabelOpts(
                    position="outside",
                    formatter="{a|{a}}{abg|}\n{hr|}\n {b|{b}: }{c}  {per|{d}%}  ",
                    background_color="#eee",
                    border_color="#aaa",
                    border_width=1,
                    border_radius=4,
                    rich={
                        "a": {"color": "#999", "lineHeight": 22, "align": "center"},
                        "abg": {
                            "backgroundColor": "#e3e3e3",
                            "width": "100%",
                            "align": "right",
                            "height": 22,
                            "borderRadius": [4, 4, 0, 0],
                        },
                        "hr": {
                            "borderColor": "#aaa",
                            "width": "100%",
                            "borderWidth": 0.5,
                            "height": 0,
                        },
                        "b": {"fontSize": 16, "lineHeight": 33},
                        "per": {
                            "color": "#eee",
                            "backgroundColor": "#334455",
                            "padding": [2, 4],
                            "borderRadius": 2,
                        },
                    },
                ),
            )
            .set_global_opts(legend_opts=opts.LegendOpts(pos_left="left", orient="vertical"),
                             title_opts=opts.TitleOpts(title="一整年聊天记录类别统计图",
                                                       pos_left="center",  # 设置标题居中
                                                       pos_top="top",  # 设置标题在顶部
                                                       ))
            .set_series_opts(
                tooltip_opts=opts.TooltipOpts(
                    trigger="item", formatter="{a} <br/>{b}: {c} ({d}%)"
                )
            )
            .render("./pictures/statistics_records_catalogies.html")
        )

    def calculate_records_count(self):
        seperate_records = self.dataFrame.groupby('mesDes').size()
        new_index = {0:'Lu(🏃🏻🕶️🧑🏻‍💻)',1:'Xi(🎀🎊🎁)'}
        seperate_records = seperate_records.rename(index=new_index)
        l1 = list(seperate_records.index)
        l2 = [int(a) for a in seperate_records.values]
        (
            Bar()
            .add_xaxis(l1)
            .add_yaxis("", l2, category_gap="60%")# category_gap同一系列的柱间距离，默认为类目间距的 20%，可设固定值
            .set_series_opts(
                itemstyle_opts={ 
                    "normal": {
                        "color": JsCode(
                            """new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                        offset: 0,
                        color: 'rgba(0, 244, 255, 1)'
                    }, {
                        offset: 1,
                        color: 'rgba(0, 77, 167, 1)'
                    }], false)"""
                        ),
                        "barBorderRadius": [30, 30, 30, 30],
                        "shadowColor": "rgb(0, 160, 221)",
                    }
                }
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="给对方发的聊天记录计数图",
                                                       pos_left="center",
                                                       pos_top="top"))
            .render("./pictures/calculate_records_count.html")
        )

    def masked_divide_words(self, masked_pic_firname):
        alice_mask = np.array(Image.open(masked_pic_firname))
        stopwords = set(STOPWORDS)
        stopwords.add("said")
        wc = WordCloud(background_color="white", max_words=2000, mask=alice_mask,
                    stopwords=stopwords, contour_width=3, contour_color='steelblue',font_path="fangsong.ttf")
        wc.generate('\n'.join(self.content_list))
        wc.to_file(path.join(self.workplace_dir, "pictures/words_masked.png"))


    def analyze_monthly_records(self):
        result = self.dataFrame.groupby([self.dataFrame['year'], self.dataFrame['month']]).size()
        result = result.reset_index()
        result.columns = ['year', 'month', 'total_value']
        result['year_month'] = result['year'].astype(str) + '-' + result['month'].astype(str)

        bar_chart = (
            Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))  # Specify a light theme
            .add_xaxis(result['year_month'].tolist())
            .add_yaxis(
                "Total Value",
                result['total_value'].tolist(),
                label_opts=opts.LabelOpts(is_show=True, position='top', color='black'),  # Show data labels on top
                itemstyle_opts=opts.ItemStyleOpts(color='skyblue'),  # Set bar color
            )
            .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=-45),
                    axisline_opts=opts.AxisLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="gray")),
                ),
                title_opts=opts.TitleOpts(title="the total number of monthly messages"),
                yaxis_opts=opts.AxisOpts(
                    name="Total Value",
                    axisline_opts=opts.AxisLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(color="gray")),
                    splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed")),
                ),
                datazoom_opts=[opts.DataZoomOpts(is_show=True, orient="horizontal", xaxis_index=[0], range_start=0, range_end=100, pos_bottom="0.05%")],  # Enable data zooming
            )
        )
        bar_chart.render("./pictures/bar_chart.html")
        

if __name__=="__main__":
    dir_name = path.dirname(__file__) if "__file__" in locals() else os.getcwd() 
    json_file = path.join(dir_name,'data/Chat_166fe9a8049b4c4296159926114f0557.json')
    wc = Wechat(dir_name, json_file)

    # content_list = wc.process_content()
    # while True:
    #     text = input("请输入是否保存所有聊天记录的文本.(1---保存到当前路径, 0---不保存)\n")
    #     if int(text) == 0:
    #         break
    #     elif int(text) == 1:
    #         dir_name = input("请输入保存的名称，以.txt后缀结尾\n")
    #         try:
    #             fout = open(str(dir_name), "w")
    #             for per in content_list:
    #                 fout.write("{}\n".format(per))
    #             fout.close()
    #             print("保存成功")
    #         except:
    #             pass
    #         break
    #     else:
    #         print("请输入正确的数字！！！\n")
    #         continue
    # print("==已获取文本信息==")

    # input("正在计算一天中不同聊天时段记录数量的分布，请按回车键继续：")
    # wc.calculate_24hours_records()
    # print("successfully\n")

    # input("正在统计聊天记录中不同类型的数量，请按回车键继续：")
    # wc.statistics_records_catalogies()
    # print("successfully\n")

    # input("正在统计彼此一年来的聊天记录数，请按回车键继续：")
    # wc.calculate_records_count()
    # print("successfully\n")

    # input("正在统计不同月份的聊天记录数，请按回车键继续：")
    # wc.analyze_monthly_records()
    # print("successfully")

    # firname = input("请输入用于maske的图片的路径.(请用全局路径)")  # suitable_masked.png
    # while True: 
    #     if os.path.isabs(firname):
    #         break
    #     else:
    #         firname = input("您输入的路径有误，请重新输入图片的全局路径：")
    #         continue
    # wc.masked_divide_words(firname)
    