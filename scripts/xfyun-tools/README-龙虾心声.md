# 龙虾头条语音工具说明

## 推荐执行方式（避免环境变量丢失）
- 先通过包装脚本加载环境变量，再执行 Python：
- `./with_xfyun_env.sh python3 xfyun_super_official_run.py --url ... --voice ... --text ... --out ...`

包装脚本会自动 source 常见 shell 配置（`.bash_profile/.zprofile/.zshrc/.bashrc`）并校验：
- `XFYUN_APPID`
- `XFYUN_API_KEY`
- `XFYUN_API_SECRET`
