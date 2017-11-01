# -*- coding: utf-8 -*-
from scrapy import Request,Spider
import json
from zhihuuser.items import ZhihuuserItem

class ZhihuSpider(Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']
    followees_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    start_user = 'Germey'
    followees_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'

    #重写发送第一个请求的方法
    #实现了第一个大V用户的详细信息请求还有他的粉丝和关注列表请求。
    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        #url = 'https://www.zhihu.com/api/v4/members/Germey/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=0&limit=20'
        #url = self.followees_url.format(user=self.start_user, include=self.followees_query, offset=0, limit=20)
        #对于一个正常请求，会返回一个response，传给parse方法
        yield Request(self.followees_url.format(user=self.start_user, include=self.followees_query, offset=0, limit=20),
                      callback=self.parse_follows)
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20),
                      callback=self.parse_followers)

    def parse_user(self, response):
        #loads针对内存对象，即将Python内置数据序列化为字串
        result=json.loads(response.text)
        item=ZhihuuserItem()
        for field in item.fields:
            if field in result.keys():
                item[field]=result.get(field)
        yield item

    def parse_follows(self, response):
         #print(response.text)
         results=json.loads(response.text)
         #解析返回结果页面的每一位作者的信息
         if 'data' in results.keys():
             for result in results.get('data'):
                 url=self.user_url.format(user=result.get("url_token"),include=self.user_query)
                 yield Request(url,callback=self.parse_user)
         #如果还有下一页，需要继续爬取
         if 'paging' in results.keys():
             next_page = results.get('paging').get('next')
             yield Request(next_page, callback=self.parse_follows)


    def parse_followers(self, response):
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get("url_token"),include=self.user_query),callback=self.parse_user)

        if 'paging' in results.keys() and results.get('paging').get('is_end')==False:
            next_page=results.get('paging').get('next')
            yield Request(next_page,callback=self.parse_followers)