<div align=center>
  <img width=200 src="asset/cczusnap.png"  alt="asset/cczusnap.png"/>
  <h1 align="center">CCZU SNAP</h1>
</div>

<div align=center>
  <img src="https://img.shields.io/badge/python-3.8+-blue" alt="python">
  <img src="https://img.shields.io/github/license/H2Sxxa/cczusnap" alt="license">
</div>

## 吊州大学选课脚本 📚

军训抢课卡了半天，于是写了这个脚本解放双手与焦虑，这就是异步蟒蛇给我的自信 😤

## 声明 🔈

使用MIT开源，如使用过程中造成了损失，概不负责 😋

请勿在无关的地方提及本脚本 ❗

## 使用方法 💡

首次启动后会生成一个 `config.yaml`，打开编辑

```yaml

account: '学号'
password: '身份证后六位'
targets:
- "load(web=\"web_xsxk/xfz_xsxk_fs1_zcxk.aspx\",name_included=[\"C++\"])"
# 使用方法 load(web, name_included = [], id_included = [])
# web 字符串 必填 可以参考下方的选课网址
# name_included 列表<字符串> 可选 例如 太极，羽毛球，健美操，如果这个字段在目标的课程里，就会选择相应的课。
# id_included 列表<字符串> 可选 例如 Select$1，每个地方的课程ID都有所不同，没把握请勿使用。
url: 202.195.102.53 # 选课地址


```

## 选课网址（可以自己用浏览器F12抓） 🔧

 - web_xsxk/xfz_xsxk_fs1_zcxk.aspx 教学任务课程
 - web_xsxk/ggxx_xsxk_sql_new.aspx?dm=0003-001 通识类选课
 - web_xsxk/ty_xsxk_xh_sql_new.aspx?dm=0003-008 体育