# 更新垃圾桶坐标数据文件说明

## 问题分析
容器中的代码是旧版本，无法正确处理 float 类型的坐标数据。虽然本地代码已经更新，但容器需要重新构建才能使用最新代码。

## 已完成的配置

1. ✅ **Dockerfile 已更新**：添加了 `COPY data /code/data`，确保数据文件被复制到容器中
2. ✅ **docker-compose.yml 已更新**：添加了 volume 挂载，使容器直接使用本地的数据文件
3. ✅ **数据文件已验证**：本地 `services/guide_service/data/dustbins.xlsx` 文件格式正确（十进制度数格式）

## 需要执行的步骤

### 方法 1：重新构建容器（推荐）

当网络连接正常时，执行以下命令：

```bash
docker-compose build guide_service
docker-compose up -d guide_service
```

这将使用最新的代码重新构建容器。

### 方法 2：检查数据文件

确认 `services/guide_service/data/dustbins.xlsx` 文件包含：
- 列名：`经度`、`纬度`、`站点名称`
- 数据格式：十进制度数（如 `116.338829`, `39.949510`），不是度分秒格式

### 方法 3：验证更新

容器启动后，可以通过以下命令验证：

```bash
# 检查容器日志
docker-compose logs guide_service

# 测试 API
curl http://localhost:8085/dustbins
```

## 注意事项

- Volume 挂载已配置，本地数据文件的更改会立即反映到容器中
- 如果容器仍然无法启动，可能是代码版本问题，需要重新构建容器
- 确保 Excel 文件中的列名是 `经度`、`纬度`、`站点名称`（中文列名）

