# run.py
from app import create_app

# 通过工厂函数创建 app 实例
app = create_app()

if __name__ == '__main__':
    # 启动 Flask 服务器
    # host='0.0.0.0' 允许局域网内的其他设备(如您的TS客户端)访问
    # debug=False 在生产模式下运行，可避免模型重复加载
    app.run(host='0.0.0.0', port=3723, debug=False)
