import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# 页面设置
st.set_page_config(
    page_title="YouTube视频数据分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data(sample_size=5000):
    """加载数据的主函数"""
    try:
        # 尝试从Kaggle下载数据
        try:
            import kagglehub
            st.info("📥 正在从Kaggle下载数据集...")
            path = kagglehub.dataset_download("datasnaek/youtube-new")
            df = pd.read_csv(os.path.join(path, 'USvideos.csv'))
            st.success("✅ 数据集下载完成！")
        except:
            # 如果下载失败，尝试本地文件
            try:
                df = pd.read_csv('data/USvideos.csv')
                st.info("使用本地数据文件")
            except:
                # 如果都没有，创建示例数据
                st.warning("使用示例数据进行演示")
                df = create_sample_data()
        
        # 数据预处理
        df = preprocess_data(df, sample_size)
        return df
        
    except Exception as e:
        st.error(f"数据加载错误: {e}")
        return create_sample_data()

def preprocess_data(df, sample_size=5000):
    """数据预处理"""
    # 数据抽样
    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)
    
    # 日期处理
    if 'trending_date' in df.columns:
        df['trending_date'] = pd.to_datetime(df['trending_date'], format='%y.%d.%m', errors='coerce')
    
    if 'publish_time' in df.columns:
        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
    
    # 类别映射
    category_mapping = {
        1: 'Film & Animation', 2: 'Autos & Vehicles', 10: 'Music',
        15: 'Pets & Animals', 17: 'Sports', 19: 'Travel & Events',
        20: 'Gaming', 22: 'People & Blogs', 23: 'Comedy',
        24: 'Entertainment', 25: 'News & Politics', 26: 'Howto & Style',
        27: 'Education', 28: 'Science & Technology', 29: 'Nonprofits & Activism'
    }
    
    if 'category_id' in df.columns:
        df['category_name'] = df['category_id'].map(category_mapping)
        df['category_name'] = df['category_name'].fillna('Unknown')
    
    # 计算衍生特征
    numeric_cols = ['views', 'likes', 'dislikes', 'comment_count']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    if all(col in df.columns for col in ['views', 'likes', 'comment_count']):
        df['engagement_rate'] = (df['likes'] + df['comment_count']) / (df['views'] + 1) * 100
    
    if all(col in df.columns for col in ['likes', 'dislikes']):
        df['like_ratio'] = df['likes'] / (df['likes'] + df['dislikes'] + 1) * 100
    
    if 'tags' in df.columns:
        df['tags_count'] = df['tags'].apply(lambda x: len(str(x).split('|')))
    
    if 'publish_time' in df.columns:
        df['publish_hour'] = df['publish_time'].dt.hour
        df['publish_day'] = df['publish_time'].dt.day_name()
    
    if 'title' in df.columns:
        df['title_length'] = df['title'].str.len()
    
    return df

def create_sample_data():
    """创建示例数据"""
    np.random.seed(42)
    n_samples = 1000
    
    categories = ['Music', 'Entertainment', 'Gaming', 'Sports', 'Education', 'News & Politics']
    
    data = {
        'video_id': [f'video_{i}' for i in range(n_samples)],
        'title': [f'Sample Video Title {i}' for i in range(n_samples)],
        'channel_title': [f'Channel {i}' for i in range(n_samples)],
        'category_id': np.random.choice([10, 24, 20, 17, 27, 25], n_samples),
        'category_name': np.random.choice(categories, n_samples),
        'views': np.random.randint(1000, 1000000, n_samples),
        'likes': np.random.randint(100, 100000, n_samples),
        'dislikes': np.random.randint(0, 5000, n_samples),
        'comment_count': np.random.randint(0, 10000, n_samples),
        'tags': ['music|entertainment|vlog'] * n_samples,
        'publish_time': [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(n_samples)],
    }
    
    df = pd.DataFrame(data)
    
    # 计算衍生特征
    df['engagement_rate'] = (df['likes'] + df['comment_count']) / (df['views'] + 1) * 100
    df['like_ratio'] = df['likes'] / (df['likes'] + df['dislikes'] + 1) * 100
    df['tags_count'] = df['tags'].apply(lambda x: len(str(x).split('|')))
    df['publish_hour'] = np.random.randint(0, 24, n_samples)
    df['publish_day'] = np.random.choice(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], n_samples)
    df['title_length'] = np.random.randint(10, 100, n_samples)
    
    return df

