import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import time
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="動画のデジタル表現",
    page_icon="🎬",
    layout="wide"
)

st.title("動画のデジタル表現（pp.164-165）")
st.caption("Created by Dit-Lab.(Daiki ITO)")
st.caption("Supported by Tomoaki ATSUMI")

st.markdown("### 📺 動画の基本概念")
st.info("動画とは、たくさんの静止画（フレーム）をパラパラ漫画のように連続で表示しているものです。")

st.markdown("### 🎛️ パラメータを調整して動画の仕組みを理解しよう")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 解像度 (Resolution)")
    st.markdown("1枚の静止画（フレーム）のピクセル数を設定します")
    resolution = st.slider(
        "解像度を選択",
        min_value=32,
        max_value=256,
        value=128,
        step=32,
        help="解像度が高いほど画像が鮮明になりますが、データ量も増えます"
    )

with col2:
    st.markdown("#### フレームレート (fps)")
    st.markdown("1秒間に表示する静止画（フレーム）の枚数を設定します")
    fps = st.slider(
        "フレームレート (frames per second)",
        min_value=5,
        max_value=60,
        value=30,
        step=5,
        help="フレームレートが高いほど動画が滑らかになりますが、データ量も増えます"
    )

st.markdown("---")

st.markdown("### 🎮 動画シミュレーション")

