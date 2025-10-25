import kagglehub
import pandas as pd
import os
import streamlit as st


@st.cache_resource
def download_youtube_data():
    """下载YouTube数据集"""
    try:
        st.info(" 正在从Kaggle下载YouTube数据集...")
        path = kagglehub.dataset_download("datasnaek/youtube-new")
        st.success(" 数据集下载完成！")
        return path
    except Exception as e:
        st.error(f" 下载失败: {e}")
        return None


@st.cache_data
def load_country_data(country_code='US', sample_size=5000):
    """加载特定国家的数据并进行预处理"""
    dataset_path = download_youtube_data()

    if dataset_path is None:
        st.warning("使用备用数据加载方式...")
        return None

    try:
        # 读取视频数据和类别数据
        videos_path = os.path.join(dataset_path, f'{country_code}videos.csv')
        category_path = os.path.join(dataset_path, f'{country_code}_category_id.json')

        # 读取数据
        df = pd.read_csv(videos_path)
        category_df = pd.read_json(category_path)

        # 数据预处理
        df = preprocess_data(df, category_df, sample_size)

        return df

    except Exception as e:
        st.error(f"数据加载错误: {e}")
        return None


def preprocess_data(df, category_df, sample_size=5000):
    """数据预处理函数"""
    # 数据抽样
    if len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)

    # 日期处理
    df['trending_date'] = pd.to_datetime(df['trending_date'], format='%y.%d.%m')
    df['publish_time'] = pd.to_datetime(df['publish_time'])

    # 创建类别名称映射
    category_mapping = {}
    for item in category_df['items']:
        category_mapping[int(item['id'])] = item['snippet']['title']

    df['category_name'] = df['category_id'].map(category_mapping)

    # 计算衍生特征
    df['engagement_rate'] = (df['likes'] + df['comments']) / df['views'] * 100
    df['like_ratio'] = df['likes'] / (df['likes'] + df['dislikes'] + 1) * 100
    df['tags_count'] = df['tags'].apply(lambda x: len(str(x).split('|')))
    df['publish_hour'] = df['publish_time'].dt.hour
    df['publish_day'] = df['publish_time'].dt.day_name()
    df['title_length'] = df['title'].str.len()

    return df