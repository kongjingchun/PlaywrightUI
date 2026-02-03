# ========================================
# 图像识别工具
# ========================================
# 基于 OpenCV 的图像识别和对比功能
# ========================================

import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Tuple, Any
from utils.logger import Logger


class ImageRecognition:
    """图像识别和对比工具类"""
    
    logger = Logger("ImageRecognition")
    
    @classmethod
    def load_image(cls, image_path: str, grayscale: bool = False) -> Optional[np.ndarray]:
        """
        加载图片
        
        Args:
            image_path: 图片路径
            grayscale: 是否转为灰度图
        
        Returns:
            图片数组，加载失败返回 None
        """
        try:
            if not Path(image_path).exists():
                cls.logger.error(f"✗ 图片不存在: {image_path}")
                return None
            
            # 读取图片
            if grayscale:
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            else:
                img = cv2.imread(image_path)
            
            if img is None:
                cls.logger.error(f"✗ 无法读取图片: {image_path}")
                return None
            
            cls.logger.info(f"✓ 加载图片成功: {image_path}")
            return img
        except Exception as e:
            cls.logger.error(f"✗ 加载图片失败: {e}")
            return None
    
    @classmethod
    def save_image(cls, image: np.ndarray, save_path: str) -> bool:
        """
        保存图片
        
        Args:
            image: 图片数组
            save_path: 保存路径
        
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            result = cv2.imwrite(save_path, image)
            if result:
                cls.logger.info(f"✓ 保存图片成功: {save_path}")
            else:
                cls.logger.error(f"✗ 保存图片失败: {save_path}")
            return result
        except Exception as e:
            cls.logger.error(f"✗ 保存图片失败: {e}")
            return False
    
    @classmethod
    def compare_images(cls, image1_path: str, image2_path: str, 
                      method: str = "ssim") -> float:
        """
        比较两张图片的相似度
        
        Args:
            image1_path: 第一张图片路径
            image2_path: 第二张图片路径
            method: 比较方法 ("ssim" 或 "mse")
                - ssim: 结构相似性指数，范围 0-1，值越大越相似
                - mse: 均方误差，值越小越相似
        
        Returns:
            相似度值（SSIM: 0-1，MSE: 0-无穷大）
        
        示例：
            similarity = ImageRecognition.compare_images("expected.png", "actual.png")
            assert similarity > 0.95  # SSIM > 95% 表示高度相似
        """
        try:
            # 加载图片（灰度）
            img1 = cls.load_image(image1_path, grayscale=True)
            img2 = cls.load_image(image2_path, grayscale=True)
            
            if img1 is None or img2 is None:
                return 0.0
            
            # 调整尺寸一致
            if img1.shape != img2.shape:
                cls.logger.warning("图片尺寸不一致，正在调整...")
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            if method.lower() == "ssim":
                # 使用 SSIM（结构相似性指数）
                from skimage.metrics import structural_similarity as ssim
                similarity = ssim(img1, img2)
                cls.logger.info(f"✓ SSIM 相似度: {similarity:.4f}")
                return similarity
            
            elif method.lower() == "mse":
                # 使用 MSE（均方误差）
                mse = np.mean((img1 - img2) ** 2)
                cls.logger.info(f"✓ MSE 误差: {mse:.4f}")
                return mse
            
            else:
                cls.logger.error(f"✗ 不支持的比较方法: {method}")
                return 0.0
        
        except Exception as e:
            cls.logger.error(f"✗ 图片比较失败: {e}")
            return 0.0
    
    @classmethod
    def find_template(cls, source_image_path: str, template_image_path: str,
                     threshold: float = 0.8) -> Optional[Dict[str, int]]:
        """
        在源图片中查找模板图片的位置
        
        Args:
            source_image_path: 源图片路径（大图）
            template_image_path: 模板图片路径（小图）
            threshold: 匹配阈值（0-1），值越大要求越严格
        
        Returns:
            匹配位置字典 {"x": int, "y": int, "width": int, "height": int, "confidence": float}
            未找到返回 None
        
        示例：
            position = ImageRecognition.find_template("screenshot.png", "button.png")
            if position:
                print(f"按钮位置: ({position['x']}, {position['y']})")
                page.mouse.click(position['x'] + position['width']//2, 
                                position['y'] + position['height']//2)
        """
        try:
            # 加载图片（灰度）
            source = cls.load_image(source_image_path, grayscale=True)
            template = cls.load_image(template_image_path, grayscale=True)
            
            if source is None or template is None:
                return None
            
            # 模板匹配
            result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 检查是否满足阈值
            if max_val < threshold:
                cls.logger.warning(f"✗ 未找到匹配，置信度: {max_val:.4f} < {threshold}")
                return None
            
            # 获取模板尺寸
            h, w = template.shape
            
            # 返回匹配位置
            position = {
                "x": int(max_loc[0]),
                "y": int(max_loc[1]),
                "width": int(w),
                "height": int(h),
                "confidence": float(max_val)
            }
            
            cls.logger.info(f"✓ 找到匹配位置: ({position['x']}, {position['y']}), "
                          f"置信度: {position['confidence']:.4f}")
            return position
        
        except Exception as e:
            cls.logger.error(f"✗ 模板匹配失败: {e}")
            return None
    
    @classmethod
    def find_all_templates(cls, source_image_path: str, template_image_path: str,
                          threshold: float = 0.8) -> list:
        """
        在源图片中查找所有模板匹配位置
        
        Args:
            source_image_path: 源图片路径
            template_image_path: 模板图片路径
            threshold: 匹配阈值
        
        Returns:
            匹配位置列表
        
        示例：
            positions = ImageRecognition.find_all_templates("page.png", "icon.png")
            for pos in positions:
                print(f"找到图标: ({pos['x']}, {pos['y']})")
        """
        try:
            # 加载图片
            source = cls.load_image(source_image_path, grayscale=True)
            template = cls.load_image(template_image_path, grayscale=True)
            
            if source is None or template is None:
                return []
            
            # 模板匹配
            result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
            h, w = template.shape
            
            # 找到所有匹配位置
            locations = np.where(result >= threshold)
            positions = []
            
            for pt in zip(*locations[::-1]):
                position = {
                    "x": int(pt[0]),
                    "y": int(pt[1]),
                    "width": int(w),
                    "height": int(h),
                    "confidence": float(result[pt[1], pt[0]])
                }
                positions.append(position)
            
            cls.logger.info(f"✓ 找到 {len(positions)} 个匹配位置")
            return positions
        
        except Exception as e:
            cls.logger.error(f"✗ 批量模板匹配失败: {e}")
            return []
    
    @classmethod
    def get_image_hash(cls, image_path: str) -> Optional[str]:
        """
        计算图片的感知哈希值（用于快速比较）
        
        Args:
            image_path: 图片路径
        
        Returns:
            哈希值字符串
        
        示例：
            hash1 = ImageRecognition.get_image_hash("image1.png")
            hash2 = ImageRecognition.get_image_hash("image2.png")
            if hash1 == hash2:
                print("图片相同")
        """
        try:
            import imagehash
            from PIL import Image
            
            img = Image.open(image_path)
            hash_value = str(imagehash.phash(img))
            cls.logger.info(f"✓ 图片哈希: {hash_value}")
            return hash_value
        
        except ImportError:
            cls.logger.error("✗ 需要安装 imagehash 库: pip install imagehash")
            return None
        except Exception as e:
            cls.logger.error(f"✗ 计算图片哈希失败: {e}")
            return None
    
    @classmethod
    def compare_image_hashes(cls, image1_path: str, image2_path: str,
                           max_difference: int = 5) -> bool:
        """
        通过哈希值快速比较两张图片是否相似
        
        Args:
            image1_path: 第一张图片路径
            image2_path: 第二张图片路径
            max_difference: 最大允许差异（0-64），值越小要求越严格
        
        Returns:
            是否相似
        
        示例：
            is_similar = ImageRecognition.compare_image_hashes("img1.png", "img2.png")
            if is_similar:
                print("图片相似")
        """
        try:
            import imagehash
            from PIL import Image
            
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)
            
            hash1 = imagehash.phash(img1)
            hash2 = imagehash.phash(img2)
            
            difference = hash1 - hash2
            is_similar = difference <= max_difference
            
            cls.logger.info(f"✓ 哈希差异: {difference}, 相似: {is_similar}")
            return is_similar
        
        except ImportError:
            cls.logger.error("✗ 需要安装 imagehash 库: pip install imagehash")
            return False
        except Exception as e:
            cls.logger.error(f"✗ 哈希比较失败: {e}")
            return False
    
    @classmethod
    def crop_image(cls, image_path: str, x: int, y: int, width: int, height: int,
                  save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        裁剪图片
        
        Args:
            image_path: 源图片路径
            x: 起始 X 坐标
            y: 起始 Y 坐标
            width: 宽度
            height: 高度
            save_path: 保存路径（可选）
        
        Returns:
            裁剪后的图片数组
        
        示例：
            # 裁剪指定区域
            cropped = ImageRecognition.crop_image("full.png", 100, 100, 200, 150)
            # 保存裁剪结果
            ImageRecognition.crop_image("full.png", 100, 100, 200, 150, "cropped.png")
        """
        try:
            img = cls.load_image(image_path)
            if img is None:
                return None
            
            # 裁剪
            cropped = img[y:y+height, x:x+width]
            
            # 保存（如果指定了路径）
            if save_path:
                cls.save_image(cropped, save_path)
            
            cls.logger.info(f"✓ 裁剪图片成功: ({x}, {y}, {width}, {height})")
            return cropped
        
        except Exception as e:
            cls.logger.error(f"✗ 裁剪图片失败: {e}")
            return None
    
    @classmethod
    def resize_image(cls, image_path: str, width: int, height: int,
                    save_path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        调整图片尺寸
        
        Args:
            image_path: 源图片路径
            width: 目标宽度
            height: 目标高度
            save_path: 保存路径（可选）
        
        Returns:
            调整后的图片数组
        """
        try:
            img = cls.load_image(image_path)
            if img is None:
                return None
            
            # 调整尺寸
            resized = cv2.resize(img, (width, height))
            
            # 保存（如果指定了路径）
            if save_path:
                cls.save_image(resized, save_path)
            
            cls.logger.info(f"✓ 调整尺寸成功: {width}x{height}")
            return resized
        
        except Exception as e:
            cls.logger.error(f"✗ 调整尺寸失败: {e}")
            return None
    
    @classmethod
    def highlight_difference(cls, image1_path: str, image2_path: str,
                           save_path: str) -> bool:
        """
        高亮显示两张图片的差异区域
        
        Args:
            image1_path: 第一张图片路径
            image2_path: 第二张图片路径
            save_path: 差异图保存路径
        
        Returns:
            是否成功
        
        示例：
            # 生成差异对比图
            ImageRecognition.highlight_difference("expected.png", "actual.png", "diff.png")
        """
        try:
            # 加载图片
            img1 = cls.load_image(image1_path)
            img2 = cls.load_image(image2_path)
            
            if img1 is None or img2 is None:
                return False
            
            # 调整尺寸一致
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 计算差异
            diff = cv2.absdiff(img1, img2)
            
            # 转为灰度
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # 二值化
            _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 在原图上绘制差异区域
            result = img1.copy()
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 255), 2)
            
            # 保存结果
            cls.save_image(result, save_path)
            cls.logger.info(f"✓ 差异高亮完成，找到 {len(contours)} 个差异区域")
            return True
        
        except Exception as e:
            cls.logger.error(f"✗ 高亮差异失败: {e}")
            return False


if __name__ == '__main__':
    # 使用示例
    print("图像识别工具已加载")
    print("\n主要功能:")
    print("1. compare_images() - 比较图片相似度")
    print("2. find_template() - 查找模板位置")
    print("3. find_all_templates() - 查找所有匹配位置")
    print("4. get_image_hash() - 计算图片哈希")
    print("5. crop_image() - 裁剪图片")
    print("6. resize_image() - 调整尺寸")
    print("7. highlight_difference() - 高亮差异")
