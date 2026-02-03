# 图像识别使用指南

## 功能概述

框架提供了基于 OpenCV 的图像识别功能，用于：
- 🖼️ UI 截图对比（回归测试）
- 🔍 模板匹配（查找元素位置）
- 📊 图片相似度计算
- ✨ 差异高亮显示
- 🎯 图片哈希快速对比

## 安装依赖

图像识别功能需要额外的依赖库：

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或单独安装图像识别相关库
pip install opencv-python Pillow imagehash scikit-image
```

## 主要功能

### 1. 图片相似度比较

#### SSIM（结构相似性指数）

推荐使用，适合大部分场景：

```python
from utils.image_recognition import ImageRecognition

# 比较两张图片的相似度
similarity = ImageRecognition.compare_images(
    "expected.png",
    "actual.png",
    method="ssim"  # 默认方法
)

print(f"相似度: {similarity:.4f}")  # 0.9523

# 断言相似度
assert similarity > 0.95  # 95% 以上表示高度相似
```

**SSIM 值说明：**
- `1.0`: 完全相同
- `0.95 - 0.99`: 高度相似（UI 基本一致）
- `0.90 - 0.95`: 较为相似（有细微差异）
- `< 0.90`: 差异较大

#### MSE（均方误差）

适合精确比较：

```python
# 使用 MSE 方法
mse = ImageRecognition.compare_images(
    "expected.png",
    "actual.png",
    method="mse"
)

print(f"MSE 误差: {mse:.4f}")

# MSE 值越小越相似
assert mse < 100  # 误差小于 100
```

### 2. 模板匹配

#### 查找单个模板

在大图中查找小图的位置：

```python
from utils.image_recognition import ImageRecognition

# 查找按钮位置
position = ImageRecognition.find_template(
    source_image_path="screenshot.png",
    template_image_path="button.png",
    threshold=0.8  # 匹配阈值 0-1
)

if position:
    print(f"找到按钮位置:")
    print(f"  X: {position['x']}")
    print(f"  Y: {position['y']}")
    print(f"  宽度: {position['width']}")
    print(f"  高度: {position['height']}")
    print(f"  置信度: {position['confidence']:.4f}")
    
    # 在 Playwright 中点击该位置
    center_x = position['x'] + position['width'] // 2
    center_y = position['y'] + position['height'] // 2
    page.mouse.click(center_x, center_y)
else:
    print("未找到匹配的按钮")
```

#### 查找所有匹配

查找页面中所有相同的元素：

```python
# 查找所有图标
positions = ImageRecognition.find_all_templates(
    source_image_path="page.png",
    template_image_path="icon.png",
    threshold=0.8
)

print(f"找到 {len(positions)} 个图标")
for i, pos in enumerate(positions, 1):
    print(f"图标 {i}: ({pos['x']}, {pos['y']})")
```

### 3. 图片哈希对比

快速比较大量图片（性能优于 SSIM）：

```python
from utils.image_recognition import ImageRecognition

# 方式一：获取哈希值
hash1 = ImageRecognition.get_image_hash("image1.png")
hash2 = ImageRecognition.get_image_hash("image2.png")

if hash1 == hash2:
    print("图片完全相同")

# 方式二：直接比较（推荐）
is_similar = ImageRecognition.compare_image_hashes(
    "image1.png",
    "image2.png",
    max_difference=5  # 允许的最大差异（0-64）
)

if is_similar:
    print("图片相似")
```

**差异值说明：**
- `0`: 完全相同
- `1-5`: 高度相似
- `6-10`: 较为相似
- `> 10`: 差异较大

### 4. 差异高亮

生成对比图，直观显示差异：

```python
from utils.image_recognition import ImageRecognition

# 高亮差异区域（红色框标记）
ImageRecognition.highlight_difference(
    image1_path="expected.png",
    image2_path="actual.png",
    save_path="diff_highlighted.png"
)

# 在 Allure 报告中附加差异图
import allure
allure.attach.file("diff_highlighted.png", "差异对比", 
                   attachment_type=allure.attachment_type.PNG)
```

### 5. 图片裁剪与调整

```python
from utils.image_recognition import ImageRecognition

# 裁剪指定区域
cropped = ImageRecognition.crop_image(
    image_path="full.png",
    x=100,
    y=100,
    width=200,
    height=150,
    save_path="cropped.png"
)

# 调整图片尺寸
resized = ImageRecognition.resize_image(
    image_path="original.png",
    width=800,
    height=600,
    save_path="resized.png"
)
```

## 测试用例示例

### 示例 1: UI 回归测试

验证 UI 没有变化：

```python
import pytest
import allure
from playwright.sync_api import Page
from utils.image_recognition import ImageRecognition
from utils.screenshot_helper import ScreenshotHelper

