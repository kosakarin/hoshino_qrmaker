import base64, os
from PIL import Image, ImageSequence
from io import BytesIO
from amzqr import amzqr

class qrcode:   #amzqr可以提供的参数条目比较多，但是很多都没有必要提供，就简化了下
    def __init__(self, text, picture = None, colorized = False, contrast = 1.0, brightness = 1.0, image_type = 'png'):
        self.text = str(text)
        self.picture = picture
        self.colorized = colorized
        self.contrast = contrast
        self.brightness = brightness
        self.image_type = image_type
		
        self.get_qrcode()
        self.load_qrcode()
        self.load_qrcode_to_base64()
        self.remove_temp_img()

    def get_qrcode(self):  #将参数传给amzqr去生成二维码 qr_name的返回就是生成的二维码保存路径，直接可以调用Image.open去打开
        self.version, self.level, self.qr_name = amzqr.run(self.text,
                                                           picture = self.picture,
                                                           colorized = self.colorized,
                                                           contrast = self.contrast,
                                                           brightness = self.brightness)
    
    def load_qrcode(self): #打开生成好的二维码
        self.qr_img = Image.open(self.qr_name) 
    
    def load_qrcode_to_base64(self):  #用base64来发送图片效果比较好，比R的限制少多了
        buf = BytesIO()
        if self.image_type == 'png':
            qr_img = self.remake_qrcode(self.qr_img)
            qr_img.save(buf, format = 'PNG')
            self.base64_str = f'base64://{base64.b64encode(buf.getvalue()).decode()}'
        elif self.image_type == 'gif':
            self.info = self.qr_img.info
            sequence = [self.remake_qrcode(f.copy()) for f in ImageSequence.Iterator(self.qr_img)]
            sequence[0].save(buf, format='GIF', save_all=True,
                         append_images=sequence[1:], disposal=2,
                         quality=100, **self.info)
            self.base64_str =  f'base64://{base64.b64encode(buf.getvalue()).decode()}'
    
    def remake_qrcode(self, qr_img):
        crop_size = 27  #原图像白边为36像素，每个特征点为9像素,故整体居中裁剪27像素较为美观
        new_img = qr_img.crop((crop_size, crop_size, 
                               qr_img.size[0] - crop_size, qr_img.size[1] - crop_size)) 
        return new_img

    def remove_temp_img(self):
        os.remove(self.qr_name)  #删掉生成的二维码图片
