import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_country_data

# 页面设置
st.set_page_config(
    page_title="YouTube视频数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    # 标题和介绍
    st.title("🎬 YouTube热门视频数据分析平台")
    st.markdown("""
    本应用对YouTube热门视频数据进行深度分析，探索视频表现与各种因素之间的关系。
    """)
    st.markdown("---")

    # 加载数据
    with st.spinner('正在加载数据，请稍候...'):
        df = load_country_data('US', 5000)

    if df is None:
        st.error("无法加载数据，请检查网络连接或数据文件")
        return

    st.success(f"✅ 成功加载 {len(df)} 条视频记录")

    # 侧边栏控件
    st.sidebar.title("🔧 控制面板")

    # 分析选择器
    analysis_type = st.sidebar.radio(
        "选择分析类型:",
        ["📈 类别分析", "⏰ 时间分析", "🔥 热门视频分析", "📊 综合洞察"]
    )

    # 通用过滤器
    st.sidebar.subheader("数据过滤器")

    # 类别选择
    available_categories = df['category_name'].unique()
    selected_categories = st.sidebar.multiselect(
        "选择视频类别:",
        options=available_categories,
        default=available_categories[:3]
    )

    # 视图范围滑块
    min_views = int(df['views'].min())
    max_views = int(df['views'].max())
    view_range = st.sidebar.slider(
        "选择视图范围:",
        min_value=min_views,
        max_value=max_views,
        value=(min_views, max_views)
    )

    # 数据过滤
    filtered_df = df[
        (df['category_name'].isin(selected_categories)) &
        (df['views'] >= view_range[0]) &
        (df['views'] <= view_range[1])
        ]

    # 根据选择的分析类型显示不同内容
    if analysis_type == "📈 类别分析":
        show_category_analysis(filtered_df)
    elif analysis_type == "⏰ 时间分析":
        show_time_analysis(filtered_df)
    elif analysis_type == "🔥 热门视频分析":
        show_popular_videos_analysis(filtered_df)
    else:
        show_comprehensive_insights(filtered_df)


def show_category_analysis(df):
    """分析任务1: 视频类别分析"""
    st.header("📊 分析任务1: 视频类别表现分析")

    col1, col2 = st.columns(2)

    with col1:
        # 图表1: 各类别平均观看量
        category_views = df.groupby('category_name')['views'].mean().sort_values(ascending=False)
        fig1 = px.bar(
            x=category_views.values,
            y=category_views.index,
            orientation='h',
            title="各类别平均观看量",
            labels={'x': '平均观看量', 'y': '视频类别'},
            color=category_views.values
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # 图表2: 互动率箱线图
        fig2 = px.box(
            df,
            x='category_name',
            y='engagement_rate',
            title="各类别互动率分布",
            labels={'engagement_rate': '互动率 (%)', 'category_name': '视频类别'}
        )
        st.plotly_chart(fig2, use_container_width=True)

    # 洞察总结
    st.subheader("🔍 关键洞察")
    top_category = df.groupby('category_name')['engagement_rate'].mean().idxmax()
    st.write(f"- **最高互动率类别**: {top_category}")
    st.write(f"- **数据范围**: {len(df)} 个视频，{len(df['category_name'].unique())} 个类别")


def show_time_analysis(df):
    """分析任务2: 发布时间分析"""
    st.header("⏰ 分析任务2: 发布时间策略分析")

    col1, col2 = st.columns(2)

    with col1:
        # 图表3: 发布时间热力图
        pivot_data = df.pivot_table(
            values='views',
            index='publish_day',
            columns='publish_hour',
            aggfunc='mean'
        )

        # 确保星期顺序正确
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        pivot_data = pivot_data.reindex(days_order)

        fig3 = px.imshow(
            pivot_data,
            title="发布时间与平均观看量热力图",
            labels=dict(x="发布时间 (小时)", y="星期", color="平均观看量"),
            aspect="auto",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        # 图表4: 标题长度与观看量关系
        fig4 = px.scatter(
            df,
            x='title_length',
            y='views',
            color='category_name',
            size='likes',
            title="标题长度与观看量关系",
            labels={'title_length': '标题长度 (字符数)', 'views': '观看量'},
            hover_data=['title']
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("📋 发布时间建议")
    best_hour = df.groupby('publish_hour')['views'].mean().idxmax()
    best_day = df.groupby('publish_day')['views'].mean().idxmax()
    st.write(f"- **最佳发布时间**: {best_day} 的 {best_hour}:00")
    st.write(f"- **标题长度建议**: {int(df['title_length'].mean())} 字符左右")


def show_popular_videos_analysis(df):
    """热门视频深度分析"""
    st.header("🔥 热门视频特征分析")

    # 顶级视频展示
    top_videos = df.nlargest(10, 'views')[['title', 'views', 'likes', 'category_name', 'engagement_rate']]

    st.subheader("🏆 观看量Top 10视频")
    st.dataframe(top_videos.style.format({
        'views': '{:,.0f}',
        'likes': '{:,.0f}',
        'engagement_rate': '{:.2f}%'
    }))

    col1, col2 = st.columns(2)

    with col1:
        # 标签数量分析
        fig5 = px.scatter(
            df,
            x='tags_count',
            y='engagement_rate',
            color='category_name',
            title="标签数量与互动率关系",
            labels={'tags_count': '标签数量', 'engagement_rate': '互动率 (%)'}
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col2:
        # 点赞率分布
        fig6 = px.histogram(
            df,
            x='like_ratio',
            nbins=50,
            title="视频点赞率分布",
            labels={'like_ratio': '点赞率 (%)'}
        )
        st.plotly_chart(fig6, use_container_width=True)


def show_comprehensive_insights(df):
    """综合洞察分析"""
    st.header("📈 综合数据洞察")

    # 相关性分析
    st.subheader("特征相关性分析")
    numeric_cols = ['views', 'likes', 'dislikes', 'comment_count', 'engagement_rate', 'tags_count', 'title_length']
    correlation_matrix = df[numeric_cols].corr()

    fig7 = px.imshow(
        correlation_matrix,
        title="数值特征相关性热力图",
        color_continuous_scale='RdBu_r',
        aspect="auto",
        text_auto=True
    )
    st.plotly_chart(fig7, use_container_width=True)

    # 关键指标
    st.subheader("📊 关键性能指标")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("平均观看量", f"{df['views'].mean():,.0f}")
    with col2:
        st.metric("平均互动率", f"{df['engagement_rate'].mean():.2f}%")
    with col3:
        st.metric("平均点赞率", f"{df['like_ratio'].mean():.2f}%")
    with col4:
        st.metric("视频类别数", len(df['category_name'].unique()))

    # 数据导出
    if st.button("📥 导出分析数据"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="下载CSV文件",
            data=csv,
            file_name="youtube_analysis_data.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()