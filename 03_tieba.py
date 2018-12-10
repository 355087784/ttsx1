# coding=utf-8
import requests
from retrying import retry
from lxml import etree
import json

class TiebaSpider:
    def __init__(self,tieba_name):
        self.tieba_name = tieba_name
        self.start_url = "http://tieba.baidu.com/mo/q----,sz@320_240-1-3---2/m?kw={}".format(tieba_name)
        self.part_url = "http://tieba.baidu.com/mo/q----,sz@320_240-1-3---2/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"}

    @retry(stop_max_attempt_number=3)
    def _parse_url(self,url):
        r = requests.get(url,headers=self.headers,timeout=5)
        return r.content.decode()

    def parse_url(self,url): #发送请求，获取列表响应
        try:
            html_str = self._parse_url(url)
        except:
            html_str = None
        return html_str

    def get_content_list(self,html):#提取列表页的数据
        html = etree.HTML(html)
        div_list = html.xpath("//div[contains(@class,'i')]") #获取一个div的分组后的列表
        content_list = []
        for div in div_list:
            item = {}
            item["title"] = div.xpath("./a/text()")[0] if len( div.xpath("./a/text()"))>0 else None
            item["href"] = div.xpath("./a/href")[0] if len( div.xpath("./a/@href"))>0 else None
            item["img_list"] = self.get_img_list(item["href"],[]) if item["href"] is not None else None
            content_list.append(item)
            # item["href"] = div.xpath("./a/href")
            # if len(item["href"])>0:
            #     item["href"] = item["href"][0]
            #     item["img_list"] = self.get_img_list(item["href"])
            # else:
            #     item["href"] = None
         return content_list

    def get_img_list(self,detail_url,total_img_list): #获取详情页的图片
        detail_html = self.parse_url(detail_url) #获取详情页的html——str
        detail_html = etree.HTML(detail_html) #使用etree处理
        img_list = detail_html.xpath("//img[@class='BDE_Image']/@src")
        total_img_list.extend(img_list) #把当前页面的所有图片地址放入total_img_list
        # total_img_list += img_list
        next_url = detail_html.xpath("//a[text()='下一页']/@href")
        if len(next_url)>0: #判断详情页是否有下一页
            next_url = self.part_url + next_url[0]
            return self.get_img_list(next_url) #调用自己，进入递归
        return total_img_list

    def save_content_list(self,content_list):#保存
        file_path = "{}.txt".format(self.tieba_name)
        with open(file_path,"a") as f:
            for content in content_list:
                f.write(json.dumps(content,ensure_ascii=False,indent=2))
                f.write("\n")


    def run(self):#实现主要逻辑
        #1.start_url第一页的url地址
        #2.发送请求，获取列表响应
        html_str = self.parse_url(self.start_url)
        #3.提取列表页的数据

        #4.遍历，请求详情页的url地址
        #5.提取详情页的图片
        self.get_content_list(html_str)
        #5.1保存
        self.save_content_list(content_list)
        #5.详情页有下一页，请求，循环
        #6.找到列表的页的下一页，请求，循环