@allure.feature("UI 回归测试")
class TestUIRegression:
    
    @allure.story("首页UI对比")
    def test_homepage_ui(self, page: Page):
        """验证首页 UI 没有变化"""
        # 访问首页
        page.goto("https://www.example.com")
        page.wait_for_load_state("networkidle")
        
        # 截取当前页面
        actual_screenshot = "screenshots/homepage_actual.png"
        page.screenshot(path=actual_screenshot, full_page=True)
        
        # 与基准图对比
        baseline_screenshot = "tests/baseline/homepage_baseline.png"
        
        similarity = ImageRecognition.compare_images(
            baseline_screenshot,
            actual_screenshot,
            method="ssim"
        )
        
        with allure.step(f"UI 相似度: {similarity:.4f}"):
            if similarity < 0.95:
                # 生成差异对比图
                diff_image = "screenshots/homepage_diff.png"
                ImageRecognition.highlight_difference(
                    baseline_screenshot,
                    actual_screenshot,
                    diff_image
                )
                allure.attach.file(diff_image, "差异对比", 
                                 attachment_type=allure.attachment_type.PNG)
            
            assert similarity > 0.95, f"UI 发生变化，相似度: {similarity:.4f}"
```

### 示例 2: 图标查找与点击

无法定位元素时使用图像识别：

```python
import pytest
import allure
from playwright.sync_api import Page
from utils.image_recognition import ImageRecognition

@allure.feature("图像定位")
class TestImageLocator:
    
    @allure.story("通过图标查找按钮")
    def test_click_button_by_image(self, page: Page):
        """使用图像识别查找并点击按钮"""
        # 访问页面
        page.goto("https://www.example.com")
        
        # 截取页面
        screenshot_path = "screenshots/page.png"
        page.screenshot(path=screenshot_path)
        
        # 查找登录按钮图标
        position = ImageRecognition.find_template(
            source_image_path=screenshot_path,
            template_image_path="tests/templates/login_button.png",
            threshold=0.85
        )
        
        assert position is not None, "未找到登录按钮"
        
        with allure.step(f"点击按钮位置: ({position['x']}, {position['y']})"):
            # 计算按钮中心点
            center_x = position['x'] + position['width'] // 2
            center_y = position['y'] + position['height'] // 2
            
            # 点击
            page.mouse.click(center_x, center_y)
        
        # 验证点击效果
        assert page.url.endswith("/login"), "未跳转到登录页"
```

### 示例 3: 验证码识别准备

为 OCR 识别准备图片：

```python
import pytest
import allure
from playwright.sync_api import Page
from utils.image_recognition import ImageRecognition

@allure.feature("验证码处理")
class TestCaptcha:
    
    @allure.story("验证码预处理")
    def test_captcha_preprocessing(self, page: Page):
        """验证码图片预处理"""
        # 访问登录页
        page.goto("https://www.example.com/login")
        
        # 定位验证码元素
        captcha_element = page.locator("#captcha-image")
        
        # 截取验证码
        captcha_element.screenshot(path="screenshots/captcha_raw.png")
        
        # 裁剪去除边框
        captcha_cropped = ImageRecognition.crop_image(
            image_path="screenshots/captcha_raw.png",
            x=5, y=5, width=90, height=30,
            save_path="screenshots/captcha_cropped.png"
        )
        
        # 放大图片（提高识别率）
        captcha_resized = ImageRecognition.resize_image(
            image_path="screenshots/captcha_cropped.png",
            width=180, height=60,
            save_path="screenshots/captcha_resized.png"
        )
        
        # 附加到报告
        allure.attach.file("screenshots/captcha_resized.png", 
                          "预处理后的验证码",
                          attachment_type=allure.attachment_type.PNG)
        
        # 后续可以调用 OCR 识别...
```

### 示例 4: 批量图片对比

CI/CD 中批量验证截图：

```python
import pytest
import allure
from pathlib import Path
from utils.image_recognition import ImageRecognition