def create_bouncing_ball_animation(resolution, fps):
    # フレームレートに応じたフレーム数を生成（最小10、最大60）
    frame_count = max(10, min(60, fps))
    frames = []
    
    for i in range(frame_count):
        t = i / frame_count * 2 * np.pi
        x = resolution // 2 + (resolution // 4) * np.sin(t)
        y = resolution // 2 + (resolution // 4) * np.cos(t) * 0.5
        
        frame_data = np.zeros((resolution, resolution))
        
        ball_size = max(2, resolution // 20)
        y_start = max(0, int(y - ball_size))
        y_end = min(resolution, int(y + ball_size + 1))
        x_start = max(0, int(x - ball_size))
        x_end = min(resolution, int(x + ball_size + 1))
        
        for yi in range(y_start, y_end):
            for xi in range(x_start, x_end):
                if (xi - x) ** 2 + (yi - y) ** 2 <= ball_size ** 2:
                    frame_data[yi, xi] = 1
        
        frames.append(frame_data)
    
    return frames

animation_container = st.empty()
control_container = st.empty()

# アニメーション制御のセッション状態
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False

col1, col2 = st.columns(2)

with col1:
    start_button = st.button("アニメーション開始", type="primary")

with col2:
    stop_button = st.button("アニメーション停止", type="secondary")

if start_button:
    st.session_state.animation_running = True

if stop_button:
    st.session_state.animation_running = False

if st.session_state.animation_running:
    # フレームレートが変更された時にアニメーションを再開始するため、現在の設定を保存
    if 'current_fps' not in st.session_state:
        st.session_state.current_fps = fps
    if 'current_resolution' not in st.session_state:
        st.session_state.current_resolution = resolution
        
    # パラメータが変更された場合はアニメーションを再開始
    if st.session_state.current_fps != fps or st.session_state.current_resolution != resolution:
        st.session_state.current_fps = fps
        st.session_state.current_resolution = resolution
        st.rerun()
    
    frames = create_bouncing_ball_animation(resolution, fps)
    
    # フレームレートに応じた実際の待機時間を計算
    sleep_time = 1.0 / fps
    
    # 1秒間のループアニメーション
    start_time = time.time()
    frame_index = 0
    
    while st.session_state.animation_running and (time.time() - start_time) < 1.0:
        current_frame = frames[frame_index % len(frames)]
        
        fig = go.Figure()
        fig.add_trace(go.Heatmap(
            z=current_frame,
            colorscale='Blues',
            showscale=False,
            hoverinfo='skip'
        ))
        
        elapsed_time = time.time() - start_time
        fig.update_layout(
            title=f"フレーム {(frame_index % len(frames)) + 1}/{len(frames)} | 経過時間: {elapsed_time:.2f}秒 (解像度: {resolution}x{resolution}, FPS: {fps})",
            width=min(400, resolution * 2),
            height=min(400, resolution * 2),
            xaxis=dict(showticklabels=False, showgrid=False),
            yaxis=dict(showticklabels=False, showgrid=False),
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        with animation_container.container():
            st.plotly_chart(fig, use_container_width=False)
        
        frame_index += 1
        time.sleep(sleep_time)
    
    # 1秒経過後は自動停止
    if (time.time() - start_time) >= 1.0:
        st.session_state.animation_running = False
        st.success(f"1秒間のアニメーション完了！ (総フレーム数: {frame_index}, 設定FPS: {fps})")

st.info("""
💡 **アニメーションについて:**
- 1秒間のループアニメーションで、設定したFPSでフレームが切り替わります
- フレーム数はFPSに応じて変化します（10〜60フレーム）
- 低いFPS（例：5fps）では少ないフレームをゆっくり表示し、高いFPS（例：60fps）では多くのフレームを素早く表示します
- アニメーションは1秒後に自動停止します
- 「アニメーション停止」ボタンで途中停止も可能です
""")

st.markdown("---")

st.markdown("### 📊 データ量の計算")

st.markdown("#### 💡 計算式の理解")
st.markdown("""
**データ量の計算手順：**
1. **1ピクセルのデータ量** = 3 bytes (RGB各色1byte)
2. **1フレームのデータ量** = 解像度 × 解像度 × 3 bytes
3. **1秒間のデータ量** = 1フレームのデータ量 × フレームレート
4. **1分間のデータ量** = 1秒間のデータ量 × 60秒
""")

bytes_per_pixel = 3
frame_data_size = resolution * resolution * bytes_per_pixel
data_per_second = frame_data_size * fps
data_per_minute = data_per_second * 60

st.markdown("#### 🧮 現在の設定での計算過程")
with st.container():
    st.markdown(f"""
    **設定値:**
    - 解像度: {resolution} × {resolution} pixels
    - フレームレート: {fps} fps
    - 1ピクセルあたり: {bytes_per_pixel} bytes (RGB)
    
    **計算過程:**
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        **ステップ1: 1フレームのデータ量**
        ```
        {resolution} × {resolution} × {bytes_per_pixel} = {frame_data_size:,} bytes
        = {frame_data_size / 1024:.1f} KB
        = {frame_data_size / 1024 / 1024:.3f} MB
        ```
        """)
    
    with col2:
        st.markdown(f"""
        **ステップ2: 1秒間のデータ量**
        ```
        {frame_data_size:,} × {fps} = {data_per_second:,} bytes
        = {data_per_second / 1024:.1f} KB  
        = {data_per_second / 1024 / 1024:.2f} MB
        ```
        """)

st.markdown(f"""
**ステップ3: 1分間のデータ量**
```
{data_per_second:,} × 60 = {data_per_minute:,} bytes
= {data_per_minute / 1024 / 1024:.2f} MB
= {data_per_minute / 1024 / 1024 / 1024:.3f} GB
```
""")

st.markdown("#### 📈 結果まとめ")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "1フレームのデータ量",
        f"{frame_data_size:,} bytes",
        f"{frame_data_size / 1024:.1f} KB"
    )

with col2:
    st.metric(
        "1秒あたりのデータ量",
        f"{data_per_second / 1024 / 1024:.2f} MB",
        f"{data_per_second:,} bytes"
    )

with col3:
    st.metric(
        "1分あたりのデータ量",
        f"{data_per_minute / 1024 / 1024:.2f} MB",
        f"{data_per_minute / 1024 / 1024 / 1024:.3f} GB"
    )

st.markdown("### 📈 パラメータとデータ量の関係")

resolution_range = np.arange(32, 257, 32)
fps_range = np.arange(5, 61, 5)

data_by_resolution = []
data_by_fps = []

for r in resolution_range:
    frame_size = r * r * bytes_per_pixel
    data_size = frame_size * fps / 1024 / 1024
    data_by_resolution.append(data_size)

for f in fps_range:
    frame_size = resolution * resolution * bytes_per_pixel
    data_size = frame_size * f / 1024 / 1024
    data_by_fps.append(data_size)

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('解像度とデータ量の関係', 'フレームレートとデータ量の関係')
)

