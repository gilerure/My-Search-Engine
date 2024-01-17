import os

result_folder = 'result'
comment_folder = 'comment'

# 获取 result 文件夹中的文件列表
result_files = os.listdir(result_folder)

for result_file in result_files:
    # 构建对应的 comment 文件路径
    comment_file = os.path.join(comment_folder, result_file)

    # 如果 comment 文件存在，则删除对应的 result 文件
    if os.path.exists(comment_file):
        result_file_path = os.path.join(result_folder, result_file)
        os.remove(result_file_path)
        print(f"已删除文件: {result_file}")