@allure.feature("批量UI测试")
class TestBulkUIComparison:
    
    def test_compare_all_pages(self):
        """批量对比所有页面截图"""
        baseline_dir = Path("tests/baseline")
        actual_dir = Path("screenshots/actual")
        
        results = []
        
        for baseline_file in baseline_dir.glob("*.png"):
            actual_file = actual_dir / baseline_file.name
            
            if not actual_file.exists():
                results.append({
                    "page": baseline_file.name,
                    "status": "缺少实际截图",
                    "similarity": 0.0
                })
                continue
            
            # 对比相似度
            similarity = ImageRecognition.compare_images(
                str(baseline_file),
                str(actual_file),
                method="ssim"
            )
            
            status = "通过" if similarity > 0.95 else "失败"
            results.append({
                "page": baseline_file.name,
                "status": status,
                "similarity": similarity
            })
            
            # 如果失败，生成差异图
            if similarity <= 0.95:
                diff_file = f"screenshots/diff/{baseline_file.name}"
                ImageRecognition.highlight_difference(
                    str(baseline_file),
                    str(actual_file),
                    diff_file
                )
        
        # 生成报告
        report = "\n".join([
            f"{r['page']}: {r['status']} (相似度: {r['similarity']:.4f})"
            for r in results
        ])
        
        with allure.step("对比结果"):
            allure.attach(report, "批量对比报告", 
                         allure.attachment_type.TEXT)
        
        # 断言所有页面都通过
        failed = [r for r in results if r['status'] != "通过"]
        assert len(failed) == 0, f"有 {len(failed)} 个页面对比失败"
```

## 应用场景

### 1. UI 回归测试

适合以下场景：
- 页面布局验证
- 样式回归测试
- 多浏览器对比
- 响应式设计验证

### 2. 无法定位的元素

当元素无法通过常规方式定位时：
- Canvas 绘制的元素
- Flash/插件内容
- 图片按钮
- 动态生成的元素

### 3. 可视化验证

需要验证视觉效果：
- 图表渲染
- 图片加载
- 颜色/字体
- 动画效果

### 4. 验证码处理

为 OCR 识别做准备：
- 图片预处理
- 裁剪/缩放
- 噪点去除

## 最佳实践

### 1. 基准图管理

```
tests/
  baseline/           # 基准图片目录
    homepage.png
    login_page.png
    dashboard.png
  templates/         # 模板图片目录
    button_login.png
    icon_close.png
```

### 2. 阈值选择

**SSIM 相似度阈值建议：**
- 严格模式: `> 0.98`（几乎完全一致）
- 标准模式: `> 0.95`（允许细微差异）
- 宽松模式: `> 0.90`（允许一定差异）

**模板匹配阈值建议：**
- 精确匹配: `> 0.95`
- 标准匹配: `> 0.85`
- 宽松匹配: `> 0.75`

### 3. 性能优化

```python
# 1. 使用哈希对比（快速筛选）
is_similar = ImageRecognition.compare_image_hashes(img1, img2)
if not is_similar:
    # 只有不相似时才用 SSIM 详细对比
    similarity = ImageRecognition.compare_images(img1, img2)

# 2. 裁剪关键区域（减少比较范围）
cropped = ImageRecognition.crop_image("full.png", 100, 100, 500, 400)

# 3. 调整图片尺寸（减少计算量）
resized = ImageRecognition.resize_image("large.png", 800, 600)
```

### 4. 错误处理

```python
try:
    similarity = ImageRecognition.compare_images(baseline, actual)
    assert similarity > 0.95
except AssertionError:
    # 生成差异图
    ImageRecognition.highlight_difference(baseline, actual, "diff.png")
    # 附加到报告
    allure.attach.file("diff.png", "差异对比")
    raise
except Exception as e:
    pytest.skip(f"图片对比失败: {e}")
```

## 注意事项

### 1. 环境一致性

- 确保截图环境一致（分辨率、浏览器版本、系统）
- 使用固定的视口尺寸
- 禁用动画和过渡效果

### 2. 动态内容处理

对于动态内容（时间、随机数据）：
- 使用 CSS 隐藏动态区域
- 裁剪比较静态区域
- 降低相似度阈值

### 3. 性能考虑

- 图像识别比常规定位慢，优先使用常规定位
- 大图片会消耗更多内存和时间
- 批量对比时使用多线程

### 4. 维护成本

- 基准图需要随 UI 更新
- 建立基准图更新流程
- 记录更新原因

## 故障排查

### 1. OpenCV 安装失败

```bash
# macOS
brew install opencv

# Linux
sudo apt-get install python3-opencv

# 或使用 headless 版本
pip install opencv-python-headless
```

### 2. 相似度异常低

可能原因：
- 图片尺寸不一致
- 颜色模式不同（RGB vs RGBA）
- 截图环境不同

### 3. 模板匹配失败

- 降低阈值
- 确认模板图是否在源图中
- 检查图片是否变形
- 尝试调整模板大小

## 相关资源

- [OpenCV 官方文档](https://docs.opencv.org/)
- [scikit-image 文档](https://scikit-image.org/)
- [imagehash 文档](https://github.com/JohannesBuchner/imagehash)
- [SSIM 算法说明](https://en.wikipedia.org/wiki/Structural_similarity)