def create_bar_chart(data, x_col, y_col, title, x_label, y_label):
    """创建条形图"""
    chart_data = data.groupby(x_col)[y_col].mean().sort_values(ascending=False)
    st.bar_chart(chart_data)
    st.caption(title)

def create_line_chart(data, x_col, y_col, title):
    """创建折线图"""
    chart_data = data.groupby(x_col)[y_col].mean()
    st.line_chart(chart_data)
    st.caption(title)

def create_histogram(data, column, title, bins=20):
    """创建直方图"""
    st.subheader(title)
    hist_values = np.histogram(data[column].dropna(), bins=bins)[0]
    st.bar_chart(hist_values)

def main():
    st.title("🎬 YouTube热门视频数据分析平台")
    st.markdown("分析YouTube热门视频的表现与各种因素之间的关系")
    st.markdown("---")
    
    # 加载数据
    with st.spinner('正在加载数据，请稍候...'):
        df = load_data(3000)
    
    st.success(f"✅ 成功加载 {len(df)} 条视频记录")
    
    # 侧边栏控件
    st.sidebar.title("🔧 控制面板")
    
    # 分析选择
    analysis_type = st.sidebar.radio(
        "选择分析类型:",
        ["📈 类别分析", "⏰ 时间分析", "🔥 热门视频分析", "📊 综合洞察"]
    )
    
    # 数据过滤器
    st.sidebar.subheader("数据过滤器")
    
    if 'category_name' in df.columns:
        available_categories = df['category_name'].unique()
        selected_categories = st.sidebar.multiselect(
            "选择视频类别:",
            options=available_categories,
            default=available_categories[:3] if len(available_categories) > 3 else available_categories
        )
    else:
        selected_categories = []
    
    # 视图范围滑块
    if 'views' in df.columns:
        min_views = int(df['views'].min())
        max_views = int(df['views'].max())
        view_range = st.sidebar.slider(
            "选择视图范围:",
            min_value=min_views,
            max_value=max_views,
            value=(min_views, max_views // 2)
        )
    else:
        view_range = (0, 1000000)
    
    # 数据过滤
    filtered_df = df.copy()
    if selected_categories and 'category_name' in df.columns:
        filtered_df = filtered_df[filtered_df['category_name'].isin(selected_categories)]
    
    if 'views' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['views'] >= view_range[0]) & 
            (filtered_df['views'] <= view_range[1])
        ]
    
    # 根据分析类型显示内容
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
    
    if 'category_name' not in df.columns or 'views' not in df.columns:
        st.warning("缺少必要的列进行类别分析")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("各类别平均观看量")
        category_views = df.groupby('category_name')['views'].mean().sort_values(ascending=False)
        st.bar_chart(category_views)
        
        # 显示具体数值
        st.write("**各类别平均观看量:**")
        for category, views in category_views.items():
            st.write(f"- {category}: {views:,.0f} 次观看")
    
    with col2:
        st.subheader("各类别平均互动率")
        if 'engagement_rate' in df.columns:
            engagement_by_category = df.groupby('category_name')['engagement_rate'].mean().sort_values(ascending=False)
            st.bar_chart(engagement_by_category)
            
            # 显示具体数值
            st.write("**各类别平均互动率:**")
            for category, rate in engagement_by_category.items():
                st.write(f"- {category}: {rate:.2f}%")
        else:
            st.info("无法计算互动率")
    
    # 关键洞察
    st.subheader("🔍 关键洞察")
    if 'engagement_rate' in df.columns:
        top_engagement = df.groupby('category_name')['engagement_rate'].mean().idxmax()
        top_views = df.groupby('category_name')['views'].mean().idxmax()
        st.write(f"- **最高互动率类别**: {top_engagement}")
        st.write(f"- **最高观看量类别**: {top_views}")
    st.write(f"- **数据范围**: {len(df)} 个视频，{len(df['category_name'].unique())} 个类别")

