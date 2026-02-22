# activate-agent-env.ps1
# 一键激活 Qwen3 Agent 的虚拟环境

$venvPath = "E:\AIlibs\agent-env"

if (Test-Path "$venvPath\Scripts\Activate.ps1") {
    Write-Host "正在激活虚拟环境: $venvPath" -ForegroundColor Green
    & "$venvPath\Scripts\Activate.ps1"
    
    # 可选：激活后自动显示当前 python 路径确认
    Write-Host "激活成功！当前 Python：" -ForegroundColor Cyan
    python -c "import sys; print(sys.executable)"
    
    # 可选：显示欢迎信息或常用命令提示
    Write-Host "`n常用命令快速参考：" -ForegroundColor Yellow
    Write-Host "  python server.py          # 启动 Agent 服务"
    Write-Host "  deactivate                # 退出虚拟环境"
    Write-Host "  pip list                  # 查看已安装包"
} else {
    Write-Host "错误：虚拟环境未找到！" -ForegroundColor Red
    Write-Host "预期路径：$venvPath"
    Write-Host "请检查路径是否正确，或虚拟环境是否已创建。"
}