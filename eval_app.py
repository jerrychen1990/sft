import pandas as pd
import streamlit as st
import random

st.set_page_config(layout="wide")
st.title("evaluate LLM")


def parse_text(text):
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1]
    text = text.replace("\\n", "  \n")
    return text


def get_data(data_path):
    if data_path.endswith("csv"):
        df = pd.read_csv(data_path)
    else:
        df = pd.read_excel(data_path)
    return df


col1, col2, col3 = st.columns([8, 1, 1])
with col1:
    eval_data_path = st.text_input("待测评数据路径", value="eval_data/eval_result.xlsx")
with col2:
    reload = st.button("重新加载数据")
with col3:
    export = st.button("导出数据")


def init():
    df = get_data(eval_data_path)
    df.fillna(value="", inplace=True)
    records = df.to_records(index=False)
    records = [dict(zip(df.columns, item)) for item in records]
    st.session_state.data_path = eval_data_path
    st.session_state.records = records
    st.session_state.cur_idx = 0
    st.session_state.llms = df.columns[1:3]
    st.session_state.scoreboard = dict()
    st.info("数据加载完成")





def get_next_record():
    records = st.session_state.records
    # st.info(len(records))

    cur_idx = st.session_state.cur_idx
    if cur_idx >= len(records):
        st.error("已经到达最后一条数据")
        return None
    while records[cur_idx].get("Label", None):
        # st.info(records[cur_idx])
        cur_idx += 1
    st.session_state.cur_idx = cur_idx
    return records[cur_idx]


if export:
    export_path = st.session_state.data_path
    # export_path = export_path.split(".")[0] + ".csv"
    export_df = pd.DataFrame.from_records(st.session_state.records)
    if export_path.endswith("xlsx"):
        export_df.to_excel(export_path, index=False)
    else:
        export_df.to_csv(export_path, index=False)
    st.info(f"数据已导出到{export_path}")

if reload:
    init()
if st.session_state.get("records", None) is None:
    st.info("请先加载数据")
else:
    # 展示当前信息
    with st.form("form"):
        record = get_next_record()
        cur_idx = st.session_state.cur_idx
        extra_info = dict()
        st.info(f"当前记录idx：{st.session_state.cur_idx}, 当前比分：{st.session_state.scoreboard}")

        # 展示问题
        prompt = record["Prompt"]
        st.markdown("### 问题")
        texts = parse_text(prompt)
        st.markdown(texts)
        # prompt_types = ["Unset", "Generation", "OpenQA", "Brainstorming", "Chat", "Rewrite", "Summarization",
        #                 "Classification", "ClosedQA", "Extract", "Other"]
        #
        # prompt_type = record.get("PromptType", "Unset")
        # st.info(prompt_type)
        #
        # idx = prompt_types.index(prompt_type) if prompt_type in prompt_types else 0
        # prompt_type = st.radio("问题类别", prompt_types, index=idx, horizontal=True, key=f"radio_{cur_idx}")
        # extra_info["PromptType"] = prompt_type

        # 展示回答

        llms = st.session_state.llms
        answers = [record[e] for e in llms]

        for col, llm, answer in zip(st.columns(2), llms, answers):
            col.markdown(f"### 回答")
            texts = parse_text(answer)
            col.markdown(texts)
            st.multiselect
            # answer_errors = ["一致性", "正确性", "流畅性", "无害性", "有帮助性"]
            # ErrorType = record.get("ErrorType", None)
            # ErrorType = col.multiselect("错误类型", answer_errors, key=f"{llm}_error_{cur_idx}", default=ErrorType)
            # extra_info[f"{llm}Error"] = ErrorType

        # 展示button
        labels = ["left", "draw", "right"]
        values = [llms[0], "draw", llms[1]]
        chooses = []
        res = st.selectbox(label="ck", options=["1", "2", "3"])
        submit = st.form_submit_button("提交")
        if submit:
            extra_info["Label"] = res
            st.session_state.scoreboard[res] = st.session_state.scoreboard.get(res, 0) + 1
            record.update(**extra_info)
            st.session_state.records[cur_idx] += 1
