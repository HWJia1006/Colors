import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import re


# 数据加载和处理函数
@st.cache_data
def load_colors(file_path="colors.txt"):
    """加载并处理颜色数据"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        colors = [sorted(line.strip().split(",")) for line in lines if line.strip()]
        # 去重
        unique_colors = []
        for c in colors:
            if c not in unique_colors:
                unique_colors.append(c)
        # 按颜色数量排序
        unique_colors.sort(key=len)
        return unique_colors
    except FileNotFoundError:
        # 如果文件不存在，返回示例数据
        return [
            ["#4DBBD5", "#00A087"],
            ["#4DBBD5", "#00A087", "#E64B35"],
            ["#F39B7F", "#8491B4", "#91D1C2", "#DC0000"],
            ["#3C5488", "#00A087", "#F39B7F", "#8491B4", "#91D1C2"],
            ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4"],
        ]


def is_valid_hex_color(color_str):
    """验证HEX颜色代码"""
    colors = re.split(r"[,，;、\s]+", color_str.strip())
    colors = [c.strip() for c in colors if c.strip()]
    valid_colors = []
    for c in colors:
        if re.match(r"^#[A-Fa-f0-9]{6}$", c):
            valid_colors.append(c)
    # 去重
    valid_colors = list(dict.fromkeys(valid_colors))
    return valid_colors if valid_colors and len(valid_colors) <= 16 else None


def create_example_plots(colors, alpha=1.0):
    """创建示例图表"""
    n_colors = len(colors)
    np.random.seed(42)

    # 关闭之前的所有图表
    plt.close("all")

    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.35)

    # 图1: 条形图
    ax1 = fig.add_subplot(gs[0, 0])
    categories = [chr(97 + i) for i in range(min(n_colors, 26))]
    values = np.random.uniform(7, 10, n_colors)
    bars = ax1.bar(categories, values, color=colors, edgecolor="black", alpha=alpha)
    ax1.set_xlabel("x-axis")
    ax1.set_ylabel("y-axis")
    ax1.set_title("Bar Chart with outlines")
    ax1.set_ylim(0, max(values) * 1.1)

    # 图2: 箱线图
    ax2 = fig.add_subplot(gs[0, 1])
    box_data = [np.random.uniform(7, 10, 20) for _ in range(n_colors)]
    bp = ax2.boxplot(box_data, labels=categories, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(alpha)
    ax2.set_xlabel("x-axis")
    ax2.set_ylabel("y-axis")
    ax2.set_title("Boxplot with outlines")

    # 图3: 散点图
    ax3 = fig.add_subplot(gs[1, 0])
    for i, color in enumerate(colors):
        x = np.random.uniform(0, 1, 30)
        y = np.random.uniform(0, 1, 30)
        ax3.scatter(
            x,
            y,
            c=color,
            s=100,
            alpha=alpha,
            edgecolors=color,
            linewidth=1.5,
            label=categories[i],
        )
    ax3.set_xlabel("x-axis")
    ax3.set_ylabel("y-axis")
    ax3.set_title("Scatterplot without outlines")
    if n_colors <= 8:
        ax3.legend(loc="best", fontsize=8, ncol=2)

    # 图4: 折线图
    ax4 = fig.add_subplot(gs[1, 1])
    x = np.arange(1, 21)
    for i, color in enumerate(colors):
        y = (i + 1) + np.random.normal(0, 0.3, 20)
        ax4.plot(x, y, color=color, linewidth=2, alpha=alpha, label=categories[i])
    ax4.set_xlabel("x-axis")
    ax4.set_ylabel("y-axis")
    ax4.set_title("Line chart without outlines")
    if n_colors <= 8:
        ax4.legend(loc="best", fontsize=8, ncol=2)

    return fig


def create_color_palette_display(colors):
    """创建颜色方案显示"""
    plt.close("all")
    fig, ax = plt.subplots(figsize=(10, 8))
    n = len(colors)
    for i, color in enumerate(colors):
        ax.add_patch(
            mpatches.Rectangle((0, n - i - 1), 1, 1, facecolor=color, edgecolor="black")
        )
        ax.text(1.1, n - i - 0.5, color, va="center", fontsize=12, family="monospace")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, n)
    ax.axis("off")
    return fig


# 页面配置
st.set_page_config(page_title="科研绘图配色推荐器", page_icon="🎨", layout="wide")


def handle_button_click(selected_id, show_type, selected_num, display_start_id):
    """
    Callback function to update session state when a "Select" button is clicked.
    This runs *before* the page rerenders, avoiding the APIException.
    """
    if show_type == "配色数据库方案id":
        if selected_num == "全部":
            relative_id = selected_id
        else:
            relative_id = selected_id - display_start_id
    else:
        # If in "custom" mode, switch to "all"
        st.session_state.selected_num = "全部"
        relative_id = selected_id

    # This is safe because it runs *before* the slider is instantiated
    st.session_state.slider_value = relative_id


# 自定义CSS
st.markdown(
    """
    <style>
    .main {padding-top: 2rem;}
    .stButton>button {width: 100%;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# 初始化session state
if "slider_value" not in st.session_state:
    st.session_state.slider_value = 0
if "selected_num" not in st.session_state:
    st.session_state.selected_num = "全部"
if "db_page" not in st.session_state:  # 为数据库表格添加分页
    st.session_state.db_page = 0


@st.cache_data
def load_colors(file_path="colors.txt"):
    """加载并处理颜色数据"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        colors = [sorted(line.strip().split(",")) for line in lines if line.strip()]
        # 去重
        unique_colors = []
        for c in colors:
            if c not in unique_colors:
                unique_colors.append(c)
        # 按颜色数量排序
        unique_colors.sort(key=len)
        return unique_colors
    except FileNotFoundError:
        # 如果文件不存在，返回示例数据
        return [
            ["#4DBBD5", "#00A087"],
            ["#4DBBD5", "#00A087", "#E64B35"],
            ["#F39B7F", "#8491B4", "#91D1C2", "#DC0000"],
            ["#3C5488", "#00A087", "#F39B7F", "#8491B4", "#91D1C2"],
            ["#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F", "#8491B4"],
        ]


def is_valid_hex_color(color_str):
    """验证HEX颜色代码"""
    colors = re.split(r"[,，;、\s]+", color_str.strip())
    colors = [c.strip() for c in colors if c.strip()]
    valid_colors = []
    for c in colors:
        if re.match(r"^#[A-Fa-f0-9]{6}$", c):
            valid_colors.append(c)
    # 去重
    valid_colors = list(dict.fromkeys(valid_colors))
    return valid_colors if valid_colors and len(valid_colors) <= 16 else None


def create_example_plots(colors, alpha=1.0):
    """创建示例图表"""
    n_colors = len(colors)
    np.random.seed(42)

    # 关闭之前的所有图表
    plt.close("all")

    fig = plt.figure(figsize=(10, 8))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.35)

    # 图1: 条形图
    ax1 = fig.add_subplot(gs[0, 0])
    categories = [chr(97 + i) for i in range(min(n_colors, 26))]
    values = np.random.uniform(7, 10, n_colors)
    bars = ax1.bar(categories, values, color=colors, edgecolor="black", alpha=alpha)
    ax1.set_xlabel("x-axis")
    ax1.set_ylabel("y-axis")
    ax1.set_title("Bar Chart with outlines")
    ax1.set_ylim(0, max(values) * 1.1)

    # 图2: 箱线图
    ax2 = fig.add_subplot(gs[0, 1])
    box_data = [np.random.uniform(7, 10, 20) for _ in range(n_colors)]
    bp = ax2.boxplot(box_data, labels=categories, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(alpha)
    ax2.set_xlabel("x-axis")
    ax2.set_ylabel("y-axis")
    ax2.set_title("Boxplot with outlines")

    # 图3: 散点图
    ax3 = fig.add_subplot(gs[1, 0])
    for i, color in enumerate(colors):
        x = np.random.uniform(0, 1, 30)
        y = np.random.uniform(0, 1, 30)
        ax3.scatter(
            x,
            y,
            c=color,
            s=100,
            alpha=alpha,
            edgecolors=color,
            linewidth=1.5,
            label=categories[i],
        )
    ax3.set_xlabel("x-axis")
    ax3.set_ylabel("y-axis")
    ax3.set_title("Scatterplot without outlines")
    if n_colors <= 8:
        ax3.legend(loc="best", fontsize=8, ncol=2)

    # 图4: 折线图
    ax4 = fig.add_subplot(gs[1, 1])
    x = np.arange(1, 21)
    for i, color in enumerate(colors):
        y = (i + 1) + np.random.normal(0, 0.3, 20)
        ax4.plot(x, y, color=color, linewidth=2, alpha=alpha, label=categories[i])
    ax4.set_xlabel("x-axis")
    ax4.set_ylabel("y-axis")
    ax4.set_title("Line chart without outlines")
    if n_colors <= 8:
        ax4.legend(loc="best", fontsize=8, ncol=2)

    return fig


def create_color_palette_display(colors):
    """创建颜色方案显示"""
    plt.close("all")
    fig, ax = plt.subplots(figsize=(10, 8))
    n = len(colors)
    for i, color in enumerate(colors):
        ax.add_patch(
            mpatches.Rectangle((0, n - i - 1), 1, 1, facecolor=color, edgecolor="black")
        )
        ax.text(1.1, n - i - 0.5, color, va="center", fontsize=12, family="monospace")
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0, n)
    ax.axis("off")
    return fig


# 主程序
def main():
    st.title("🎨 科研绘图配色推荐器")

    # 加载颜色数据
    colors_data = load_colors()

    # 创建颜色统计信息
    color_counts = {}

    for i, colors in enumerate(colors_data):
        n = len(colors)
        if n not in color_counts:
            color_counts[n] = []
        color_counts[n].append(colors)

    st.markdown(f"**数据库内现有 {len(colors_data)} 种配色方案**")
    st.markdown("---")

    # 方案选择
    st.subheader("方案选择")
    show_type = st.radio(
        "选择方式", ["配色数据库方案id", "自定义配色方案"], horizontal=True
    )

    if show_type == "配色数据库方案id":
        # 颜色数量选择 - 按数值大小排序
        sorted_nums = sorted(color_counts.keys())
        num_options = ["全部"] + [str(n) for n in sorted_nums]

        selected_num = st.selectbox(
            "选择颜色数量",
            num_options,
            index=(
                num_options.index(st.session_state.selected_num)
                if st.session_state.selected_num in num_options
                else 0
            ),
        )

        # 当数量选择改变时，重置滑块值和分页
        if selected_num != st.session_state.selected_num:
            st.session_state.selected_num = selected_num
            st.session_state.slider_value = 0
            st.session_state.db_page = 0  # 重置分页

        # 根据选择的数量筛选
        if selected_num == "全部":
            available_colors = colors_data
            start_idx = 0
        else:
            num = int(selected_num)
            available_colors = color_counts[num]
            start_idx = sum(
                len(color_counts[k]) for k in sorted(color_counts.keys()) if k < num
            )

        max_idx = len(available_colors) - 1

        # 确保slider_value在有效范围内
        if st.session_state.slider_value > max_idx:
            st.session_state.slider_value = 0

        col1, col2 = st.columns([3, 1])

        with col2:
            st.write("")
            st.write("")
            st.write("")
            # 上一个按钮
            if st.button("⬅️ 上一个", key="prev_btn", use_container_width=True):
                if st.session_state.slider_value > 0:
                    st.session_state.slider_value -= 1

            # 下一个按钮
            if st.button("下一个 ➡️", key="next_btn", use_container_width=True):
                if st.session_state.slider_value < max_idx:
                    st.session_state.slider_value += 1

        with col1:
            # ID选择器 (已修复，可与按钮同步)
            st.slider(
                "选择方案id",
                min_value=0,
                max_value=max_idx,
                key="slider_value",  # 绑定到 session_state.slider_value
            )

        selected_colors = available_colors[st.session_state.slider_value]
        actual_id = start_idx + st.session_state.slider_value

    else:  # 自定义配色
        col1, col2 = st.columns([4, 1])

        with col1:
            custom_input = st.text_input(
                "自定义颜色（HEX码，多个颜色以逗号、空格等间隔，最多16个颜色）",
                value="#4DBBD5, #00A087, #E64B35",
            )

        with col2:
            st.write("")
            st.write("")
            if st.button("🔄 重置"):
                st.rerun()

        selected_colors = is_valid_hex_color(custom_input)
        if selected_colors is None:
            st.error("❌ 输入的颜色格式不正确或数量超过16个")
            selected_colors = ["#FFFFFF"]
            actual_id = "ERROR"
        else:
            actual_id = 0

    # 显示所选配色方案
    st.markdown("---")
    st.subheader("所选配色方案")

    col1, col2, col3 = st.columns([1, 2, 4])
    with col1:
        st.metric("方案ID", actual_id)
    with col2:
        st.metric("颜色数量", len(selected_colors))
    with col3:
        # 显示颜色预览
        color_html = "".join(
            [
                f'<div style="width:30px;height:30px;background-color:{c};display:inline-block;margin:2px;border:1px solid black;"></div>'
                for c in selected_colors
            ]
        )
        st.markdown(f"<div>{color_html}</div>", unsafe_allow_html=True)

    st.code(", ".join(selected_colors), language=None)

    # 颜色透明度控制
    alpha = st.slider("颜色透明度（alpha值）", 0.0, 1.0, 1.0, 0.05)

    st.markdown("---")

    # 显示图表
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("绘图效果")
        if actual_id != "ERROR":
            with st.spinner("生成绘图效果..."):
                fig1 = create_example_plots(selected_colors, alpha)
                st.pyplot(fig1, clear_figure=True)
                plt.close(fig1)
        else:
            st.error("请输入正确的颜色格式")

    with col2:
        st.subheader("方案样式")
        if actual_id != "ERROR":
            with st.spinner("生成方案样式..."):
                fig2 = create_color_palette_display(selected_colors)
                st.pyplot(fig2, clear_figure=True)
                plt.close(fig2)
        else:
            st.error("请输入正确的颜色格式")

    # --- (配色数据库部分) ---
    st.markdown("---")
    st.subheader("配色数据库")

    # 根据选择的数量筛选显示的数据
    if show_type == "配色数据库方案id":
        if selected_num == "全部":
            display_colors = colors_data
            display_start_id = 0
        else:
            num = int(selected_num)
            display_colors = color_counts[num]
            display_start_id = sum(
                len(color_counts[k]) for k in sorted(color_counts.keys()) if k < num
            )
    else:
        display_colors = colors_data
        display_start_id = 0

    # 创建数据框 (我们仍然需要df来组织数据)
    df_data = []
    for i, colors in enumerate(display_colors):
        df_data.append(
            {
                "方案id": display_start_id + i,
                "所含颜色数": len(colors),
                "颜色HEX码": ", ".join(colors),
            }
        )
    df = pd.DataFrame(df_data)

    # --- 分页设置 ---
    PAGE_SIZE = 10  # 每页显示10条
    total_rows = len(df)
    total_pages = int(np.ceil(total_rows / PAGE_SIZE))

    if total_pages > 0:
        # 确保页码不溢出
        if st.session_state.db_page >= total_pages:
            st.session_state.db_page = total_pages - 1

        # 分页控件
        page_col1, page_col2, page_col3, page_col4 = st.columns([3, 1, 1, 3])
        with page_col1:
            st.markdown(f"总计 {total_rows} 条数据")
        with page_col2:
            if st.button("⬅️ 上一页", key="prev_page"):
                if st.session_state.db_page > 0:
                    st.session_state.db_page -= 1
        with page_col3:
            if st.button("下一页 ➡️", key="next_page"):
                if st.session_state.db_page < total_pages - 1:
                    st.session_state.db_page += 1
        with page_col4:
            st.markdown(
                f"<div style='text-align: right; padding-top: 5px;'>页码: {st.session_state.db_page + 1} / {total_pages}</div>",
                unsafe_allow_html=True,
            )

        # 计算当前页的数据
        start_idx_page = st.session_state.db_page * PAGE_SIZE
        end_idx_page = min(start_idx_page + PAGE_SIZE, total_rows)
        df_page = df.iloc[start_idx_page:end_idx_page]

        # 渲染表头
        header_cols = st.columns([1, 1, 4, 3, 1])
        with header_cols[0]:
            st.markdown("**方案id**")
        with header_cols[1]:
            st.markdown("**所含颜色数**")
        with header_cols[2]:
            st.markdown("**颜色HEX码**")
        with header_cols[3]:
            st.markdown("**颜色预览**")
        with header_cols[4]:
            st.markdown("**操作**")
        st.markdown("---")

        # 渲染当前页的列表
        for idx, row in df_page.iterrows():
            cols = st.columns([1, 1, 4, 3, 1])
            with cols[0]:
                st.write(f"**{row['方案id']}**")
            with cols[1]:
                st.write(f"{row['所含颜色数']}色")
            with cols[2]:
                st.write(row["颜色HEX码"])
            with cols[3]:
                colors_list = row["颜色HEX码"].split(", ")
                color_blocks = "".join(
                    [
                        f'<div style="width:25px;height:25px;background-color:{c};display:inline-block;margin-right:3px;border:1px solid #666;"></div>'
                        for c in colors_list
                    ]
                )
                st.markdown(color_blocks, unsafe_allow_html=True)
            with cols[4]:
                # 【核心修改】
                # 替换 if st.button(...) with st.button(on_click=...)
                selected_id = row["方案id"]
                st.button(
                    "选择",
                    key=f"select_{selected_id}",
                    on_click=handle_button_click,  # 使用回调
                    args=(
                        selected_id,
                        show_type,
                        selected_num,
                        display_start_id,
                    ),  # 传递参数给回调
                )

    else:
        st.write("当前筛选条件下无数据。")

    # 页脚
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
        <p>© 2021-2024, Lcpmgh, All rights reserved.</p>
        <p>
        <a href='https://github.com/HWJia1006' target='_blank'>GitHub</a> | 
        <a href='mailto:hongwangj@gmail.com'>Email</a> | 
        <a href='https://github.com/HWJia1006' target='_blank'>Website</a>
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
