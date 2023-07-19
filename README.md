# SFT数据标注工具项目
- 安装需要的python包
```shell
pip install -r requirements.txt
```
- 把待标注的数据放入到 ./data/parsed/to_label.jsonl
- 运行数据服务
```shell
python data_service.py
```
- 运行定时脚本，定时将标好的数据导出到./data/parsed/labeled.jsonl
- 运行WebUI
```shell
streamlit run labeling_app.py
```
- 开始标注
