import pandas as pd
import math
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
from itables import to_html_datatable, init_notebook_mode
import itables.options as opt

# 抑制 itables 关于未记录参数的警告
opt.warn_on_undocumented_option = False

# 初始化 notebook 模式，确保 JS 依赖加载
try:
    init_notebook_mode(all_interactive=False)
except Exception:
    pass # 在某些非 notebook 环境下可能报错，忽略

def pagination_view(df: pd.DataFrame, page_size: int = 200) -> None:
    """
    对 DataFrame 数据进行交互式分页浏览。
    
    Algorithm:
        name: 数据分页浏览
        category: eda
        prompt: 对 {VAR_NAME} 进行分页浏览，每页 {page_size} 行。
        imports: import pandas as pd
    
    Parameters:
    df (pd.DataFrame): 输入数据表
        role: input
    page_size (int): 每页显示的行数
        label: 每页行数
        widget: number
        min: 10
        max: 1000
        step: 10
        default: 200
        role: parameter
    
    Returns:
    None
    """
    if df is None:
        print("Error: Input DataFrame is None")
        return

    # --- 状态变量初始化 ---
    current_page = 1
    current_page_size = page_size
    total_rows = len(df)
    
    def calculate_total_pages():
        return math.ceil(total_rows / current_page_size) if current_page_size > 0 else 1
    
    total_pages = calculate_total_pages()

    # --- 样式定义 ---
    style_html = widgets.HTML("""
    <style>
        .pagination-container {
            font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
            padding: 10px 0;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            border-radius: 4px 4px 0 0;
        }
        .status-text {
            color: #6c757d;
            font-size: 14px;
            margin-left: 10px;
            vertical-align: middle;
            line-height: 32px; /* 增加行高以垂直居中 */
        }
        .total-pages {
            font-weight: bold;
            margin: 0 5px;
        }
        /* 修正输入框对齐 */
        .widget-text input {
            padding-top: 4px !important;
            padding-bottom: 4px !important;
            height: 32px !important;
        }
        /* 隐藏最外层的多余横向滚动条 */
        .jp-OutputArea-output {
            overflow-x: hidden !important;
        }
        /* 确保表格容器宽度适配 */
        .dataTables_wrapper {
            width: 100% !important;
        }
    </style>
    """)

    # --- 左侧：分页控制区 ---
    prev_btn = widgets.Button(
        description="",
        disabled=True,
        icon="chevron-left", 
        layout=widgets.Layout(width='32px', height='32px'), 
        tooltip='上一页'
    )
    next_btn = widgets.Button(
        description="",
        disabled=total_pages <= 1,
        icon="chevron-right",
        layout=widgets.Layout(width='32px', height='32px'), 
        tooltip='下一页'
    )
    
    page_input = widgets.IntText(
        value=current_page,
        layout=widgets.Layout(width='60px', height='32px')
    )
    
    total_pages_label = widgets.HTML(
        value=f"<span class='status-text' style='line-height:32px'>/ <span class='total-pages'>{total_pages}</span> 页</span>",
        layout=widgets.Layout(height='32px', display='flex', align_items='center') 
    )
    
    pagination_box = widgets.HBox(
        [prev_btn, page_input, total_pages_label, next_btn],
        layout=widgets.Layout(align_items='center')
    )

    # --- 右侧：设置与信息区 ---
    page_size_input = widgets.Dropdown(
        options=[50, 100, 200, 500, 1000],
        value=current_page_size,
        description="每页显示:",
        layout=widgets.Layout(width='180px', height='32px'),
        style={'description_width': 'initial'}
    )
    
    status_label = widgets.HTML(
        value=f"<span class='status-text'>共 <b>{total_rows}</b> 行数据</span>"
    )
    
    settings_box = widgets.HBox(
        [page_size_input, status_label],
        layout=widgets.Layout(align_items='center')
    )

    # --- 顶部工具栏容器 ---
    controls = widgets.HBox(
        [style_html, pagination_box, settings_box], 
        layout=widgets.Layout(
            width='100%', 
            justify_content='space-between', # 左右对齐
            align_items='center',
            margin='0 0 10px 0',
            padding='5px 10px',
            border='1px solid #ddd' 
        )
    )
    controls.add_class("pagination-container")

    # --- 输出区域 ---
    output_area = widgets.Output(layout=widgets.Layout(width='100%'))

    # --- 逻辑控制函数 ---
    def update_view():
        # 计算切片
        start_idx = (current_page - 1) * current_page_size
        end_idx = min(start_idx + current_page_size, total_rows)
        
        # 获取当前页数据
        current_df = df.iloc[start_idx:end_idx]
        
        # 更新按钮状态
        prev_btn.disabled = current_page <= 1
        next_btn.disabled = current_page >= total_pages
        
        # 更新状态标签
        total_pages_label.value = f"<span class='status-text' style='line-height:32px'>/ <span class='total-pages'>{total_pages}</span> 页</span>"
        status_label.value = f"<span class='status-text'>显示 <b>{start_idx+1}-{end_idx}</b> 行 / 共 <b>{total_rows}</b> 行</span>"
        
        # 在 Output 区域渲染
        with output_area:
            clear_output(wait=True)
            try:
                # 生成 HTML
                html_content = to_html_datatable(
                    current_df,
                    classes="display nowrap cell-border hover stripe", # 更丰富的样式
                    paging=False, # 禁用前端分页
                    scrollX=True,
                    scrollY="500px", # 固定高度并启用纵向滚动
                    dom='t', # 只显示表格主体(table)，隐藏 search(f), info(i), pagination(p) 等组件
                    showIndex=True,
                    style="width:100%; font-family: Arial, sans-serif; font-size: 13px;" # 自定义表格字体
                )
                display(HTML(html_content))
            except Exception as e:
                print(f"Error rendering table: {e}")

    def on_prev_click(b):
        nonlocal current_page
        if current_page > 1:
            page_input.value = current_page - 1 # 触发 on_page_change
            
    def on_next_click(b):
        nonlocal current_page
        if current_page < total_pages:
            page_input.value = current_page + 1 # 触发 on_page_change

    def on_page_change(change):
        nonlocal current_page
        new_page = change['new']
        # 防止输入无效页码
        if 1 <= new_page <= total_pages:
            if current_page != new_page:
                current_page = new_page
                update_view()
        else:
            # 如果输入无效，可以选择忽略或重置，这里暂时忽略
            pass

    def on_page_size_change(change):
        nonlocal current_page_size, total_pages, current_page
        new_size = change['new']
        if new_size > 0:
            current_page_size = new_size
            total_pages = calculate_total_pages()
            
            # 重置到第一页
            current_page = 1
            page_input.value = 1
            
            # 无论 page_input 是否变化（比如原来就是1），都强制刷新视图
            update_view()

    # --- 绑定事件 ---
    prev_btn.on_click(on_prev_click)
    next_btn.on_click(on_next_click)
    page_input.observe(on_page_change, names='value')
    page_size_input.observe(on_page_size_change, names='value')

    # --- 首次渲染 ---
    update_view()
    display(widgets.VBox([controls, output_area]))