fig.add_trace(
    go.Scatter(
        x=resolution_range,
        y=data_by_resolution,
        mode='lines+markers',
        name='解像度による変化',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=fps_range,
        y=data_by_fps,
        mode='lines+markers',
        name='フレームレートによる変化',
        line=dict(color='red', width=3),
        marker=dict(size=8)
    ),
    row=1, col=2
)

fig.add_vline(x=resolution, line_dash="dash", line_color="blue", row=1, col=1)
fig.add_vline(x=fps, line_dash="dash", line_color="red", row=1, col=2)

fig.update_xaxes(title_text="解像度 (pixels)", row=1, col=1)
fig.update_xaxes(title_text="フレームレート (fps)", row=1, col=2)
fig.update_yaxes(title_text="データ量 (MB/秒)", row=1, col=1)
fig.update_yaxes(title_text="データ量 (MB/秒)", row=1, col=2)

fig.update_layout(
    height=400,
    showlegend=False,
    title_text="パラメータがデータ量に与える影響"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📋 現在の設定での詳細分析")

fig_3d = go.Figure()

resolution_mesh = np.linspace(32, 256, 20)
fps_mesh = np.linspace(5, 60, 20)
R, F = np.meshgrid(resolution_mesh, fps_mesh)
Z = R * R * F * bytes_per_pixel / 1024 / 1024

fig_3d.add_trace(go.Surface(
    x=R,
    y=F,
    z=Z,
    colorscale='Viridis',
    name='データ量 (MB/秒)'
))

fig_3d.add_trace(go.Scatter3d(
    x=[resolution],
    y=[fps],
    z=[resolution * resolution * fps * bytes_per_pixel / 1024 / 1024],
    mode='markers',
    marker=dict(size=10, color='red'),
    name='現在の設定'
))

fig_3d.update_layout(
    title='解像度とフレームレートがデータ量に与える影響（3D表示）',
    scene=dict(
        xaxis_title='解像度 (pixels)',
        yaxis_title='フレームレート (fps)',
        zaxis_title='データ量 (MB/秒)'
    ),
    height=600
)

st.plotly_chart(fig_3d, use_container_width=True)

st.markdown("---")

st.markdown("### 🎯 まとめと応用")

st.success("""
**動画の仕組みのまとめ：**
- 動画は「解像度」（画像の細かさ）と「フレームレート」（静止画の連続性）によって成り立っています
- 解像度が高いほど画像が鮮明になりますが、データ量は二乗に比例して増加します
- フレームレートが高いほど動画が滑らかになりますが、データ量は比例して増加します
- 両方のパラメータを上げると、データ量は急激に増加します
""")

st.info("""
**圧縮技術の重要性：**
実際の動画では、このような大量のデータを効率的に保存・送信するため、様々な圧縮技術が使われています。
- H.264、H.265などの動画圧縮フォーマット
- フレーム間の差分を利用した圧縮
- 人間の視覚特性を利用した最適化

次のステップとして、これらの圧縮技術について学んでみましょう！
""")

st.markdown("### 📚 補足情報")

with st.expander("技術的な詳細を見る"):
    st.markdown(f"""
    **現在の設定での計算詳細：**
    - 解像度: {resolution} × {resolution} = {resolution**2:,} ピクセル
    - 1ピクセルあたり: {bytes_per_pixel} bytes (RGB)
    - 1フレーム: {resolution**2:,} × {bytes_per_pixel} = {frame_data_size:,} bytes
    - 1秒間: {frame_data_size:,} × {fps} = {data_per_second:,} bytes = {data_per_second/1024/1024:.2f} MB
    - 1分間: {data_per_second:,} × 60 = {data_per_minute:,} bytes = {data_per_minute/1024/1024:.2f} MB
    - 1時間: {data_per_minute:,} × 60 = {data_per_minute*60:,} bytes = {data_per_minute*60/1024/1024/1024:.2f} GB
    """)

st.markdown("---")
st.markdown("*このアプリケーションを通じて、動画のデジタル表現の基礎を理解していただけましたでしょうか？*")
