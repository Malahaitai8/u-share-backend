# 垃圾分类识别功能文档

## 功能概述

垃圾分类识别模块提供三种智能识别方式，帮助用户快速准确地识别垃圾分类：

1. **文字识别** - 输入文字，智能识别垃圾类型
2. **语音识别** - 语音输入，自动转文字识别
3. **图像识别** - AI图像识别，拍照即可识别

## 页面结构

```
/classification                        # 垃圾分类识别首页（功能选择）
├── /classification/text              # 文字识别
├── /classification/voice             # 语音识别
└── /classification/image             # 图像识别
```

## 功能详情

### 1. 垃圾分类识别首页 (`/classification`)

**文件路径**: `src/views/GarbageClassification/Index.vue`

**功能说明**:
- 展示三种识别方式的入口
- 提供使用提示和说明
- 精美的卡片式布局

**特色**:
- 响应式设计，适配移动端
- 流畅的动画效果
- 清晰的图标指引

---

### 2. 文字识别 (`/classification/text`)

**文件路径**: `src/views/GarbageClassification/TextRecognition.vue`

**功能说明**:
- 用户输入垃圾名称（如"塑料瓶"）
- 实时字数统计（最多100字）
- 显示识别结果和投放建议

**核心功能**:
- ✅ 文本输入框（支持多行）
- ✅ 识别历史记录（最多保存5条）
- ✅ 快捷示例标签
- ✅ 详细的分类结果展示
- ✅ 温馨提示和投放说明

**API 接口** (待接入):
```javascript
// NLP 服务接口
POST /api/nlp/classify
Body: {
  "text": "塑料瓶"
}
Response: {
  "name": "塑料瓶",
  "category": "recyclable",
  "description": "投放至蓝色可回收物垃圾桶",
  "tips": "请清洗干净后投放"
}
```

---

### 3. 语音识别 (`/classification/voice`)

**文件路径**: `src/views/GarbageClassification/VoiceRecognition.vue`

**功能说明**:
- 点击录音按钮开始录音
- 语音转文字
- 自动分析垃圾分类

**核心功能**:
- ✅ 动态录音按钮（带波纹动画）
- ✅ 录音状态实时显示
- ✅ 语音转文字展示
- ✅ 二次确认分析
- ✅ 详细的识别结果

**API 接口** (待接入):
```javascript
// 1. 百度语音识别接口
POST /api/nlp/speech-to-text
Body: FormData (audio file)
Response: {
  "text": "塑料瓶"
}

// 2. NLP 分类接口（同文字识别）
POST /api/nlp/classify
```

**技术要点**:
- 使用 `navigator.mediaDevices.getUserMedia()` 获取音频流
- 录音时间验证（最少0.5秒）
- 录音状态管理（录音中/处理中/完成）

---

### 4. 图像识别 (`/classification/image`)

**文件路径**: `src/views/GarbageClassification/ImageRecognition.vue`

**功能说明**:
- 上传图片或拍照
- AI 智能识别垃圾类型
- 显示置信度和相似物品

**核心功能**:
- ✅ 图片上传（支持 JPG/PNG/GIF）
- ✅ 图片预览
- ✅ 文件大小限制（10MB）
- ✅ 置信度显示
- ✅ 相似物品推荐
- ✅ 详细的识别结果

**API 接口** (待接入):
```javascript
// 图像识别服务接口
POST /api/image/recognize
Body: FormData {
  "image": File
}
Response: {
  "name": "塑料饮料瓶",
  "category": "recyclable",
  "description": "投放至蓝色可回收物垃圾桶",
  "tips": "请清洗干净后投放",
  "confidence": 95,
  "similar": [
    { "name": "矿泉水瓶", "match": 92 },
    { "name": "可乐瓶", "match": 88 }
  ]
}
```

---

## 垃圾分类类型

系统支持四种垃圾分类类型：

| 类型 | 标识颜色 | CSS Class | 示例 |
|------|---------|-----------|------|
| 可回收物 | 蓝色 | `recyclable` | 塑料瓶、废纸、玻璃瓶 |
| 有害垃圾 | 红色 | `harmful` | 电池、药品、荧光灯 |
| 厨余垃圾 | 绿色 | `kitchen` | 果皮、剩菜、茶叶渣 |
| 其他垃圾 | 灰色 | `other` | 烟蒂、尘土、污染纸张 |

---

## UI/UX 设计特点

### 1. 颜色方案
- **文字识别**: 蓝色渐变 (#2196F3 → #64B5F6)
- **语音识别**: 橙色渐变 (#FF9800 → #FFB74D)
- **图像识别**: 紫色渐变 (#9C27B0 → #BA68C8)

### 2. 动画效果
- 页面进入淡入上升动画
- 卡片悬停交互效果
- 录音按钮波纹动画
- 结果展示过渡动画

### 3. 响应式设计
- 最大宽度限制: 414px（移动端优先）
- 小屏适配: ≤375px
- 安全区域适配（iOS 刘海屏）

---

## 待接入后端服务

### 1. NLP 服务 (端口: 8083)
- 文字识别垃圾分类
- 语音转文字
- Swagger 文档: `http://localhost:8083/docs`

### 2. 图像识别服务 (端口: 8082)
- 图片上传识别
- AI 模型推理
- Swagger 文档: `http://localhost:8082/docs`

---

## 如何测试

### 1. 启动服务
```bash
# 前端
cd u-share-frontend
npm run dev

# 后端
docker-compose up -d
```

### 2. 访问页面
1. 登录系统: `http://localhost:5173`
2. 进入 Dashboard
3. 点击"垃圾分类识别"卡片
4. 选择任意识别方式进行测试

### 3. 测试数据
**文字识别示例**:
- 塑料瓶 → 可回收物
- 电池 → 有害垃圾
- 果皮 → 厨余垃圾
- 烟蒂 → 其他垃圾

---

## 下一步优化

### 功能优化
- [ ] 接入真实的后端 API
- [ ] 添加用户识别历史记录存储
- [ ] 实现积分奖励机制
- [ ] 添加分享功能
- [ ] 支持批量识别

### 性能优化
- [ ] 图片压缩上传
- [ ] 识别结果缓存
- [ ] 离线识别支持
- [ ] 接口请求优化

### 用户体验优化
- [ ] 添加引导教程
- [ ] 优化错误提示
- [ ] 添加快捷操作
- [ ] 支持语音播报结果

---

## 技术栈

- **前端框架**: Vue 3 + Composition API
- **UI 组件库**: Element Plus
- **样式预处理**: SCSS
- **路由管理**: Vue Router
- **状态管理**: Pinia
- **构建工具**: Vite

---

## 文件清单

```
src/views/GarbageClassification/
├── Index.vue              # 功能选择页面
├── TextRecognition.vue    # 文字识别
├── VoiceRecognition.vue   # 语音识别
└── ImageRecognition.vue   # 图像识别
```

---

## 更新日志

### v1.0.0 (2025-10-18)
- ✅ 创建垃圾分类识别模块
- ✅ 实现文字识别页面
- ✅ 实现语音识别页面
- ✅ 实现图像识别页面
- ✅ 添加路由配置
- ✅ 集成到 Dashboard

---

## 联系与反馈

如有问题或建议，请联系开发团队。