def show_time_analysis(df):
    """分析任务2: 发布时间分析"""
    st.header("⏰ 分析任务2: 发布时间策略分析")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("各小时平均观看量")
        if 'publish_hour' in df.columns and 'views' in df.columns:
            hourly_views = df.groupby('publish_hour')['views'].mean().sort_index()
            st.line_chart(hourly_views)
            
            best_hour = hourly_views.idxmax()
            st.write(f"**最佳发布小时**: {best_hour}:00 (平均观看量: {hourly_views.max():,.0f})")
        else:
            st.info("缺少时间数据")
    
    with col2:
        st.subheader("各星期平均观看量")
        if 'publish_day' in df.columns and 'views' in df.columns:
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_views = df.groupby('publish_day')['views'].mean().reindex(days_order, fill_value=0)
            st.line_chart(daily_views)
            
            best_day = daily_views.idxmax()
            st.write(f"**最佳发布日期**: {best_day} (平均观看量: {daily_views.max():,.0f})")
        else:
            st.info("缺少日期数据")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("标题长度分布")
        if 'title_length' in df.columns:
            hist_values = np.histogram(df['title_length'].dropna(), bins=20)[0]
            st.bar_chart(hist_values)
            avg_length = df['title_length'].mean()
            st.write(f"**平均标题长度**: {avg_length:.1f} 字符")
    
    with col4:
        st.subheader("标签数量分布")
        if 'tags_count' in df.columns:
            tag_counts = df['tags_count'].value_counts().sort_index()
            st.bar_chart(tag_counts)
            avg_tags = df['tags_count'].mean()
            st.write(f"**平均标签数量**: {avg_tags:.1f} 个")
    
    # 发布时间建议
    st.subheader("📋 发布时间建议")
    if all(col in df.columns for col in ['publish_hour', 'publish_day', 'views']):
        best_hour = df.groupby('publish_hour')['views'].mean().idxmax()
        best_day = df.groupby('publish_day')['views'].mean().idxmax()
        st.write(f"- **最佳发布时间**: {best_day} 的 {best_hour}:00")
    
    if 'title_length' in df.columns:
        st.write(f"- **标题长度建议**: {int(df['title_length'].mean())} 字符左右")
    
    if 'tags_count' in df.columns:
        st.write(f"- **标签数量建议**: {int(df['tags_count'].mean())} 个标签左右")

