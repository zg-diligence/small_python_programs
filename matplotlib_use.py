from matplotlib import pyplot as plt
from matplotlib import colors as mcolors
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签

# 画饼状图
sizes = [4, 11, 20, 8, 6, 4]
labels = [u'age<20:' + str(sizes[0]) + "人", u'20-29:' + str(sizes[1]) + "人", u'30-39:' + str(sizes[2]) + "人", u'40-49:' + str(sizes[3]) + "人", u'50-59:' + str(sizes[4]) + "人", u'age>60:' + str(sizes[5]) + "人"]
colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
colors = [list(colors.values())[i * 8] for i in range(len(labels))]

plt.figure(figsize=(8, 6))
plt.pie(sizes, labels=labels,colors=colors, autopct = '%3.1f%%', shadow = True, startangle = 90)
plt.title("总人数:" + str(sum(sizes)) + "人")
plt.axis('equal')
plt.show()

# 画折线图
X_ticks = ['10月1日', '10月2日', '10月3日', '10月4日', '10月5日', '10月6日', '10月7日']
X = list(range(1, 8))
Y = [60, 85, 95, 90, 80, 85, 75]

plt.figure()
plt.title("身体状况变化曲线图")
plt.plot(X, Y, '#9932CC')
plt.xlabel("时间")
plt.ylabel("健康指数")
plt.xticks(X, X_ticks)
plt.show()

# 画柱状图
x = [4, 11, 11, 17, 8]
plt.barh(range(len(x)), x, height=0.2, color=list(colors.values())[:len(x)], hatch='|')
plt.show()