def show_popular_videos_analysis(df):
    """热门视频深度分析"""
    st.header("🔥 热门视频特征分析")
    
    # 顶级视频展示
    if all(col in df.columns for col in ['title', 'views', 'likes', 'category_name', 'engagement_rate']):
        top_videos = df.nlargest(10, 'views')[['title', 'views', 'likes', 'category_name', 'engagement_rate']]
        
        st.subheader("🏆 观看量Top 10视频")
        
        # 使用表格显示Top视频
        for i, (idx, row) in enumerate(top_videos.iterrows(), 1):
            with st.container():
                cols = st.columns([3, 2, 2, 2, 2])
                cols[0].write(f"**{i}. {row['title']}**")
                cols[1].write(f"👁️ {row['views']:,}")
                cols[2].write(f"👍 {row['likes']:,}")
                cols[3].write(f"📊 {row['engagement_rate']:.2f}%")
                cols[4].write(f"🎯 {row['category_name']}")
                st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("点赞率分布")
        if 'like_ratio' in df.columns:
            # 创建点赞率分布直方图
            like_ratio_bins = np.linspace(df['like_ratio'].min(), df['like_ratio'].max(), 20)
            hist_values = np.histogram(df['like_ratio'], bins=like_ratio_bins)[0]
            st.bar_chart(hist_values)
            
            avg_like_ratio = df['like_ratio'].mean()
            st.write(f"**平均点赞率**: {avg_like_ratio:.1f}%")
    
    with col2:
        st.subheader("互动率分布")
        if 'engagement_rate' in df.columns:
            engagement_bins = np.linspace(df['engagement_rate'].min(), df['engagement_rate'].max(), 20)
            hist_values = np.histogram(df['engagement_rate'], bins=engagement_bins)[0]
            st.bar_chart(hist_values)
            
            avg_engagement = df['engagement_rate'].mean()
            st.write(f"**平均互动率**: {avg_engagement:.2f}%")
    
    # 标签数量分析
    st.subheader("标签数量分析")
    if 'tags_count' in df.columns and 'engagement_rate' in df.columns:
        col3, col4 = st.columns(2)
        
        with col3:
            tag_engagement = df.groupby('tags_count')['engagement_rate'].mean()
            st.line_chart(tag_engagement)
            st.write("标签数量 vs 平均互动率")
        
        with col4:
            tag_views = df.groupby('tags_count')['views'].mean()
            st.line_chart(tag_views)
            st.write("标签数量 vs 平均观看量")

def show_comprehensive_insights(df):
    """综合洞察分析"""
    st.header("📈 综合数据洞察")
    
    # 关键指标
    st.subheader("📊 关键性能指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'views' in df.columns:
            avg_views = df['views'].mean()
            st.metric("平均观看量", f"{avg_views:,.0f}")
    
    with col2:
        if 'engagement_rate' in df.columns:
            avg_engagement = df['engagement_rate'].mean()
            st.metric("平均互动率", f"{avg_engagement:.2f}%")
    
    with col3:
        if 'like_ratio' in df.columns:
            avg_like_ratio = df['like_ratio'].mean()
            st.metric("平均点赞率", f"{avg_like_ratio:.1f}%")
    
    with col4:
        if 'category_name' in df.columns:
            category_count = len(df['category_name'].unique())
            st.metric("视频类别数", category_count)
    
    # 数据分布概览
    st.subheader("📋 数据分布概览")
    
    if 'category_name' in df.columns:
        st.write("**类别分布:**")
        category_counts = df['category_name'].value_counts()
        for category, count in category_counts.items():
            percentage = (count / len(df)) * 100
            st.write(f"- {category}: {count} 个视频 ({percentage:.1f}%)")
    
    # 数值统计
    st.subheader("🔢 数值统计摘要")
    
    numeric_cols = ['views', 'likes', 'dislikes', 'comment_count', 'engagement_rate']
    available_numeric_cols = [col for col in numeric_cols if col in df.columns]
    
    if available_numeric_cols:
        stats_df = df[available_numeric_cols].describe()
        st.dataframe(stats_df.style.format("{:,.2f}"))
    
    # 相关性分析（简化版）
    st.subheader("🔗 特征关系分析")
    
    if all(col in df.columns for col in ['views', 'likes', 'comment_count']):
        col5, col6 = st.columns(2)
        
        with col5:
            st.write("**观看量 vs 点赞数**")
            # 创建散点图的简化版本
            sample_data = df[['views', 'likes']].sample(min(100, len(df)))
            st.dataframe(sample_data.corr().style.format("{:.2f}"))
        
        with col6:
            st.write("**观看量 vs 评论数**")
            sample_data = df[['views', 'comment_count']].sample(min(100, len(df)))
            st.dataframe(sample_data.corr().style.format("{:.2f}"))
    
    # 数据导出
    st.subheader("📥 数据导出")
    
    if st.button("导出当前视图数据为CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="下载CSV文件",
            data=csv,
            file_name="youtube_analysis_data.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
